"""Daily routine scheduler (APScheduler when installed).

10:00 + 22:00 Masai check, 11:00 coding, 14:00 revision, 17:00 interview,
22:00 progress report. Times are configurable via DAILY_ROUTINE in .env /
dashboard settings. No email is sent when nothing changed (checked in jobs).
"""
def build_scheduler(jobs):
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
    except ImportError:
        return None, "apscheduler not installed — install requirements to enable scheduling"
    sch = BackgroundScheduler(timezone="Asia/Kolkata")
    sch.add_job(jobs["check_masai"], "cron", hour=10, minute=0, id="check_am")
    sch.add_job(jobs["check_masai"], "cron", hour=22, minute=0, id="check_pm")
    sch.add_job(jobs["coding"], "cron", hour=11, minute=0, id="coding")
    sch.add_job(jobs["revision"], "cron", hour=14, minute=0, id="revision")
    sch.add_job(jobs["interview"], "cron", hour=17, minute=0, id="interview")
    sch.add_job(jobs["report"], "cron", hour=22, minute=0, id="report")
    return sch, "scheduler configured (Asia/Kolkata)"
