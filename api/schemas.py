"""
API request/response schemas.
Separated from app/models.py (domain models) to keep API contracts
independent from internal business types.
"""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """One message in an OpenAI-style chat history."""

    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    """Request body for POST /chat."""

    messages: list[ChatMessage] = Field(..., min_length=1, max_length=50)
    model: str | None = None  # optional override, falls back to settings.llm_model


class ChatResponse(BaseModel):
    """Response body for POST /chat."""

    model: str
    reply: str


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str
    model: str
    log_level: str
