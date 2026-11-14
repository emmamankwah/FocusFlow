import re


_HORIZONTAL_SPACE = re.compile(
    r"[^\S\n]+"
)

_BLANK_LINES = re.compile(
    r"\n{3,}"
)


def normalize_line_endings(text: str) -> str:
    """
    Standardize line endings.
    """

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return text


def normalize_spaces(text: str) -> str:
    """
    Replace consecutive horizontal whitespace
    with a single space.
    """

    return _HORIZONTAL_SPACE.sub(" ", text)


def remove_trailing_spaces(text: str) -> str:
    """
    Remove trailing whitespace from every line.
    """

    lines = text.split("\n")

    lines = [
        line.rstrip()
        for line in lines
    ]

    return "\n".join(lines)


def normalize_blank_lines(text: str) -> str:
    """
    Replace three or more consecutive newlines
    with two newlines.
    """

    return _BLANK_LINES.sub("\n\n", text)


def clean_whitespace(text: str) -> str:
    """
    Apply whitespace cleaning.
    """

    text = normalize_line_endings(text)

    text = normalize_spaces(text)

    text = remove_trailing_spaces(text)

    text = normalize_blank_lines(text)

    return text.strip()