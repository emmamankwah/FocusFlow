"""Reconstruct paragraphs from hard-wrapped text."""

from __future__ import annotations

import re

_PARAGRAPH_BREAK = re.compile(r"\n\s*\n")
_HORIZONTAL_SPACE = re.compile(r"[^\S\n]+")
_LIST_ITEM = re.compile(r"^\s*(?:[-*+•]|\d+[.)])\s+")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+")
_FENCE = re.compile(r"^\s*(?:```|~~~)")


def _is_structural(line: str) -> bool:
    return bool(_LIST_ITEM.match(line) or _HEADING.match(line) or _FENCE.match(line))


def reconstruct_paragraphs(text: str) -> str:
    """Join wrapped lines inside a paragraph while keeping structure."""
    if not text:
        return ""

    paragraphs: list[str] = []

    for block in _PARAGRAPH_BREAK.split(text):
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue

        output: list[str] = []
        in_fence = False

        for raw_line in lines:
            stripped = raw_line.strip()
            if _FENCE.match(stripped):
                output.append(raw_line)
                in_fence = not in_fence
                continue
            if in_fence:
                output.append(raw_line)
                continue
            if not output:
                output.append(raw_line)
                continue
            if _is_structural(stripped):
                output.append(raw_line)
                continue
            previous = output[-1]
            if _HEADING.match(previous) or _FENCE.match(previous):
                output.append(raw_line)
                continue
            output[-1] = _HORIZONTAL_SPACE.sub(
                " ", f"{previous} {stripped}"
            ).strip()

        paragraphs.append("\n".join(output))

    return "\n\n".join(paragraphs)
