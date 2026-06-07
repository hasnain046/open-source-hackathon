# Module: app.schemas.rag
# Description: Pydantic request/response schemas for the RAG Knowledge Base API layer.

import uuid
from datetime import date, datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Citation & Passage Schemas
# ---------------------------------------------------------------------------

class CitationSchema(BaseModel):
    """Structured citation metadata for a retrieved passage."""
    source_name: str
    publisher: Optional[str] = None
    publication_date: Optional[date] = None
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    chunk_id: Optional[str] = None


class PassageSchema(BaseModel):
    """A single ranked and scored passage from the RAG retrieval pipeline."""
    rank: int
    relevance_score: float
    freshness_score: float = 0.0
    final_score: float
    citation_confidence: Literal["High", "Medium", "Low"]
    text: str
    citation: CitationSchema


# ---------------------------------------------------------------------------
# Document Management Schemas
# ---------------------------------------------------------------------------

class DocumentUploadResponseSchema(BaseModel):
    """Response returned after a document is submitted for ingestion."""
    id: uuid.UUID
    title: str
    source_type: str
    publisher: Optional[str] = None
    publication_date: Optional[date] = None
    ingestion_status: str
    total_chunks: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListItemSchema(BaseModel):
    """Summary item for the document list endpoint."""
    id: uuid.UUID
    title: str
    publisher: Optional[str] = None
    source_type: str
    publication_date: Optional[date] = None
    ingestion_status: str
    total_chunks: int = 0
    total_pages: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Search Schemas
# ---------------------------------------------------------------------------

class RAGFilterSchema(BaseModel):
    """Optional filters to narrow the candidate retrieval pool."""
    publisher: Optional[List[str]] = None
    source_type: Optional[List[str]] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class RAGSearchRequestSchema(BaseModel):
    """Request body for the /rag/search endpoint."""
    query: str = Field(..., min_length=3, description="Search query text")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of passages to return")
    filters: Optional[RAGFilterSchema] = None
    search_mode: Literal["semantic", "hybrid"] = Field(default="hybrid")
    freshness_enabled: bool = Field(default=True, description="Apply recency weighting")


class RAGSearchResponseSchema(BaseModel):
    """Response from the /rag/search endpoint."""
    query: str
    passages: List[PassageSchema]
    rag_available: bool
    rag_confidence: float
    freshness_applied: bool
    retrieval_latency_ms: int
    total_documents_searched: int


# ---------------------------------------------------------------------------
# Statistics Schema
# ---------------------------------------------------------------------------

class RAGStatsSchema(BaseModel):
    """High-level statistics about the RAG index health."""
    total_documents: int
    total_chunks: int
    indexed_documents: int
    failed_documents: int
    index_health: str
