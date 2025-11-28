"""Pytest configuration and fixtures for the Mergington High School API tests."""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)
