import unittest

from cleaners.character_cleaner import clean_characters
from cleaners.unicode_cleaner import normalize_unicode
from cleaners.whitespace_cleaner import clean_whitespace
from cleaners.dehyphenation import dehyphenate
from cleaners.structure_cleaner import reconstruct_paragraphs
from cleaners.document_cleaner import remove_repeated_lines


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

    def test_repeated_headers(self):

        pages = [
            "UNIVERSITY OF CAPE COAST\nIntroduction",
            "UNIVERSITY OF CAPE COAST\nChapter One",
            "UNIVERSITY OF CAPE COAST\nChapter Two"
        ]

        result = remove_repeated_lines(pages)

        for page in result:
            self.assertNotIn(
                "UNIVERSITY OF CAPE COAST",
                page
            )


if __name__ == "__main__":
    unittest.main()