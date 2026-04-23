# Agentic AI App

A production-grade agentic AI scaffold mapping directly to the architecture diagram.

## Architecture

```
Client → FastAPI Gateway → LangGraph Orchestrator → LLM + Tools
                                    ↓
                          Memory (short/long/vector)
                                    ↓
                       PostgreSQL · Redis · pgvector
```

## Quick start

```bash
cp .env.example .env        # fill in your keys
uv sync                     # install deps
make dev                    # start FastAPI on :8000
make test                   # run test suite
```

## For local inference (Mac Mini M1 + Ollama)

1. Run `ollama pull llama3` in your terminal
2. In `.env` set `OPENAI_BASE_URL=http://localhost:11434/v1`
3. Set `DEFAULT_LLM_MODEL=llama3`

## Component map

| File | Diagram component |
|---|---|
| `app/api/v1/chat.py` | FastAPI gateway |
| `app/core/langgraph/graph.py` | LangGraph orchestrator |
| `app/core/langgraph/nodes.py` | Graph nodes (LLM, tools, security) |
| `app/core/langgraph/state.py` | AgentState TypedDict |
| `app/core/tools.py` | Tool node registry |
| `app/core/security_guards.py` | OWASP LLM01/02 guards |
| `app/services/llm.py` | LLM abstraction + retry |
| `app/services/memory.py` | Memory tiers (short/long/vector) |
| `app/services/database.py` | PostgreSQL async session |
| `app/core/metrics.py` | Prometheus /metrics endpoint |
| `evals/` | Observability + eval framework |
