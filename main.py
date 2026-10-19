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
    if os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY"):
        return

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from helper import get_openai_api_key

    os.environ["OPENAI_API_KEY"] = get_openai_api_key()


def build_chat_model(model_name: str = MODEL):
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
    """Kill any process currently listening on *port*."""
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
    agent.graph = build_graph(model_name=model_name)
    return agent.graph


def start_backend(
    host: str = HOST, port: int = PORT, log_level: str = "warning"
) -> str:
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
    load_graph()
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
