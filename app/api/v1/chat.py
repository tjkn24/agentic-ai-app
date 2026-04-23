from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatInput, ChatResponse
from app.core.security import get_current_user
from app.core.limiter import limiter
from app.services.agent import AgentService
from starlette.requests import Request
import structlog

router = APIRouter()
log = structlog.get_logger()

@router.post("/", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(
    request: Request,
    body: ChatInput,
    user: str = Depends(get_current_user),
    agent: AgentService = Depends(AgentService.get),
):
    """
    Main chat endpoint. Input validated by Pydantic before reaching agent.
    Rate-limited per user. All steps logged via observability layer.
    """
    bound_log = log.bind(user=user, session=body.session_id)
    bound_log.info("chat_received", message_len=len(body.message))
    result = await agent.run(body.message, session_id=body.session_id, user=user)
    return ChatResponse(content=result, session_id=body.session_id)

@router.post("/stream")
@limiter.limit("20/minute")
async def chat_stream(
    request: Request,
    body: ChatInput,
    user: str = Depends(get_current_user),
    agent: AgentService = Depends(AgentService.get),
):
    """
    Streaming variant — yields tokens as they arrive from the LLM.
    Uses FastAPI StreamingResponse + async generator.
    """
    async def token_generator():
        async for chunk in agent.stream(body.message, session_id=body.session_id, user=user):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(token_generator(), media_type="text/event-stream")
