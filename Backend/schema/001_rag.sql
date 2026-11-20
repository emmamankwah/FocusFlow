-- Retrieval-Augmented Generation storage.
--
-- Per-user documents and their embedded chunks. Requires the pgvector
-- extension (https://github.com/pgvector/pgvector). Run this once per
-- environment; every statement is idempotent.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    filename VARCHAR(255),
    content_type VARCHAR(100),
    size_bytes INTEGER,
    status VARCHAR(16) NOT NULL DEFAULT 'processing'
        CHECK (status IN ('processing', 'ready', 'failed')),
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER,
    embedding vector(384),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_documents_user
    ON documents (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chunks_user_document
    ON document_chunks (user_id, document_id);

-- The embedding column is sized to RAG_EMBEDDING_DIM (384 for
-- all-MiniLM-L6-v2). Changing the model dimensions requires migrating the
-- column and re-embedding the corpus.
--
-- Add an ANN index once the corpus grows. For small datasets an exact scan is
-- fast enough and avoids index tuning:
-- CREATE INDEX IF NOT EXISTS idx_chunks_embedding
--     ON document_chunks USING hnsw (embedding vector_cosine_ops);
