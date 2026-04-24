import asyncio
from dataclasses import dataclass
from functools import wraps
from app.core.config import settings
import structlog

log = structlog.get_logger()


@dataclass
class LLMResponse:
    text: str
    tool_call: str | None = None
    usage: dict | None = None


def retry(max_attempts: int = 3, delay: float = 1.0):
    """Exponential backoff retry decorator for LLM calls."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = delay * (2**attempt)
                    log.warning(
                        "llm_retry", attempt=attempt + 1, wait=wait, error=str(e)
                    )
                    await asyncio.sleep(wait)

        return wrapper

    return decorator


class LLMService:
    """
    Abstraction over LLM providers.
    Switch between OpenAI and Ollama by changing settings.DEFAULT_LLM_MODEL.
    For local inference on Mac Mini M1: set OLLAMA_BASE_URL in .env.
    """

    @retry(max_attempts=3)
    async def chat(self, messages: list[dict]) -> LLMResponse:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY or "ollama",
        )
        log.info("llm_call", model=settings.DEFAULT_LLM_MODEL, messages=len(messages))
        resp = await client.chat.completions.create(
            model=settings.DEFAULT_LLM_MODEL, messages=messages
        )
        return LLMResponse(
            text=resp.choices[0].message.content,
            usage=dict(resp.usage) if resp.usage else None,
        )

    async def stream(self, messages: list[dict]):
        """Async generator — yields text chunks for streaming endpoint."""
        # TODO: replace with real streaming call
        for word in "This is a stub streaming response from the LLM.".split():
            yield word + " "
            await asyncio.sleep(0.05)

    @classmethod
    def get(cls) -> "LLMService":
        """FastAPI Depends() factory."""
        return cls()
