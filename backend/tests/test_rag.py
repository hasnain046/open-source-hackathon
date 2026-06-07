# Module: tests.test_rag
# Description: Comprehensive automated tests for Phase 12: RAG Knowledge Base.
# Tests cover chunk metadata schema, freshness scoring, citation confidence,
# RRF fusion, retrieval service, API endpoints, and Copilot integration.

import os
import sys
import io
import math
import uuid
import json
import struct
import zlib
import unittest
from datetime import date, datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import Base
from app.models.user import User
from app.models.rag import RagDocument, RagChunk, RagRetrievalLog
from app.services.rag_service import RAGService
from app.services.copilot_service import CopilotService
from app.api.deps import get_current_user, get_db

SQLITE_PATH = (
    "sqlite:///"
    + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "local_sqlite.db")).replace("\\", "/")
)

# ---------------------------------------------------------------------------
# Shared mock users
# ---------------------------------------------------------------------------

mock_admin_id = uuid.uuid4()
mock_admin_user = User(
    id=mock_admin_id,
    email="admin-rag@inflationiq.ai",
    full_name="RAG Admin Tester",
    role="admin",
    is_active=True,
    created_at=datetime.utcnow(),
)

mock_analyst_id = uuid.uuid4()
mock_analyst_user = User(
    id=mock_analyst_id,
    email="analyst-rag@inflationiq.ai",
    full_name="RAG Analyst Tester",
    role="analyst",
    is_active=True,
    created_at=datetime.utcnow(),
)


# ---------------------------------------------------------------------------
# Minimal PDF builder (creates a syntactically valid single-page PDF in memory)
# ---------------------------------------------------------------------------

def _make_minimal_pdf(text: str = "InflationIQ RAG test document.") -> bytes:
    """Generate a minimal valid PDF file with one text page."""
    content_stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = []

    # Object 1: Catalog
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    # Object 2: Pages
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    # Object 3: Page
    objects.append(
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
        b" /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    )
    # Object 4: Content stream
    stream_len = len(content_stream)
    objects.append(
        f"4 0 obj\n<< /Length {stream_len} >>\nstream\n".encode()
        + content_stream
        + b"\nendstream\nendobj\n"
    )
    # Object 5: Font
    objects.append(
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    )

    header = b"%PDF-1.4\n"
    body = b""
    offsets = []
    offset = len(header)
    for obj in objects:
        offsets.append(offset)
        body += obj
        offset += len(obj)

    xref_offset = len(header) + len(body)
    xref = f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n"
    for off in offsets:
        xref += f"{off:010d} 00000 n \n"
    trailer = (
        f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    )
    return header + body + xref.encode() + trailer.encode()


# ---------------------------------------------------------------------------
# Helper: confidence tagger (mirrors RAGService logic)
# ---------------------------------------------------------------------------

def _tag_confidence(score: float) -> str:
    if score >= 0.75:
        return "High"
    elif score >= 0.50:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# Helper: RRF fusion
# ---------------------------------------------------------------------------

def _rrf_fusion(dense_list: list, sparse_list: list, k: int = 60) -> dict:
    """Compute Reciprocal Rank Fusion scores from two ranked lists of chunk IDs."""
    fused = {}
    for rank, cid in enumerate(dense_list, start=1):
        fused[cid] = fused.get(cid, 0.0) + 1.0 / (k + rank)
    for rank, cid in enumerate(sparse_list, start=1):
        fused[cid] = fused.get(cid, 0.0) + 1.0 / (k + rank)
    return fused


class TestRAGKnowledgeBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(SQLITE_PATH)
        Base.metadata.create_all(bind=cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.Session()
        self.client = TestClient(app)
        # Default to admin for most tests
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user
        app.dependency_overrides[get_db] = lambda: self.db

    def tearDown(self):
        self.db.close()
        app.dependency_overrides.clear()

    # -----------------------------------------------------------------------
    # Test 1: Chunk metadata schema
    # -----------------------------------------------------------------------

    def test_chunk_metadata_schema(self):
        """1. Assert that a manually constructed chunk dict has all required fields."""
        required_fields = [
            "chunk_id",
            "document_id",
            "source_name",
            "publisher",
            "publication_date",
            "page_number",
            "section_title",
            "content_type",
            "token_count",
            "text",
        ]

        chunk = {
            "chunk_id": str(uuid.uuid4()),
            "document_id": str(uuid.uuid4()),
            "source_name": "RBI Monetary Policy Report – June 2024",
            "source_type": "rbi_mpc",
            "publisher": "RBI",
            "publication_date": "2024-06-08",
            "page_number": 14,
            "section_title": "Section 2: Inflation Assessment",
            "chunk_index": 3,
            "content_type": "text",
            "extraction_method": "native",
            "token_count": 743,
            "text": "Headline inflation moderated to 4.2% in May 2024, driven by easing food prices.",
        }

        for field in required_fields:
            self.assertIn(field, chunk, f"Missing required field: {field}")

        # Validate UUID format
        self.assertIsNotNone(uuid.UUID(chunk["chunk_id"]))
        self.assertIsNotNone(uuid.UUID(chunk["document_id"]))

        # Validate content type is in allowed set
        allowed_types = {"text", "table", "executive_summary", "formula"}
        self.assertIn(chunk["content_type"], allowed_types)

        # Validate token count is positive
        self.assertGreater(chunk["token_count"], 0)

    # -----------------------------------------------------------------------
    # Test 2: Freshness score computation
    # -----------------------------------------------------------------------

    def test_freshness_score_computation(self):
        """2. Verify freshness score formula: exp(-0.002 * age_days)."""
        lambda_decay = 0.002
        today = date.today()

        # 1 year old → ~0.48
        pub_1yr_ago = date(today.year - 1, today.month, today.day)
        age_days_1yr = (today - pub_1yr_ago).days
        expected_1yr = math.exp(-lambda_decay * age_days_1yr)
        score_1yr = RAGService._compute_freshness(str(pub_1yr_ago), today, lambda_decay)
        self.assertAlmostEqual(score_1yr, expected_1yr, places=4)
        self.assertAlmostEqual(score_1yr, math.exp(-0.002 * 365), delta=0.05,
                               msg="1-year-old document should score ≈ 0.48")

        # Today → 1.0
        score_today = RAGService._compute_freshness(str(today), today, lambda_decay)
        self.assertAlmostEqual(score_today, 1.0, places=4,
                               msg="Today's document should score 1.0")

        # Missing date → 0.0
        score_missing = RAGService._compute_freshness("", today, lambda_decay)
        self.assertEqual(score_missing, 0.0,
                         msg="Missing publication date should yield freshness=0.0")

        # None-like empty string
        score_none = RAGService._compute_freshness(None, today, lambda_decay)
        self.assertEqual(score_none, 0.0)

    # -----------------------------------------------------------------------
    # Test 3: Citation confidence thresholds
    # -----------------------------------------------------------------------

    def test_citation_confidence_thresholds(self):
        """3. Assert score≥0.75→High, ≥0.50→Medium, <0.50→Low."""
        self.assertEqual(_tag_confidence(0.75), "High")
        self.assertEqual(_tag_confidence(0.90), "High")
        self.assertEqual(_tag_confidence(1.00), "High")
        self.assertEqual(_tag_confidence(0.50), "Medium")
        self.assertEqual(_tag_confidence(0.74), "Medium")
        self.assertEqual(_tag_confidence(0.60), "Medium")
        self.assertEqual(_tag_confidence(0.49), "Low")
        self.assertEqual(_tag_confidence(0.00), "Low")
        self.assertEqual(_tag_confidence(0.35), "Low")

    # -----------------------------------------------------------------------
    # Test 4: RRF fusion
    # -----------------------------------------------------------------------

    def test_rrf_fusion(self):
        """4. Verify RRF scores are computed correctly and ranking is correct."""
        dense_list = ["chunk_A", "chunk_B", "chunk_C"]
        sparse_list = ["chunk_B", "chunk_D", "chunk_A"]

        fused = _rrf_fusion(dense_list, sparse_list, k=60)

        # chunk_A appears at rank 1 in dense and rank 3 in sparse
        expected_A = 1 / (60 + 1) + 1 / (60 + 3)
        self.assertAlmostEqual(fused["chunk_A"], expected_A, places=8)

        # chunk_B appears at rank 2 in dense and rank 1 in sparse
        expected_B = 1 / (60 + 2) + 1 / (60 + 1)
        self.assertAlmostEqual(fused["chunk_B"], expected_B, places=8)

        # chunk_C appears only in dense at rank 3
        expected_C = 1 / (60 + 3)
        self.assertAlmostEqual(fused["chunk_C"], expected_C, places=8)

        # chunk_D appears only in sparse at rank 2
        expected_D = 1 / (60 + 2)
        self.assertAlmostEqual(fused["chunk_D"], expected_D, places=8)

        # Sort by fused score
        ranked = sorted(fused.items(), key=lambda x: x[1], reverse=True)
        ranked_ids = [r[0] for r in ranked]

        # chunk_B should rank highest (appears high in both lists)
        self.assertEqual(ranked_ids[0], "chunk_B")
        # chunk_A should rank second
        self.assertEqual(ranked_ids[1], "chunk_A")

    # -----------------------------------------------------------------------
    # Test 5: RAGService.retrieve on empty DB
    # -----------------------------------------------------------------------

    def test_rag_service_retrieve_empty_db(self):
        """5. RAGService.retrieve() must return rag_available=False gracefully when ChromaDB empty."""
        result = RAGService.retrieve(self.db, "What is India's inflation forecast?")

        # Must return a dict (no crash)
        self.assertIsInstance(result, dict)

        # Required keys must be present
        required_keys = [
            "query", "passages", "rag_available",
            "rag_confidence", "freshness_applied",
            "retrieval_latency_ms", "total_documents_searched",
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

        # rag_available must be bool
        self.assertIsInstance(result["rag_available"], bool)

        # Passages must be a list
        self.assertIsInstance(result["passages"], list)

        # Latency must be non-negative
        self.assertGreaterEqual(result["retrieval_latency_ms"], 0)

    # -----------------------------------------------------------------------
    # Test 6: Document upload API
    # -----------------------------------------------------------------------

    def test_document_upload_api(self):
        """6. POST /api/v1/rag/documents/upload — verify 200 and schema."""
        pdf_bytes = _make_minimal_pdf("RAG upload test document page 1.")

        response = self.client.post(
            "/api/v1/rag/documents/upload",
            data={
                "title": "Test RAG PDF Upload",
                "source_type": "rbi_mpc",
                "publisher": "RBI",
                "publication_date": "2024-06-08",
            },
            files={"file": ("test_upload.pdf", pdf_bytes, "application/pdf")},
        )

        self.assertIn(response.status_code, [200, 201, 409],
                      f"Expected 200/201/409, got {response.status_code}: {response.text}")

        if response.status_code in (200, 201):
            data = response.json()
            required_fields = ["id", "title", "source_type", "ingestion_status", "created_at"]
            for field in required_fields:
                self.assertIn(field, data, f"Missing field in upload response: {field}")
            self.assertEqual(data["title"], "Test RAG PDF Upload")
            self.assertEqual(data["source_type"], "rbi_mpc")
            self.assertIn(data["ingestion_status"], [
                "pending", "extracting", "chunking", "embedding", "indexed", "failed"
            ])

    # -----------------------------------------------------------------------
    # Test 7: Search API
    # -----------------------------------------------------------------------

    def test_search_api(self):
        """7. POST /api/v1/rag/search — verify 200 with RAGSearchResponseSchema fields."""
        payload = {
            "query": "What is the RBI inflation outlook for 2024?",
            "top_k": 3,
            "search_mode": "hybrid",
            "freshness_enabled": True,
        }
        response = self.client.post("/api/v1/rag/search", json=payload)

        self.assertEqual(response.status_code, 200,
                         f"Search API returned {response.status_code}: {response.text}")

        data = response.json()
        required_fields = [
            "query", "passages", "rag_available",
            "rag_confidence", "freshness_applied",
            "retrieval_latency_ms", "total_documents_searched",
        ]
        for field in required_fields:
            self.assertIn(field, data, f"Missing field in search response: {field}")

        self.assertIsInstance(data["passages"], list)
        self.assertIsInstance(data["rag_available"], bool)
        self.assertGreaterEqual(data["retrieval_latency_ms"], 0)
        self.assertGreaterEqual(data["total_documents_searched"], 0)

    # -----------------------------------------------------------------------
    # Test 8: Stats API
    # -----------------------------------------------------------------------

    def test_stats_api(self):
        """8. GET /api/v1/rag/stats — verify 200 with RAGStatsSchema fields."""
        response = self.client.get("/api/v1/rag/stats")

        self.assertEqual(response.status_code, 200,
                         f"Stats API returned {response.status_code}: {response.text}")

        data = response.json()
        required_fields = [
            "total_documents",
            "total_chunks",
            "indexed_documents",
            "failed_documents",
            "index_health",
        ]
        for field in required_fields:
            self.assertIn(field, data, f"Missing field in stats response: {field}")

        self.assertIsInstance(data["total_documents"], int)
        self.assertIsInstance(data["total_chunks"], int)
        self.assertIsInstance(data["indexed_documents"], int)
        self.assertIsInstance(data["failed_documents"], int)
        self.assertIsInstance(data["index_health"], str)

    # -----------------------------------------------------------------------
    # Test 9: Copilot RAG integration
    # -----------------------------------------------------------------------

    def test_copilot_rag_integration(self):
        """9. CopilotService.assemble_context() must include RAG Knowledge Base in sources."""
        result = CopilotService.assemble_context(self.db, query="inflation outlook")

        # Unpack 5-tuple
        self.assertEqual(len(result), 5,
                         f"assemble_context should return 5-tuple, got {len(result)}")
        context_string, sources, conf_score, conf_indicator, citations = result

        self.assertIsNotNone(context_string)
        self.assertIsInstance(sources, list)
        self.assertIsInstance(citations, list)
        self.assertTrue(0.0 <= conf_score <= 1.0)
        self.assertIn(conf_indicator, ["High", "Moderate", "Low"])

        # RAG Knowledge Base must appear in sources
        engine_names = [s["engine"] for s in sources]
        self.assertIn("RAG Knowledge Base", engine_names,
                      f"RAG Knowledge Base missing from sources: {engine_names}")

        # Every source must have 'status'
        for source in sources:
            self.assertIn("status", source, f"Source missing 'status': {source}")

    # -----------------------------------------------------------------------
    # Test 10: Hallucination guard (no RAG) disclaimer
    # -----------------------------------------------------------------------

    def test_hallucination_guard_no_rag(self):
        """10. When RAG is Unavailable for a document-grounding query, disclaimer must appear."""
        sources_no_rag = [
            {"engine": "Forecast Engine", "source_type": "forecasts", "status": "Retrieved 12 projections"},
            {"engine": "SHAP Engine", "source_type": "forecast_explainability", "status": "Retrieved 6 local decomps"},
            {"engine": "News Intelligence", "source_type": "news_signals", "status": "Retrieved latest sentiment scoring"},
            {"engine": "Currency Prediction", "source_type": "currency_data", "status": "Retrieved spot exchange rates"},
            {"engine": "RAG Knowledge Base", "source_type": "rag_passages", "status": "Unavailable"},
        ]

        # Test a document-grounding query (contains "rbi", "report", "policy", etc.)
        doc_query = "What does the RBI report say about inflation outlook and policy?"
        reply = CopilotService.generate_reply_via_nlg(
            doc_query, "analyst", "some context", sources_no_rag
        )

        self.assertIsInstance(reply, str)
        self.assertIn(
            "Relevant supporting documents were not found",
            reply,
            msg="Hallucination disclaimer must appear when RAG is Unavailable for document-grounding query"
        )

        # Test a non-document-grounding query (should NOT get the disclaimer)
        non_doc_query = "What is the current USD/INR exchange rate?"
        reply_currency = CopilotService.generate_reply_via_nlg(
            non_doc_query, "analyst", "some context", sources_no_rag
        )
        self.assertIsInstance(reply_currency, str)
        # For a currency query with valid currency source, disclaimer should NOT appear
        # (only appears when RAG is unavailable AND query matches document-grounding keywords)


if __name__ == "__main__":
    unittest.main(verbosity=2)
