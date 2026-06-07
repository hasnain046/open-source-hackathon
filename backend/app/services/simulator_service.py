# Module: app.services.simulator_service
# Description: Service handling policy slider inputs and evaluating simulated CPI changes.

import uuid
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from app.models.simulation import Simulation
from app.schemas.simulation import RunSimulationSchema


class SimulatorService:
    @staticmethod
    def run_shock_simulation(user_id: str | None, params: RunSimulationSchema, db: Session):
        """Evaluate simulated CPI changes using ML forecasting models with exogenous overrides."""
        # Baseline multipliers fallback
        baseline_rate = 4.82
        oil_effect = (params.oil_change / 10.0) * 0.22
        rate_effect = (params.interest_rate_change / 100.0) * -0.35
        currency_effect = params.currency_change * -0.10
        projected_rate = round(baseline_rate + oil_effect + rate_effect + currency_effect, 3)

        # Try using the real XGBoost ML model
        try:
            from app.services.forecast_service import ForecastService
            ForecastService.load_models()

            from app.pipelines.forecaster import ForecastPipeline
            df_raw = ForecastPipeline.load_data_from_db(db)

            if len(df_raw) >= 12 and ForecastService._xgb_model is not None and ForecastService._feature_cols is not None:
                # Construct features for the next month (t+1)
                last_date = df_raw['date'].max()
                target_date = last_date + pd.DateOffset(months=1)
                last_row = df_raw.iloc[-1].copy()

                # Apply shocks as overrides to exogenous variables
                brent_crude_val = last_row["brent_crude"] + params.oil_change
                # Currency change: local strength increase means exchange rate decreases (fewer local units per USD)
                usd_inr_val = last_row["usd_inr"] * (1.0 - params.currency_change / 100.0)

                # Append the future row
                new_row = {
                    "date": target_date,
                    "headline": last_row["headline"], # guess
                    "core": last_row["core"],
                    "wholesale": last_row["wholesale"],
                    "usd_inr": usd_inr_val,
                    "eur_usd": last_row["eur_usd"],
                    "brent_crude": brent_crude_val,
                    "gold_index": last_row["gold_index"],
                    "news_sentiment": last_row["news_sentiment"],
                    "economic_risk": last_row["economic_risk"],
                    "inflation_pressure": last_row["inflation_pressure"]
                }
                df_sim = pd.concat([df_raw, pd.DataFrame([new_row])], ignore_index=True)

                # Re-calculate features
                df_temp = df_sim.copy()
                df_temp["month"] = df_temp["date"].dt.month
                df_temp["quarter"] = df_temp["date"].dt.quarter

                for col in ["headline", "brent_crude", "usd_inr", "news_sentiment", "economic_risk", "inflation_pressure"]:
                    for lag in [1, 2, 3, 6, 12]:
                        df_temp[f"{col}_lag_{lag}"] = df_temp[col].shift(lag)

                for col in ["brent_crude", "headline"]:
                    for window in [3, 6]:
                        df_temp[f"{col}_roll_mean_{window}"] = df_temp[col].shift(1).rolling(window=window).mean()
                        df_temp[f"{col}_roll_std_{window}"] = df_temp[col].shift(1).rolling(window=window).std()

                df_temp["headline_diff"] = df_temp["headline"].shift(1) - df_temp["headline"].shift(2)

                # Predict using XGBoost
                X_pred = df_temp[ForecastService._feature_cols].iloc[[-1]]
                xgb_pred = float(ForecastService._xgb_model.predict(X_pred)[0])

                # Combine XGBoost projection with the monetary policy transmission channel (interest rate effect)
                projected_rate = round(xgb_pred + rate_effect, 3)
                print(f"Simulator successfully evaluated shock projection using ML models: {projected_rate}")
        except Exception as e:
            print(f"Real-time ML simulator evaluation failed ({e}). Falling back to static multipliers.")

        # Generate a fallback UUID and execution time immediately
        res_id = uuid.uuid4()
        executed_at = datetime.utcnow()

        if user_id:
            try:
                user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
                db_sim = Simulation(
                    id=res_id,  # Explicitly assign pre-generated UUID
                    user_id=user_uuid,
                    input_crude_change=params.oil_change,
                    input_rate_change=params.interest_rate_change,
                    input_currency_change=params.currency_change,
                    output_projected_rate=projected_rate,
                    executed_at=executed_at
                )
                db.add(db_sim)
                db.commit()
                db.refresh(db_sim)
                res_id = db_sim.id
                executed_at = db_sim.executed_at
            except Exception as e:
                db.rollback()
                print(f"Failed to persist simulation in SimulatorService: {e}")

        return {
            "id": res_id,
            "user_id": user_id,
            "input_crude_change": params.oil_change,
            "input_rate_change": params.interest_rate_change,
            "input_currency_change": params.currency_change,
            "output_projected_rate": projected_rate,
            "executed_at": executed_at
        }
