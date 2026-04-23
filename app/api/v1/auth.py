from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth import LoginInput, TokenResponse
from app.core.security import create_access_token, verify_password

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginInput):
    """
    Authenticate user and return JWT token.
    OWASP LLM guard: credentials never reach the agent core.
    """
    # TODO: replace with real DB lookup
    if body.username != "demo" or not verify_password(body.password, "demo"):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": body.username})
    return TokenResponse(access_token=token)
