# Module: app.models.rag
# Description: SQLAlchemy database models for the RAG Knowledge Base system.
# Tracks ingested documents, semantic chunks, and retrieval audit logs.

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class RagDocument(Base):
    """Tracks every ingested source document and its processing state."""
    __tablename__ = "rag_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(512), nullable=False)
    source_type = Column(
        SAEnum(
            "rbi_mpc", "rbi_annual", "imf_weo", "world_bank", "government", "research_paper",
            name="rag_source_type"
        ),
        nullable=False
    )
    publisher = Column(String(100), nullable=True)
    publication_date = Column(Date, nullable=True)
    file_path = Column(Text, nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)  # SHA-256 hex digest
    total_pages = Column(Integer, nullable=True, default=0)
    total_chunks = Column(Integer, nullable=True, default=0)
    embedding_model = Column(String(100), nullable=True)
    ingestion_status = Column(
        SAEnum(
            "pending", "extracting", "chunking", "embedding", "indexed", "failed",
            name="rag_ingestion_status"
        ),
        nullable=False,
        default="pending"
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ORM Relationships
    chunks = relationship("RagChunk", back_populates="document", cascade="all, delete-orphan")


class RagChunk(Base):
    """Stores chunk metadata for metadata-only queries (without hitting ChromaDB)."""
    __tablename__ = "rag_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("rag_documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    section_title = Column(Text, nullable=True)
    content_type = Column(
        SAEnum(
            "text", "table", "executive_summary", "formula",
            name="rag_content_type"
        ),
        nullable=False,
        default="text"
    )
    token_count = Column(Integer, nullable=True, default=0)
    extraction_method = Column(
        SAEnum("native", "ocr", name="rag_extraction_method"),
        nullable=False,
        default="native"
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    # ORM Relationships
    document = relationship("RagDocument", back_populates="chunks")


class RagRetrievalLog(Base):
    """Audit trail for all RAG retrievals — feeds monitoring and telemetry."""
    __tablename__ = "rag_retrieval_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), nullable=True)
    query_text = Column(Text, nullable=False)
    retrieved_chunk_ids = Column(Text, nullable=True)   # JSON-serialized list
    reranked_chunk_ids = Column(Text, nullable=True)    # JSON-serialized list
    top_score = Column(Float, nullable=True)
    retrieval_latency_ms = Column(Integer, nullable=True)
    filter_applied = Column(Text, nullable=True)        # JSON-serialized dict
    hallucination_flagged = Column(Boolean, default=False)
    freshness_applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
