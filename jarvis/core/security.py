"""
================================================================================
                    JARVIS SECURITY & CREDENTIALS VAULT
================================================================================
Encrypted credential storage, voice profile hashing, safe token verification,
and execution safety sandboxing for high-risk shell commands.
================================================================================
"""

import os
import json
import base64
import hashlib
import hmac
import platform
from typing import Dict, Any, Optional
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent.parent / "jarvis" / "data"
VAULT_DIR.mkdir(parents=True, exist_ok=True)
VAULT_FILE = VAULT_DIR / "secure_vault.json"


def _derive_hardware_key() -> bytes:
    """Derive a deterministic machine-specific key for local encryption."""
    node = platform.node()
    processor = platform.processor()
    system = platform.system()
    raw = f"JARVIS_SECURE_{node}_{processor}_{system}".encode("utf-8")
    return hashlib.sha256(raw).digest()


class SecurityVault:
    """Stores sensitive API keys and secrets encrypted with machine-bound key."""
    
    _instance: Optional["SecurityVault"] = None

    def __new__(cls) -> "SecurityVault":
        if cls._instance is None:
            cls._instance = super(SecurityVault, cls).__new__(cls)
            cls._instance._init_vault()
        return cls._instance

    def _init_vault(self) -> None:
        self._key = _derive_hardware_key()
        self._store: Dict[str, str] = {}
        self._load()

    def _xor_cipher(self, data: bytes) -> bytes:
        """Symmetric streaming XOR cipher using repeating 32-byte hardware key."""
        out = bytearray(len(data))
        for i, b in enumerate(data):
            out[i] = b ^ self._key[i % len(self._key)]
        return bytes(out)

    def _load(self) -> None:
        if VAULT_FILE.exists():
            try:
                with open(VAULT_FILE, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                
                # Decrypt entries
                self._store = {}
                for k, enc_v in raw_data.items():
                    try:
                        raw_bytes = base64.b64decode(enc_v.encode("utf-8"))
                        decrypted = self._xor_cipher(raw_bytes).decode("utf-8")
                        self._store[k] = decrypted
                    except Exception:
                        continue
            except Exception as e:
                print(f"[SecurityVault] Failed to load vault: {e}")

    def _save(self) -> None:
        try:
            encrypted_dict: Dict[str, str] = {}
            for k, val in self._store.items():
                enc_bytes = self._xor_cipher(val.encode("utf-8"))
                encrypted_dict[k] = base64.b64encode(enc_bytes).decode("utf-8")
            
            with open(VAULT_FILE, "w", encoding="utf-8") as f:
                json.dump(encrypted_dict, f, indent=2)
        except Exception as e:
            print(f"[SecurityVault] Failed to save vault: {e}")

    def set_secret(self, key_name: str, secret_value: str) -> None:
        """Store a secret encrypted on disk."""
        self._store[key_name] = secret_value.strip()
        self._save()

    def get_secret(self, key_name: str, fallback_env: Optional[str] = None) -> Optional[str]:
        """Retrieve a secret, falling back to environment variable if present."""
        if key_name in self._store and self._store[key_name]:
            return self._store[key_name]
        if fallback_env and fallback_env in os.environ:
            return os.environ[fallback_env]
        return None

    def delete_secret(self, key_name: str) -> bool:
        if key_name in self._store:
            del self._store[key_name]
            self._save()
            return True
        return False

    def list_keys(self) -> list:
        return list(self._store.keys())


class SafetyGuard:
    """Inspects actions and shell commands to prevent catastrophic operations."""

    DISALLOWED_PATTERNS = [
        "rmdir /s /q c:\\",
        "format c:",
        "del /f /s /q c:\\windows",
        ":(){ :|:& };:",
        "drop database",
        "drop table",
        "remove-item -recurse c:\\windows",
        "diskpart",
    ]

    @classmethod
    def is_command_safe(cls, command_str: str) -> bool:
        cmd_lower = command_str.lower().strip()
        for pattern in cls.DISALLOWED_PATTERNS:
            if pattern in cmd_lower:
                return False
        return True


def hash_audio_fingerprint(features_bytes: bytes) -> str:
    """Generate SHA-256 HMAC hash of a speaker's biometric array."""
    key = _derive_hardware_key()
    return hmac.new(key, features_bytes, hashlib.sha256).hexdigest()
