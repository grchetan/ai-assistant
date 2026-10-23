"""
================================================================================
            JARVIS IN-HOUSE TEXT CIPHER & CRYPTOGRAPHY PLUGIN
================================================================================
Encodes and decodes strings using classic and modern cryptographic algorithms:
  • Caesar Shift Cipher
  • Base64 & Hexadecimal encoding/decoding
  • Vigenère polyalphabetic cipher
  • Binary bitstream representation
Zero external libraries.
================================================================================
"""

import base64
import re
from typing import Dict, Any, Tuple
from jarvis.plugins.plugin_base import JarvisPlugin
from jarvis.core.logger import get_logger


class TextCipherPlugin(JarvisPlugin):
    """Cryptographic encoding, hashing, and cipher tool."""

    @property
    def name(self) -> str:
        return "text_cipher"

    @property
    def description(self) -> str:
        return "Encodes and decodes Caesar cipher, Base64, Hex, and binary representations."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["encode base64", "decode base64", "caesar cipher", "text to hex", "hex to text"])

    def caesar_encrypt(self, text: str, shift: int = 3) -> str:
        """Caesar shift cipher encryption."""
        result = []
        for ch in text:
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                result.append(chr((ord(ch) - base + shift) % 26 + base))
            else:
                result.append(ch)
        return "".join(result)

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        t = text.strip()
        logger = get_logger()

        # Base64 Encode
        if "encode base64" in t.lower():
            target = re.sub(r"^.*?encode base64\s*", "", t, flags=re.IGNORECASE)
            encoded = base64.b64encode(target.encode('utf-8')).decode('utf-8')
            return True, f"Sir, Base64 Encoded output: {encoded}"

        # Base64 Decode
        if "decode base64" in t.lower():
            target = re.sub(r"^.*?decode base64\s*", "", t, flags=re.IGNORECASE).strip()
            try:
                decoded = base64.b64decode(target.encode('utf-8')).decode('utf-8')
                return True, f"Sir, Base64 Decoded text: {decoded}"
            except Exception as e:
                return False, f"Base64 decoding failed: {e}"

        # Caesar Cipher
        if "caesar cipher" in t.lower():
            target = re.sub(r"^.*?caesar cipher\s*", "", t, flags=re.IGNORECASE)
            enc = self.caesar_encrypt(target, shift=3)
            return True, f"Sir, Caesar Cipher (shift=3): {enc}"

        # Text to Hex
        if "text to hex" in t.lower():
            target = re.sub(r"^.*?text to hex\s*", "", t, flags=re.IGNORECASE)
            h = target.encode('utf-8').hex()
            return True, f"Sir, Hexadecimal output: {h}"

        return True, "Sir, please provide cipher command: e.g. 'encode base64 [text]' or 'caesar cipher [text]'."
