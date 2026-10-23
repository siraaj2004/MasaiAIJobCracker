"""Authorized Masai Learn AI-Summary scraper (Playwright).

Rules: saved session (storage_state) preferred; official login page only if
env credentials are set; CAPTCHA or any access restriction STOPS the run —
never bypassed. Only the AI Summary section is extracted, never the transcript.
Temporary errors are retried with backoff and logged. Duplicates are skipped
by summary hash in the DB layer.
"""
import os, time, logging
log = logging.getLogger("masai.scraper")

class CaptchaEncountered(Exception): pass
class SummaryUnavailable(Exception): pass

# The three session types on Masai Learn, as named by the student (2026-10-23).
# Discovery covers ALL THREE — no category is skipped. The saved category is
# stored in the lecture's module field.
SESSION_CATEGORIES = [
    {"key": "academic", "label": "Academic Sessions",
     "patterns": ["academic"]},
    {"key": "im", "label": "IM Sessions",
     "patterns": ["im sessions", "im session", "/im/", "-im-", "industry mentor"]},
    {"key": "masterclass", "label": "MasterClasses",
     "patterns": ["masterclass", "master class", "masterclasses"]},
]

def classify_session(text="", href=""):
    """Return the category key for a session from its title/section text or URL.
    MasterClass is checked first so a 'MasterClass' link is never swallowed by
    a generic match; IM requires an explicit IM marker (never a substring of
    another word). Returns 'other' when nothing matches — the session is still
    processed, just labelled honestly."""
    t = (" %s " % (text or "")).lower()
    h = (href or "").lower()
    for cat in (SESSION_CATEGORIES[2], SESSION_CATEGORIES[0]):
        if any(p in t or p in h for p in cat["patterns"]):
            return cat["key"]
    im = SESSION_CATEGORIES[1]
    if any(p in t or p in h for p in im["patterns"]) or " im " in t:
        return "im"
    return "other"

def category_label(key):
    for cat in SESSION_CATEGORIES:
        if cat["key"] == key:
            return cat["label"]
    return "Other Sessions"

def manual_upload(db, title, module, lecture_date, summary_text):
    """Manual upload path — the supported fallback when automation is unavailable."""
    if not summary_text or not summary_text.strip():
        raise ValueError("empty summary — nothing to save, nothing invented")
    return db.add_lecture(title, module, lecture_date, summary_text.strip(), source="manual")

def _looks_like_captcha(page_text, html=""):
    t = (page_text or "").lower() + (html or "").lower()
    return "captcha" in t or "verify you are human" in t or "recaptcha" in t

def discover_and_extract(db, max_retries=3):
    """Returns dict with counts. Requires playwright + a saved session or env login."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        return {"ok": False, "error": "playwright not installed: %s" % e, "new": 0}
    base = os.environ.get("MASAI_BASE_URL", "https://learn.masaischool.com")
    state = os.environ.get("MASAI_STORAGE_STATE", "data/storage_state.json")
    results = {"ok": True, "new": 0, "duplicates": 0, "errors": []}
    for attempt in range(1, max_retries + 1):
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                ctx = browser.new_context(storage_state=state) if os.path.exists(state) else browser.new_context()
                page = ctx.new_page()
                page.goto(base, wait_until="networkidle", timeout=60000)
                if "login" in page.url or "sign" in page.url:
                    email, pwval = os.environ.get("MASAI_EMAIL"), os.environ.get("MASAI_PASSWORD")
                    if not (email and pwval):
                        results.update(ok=False, error="login required and no saved session / env credentials")
                        browser.close(); return results
                    page.fill("input[type=email]", email)
                    page.fill("input[type=password]", pwval)
                    page.click("button[type=submit]")
                    page.wait_for_load_state("networkidle")
                body = page.inner_text("body")
                if _looks_like_captcha(body, page.content()):
                    raise CaptchaEncountered("CAPTCHA/access check shown — stopping, never bypassed")
                # Discover across all three categories: first follow the
                # Academic Sessions / IM Sessions / MasterClasses section
                # links if present, then also scan the landing page itself.
                links = page.eval_on_selector_all("a[href*=lecture], a[href*=session]",
                    "els => els.map(e => ({href: e.href, text: e.innerText}))")
                nav = page.eval_on_selector_all("a",
                    "els => els.map(e => ({href: e.href, text: e.innerText}))")
                section_pages = []
                for nv in nav:
                    key = classify_session(nv.get("text", ""), nv.get("href", ""))
                    if key != "other" and nv["href"] not in [s[0] for s in section_pages]:
                        section_pages.append((nv["href"], key))
                for sec_href, sec_key in section_pages:
                    try:
                        sp = ctx.new_page(); sp.goto(sec_href, wait_until="networkidle", timeout=60000)
                        sub = sp.eval_on_selector_all("a[href*=lecture], a[href*=session]",
                            "els => els.map(e => ({href: e.href, text: e.innerText}))")
                        for s in sub:
                            s["_category"] = sec_key
                        links.extend(sub)
                        sp.close()
                    except Exception as e:
                        results["errors"].append({"section": sec_href, "error": str(e)})
                results["by_category"] = {"academic": 0, "im": 0, "masterclass": 0, "other": 0}
                seen = set()
                for lk in links:
                    if lk["href"] in seen: continue
                    seen.add(lk["href"])
                    try:
                        lp = ctx.new_page(); lp.goto(lk["href"], wait_until="networkidle", timeout=60000)
                        text = lp.inner_text("body")
                        if _looks_like_captcha(text, lp.content()):
                            raise CaptchaEncountered("CAPTCHA on lecture page — stopping")
                        summary = _extract_ai_summary(lp)
                        if summary is None:
                            results["errors"].append({"lecture": lk["text"], "error": "AI Summary unavailable — recorded, not invented"})
                        else:
                            cat_key = lk.get("_category") or classify_session(lk["text"], lk["href"])
                            _, is_new = db.add_lecture(lk["text"].strip() or "Untitled",
                                                       category_label(cat_key), "", summary, source="masai")
                            results["new" if is_new else "duplicates"] += 1
                            results["by_category"][cat_key] = results["by_category"].get(cat_key, 0) + 1
                        lp.close()
                        time.sleep(2)  # rate-limit respect
                    except CaptchaEncountered:
                        raise
                    except Exception as e:
                        results["errors"].append({"lecture": lk["text"], "error": str(e)})
                browser.close()
            return results
        except CaptchaEncountered as e:
            results.update(ok=False, error=str(e)); return results
        except Exception as e:
            log.warning("scraper attempt %s failed: %s", attempt, e)
            if attempt == max_retries:
                results.update(ok=False, error="temporary failure after %s retries: %s" % (max_retries, e))
                return results
            time.sleep(5 * attempt)

def _extract_ai_summary(page):
    """Find the 'AI Summary' section and return only the text under it."""
    return page.evaluate("""() => {
      const heads = [...document.querySelectorAll('h1,h2,h3,h4,div,span')];
      const h = heads.find(e => e.innerText && e.innerText.trim().toLowerCase() === 'ai summary');
      if (!h) return null;
      let out = [], el = h.parentElement ? h.parentElement.nextElementSibling : h.nextElementSibling;
      let guard = 0;
      while (el && guard++ < 10) {
        const t = el.innerText ? el.innerText.trim() : '';
        if (t) out.push(t);
        el = el.nextElementSibling;
      }
      const joined = out.join('\n').trim();
      return joined ? joined : null;
    }""")
