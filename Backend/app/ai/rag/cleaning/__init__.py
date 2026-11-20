"""Text cleaning helpers applied before chunking."""

from __future__ import annotations

from .boilerplate import remove_boilerplate
from .character_cleaning import clean_characters
from .dehyphenation import dehyphenate
from .structure_cleaner import reconstruct_paragraphs
from .unicode_cleaning import normalize_unicode
from .whitespace_cleaner import clean_whitespace


def clean_text(text: str | None) -> str:
    """Apply the standard cleaning pipeline to extracted text."""
    if not text:
        return ""
    text = normalize_unicode(text)
    text = clean_characters(text)
    text = dehyphenate(text)
    return clean_whitespace(text)
