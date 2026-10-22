"""
================================================================================
                    JARVIS WHATSAPP AUTOMATION
================================================================================
Automated WhatsApp message dispatcher using WhatsApp Web protocols, contact
book phone number resolution, and browser automation.
================================================================================
"""

import time
import urllib.parse
import webbrowser
from typing import Dict, Tuple, Optional

try:
    import pyautogui
    _PYAUTOGUI_AVAILABLE = True
except ImportError:
    _PYAUTOGUI_AVAILABLE = False

from jarvis.core.logger import get_logger

# Default local address book mapping friendly names to country-code phone numbers
CONTACTS_BOOK: Dict[str, str] = {
    "me": "+919999999999",
    "bhai": "+919876543210",
    "home": "+919876543211",
    "office": "+919876543212"
}


class WhatsAppAutomator:
    """Automates WhatsApp Web communications."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.contacts = CONTACTS_BOOK.copy()

    def add_contact(self, name: str, phone: str) -> None:
        clean_phone = phone.strip().replace(" ", "").replace("-", "")
        self.contacts[name.lower().strip()] = clean_phone
        self.logger.info(f"Added WhatsApp contact: '{name}' -> {clean_phone}", "WHATSAPP")

    def send_message(self, target_name_or_number: str, message: str) -> Tuple[bool, str]:
        """Open chat with recipient and prepare message."""
        target = target_name_or_number.lower().strip()
        phone = self.contacts.get(target, target)

        # Remove invalid characters
        phone_digits = "".join([c for c in phone if c.isdigit() or c == "+"])
        if not phone_digits:
            return False, "Invalid phone number."

        encoded_msg = urllib.parse.quote(message.strip())
        url = f"https://web.whatsapp.com/send?phone={phone_digits}&text={encoded_msg}"

        self.logger.info(f"Opening WhatsApp chat for: {phone_digits}", "WHATSAPP")
        webbrowser.open(url)

        return True, f"WhatsApp Web open kar diya hai sir {target} ke liye. Send button press karein."


def get_whatsapp_automator() -> WhatsAppAutomator:
    return WhatsAppAutomator()
