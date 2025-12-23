from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Initialize OpenAI Chat Model
llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7)

# Tools
search_tool = DuckDuckGoSearchRun()
tools = [search_tool]

# Initialize Memory
checkpointer = MemorySaver()

# Initialize LangGraph Agent with Checkpointer
agent_executor = create_react_agent(llm, tools, checkpointer=checkpointer)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        query = data.get('query')
        # Allow client to provide a thread_id for conversation persistence
        thread_id = data.get('thread_id', 'default_thread')
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Basic preprocessing
        query = query.strip()
        
        # Run agent with config for memory
        config = {"configurable": {"thread_id": thread_id}}
        response = agent_executor.invoke({"messages": [("user", query)]}, config=config)
        
        # The agent state contains the full message history.
        # We want to return the last message (AI response).
        last_message = response["messages"][-1]
        
        return jsonify({
            "response": last_message.content,
            "thread_id": thread_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
