"""
================================================================================
                    JARVIS EMAIL AUTOMATION & DISPATCHER
================================================================================
SMTP email composition and dispatch engine supporting TLS/SSL encryption,
file attachments (screenshots, logs), and address book aliasing.
================================================================================
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Tuple
from pathlib import Path

from jarvis.core.logger import get_logger
from jarvis.core.security import SecurityVault


class EmailDispatcher:
    """Manages automated email dispatch."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.vault = SecurityVault()

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body_text: str,
        attachment_paths: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """Send email via SMTP."""
        sender_email = self.vault.get_secret("SMTP_EMAIL")
        sender_pass = self.vault.get_secret("SMTP_PASSWORD")
        smtp_server = self.vault.get_secret("SMTP_SERVER") or "smtp.gmail.com"
        smtp_port = int(self.vault.get_secret("SMTP_PORT") or "587")

        if not sender_email or not sender_pass:
            msg = "Sir, email bhejne ke liye vault me SMTP_EMAIL aur SMTP_PASSWORD configure karna hoga."
            self.logger.warning(msg, "EMAIL")
            return False, msg

        self.logger.info(f"Dispatching email to '{recipient_email}'...", "EMAIL")

        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

            if attachment_paths:
                for file_path in attachment_paths:
                    p = Path(file_path)
                    if p.exists():
                        part = MIMEBase('application', 'octet-stream')
                        with open(p, 'rb') as f:
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{p.name}"')
                        msg.attach(part)

            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.starttls()
            server.login(sender_email, sender_pass)
            server.send_message(msg)
            server.quit()

            success_msg = f"Email successfully sent to {recipient_email} sir."
            self.logger.success(success_msg, "EMAIL")
            return True, success_msg

        except Exception as e:
            err_msg = f"Failed to send email: {e}"
            self.logger.error(err_msg, "EMAIL")
            return False, err_msg


def get_email_dispatcher() -> EmailDispatcher:
    return EmailDispatcher()
