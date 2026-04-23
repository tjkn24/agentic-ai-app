from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.limiter import limiter
from app.core.metrics import router as metrics_router
from app.api.v1.api import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    # TODO: initialise DB pool, Redis, LangSmith tracer here
    yield
    # TODO: close DB pool, Redis connections here

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestLoggingMiddleware)
app.include_router(api_router, prefix="/api/v1")
app.include_router(metrics_router)

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.APP_ENV}
