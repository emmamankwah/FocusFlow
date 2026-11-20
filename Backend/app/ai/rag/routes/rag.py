"""RAG routes: document management and grounded querying."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.authentication.security.current_user import get_current_user_id

from .. import config, ingest, pipeline, vector_store
from ..schemas import InlineDocument, RagQuery

router = APIRouter(prefix="/ai", tags=["rag"])
logger = logging.getLogger(__name__)


def _document_json(row: dict) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "filename": row.get("filename"),
        "contentType": row.get("content_type"),
        "sizeBytes": row.get("size_bytes"),
        "status": row["status"],
        "error": row.get("error"),
        "chunkCount": row.get("chunk_count"),
        "createdAt": row.get("created_at"),
        "updatedAt": row.get("updated_at"),
    }


@router.post("/documents")
def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    user_id: int = Depends(get_current_user_id),
):
    # Sync def: Starlette runs it in a threadpool, so the CPU-bound embedding
    # call does not block the event loop.
    limit = ingest.max_upload_bytes()
    data = file.file.read(limit + 1)
    if len(data) > limit:
        return {"error": f"File is larger than {config.MAX_UPLOAD_MB} MB."}
    filename = file.filename or "document"
    resolved_title = (title or Path(filename).stem or "Untitled document").strip()[:200]

    try:
        row = ingest.ingest_file(
            user_id,
            resolved_title,
            filename,
            file.content_type,
            data,
        )
    except ingest.IngestError as exc:
        return {"error": exc.message}
    except ConnectionError:
        return {"error": "Database connection failed."}
    except Exception:
        logger.exception("RAG upload failed for user %s", user_id)
        return {"error": "Could not process the document."}

    return _document_json(row)


@router.post("/documents/text")
def create_text_document(
    payload: InlineDocument,
    user_id: int = Depends(get_current_user_id),
):
    title = payload.title.strip()[:200]
    try:
        row = ingest.ingest_text(
            user_id,
            title,
            payload.content,
            content_type="text/plain",
            size_bytes=len(payload.content.encode("utf-8")),
        )
    except ingest.IngestError as exc:
        return {"error": exc.message}
    except ConnectionError:
        return {"error": "Database connection failed."}
    except Exception:
        logger.exception("RAG text ingest failed for user %s", user_id)
        return {"error": "Could not process the document."}

    return _document_json(row)


@router.get("/documents")
def list_documents(user_id: int = Depends(get_current_user_id)):
    try:
        rows = vector_store.list_documents(user_id)
    except ConnectionError:
        return {"error": "Database connection failed."}
    return {"documents": [_document_json(row) for row in rows]}


@router.get("/documents/{document_id}")
def get_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
):
    try:
        row = vector_store.get_document(user_id, document_id)
    except ConnectionError:
        return {"error": "Database connection failed."}
    if row is None:
        return {"error": "Document not found."}
    return _document_json(row)


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
):
    try:
        deleted = vector_store.delete_document(user_id, document_id)
    except ConnectionError:
        return {"error": "Database connection failed."}
    if not deleted:
        return {"error": "Document not found."}
    return {"message": "Document deleted."}


@router.post("/rag/query")
def rag_query(
    payload: RagQuery,
    user_id: int = Depends(get_current_user_id),
):
    query = payload.query.strip()
    if not query:
        return {"error": "Ask a question about your documents."}

    try:
        return pipeline.answer(
            user_id,
            query,
            top_k=payload.topK,
            document_ids=payload.documentIds,
        )
    except ConnectionError:
        return {"error": "Database connection failed."}
    except Exception:
        logger.exception("RAG query failed for user %s", user_id)
        return {"error": "Could not answer from your documents."}
