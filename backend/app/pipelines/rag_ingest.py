# Module: app.pipelines.rag_ingest
# Description: PDF ingestion pipeline for the RAG Knowledge Base.
# Handles document text extraction (PyMuPDF → pdfplumber → OCR fallback),
# semantic chunking, embedding via sentence-transformers, and storage in ChromaDB.

import os
import re
import uuid
import hashlib
import unicodedata
import json
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

# All heavy ML/parsing imports are guarded so the service stays importable
# even when optional packages are absent.

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    print("[RAGIngest] WARNING: PyMuPDF (fitz) not installed. PDF extraction will use fallbacks.")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("[RAGIngest] WARNING: pdfplumber not installed. Table extraction disabled.")

try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[RAGIngest] WARNING: pytesseract/pdf2image not installed. OCR fallback disabled.")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("[RAGIngest] WARNING: sentence_transformers not installed. Embedding disabled.")

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("[RAGIngest] WARNING: chromadb not installed. Vector storage disabled.")

from app.models.rag import RagDocument, RagChunk
from app.config import settings

# Section heading patterns
HEADING_PATTERNS = [
    r"^\s*(chapter|section|part)\s+\d+[\.\:]?\s+\S",
    r"^\s*\d+\.\d*\s+[A-Z]",
    r"^\s*[A-Z][A-Z\s]{5,50}$",   # All-caps heading
    r"^\s*(executive\s+summary|introduction|conclusion|overview|appendix)",
]
HEADING_RE = re.compile("|".join(HEADING_PATTERNS), re.IGNORECASE | re.MULTILINE)

# Characters per approximate token (rough estimate; ~4 chars per token)
CHARS_PER_TOKEN = 4


class RAGIngestPipeline:
    """
    End-to-end PDF ingestion pipeline.
    Each document passes through: extract → clean → detect sections →
    chunk → embed → store (ChromaDB + PostgreSQL).
    """

    def __init__(self):
        self._embedding_model = None
        self._chroma_client = None
        self._chroma_collection = None

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def process_document(
        self,
        file_path: str,
        title: str,
        source_type: str,
        publisher: Optional[str],
        publication_date: Optional[date],
        db: Session,
    ) -> RagDocument:
        """
        Full ingestion pipeline for a single PDF.
        Creates/updates a RagDocument record and spawns chunk records.
        """
        os.makedirs(getattr(settings, "RAG_DOCUMENT_STORE", "./rag_documents"), exist_ok=True)

        file_hash = self.compute_file_hash(file_path)

        # Deduplication check
        existing = db.query(RagDocument).filter(RagDocument.file_hash == file_hash).first()
        if existing:
            return existing

        # Create document record
        doc = RagDocument(
            id=uuid.uuid4(),
            title=title,
            source_type=source_type,
            publisher=publisher,
            publication_date=publication_date,
            file_path=file_path,
            file_hash=file_hash,
            ingestion_status="pending",
            embedding_model=getattr(settings, "RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        try:
            # --- EXTRACTING ---
            doc.ingestion_status = "extracting"
            db.commit()
            pages = self._extract_text_pymupdf(file_path)
            if not pages:
                pages = self._extract_text_pdfplumber(file_path)
            doc.total_pages = len(pages)

            # --- CHUNKING ---
            doc.ingestion_status = "chunking"
            db.commit()
            pages = self._detect_sections(pages)
            chunks = self._chunk_document(pages, doc.id, {
                "source_name": title,
                "source_type": source_type,
                "publisher": publisher or "",
                "publication_date": str(publication_date) if publication_date else "",
            })
            doc.total_chunks = len(chunks)

            # --- EMBEDDING ---
            doc.ingestion_status = "embedding"
            db.commit()
            self._embed_and_store(chunks, doc.id, db)

            # --- INDEXED ---
            doc.ingestion_status = "indexed"
            db.commit()

        except Exception as exc:
            doc.ingestion_status = "failed"
            doc.error_message = str(exc)
            db.commit()
            print(f"[RAGIngest] ERROR processing '{title}': {exc}")

        db.refresh(doc)
        return doc

    # ------------------------------------------------------------------
    # Text extraction
    # ------------------------------------------------------------------

    def _extract_text_pymupdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text page-by-page using PyMuPDF. Falls back to empty list if unavailable."""
        if not FITZ_AVAILABLE:
            return []
        pages = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                if not text or len(text.strip()) < 50:
                    # Scanned page — attempt OCR if available
                    text = self._ocr_page(file_path, page_num) or text
                    extraction_method = "ocr"
                else:
                    extraction_method = "native"
                pages.append({
                    "page_number": page_num + 1,
                    "text": self._clean_text(text),
                    "has_table": False,
                    "section_title": "",
                    "extraction_method": extraction_method,
                })
            doc.close()
        except Exception as e:
            print(f"[RAGIngest] PyMuPDF error: {e}")
        return pages

    def _extract_text_pdfplumber(self, file_path: str) -> List[Dict[str, Any]]:
        """Fallback text extraction using pdfplumber (better table support)."""
        if not PDFPLUMBER_AVAILABLE:
            return []
        pages = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    has_table = bool(page.extract_tables())
                    pages.append({
                        "page_number": page_num + 1,
                        "text": self._clean_text(text),
                        "has_table": has_table,
                        "section_title": "",
                        "extraction_method": "native",
                    })
        except Exception as e:
            print(f"[RAGIngest] pdfplumber error: {e}")
        return pages

    def _ocr_page(self, file_path: str, page_num: int) -> str:
        """OCR fallback for a single page using pytesseract + pdf2image."""
        if not OCR_AVAILABLE:
            return ""
        try:
            images = convert_from_path(file_path, first_page=page_num + 1, last_page=page_num + 1, dpi=300)
            if images:
                return pytesseract.image_to_string(images[0], config="--oem 3 --psm 6")
        except Exception as e:
            print(f"[RAGIngest] OCR error on page {page_num+1}: {e}")
        return ""

    # ------------------------------------------------------------------
    # Text cleaning
    # ------------------------------------------------------------------

    def _clean_text(self, text: str) -> str:
        """Strip headers/footers artifacts, normalize unicode, fix hyphenation."""
        if not text:
            return ""
        # Normalize unicode (ligatures, smart quotes, etc.)
        text = unicodedata.normalize("NFKC", text)
        # Fix hyphenated line-breaks ("infla-\ntion" → "inflation")
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
        # Collapse excessive whitespace
        text = re.sub(r" {2,}", " ", text)
        # Remove common header/footer noise (page numbers, repeated org names)
        text = re.sub(r"\bPage\s+\d+\s+of\s+\d+\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
        return text.strip()

    # ------------------------------------------------------------------
    # Section detection
    # ------------------------------------------------------------------

    def _detect_sections(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect section headings per page using regex heuristics."""
        current_section = "Introduction"
        for page in pages:
            text = page.get("text", "")
            for line in text.splitlines():
                if HEADING_RE.match(line):
                    current_section = line.strip()
                    break
            page["section_title"] = current_section
        return pages

    # ------------------------------------------------------------------
    # Chunking
    # ------------------------------------------------------------------

    def _chunk_document(
        self,
        pages: List[Dict[str, Any]],
        document_id: uuid.UUID,
        metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Recursive character text splitter with section awareness.
        chunk_size=800 tokens, overlap=150 tokens.
        """
        chunk_size = getattr(settings, "RAG_CHUNK_SIZE", 800) * CHARS_PER_TOKEN
        overlap = getattr(settings, "RAG_CHUNK_OVERLAP", 150) * CHARS_PER_TOKEN

        chunks = []
        chunk_index = 0

        for page in pages:
            text = page.get("text", "").strip()
            if not text:
                continue

            section_title = page.get("section_title", "")
            page_number = page.get("page_number", 0)
            extraction_method = page.get("extraction_method", "native")
            has_table = page.get("has_table", False)

            # Determine content type
            content_type = "table" if has_table else "text"
            if section_title and "executive summary" in section_title.lower():
                content_type = "executive_summary"

            # Tables and executive summaries: keep whole (up to 1200 tokens ≈ 4800 chars)
            if content_type in ("table", "executive_summary"):
                chunk = self._make_chunk(
                    chunk_index=chunk_index,
                    text=text,
                    document_id=document_id,
                    page_number=page_number,
                    section_title=section_title,
                    content_type=content_type,
                    extraction_method=extraction_method,
                    metadata=metadata,
                )
                chunks.append(chunk)
                chunk_index += 1
                continue

            # Standard sliding window split
            start = 0
            while start < len(text):
                end = start + chunk_size
                segment = text[start:end]

                # Try to split at a sentence boundary within last 200 chars
                if end < len(text):
                    cut = segment.rfind(". ")
                    if cut == -1:
                        cut = segment.rfind("\n")
                    if cut != -1 and cut > chunk_size // 2:
                        segment = segment[: cut + 1]
                        end = start + cut + 1

                chunk = self._make_chunk(
                    chunk_index=chunk_index,
                    text=segment.strip(),
                    document_id=document_id,
                    page_number=page_number,
                    section_title=section_title,
                    content_type=content_type,
                    extraction_method=extraction_method,
                    metadata=metadata,
                )
                chunks.append(chunk)
                chunk_index += 1
                start = end - overlap
                if start >= len(text):
                    break

        return chunks

    def _make_chunk(
        self,
        chunk_index: int,
        text: str,
        document_id: uuid.UUID,
        page_number: int,
        section_title: str,
        content_type: str,
        extraction_method: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build a chunk dict with all required metadata fields."""
        token_count = max(1, len(text) // CHARS_PER_TOKEN)
        return {
            "chunk_id": str(uuid.uuid4()),
            "document_id": str(document_id),
            "source_name": metadata.get("source_name", ""),
            "source_type": metadata.get("source_type", ""),
            "publisher": metadata.get("publisher", ""),
            "publication_date": metadata.get("publication_date", ""),
            "page_number": page_number,
            "section_title": section_title,
            "chunk_index": chunk_index,
            "content_type": content_type,
            "extraction_method": extraction_method,
            "token_count": token_count,
            "text": text,
        }

    # ------------------------------------------------------------------
    # Embedding & storage
    # ------------------------------------------------------------------

    def _get_embedding_model(self):
        """Lazy-load sentence transformer (MiniLM primary, fallback None)."""
        if self._embedding_model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                model_name = getattr(settings, "RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
                self._embedding_model = SentenceTransformer(model_name)
            except Exception as e:
                print(f"[RAGIngest] Failed to load embedding model: {e}")
        return self._embedding_model

    def _get_chroma_collection(self):
        """Lazy-load ChromaDB PersistentClient and return the RAG collection."""
        if self._chroma_collection is None and CHROMADB_AVAILABLE:
            try:
                persist_dir = getattr(settings, "CHROMA_PERSIST_DIR", "./chroma_store")
                os.makedirs(persist_dir, exist_ok=True)
                self._chroma_client = chromadb.PersistentClient(path=persist_dir)
                self._chroma_collection = self._chroma_client.get_or_create_collection(
                    name="inflationiq_rag",
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception as e:
                print(f"[RAGIngest] ChromaDB init failed: {e}")
        return self._chroma_collection

    def _embed_and_store(
        self,
        chunks: List[Dict[str, Any]],
        document_id: uuid.UUID,
        db: Session,
    ) -> None:
        """Encode chunks with sentence-transformers and store in ChromaDB + RagChunk table."""
        if not chunks:
            return

        model = self._get_embedding_model()
        collection = self._get_chroma_collection()

        texts = [c["text"] for c in chunks]

        # Compute embeddings if model available
        embeddings = None
        if model is not None:
            try:
                embeddings = model.encode(texts, show_progress_bar=False).tolist()
            except Exception as e:
                print(f"[RAGIngest] Embedding error: {e}")

        # Store in ChromaDB
        if collection is not None:
            try:
                ids = [c["chunk_id"] for c in chunks]
                metadatas = [
                    {
                        k: v
                        for k, v in c.items()
                        if k not in ("text",) and isinstance(v, (str, int, float, bool))
                    }
                    for c in chunks
                ]
                if embeddings:
                    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
                else:
                    collection.add(ids=ids, documents=texts, metadatas=metadatas)
            except Exception as e:
                print(f"[RAGIngest] ChromaDB storage error: {e}")

        # Persist chunk metadata to PostgreSQL
        for chunk in chunks:
            db_chunk = RagChunk(
                id=uuid.UUID(chunk["chunk_id"]),
                document_id=document_id,
                chunk_index=chunk["chunk_index"],
                page_number=chunk.get("page_number"),
                section_title=chunk.get("section_title"),
                content_type=chunk.get("content_type", "text"),
                token_count=chunk.get("token_count", 0),
                extraction_method=chunk.get("extraction_method", "native"),
            )
            db.add(db_chunk)
        db.commit()

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """Compute SHA-256 hash of a file for deduplication."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    sha256.update(chunk)
        except Exception as e:
            print(f"[RAGIngest] Hash error: {e}")
            return str(uuid.uuid4())
        return sha256.hexdigest()
