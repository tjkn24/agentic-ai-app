import structlog
from app.core.langgraph.state import AgentState
from app.services.llm import LLMService
from app.core.security_guards import check_prompt_injection
from app.core.tools import TOOLS

log = structlog.get_logger()
MAX_ITERATIONS = 10

async def security_check(state: AgentState) -> AgentState:
    """
    OWASP LLM01: Prompt Injection guard.
    Runs before any message reaches the LLM.
    Halts the graph if injection pattern detected.
    """
    last_message = state["messages"][-1]["content"]
    if check_prompt_injection(last_message):
        log.warning("prompt_injection_detected", user=state["user"])
        return {**state, "done": True, "error": "Input rejected by security policy."}
    return state

async def llm_node(state: AgentState) -> AgentState:
    """
    Core reasoning node. Sends messages to the LLM.
    If the LLM requests a tool, sets current_tool.
    If the LLM produces a final answer, sets done=True.
    """
    if state.get("done") or state["iteration"] >= MAX_ITERATIONS:
        return {**state, "done": True}

    llm = LLMService()
    response = await llm.chat(state["messages"])

    if response.tool_call:
        log.info("tool_requested", tool=response.tool_call, user=state["user"])
        return {
            **state,
            "current_tool": response.tool_call,
            "messages": [{"role": "assistant", "content": f"[calling tool: {response.tool_call}]"}],
            "iteration": state["iteration"] + 1,
        }

    return {
        **state,
        "messages": [{"role": "assistant", "content": response.text}],
        "done": True,
        "iteration": state["iteration"] + 1,
    }

async def tool_node(state: AgentState) -> AgentState:
    """
    Executes whichever tool the LLM requested.
    Tool output is added back into messages so the LLM can reason over it.
    OWASP Agentic Top 10 #3: tools run with minimal permissions.
    """
    tool_name = state.get("current_tool")
    if not tool_name or tool_name not in TOOLS:
        return {**state, "tool_result": "Tool not found.", "current_tool": None}

    log.info("tool_executing", tool=tool_name, user=state["user"])
    result = await TOOLS[tool_name](state)
    return {
        **state,
        "tool_result": result,
        "current_tool": None,
        "messages": [{"role": "tool", "content": result}],
    }

def should_continue(state: AgentState) -> str:
    """Conditional edge: route to tool or end."""
    if state.get("done") or state["iteration"] >= MAX_ITERATIONS:
        return "end"
    if state.get("current_tool"):
        return "tool"
    return "end"
