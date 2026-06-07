# Module: app.api.v1.rag
# Description: FastAPI router exposing RAG Knowledge Base endpoints for document
# management, hybrid semantic search, monitoring, and health checks.

import os
import uuid
import json
import shutil
import hashlib
from datetime import datetime
from typing import List, Optional
from urllib.request import urlretrieve

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Body, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, RoleChecker, get_current_user
from app.models.user import User
from app.models.rag import RagDocument, RagRetrievalLog
from app.schemas.rag import (
    DocumentUploadResponseSchema,
    DocumentListItemSchema,
    RAGSearchRequestSchema,
    RAGSearchResponseSchema,
    RAGStatsSchema,
    PassageSchema,
    CitationSchema,
)
from app.services.rag_service import RAGService
from app.config import settings

router = APIRouter(prefix="/rag", tags=["rag"])

_admin_only = RoleChecker(allowed_roles=["admin"])
_analyst_plus = RoleChecker(allowed_roles=["admin", "analyst"])

RAG_DOCUMENT_STORE = getattr(settings, "RAG_DOCUMENT_STORE", "./rag_documents")
os.makedirs(RAG_DOCUMENT_STORE, exist_ok=True)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _doc_to_upload_response(doc: RagDocument) -> DocumentUploadResponseSchema:
    return DocumentUploadResponseSchema(
        id=doc.id,
        title=doc.title,
        source_type=doc.source_type,
        publisher=doc.publisher,
        publication_date=doc.publication_date,
        ingestion_status=doc.ingestion_status,
        total_chunks=doc.total_chunks or 0,
        created_at=doc.created_at,
    )


def _doc_to_list_item(doc: RagDocument) -> DocumentListItemSchema:
    return DocumentListItemSchema(
        id=doc.id,
        title=doc.title,
        publisher=doc.publisher,
        source_type=doc.source_type,
        publication_date=doc.publication_date,
        ingestion_status=doc.ingestion_status,
        total_chunks=doc.total_chunks or 0,
        total_pages=doc.total_pages or 0,
        created_at=doc.created_at,
    )


def _run_ingestion(file_path: str, title: str, source_type: str, publisher: str,
                   publication_date, db: Session, document_id: uuid.UUID):
    """Background task: run ingest pipeline and update existing doc record."""
    try:
        from app.pipelines.rag_ingest import RAGIngestPipeline
        pipeline = RAGIngestPipeline()
        doc = db.query(RagDocument).filter(RagDocument.id == document_id).first()
        if doc:
            pipeline.process_document(file_path, title, source_type, publisher, publication_date, db)
    except Exception as e:
        print(f"[RAG API] Background ingestion error: {e}")


# ---------------------------------------------------------------------------
# Document Management
# ---------------------------------------------------------------------------

@router.post("/documents/upload", response_model=DocumentUploadResponseSchema)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Body(...),
    source_type: str = Body(...),
    publisher: Optional[str] = Body(default=None),
    publication_date: Optional[str] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_only),
):
    """Upload a PDF document for ingestion into the RAG Knowledge Base. Admin only."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    os.makedirs(RAG_DOCUMENT_STORE, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(RAG_DOCUMENT_STORE, safe_name)

    # Stream file to disk
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Compute hash for deduplication
    sha256 = hashlib.sha256(content).hexdigest()
    existing = db.query(RagDocument).filter(RagDocument.file_hash == sha256).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Document already exists: {existing.id}")

    # Parse optional date
    pub_date = None
    if publication_date:
        try:
            from datetime import date
            pub_date = date.fromisoformat(publication_date)
        except Exception:
            pass

    # Create document record
    doc = RagDocument(
        id=uuid.uuid4(),
        title=title,
        source_type=source_type,
        publisher=publisher,
        publication_date=pub_date,
        file_path=file_path,
        file_hash=sha256,
        ingestion_status="pending",
        embedding_model=getattr(settings, "RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(
        _run_ingestion, file_path, title, source_type, publisher or "", pub_date, db, doc.id
    )

    return _doc_to_upload_response(doc)


@router.post("/documents/crawl", response_model=DocumentUploadResponseSchema)
async def crawl_document(
    background_tasks: BackgroundTasks,
    url: str = Body(...),
    title: str = Body(...),
    source_type: str = Body(...),
    publisher: Optional[str] = Body(default=None),
    publication_date: Optional[str] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_only),
):
    """Download and ingest a PDF from a URL. Admin only."""
    os.makedirs(RAG_DOCUMENT_STORE, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_crawled.pdf"
    file_path = os.path.join(RAG_DOCUMENT_STORE, safe_name)
    try:
        urlretrieve(url, file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download PDF: {e}")

    with open(file_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    existing = db.query(RagDocument).filter(RagDocument.file_hash == sha256).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Document already exists: {existing.id}")

    pub_date = None
    if publication_date:
        try:
            from datetime import date
            pub_date = date.fromisoformat(publication_date)
        except Exception:
            pass

    doc = RagDocument(
        id=uuid.uuid4(),
        title=title,
        source_type=source_type,
        publisher=publisher,
        publication_date=pub_date,
        file_path=file_path,
        file_hash=sha256,
        ingestion_status="pending",
        embedding_model=getattr(settings, "RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(
        _run_ingestion, file_path, title, source_type, publisher or "", pub_date, db, doc.id
    )
    return _doc_to_upload_response(doc)


@router.get("/documents", response_model=List[DocumentListItemSchema])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(_analyst_plus),
):
    """List all ingested documents with their status. Analyst+ access."""
    docs = db.query(RagDocument).order_by(RagDocument.created_at.desc()).all()
    return [_doc_to_list_item(d) for d in docs]


@router.get("/documents/{document_id}", response_model=DocumentListItemSchema)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_analyst_plus),
):
    """Get single document detail. Analyst+ access."""
    doc = db.query(RagDocument).filter(RagDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _doc_to_list_item(doc)


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_only),
):
    """Delete a document and all its chunks. Admin only."""
    doc = db.query(RagDocument).filter(RagDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    success = RAGService.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=500, detail="Delete operation failed")
    return {"status": "deleted", "document_id": str(document_id)}


@router.post("/documents/{document_id}/reindex", response_model=DocumentUploadResponseSchema)
def reindex_document(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_only),
):
    """Re-run ingestion pipeline on an existing file. Admin only."""
    doc = db.query(RagDocument).filter(RagDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.file_path or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=400, detail="Source file no longer available on disk")

    doc.ingestion_status = "pending"
    db.commit()

    background_tasks.add_task(
        _run_ingestion, doc.file_path, doc.title, doc.source_type,
        doc.publisher or "", doc.publication_date, db, doc.id
    )
    db.refresh(doc)
    return _doc_to_upload_response(doc)


# ---------------------------------------------------------------------------
# Search & Retrieval
# ---------------------------------------------------------------------------

@router.post("/search", response_model=RAGSearchResponseSchema)
def search(
    request: RAGSearchRequestSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(_analyst_plus),
):
    """Hybrid semantic/BM25 search across the RAG Knowledge Base. Analyst+ access."""
    filters = None
    if request.filters:
        filters = {
            "publisher": request.filters.publisher,
            "source_type": request.filters.source_type,
            "from_date": request.filters.from_date,
            "to_date": request.filters.to_date,
        }

    result = RAGService.retrieve(
        db=db,
        query=request.query,
        top_k=request.top_k,
        filters=filters,
        freshness_enabled=request.freshness_enabled,
        search_mode=request.search_mode,
    )

    # Convert passage dicts to schema objects
    passages = [
        PassageSchema(
            rank=p["rank"],
            relevance_score=p["relevance_score"],
            freshness_score=p["freshness_score"],
            final_score=p["final_score"],
            citation_confidence=p["citation_confidence"],
            text=p["text"],
            citation=CitationSchema(**p["citation"]),
        )
        for p in result["passages"]
    ]

    return RAGSearchResponseSchema(
        query=result["query"],
        passages=passages,
        rag_available=result["rag_available"],
        rag_confidence=result["rag_confidence"],
        freshness_applied=result["freshness_applied"],
        retrieval_latency_ms=result["retrieval_latency_ms"],
        total_documents_searched=result["total_documents_searched"],
    )


@router.get("/search/filters")
def get_search_filters(
    db: Session = Depends(get_db),
    current_user: User = Depends(_analyst_plus),
):
    """Return available filter values from the document index. Analyst+ access."""
    from sqlalchemy import distinct, func
    publishers = [r[0] for r in db.query(distinct(RagDocument.publisher)).filter(RagDocument.publisher != None).all()]
    source_types = [r[0] for r in db.query(distinct(RagDocument.source_type)).all()]
    min_date = db.query(func.min(RagDocument.publication_date)).scalar()
    max_date = db.query(func.max(RagDocument.publication_date)).scalar()
    return {
        "publishers": publishers,
        "source_types": source_types,
        "date_range": {
            "from_date": str(min_date) if min_date else None,
            "to_date": str(max_date) if max_date else None,
        },
    }


# ---------------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=RAGStatsSchema)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_only),
):
    """Return RAG index statistics. Admin only."""
    stats = RAGService.get_stats(db)
    return RAGStatsSchema(**stats)


@router.get("/retrieval-logs")
def get_retrieval_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_only),
):
    """Paginated retrieval audit log. Admin only."""
    offset = (page - 1) * page_size
    logs = (
        db.query(RagRetrievalLog)
        .order_by(RagRetrievalLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    total = db.query(RagRetrievalLog).count()
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "logs": [
            {
                "id": str(log.id),
                "query_text": log.query_text,
                "top_score": log.top_score,
                "retrieval_latency_ms": log.retrieval_latency_ms,
                "hallucination_flagged": log.hallucination_flagged,
                "freshness_applied": log.freshness_applied,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }


@router.get("/health")
def health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_only),
):
    """Check ChromaDB connection + embedding model status. Admin only."""
    chroma_status = "unavailable"
    chroma_count = 0
    embedding_status = "unavailable"

    try:
        collection = RAGService._get_chroma_collection()
        if collection is not None:
            chroma_count = collection.count()
            chroma_status = "healthy"
    except Exception as e:
        chroma_status = f"error: {e}"

    try:
        model = RAGService._get_embedding_model()
        if model is not None:
            embedding_status = "healthy"
    except Exception:
        pass

    return {
        "chroma_db": chroma_status,
        "chroma_document_count": chroma_count,
        "embedding_model": embedding_status,
        "timestamp": datetime.utcnow().isoformat(),
    }
