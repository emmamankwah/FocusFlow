import re


def is_heading(line: str) -> bool:
    """
    Basic heading detection.
    """

    line = line.strip()

    if not line:
        return False

    # Numbered headings: 1. Introduction
    if re.match(r"^\d+(\.\d+)*\.?\s+\S+", line):
        return True

    # Short uppercase headings
    if line.isupper() and len(line) < 100:
        return True

    return False


def is_list_item(line: str) -> bool:
    """
    Detect common list markers.
    """

    return bool(
        re.match(
            r"^\s*(?:[-*•]|\d+[.)]|[a-zA-Z][.)])\s+",
            line
        )
    )


def reconstruct_paragraphs(text: str) -> str:
    """
    Join wrapped lines within paragraphs.

    Preserves blank lines, headings and list items.
    """

    lines = text.splitlines()

    paragraphs = []
    current_paragraph = []

    def flush():
        if current_paragraph:
            paragraphs.append(
                " ".join(current_paragraph)
            )
            current_paragraph.clear()

    for line in lines:

        line = line.strip()

        if not line:
            flush()
            continue

        if is_heading(line) or is_list_item(line):

            flush()
            paragraphs.append(line)
            continue

        current_paragraph.append(line)

    flush()

    return "\n\n".join(paragraphs)