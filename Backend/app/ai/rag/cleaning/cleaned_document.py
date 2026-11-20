from cleaners.character_cleaner import clean_characters
from cleaners.unicode_cleaner import normalize_unicode
from cleaners.whitespace_cleaner import clean_whitespace
from cleaners.dehyphenation import dehyphenate
from cleaners.structure_cleaner import reconstruct_paragraphs

from cleaners.document_cleaner import (
    remove_repeated_lines,
    remove_page_numbers
)


def clean_page(
    text: str,
    remove_private_use: bool = False,
    reconstruct: bool = True
) -> str:
    """
    Clean an individual document page.
    """

    if not text:
        return ""

    # 1. Unicode normalization
    text = normalize_unicode(text)

    # 2. Character cleaning
    text = clean_characters(
        text,
        remove_private_use=remove_private_use
    )

    # 3. Whitespace cleaning
    text = clean_whitespace(text)

    # 4. Dehyphenation
    text = dehyphenate(text)

    # 5. Remove standalone page numbers
    text = remove_page_numbers(text)

    # 6. Paragraph reconstruction
    if reconstruct:
        text = reconstruct_paragraphs(text)

    return text.strip()


def clean_document(
    pages: list[str],
    remove_private_use: bool = False,
    reconstruct: bool = True,
    remove_headers: bool = True
) -> str:
    """
    Clean an entire document containing multiple pages.
    """

    if not pages:
        return ""

    # First normalize and clean individual pages
    cleaned_pages = [
        clean_page(
            page,
            remove_private_use=remove_private_use,
            reconstruct=False
        )
        for page in pages
    ]

    # Remove repeated headers and footers
    if remove_headers:

        cleaned_pages = remove_repeated_lines(
            cleaned_pages,
            threshold=0.5
        )

    # Reconstruct paragraphs after page-level cleaning
    if reconstruct:

        cleaned_pages = [
            reconstruct_paragraphs(page)
            for page in cleaned_pages
        ]

    # Combine pages
    return "\n\n".join(
        page.strip()
        for page in cleaned_pages
        if page.strip()
    )