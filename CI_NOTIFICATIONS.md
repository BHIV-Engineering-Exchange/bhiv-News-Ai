# CI Notification Setup

This document explains how to configure notifications for the repository CI.

Slack (recommended)
- Create an incoming webhook in your Slack workspace and copy the webhook URL.
- In the GitHub repository, go to Settings → Secrets → Actions and add a secret named `SLACK_WEBHOOK` with the webhook URL.
- The CI will automatically post a short message when the workflow finishes.

Email (optional)
- CI can send an email alert using SMTP. Provide these repository secrets:
  - `SMTP_HOST` (e.g. smtp.sendgrid.net)
  - `SMTP_PORT` (default 587)
  - `SMTP_USER` (SMTP username / sender email)
  - `SMTP_PASS` (SMTP password)
  - `ALERT_RECIPIENT` (email address to receive alerts)
- The workflow calls `Task2-master/send_email_alert.py` when these secrets are set.

Security
- Store secrets in GitHub Secrets (not in code).
- Limit access to the repository and rotate credentials as needed.
