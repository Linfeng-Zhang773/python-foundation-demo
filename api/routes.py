"""
HTTP routes for the chat API
"""

from fastapi import APIRouter, HTTPException, status


from api.schemas import ChatRequest, ChatResponse, HealthResponse
from app.config import settings
from app.logger import setup_logger
from fastapi.responses import StreamingResponse
from app.services.llm_client import chat_once_with_retry, LLMError

logger = setup_logger(__name__, settings.log_level)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Liveness probe
    """
    return HealthResponse(
        status="ok",
        model=settings.llm_model,
        log_level=settings.log_level,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a chat request to the LLM and return the full reply.
    Non-streaming. Streaming endpoint is added in a later step.
    """
    # Convert Pydantic models to plain dicts for the LLM client
    messages = [m.model_dump() for m in request.messages]
    model = request.model or settings.llm_model

    logger.info("收到 /chat 请求: %d 条消息, model=%s", len(messages), model)

    try:
        reply = await chat_once_with_retry(messages)
    except LLMError as e:
        logger.exception("LLM 调用失败")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM upstream error: {e}",
        ) from e

    return ChatResponse(model=model, reply=reply)


@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest) -> StreamingResponse:
    """
    Stream a chat response as Server-Sent Events.
    Each event has the form:  data: <text chunk>\n\n
    """
    from app.services.llm_client import chat_stream  # local import to keep top tidy

    messages = [m.model_dump() for m in request.messages]
    logger.info("收到 /chat/stream 请求: %d 条消息", len(messages))

    async def event_generator():
        try:
            async for chunk in chat_stream(messages):
                # SSE format: "data: <payload>\n\n"
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except LLMError as e:
            logger.exception("流式 LLM 调用失败")
            yield f"data: [ERROR] {e}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
