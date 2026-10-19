/**
 * 🎙️ Stop 2: The Gateway — The Traffic Controller
 *
 * This Node.js + Hono server acts as the API Gateway between the React UI
 * and the various Python backend agents.
 *
 * The Problem It Solves:
 * Instead of the browser directly hardcoding connection logic, WebSocket/SSE
 * handling, and auth for multiple disparate Python servers, this gateway provides
 * a unified entry point (/api/copilotkit) on Port 4002.
 *
 * How Routing Works:
 * - When React sends a request with agentId = "default", it routes to LangGraph (port 8002).
 * - When React sends a request with agentId = "gemini", it routes to Google ADK (port 8009).
 */

import { CopilotRuntime, createCopilotEndpoint } from "@copilotkit/runtime/v2";
import { HttpAgent } from "@ag-ui/client";
import { LangGraphHttpAgent } from "@copilotkit/runtime/langgraph";
import { serve } from "@hono/node-server";

// 1. Define agent remote endpoints
const langGraphAgent = new LangGraphHttpAgent({
  url: process.env.LANGGRAPH_DEPLOYMENT_URL || "http://127.0.0.1:8002",
});

const adkAgent = new HttpAgent({
  url: process.env.ADK_AGENT_URL || "http://127.0.0.1:8009",
});

// 2. Register agents in the CopilotRuntime registry
const runtime = new CopilotRuntime({
  agents: {
    default: langGraphAgent, // Used when agentId="default" or omitted
    gemini: adkAgent,        // Used when agentId="gemini"
  },
});

// 3. Expose the /api/copilotkit endpoint on port 4002
const app = createCopilotEndpoint({
  runtime,
  basePath: "/api/copilotkit",
});

serve({ fetch: app.fetch, port: 4002 }, () => {
  console.log("CopilotKit API server running at http://localhost:4002");
});
