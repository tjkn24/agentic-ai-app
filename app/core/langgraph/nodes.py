import structlog
from app.core.langgraph.state import AgentState
from app.services.llm import LLMService
from app.core.security_guards import check_prompt_injection
from app.core.tools import TOOLS

log = structlog.get_logger()
MAX_ITERATIONS = 10

async def security_check(state: AgentState) -> AgentState:
    last_message = state["messages"][-1]["content"]
    if check_prompt_injection(last_message):
        log.warning("prompt_injection_detected", user=state["user"])
        return {**state, "done": True, "error": "Input rejected by security policy."}
    return state

async def llm_node(state: AgentState) -> AgentState:
    if state.get("done") or state["iteration"] >= MAX_ITERATIONS:
        return {**state, "done": True}

    try:
        from pathlib import Path
        llm = LLMService()
        system_prompt = (Path(__file__).parent.parent / "prompts" / "system.md").read_text()
        messages_with_system = [{"role": "system", "content": system_prompt}] + state["messages"]
        response = await llm.chat(messages_with_system)
    except Exception as e:
        # Surface the real error message rather than swallowing it
        log.error("llm_node_error", error=str(e), model_hint="check ollama is running and model name is correct")
        return {
            **state,
            "done": True,
            "error": f"LLM error: {e}",
            "messages": [*state["messages"], {"role": "assistant", "content": f"LLM error: {e}"}],
        }

    if response.tool_call:
        log.info("tool_requested", tool=response.tool_call, user=state["user"])
        return {
            **state,
            "current_tool": response.tool_call,
            "messages": [*state["messages"], {"role": "assistant", "content": f"[calling tool: {response.tool_call}]"}],
            "iteration": state["iteration"] + 1,
        }

    return {
        **state,
        "messages": [*state["messages"], {"role": "assistant", "content": response.text}],
        "done": True,
        "iteration": state["iteration"] + 1,
    }

async def tool_node(state: AgentState) -> AgentState:
    tool_name = state.get("current_tool")
    if not tool_name or tool_name not in TOOLS:
        return {**state, "tool_result": "Tool not found.", "current_tool": None}

    log.info("tool_executing", tool=tool_name, user=state["user"])
    try:
        result = await TOOLS[tool_name](state)
    except Exception as e:
        log.error("tool_error", tool=tool_name, error=str(e))
        result = f"Tool error: {e}"

    return {
        **state,
        "tool_result": result,
        "current_tool": None,
        "messages": [*state["messages"], {"role": "tool", "content": result}],
    }

def should_continue(state: AgentState) -> str:
    if state.get("done") or state["iteration"] >= MAX_ITERATIONS:
        return "end"
    if state.get("current_tool"):
        return "tool"
    return "end"
