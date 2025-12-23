FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install flask langchain langchain-openai python-dotenv duckduckgo-search langchain-community

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
