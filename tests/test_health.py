"""
DocPilot — Health Endpoint Tests

Smoke tests for the /health endpoint.
Run with: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient

from app.backend.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """Health endpoint should return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client: TestClient) -> None:
        """Health response should contain status=healthy."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_returns_version(self, client: TestClient) -> None:
        """Health response should contain a version string."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert isinstance(data["version"], str)

    def test_health_returns_service_name(self, client: TestClient) -> None:
        """Health response should contain the service name."""
        response = client.get("/health")
        data = response.json()
        assert data["service"] == "DocPilot"


class TestRootEndpoint:
    """Tests for GET /."""

    def test_root_returns_200(self, client: TestClient) -> None:
        """Root endpoint should return HTTP 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_welcome_message(self, client: TestClient) -> None:
        """Root response should contain a welcome message."""
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "DocPilot" in data["message"]


class TestUploadEndpoint:
    """Tests for POST /upload."""

    def test_upload_rejects_non_pdf(self, client: TestClient) -> None:
        """Upload should reject non-PDF files with 400."""
        response = client.post(
            "/upload",
            files={"file": ("test.txt", b"hello world", "text/plain")},
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_upload_accepts_pdf(self, client: TestClient) -> None:
        """Upload should accept a valid PDF file."""
        # Minimal valid PDF content
        pdf_content = b"%PDF-1.4 fake content for testing"
        response = client.post(
            "/upload",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.pdf"
        assert data["status"] == "uploaded"

    def test_upload_returns_file_size(self, client: TestClient) -> None:
        """Upload response should include file size."""
        pdf_content = b"%PDF-1.4 test content"
        response = client.post(
            "/upload",
            files={"file": ("size_test.pdf", pdf_content, "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "size_bytes" in data
        assert int(data["size_bytes"]) == len(pdf_content)
