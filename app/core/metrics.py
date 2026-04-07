from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter

router = APIRouter()

llm_calls_total = Counter("llm_calls_total", "Total LLM invocations", ["model", "status"])
llm_latency = Histogram("llm_latency_seconds", "LLM call latency", ["model"])
tool_calls_total = Counter("tool_calls_total", "Total tool invocations", ["tool_name"])

@router.get("/metrics")
async def metrics():
    from starlette.responses import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
