"""Retrieve the most relevant chunks for a query."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from . import config, embeddings, vector_store

_RRF_K = 60
_CANDIDATE_MULTIPLIER = 2


def _search_vector(
    user_id: int,
    query: str,
    top_k: int,
    document_ids: list[int] | None,
) -> list[dict]:
    vector = embeddings.embed_query(query)
    return vector_store.search_chunks(
        user_id=user_id,
        query_vector=embeddings.vector_to_sql(vector),
        top_k=top_k,
        document_ids=document_ids,
    )


def _fuse_rankings(*ranked_lists: list[dict]) -> list[dict]:
    """Merge ranked chunk lists with reciprocal rank fusion."""
    fused: dict[int, dict] = {}
    fused_scores: dict[int, float] = {}

    for rows in ranked_lists:
        for rank, row in enumerate(rows, start=1):
            chunk_id = row["id"]
            if chunk_id not in fused:
                fused[chunk_id] = row
                fused_scores[chunk_id] = 0.0
            fused_scores[chunk_id] += 1.0 / (_RRF_K + rank)

    # Keep the combined score on a 0–1 scale, matching the existing score
    # field's range while reflecting agreement between both retrieval methods.
    max_score = 2.0 / (_RRF_K + 1)
    ordered_ids = sorted(
        fused,
        key=lambda chunk_id: (
            -fused_scores[chunk_id],
            fused[chunk_id]["document_id"],
            fused[chunk_id]["chunk_index"],
        ),
    )

    results = []
    for chunk_id in ordered_ids:
        row = fused[chunk_id]
        results.append(
            {
                "documentId": row["document_id"],
                "title": row["title"],
                "chunkIndex": row["chunk_index"],
                "content": row["content"],
                "score": fused_scores[chunk_id] / max_score,
            }
        )
    return results


def retrieve(
    user_id: int,
    query: str,
    top_k: int | None = None,
    document_ids: list[int] | None = None,
) -> list[dict]:
    top_k = top_k or config.TOP_K
    if document_ids is not None and not document_ids:
        document_ids = None

    candidate_k = top_k * _CANDIDATE_MULTIPLIER
    with ThreadPoolExecutor(max_workers=2) as executor:
        vector_search = executor.submit(
            _search_vector,
            user_id,
            query,
            candidate_k,
            document_ids,
        )
        keyword_search = executor.submit(
            vector_store.search_keyword_chunks,
            user_id=user_id,
            query=query,
            top_k=candidate_k,
            document_ids=document_ids,
        )
        vector_rows = vector_search.result()
        keyword_rows = keyword_search.result()

    return _fuse_rankings(vector_rows, keyword_rows)[:top_k]
