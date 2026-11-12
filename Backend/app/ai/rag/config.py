"""Configuration for the retrieval-augmented generation (RAG) layer."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Backend/.env (parents: rag -> ai -> app -> Backend).
load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)
EMBEDDING_DIM = _int("RAG_EMBEDDING_DIM", 384)
EMBEDDING_DEVICE = os.getenv("RAG_EMBEDDING_DEVICE", "cpu")
EMBEDDING_BATCH = _int("RAG_EMBEDDING_BATCH", 32)
WARMUP = _bool("RAG_WARMUP", False)

CHUNK_CHARS = _int("RAG_CHUNK_CHARS", 1500)
CHUNK_OVERLAP = _int("RAG_CHUNK_OVERLAP", 200)

TOP_K = _int("RAG_TOP_K", 5)
MAX_UPLOAD_MB = _int("RAG_MAX_UPLOAD_MB", 20)
MAX_CONTEXT_CHARS = _int("RAG_MAX_CONTEXT_CHARS", 4000)
