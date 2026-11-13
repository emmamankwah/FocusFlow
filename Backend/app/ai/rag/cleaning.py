"""Clean text extracted from PDFs, Word files and other documents."""

from __future__ import annotations

import re
import unicodedata

# Invisible formatting marks and private-use glyphs that leak out of PDF/Word
# extraction (zero-width spaces, bidi controls, replacement chars, icon fonts).
_INVISIBLE = re.compile(
    "[\u00ad\u061c\u115f\u1160\u180e\u200b-\u200f"
    "\u202a-\u202e\u2060-\u206f\ufeff\ufff9-\ufffb\ufffd\ue000-\uf8ff]"
)
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_HORIZONTAL_SPACE = re.compile(r"[ \t\f\v\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000]+")
_BLANK_LINES = re.compile(r"\n{3,}")


def remove_hidden_characters(text: str) -> str:
    """Drop control characters, zero-width marks and orphaned glyphs."""
    return _CONTROL.sub("", _INVISIBLE.sub("", text))


def clean_text(text: str | None) -> str:
    """Normalise document text: strip trailing whitespace, tidy spacing and junk."""
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = unicodedata.normalize("NFKC", text)
    text = remove_hidden_characters(text)
    text = _HORIZONTAL_SPACE.sub(" ", text)

    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = _BLANK_LINES.sub("\n\n", text)
    return text.strip()
