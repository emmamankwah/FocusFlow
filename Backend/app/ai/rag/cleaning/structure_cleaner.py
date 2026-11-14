"""Reconstruct paragraphs from hard-wrapped text."""

from __future__ import annotations

import re

_PARAGRAPH_BREAK = re.compile(r"\n\s*\n")
_HORIZONTAL_SPACE = re.compile(r"[^\S\n]+")


def reconstruct_paragraphs(text: str) -> str:
    """Join wrapped lines inside a paragraph while keeping paragraph breaks."""
    if not text:
        return ""

    paragraphs: list[str] = []
    for block in _PARAGRAPH_BREAK.split(text):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        paragraph = _HORIZONTAL_SPACE.sub(" ", " ".join(lines)).strip()
        paragraphs.append(paragraph)

    return "\n\n".join(paragraphs)
