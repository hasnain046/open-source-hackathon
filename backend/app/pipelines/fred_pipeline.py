# Module: app.pipelines.fred_pipeline
# Description: ETL pipeline subclass fetching Federal Reserve Economic Data.

from app.pipelines.base_pipeline import BasePipeline


class FredPipeline(BasePipeline):
    def extract(self):
        """Query FRED economic indicators feeds."""
        pass

    def transform(self, raw_data):
        """Structure raw rate numbers."""
        pass

    def load(self, cleaned_data):
        """Save rates records to PostgreSQL databases."""
        pass
