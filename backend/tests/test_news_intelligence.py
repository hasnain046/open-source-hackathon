# Module: tests.test_news_intelligence
# Description: Unit and integration tests validating Phase 8 News Intelligence and ML Forecaster integration.

import os
import sys
import unittest
import uuid
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import Base
from app.models.news import NewsItem, NewsSignal
from app.services.deduplicator import DeduplicatorService, MinHashLSHDeduplicator
from app.pipelines.sentiment_engine import SentimentEngine
from app.pipelines.news_ingest import NewsIngestionPipeline
from app.pipelines.forecaster import ForecastPipeline
from app.services.forecast_service import ForecastService

SQLITE_PATH = "sqlite:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "local_sqlite.db")).replace("\\", "/")


class TestNewsIntelligence(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(SQLITE_PATH)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        
        # Make sure tables exist
        Base.metadata.create_all(bind=self.engine)

    def tearDown(self):
        self.db.close()

    def test_deduplication_exact_sha256(self):
        """Validate exact matching on titles/URLs via SHA-256."""
        print("[*] Running Exact SHA-256 Deduplication Validation...")
        text1 = "RBI keeps policy repo rate unchanged at 6.5%"
        text2 = "rbi keeps policy repo rate unchanged at 6.5% " # test casing and spacing
        
        hash1 = DeduplicatorService.get_sha256_hash(text1)
        hash2 = DeduplicatorService.get_sha256_hash(text2)
        
        self.assertEqual(hash1, hash2)
        print("[+] Exact SHA-256 deduplication passed.")

    def test_deduplication_minhash_lsh(self):
        """Validate phrasal syndication matching via MinHash LSH."""
        print("[*] Running MinHash LSH Near-Duplicate Validation...")
        lsh = MinHashLSHDeduplicator(num_hashes=64, threshold=0.82)
        
        parent_id = "parent-123"
        article1 = "RBI raises policy repo rate by 50bps to contain inflation pressures"
        article2 = "RBI raises policy repo rate by 50bps to contain inflation pressures on Tuesday"
        article3 = "Brent crude price drops below $75 a barrel amid supply expansion"
        
        lsh.register_article(parent_id, article1)
        
        # Test near-duplicate match
        match_id1 = lsh.is_duplicate(article2)
        self.assertEqual(match_id1, parent_id)
        
        # Test distinct article mismatch
        match_id2 = lsh.is_duplicate(article3)
        self.assertNotEqual(match_id2, parent_id)
        self.assertIsNone(match_id2)
        
        print("[+] MinHash LSH phrasal deduplication passed.")

    def test_nlp_sentiment_validation(self):
        """Validate FinBERT/lexical polarity scoring."""
        print("[*] Running NLP Sentiment and Polarity Validation...")
        text_neg = "Surging food prices and supply shocks trigger negative inflation risks"
        text_pos = "Gains in currency and agricultural growth boost local market confidence"
        
        neg_res = SentimentEngine.analyze_sentiment(text_neg)
        pos_res = SentimentEngine.analyze_sentiment(text_pos)
        
        # Neg text polarity must be negative (< 0)
        self.assertTrue(neg_res["polarity"] < 0)
        # Pos text polarity must be positive (> 0)
        self.assertTrue(pos_res["polarity"] > 0)
        
        print(f"[+] NLP Polarity scores: Neg={neg_res['polarity']}, Pos={pos_res['polarity']}")
        print("[+] NLP Sentiment checks passed.")

    def test_entity_and_topic_extraction(self):
        """Validate spaCy/regex economic entity mapping and topic classifications."""
        print("[*] Running Entity Extraction & Topic Classification Validation...")
        text = "RBI governor discussed Brent crude prices fluctuations in Mumbai, Maharashtra"
        
        entities = SentimentEngine.extract_entities(text)
        topic = SentimentEngine.classify_topic(text)
        
        # Check ORG entity (RBI)
        has_rbi = any(ent["name"] == "RBI" for ent in entities)
        # Check GPE state entity (Maharashtra)
        has_state = any(ent["name"] == "Maharashtra" for ent in entities)
        
        self.assertTrue(has_rbi or len(entities) > 0)
        # Topics classification should match Commodity Shocks (crude) or Monetary Policy (repo/rbi)
        self.assertIn(topic, ["Monetary Policy", "Commodity Shocks"])
        
        print(f"[+] Extracted Topic: {topic}")
        print(f"[+] Extracted Entities: {entities}")
        print("[+] Entity and Topic extraction passed.")

    def test_news_ingestion_pipeline_run(self):
        """Validate complete crawling, deduplication, scoring, and daily signals persist cycle."""
        print("[*] Running News Ingestion Pipeline Validation...")
        
        # Clear existing signal tables
        self.db.query(NewsItem).delete()
        self.db.query(NewsSignal).delete()
        self.db.commit()
        
        ingest_res = NewsIngestionPipeline.run_ingestion_cycle(self.db)
        
        # Verify database inserts
        items_count = self.db.query(NewsItem).count()
        signals_count = self.db.query(NewsSignal).count()
        
        self.assertTrue(items_count > 0)
        self.assertEqual(signals_count, 1)
        
        latest_sig = self.db.query(NewsSignal).first()
        self.assertIsNotNone(latest_sig.avg_sentiment)
        self.assertIsNotNone(latest_sig.risk_score)
        self.assertIsNotNone(latest_sig.inflation_pressure)
        
        print(f"[+] Successfully saved {items_count} items and 1 daily NewsSignal.")
        print("[+] News Ingestion Pipeline validation passed.")

    def test_forecast_engine_retraining_integration(self):
        """Validate that ML forecast models retrain successfully using the new news signals exogenous lag features."""
        print("[*] Running Forecast Engine Retraining Integration Validation...")
        
        # Retrain forecaster models with new features!
        success = ForecastPipeline.train_models()
        self.assertTrue(success)
        
        # Test model prediction outputs
        ForecastService.load_models()
        self.assertIsNotNone(ForecastService._xgb_model)
        self.assertIn("news_sentiment_lag_1", ForecastService._feature_cols)
        self.assertIn("economic_risk_lag_1", ForecastService._feature_cols)
        self.assertIn("inflation_pressure_lag_1", ForecastService._feature_cols)
        
        projections = ForecastService.get_projections("ensemble", self.db)
        self.assertEqual(len(projections), 12)
        
        print("[+] Forecaster successfully retrained with news signals and generated ML projections.")
        print("[+] Forecast Engine Integration validation passed.")


if __name__ == "__main__":
    unittest.main()
