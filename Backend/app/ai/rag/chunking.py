"""Split documents into overlapping chunks for embedding."""

from __future__ import annotations

from . import config


def normalise(text: str) -> str:
    """Collapse trailing spaces and repeated blank lines without losing breaks."""
    lines = (
        text.replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
    )
    cleaned: list[str] = []
    previous_blank = False
    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            if not previous_blank and cleaned:
                cleaned.append("")
            previous_blank = True
            continue
        cleaned.append(stripped)
        previous_blank = False
    return "\n".join(cleaned).strip()


def _find_split(text: str, start: int, end: int) -> int:
    """Return a split point near ``end``, preferring paragraph/sentence breaks."""
    window_start = start + int((end - start) * 0.6)
    segment = text[window_start:end]

    for marker in ("\n\n", "\n", ". "):
        cut = segment.rfind(marker)
        if cut != -1:
            width = len(marker) if marker != ". " else 1
            candidate = window_start + cut + width
            if candidate > start:
                return candidate
    return end


def chunk_text(
    text: str,
    size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    size = size or config.CHUNK_CHARS
    overlap = config.CHUNK_OVERLAP if overlap is None else overlap

    normalised = normalise(text)
    if not normalised:
        return []
    if size <= 0:
        raise ValueError("Chunk size must be positive.")

    overlap = max(0, min(overlap, size // 2))
    chunks: list[str] = []
    start = 0
    length = len(normalised)

    while start < length:
        end = min(start + size, length)
        if end < length:
            end = _find_split(normalised, start, end)

        chunk = normalised[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= length:
            break
        start = max(end - overlap, start + 1)

    return chunks


def approximate_token_count(text: str) -> int:
    return max(1, len(text) // 4)
