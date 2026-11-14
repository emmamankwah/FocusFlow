import sys
import unittest
from pathlib import Path
from unittest import mock

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.ai.rag import ingest


class IngestTests(unittest.TestCase):
    def _run_file(self, filename, content_type, chunk_text=None):
        calls = []
        document = {"id": 7, "title": "Doc", "status": "processing"}
        chunk_mock = mock.Mock()
        if chunk_text is None:
            chunk_mock.return_value = ["piece"]
        else:
            chunk_mock.side_effect = chunk_text

        with mock.patch.object(
            ingest.extract, "extract_text", return_value="raw text"
        ), mock.patch.object(
            ingest.cleaning,
            "clean_text",
            side_effect=lambda value: calls.append("clean") or value,
        ), mock.patch.object(
            ingest.boilerplate,
            "remove_boilerplate",
            side_effect=lambda value: calls.append("boilerplate") or value,
        ), mock.patch.object(
            ingest.cleaning,
            "reconstruct_paragraphs",
            side_effect=lambda value: calls.append("reconstruct") or value,
        ), mock.patch.object(
            ingest.chunking, "chunk_text", chunk_mock
        ), mock.patch.object(
            ingest.chunking, "approximate_token_count", return_value=1
        ), mock.patch.object(
            ingest.embeddings, "embed_texts", return_value=[[0.1, 0.2]]
        ), mock.patch.object(
            ingest.embeddings, "vector_to_sql", return_value="[0.1,0.2]"
        ), mock.patch.object(
            ingest.vector_store, "create_document", return_value=dict(document)
        ), mock.patch.object(
            ingest.vector_store, "store_document_chunks"
        ) as store, mock.patch.object(
            ingest.vector_store, "set_document_status"
        ) as set_status:
            result = ingest.ingest_file(
                1, "Doc", filename, content_type, b"data"
            )

        return calls, store, set_status, result

    def test_pdf_runs_boilerplate_before_reconstruction(self):
        calls, store, set_status, result = self._run_file(
            "doc.pdf", "application/pdf"
        )

        self.assertEqual(calls, ["clean", "boilerplate", "reconstruct"])
        store.assert_called_once()
        document_id, user_id, chunks = store.call_args.args
        self.assertEqual((document_id, user_id), (7, 1))
        self.assertEqual(chunks[0]["chunkIndex"], 0)
        set_status.assert_not_called()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["chunk_count"], 1)

    def test_docx_reconstructs_paragraphs(self):
        calls, _, _, _ = self._run_file(
            "doc.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        self.assertEqual(calls, ["clean", "boilerplate", "reconstruct"])

    def test_txt_skips_reconstruction(self):
        calls, _, _, _ = self._run_file("notes.txt", "text/plain")

        self.assertEqual(calls, ["clean", "boilerplate"])

    def test_inline_text_skips_reconstruction(self):
        calls = []
        document = {"id": 3, "title": "Doc", "status": "processing"}

        with mock.patch.object(
            ingest.cleaning,
            "clean_text",
            side_effect=lambda value: calls.append("clean") or value,
        ), mock.patch.object(
            ingest.boilerplate,
            "remove_boilerplate",
            side_effect=lambda value: calls.append("boilerplate") or value,
        ), mock.patch.object(
            ingest.cleaning,
            "reconstruct_paragraphs",
            side_effect=lambda value: calls.append("reconstruct") or value,
        ), mock.patch.object(
            ingest.chunking, "chunk_text", return_value=["piece"]
        ), mock.patch.object(
            ingest.chunking, "approximate_token_count", return_value=1
        ), mock.patch.object(
            ingest.embeddings, "embed_texts", return_value=[[0.1]]
        ), mock.patch.object(
            ingest.embeddings, "vector_to_sql", return_value="[0.1]"
        ), mock.patch.object(
            ingest.vector_store, "create_document", return_value=dict(document)
        ), mock.patch.object(
            ingest.vector_store, "store_document_chunks"
        ), mock.patch.object(
            ingest.vector_store, "set_document_status"
        ):
            ingest.ingest_text(1, "Doc", "inline text")

        self.assertEqual(calls, ["clean", "boilerplate"])

    def test_failure_marks_document_failed(self):
        document = {"id": 9, "title": "Doc", "status": "processing"}

        with mock.patch.object(
            ingest.cleaning, "clean_text", side_effect=lambda value: value
        ), mock.patch.object(
            ingest.boilerplate, "remove_boilerplate", side_effect=lambda value: value
        ), mock.patch.object(
            ingest.chunking, "chunk_text", side_effect=RuntimeError("boom")
        ), mock.patch.object(
            ingest.vector_store, "create_document", return_value=dict(document)
        ), mock.patch.object(
            ingest.vector_store, "store_document_chunks"
        ) as store, mock.patch.object(
            ingest.vector_store, "set_document_status"
        ) as set_status:
            with self.assertRaises(RuntimeError):
                ingest.ingest_text(1, "Doc", "text")

        store.assert_not_called()
        set_status.assert_called_once_with(9, 1, "failed", "boom")

    def test_rejects_oversized_file_before_extraction(self):
        with mock.patch.object(
            ingest, "max_upload_bytes", return_value=2
        ), mock.patch.object(
            ingest.extract, "extract_text"
        ) as extract_text:
            with self.assertRaises(ingest.IngestError):
                ingest.ingest_file(1, "Doc", "big.txt", "text/plain", b"123")

        extract_text.assert_not_called()


if __name__ == "__main__":
    unittest.main()
