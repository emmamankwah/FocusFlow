"""Retrieve the most relevant chunks for a query."""

from __future__ import annotations

from . import config, embeddings, vector_store


def retrieve(
    user_id: int,
    query: str,
    top_k: int | None = None,
    document_ids: list[int] | None = None,
) -> list[dict]:
    top_k = top_k or config.TOP_K
    if document_ids is not None and not document_ids:
        document_ids = None

    vector = embeddings.embed_query(query)
    rows = vector_store.search_chunks(
        user_id=user_id,
        query_vector=embeddings.vector_to_sql(vector),
        top_k=top_k,
        document_ids=document_ids,
    )

    return [
        {
            "documentId": row["document_id"],
            "title": row["title"],
            "chunkIndex": row["chunk_index"],
            "content": row["content"],
            "score": float(row["score"]),
        }
        for row in rows
    ]
