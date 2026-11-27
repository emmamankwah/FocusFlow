-- Add an automatically maintained English full-text index for hybrid RAG
-- retrieval. Existing chunks are indexed when this column is added.
ALTER TABLE document_chunks
    ADD COLUMN IF NOT EXISTS search_vector tsvector
    GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;

CREATE INDEX IF NOT EXISTS idx_chunks_search_vector
    ON document_chunks USING GIN (search_vector);
