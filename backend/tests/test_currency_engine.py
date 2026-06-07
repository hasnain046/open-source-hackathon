# Module: tests.test_currency_engine
# Description: Automated unit and integration tests for Phase 9: Currency Prediction Engine.

import os
import sys
import unittest
import uuid
from datetime import datetime, timedelta
import torch
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import Base
from app.models.currency import CurrencyData, CurrencyForecast
from app.pipelines.currency_forecaster import CurrencyForecastPipeline, PyTorchLSTMModel
from app.services.currency_service import CurrencyService

SQLITE_PATH = "sqlite:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "local_sqlite.db")).replace("\\", "/")


class TestCurrencyPredictionEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(SQLITE_PATH)
        cls.Session = sessionmaker(bind=cls.engine)
        
    def setUp(self):
        self.db = self.Session()
        
    def tearDown(self):
        self.db.close()

    def test_pytorch_lstm_model_inference(self):
        """1. LSTM Inference check: Verify LSTM forward pass shapes and types."""
        # Create a dummy model
        model = PyTorchLSTMModel(input_dim=5, hidden_dim=16, num_layers=1, output_dim=1)
        model.eval()
        
        # input batch_size=2, seq_len=1, input_dim=5
        dummy_input = torch.randn(2, 1, 5)
        with torch.no_grad():
            output = model(dummy_input)
            
        self.assertEqual(output.shape, (2, 1))
        self.assertTrue(isinstance(output, torch.Tensor))

    def test_scoring_signal_boundaries(self):
        """2. Signal Validation: Assert Trend, Risk, Shock, and Inflation Impact scores fall within valid bounds."""
        latest_record = self.db.query(CurrencyData).order_by(CurrencyData.recording_date.desc()).first()
        if latest_record is not None and latest_record.usd_inr_trend_score is not None:
            # Validate actual database records
            self.assertTrue(-20.0 <= latest_record.usd_inr_trend_score <= 20.0, f"Trend score {latest_record.usd_inr_trend_score} out of bounds")
            self.assertTrue(0.0 <= latest_record.usd_inr_risk_score <= 10.0, f"Risk score {latest_record.usd_inr_risk_score} out of bounds")
            self.assertTrue(0.0 <= latest_record.brent_crude_shock_score <= 10.0, f"Shock score {latest_record.brent_crude_shock_score} out of bounds")
            self.assertTrue(0.0 <= latest_record.inflation_impact_score <= 10.0, f"Inflation impact score {latest_record.inflation_impact_score} out of bounds")
        
        # Test the service fallback responses bounds as well
        scores = CurrencyService.get_currency_impact_scores(self.db)
        self.assertIn("currency_trend_score", scores)
        self.assertIn("currency_risk_score", scores)
        self.assertIn("commodity_shock_score", scores)
        self.assertIn("inflation_impact_score", scores)
        
        self.assertTrue(-20.0 <= scores["currency_trend_score"] <= 20.0)
        self.assertTrue(0.0 <= scores["currency_risk_score"] <= 10.0)
        self.assertTrue(0.0 <= scores["commodity_shock_score"] <= 10.0)
        self.assertTrue(0.0 <= scores["inflation_impact_score"] <= 10.0)

    def test_database_persistence_and_horizons(self):
        """3. Database Integration: Assert currency_forecasts writes and queries support 30, 60, 90, 180, 365 day horizons."""
        # Query forecasts
        forecasts = self.db.query(CurrencyForecast).all()
        
        # If no forecasts exist in DB (e.g. fresh db), generate them using pipeline
        if len(forecasts) == 0:
            success = CurrencyForecastPipeline.train_models()
            self.assertTrue(success, "Pipeline training failed")
            forecasts = self.db.query(CurrencyForecast).all()
            
        self.assertTrue(len(forecasts) > 0, "No currency forecasts found or persisted in database.")
        
        # Assert horizons check (30, 60, 90, 180, 365)
        expected_horizons = {30, 60, 90, 180, 365}
        db_horizons = set(f.horizon_days for f in forecasts)
        
        # Check that all expected horizons are subset of what we have in DB
        self.assertTrue(expected_horizons.issubset(db_horizons), f"Horizons {expected_horizons} not fully satisfied by DB horizons {db_horizons}")
        
        # Assert assets checked
        expected_assets = {"USD/INR", "Brent Crude"}
        db_assets = set(f.target_asset for f in forecasts)
        self.assertTrue(expected_assets.issubset(db_assets), f"Assets {expected_assets} not fully satisfied by DB assets {db_assets}")

    def test_forecast_engine_integration(self):
        """4. Forecast Engine Integration: Verify forecast service utilizes historical currency data for feature matrix."""
        from app.services.forecast_service import ForecastService
        ForecastService.load_models()
        
        # Query inflation data to see if we have records
        from app.models.cpi import InflationData
        from app.models.news import NewsSignal
        
        inf_count = self.db.query(InflationData).count()
        curr_count = self.db.query(CurrencyData).count()
        sig_count = self.db.query(NewsSignal).count()
        
        if inf_count > 0 and curr_count > 0 and sig_count > 0:
            # Should run without raising errors
            try:
                projections = ForecastService.get_projections("ensemble", self.db)
                self.assertTrue(len(projections) > 0)
                # Verify that it fetched from database if cached, or generated successfully
                self.assertIsNotNone(projections[0])
            except Exception as e:
                self.fail(f"ForecastService integration check failed: {e}")


if __name__ == "__main__":
    unittest.main()
