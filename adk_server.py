import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from google.adk.agents import LlmAgent

# Load GOOGLE_API_KEY from .env
load_dotenv()

# Verify Google API key is set
if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
    print("⚠ Warning: GOOGLE_API_KEY is not set in your .env file!")

gemini_agent = LlmAgent(
    name="assistant",
    model="gemini-3.8-flash",
    instruction="Be helpful and fun!",  # instruction: The System Prompt sent to the LLM (Gemini) before any conversation begins:
)  # It defines the agent's persona, tone, and rules.
# It tells the model how to act and respond to every message.
# It is the exact equivalent of system_prompt in main.py

adk_agent = ADKAgent(
    adk_agent=gemini_agent,
    app_name="demo_app",
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,  # state management
)

app_adk = FastAPI()
add_adk_fastapi_endpoint(app_adk, adk_agent, path="/")

def main():
    print("✓ Starting Google ADK Gemini agent on http://localhost:8009 ...")
    uvicorn.run(app_adk, host="0.0.0.0", port=8009)

if __name__ == "__main__":
    main()
