import time
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

log = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Binds request_id to every log line within a request lifecycle.
    Logs method, path, status code, and duration automatically.
    Maps to OWASP LLM09 (logging & monitoring) requirement.
    """
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        t = time.perf_counter()
        log.info("request_start", method=request.method, path=request.url.path)
        response = await call_next(request)
        duration = round((time.perf_counter() - t) * 1000)
        log.info("request_end", status=response.status_code, duration_ms=duration)
        return response
