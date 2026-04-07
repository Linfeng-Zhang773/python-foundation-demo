from dataclasses import dataclass
from pydantic import BaseModel, Field


@dataclass
class ChatMessage:
    """Data structure for internal use."""

    role: str
    content: str
    timestamp: str


class UserQuery(BaseModel):
    """User input validated by Pydantic."""

    question: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    filters: dict[str, str] | None = None


class InvalidQueryError(Exception):
    """Custom exception for invalid input."""

    pass
