import io
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

# Add Backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.ai.rag import chunking, cleaning, embeddings, extract, loaders, pipeline, retriever
from app.ai.rag.cleaning import boilerplate
from app.ai.rag.routes import rag as rag_routes


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


class ExtractionTests(unittest.TestCase):
    def test_extracts_raw_text(self):
        self.assertEqual(
            extract.extract_text("notes.txt", "text/plain", b"hello   \nworld\x00"),
            "hello   \nworld\x00",
        )

    def test_rejects_unsupported_type(self):
        with self.assertRaises(extract.UnsupportedDocument):
            extract.extract_text("archive.zip", "application/zip", b"PK\x03\x04")

    def test_pdf_uses_pdf_reader(self):
        page = mock.Mock()
        page.extract_text.return_value = "pdf text"
        reader = mock.Mock(pages=[page])

        with mock.patch("pypdf.PdfReader", return_value=reader) as pdf_reader:
            self.assertEqual(
                extract.extract_text("report.pdf", "application/pdf", b"%PDF-1.4"),
                "pdf text",
            )

        pdf_reader.assert_called_once()


class BoilerplateTests(unittest.TestCase):
    def test_removes_page_numbers(self):
        self.assertEqual(
            boilerplate.remove_boilerplate("Body text\nPage 3\nMore text"),
            "Body text\nMore text",
        )

    def test_removes_repeated_header(self):
        text = "ACME Corp\nfirst\nACME Corp\nsecond\nACME Corp\nthird"
        self.assertEqual(
            boilerplate.remove_boilerplate(text),
            "first\nsecond\nthird",
        )

    def test_removes_known_notices(self):
        self.assertEqual(
            boilerplate.remove_boilerplate("Hello\nAll rights reserved."),
            "Hello",
        )

    def test_keeps_unique_short_lines(self):
        self.assertEqual(
            boilerplate.remove_boilerplate("Title\nOne\nTwo"),
            "Title\nOne\nTwo",
        )

    def test_empty_input(self):
        self.assertEqual(boilerplate.remove_boilerplate(""), "")


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


class RetrieverTests(unittest.TestCase):
    def test_merges_vector_and_keyword_results_and_deduplicates_chunks(self):
        vector_rows = [
            {
                "id": 10,
                "document_id": 3,
                "title": "Doc",
                "chunk_index": 2,
                "content": "shared passage",
                "score": 0.87,
            },
            {
                "id": 12,
                "document_id": 3,
                "title": "Doc",
                "chunk_index": 3,
                "content": "vector passage",
                "score": 0.81,
            },
        ]
        keyword_rows = [
            {
                "id": 10,
                "document_id": 3,
                "title": "Doc",
                "chunk_index": 2,
                "content": "shared passage",
                "score": 0.6,
            },
            {
                "id": 11,
                "document_id": 3,
                "title": "Doc",
                "chunk_index": 4,
                "content": "keyword passage",
                "score": 0.5,
            },
        ]

        with mock.patch.object(
            retriever.embeddings, "embed_query", return_value=[0.1, 0.2]
        ) as embed, mock.patch.object(
            retriever.embeddings, "vector_to_sql", return_value="[0.1,0.2]"
        ), mock.patch.object(
            retriever.vector_store, "search_chunks", return_value=vector_rows
        ) as vector_search, mock.patch.object(
            retriever.vector_store,
            "search_keyword_chunks",
            return_value=keyword_rows,
        ) as keyword_search:
            result = retriever.retrieve(5, "question", top_k=2, document_ids=[3])

        embed.assert_called_once_with("question")
        vector_search.assert_called_once_with(
            user_id=5,
            query_vector="[0.1,0.2]",
            top_k=4,
            document_ids=[3],
        )
        keyword_search.assert_called_once_with(
            user_id=5,
            query="question",
            top_k=4,
            document_ids=[3],
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["content"], "shared passage")
        self.assertIn("keyword passage", [row["content"] for row in result])
        self.assertEqual(len({row["content"] for row in result}), len(result))
        self.assertTrue(all(0 <= row["score"] <= 1 for row in result))


class PipelineAnswerTests(unittest.TestCase):
    def test_returns_sources(self):
        chunks = [
            {
                "documentId": 1,
                "title": "Doc",
                "chunkIndex": 0,
                "content": "alpha",
                "score": 0.9,
            }
        ]

        with mock.patch(
            "app.ai.rag.retriever.retrieve", return_value=chunks
        ), mock.patch(
            "app.ai.chatbot.chat_service.get_reply", return_value="answer"
        ):
            result = pipeline.answer(1, "question", top_k=2)

        self.assertEqual(result["reply"], "answer")
        self.assertEqual(result["sources"][0]["snippet"], "alpha")
        self.assertEqual(result["sources"][0]["score"], 0.9)

    def test_returns_no_answer_without_chunks(self):
        with mock.patch("app.ai.rag.retriever.retrieve", return_value=[]):
            result = pipeline.answer(1, "question")

        self.assertEqual(result["sources"], [])
        self.assertEqual(result["reply"], pipeline.NO_ANSWER)


class BoundedBytesIO(io.BytesIO):
    def read(self, size=-1):
        if size is None or size < 0:
            raise AssertionError("upload was read without a size limit")
        return super().read(size)


class DocumentUploadTests(unittest.TestCase):
    def test_rejects_oversized_upload(self):
        upload = SimpleNamespace(
            file=BoundedBytesIO(b"12345"),
            filename="big.txt",
            content_type="text/plain",
        )

        with mock.patch.object(
            rag_routes.ingest, "max_upload_bytes", return_value=4
        ):
            result = rag_routes.upload_document(upload, title=None, user_id=1)

        self.assertIn("error", result)

    def test_passes_bounded_data_to_ingest(self):
        upload = SimpleNamespace(
            file=BoundedBytesIO(b"1234"),
            filename="small.txt",
            content_type="text/plain",
        )

        with mock.patch.object(
            rag_routes.ingest, "max_upload_bytes", return_value=10
        ), mock.patch.object(
            rag_routes.ingest,
            "ingest_file",
            return_value={"id": 1, "title": "Small", "status": "ready"},
        ) as ingest_file:
            result = rag_routes.upload_document(upload, title="Small", user_id=1)

        ingest_file.assert_called_once_with(
            1, "Small", "small.txt", "text/plain", b"1234"
        )
        self.assertEqual(result["id"], 1)


if __name__ == "__main__":
    unittest.main()
