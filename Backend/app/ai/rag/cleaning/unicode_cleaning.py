import unicodedata


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode using NFKC.

    Also standardizes different line separator characters.
    """

    text = unicodedata.normalize("NFKC", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Unicode line separators
    text = text.replace("\u2028", "\n")
    text = text.replace("\u2029", "\n")

    return text