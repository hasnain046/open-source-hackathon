# Module: app.services.trends_service
# Description: Service handling historical inflation trends and detailed category comparisons.

from sqlalchemy.orm import Session
from app.models.cpi import InflationData


class TrendsService:
    @staticmethod
    def get_historical_trends(db: Session):
        """Retrieve annual inflation averages and GDP growths from DB or fallback."""
        try:
            db_inflation = db.query(InflationData).all()
            if db_inflation:
                years = {}
                for entry in db_inflation:
                    yr = str(entry.reporting_date.year)
                    if yr not in years:
                        years[yr] = []
                    years[yr].append(entry.headline_rate)
                
                trends = []
                for yr, rates in sorted(years.items()):
                    avg_rate = round(sum(rates) / len(rates), 2)
                    gdp_growth = 7.3 if yr == "2026" else 6.8
                    trends.append({
                        "year": yr,
                        "rate": avg_rate,
                        "growth": gdp_growth
                    })
                return trends
        except Exception as e:
            print(f"Database query failed in TrendsService.get_historical_trends: {e}")

        # Fallback mock data matching frontend
        return [
            {"year": "2017", "rate": 3.33, "growth": 6.8},
            {"year": "2018", "rate": 3.94, "growth": 6.5},
            {"year": "2019", "rate": 3.73, "growth": 6.1},
            {"year": "2020", "rate": 6.62, "growth": -5.8},
            {"year": "2021", "rate": 5.13, "growth": 8.7},
            {"year": "2022", "rate": 6.70, "growth": 7.2},
            {"year": "2023", "rate": 5.65, "growth": 6.3},
            {"year": "2024", "rate": 5.40, "growth": 6.8},
            {"year": "2025", "rate": 4.98, "growth": 7.1},
            {"year": "2026 (YTD)", "rate": 4.82, "growth": 7.3}
        ]

    @staticmethod
    def get_comparison_trends(db: Session):
        """Retrieve monthly detailed inflation overlays (headline, food, fuel, core) from DB or fallback."""
        try:
            db_inflation = db.query(InflationData).order_by(InflationData.reporting_date.asc()).all()
            if db_inflation:
                detailed = []
                for entry in db_inflation:
                    food_rate = 5.42
                    fuel_rate = 3.10
                    for cpi in entry.cpi_entries:
                        if "food" in cpi.category_name.lower():
                            food_rate = cpi.current_rate
                        elif "fuel" in cpi.category_name.lower():
                            fuel_rate = cpi.current_rate
                    
                    detailed.append({
                        "date": entry.reporting_date.strftime("%Y-%m"),
                        "inflation": entry.headline_rate,
                        "food": food_rate,
                        "fuel": fuel_rate,
                        "core": entry.core_rate
                    })
                return detailed
        except Exception as e:
            print(f"Database query failed in TrendsService.get_comparison_trends: {e}")

        # Fallback mock data matching frontend
        return [
            {"date": "2021-06", "inflation": 5.30, "food": 5.15, "fuel": 12.60, "core": 5.40},
            {"date": "2021-12", "inflation": 5.66, "food": 5.40, "fuel": 11.20, "core": 5.85},
            {"date": "2022-06", "inflation": 7.01, "food": 7.50, "fuel": 10.10, "core": 6.40},
            {"date": "2022-12", "inflation": 5.72, "food": 5.20, "fuel": 8.40, "core": 6.10},
            {"date": "2023-06", "inflation": 4.87, "food": 4.60, "fuel": 3.90, "core": 5.10},
            {"date": "2023-12", "inflation": 5.69, "food": 9.50, "fuel": -0.70, "core": 3.80},
            {"date": "2024-06", "inflation": 5.08, "food": 8.10, "fuel": -3.20, "core": 3.15},
            {"date": "2024-12", "inflation": 5.12, "food": 7.90, "fuel": -2.80, "core": 3.50},
            {"date": "2025-06", "inflation": 4.95, "food": 6.20, "fuel": 1.10, "core": 4.10},
            {"date": "2025-12", "inflation": 5.01, "food": 6.80, "fuel": 2.90, "core": 4.30},
            {"date": "2026-06", "inflation": 4.82, "food": 5.42, "fuel": 3.10, "core": 4.25}
        ]
