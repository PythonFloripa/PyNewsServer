import os
from typing import Iterable

import resend

resend.api_key = os.getenv("RESEND_API_KEY", "")


def send_email(to: str, subject: str, body: str) -> None:
    resend.Emails.send(
        {
            "from": "noreply@pynews.com",
            "to": to,
            "subject": subject,
            "html": body,
        }
    )


def send_bulk_emails(
    recipients: Iterable[str], subject: str, body: str
) -> None:
    unique_recipients = {
        email.strip() for email in recipients if email and email.strip()
    }

    for email in unique_recipients:
        send_email(email=email, subject=subject, body=body)

