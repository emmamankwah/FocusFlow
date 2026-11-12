"""Document ingestion: extract text, chunk it, embed it, persist it."""

from __future__ import annotations

from . import chunking, config, embeddings, loaders, vector_store


class IngestError(Exception):
    """A user-facing ingestion failure."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def ingest_file(
    user_id: int,
    title: str,
    filename: str | None,
    content_type: str | None,
    data: bytes,
) -> dict:
    size = len(data)
    limit = config.MAX_UPLOAD_MB * 1024 * 1024
    if size > limit:
        raise IngestError(f"File is larger than {config.MAX_UPLOAD_MB} MB.")

    try:
        text = loaders.extract_text(filename, content_type, data)
    except loaders.UnsupportedDocument as exc:
        raise IngestError(str(exc)) from exc

    return ingest_text(
        user_id,
        title,
        text,
        filename=filename,
        content_type=content_type,
        size_bytes=size,
    )


def ingest_text(
    user_id: int,
    title: str,
    text: str,
    filename: str | None = None,
    content_type: str | None = None,
    size_bytes: int | None = None,
) -> dict:
    text = (text or "").strip()
    if not text:
        raise IngestError("The document has no extractable text.")

    document = vector_store.create_document(
        user_id=user_id,
        title=title,
        filename=filename,
        content_type=content_type,
        size_bytes=size_bytes,
    )

    try:
        pieces = chunking.chunk_text(text)
        if not pieces:
            raise IngestError("The document has no extractable text.")

        vectors = embeddings.embed_texts(pieces)
        chunks = [
            {
                "chunkIndex": index,
                "content": piece,
                "tokenCount": chunking.approximate_token_count(piece),
                "embedding": embeddings.vector_to_sql(vector),
            }
            for index, (piece, vector) in enumerate(zip(pieces, vectors))
        ]

        vector_store.insert_chunks(document["id"], user_id, chunks)
        vector_store.set_document_status(document["id"], user_id, "ready")
    except Exception as exc:
        try:
            vector_store.set_document_status(
                document["id"],
                user_id,
                "failed",
                str(exc),
            )
        except Exception:
            # Preserve the original failure; the status update is best-effort.
            pass
        raise

    document["status"] = "ready"
    document["chunk_count"] = len(chunks)
    return document
