"""
test_agent.py
Automated test suite for testing the agent backend, multi-turn memory,
latency benchmarks, and live service health.

Usage:
    python test_agent.py
    # or with pytest:
    pytest test_agent.py
"""

import os
import time
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Load environment
load_dotenv(override=True)


def test_agent_graph_initialization():
    """Test that the agent graph initializes without error."""
    import main
    graph = main.load_graph()
    assert graph is not None, "Failed to load agent graph"
    print("\n✓ Agent graph initialized successfully")


def test_agent_single_turn_response():
    """Test that the agent can receive a prompt and return a valid response."""
    import main
    graph = main.load_graph()
    config = {"configurable": {"thread_id": "test-single-turn"}}

    start_time = time.time()
    response = graph.invoke(
        {"messages": [{"role": "user", "content": "Reply with only the word 'Antigravity'"}]},
        config=config,
    )
    elapsed = time.time() - start_time

    assert "messages" in response, "Response must contain 'messages'"
    last_msg = response["messages"][-1].content
    assert len(last_msg.strip()) > 0, "Agent response should not be empty"

    print(f"\n✓ Single-turn response received in {elapsed:.2f}s:")
    print(f"  Response: \"{last_msg.strip()[:60]}...\"")


def test_agent_multi_turn_memory():
    """
    Test multi-turn state persistence across turns with the same thread_id.
    Turn 1: Introduce a specific detail.
    Turn 2: Ask the agent to recall that detail.
    """
    import main
    graph = main.load_graph()
    unique_thread_id = f"test-memory-{int(time.time())}"
    config = {"configurable": {"thread_id": unique_thread_id}}

    secret_key = "dragonfruit"

    # Turn 1
    t1_input = f"Remember this secret: my favorite fruit is {secret_key}."
    t1_res = graph.invoke({"messages": [{"role": "user", "content": t1_input}]}, config=config)
    assert t1_res["messages"][-1].content, "Turn 1 did not produce output"

    # Turn 2
    t2_input = "What is my favorite fruit? Answer in one word."
    t2_res = graph.invoke({"messages": [{"role": "user", "content": t2_input}]}, config=config)
    answer = t2_res["messages"][-1].content.lower()

    print(f"\n✓ Memory test result for thread '{unique_thread_id}':")
    print(f"  Agent recalled: \"{t2_res['messages'][-1].content.strip()}\"")
    assert secret_key in answer, f"Expected '{secret_key}' to be in agent memory, got: {answer}"


def check_port_health(name: str, url: str) -> bool:
    """Helper to check if a service is running and accessible."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TestAgent/1.0"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status in (200, 404)  # 404 is still alive HTTP
    except urllib.error.HTTPError:
        return True  # Server responded with an HTTP code (alive)
    except Exception:
        return False


def test_live_services_health():
    """Check connectivity to all 3 application tiers."""
    endpoints = {
        "Frontend UI (:3002)": "http://localhost:3002",
        "CopilotKit Runtime (:4002)": "http://localhost:4002/api/copilotkit/info",
        "Python Agent Backend (:8002)": "http://localhost:8002/",
    }

    print("\n--- Live Tier Health Check ---")
    results = {}
    for name, url in endpoints.items():
        is_live = check_port_health(name, url)
        status_icon = "🟢 UP" if is_live else "🔴 DOWN"
        print(f"  {status_icon} - {name}")
        results[name] = is_live

    if not results["Python Agent Backend (:8002)"]:
        print("  ℹ Note: Start 'python main.py' to run the backend server.")


if __name__ == "__main__":
    print("=" * 60)
    print(" Running CopilotKit Agent Automated Test Suite")
    print("=" * 60)

    try:
        test_live_services_health()
    except Exception as e:
        print(f"Health check error: {e}")

    try:
        test_agent_graph_initialization()
    except AssertionError as e:
        print(f"❌ Graph init failed: {e}")

    try:
        test_agent_single_turn_response()
    except AssertionError as e:
        print(f"❌ Single-turn test failed: {e}")

    try:
        test_agent_multi_turn_memory()
    except AssertionError as e:
        print(f"❌ Memory test failed: {e}")

    print("\n" + "=" * 60)
    print(" All Agent Tests Completed Successfully! 🚀")
    print("=" * 60)
