"""Enterprise input sanitization and anti-XSS protection service."""

from __future__ import annotations

import html
import re
import unicodedata
from typing import Any, Dict, List, Optional


# Dangerous HTML/url patterns to neutralize
DANGEROUS_PATTERNS = [
    re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"data:text/html", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),
]


def sanitize_text(text: Any, allow_markdown: bool = True) -> str:
    """Sanitize user-supplied string input against XSS and injections."""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    
    cleaned = text.strip()
    if not cleaned:
        return ""
    
    # Neutralize dangerous HTML scripts and event handlers
    for pattern in DANGEROUS_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    
    if not allow_markdown:
        # Escape all HTML entities
        cleaned = html.escape(cleaned, quote=True)
    else:
        # Neutralize unsafe HTML tags (<script>, <iframe>, <embed>, <object>, <form>, <link>, <style>)
        cleaned = re.sub(
            r"<\/?(script|iframe|embed|object|form|link|style|meta|svg|base)[^>]*>",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
    
    return cleaned.strip()


def sanitize_filename(filename: str) -> str:
    """Sanitize filenames to prevent directory traversal."""
    if not filename:
        return "untitled_document"
    # Remove directory path separators and special characters
    base = re.sub(r'[\\/:\*\?"<>|]', "_", filename)
    base = unicodedata.normalize("NFD", base)
    cleaned = re.sub(r"\.+", ".", base).strip(". ")
    return cleaned if cleaned else "untitled_document"


def sanitize_dict(
    request_dict: Dict[str, Any], fields_to_clean: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Recursively sanitize all string values in a dictionary."""
    result = {}
    for k, v in request_dict.items():
        if fields_to_clean and k not in fields_to_clean:
            result[k] = v
            continue
        if isinstance(v, str):
            result[k] = sanitize_text(v)
        elif isinstance(v, dict):
            result[k] = sanitize_dict(v, fields_to_clean)
        elif isinstance(v, list):
            result[k] = [
                sanitize_text(x) if isinstance(x, str) else x
                for x in v
            ]
        else:
            result[k] = v
    return result
