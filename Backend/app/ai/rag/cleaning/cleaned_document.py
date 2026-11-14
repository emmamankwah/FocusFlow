import re
from collections import Counter


def normalize_header_line(line: str) -> str:
    """
    Normalize lines before comparing them.
    """

    line = line.strip().lower()

    line = re.sub(r"\s+", " ", line)

    return line


def detect_repeated_lines(
    pages: list[str],
    threshold: float = 0.5
) -> set[str]:
    """
    Detect lines appearing in a sufficient proportion
    of document pages.

    Each page is counted at most once per line.
    """

    if not pages:
        return set()

    counts = Counter()

    for page in pages:

        lines = {
            normalize_header_line(line)
            for line in page.splitlines()
            if line.strip()
        }

        counts.update(lines)

    minimum_count = max(
        2,
        int(len(pages) * threshold)
    )

    return {
        line
        for line, count in counts.items()
        if count >= minimum_count
    }


def remove_repeated_lines(
    pages: list[str],
    threshold: float = 0.5
) -> list[str]:
    """
    Remove repeated headers and footers.
    """

    repeated_lines = detect_repeated_lines(
        pages,
        threshold
    )

    cleaned_pages = []

    for page in pages:

        lines = page.splitlines()

        cleaned_lines = [
            line
            for line in lines
            if normalize_header_line(line)
            not in repeated_lines
        ]

        cleaned_pages.append(
            "\n".join(cleaned_lines)
        )

    return cleaned_pages


def remove_page_numbers(text: str) -> str:
    """
    Remove standalone numeric page markers.

    Conservative: only removes lines consisting
    entirely of a number.
    """

    return re.sub(
        r"(?m)^\s*\d{1,4}\s*$",
        "",
        text
    )