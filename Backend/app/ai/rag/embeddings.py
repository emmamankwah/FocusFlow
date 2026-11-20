"""Local text embeddings backed by fastembed (ONNX Runtime).

fastembed is used instead of sentence-transformers/PyTorch because PyTorch's
Windows DLLs are unsigned and are blocked by Smart App Control (WinError 4551)
on some machines. The configured model is the ONNX build of the same MiniLM
model, so the vector dimension (384) is unchanged.

The model is loaded lazily on first use so importing the package (and running
the API without touching RAG) stays cheap. Tests can replace the encoder with
``set_encoder`` to avoid downloading the model.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Sequence
from pathlib import Path

from . import config

_model = None
_load_lock = threading.Lock()
_encode_lock = threading.Lock()
_encoder_override: Callable[[Sequence[str]], Sequence[Sequence[float]]] | None = None


def set_encoder(
    encoder: Callable[[Sequence[str]], Sequence[Sequence[float]]] | None,
) -> None:
    """Replace (or clear) the encoder. Intended for tests."""
    global _encoder_override
    _encoder_override = encoder


def _cache_dir() -> str:
    path = Path(config.EMBEDDING_CACHE)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def load_model():
    global _model
    if _model is None:
        with _load_lock:
            if _model is None:
                from fastembed import TextEmbedding

                model = TextEmbedding(
                    model_name=config.EMBEDDING_MODEL,
                    cache_dir=_cache_dir(),
                )
                dimension = len(next(iter(model.embed(["dimension check"]))))
                if dimension != config.EMBEDDING_DIM:
                    raise RuntimeError(
                        "Embedding dimension mismatch: model reports "
                        f"{dimension}, RAG_EMBEDDING_DIM is {config.EMBEDDING_DIM}."
                    )
                _model = model
    return _model


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    if not texts:
        return []

    if _encoder_override is not None:
        return [list(vector) for vector in _encoder_override(list(texts))]

    model = load_model()
    with _encode_lock:
        vectors = list(
            model.embed(list(texts), batch_size=config.EMBEDDING_BATCH)
        )
    return [vector.tolist() for vector in vectors]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


def vector_to_sql(vector: Sequence[float]) -> str:
    """Serialise a vector for a ``%s::vector`` cast in psycopg2."""
    return "[" + ",".join(f"{value:.8f}" for value in vector) + "]"


def warmup() -> None:
    """Load the model and run one encode so the first request is fast."""
    embed_texts(["warmup"])
