"""Unit tests for enterprise hardening: Secret Encryption, Anti-XSS, and Idempotency."""

import pytest
from services.secret_encryption_service import (
    encrypt_secret,
    decrypt_secret,
    encrypt_dict,
    decrypt_dict,)
from services.sanitization_service import (
    sanitize_text,
    sanitize_filename,
    sanitize_dict,
)


class TestSecretEncryption:
    def test_string_encryption_decryption(self):
        plain = "super_secret_whatsapp_access_token_12345"
        enc = encrypt_secret(plain)
        assert enc.startswith("enc::")
        assert enc != plain
        dec = decrypt_secret(enc)
        assert dec == plain

    def test_empty_string_encryption(self):
        assert encrypt_secret("") == ""
        assert decrypt_secret("") == ""


    def test_legacy_unencrypted_fallback(self):
        legacy = "regular_plain_text_token"
        assert decrypt_secret(legacy) == legacy

    def test_dict_encryption_decryption(self):
        payload = {
            "whatsapp_number": "+91 96070 53130",
            "naukri_user": "rumana_recruiter",
            "api_token": "sk-live-xyz987",
        }
        enc = encrypt_dict(payload)
        assert enc.startswith("enc::")
        dec = decrypt_dict(enc)
        assert dec == payload

    def test_corrupted_ciphertext_graceful_handling(self):
        corrupted = "enc::corrupted_base64_payload_xyz"
        assert decrypt_secret(corrupted) == ""
        assert decrypt_dict(corrupted) == {}


class TestInputSanitization:
    def test_xss_script_neutralization(self):
        raw = "<script>document.cookie='stolen'</script>Senior Backend Engineer"
        cleaned = sanitize_text(raw)
        assert "<script>" not in cleaned
        assert "Senior Backend Engineer" in cleaned


    def test_html_event_handler_neutralization(self):
        raw = "<img src=x onerror=alert(1)>Frontend Developer"
        cleaned = sanitize_text(raw)
        assert "onerror" not in cleaned

    def test_filename_directory_traversal_neutralization(self):
        dangerous_paths = [
            "../../../../etc/passwd.pdf",
            "..\\..\\Windows\\System32\\cmd.exe",
            "resume/../../../secret.docx",
        ]
        for path in dangerous_paths:
            cleaned = sanitize_filename(path)
            assert "../" not in cleaned
            assert "..\\" not in cleaned
            assert "/" not in cleaned
            assert "\\" not in cleaned


    def test_dict_recursive_sanitization(self):
        payload = {
            "title": "<script>alert(1)</script>Tech Lead",
            "notes": ["<iframe src='evil.com'></iframe>Good skills", "Normal note"],
            "meta": {"location": "Pune <script>bad()</script>"},
        }
        cleaned = sanitize_dict(payload)
        assert cleaned["title"] == "Tech Lead"
        assert "<iframe" not in cleaned["notes"][0]
        assert cleaned["meta"]["location"] == "Pune"
        assert "<script>" not in cleaned["meta"]["location"]
