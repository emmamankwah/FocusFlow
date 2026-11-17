"""Strip page numbers, repeated headers/footers and common notices."""

from __future__ import annotations

import re
from collections import Counter

MIN_REPEATS = 3
MAX_BOILERPLATE_LINE = 80

_PAGE_NUMBER = re.compile(
    r"^\s*(?:page\s*)?\d+\s*(?:(?:of|/)\s*\d+)?\s*$",
    re.IGNORECASE,
)
_PAGE_NUMBER_ORNAMENT = re.compile(
    r"^\s*[-\u2013\u2014\s]*\d+[-\u2013\u2014\s]*$",
)

_KNOWN_PATTERNS = [
    re.compile(r"^\s*\u00a9.*$", re.IGNORECASE),
    re.compile(r"^\s*copyright\b.*$", re.IGNORECASE),
    re.compile(r"^\s*all rights reserved\.?\s*$", re.IGNORECASE),
    re.compile(r"^\s*confidential\b.*$", re.IGNORECASE),
    re.compile(r"^\s*do not distribute\.?\s*$", re.IGNORECASE),
    re.compile(
        r"^\s*this (?:page|document) (?:is )?"
        r"(?:intentionally )?left blank\.?\s*$",
        re.IGNORECASE,
    ),
]

_URL_OR_DOMAIN = re.compile(
    r"^\s*(?:https?://|www\.)\S+|^\s*[\w.-]+\.(?:com|org|net|edu|gov)\b",
    re.IGNORECASE,
)


def is_page_number(line: str) -> bool:
    """Return True for page labels such as ``Page 3`` or ``3 of 9``."""
    stripped = line.strip()
    return bool(
        _PAGE_NUMBER.match(stripped)
        or _PAGE_NUMBER_ORNAMENT.match(stripped)
    )


def is_known_boilerplate(line: str) -> bool:
    """Return True for common copyright, confidentiality and print notices."""
    return any(pattern.match(line) for pattern in _KNOWN_PATTERNS)


def _looks_like_repeated_header_or_footer(line: str) -> bool:
    """Avoid dropping repeated prose; only infer likely header-like lines."""
    stripped = line.strip()
    words = stripped.split()
    multword_uppercase = (
        len(words) >= 2
        and any(character.isalpha() for character in stripped)
        and stripped == stripped.upper()
    )
    return multword_uppercase or bool(_URL_OR_DOMAIN.match(stripped))


def repeated_lines(
    text: str,
    min_repeats: int = MIN_REPEATS,
    max_line_chars: int = MAX_BOILERPLATE_LINE,
) -> set[str]:
    """Find short, repeated lines that resemble headers or footers."""
    counts = Counter(line.strip() for line in text.split("\n") if line.strip())
    return {
        line
        for line, count in counts.items()
        if (
            count >= min_repeats
            and len(line) <= max_line_chars
            and _looks_like_repeated_header_or_footer(line)
        )
    }


def remove_boilerplate(
    text: str,
    min_repeats: int = MIN_REPEATS,
    max_line_chars: int = MAX_BOILERPLATE_LINE,
) -> str:
    """Drop page numbers, likely repeated headers/footers and known notices."""
    if not text:
        return ""

    repeated = repeated_lines(text, min_repeats, max_line_chars)
    kept: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            kept.append(line)
            continue
        if is_page_number(stripped) or is_known_boilerplate(stripped):
            continue
        if stripped in repeated:
            continue
        kept.append(line)

    return "\n".join(kept)
