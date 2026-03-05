#!/usr/bin/env python3
"""Send a simple email alert using SMTP.

Reads SMTP connection details from environment variables and sends a
single email to the recipient. Intended for optional CI/monitoring use.

Environment variables:
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, ALERT_RECIPIENT
"""
import os
import smtplib
from email.message import EmailMessage


def send_mail(subject: str, body: str) -> bool:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    recipient = os.getenv("ALERT_RECIPIENT")

    if not (host and user and password and recipient):
        print("SMTP not configured - skipping email")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient
    msg.set_content(body)

    try:
        with smtplib.SMTP(host, port, timeout=10) as s:
            s.starttls()
            s.login(user, password)
            s.send_message(msg)
        print("Email sent")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


if __name__ == "__main__":
    import sys
    subj = sys.argv[1] if len(sys.argv) > 1 else "CI Alert"
    body = sys.argv[2] if len(sys.argv) > 2 else "CI job completed."
    send_mail(subj, body)
