import re


def remove_line_end_hyphens(text: str) -> str:
    """
    Reconstruct words broken by line-ending hyphens.

    This is a conservative heuristic for English text.
    """

    pattern = re.compile(
        r"(?<=[A-Za-z])-\n(?=[a-z])"
    )

    return pattern.sub("", text)


def dehyphenate(text: str) -> str:
    """
    Apply dehyphenation.
    """

    return remove_line_end_hyphens(text)