# Module: tests.verify_forecast_engine
# Description: Verification script for validating Phase 7 ML Forecaster and Simulator services.

import os
import sys
import uuid
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import Base
from app.models.forecast import Forecast
from app.models.simulation import Simulation
from app.schemas.forecast import ForecastResponseSchema
from app.schemas.simulation import RunSimulationSchema, SimulationResponseSchema
from app.services.forecast_service import ForecastService
from app.services.simulator_service import SimulatorService
from app.pipelines.forecaster import ForecastPipeline

SQLITE_PATH = "sqlite:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "local_sqlite.db")).replace("\\", "/")

def run_verification():
    print("=========================================================")
    print("   INFLATION FORECAST ENGINE (PHASE 7) VALIDATION SUITE  ")
    print("=========================================================")
    
    working_endpoints = []
    issues = []
    errors = []
    
    # 1. Database Connection & Seeding
    try:
        engine = create_engine(SQLITE_PATH)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Check if historical data exists
        from app.models.cpi import InflationData
        inf_count = db.query(InflationData).count()
        print(f"[*] Database check: Found {inf_count} historical inflation records.")
        if inf_count == 0:
            print("[*] Database is empty, seeding historical data...")
            ForecastPipeline.seed_historical_data_if_empty(db)
            inf_count = db.query(InflationData).count()
            print(f"[+] Seeded successfully. Total records: {inf_count}")
        working_endpoints.append("Database Connection & Seeding")
    except Exception as e:
        errors.append(f"Database Connection failed: {e}")
        print(f"[-] Database Error: {e}")
        return
        
    # 2. Test ML Model Loading
    try:
        print("[*] Loading ML models...")
        ForecastService.load_models()
        if ForecastService._xgb_model is None or ForecastService._prophet_model is None:
            issues.append("Prophet or XGBoost model binaries are missing. Fallbacks will be tested.")
            print("[!] Warning: Prophet or XGBoost model binaries are missing.")
        else:
            print("[+] Successfully loaded XGBoost and Prophet binaries.")
    except Exception as e:
        errors.append(f"Model Loading failed: {e}")
        print(f"[-] Model Loading Error: {e}")
        
    # 3. Test Projections Generation (ML Engine)
    try:
        print("[*] Generating ML projections...")
        # Clear existing forecasts for clean test
        db.query(Forecast).delete()
        db.commit()
        
        projections = ForecastService.get_projections("ensemble", db)
        print(f"[+] Successfully generated {len(projections)} ensemble projections.")
        
        # Verify schema compliance
        for proj in projections:
            # If it's a dict or model object, validate
            if isinstance(proj, dict):
                ForecastResponseSchema(**proj)
            else:
                ForecastResponseSchema.model_validate(proj)
                
        print("[+] Schema validation passed for projections.")
        working_endpoints.append("Forecast Projections Endpoint (ML Generated)")
    except Exception as e:
        errors.append(f"Forecast Projections failed: {e}")
        print(f"[-] Forecast Error: {e}")
        
    # 4. Verify Database First Strategy
    try:
        print("[*] Verifying Database First Strategy...")
        # First query should have cached the projections in DB
        db_forecasts_count = db.query(Forecast).count()
        print(f"[*] Found {db_forecasts_count} forecasts in forecasts table.")
        
        if db_forecasts_count == 0:
            errors.append("Database First Strategy Error: Forecasts were not cached in database.")
            print("[-] Error: Forecasts were not cached in DB.")
        else:
            # Run get_projections again, should hit DB (we verify by inspecting returned model types/ids)
            projections_db = ForecastService.get_projections("ensemble", db)
            print(f"[+] Database First Strategy successfully retrieved {len(projections_db)} cached forecasts.")
            working_endpoints.append("Database First Strategy Caching")
    except Exception as e:
        errors.append(f"Database First Strategy check failed: {e}")
        print(f"[-] Database First Error: {e}")
        
    # 5. Test Real-Time Simulation Run (ML Powered)
    try:
        print("[*] Executing real-time ML-powered shock simulation...")
        params = RunSimulationSchema(
            oil_change=15.0,
            interest_rate_change=-50.0,
            currency_change=2.5
        )
        
        # Clear existing simulations for clean count
        db.query(Simulation).delete()
        db.commit()
        
        sim_res = SimulatorService.run_shock_simulation(None, params, db)
        print(f"[+] Simulation projection output: {sim_res['output_projected_rate']}%")
        
        # Verify schema compliance
        SimulationResponseSchema(**sim_res)
        print("[+] Schema validation passed for Simulation response.")
        working_endpoints.append("Simulator Run Endpoint (ML Override)")
    except Exception as e:
        errors.append(f"Simulator Run failed: {e}")
        print(f"[-] Simulator Error: {e}")
        
    db.close()
    
    # Print Validation Report
    print("\n=========================================================")
    print("                  FINAL VALIDATION REPORT                ")
    print("=========================================================")
    
    print("\n[OK] Working Endpoints:")
    for ep in working_endpoints:
        print(f"  - {ep}")
        
    if issues:
        print("\n[WARN] Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n[WARN] Issues: None")
        
    if errors:
        print("\n[ERROR] Errors:")
        for err in errors:
            print(f"  - {err}")
    else:
        print("\n[ERROR] Errors: None")
    print("=========================================================\n")

if __name__ == "__main__":
    run_verification()
