"""
LangChain Chat Agent.

This module initializes a FastAPI application that serves a RAG-enabled
chat agent using OpenAI and DuckDuckGo search tools. It utilizes
LangGraph for state management and memory persistence.
"""

from typing import Any, cast, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
import re
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.callbacks import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="LangChain Chat Agent",
    description="A RAG-enabled chat agent using OpenAI and DuckDuckGo",
    version="1.0.0",
)

# Initialize Templates
templates = Jinja2Templates(directory="templates")

# Initialize OpenAI Chat Model
# ChatOpenAI automatically reads OPENAI_API_KEY from environment variables.
llm = ChatOpenAI(temperature=0.7)

# Tools
search = DuckDuckGoSearchResults(max_results=6)


def enhance_query_with_recency(query: str) -> str:
    """Automatically add time filters for time-sensitive queries"""
    lower_query = query.lower()
    
    time_keywords = [
        "today", "now", "latest", "recent", "current", "news", "update",
        "happened", "happening", "score", "price", "weather", "stock"
    ]
    
    if any(k in lower_query for k in time_keywords):
        # Add site operators or time hints
        return f"{query} after:{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}"
    
    return query

class SearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Useful for searching the internet for real-time information."

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        print(f"\n[REAL-TIME SEARCH] Query: {query}")
        try:
            enhanced_query = enhance_query_with_recency(query)
            results = search.invoke({"query": enhanced_query})
            print(f"[FOUND] {len(results)} results\n")
            return self._format_results(results)
        except Exception as e:
            return f"Search failed: {str(e)}"

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        print(f"\n[REAL-TIME SEARCH] Query: {query}")
        try:
            enhanced_query = enhance_query_with_recency(query)
            # ainvoke also accepts dict input for DuckDuckGoSearchResults
            results = await search.ainvoke({"query": enhanced_query})
            print(f"[FOUND] {len(results)} results (async)\n")
            return self._format_results(results)
        except Exception as e:
            return f"Search failed: {str(e)}"

    def _format_results(self, results: str) -> str:
        """Parse and format search results cleanly"""
        if not results.strip():
            return "No results found."

        formatted = ["Latest web results:\n"]
        # DuckDuckGoSearchResults returns a list of results as a string in format:
        # [snippet] link [title], etc. dependent on the version, or [title](link) snippet
        # The user provided parser: [title]url[snippet]
        # Let's adapt based on standard output or user suggestion.
        # User suggestion:
        for i, result in enumerate(results.split("\n")[:6], 1):  # Limit to top 6
            if not result.strip():
                continue
            # Each result format: [title]url[snippet] ? 
            # Actually standard DDG output usually is: [snippet] (url), title is implicit or [title] (url) snippet.
            # But let's use the user's logic which splits by ']'
            try:
                parts = result.split("]", 2)
                if len(parts) < 3:
                    # Fallback if format is different
                    formatted.append(f"{i}. {result}\n")
                    continue
                title = parts[0][1:]  # Remove leading [
                url = parts[1]
                snippet = parts[2] if len(parts) > 2 else ""
                formatted.append(f"{i}. {title}\n   Link: {url}\n   {snippet.strip()}\n")
            except Exception:
                formatted.append(f"{i}. {result}\n")
        return "\n".join(formatted)

search_tool = SearchTool()
tools: list[BaseTool] = [search_tool]

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
