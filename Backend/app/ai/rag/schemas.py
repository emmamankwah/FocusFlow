"""Pydantic models for the RAG endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class Source(BaseModel):
    documentId: int
    title: str
    chunkIndex: int
    snippet: str
    score: float


class RagQuery(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    topK: int | None = Field(default=None, ge=1, le=20)
    documentIds: list[int] | None = None


class RagResponse(BaseModel):
    reply: str
    sources: list[Source] = Field(default_factory=list)


class InlineDocument(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class DocumentPublic(BaseModel):
    id: int
    title: str
    filename: str | None = None
    contentType: str | None = None
    sizeBytes: int | None = None
    status: str
    error: str | None = None
    chunkCount: int | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
