# Module: app.pipelines.base_pipeline
# Description: Abstract base class defining common ETL routines for macro pipeline tasks.

from abc import ABC, abstractmethod


class BasePipeline(ABC):
    @abstractmethod
    def extract(self) -> Any:
        """Fetch raw indicators from target API feeds."""
        pass

    @abstractmethod
    def transform(self, raw_data: Any) -> Any:
        """Parse, validate, and structure macro indices."""
        pass

    @abstractmethod
    def load(self, cleaned_data: Any) -> bool:
        """Write structured data models to databases."""
        pass

    def run(self) -> bool:
        """Execute the ETL transaction cycle."""
        raw = self.extract()
        cleaned = self.transform(raw)
        return self.load(cleaned)
