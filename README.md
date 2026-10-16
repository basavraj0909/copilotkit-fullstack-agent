# CopilotKit Fullstack Agent

An enterprise agentic application featuring a React UI powered by **CopilotKit**, a multi-agent API Gateway, and backend agent servers built with **LangGraph** (OpenAI) and **Google ADK** (Gemini).

---

## 🏗️ Architecture

```
React (Port 3002) ──► CopilotKit Runtime (Port 4002) ──► FastAPI Agent (Port 8002 / 8009) ──► LLM
```

- **Frontend**: React 19 + Vite + TailwindCSS (`frontend/`)
- **Agent Gateway**: Node.js + Hono + `@copilotkit/runtime` (`frontend/server.ts`)
- **LangGraph Agent**: Python + FastAPI + LangChain (`main.py` on `:8002`)
- **Google ADK Agent**: Python + FastAPI + Google GenAI (`adk_server.py` on `:8009`)

Detailed architecture documentation is available in [ARCHITECTURE_AND_DEBUGGING_GUIDE.md](ARCHITECTURE_AND_DEBUGGING_GUIDE.md).

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.12 (Python 3.10–3.12 required for `copilotkit`)
- Node.js 20+

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/basavraj0909/copilotkit-fullstack-agent.git
cd copilotkit-fullstack-agent

# Create Python virtual environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..

# Setup API Keys
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and/or GOOGLE_API_KEY
```

### 3. Run the Application

#### Terminal 1: Backend Agent
```bash
source venv/bin/activate

# For Google Gemini agent:
python adk_server.py

# OR for OpenAI LangGraph agent:
# python main.py
```

#### Terminal 2: Frontend & Runtime
```bash
cd frontend
npm run dev -- --port 3002
```

Visit **http://localhost:3002** in your browser.

---

## 🛠️ Switching Between Agents

In `frontend/src/App.tsx`:
- For **Gemini**: `export const agentId = "gemini";` (runs on `:8009`)
- For **OpenAI**: `export const agentId = "default";` (runs on `:8002`)
