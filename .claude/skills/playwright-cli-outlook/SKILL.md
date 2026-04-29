---
name: playwright-cli-outlook
description: "Use when: send email via Outlook Web because Outlook API is disabled. Automates Outlook Web (OWA) to compose and send mail with Playwright. Triggers: outlook web, send email, outlook cli, OWA, webmail automation."
license: MIT
argument-hint: <to> <subject> <body> [--cc] [--bcc] [--attachment]
metadata:
  author: mleon019
  version: 0.0.1
---

# playwright-cli-outlook

Automate sending email through Outlook Web (OWA) using Playwright when the Outlook API is disabled.

## When to Use This Skill

- User asks to send an email from Outlook but API access is blocked
- User wants a CLI-style flow that drives Outlook Web in the browser
- User says "outlook web", "OWA", "send email", "outlook cli"

## Assumptions

- The user is already logged in to Outlook Web
- Use the currently opened Playwright browser tab/session (no credential handling)
- Base URL: https://outlook.cloud.microsoft/mail/

## Inputs

- `to`: recipient email address (required)
- `subject`: email subject (required)
- `body`: email body (required)
- `cc`: cc recipients (optional)
- `bcc`: bcc recipients (optional)
- `attachment`: file path to attach (optional)

## Workflow (Playwright)

1. Reuse the currently opened Playwright browser tab.
2. If that tab is not Outlook Web, navigate it to the base URL.
3. Verify the mailbox loads.
2. Click **New mail** to open the compose window.
3. Fill **To**, **Subject**, and the message body.
4. (Optional) Add **Cc/Bcc** and attach a file.
5. Click **Send** and wait for the "Sent" toast/confirmation.

## Playwright Actions (Pseudo-steps)

- Use the existing browser tab (do not open a new one unless required)
- If needed, navigate that tab to https://outlook.cloud.microsoft/mail/
- If not logged in, ask the user to log in manually and retry
- Click the "New mail" button
- Fill the To field, Subject field, and message body
- If `cc`/`bcc` provided, open those fields and fill them
- If `attachment` provided, upload via the Attach button
- Click "Send"
- Confirm a sent notification appears

## Notes

- Do not attempt to access the Outlook API
- Do not request or store credentials
- If the compose UI changes, re-capture selectors and retry
