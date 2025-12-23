from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
import os

# Set dummy API key to pass Tavily validation during import
os.environ["TAVILY_API_KEY"] = "test-key"
os.environ["OPENAI_API_KEY"] = "test-key"

from main import app

@pytest.fixture
def client():
    """Fixture that creates a FastAPI TestClient for the application."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_agent_executor():
    """Fixture that mocks the agent_executor to prevent actual execution during tests."""
    with patch("main.agent_executor") as mock:
        yield mock
