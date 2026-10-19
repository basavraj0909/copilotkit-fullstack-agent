# CopilotKit Fullstack Agent

An enterprise agentic application featuring a React UI powered by **CopilotKit**, a multi-agent API Gateway, and backend agent servers built with **LangGraph** (Groq / OpenAI) and **Google ADK** (Gemini).

---

## 🏗️ Architecture

```text
React (:3002) ──► CopilotKit Runtime (:4002) ──► FastAPI Agent (:8002 / :8009) ──► LLM (Groq / OpenAI / Gemini)
```

### Port Mapping & Services

| Port | Service | Tech Stack | Entry Point | Description |
| :--- | :--- | :--- | :--- | :--- |
| **3002** | Frontend Web App | React 19, Vite, TailwindCSS | `frontend/src/App.tsx` | Chat UI with Generative UI support |
| **4002** | Agent Gateway | Node.js, Hono, `@copilotkit/runtime` | `frontend/server.ts` | Multi-agent router & protocol bridge |
| **8002** | LangGraph Agent | Python 3.12, FastAPI, LangGraph | `main.py` | Groq / OpenAI agent with session memory |
| **8009** | Google ADK Agent | Python 3.12, FastAPI, Google GenAI | `adk_server.py` | Gemini agent with in-memory state |

Detailed architectural flow and debugging instructions are available in [ARCHITECTURE_AND_DEBUGGING_GUIDE.md](ARCHITECTURE_AND_DEBUGGING_GUIDE.md).

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- **Python**: 3.10 – 3.12 (Python 3.12 recommended)
- **Node.js**: 20+

### 2. Installation

```bash
# 1. Clone the repository
git clone https://github.com/basavraj0909/copilotkit-fullstack-agent.git
cd copilotkit-fullstack-agent

# 2. Setup Python virtual environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Setup Frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Configure API Keys

Copy the example environment file:
```bash
cp .env.example .env
```

Open `.env` and set your active key. For example, using **Groq** for high-speed inference:
```ini
# Active API Key (Groq)
GROQ_API_KEY=your_groq_api_key_here

# Optional: choose model (default: "openai/gpt-oss-120b")
# GROQ_MODEL=openai/gpt-oss-120b

# Unused / Inactive Keys (Keep commented out when not in use)
# OPENAI_API_KEY=your_openai_api_key_here
# GOOGLE_API_KEY=your_google_api_key_here
```

---

## 💻 Running the Application

To run the full stack, open **two separate terminal windows**:

### Terminal 1: Backend Agent Server
```bash
source venv/bin/activate

# Option A: Run LangGraph Agent (Groq / OpenAI) - Port 8002
python main.py

# Option B: Run Google Gemini Agent - Port 8009
# python adk_server.py
```

### Terminal 2: Frontend UI & CopilotKit Gateway
```bash
cd frontend
npm run dev -- --port 3002
```

This starts:
- **CopilotKit API Gateway** at `http://localhost:4002`
- **React Web App** at `http://localhost:3002`

👉 Open your browser at **[http://localhost:3002](http://localhost:3002)** to chat!

---

## 🛠️ Switching Between Agents

To switch the active agent in the frontend UI, open [`frontend/src/App.tsx`](frontend/src/App.tsx) and set `agentId`:

- **For Groq / OpenAI (`main.py` on `:8002`)**:
  ```tsx
  export const agentId = "default";
  ```
- **For Google Gemini (`adk_server.py` on `:8009`)**:
  ```tsx
  export const agentId = "gemini";
  ```

---

## 🧪 Testing

### 1. Automated Backend Test Suite
Run the built-in automated test suite to check health across all 3 tiers, response latency, and multi-turn session memory:
```bash
python test_agent.py
```

### 2. End-to-End (E2E) Browser Tests
Run automated Playwright tests simulating user interactions in the browser:
```bash
cd frontend
npm run test:e2e
```

---

## 🧰 Useful Commands

| Task | Command |
| :--- | :--- |
| **Run LangGraph backend** | `python main.py` |
| **Run Gemini backend** | `python adk_server.py` |
| **Run Frontend & Gateway** | `cd frontend && npm run dev -- --port 3002` |
| **Run test suite** | `python test_agent.py` |
| **Kill hanging processes on ports** | `lsof -ti :3002 -ti :4002 -ti :8002 -ti :8009 \| xargs kill -9` |
| **Check open ports** | `lsof -i :3002 -i :4002 -i :8002 -i :8009` |
