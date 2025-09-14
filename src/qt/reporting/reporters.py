"""
Modules for sending notifications and reports (e.g., Slack, email).
"""
from __future__ import annotations

class EmailReporter:
    """A reporter for sending emails."""

    def __init__(self, smtp_server: str, from_addr: str, to_addr: str) -> None:
        self.smtp_server = smtp_server
        self.from_addr = from_addr
        self.to_addr = to_addr

    def send_email(self, subject: str, body: str) -> None:
        """Sends an email with the given subject and body."""
        print(f"[{self.__class__.__name__}] Sending email: '{subject}'")
        raise NotImplementedError

class WhatsAppReporter:
    """A reporter for sending messages to a WhatsApp chat."""

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    def send_message(self, message: str) -> None:
        """Sends a plain text message."""
        print(f"[{self.__class__.__name__}] Sending: '{message}'")
        raise NotImplementedError