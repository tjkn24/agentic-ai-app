from langgraph.graph import StateGraph, END
from app.core.langgraph.state import AgentState
from app.core.langgraph import nodes

def build_graph() -> StateGraph:
    """
    Assemble the LangGraph state graph.
    Flow: START → security_check → llm_node → router
          router → tool_node → llm_node  (loop)
          router → END                   (done)
    """
    g = StateGraph(AgentState)

    g.add_node("security_check", nodes.security_check)
    g.add_node("llm_node", nodes.llm_node)
    g.add_node("tool_node", nodes.tool_node)

    g.set_entry_point("security_check")
    g.add_edge("security_check", "llm_node")
    g.add_edge("tool_node", "llm_node")

    g.add_conditional_edges(
        "llm_node",
        nodes.should_continue,
        {"tool": "tool_node", "end": END},
    )

    return g.compile()
