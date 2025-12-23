"""
LangChain Chat Agent.

This module initializes a FastAPI application that serves a RAG-enabled
chat agent using OpenAI and Tavily search tools. It utilizes
LangGraph for state management and memory persistence.
"""

from typing import Any, cast

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="LangChain Chat Agent",
    description="A RAG-enabled chat agent using OpenAI and Tavily",
    version="1.0.0",
)

# Initialize Templates
templates = Jinja2Templates(directory="templates")

# Initialize OpenAI Chat Model
# ChatOpenAI automatically reads OPENAI_API_KEY from environment variables.
llm = ChatOpenAI(temperature=0.7)

# Tools
tavily_search = TavilySearchResults(
    max_results=8,                  # More context
    search_depth="advanced",        # Better for news/sports/finance
    include_answer=True,            # Direct summarized answer
    include_raw_content=False
)

tools: list[BaseTool] = [tavily_search]

# Initialize Memory
checkpointer = MemorySaver()

# Initialize LangGraph Agent with Checkpointer
# Return type of create_react_agent is CompiledGraph, but importing it
# can be flaky with stubs. We allow type inference or Any if strict.
agent_executor: Any = create_react_agent(
    llm, tools, checkpointer=checkpointer
)


class ChatRequest(BaseModel):
    """
    Request model for the chat endpoint.

    Attributes:
        query: The user's input message.
        thread_id: A unique identifier for the conversation thread.
    """

    query: str = Field(..., description="The user's input query.")
    thread_id: str = Field(
        "default_thread", description="Unique ID for the conversation thread."
    )


class ChatResponse(BaseModel):
    """
    Response model for the chat endpoint.

    Attributes:
        response: The AI's response message.
        thread_id: The conversation thread ID.
    """

    response: str = Field(..., description="The AI's response.")
    thread_id: str = Field(..., description="The conversation thread ID.")


@app.get("/")
async def health_check(request: Request):
    """
    Serve the chat interface.

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: The rendered HTML page.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat request using the LangGraph agent.

    Args:
        request (ChatRequest): The input request containing query and thread_id.

    Returns:
        ChatResponse: The agent's response.

    Raises:
        HTTPException: If query is missing or processing fails.
    """
    try:
        # Basic preprocessing
        query = request.query.strip()

        if not query:
            raise HTTPException(status_code=400, detail="No query provided")

        # Run agent with config for memory
        # Explicit type cast for mypy strictness
        config = cast(
            RunnableConfig,
            {"configurable": {"thread_id": request.thread_id}},
        )

        # Invoke agent
        response: dict[str, Any] = agent_executor.invoke(
            {"messages": [("user", query)]}, config=config
        )

        # The agent state contains the full message history.
        # We want to return the last message (AI response).
        last_message = response["messages"][-1]

        return ChatResponse(
            response=str(last_message.content),
            thread_id=request.thread_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
