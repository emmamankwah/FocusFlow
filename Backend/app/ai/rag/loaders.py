"""Extract plain text from uploaded documents."""

from __future__ import annotations

import io
from pathlib import Path


class UnsupportedDocument(Exception):
    """Raised when a file type cannot be read."""


def extension_of(filename: str | None) -> str:
    return Path(filename or "").suffix.lower()


def extract_text(filename: str | None, content_type: str | None, data: bytes) -> str:
    ext = extension_of(filename)

    if ext == ".pdf":
        return _extract_pdf(data)
    if ext == ".docx":
        return _extract_docx(data)
    if ext in {".txt", ".md"} or (content_type or "").startswith("text/"):
        return _decode_text(data)

    raise UnsupportedDocument(
        f"Unsupported document type: {ext or content_type or 'unknown'}. "
        "Upload a .txt, .md, .pdf or .docx file."
    )


def _decode_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _extract_docx(data: bytes) -> str:
    from docx import Document

    document = Document(io.BytesIO(data))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)
