"""
ui.py — Chainlit chat UI for the agentic AI app.

Run with:  chainlit run ui.py
Opens at:  http://localhost:8001

This file is completely separate from the FastAPI backend.
It talks to the backend via HTTP — the same way any real client would.
Make sure the FastAPI server is running first:  make dev (port 8000)
"""

import httpx
import chainlit as cl

# ── Configuration ──────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"
DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo"


async def get_token() -> str:
    """
    Authenticate against POST /api/v1/auth/login and return a JWT token.
    Called once when a new chat session starts.
    In production: replace with real user auth (OAuth, SSO, etc.)
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json={"username": DEMO_USERNAME, "password": DEMO_PASSWORD},
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


# ── Chainlit lifecycle hooks ────────────────────────────────────────────────

@cl.on_chat_start
async def on_start():
    """
    Runs once when a user opens the chat.
    Gets a JWT token and stores it in the Chainlit session
    so every subsequent message can use it.
    """
    try:
        token = await get_token()
        cl.user_session.set("token", token)
        cl.user_session.set("session_id", None)  # backend will generate one

        await cl.Message(
            content=(
                "Hello! I'm your AI assistant.\n\n"
                "I can answer questions, search the web, run calculations, "
                "and execute code. How can I help you today?"
            )
        ).send()

    except Exception as e:
        await cl.Message(
            content=f"Could not connect to the backend: {e}\n\n"
                    "Make sure the FastAPI server is running:\n`make dev`"
        ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """
    Runs every time the user sends a message.
    Forwards the message to POST /api/v1/chat/stream and streams
    tokens back to the UI as they arrive.
    """
    token = cl.user_session.get("token")
    session_id = cl.user_session.get("session_id")

    if not token:
        await cl.Message(content="Session expired. Please refresh the page.").send()
        return

    # Show a thinking indicator while waiting for first token
    msg = cl.Message(content="")
    await msg.send()

    payload = {"message": message.content}
    if session_id:
        payload["session_id"] = session_id

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{BACKEND_URL}/api/v1/chat/stream",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            ) as resp:
                resp.raise_for_status()

                # Stream tokens as they arrive from the backend
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        token_text = line[6:]  # strip "data: " prefix
                        await msg.stream_token(token_text)

                    # Capture session_id from first response header
                    # so memory is tied to this conversation
                    if not session_id and "x-session-id" in resp.headers:
                        session_id = resp.headers["x-session-id"]
                        cl.user_session.set("session_id", session_id)

        await msg.update()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            # Token expired — re-authenticate silently
            try:
                new_token = await get_token()
                cl.user_session.set("token", new_token)
                await msg.update()
                await cl.Message(
                    content="Session refreshed. Please resend your message."
                ).send()
            except Exception:
                await msg.update()
                await cl.Message(content="Authentication failed. Please refresh.").send()
        elif e.response.status_code == 429:
            await msg.update()
            await cl.Message(
                content="Rate limit reached. Please wait a moment before sending again."
            ).send()
        else:
            await msg.update()
            await cl.Message(content=f"Backend error: {e.response.status_code}").send()

    except httpx.ConnectError:
        await msg.update()
        await cl.Message(
            content="Cannot reach the backend. Is `make dev` running on port 8000?"
        ).send()

    except Exception as e:
        await msg.update()
        await cl.Message(content=f"Unexpected error: {e}").send()
