# Module: app.services.rag_service
# Description: Core retrieval service implementing hybrid search (dense + BM25 + RRF),
# cross-encoder reranking, freshness ranking, citation confidence tagging,
# and diversity filtering for the RAG Knowledge Base.

import os
import uuid
import json
import math
import time
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.models.rag import RagDocument, RagChunk, RagRetrievalLog
from app.schemas.rag import RAGStatsSchema
from app.config import settings

# ---------------------------------------------------------------------------
# Optional ML imports — all guarded
# ---------------------------------------------------------------------------

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False
    print("[RAGService] WARNING: sentence_transformers not installed.")

try:
    from sentence_transformers.cross_encoder import CrossEncoder
    CE_AVAILABLE = True
except ImportError:
    CE_AVAILABLE = False
    print("[RAGService] WARNING: CrossEncoder (sentence_transformers) not installed.")

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("[RAGService] WARNING: chromadb not installed.")

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    print("[RAGService] WARNING: rank_bm25 not installed. BM25 search disabled.")


class RAGService:
    """
    Retrieval service implementing the full hybrid RAG pipeline:
      Dense search → BM25 sparse search → RRF fusion → cross-encoder reranking →
      freshness ranking → diversity filter → citation confidence tagging.
    """

    # Class-level lazy-loaded singletons
    _embedding_model = None
    _reranker_model = None
    _chroma_client = None
    _chroma_collection = None
    _bm25_index = None
    _bm25_corpus: List[str] = []
    _bm25_chunk_ids: List[str] = []

    # ------------------------------------------------------------------
    # Lazy singletons
    # ------------------------------------------------------------------

    @classmethod
    def _get_embedding_model(cls):
        """Load all-MiniLM-L6-v2 once; return None if unavailable."""
        if cls._embedding_model is None and ST_AVAILABLE:
            try:
                model_name = getattr(settings, "RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
                cls._embedding_model = SentenceTransformer(model_name)
            except Exception as e:
                print(f"[RAGService] Embedding model load failed: {e}")
        return cls._embedding_model

    @classmethod
    def _get_reranker(cls):
        """Load cross-encoder/ms-marco-MiniLM-L-6-v2 once; return None if unavailable."""
        if cls._reranker_model is None and CE_AVAILABLE:
            try:
                model_name = getattr(settings, "RAG_RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
                cls._reranker_model = CrossEncoder(model_name)
            except Exception as e:
                print(f"[RAGService] Reranker model load failed: {e}")
        return cls._reranker_model

    @classmethod
    def _get_chroma_collection(cls):
        """Return ChromaDB PersistentClient collection; None if unavailable."""
        if cls._chroma_collection is None and CHROMADB_AVAILABLE:
            try:
                persist_dir = getattr(settings, "CHROMA_PERSIST_DIR", "./chroma_store")
                os.makedirs(persist_dir, exist_ok=True)
                cls._chroma_client = chromadb.PersistentClient(path=persist_dir)
                cls._chroma_collection = cls._chroma_client.get_or_create_collection(
                    name="inflationiq_rag",
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception as e:
                print(f"[RAGService] ChromaDB init failed: {e}")
        return cls._chroma_collection

    @classmethod
    def _build_bm25_index(cls, db: Session) -> None:
        """Build in-memory BM25Okapi index from all chunk texts in ChromaDB."""
        if not BM25_AVAILABLE:
            return
        try:
            collection = cls._get_chroma_collection()
            if collection is None:
                return
            count = collection.count()
            if count == 0:
                return
            results = collection.get(include=["documents", "metadatas"])
            cls._bm25_corpus = results.get("documents", []) or []
            cls._bm25_chunk_ids = results.get("ids", []) or []
            if cls._bm25_corpus:
                tokenized = [doc.lower().split() for doc in cls._bm25_corpus]
                cls._bm25_index = BM25Okapi(tokenized)
        except Exception as e:
            print(f"[RAGService] BM25 index build failed: {e}")

    # ------------------------------------------------------------------
    # Main retrieval method
    # ------------------------------------------------------------------

    @classmethod
    def retrieve(
        cls,
        db: Session,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        freshness_enabled: bool = True,
        search_mode: str = "hybrid",
    ) -> Dict[str, Any]:
        """
        Full retrieval pipeline returning ranked passages with scores and citations.
        Returns rag_available=False gracefully when ChromaDB or model is unavailable.
        """
        start_ts = time.time()
        passages = []
        rag_available = False
        freshness_applied = False
        total_docs = 0

        try:
            collection = cls._get_chroma_collection()
            embed_model = cls._get_embedding_model()

            if collection is None:
                raise RuntimeError("ChromaDB collection unavailable")

            total_docs = collection.count()
            if total_docs == 0:
                raise RuntimeError("ChromaDB collection is empty")

            # Build where clause from filters
            where_clause = cls._build_where_clause(filters)

            # 1. Dense retrieval
            dense_results: Dict[str, float] = {}  # chunk_id → score
            dense_texts: Dict[str, str] = {}
            dense_metas: Dict[str, Dict] = {}

            if embed_model is not None:
                query_vec = embed_model.encode([query], show_progress_bar=False)[0].tolist()
                query_kwargs: Dict[str, Any] = {
                    "query_embeddings": [query_vec],
                    "n_results": min(20, total_docs),
                    "include": ["documents", "metadatas", "distances"],
                }
                if where_clause:
                    query_kwargs["where"] = where_clause
                dense_res = collection.query(**query_kwargs)
                for cid, dist, doc, meta in zip(
                    dense_res["ids"][0],
                    dense_res["distances"][0],
                    dense_res["documents"][0],
                    dense_res["metadatas"][0],
                ):
                    # ChromaDB cosine distance → similarity: score = 1 - distance
                    score = max(0.0, 1.0 - float(dist))
                    dense_results[cid] = score
                    dense_texts[cid] = doc
                    dense_metas[cid] = meta

            # 2. BM25 sparse retrieval (for hybrid mode)
            bm25_results: Dict[str, float] = {}
            if search_mode == "hybrid" and BM25_AVAILABLE:
                if cls._bm25_index is None:
                    cls._build_bm25_index(db)
                if cls._bm25_index is not None:
                    tokenized_query = query.lower().split()
                    scores = cls._bm25_index.get_scores(tokenized_query)
                    # Map scores to chunk ids, take top-20
                    scored = sorted(
                        zip(cls._bm25_chunk_ids, scores), key=lambda x: x[1], reverse=True
                    )[:20]
                    max_score = max((s for _, s in scored), default=1.0) or 1.0
                    for cid, raw_score in scored:
                        bm25_results[cid] = raw_score / max_score  # normalize [0,1]

            # 3. RRF Fusion
            k = 60
            all_chunk_ids = set(dense_results) | set(bm25_results)
            dense_ranked = sorted(dense_results.items(), key=lambda x: x[1], reverse=True)
            bm25_ranked = sorted(bm25_results.items(), key=lambda x: x[1], reverse=True)
            dense_rank_map = {cid: idx + 1 for idx, (cid, _) in enumerate(dense_ranked)}
            bm25_rank_map = {cid: idx + 1 for idx, (cid, _) in enumerate(bm25_ranked)}

            fused: Dict[str, float] = {}
            for cid in all_chunk_ids:
                rrf = 0.0
                if cid in dense_rank_map:
                    rrf += 1.0 / (k + dense_rank_map[cid])
                if cid in bm25_rank_map:
                    rrf += 1.0 / (k + bm25_rank_map[cid])
                fused[cid] = rrf

            fused_top = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:20]

            # Build candidate list, enriching with texts/metas from collection.get()
            missing_ids = [cid for cid, _ in fused_top if cid not in dense_texts]
            if missing_ids:
                try:
                    extra = collection.get(ids=missing_ids, include=["documents", "metadatas"])
                    for cid, doc, meta in zip(
                        extra.get("ids", []),
                        extra.get("documents", []),
                        extra.get("metadatas", []),
                    ):
                        dense_texts[cid] = doc
                        dense_metas[cid] = meta or {}
                except Exception:
                    pass

            candidates = []
            for cid, rrf_score in fused_top:
                text = dense_texts.get(cid, "")
                meta = dense_metas.get(cid, {})
                # Use dense score if available, else rrf proxy
                relevance = dense_results.get(cid, rrf_score * 10)
                candidates.append({
                    "chunk_id": cid,
                    "text": text,
                    "meta": meta,
                    "relevance_score": relevance,
                    "rrf_score": rrf_score,
                })

            # 4. Cross-encoder reranking
            reranker = cls._get_reranker()
            if reranker is not None and candidates:
                try:
                    pairs = [(query, c["text"]) for c in candidates]
                    raw_scores = reranker.predict(pairs)
                    # Sigmoid normalize to [0,1]
                    for cand, raw in zip(candidates, raw_scores):
                        cand["relevance_score"] = float(1.0 / (1.0 + math.exp(-float(raw))))
                    candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
                except Exception as e:
                    print(f"[RAGService] Reranker error (using dense scores): {e}")

            # 5. Freshness ranking
            freshness_enabled_cfg = getattr(settings, "RAG_FRESHNESS_ENABLED", True)
            freshness_weight = getattr(settings, "RAG_FRESHNESS_WEIGHT", 0.15)
            decay_rate = getattr(settings, "RAG_FRESHNESS_DECAY_RATE", 0.002)
            delta = getattr(settings, "RAG_FRESHNESS_DELTA", 0.05)
            today = datetime.utcnow().date()

            for cand in candidates:
                pub_date_str = cand["meta"].get("publication_date", "")
                cand["freshness_score"] = cls._compute_freshness(pub_date_str, today, decay_rate)
                # Compute final score — only apply when scores are within delta
                rel = cand["relevance_score"]
                cand["final_score"] = rel  # default

            if freshness_enabled and freshness_enabled_cfg and len(candidates) > 1:
                for i in range(len(candidates)):
                    for j in range(i + 1, len(candidates)):
                        if abs(candidates[i]["relevance_score"] - candidates[j]["relevance_score"]) <= delta:
                            freshness_applied = True
                            break
                    if freshness_applied:
                        break

                if freshness_applied:
                    for cand in candidates:
                        rel = cand["relevance_score"]
                        frsh = cand["freshness_score"]
                        cand["final_score"] = (1 - freshness_weight) * rel + freshness_weight * frsh
                    candidates.sort(key=lambda x: x["final_score"], reverse=True)

            # 6. Diversity filter: max 2 chunks per document_id
            doc_chunk_count: Dict[str, int] = {}
            diverse_candidates = []
            for cand in candidates:
                doc_id = cand["meta"].get("document_id", "unknown")
                if doc_chunk_count.get(doc_id, 0) < 2:
                    doc_chunk_count[doc_id] = doc_chunk_count.get(doc_id, 0) + 1
                    diverse_candidates.append(cand)

            # 7. Citation confidence + min_score filter
            min_score = getattr(settings, "RAG_MIN_SCORE", 0.35)
            high_thresh = getattr(settings, "RAG_CONFIDENCE_HIGH", 0.75)
            medium_thresh = getattr(settings, "RAG_CONFIDENCE_MEDIUM", 0.50)

            rank = 1
            for cand in diverse_candidates:
                final = cand["final_score"]
                if final < min_score:
                    continue
                if final >= high_thresh:
                    confidence = "High"
                elif final >= medium_thresh:
                    confidence = "Medium"
                else:
                    confidence = "Low"

                meta = cand["meta"]
                pub_date = None
                pub_date_str = meta.get("publication_date", "")
                if pub_date_str:
                    try:
                        pub_date = datetime.strptime(pub_date_str, "%Y-%m-%d").date()
                    except Exception:
                        pass

                passages.append({
                    "rank": rank,
                    "relevance_score": round(cand["relevance_score"], 4),
                    "freshness_score": round(cand["freshness_score"], 4),
                    "final_score": round(final, 4),
                    "citation_confidence": confidence,
                    "text": cand["text"],
                    "citation": {
                        "source_name": meta.get("source_name", ""),
                        "publisher": meta.get("publisher", ""),
                        "publication_date": pub_date,
                        "page_number": meta.get("page_number"),
                        "section_title": meta.get("section_title", ""),
                        "chunk_id": cand["chunk_id"],
                    },
                })
                rank += 1
                if rank > top_k:
                    break

            rag_available = len(passages) > 0

        except Exception as exc:
            print(f"[RAGService] Retrieval error: {exc}")
            rag_available = False
            freshness_applied = False

        latency_ms = int((time.time() - start_ts) * 1000)

        # 10. Log to RagRetrievalLog
        try:
            log = RagRetrievalLog(
                id=uuid.uuid4(),
                query_text=query,
                retrieved_chunk_ids=json.dumps([p["citation"]["chunk_id"] for p in passages]),
                reranked_chunk_ids=json.dumps([p["citation"]["chunk_id"] for p in passages]),
                top_score=passages[0]["final_score"] if passages else None,
                retrieval_latency_ms=latency_ms,
                filter_applied=json.dumps(filters) if filters else None,
                hallucination_flagged=not rag_available,
                freshness_applied=freshness_applied,
            )
            db.add(log)
            db.commit()
        except Exception as log_exc:
            print(f"[RAGService] Retrieval log error: {log_exc}")

        rag_confidence = 0.0
        if passages:
            rag_confidence = round(sum(p["final_score"] for p in passages) / len(passages), 4)

        return {
            "query": query,
            "passages": passages,
            "rag_available": rag_available,
            "rag_confidence": rag_confidence,
            "freshness_applied": freshness_applied,
            "retrieval_latency_ms": latency_ms,
            "total_documents_searched": total_docs,
        }

    # ------------------------------------------------------------------
    # Stats & Maintenance
    # ------------------------------------------------------------------

    @classmethod
    def get_stats(cls, db: Session) -> Dict[str, Any]:
        """Return high-level index statistics."""
        try:
            total_documents = db.query(RagDocument).count()
            total_chunks = db.query(RagChunk).count()
            indexed_documents = db.query(RagDocument).filter(
                RagDocument.ingestion_status == "indexed"
            ).count()
            failed_documents = db.query(RagDocument).filter(
                RagDocument.ingestion_status == "failed"
            ).count()

            # Index health: compare ChromaDB count vs DB chunks count
            collection = cls._get_chroma_collection()
            if collection is not None:
                chroma_count = collection.count()
                mismatch_pct = abs(chroma_count - total_chunks) / max(total_chunks, 1) * 100
                if mismatch_pct > 5:
                    index_health = f"Degraded (mismatch {mismatch_pct:.1f}%)"
                else:
                    index_health = "Healthy"
            else:
                index_health = "ChromaDB Unavailable"

            return {
                "total_documents": total_documents,
                "total_chunks": total_chunks,
                "indexed_documents": indexed_documents,
                "failed_documents": failed_documents,
                "index_health": index_health,
            }
        except Exception as e:
            print(f"[RAGService] Stats error: {e}")
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "indexed_documents": 0,
                "failed_documents": 0,
                "index_health": "Error",
            }

    @classmethod
    def delete_document(cls, db: Session, document_id: uuid.UUID) -> bool:
        """Remove a document and all its chunks from ChromaDB and the DB."""
        try:
            # Remove from ChromaDB
            collection = cls._get_chroma_collection()
            if collection is not None:
                chunk_ids = [
                    str(c.id)
                    for c in db.query(RagChunk).filter(RagChunk.document_id == document_id).all()
                ]
                if chunk_ids:
                    collection.delete(ids=chunk_ids)
            # Remove from DB (cascade handles RagChunk)
            doc = db.query(RagDocument).filter(RagDocument.id == document_id).first()
            if doc:
                db.delete(doc)
                db.commit()
            # Invalidate BM25 cache
            cls._bm25_index = None
            cls._bm25_corpus = []
            cls._bm25_chunk_ids = []
            return True
        except Exception as e:
            print(f"[RAGService] Delete document error: {e}")
            return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_freshness(pub_date_str: str, today: date, decay_rate: float) -> float:
        """Compute freshness score: exp(-λ × age_days). Returns 0.0 if date missing."""
        if not pub_date_str:
            return 0.0
        try:
            pub_date = datetime.strptime(pub_date_str, "%Y-%m-%d").date()
            age_days = (today - pub_date).days
            return math.exp(-decay_rate * max(0, age_days))
        except Exception:
            return 0.0

    @staticmethod
    def _build_where_clause(filters: Optional[Dict[str, Any]]) -> Optional[Dict]:
        """Convert API filter dict to a ChromaDB where clause."""
        if not filters:
            return None
        conditions = []
        if filters.get("publisher"):
            publishers = filters["publisher"]
            if isinstance(publishers, list) and len(publishers) == 1:
                conditions.append({"publisher": {"$eq": publishers[0]}})
            elif isinstance(publishers, list):
                conditions.append({"publisher": {"$in": publishers}})
            elif isinstance(publishers, str):
                conditions.append({"publisher": {"$eq": publishers}})
        if filters.get("source_type"):
            source_types = filters["source_type"]
            if isinstance(source_types, list) and len(source_types) == 1:
                conditions.append({"source_type": {"$eq": source_types[0]}})
            elif isinstance(source_types, list):
                conditions.append({"source_type": {"$in": source_types}})
        if filters.get("from_date"):
            conditions.append({"publication_date": {"$gte": str(filters["from_date"])}})
        if filters.get("to_date"):
            conditions.append({"publication_date": {"$lte": str(filters["to_date"])}})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}
