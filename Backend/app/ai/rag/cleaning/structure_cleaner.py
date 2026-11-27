import re


def is_heading(line: str) -> bool:
    """
    Basic heading detection (Markdown #, numbered, or short uppercase).
    """
    line = line.strip()

    if not line:
        return False

    # Markdown headings: # Heading, ## Subheading
    if re.match(r"^#{1,6}\s+\S+", line):
        return True

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

    Preserves blank lines, headings, list items and code fences.
    """
    if not text:
        return ""

    lines = text.splitlines()
    blocks = []
    current_paragraph = []
    in_code_block = False
    code_lines = []

    def flush_paragraph():
        if current_paragraph:
            blocks.append(("paragraph", " ".join(current_paragraph)))
            current_paragraph.clear()

    for raw_line in lines:
        line = raw_line.strip()

        if line.startswith("```"):
            flush_paragraph()
            if in_code_block:
                code_lines.append(raw_line)
                blocks.append(("code", "\n".join(code_lines)))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lines = [raw_line]
            continue

        if in_code_block:
            code_lines.append(raw_line)
            continue

        if not line:
            flush_paragraph()
            continue

        if is_heading(line):
            flush_paragraph()
            blocks.append(("heading", line))
            continue

        if is_list_item(line):
            flush_paragraph()
            blocks.append(("list", line))
            continue

        current_paragraph.append(line)

    flush_paragraph()
    if in_code_block and code_lines:
        blocks.append(("code", "\n".join(code_lines)))

    if not blocks:
        return ""

    result = []
    prev_type = None
    for b_type, content in blocks:
        if prev_type is None:
            result.append(content)
        elif prev_type == "list" and b_type == "list":
            result.append("\n" + content)
        elif prev_type == "heading" and b_type == "paragraph":
            result.append("\n" + content)
        else:
            result.append("\n\n" + content)
        prev_type = b_type

    return "".join(result)
