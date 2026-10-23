"""Optional LLM client (Gemini / OpenRouter). No key = no call; callers fall
back to grounded extractive generation and say so. Keys come from env only."""
import os, json, urllib.request

def generate_structured(prompt, schema_hint="JSON"):
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
        url = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent?key=%s" % (model, key)
        body = json.dumps({"contents": [{"parts": [{"text": prompt + "\nRespond with valid " + schema_hint + " only."}]}]}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    return None  # caller must use grounded fallback, never invent silently
