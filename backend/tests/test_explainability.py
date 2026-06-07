# Module: tests.test_explainability
# Description: Automated unit and integration tests for Phase 10: SHAP Explainability Dashboard.

import os
import sys
import unittest
import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import Base
from app.models.explainability import ForecastExplainability
from app.schemas.explainability import (
    GlobalImportanceResponseSchema,
    LocalExplainabilityResponseSchema,
    ForecastComparisonResponseSchema,
    TopDriverResponseSchema
)
from app.services.forecast_service import ForecastService
from app.api.deps import get_current_user, get_db
from app.models.user import User

SQLITE_PATH = "sqlite:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "local_sqlite.db")).replace("\\", "/")

# Mock analyst user for routing tests
mock_analyst = User(
    id=uuid.uuid4(),
    email="analyst@inflationiq.ai",
    full_name="Analyst User",
    role="analyst",
    is_active=True,
    created_at=datetime.utcnow()
)


class TestSHAPExplainabilityDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(SQLITE_PATH)
        Base.metadata.create_all(bind=cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)
        
    def setUp(self):
        self.db = self.Session()
        self.client = TestClient(app)
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_analyst
        app.dependency_overrides[get_db] = lambda: self.db
        
    def tearDown(self):
        self.db.close()
        app.dependency_overrides.clear()

    def test_mathematical_consistency(self):
        """1. Mathematical Consistency: Assert base_value + sum(contributions) == prediction_value."""
        local_explain = ForecastService.get_local_explainability(self.db, "ensemble")
        self.assertTrue(len(local_explain) > 0)
        
        for record in local_explain:
            # Map database or dict fields
            if hasattr(record, "base_value"):
                base_val = record.base_value
                pred_val = record.prediction_value
                sum_contrib = (
                    record.cpi_momentum_contribution +
                    record.commodity_shock_contribution +
                    record.currency_exchange_contribution +
                    record.risk_sentiment_contribution +
                    record.monetary_policy_contribution
                )
            else:
                base_val = record["base_value"]
                pred_val = record["prediction_value"]
                sum_contrib = (
                    record["cpi_momentum_contribution"] +
                    record["commodity_shock_contribution"] +
                    record["currency_exchange_contribution"] +
                    record["risk_sentiment_contribution"] +
                    record["monetary_policy_contribution"]
                )
                
            self.assertAlmostEqual(base_val + sum_contrib, pred_val, places=4)

    def test_api_schema_compliance(self):
        """2. API Schema Compliance: Validate API responses match Pydantic schemas exactly."""
        headers = {"Authorization": "Bearer mock_token"}
        
        # A. Global explainability
        res_global = self.client.get("/api/v1/forecasting/explainability/global", headers=headers)
        self.assertEqual(res_global.status_code, 200)
        for item in res_global.json():
            GlobalImportanceResponseSchema(**item)
            
        # B. Local explainability
        res_local = self.client.get("/api/v1/forecasting/explainability/local?model_type=ensemble", headers=headers)
        self.assertEqual(res_local.status_code, 200)
        for item in res_local.json():
            LocalExplainabilityResponseSchema(**item)
            
        # C. Forecast Comparison
        res_comp = self.client.get("/api/v1/forecasting/explainability/comparison?model_type=ensemble", headers=headers)
        self.assertEqual(res_comp.status_code, 200)
        for item in res_comp.json():
            ForecastComparisonResponseSchema(**item)
            
        # D. Top Drivers
        res_drivers = self.client.get("/api/v1/forecasting/top-drivers?model_type=ensemble", headers=headers)
        self.assertEqual(res_drivers.status_code, 200)
        for item in res_drivers.json():
            TopDriverResponseSchema(**item)

    def test_cache_persistence(self):
        """3. Cache Strategy Assert: Validate caching to SQLite database behaves correctly."""
        # Querying projections should create the cached forecast explainability entries in DB
        from app.models.cpi import InflationData
        
        # Ensure we have at least one inflation data record to run projections successfully
        inf_count = self.db.query(InflationData).count()
        if inf_count > 0:
            # Clear forecasts and explainability cache
            from app.models.forecast import Forecast
            self.db.query(Forecast).filter(Forecast.model_type == "ensemble").delete()
            self.db.query(ForecastExplainability).filter(ForecastExplainability.model_type == "ensemble").delete()
            self.db.commit()
            
            # Generate projections, which triggers persistence
            projections = ForecastService.get_projections("ensemble", self.db)
            
            # Verify cached explainability rows
            cached_count = self.db.query(ForecastExplainability).filter(ForecastExplainability.model_type == "ensemble").count()
            self.assertEqual(cached_count, len(projections))

    def test_fallback_logic(self):
        """4. Model Fallback: Validate degraded fallback operation when database is empty."""
        # Clean out database explainability to simulate empty db state
        self.db.query(ForecastExplainability).delete()
        self.db.commit()
        
        # Querying service layer directly should return mock structures seamlessly
        mock_explains = ForecastService.get_local_explainability(self.db, "ensemble")
        self.assertEqual(len(mock_explains), 12)
        for item in mock_explains:
            # Should have the correct fallback keys
            self.assertIn("base_value", item)
            self.assertIn("prediction_value", item)
            self.assertEqual(item["confidence_indicator"], "High")


if __name__ == "__main__":
    unittest.main()
