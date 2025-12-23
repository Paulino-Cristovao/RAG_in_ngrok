# OpenAI LangChain Chat Agent with DuckDuckGo Search & Memory

A powerful conversational AI agent built with **Python**, **Flask**, **LangChain**, and **OpenAI**. This agent enables real-time information retrieval using **DuckDuckGo Search** and maintains conversation context with **memory persistence**.
# LangChain Chat Agent

A simple, powerful chat agent built with **FastAPI**, **LangChain**, and **OpenAI**. It features a modern web interface and can be easily shared via **Ngrok**.

## Features

- **Interactive Web Interface**: Beautiful, dark-themed chat UI.
- **RAG + Search**: Integrated DuckDuckGo search for real-time information.
- **Memory**: Remembers conversation context using LangGraph.
- **Easy Sharing**: Includes scripts to expose your local app to the internet via Ngrok.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd RAG_in_ngrok
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Setup**:
    Create a `.env` file in the root directory and add your OpenAI API Key:
    ```bash
    OPENAI_API_KEY=sk-...
    ```

## How to Run

### Option 1: Run Locally
Use this if you just want to test on your own computer.

1.  Start the application:
    ```bash
    python main.py
    ```
2.  Open your browser to: **[http://localhost:5001](http://localhost:5001)**

### Option 2: Share with Ngrok
Use this to let others use your agent over the internet.

1.  **Open Terminal 1** (Start the App):
    ```bash
    python main.py
    ```
    *Keep this running!*

2.  **Open Terminal 2** (Start the Tunnel):
    ```bash
    ./start_ngrok.sh
    ```
3.  Copy the `Forwarding` URL (e.g., `https://xyz.ngrok-free.app`) and share it!

## Running Tests

To verify everything is working correctly:

```bash
pytest
```

### Chat API

You can interact with the agent using `curl` or Postman.

**Stateless Request:**
```bash
curl -X POST http://localhost:5001/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the latest version of LangChain?"}'
```

**Stateful Request (with Memory):**
Provide a `thread_id` to maintain conversation history.
```bash
# First question
curl -X POST http://localhost:5001/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "My name is Alice", "thread_id": "user-session-1"}'

# Follow-up question (Agent remembers name)
curl -X POST http://localhost:5001/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is my name?", "thread_id": "user-session-1"}'
```

### Exposing with Ngrok

To allow external access to your local server:
1. Ensure `main.py` is running.
2. Run the helper script:
   ```bash
   ./start_ngrok.sh
   ```
   Use the generated URL (e.g., `https://xxxx.ngrok-free.app`) to send requests.

## Testing

Run the automated tests using `pytest`:
```bash
pytest
```

## Deployment

### Docker
Build and run the container:
```bash
docker build -t chat-agent .
docker run -p 5001:5001 --env-file .env chat-agent
```

### Infrastructure (Terraform)
Deploy to AWS using the configurations in `terraform/`:
```bash
cd terraform
terraform init
terraform apply
```

## License
MIT
