# Module: tests.conftest
# Description: Shared Pytest configuration and diagnostic client fixtures.

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Provide module scope TestClient instance."""
    with TestClient(app) as c:
        yield c
