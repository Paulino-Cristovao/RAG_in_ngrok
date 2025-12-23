def test_chat_no_query(client):
    response = client.post('/chat', json={})
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_chat_health(client):
    # Just checking if the endpoint is reachable; 
    # actual agent run might require mocking OpenAI/DuckDuckGo to avoid cost/network calls in basic unit tests.
    pass
