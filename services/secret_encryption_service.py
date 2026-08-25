"""Enterprise-grade AES / Fernet secret encryption service for credentials and portal tokens."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from typing import Any, Dict

from cryptography.fernet import Fernet, InvalidToken


def _derive_fernet_key(master_secret: str) -> bytes:
    """Derive a URL-safe 32-byte base64-encoded key from master secret using SHA-256."""
    digest = hashlib.sha256(master_secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def _get_master_key() -> bytes:
    """Retrieve or compute master encryption key from environment."""
    env_secret = (
        os.getenv("SECRET_ENCRYPTION_KEY", "").strip()
        or os.getenv("APP_SECRET_KEY", "").strip()
        or os.getenv("SUPABASE_KEY", "").strip()
        or "default-hr-recruitment-production-salt-2026"
    )
    return _derive_fernet_key(env_secret)


def encrypt_secret(plaintext: str) -> str:
    """Encrypt a plaintext string to an armored ciphertext string."""
    if not plaintext:
        return ""
    fernet = Fernet(_get_master_key())
    encrypted = fernet.encrypt(plaintext.encode("utf-8"))
    return "enc::" + encrypted.decode("utf-8")


def decrypt_secret(ciphertext: str) -> str:
    """Decrypt an armored ciphertext string back to plaintext."""
    if not ciphertext:
        return ""
    if not ciphertext.startswith("enc::"):
        # Return as-is if unencrypted legacy format
        return ciphertext
    raw_token = ciphertext[len("enc::") :].encode("utf-8")
    fernet = Fernet(_get_master_key())
    try:
        decrypted = fernet.decrypt(raw_token)
        return decrypted.decode("utf-8")
    except (InvalidToken, Exception):
        return ""


def encrypt_dict(data: Dict[str, Any]) -> str:
    """Serialize and encrypt a dictionary payload."""
    json_bytes = json.dumps(data, sort_keys=True).encode("utf-8")
    fernet = Fernet(_get_master_key())
    encrypted = fernet.encrypt(json_bytes)
    return "enc::" + encrypted.decode("utf-8")


def decrypt_dict(ciphertext: str) -> Dict[str, Any]:
    """Decrypt and deserialize an encrypted dictionary payload."""
    if not ciphertext:
        return {}
    if not ciphertext.startswith("enc::"):
        try:
            return json.loads(ciphertext)
        except Exception:
            return {}
    raw_token = ciphertext[len("enc::") :].encode("utf-8")
    fernet = Fernet(_get_master_key())
    try:
        decrypted = fernet.decrypt(raw_token)
        return json.loads(decrypted.decode("utf-8"))
    except Exception:
        return {}
