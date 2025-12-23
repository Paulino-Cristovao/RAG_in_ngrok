"""
Unit tests for the FastAPI application.

This module contains tests for the chat endpoint, verifying behavior
for both invalid inputs and successful interactions using mocked agents.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient


def test_chat_no_query(client: TestClient) -> None:
    """
    Test the /chat endpoint with missing query.

    Args:
        client (TestClient): The test client for the FastAPI app.

    Asserts:
        Response status code is 400.
        Response contains key "detail".
    """
    response = client.post("/chat", json={"query": ""})
    assert response.status_code == 400, (
        f"Expected 400, got {response.status_code}. Response: {response.text}"
    )
    assert "detail" in response.json()


def test_chat_success(
    client: TestClient, mock_agent_executor: MagicMock
) -> None:
    """
    Test the /chat endpoint with a valid query and mocked agent response.

    Args:
        client (TestClient): The test client for the FastAPI app.
        mock_agent_executor (MagicMock): The mocked agent executor.

    Asserts:
        Response status code is 200.
        Response contains correct "response" and "thread_id".
        Agent executor is invoked with correct arguments.
    """
    # Setup mock return value
    mock_response = {"messages": [MagicMock(content="Hello there!")]}
    mock_agent_executor.invoke.return_value = mock_response

    response = client.post("/chat", json={"query": "Hello"})

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Hello there!"
    assert data["thread_id"] == "default_thread"  # Default thread_id check

    # Verify invoke was called correctly
    mock_agent_executor.invoke.assert_called_once()
    # Pylint generally dislikes unpacking call_args directly or assumes
    # it might be None, but strictly speaking for MagicMock it is generally
    # fine in tests. However, to be extra safe and explicitly clear:
    args, kwargs = mock_agent_executor.invoke.call_args
    assert args[0] == {"messages": [("user", "Hello")]}
    assert kwargs["config"] == {
        "configurable": {"thread_id": "default_thread"}
    }
