# Module: app.pipelines.bls_pipeline
# Description: ETL pipeline subclass fetching Bureau of Labor Statistics CPI indices.

from app.pipelines.base_pipeline import BasePipeline


class BlsPipeline(BasePipeline):
    def extract(self):
        """Query BLS API for consumer price index updates."""
        pass

    def transform(self, raw_data):
        """Structure raw category indexes and calculate weights."""
        pass

    def load(self, cleaned_data):
        """Save CPI category allocations to PostgreSQL databases."""
        pass
