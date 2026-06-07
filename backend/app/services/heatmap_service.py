# Module: app.services.heatmap_service
# Description: Service handling regional state-wise inflation heatmap rates retrieval.

import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.heatmap import HeatmapData


class HeatmapService:
    @staticmethod
    def get_mock_states():
        """Get realistic mock state inflation records matching frontend configuration."""
        updated = datetime(2026, 6, 1)
        mock_data = [
            {"state_name": "Maharashtra", "region": "West", "current_rate": 4.88, "year_ago_rate": 5.20, "threat_level": "Medium"},
            {"state_name": "Tamil Nadu", "region": "South", "current_rate": 5.25, "year_ago_rate": 5.80, "threat_level": "High"},
            {"state_name": "Uttar Pradesh", "region": "North", "current_rate": 4.60, "year_ago_rate": 5.01, "threat_level": "Medium"},
            {"state_name": "Karnataka", "region": "South", "current_rate": 4.90, "year_ago_rate": 5.30, "threat_level": "Medium"},
            {"state_name": "Gujarat", "region": "West", "current_rate": 4.10, "year_ago_rate": 4.70, "threat_level": "Low"},
            {"state_name": "West Bengal", "region": "East", "current_rate": 5.42, "year_ago_rate": 6.10, "threat_level": "High"},
            {"state_name": "Rajasthan", "region": "North", "current_rate": 5.10, "year_ago_rate": 5.50, "threat_level": "High"},
            {"state_name": "Madhya Pradesh", "region": "Central", "current_rate": 4.52, "year_ago_rate": 4.80, "threat_level": "Low"},
            {"state_name": "Kerala", "region": "South", "current_rate": 4.05, "year_ago_rate": 4.60, "threat_level": "Low"},
            {"state_name": "Bihar", "region": "East", "current_rate": 5.30, "year_ago_rate": 6.02, "threat_level": "High"},
            {"state_name": "Punjab", "region": "North", "current_rate": 4.75, "year_ago_rate": 5.15, "threat_level": "Medium"}
        ]
        
        records = []
        for idx, item in enumerate(mock_data):
            state_uuid = uuid.UUID(int=idx + 1000)
            records.append({
                "id": state_uuid,
                "state_name": item["state_name"],
                "region": item["region"],
                "current_rate": item["current_rate"],
                "year_ago_rate": item["year_ago_rate"],
                "threat_level": item["threat_level"],
                "updated_at": updated
            })
        return records

    @staticmethod
    def get_state_metrics(db: Session):
        """Query DB first. If empty, return mock state rates."""
        try:
            states = db.query(HeatmapData).all()
            if states:
                return states
        except Exception as e:
            print(f"Database query failed in HeatmapService.get_state_metrics: {e}")
        return HeatmapService.get_mock_states()
