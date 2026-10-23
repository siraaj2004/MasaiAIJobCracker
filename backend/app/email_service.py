"""Gmail delivery. Sends only when Gmail API credentials are configured.
A send is only reported with the provider message id returned by Gmail.
Duplicate lesson emails are blocked by the emails_sent table."""
import os, base64
from email.mime.text import MIMEText

def build_learning_package_email(lecture, video_link, pdf_name, quiz_link, script):
    defs = script["parts"][3]["text"] if len(script.get("parts", [])) > 3 else ""
    codes = script["parts"][4]["text"] if len(script.get("parts", [])) > 4 else ""
    body = ("Lecture: %s\n\n1. Telugu video lesson: %s\n2. AI Summary PDF: %s\n"
            "3. Important definition: %s\n4. Code notes: %s\n5. Quiz: %s\n"
            "6. Coding challenge: see the coding practice page\n"
            "7. Interview questions: %s\n8. Revision checklist: revise today, +1d, +3d, +7d\n"
            "9. Reminder: 20 minutes of focused practice beats 2 hours of scrolling. You can do this!"
            ) % (lecture["title"], video_link, pdf_name, defs, codes, quiz_link,
                 "; ".join(script["parts"][6].get("questions", [])) if len(script.get("parts", [])) > 6 else "")
    return "AI Engineer Daily Learning — %s" % lecture["title"], body

def send_email(db, lecture, to_addr, subject, body, kind="lesson"):
    creds = os.environ.get("GMAIL_CREDENTIALS_FILE", "data/gmail_credentials.json")
    token = os.environ.get("GMAIL_TOKEN_FILE", "data/gmail_token.json")
    if not (os.path.exists(creds) and os.path.exists(token)):
        return {"sent": False, "reason": "Gmail API not configured (credentials/token missing) — email not sent, not claimed"}
    if db.email_already_sent(lecture["id"], lecture["summary_hash"], kind):
        return {"sent": False, "reason": "duplicate blocked — already emailed for this summary version"}
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        c = Credentials.from_authorized_user_file(token)
        svc = build("gmail", "v1", credentials=c)
        msg = MIMEText(body, "plain", "utf-8"); msg["to"] = to_addr; msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        res = svc.users().messages().send(userId="me", body={"raw": raw}).execute()
        db.log_email(lecture["id"], lecture["summary_hash"], kind, res.get("id"))
        return {"sent": True, "provider_id": res.get("id")}
    except Exception as e:
        return {"sent": False, "reason": "Gmail send failed: %s" % e}
