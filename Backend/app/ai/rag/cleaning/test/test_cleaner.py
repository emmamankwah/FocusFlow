import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(backend_dir))

from app.ai.rag.cleaning import (
    clean_characters,
    clean_whitespace,
    dehyphenate,
    normalize_unicode,
    reconstruct_paragraphs,
    remove_boilerplate,
)


class TestDocumentCleaning(unittest.TestCase):

    def test_unicode_normalization(self):

        text = "ＡＢＣ ①"

        result = normalize_unicode(text)

        self.assertEqual(result, "ABC 1")

    def test_character_cleaning(self):

        text = "Hel\u200blo"

        result = clean_characters(text)

        self.assertEqual(result, "Hello")

    def test_whitespace_cleaning(self):

        text = "Hello     World\n\n\nPython"

        result = clean_whitespace(text)

        self.assertEqual(
            result,
            "Hello World\n\nPython"
        )

    def test_dehyphenation(self):

        text = "Artificial intelli-\ngence"

        result = dehyphenate(text)

        self.assertEqual(
            result,
            "Artificial intelligence"
        )

    def test_paragraph_reconstruction(self):

        text = (
            "Machine learning is a branch of\n"
            "artificial intelligence.\n\n"
            "Deep learning is a subset of machine learning."
        )

        result = reconstruct_paragraphs(text)

        self.assertEqual(
            result,
            "Machine learning is a branch of artificial intelligence.\n\n"
            "Deep learning is a subset of machine learning."
        )

    def test_preserves_bullet_lists(self):

        text = "- first item\n- second item"

        result = reconstruct_paragraphs(text)

        self.assertEqual(result, text)

    def test_preserves_headings_and_joins_body(self):

        text = "# Heading\nwrapped body\ncontinues here."

        result = reconstruct_paragraphs(text)

        self.assertEqual(
            result,
            "# Heading\nwrapped body continues here."
        )

    def test_preserves_code_fences(self):

        text = "```\nline one\nline two\n```"

        result = reconstruct_paragraphs(text)

        self.assertEqual(result, text)

    def test_repeated_headers(self):

        text = "\n".join(
            [
                "UNIVERSITY OF CAPE COAST\nIntroduction",
                "UNIVERSITY OF CAPE COAST\nChapter One",
                "UNIVERSITY OF CAPE COAST\nChapter Two",
            ]
        )

        result = remove_boilerplate(text)

        self.assertNotIn(
            "UNIVERSITY OF CAPE COAST",
            result
        )


if __name__ == "__main__":
    unittest.main()
