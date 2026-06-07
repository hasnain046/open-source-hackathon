# Module: tests.test_endpoints
# Description: Automated test cases verifying global router connection states and root check endpoints.

from fastapi.testclient import TestClient


def test_read_root_service(client: TestClient):
    """Verify application home route returns online status details."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Operational"
