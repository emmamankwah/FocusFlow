"""Database access for documents and their embedded chunks."""

from __future__ import annotations

import json

from app.authentication.settings.db import database_connection


def _connect():
    connection = database_connection()
    if connection is None:
        raise ConnectionError("Database connection failed.")
    return connection


def create_document(
    user_id: int,
    title: str,
    filename: str | None = None,
    content_type: str | None = None,
    size_bytes: int | None = None,
    status: str = "processing",
) -> dict:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO documents "
                "(user_id, title, filename, content_type, size_bytes, status) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
                (user_id, title, filename, content_type, size_bytes, status),
            )
            row = cursor.fetchone()
        connection.commit()
        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def store_document_chunks(
    document_id: int,
    user_id: int,
    chunks: list[dict],
) -> None:
    if not chunks:
        return

    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO document_chunks "
                "(document_id, user_id, chunk_index, content, token_count, "
                "embedding, metadata) "
                "VALUES (%s, %s, %s, %s, %s, %s::vector, %s::jsonb)",
                [
                    (
                        document_id,
                        user_id,
                        chunk["chunkIndex"],
                        chunk["content"],
                        chunk["tokenCount"],
                        chunk["embedding"],
                        json.dumps(chunk.get("metadata") or {}),
                    )
                    for chunk in chunks
                ],
            )
            cursor.execute(
                "UPDATE documents SET status = 'ready', error = NULL, "
                "updated_at = now() WHERE id = %s AND user_id = %s",
                (document_id, user_id),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def set_document_status(
    document_id: int,
    user_id: int,
    status: str,
    error: str | None = None,
) -> bool:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE documents SET status = %s, error = %s, updated_at = now() "
                "WHERE id = %s AND user_id = %s RETURNING id",
                (status, error, document_id, user_id),
            )
            row = cursor.fetchone()
        connection.commit()
        return row is not None
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def list_documents(user_id: int) -> list[dict]:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT d.*, "
                "(SELECT count(*) FROM document_chunks c "
                " WHERE c.document_id = d.id) AS chunk_count "
                "FROM documents d WHERE d.user_id = %s "
                "ORDER BY d.created_at DESC",
                (user_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()


def get_document(user_id: int, document_id: int) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT d.*, "
                "(SELECT count(*) FROM document_chunks c "
                " WHERE c.document_id = d.id) AS chunk_count "
                "FROM documents d WHERE d.id = %s AND d.user_id = %s",
                (document_id, user_id),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        connection.close()


def delete_document(user_id: int, document_id: int) -> bool:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM documents WHERE id = %s AND user_id = %s RETURNING id",
                (document_id, user_id),
            )
            row = cursor.fetchone()
        connection.commit()
        return row is not None
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def search_chunks(
    user_id: int,
    query_vector: str,
    top_k: int,
    document_ids: list[int] | None = None,
) -> list[dict]:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT c.id, c.document_id, c.chunk_index, c.content, d.title, "
                "1 - (c.embedding <=> %s::vector) AS score "
                "FROM document_chunks c "
                "JOIN documents d ON d.id = c.document_id "
                "WHERE c.user_id = %s "
                "AND d.status = 'ready' "
                "AND (%s::bigint[] IS NULL OR c.document_id = ANY(%s::bigint[])) "
                "ORDER BY c.embedding <=> %s::vector "
                "LIMIT %s",
                (
                    query_vector,
                    user_id,
                    document_ids,
                    document_ids,
                    query_vector,
                    top_k,
                ),
            )
            return [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()


def search_keyword_chunks(
    user_id: int,
    query: str,
    top_k: int,
    document_ids: list[int] | None = None,
) -> list[dict]:
    """Find chunks by PostgreSQL full-text relevance."""
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "WITH search_query AS ("
                "SELECT websearch_to_tsquery('english', %s) AS query) "
                "SELECT c.id, c.document_id, c.chunk_index, c.content, d.title, "
                "ts_rank_cd(c.search_vector, search_query.query) AS score "
                "FROM document_chunks c "
                "JOIN documents d ON d.id = c.document_id "
                "CROSS JOIN search_query "
                "WHERE c.user_id = %s "
                "AND d.status = 'ready' "
                "AND c.search_vector @@ search_query.query "
                "AND (%s::bigint[] IS NULL OR c.document_id = ANY(%s::bigint[])) "
                "ORDER BY score DESC, c.id "
                "LIMIT %s",
                (query, user_id, document_ids, document_ids, top_k),
            )
            return [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()
