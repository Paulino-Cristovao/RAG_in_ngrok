# OpenAI LangChain Chat Agent with DuckDuckGo Search & Memory

A powerful conversational AI agent built with **Python**, **Flask**, **LangChain**, and **OpenAI**. This agent enables real-time information retrieval using **DuckDuckGo Search** and maintains conversation context with **memory persistence**.

## Features

- **Real-Time Web Search**: Retrieves up-to-date information from the web using DuckDuckGo.
- **Conversation Memory**: Remembers the last 10 interactions to maintain context.
- **REST API**: Exposes a simple `/chat` endpoint for integration.
- **Dockerized**: specific `Dockerfile` for easy container deployment.
- **Public Exposure**: Includes scripts to expose the local server via **Ngrok**.
- **Infrastructure as Code**: Includes **Terraform** configuration for AWS deployment.
- **CI/CD**: GitHub Actions workflow for automated testing.

## Prerequisites

- Python 3.10+
- OpenAI API Key
- Ngrok Account (optional, for public access)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Paulino-Cristovao/RAG_in_ngrok.git
   cd RAG_in_ngrok
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Update the `.env` file with your OpenAI API Key:
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   ```

## Usage

### Running Locally

Start the Flask application:
```bash
python app.py
```
The server will start at `http://0.0.0.0:5000`.

### Chat API

You can interact with the agent using `curl` or Postman.

**Stateless Request:**
```bash
curl -X POST http://localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the latest version of LangChain?"}'
```

**Stateful Request (with Memory):**
Provide a `thread_id` to maintain conversation history.
```bash
# First question
curl -X POST http://localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "My name is Alice", "thread_id": "user-session-1"}'

# Follow-up question (Agent remembers name)
curl -X POST http://localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is my name?", "thread_id": "user-session-1"}'
```

### Exposing with Ngrok

To allow external access to your local server:
1. Ensure `app.py` is running.
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
docker run -p 5000:5000 --env-file .env chat-agent
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
