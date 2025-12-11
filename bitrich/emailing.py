"""Simple SendGrid helper with graceful fallbacks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from flask import current_app

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
except ImportError:  # pragma: no cover - optional dependency
    SendGridAPIClient = None  # type: ignore
    Mail = None  # type: ignore


@dataclass
class EmailClient:
    """Wrapper around SendGrid that degrades to logging in development."""

    api_key: Optional[str]
    sender: str

    def send_html(self, *, recipient: str, subject: str, html: str) -> None:
        """Send the given HTML email if credentials are present."""
        if not self.api_key or not SendGridAPIClient or not Mail:
            current_app.logger.info(
                'Skipping email "%s" to %s (SendGrid disabled)',
                subject,
                recipient,
            )
            return

        message = Mail(
            from_email=self.sender,
            to_emails=recipient,
            subject=subject,
            html_content=html,
        )
        client = SendGridAPIClient(self.api_key)
        client.send(message)
