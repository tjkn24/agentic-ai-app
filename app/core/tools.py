from typing import Callable
from app.core.langgraph.state import AgentState

# Tool registry: name → async function(state) → str
# Add new tools here; the LLM sees their names via the system prompt.

async def web_search(state: AgentState) -> str:
    """Stub: replace with real Tavily / SerpAPI call."""
    last = state["messages"][-1]["content"]
    return f"[web_search stub] Results for: {last}"

async def calculator(state: AgentState) -> str:
    """Stub: safe arithmetic evaluator."""
    return "[calculator stub] result: 42"

async def code_executor(state: AgentState) -> str:
    """
    Stub: sandboxed code execution.
    OWASP LLM03 — never eval() untrusted code directly.
    Use a sandbox (e2b, subprocess with timeout) in production.
    """
    return "[code_executor stub] Execution complete."

TOOLS: dict[str, Callable] = {
    "web_search": web_search,
    "calculator": calculator,
    "code_executor": code_executor,
}
