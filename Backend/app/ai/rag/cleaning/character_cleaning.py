import re
import unicodedata


# Characters that should generally be removed
_INVISIBLE = re.compile(
    "[\u00ad\u200b\u200e\u200f\u2060\ufeff\ufffd]"
)

# Control characters
_CONTROL = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]"
)


def remove_control_characters(text: str) -> str:
    """
    Remove unwanted control characters.
    """
    return _CONTROL.sub("", text)


def remove_invisible_characters(text: str) -> str:
    """
    Remove selected invisible formatting characters.

    Preserves zero-width joiners and non-joiners because
    they can be meaningful in some writing systems.
    """
    return _INVISIBLE.sub("", text)


def remove_private_use_characters(text: str) -> str:
    """
    Remove private-use Unicode characters.

    These sometimes originate from custom PDF fonts.
    Use only when these characters are known to be unwanted.
    """
    return "".join(
        char for char in text
        if not unicodedata.category(char) == "Co"
    )


def clean_characters(
    text: str,
    remove_private_use: bool = False
) -> str:
    """
    Apply character-level cleaning.
    """

    text = remove_control_characters(text)

    text = remove_invisible_characters(text)

    if remove_private_use:
        text = remove_private_use_characters(text)

    return text