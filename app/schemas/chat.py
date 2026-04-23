from pydantic import BaseModel, Field, field_validator
import re, uuid

class ChatInput(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    @field_validator("message")
    @classmethod
    def strip_and_clean(cls, v: str) -> str:
        v = v.strip()
        # Basic XSS guard — full guard is in security_guards.py
        v = re.sub(r"<[^>]+>", "", v)
        return v

class ChatResponse(BaseModel):
    content: str
    session_id: str
