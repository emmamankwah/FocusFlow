"""Extract plain text from uploaded PDF, Word and text files."""

from __future__ import annotations

import io
from pathlib import Path

from pypdf import PdfReader

from . import loaders
from .loaders import UnsupportedDocument

__all__ = ["UnsupportedDocument", "extract_path", "extract_text"]


def _extract_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def extract_text(filename: str | None, content_type: str | None, data: bytes) -> str:
    """Extract the raw text contained in document bytes."""
    if loaders.extension_of(filename) == ".pdf" or content_type == "application/pdf":
        return _extract_pdf(data)
    return loaders.extract_text(filename, content_type, data)


def extract_path(path: str | Path) -> str:
    """Extract a document stored on the local filesystem."""
    file_path = Path(path)
    return extract_text(file_path.name, None, file_path.read_bytes())
