from typing import TypedDict, Annotated
from operator import add

class AgentState(TypedDict):
    """
    LangGraph state — flows through every node in the graph.
    'messages' uses the 'add' reducer: each node appends, never replaces.
    This is the single source of truth during a reasoning loop.
    """
    messages: Annotated[list[dict], add]   # conversation history
    session_id: str                         # ties state to a user session
    user: str                               # authenticated user
    current_tool: str | None               # which tool is being called
    tool_result: str | None                # last tool output
    iteration: int                          # guard against infinite loops
    done: bool                              # stopping condition
    error: str | None                      # captured error, if any
