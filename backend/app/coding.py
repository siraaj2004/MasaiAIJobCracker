"""Coding practice with a resource-limited subprocess sandbox.
Student code never runs in the server process: it runs in a child python
with CPU/memory limits, a timeout, and no inherited environment secrets."""
import subprocess, sys, os, resource, json, tempfile

CHALLENGES = {
    "sum-list": {"title": "Sum of a list", "prompt_te": "numbers ane list lo unna anni numbers kalipi total print cheyyandi.",
                 "starter": "numbers = [10, 20, 30]\n# ikkada code rayandi\n",
                 "expected_stdout": "60", "hint": "sum() function use cheyyandi."},
    "add-40": {"title": "Add 40 to the list", "prompt_te": "List loki 40 add chesi total print cheyyandi.",
               "starter": "numbers = [10, 20, 30]\n", "expected_stdout": "100", "hint": "append() use cheyyandi."},
}

def _limits():
    resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))

def run_code(code, timeout=4):
    if len(code) > 20000: return {"ok": False, "error": "code too large"}
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code); path = f.name
    try:
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
        r = subprocess.run([sys.executable, "-I", path], capture_output=True, text=True,
                           timeout=timeout, env=env, preexec_fn=_limits)
        return {"ok": r.returncode == 0, "stdout": r.stdout, "stderr": r.stderr[-1000:], "returncode": r.returncode}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout — infinite loop? code aapeyyandi"}
    finally:
        os.unlink(path)

def submit_challenge(db, challenge_id, code):
    ch = CHALLENGES[challenge_id]
    res = run_code(code)
    passed = res.get("ok") and res.get("stdout", "").strip() == ch["expected_stdout"]
    detail = {"result": res, "expected": ch["expected_stdout"],
              "feedback": "Correct! Output match ayindi." if passed else
                          "Output match kaledu. Expected: %s, Got: %s. Hint: %s" % (ch["expected_stdout"], res.get("stdout", res.get("error", "")).strip(), ch["hint"])}
    db.save_coding(challenge_id, passed, json.dumps(detail))
    return {"passed": passed, **detail}
