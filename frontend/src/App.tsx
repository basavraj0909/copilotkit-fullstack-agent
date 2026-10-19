/**
 * 🎙️ Stop 1: The User Interface — Where It All Begins
 *
 * This React component renders the complete chat experience using CopilotKit.
 *
 * Key Concepts:
 * - agentId: Tells the CopilotRuntime gateway which backend agent to route to.
 *   - "default" -> LangGraph Agent on port 8002 (Groq / OpenAI)
 *   - "gemini"  -> Google ADK Agent on port 8009 (Google Gemini)
 *
 * - <CopilotChat />: Out-of-the-box UI component that handles:
 *   - Chat bubbles and message history display
 *   - Auto-scrolling and live token streaming character-by-character
 *   - Generative UI component rendering
 */

import { CopilotChat } from "@copilotkit/react-core/v2";

// Choose active agent backend: "default" (LangGraph :8002) or "gemini" (ADK :8009)
export const agentId = "default";

export default function App() {
  return <CopilotChat agentId={agentId} />;
}
