import sys
import unittest
from pathlib import Path

# Add Backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.ai.rag import chunking, cleaning, embeddings, loaders, pipeline


class ChunkingTests(unittest.TestCase):
    def test_blank_text_returns_no_chunks(self):
        self.assertEqual(chunking.chunk_text("   \n\n "), [])

    def test_short_text_stays_one_chunk(self):
        self.assertEqual(chunking.chunk_text("hello world", size=100), ["hello world"])

    def test_chunks_respect_size(self):
        chunks = chunking.chunk_text("A" * 1000, size=300, overlap=50)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 300)

    def test_prefers_sentence_boundaries(self):
        text = "Sentence one. " * 30
        chunks = chunking.chunk_text(text, size=120, overlap=20)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.strip() for chunk in chunks))

    def test_long_text_advances(self):
        chunks = chunking.chunk_text("word " * 400, size=200, overlap=40)
        self.assertGreater(len(chunks), 1)


class CleaningTests(unittest.TestCase):
    def test_strips_trailing_whitespace(self):
        self.assertEqual(cleaning.clean_text("hello   \nworld\t\n"), "hello\nworld")

    def test_removes_hidden_and_control_symbols(self):
        self.assertEqual(
            cleaning.clean_text("a\u200bb\x00c\ufffdd"),
            "abcd",
        )

    def test_collapses_spacing_and_blank_lines(self):
        self.assertEqual(
            cleaning.clean_text("a \t b\n\n\n\nc"),
            "a b\n\nc",
        )

    def test_empty_input(self):
        self.assertEqual(cleaning.clean_text(None), "")
        self.assertEqual(cleaning.clean_text("   \n "), "")


class LoaderTests(unittest.TestCase):
    def test_reads_txt(self):
        self.assertEqual(
            loaders.extract_text("notes.txt", "text/plain", "héllo".encode("utf-8")),
            "héllo",
        )

    def test_reads_markdown_by_extension(self):
        self.assertEqual(
            loaders.extract_text("readme.md", None, b"# Title"),
            "# Title",
        )

    def test_rejects_unsupported_type(self):
        with self.assertRaises(loaders.UnsupportedDocument):
            loaders.extract_text("archive.zip", "application/zip", b"PK\x03\x04")


class EmbeddingTests(unittest.TestCase):
    def tearDown(self):
        embeddings.set_encoder(None)

    def test_encoder_override(self):
        embeddings.set_encoder(lambda texts: [[0.5, 0.5] for _ in texts])
        self.assertEqual(embeddings.embed_texts(["a", "b"]), [[0.5, 0.5], [0.5, 0.5]])
        self.assertEqual(embeddings.embed_query("a"), [0.5, 0.5])

    def test_empty_input(self):
        self.assertEqual(embeddings.embed_texts([]), [])

    def test_vector_serialisation(self):
        self.assertEqual(
            embeddings.vector_to_sql([1.0, 0.5]),
            "[1.00000000,0.50000000]",
        )


class PipelineTests(unittest.TestCase):
    def test_build_context_numbers_sources(self):
        context = pipeline.build_context(
            [
                {"title": "Doc A", "content": "alpha"},
                {"title": "Doc B", "content": "beta"},
            ]
        )
        self.assertIn("[1] Doc A", context)
        self.assertIn("[2] Doc B", context)
        self.assertIn("alpha", context)

    def test_build_context_truncates(self):
        context = pipeline.build_context(
            [{"title": "Doc", "content": "x" * 100} for _ in range(5)],
            max_chars=150,
        )
        self.assertLessEqual(len(context), 150)
        self.assertNotIn("[2]", context)


if __name__ == "__main__":
    unittest.main()
