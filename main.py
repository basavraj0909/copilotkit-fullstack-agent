"""
🎙️ Stop 3: The Brain — LangGraph & Groq Backend

This is the primary Python backend server running on Port 8002.
It uses LangGraph to manage stateful multi-turn agent conversations and
streams responses using the AG-UI (Server-Sent Events) protocol.

Key Architectural Components:
1. Model Connector (build_chat_model):
   - Dynamically loads GROQ_API_KEY or OPENAI_API_KEY from .env.
   - Routes through Groq's high-speed API (openai/gpt-oss-120b) by default.

2. Agent Graph with Memory (build_graph):
   - MemorySaver(): Persists conversation state across multiple turns using thread IDs.
   - CopilotKitMiddleware(): Bridges LangGraph events into CopilotKit frontend tools.

3. AG-UI FastAPI Endpoint:
   - Exposes an SSE stream on "/" that emits token chunks, tool execution events,
     and run completion events directly to the gateway.
"""

from __future__ import annotations

import os
import subprocess as _sp
import sys
import threading
import time
import warnings
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Ensure .env overrides any environment variables cached in the shell session
load_dotenv(override=True)

warnings.filterwarnings("ignore")

import uvicorn
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import CopilotKitMiddleware, LangGraphAGUIAgent
from fastapi import FastAPI
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

HOST = "0.0.0.0"
PORT = 8002
MODEL = "gpt-4.1"


def _ensure_openai_api_key() -> None:
    """Ensure at least one valid LLM API key is present."""
    if os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY"):
        return

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from helper import get_openai_api_key

    os.environ["OPENAI_API_KEY"] = get_openai_api_key()


def build_chat_model(model_name: str = MODEL):
    """
    1. The Model Connector
    Inspects .env to configure either Groq or OpenAI:
    - If GROQ_API_KEY is present: Connects to Groq's high-speed OpenAI-compatible
      endpoint (https://api.groq.com/openai/v1) using 'openai/gpt-oss-120b'.
    - Otherwise: Falls back to standard OpenAI ChatOpenAI.
    """
    load_dotenv(override=True)
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        groq_model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
        masked = groq_key[:8] + "..." + groq_key[-4:]
        print(f"✓ Active API Key in use: GROQ_API_KEY ({masked}) with model '{groq_model}'")
        return ChatOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_key,
            model=groq_model,
        )

    _ensure_openai_api_key()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    masked = (api_key[:8] + "..." + api_key[-4:]) if api_key else "None"
    print(f"✓ Active API Key in use: OPENAI_API_KEY ({masked}) with model '{model_name}'")
    return ChatOpenAI(model=model_name, api_key=api_key if api_key else None)


def build_graph(model_name: str = MODEL):
    """
    2. The Agent Graph with Memory Builds the core LangGraph workflow:
    - MemorySaver():          Saves conversation history per thread_id so the agent remembers past turns.
    - CopilotKitMiddleware(): Enables Generative UI (e.g., rendering charts/cards on the client).
    - system_prompt: Instructs the agent on role and available UI components.
    """
    chat_model = build_chat_model(model_name=model_name)
    return create_agent(
        model=chat_model,
        tools=[],
        middleware=[CopilotKitMiddleware()],
        checkpointer=MemorySaver(),
        system_prompt=(
            "You are a helpful assistant for a demo app with a few available UI tools. "
            "Prefer using a matching frontend tool when it would present the answer clearly. "
            "For chart requests, use concise made-up demo data when the user does not provide data. "
            "Use pieChart for category distributions "
            "and flightCard for a single flight summary when relevant. "
            "Tool arguments must match the provided schema exactly."
        ),
    )


# 3. FastAPI AG-UI Endpoint
# Wraps the LangGraph workflow in an AG-UI compatible Server-Sent Events (SSE) server
# Exposes an AG-UI SSE (Server-Sent Events) endpoint at http://localhost:8002/.
# When called, it streams events like TEXT_MESSAGE_START, TEXT_MESSAGE_CONTENT, and TEXT_MESSAGE_END.
"""
What are name and description actually used for?

In the AG-UI and CopilotKit protocol:

name: A unique identifier for the agent. 
      It appears in the agent discovery endpoint (http://localhost:4002/api/copilotkit/info).
description: Explains the agent's purpose. 
             In multi-agent architectures (where an orchestrator routes questions to specialized agents), the orchestrator reads this description to decide which agent should answer the user's prompt.
"""
app = FastAPI()
graph = build_graph()
agent = LangGraphAGUIAgent(
    name="lesson2_agent",
    description="Lesson 2 chart agent",
    graph=graph,
)
add_langgraph_fastapi_endpoint(app=app, agent=agent, path="/")

_server_started = False
_server_lock = threading.Lock()


def _kill_port(port: int) -> None:
    """Kill any process currently listening on *port* (cross-platform for Windows, macOS, Linux)."""
    if sys.platform == "win32":
        try:
            # Query active TCP connections on Windows and kill listening PID
            out = _sp.run(
                ["netstat", "-ano"], capture_output=True, text=True, check=False
            ).stdout
            for line in out.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.strip().split()
                    pid = parts[-1]
                    if pid and pid != "0":
                        print(
                            f"⚠ Found existing process (PID {pid}) on port {port} — killing it"
                        )
                        _sp.run(["taskkill", "/F", "/PID", pid], capture_output=True, check=False)
            time.sleep(0.5)
        except Exception:
            pass
    else:
        try:
            result = _sp.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
            for pid in result.stdout.strip().split():
                if pid:
                    print(
                        f"⚠ Found existing process (PID {pid}) on port {port} — killing it"
                    )
                    os.kill(int(pid), 9)
            if result.stdout.strip():
                time.sleep(0.5)
        except Exception:
            pass


def load_graph(model_name: str = MODEL):
    """Rebuild and reload the graph with the specified model."""
    agent.graph = build_graph(model_name=model_name)
    return agent.graph


def start_backend(
    host: str = HOST, port: int = PORT, log_level: str = "warning"
) -> str:
    """Helper used in notebooks to start uvicorn in a background thread."""
    global _server_started

    with _server_lock:
        if not _server_started:
            _kill_port(port)
            threading.Thread(
                target=lambda: uvicorn.run(
                    app, host=host, port=port, log_level=log_level
                ),
                daemon=True,
            ).start()
            _server_started = True

    return f"http://localhost:{port}"


def main() -> None:
    """Entry point when running 'python main.py' from terminal."""
    load_graph()
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
