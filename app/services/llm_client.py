"""
Async LLM client for DeepSeek (OpenAI-compatible API)
"""

import httpx

from app.config import settings
from app.logger import setup_logger

logger = setup_logger(__name__, settings.log_level)


class LLMError(Exception):
    """
    Raised when LLM api call fails
    """

    pass


async def chat_once(messages: list[dict]) -> str:
    """
    Send a chat request and return the full reply as a string.

    Args:
        messages: OpenAI-style message list, e.g.
                [{"role":"user", "content": "你好"}]

    Returns:
        The assistant's reply text

    Raises:
        LLMError: if the API call fails
    """
    url = f"{settings.deepseek_base_url}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "stream": False,
    }

    logger.info("调用 LLM: model=%s, messages=%d 条", settings.llm_model, len(messages))

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.exception("LLM 请求失败")
            raise LLMError(f"LLM request failed: {e}") from e

    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    logger.info("LLM 返回 %d 字符", len(reply))
    return reply
