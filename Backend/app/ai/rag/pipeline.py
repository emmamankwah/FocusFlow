"""Grounded answering over retrieved document chunks."""

from __future__ import annotations

from . import config

NO_ANSWER = (
    "I could not find anything in your documents that answers that. "
    "Add a document and try again."
)


def build_context(chunks: list[dict], max_chars: int | None = None) -> str:
    max_chars = max_chars or config.MAX_CONTEXT_CHARS
    parts: list[str] = []
    used = 0

    for index, chunk in enumerate(chunks, start=1):
        block = f"[{index}] {chunk['title']}\n{chunk['content']}"
        if parts and used + len(block) > max_chars:
            break
        parts.append(block)
        used += len(block)

    return "\n\n".join(parts)


def answer(
    user_id: int,
    query: str,
    top_k: int | None = None,
    document_ids: list[int] | None = None,
) -> dict:
    from . import retriever

    chunks = retriever.retrieve(
        user_id,
        query,
        top_k=top_k,
        document_ids=document_ids,
    )
    if not chunks:
        return {"reply": NO_ANSWER, "sources": []}

    context = build_context(chunks)

    from app.ai.chatbot.chat_service import get_reply
    from app.ai.chatbot.models import ChatMessage

    reply = get_reply([ChatMessage(role="user", content=query)], context)

    sources = [
        {
            "documentId": chunk["documentId"],
            "title": chunk["title"],
            "chunkIndex": chunk["chunkIndex"],
            "snippet": chunk["content"][:300],
            "score": round(chunk["score"], 4),
        }
        for chunk in chunks
    ]
    return {"reply": reply, "sources": sources}
