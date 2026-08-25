from __future__ import annotations

import io
import logging
import re
from typing import Any, Dict, Tuple
from io import BytesIO

import pypdf
from PIL import Image
try:
    import pytesseract
except ImportError:
    pytesseract = None

from services.sanitization_service import sanitize_text

logger = logging.getLogger("resume_ocr_service")


def extract_text_from_pdf(pdf_bytes_or_file: bytes | BytesIO) -> Dict[str, Any]:
    """Extract text from a PDF resume using native parsing with OCR fallback."""
    if isinstance(pdf_bytes_or_file, bytes):
        file_obj = io.BytesIO(pdf_bytes_or_file)
    else:
        file_obj = pdf_bytes_or_file

    text_pages = []
    is_ocr_used = False
    extraction_method = "native_pypdf"

    try:
        reader = pypdf.PdfReader(file_obj)
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_pages.append(page_text.strip())

        raw_combined = "\n\n".join(text_pages).strip()

        # If native extraction is too short (< 60 chars), attempt OCR from embedded images
        if len(raw_combined) < 60 and pytesseract is not None:
            ocr_pages = []
            for page in reader.pages:
                for img_file_obj in page.images:
                    try:
                        img = Image.open(io.BytesIO(img_file_obj.data))
                        img_text = pytesseract.image_to_string(img)
                        if img_text.strip():
                            ocr_pages.append(img_text.strip())
                    except Exception:
                        pass

            if ocr_pages:
                raw_combined = "\n\n".join(ocr_pages).strip()
                is_ocr_used = True
                extraction_method = "ocr_tesseract"

    except Exception as err:
        logger.warning(f"Failed to extract PDF text: {err}")
        raw_combined = ""

    cleaned_text = sanitize_text(raw_combined)

    return {
        "text": cleaned_text,
        "char_count": len(cleaned_text),
        "word_count": len(cleaned_text.split()),
        "is_ocr_used": is_ocr_used,
        "extraction_method": extraction_method,
        "success": bool(cleaned_text),
    }

def extract_resume_content(file_name: str, file_bytes: bytes) -> Dict[str, Any]:
    """Unified entry point to extract resume text from PDF or Text sources."""
    lower_name = file_name.strip().lower()
    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    try:
        decoded = file_bytes.decode("utf-8", errors="ignore")
        cleaned = sanitize_text(decoded)
        return {
            "text": cleaned,
            "char_count": len(cleaned),
            "word_count": len(cleaned.split()),
            "is_ocr_used": False,
            "extraction_method": "text_decode",
            "success": bool(cleaned),
        }
    except Exception:
        return {
            "text": "",
            "char_count": 0,
            "word_count": 0,
            "is_ocr_used": False,
            "extraction_method": "unknown",
            "success": False,
        }
