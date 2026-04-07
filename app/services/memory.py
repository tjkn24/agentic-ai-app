import structlog
from app.core.config import settings

log = structlog.get_logger()


class MemoryService:
    """
    Three memory tiers:
    1. Short-term  — LangGraph state (in-memory, per-session, already handled by graph)
    2. Long-term   — PostgreSQL via mem0ai (facts about users across sessions)
    3. Semantic    — pgvector (similarity search over past conversations)

    Stub implementation — wire up mem0ai + asyncpg in production.
    """

    async def add(self, user: str, content: str, session_id: str):
        """Store a memory for long-term retrieval."""
        log.info("memory_add", user=user, session=session_id)
        # TODO: mem0ai client.add(content, user_id=user)

    async def search(self, user: str, query: str, limit: int = 5) -> list[str]:
        """Semantic search over past memories."""
        log.info("memory_search", user=user, query=query[:50])
        # TODO: pgvector similarity search
        return []

    async def get_history(self, session_id: str) -> list[dict]:
        """Retrieve conversation history for a session from PostgreSQL."""
        # TODO: asyncpg SELECT from messages WHERE session_id = $1
        return []
