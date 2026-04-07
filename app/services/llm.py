import asyncio
import json
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from openai import AsyncOpenAI, APIConnectionError
from app.core.config import settings
import structlog

log = structlog.get_logger()

# Load system prompt once at import time
_SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "core" / "prompts" / "system.md"
_SYSTEM_PROMPT = _SYSTEM_PROMPT_PATH.read_text() if _SYSTEM_PROMPT_PATH.exists() else "You are a helpful AI assistant."


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
                except APIConnectionError as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = delay * (2 ** attempt)
                    log.warning("llm_retry", attempt=attempt + 1, wait=wait, error=str(e))
                    await asyncio.sleep(wait)
        return wrapper
    return decorator


def _make_client() -> tuple[AsyncOpenAI, str]:
    """
    Return the right AsyncOpenAI client + model name based on settings.

    Priority:
      1. If OPENAI_API_KEY is set → use OpenAI (or any OpenAI-compatible endpoint
         pointed to by OPENAI_BASE_URL).
      2. Otherwise → use Ollama via its OpenAI-compatible /v1 endpoint.
         Ollama accepts any non-empty string as api_key.
    """
    if settings.OPENAI_API_KEY:
        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        model = settings.DEFAULT_LLM_MODEL
        log.info("llm_backend", backend="openai", model=model)
    else:
        client = AsyncOpenAI(
            api_key="ollama",                          # required but ignored by Ollama
            base_url=f"{settings.OLLAMA_BASE_URL}/v1",
        )
        model = settings.OLLAMA_MODEL
        log.info("llm_backend", backend="ollama", model=model, url=settings.OLLAMA_BASE_URL)
    return client, model


class LLMService:
    """
    Abstraction over LLM providers.
    - No OPENAI_API_KEY → routes to local Ollama (OLLAMA_BASE_URL / OLLAMA_MODEL).
    - OPENAI_API_KEY set → routes to OpenAI (or any compatible endpoint via OPENAI_BASE_URL).
    Both paths use the same openai-python async client.
    """

    @retry(max_attempts=3)
    async def chat(self, messages: list[dict]) -> LLMResponse:
        """Send messages to the LLM and return a structured response."""
        client, model = _make_client()

        # Prepend system prompt if not already present
        full_messages = messages
        if not messages or messages[0].get("role") != "system":
            full_messages = [{"role": "system", "content": _SYSTEM_PROMPT}] + messages

        log.info("llm_call", model=model, message_count=len(full_messages))

        resp = await client.chat.completions.create(
            model=model,
            messages=full_messages,
        )

        choice = resp.choices[0]
        text = choice.message.content or ""
        tool_call = None

        # Surface tool_calls if the model returns them
        if choice.message.tool_calls:
            tool_call = choice.message.tool_calls[0].function.name

        usage = {}
        if resp.usage:
            usage = {
                "prompt_tokens": resp.usage.prompt_tokens,
                "completion_tokens": resp.usage.completion_tokens,
                "total_tokens": resp.usage.total_tokens,
            }

        log.info("llm_response", model=model, tokens=usage.get("total_tokens"))
        return LLMResponse(text=text, tool_call=tool_call, usage=usage)

    async def stream(self, messages: list[dict]):
        """Async generator — yields text chunks for the /stream endpoint."""
        client, model = _make_client()

        full_messages = messages
        if not messages or messages[0].get("role") != "system":
            full_messages = [{"role": "system", "content": _SYSTEM_PROMPT}] + messages

        async with client.chat.completions.stream(
            model=model,
            messages=full_messages,
        ) as stream:
            async for event in stream:
                chunk = event.choices[0].delta.content if event.choices else None
                if chunk:
                    yield chunk

    @classmethod
    def get(cls) -> "LLMService":
        """FastAPI Depends() factory."""
        return cls()
