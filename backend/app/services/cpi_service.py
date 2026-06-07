# Module: app.services.cpi_service
# Description: Service handling retrieval of CPI category weights and itemized breakdowns.

import uuid
from sqlalchemy.orm import Session
from app.models.cpi import CPIData, InflationData


class CPIService:
    @staticmethod
    def get_mock_categories():
        """Get realistic mock categories matching frontend requirements."""
        food_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
        housing_id = uuid.UUID("22222222-2222-2222-2222-222222222222")
        fuel_id = uuid.UUID("33333333-3333-3333-3333-333333333333")
        clothing_id = uuid.UUID("44444444-4444-4444-4444-444444444444")
        misc_id = uuid.UUID("55555555-5555-5555-5555-555555555555")
        inflation_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

        return [
            {
                "id": food_id,
                "inflation_id": inflation_id,
                "category_name": "Food & Beverages",
                "weight": 45.86,
                "current_rate": 5.42,
                "sub_items": [
                    {"name": "Cereals", "rate": 6.20, "weight": 9.67},
                    {"name": "Vegetables", "rate": 8.50, "weight": 6.04},
                    {"name": "Pulses", "rate": 7.10, "weight": 2.38},
                    {"name": "Milk & Products", "rate": 4.80, "weight": 6.25}
                ]
            },
            {
                "id": housing_id,
                "inflation_id": inflation_id,
                "category_name": "Housing",
                "weight": 10.07,
                "current_rate": 4.10,
                "sub_items": [
                    {"name": "Urban Rent", "rate": 4.25, "weight": 8.50},
                    {"name": "Maintenance", "rate": 3.80, "weight": 1.57}
                ]
            },
            {
                "id": fuel_id,
                "inflation_id": inflation_id,
                "category_name": "Fuel & Light",
                "weight": 6.84,
                "current_rate": 3.10,
                "sub_items": [
                    {"name": "LPG Gas", "rate": 2.50, "weight": 3.20},
                    {"name": "Electricity", "rate": 3.90, "weight": 2.80},
                    {"name": "Kerosene", "rate": 2.10, "weight": 0.84}
                ]
            },
            {
                "id": clothing_id,
                "inflation_id": inflation_id,
                "category_name": "Clothing & Footwear",
                "weight": 6.53,
                "current_rate": 5.12,
                "sub_items": [
                    {"name": "Clothing", "rate": 5.25, "weight": 5.40},
                    {"name": "Footwear", "rate": 4.50, "weight": 1.13}
                ]
            },
            {
                "id": misc_id,
                "inflation_id": inflation_id,
                "category_name": "Miscellaneous / Services",
                "weight": 28.32,
                "current_rate": 4.25,
                "sub_items": [
                    {"name": "Transport & Comm.", "rate": 3.90, "weight": 8.59},
                    {"name": "Education", "rate": 5.10, "weight": 4.46},
                    {"name": "Health & Care", "rate": 6.15, "weight": 5.89},
                    {"name": "Personal Care", "rate": 4.05, "weight": 9.38}
                ]
            }
        ]

    @staticmethod
    def get_categories(db: Session):
        """Query DB first. If empty or throws, return mock data."""
        try:
            categories = db.query(CPIData).all()
            if categories:
                return categories
        except Exception as e:
            print(f"Database query failed in CPIService.get_categories: {e}")
        return CPIService.get_mock_categories()

    @staticmethod
    def get_subcategory(category_id: str, db: Session):
        """Find subcategory details by UUID or string match."""
        try:
            try:
                cat_uuid = uuid.UUID(category_id)
                db_cat = db.query(CPIData).filter(CPIData.id == cat_uuid).first()
                if db_cat:
                    return db_cat.sub_items or []
            except (ValueError, TypeError):
                db_cat = db.query(CPIData).filter(CPIData.category_name.ilike(category_id)).first()
                if db_cat:
                    return db_cat.sub_items or []
        except Exception as e:
            print(f"Database query failed in CPIService.get_subcategory: {e}")

        # Fallback to mock data
        mock_cats = CPIService.get_mock_categories()
        for cat in mock_cats:
            if str(cat["id"]) == category_id or cat["category_name"].lower() == category_id.lower():
                return cat["sub_items"]
        
        return mock_cats[0]["sub_items"]
