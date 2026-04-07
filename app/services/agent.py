import structlog
from app.core.langgraph.graph import build_graph
from app.core.langgraph.state import AgentState
from app.core.security_guards import sanitize_output

log = structlog.get_logger()
_graph = build_graph()

class AgentService:
    """
    Thin wrapper around the LangGraph compiled graph.
    Called from API routes — keeps routing logic out of graph nodes.
    """

    async def run(self, message: str, session_id: str, user: str) -> str:
        initial_state: AgentState = {
            "messages": [{"role": "user", "content": message}],
            "session_id": session_id,
            "user": user,
            "current_tool": None,
            "tool_result": None,
            "iteration": 0,
            "done": False,
            "error": None,
        }
        final_state = await _graph.ainvoke(initial_state)
        if final_state.get("error"):
            return final_state["error"]
        last = final_state["messages"][-1]["content"]
        return sanitize_output(last)

    async def stream(self, message: str, session_id: str, user: str):
        """Yield tokens progressively — used by the /stream endpoint."""
        result = await self.run(message, session_id, user)
        for word in result.split():
            yield word + " "

    @classmethod
    def get(cls) -> "AgentService":
        return cls()
