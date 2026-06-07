# Module: app.services.currency_service
# Description: Service handling forex conversions and commodity pricing indices.

import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.currency import CurrencyData


class CurrencyService:
    @staticmethod
    def get_mock_currency_records():
        """Get realistic mock currency spot records matching frontend overlays."""
        dates = [
            datetime(2026, 1, 1),
            datetime(2026, 2, 1),
            datetime(2026, 3, 1),
            datetime(2026, 4, 1),
            datetime(2026, 5, 1),
            datetime(2026, 6, 1)
        ]
        rates = [
            {"usd_inr": 83.15, "eur_usd": 1.09, "brent_crude": 79.40, "gold_index": 62500.0},
            {"usd_inr": 83.22, "eur_usd": 1.08, "brent_crude": 81.10, "gold_index": 63100.0},
            {"usd_inr": 82.95, "eur_usd": 1.10, "brent_crude": 84.50, "gold_index": 64200.0},
            {"usd_inr": 82.80, "eur_usd": 1.11, "brent_crude": 83.20, "gold_index": 65000.0},
            {"usd_inr": 82.65, "eur_usd": 1.12, "brent_crude": 80.50, "gold_index": 66800.0},
            {"usd_inr": 82.52, "eur_usd": 1.13, "brent_crude": 77.80, "gold_index": 67200.0}
        ]
        
        records = []
        for idx, date in enumerate(dates):
            rate = rates[idx]
            records.append({
                "id": uuid.UUID(int=idx + 2000),
                "recording_date": date,
                "usd_inr": rate["usd_inr"],
                "eur_usd": rate["eur_usd"],
                "brent_crude": rate["brent_crude"],
                "gold_index": rate["gold_index"]
            })
        return records

    @staticmethod
    def get_forex_rates(db: Session):
        """Query DB forex rates first. If empty, return mock data."""
        try:
            db_rates = db.query(CurrencyData).order_by(CurrencyData.recording_date.asc()).all()
            if db_rates:
                return db_rates
        except Exception as e:
            print(f"Database query failed in CurrencyService.get_forex_rates: {e}")
        return CurrencyService.get_mock_currency_records()

    @staticmethod
    def get_commodity_rates(db: Session):
        """Query DB commodity rates first. If empty, return mock data."""
        try:
            db_rates = db.query(CurrencyData).order_by(CurrencyData.recording_date.asc()).all()
            if db_rates:
                return db_rates
        except Exception as e:
            print(f"Database query failed in CurrencyService.get_commodity_rates: {e}")
        return CurrencyService.get_mock_currency_records()

    @staticmethod
    def get_currency_predictions(db: Session):
        """Query DB currency forecasts first. If empty, return mock data."""
        try:
            from app.models.currency import CurrencyForecast
            db_forecasts = db.query(CurrencyForecast).order_by(CurrencyForecast.forecast_date.asc()).all()
            if db_forecasts and len(db_forecasts) > 0:
                return db_forecasts
        except Exception as e:
            print(f"Database query failed in CurrencyService.get_currency_predictions: {e}")
            
        # Fallback mock predictions
        import uuid
        from datetime import datetime, timedelta
        base_date = datetime.utcnow()
        horizons = [30, 60, 90, 180, 365]
        assets = ["USD/INR", "EUR/USD", "Brent Crude", "Gold"]
        mock_preds = []
        for asset in assets:
            base_val = 83.15 if asset == "USD/INR" else (1.10 if asset == "EUR/USD" else (82.50 if asset == "Brent Crude" else 65000.0))
            for horizon in horizons:
                target_date = base_date + timedelta(days=horizon)
                projected = base_val * (1.0 + (horizon * 0.0001))
                mock_preds.append({
                    "id": uuid.uuid4(),
                    "target_asset": asset,
                    "horizon_days": horizon,
                    "forecast_date": target_date,
                    "projected_value": round(projected, 4),
                    "confidence_upper": round(projected * 1.05, 4),
                    "confidence_lower": round(projected * 0.95, 4),
                    "generated_at": base_date
                })
        return mock_preds

    @staticmethod
    def get_currency_impact_scores(db: Session):
        """Retrieve currency impact score trends from DB first, falling back to mock if empty."""
        try:
            db_latest = db.query(CurrencyData).order_by(CurrencyData.recording_date.desc()).first()
            if db_latest and db_latest.usd_inr_trend_score is not None:
                return {
                    "currency_trend_score": db_latest.usd_inr_trend_score,
                    "currency_risk_score": db_latest.usd_inr_risk_score,
                    "commodity_shock_score": db_latest.brent_crude_shock_score,
                    "inflation_impact_score": db_latest.inflation_impact_score,
                    "recording_date": db_latest.recording_date
                }
        except Exception as e:
            print(f"Database query failed in CurrencyService.get_currency_impact_scores: {e}")
            
        return {
            "currency_trend_score": 1.25,
            "currency_risk_score": 3.45,
            "commodity_shock_score": 2.10,
            "inflation_impact_score": 1.95,
            "recording_date": datetime.utcnow()
        }
