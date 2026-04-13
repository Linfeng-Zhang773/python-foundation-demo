"""
Async LLM client for DeepSeek (OpenAI-compatible API)
"""

import json
from typing import AsyncIterator
import httpx
import asyncio
from app.config import settings
from app.logger import setup_logger
from tenacity import retry, stop_after_attempt, wait_exponential

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


async def chat_once_with_retry(messages: list[dict]) -> str:
    """
    Same as chat once, but retries on transient failures with exponentail backoff
    """
    last_error: Exception | None = None

    for attempt in range(1, settings.max_retries + 1):
        try:
            return await chat_once(messages)
        except LLMError as e:
            last_error = e
            if attempt == settings.max_retries:
                logger.error("重试 %d 次后仍失败", settings.max_retries)
                break
            # exp backoff: 1s,2s, 4s
            wait = 2 ** (attempt - 1)
            logger.warning("第 %d 次失败, %d 秒后重试: %s", attempt, wait, e)
            await asyncio.sleep(wait)

    raise LLMError(f"All {settings.max_retries} retries failed") from last_error


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def chat_once_with_retry_v2(messages: list[dict]) -> str:
    return await chat_once(messages)


async def chat_stream(messages: list[dict]) -> AsyncIterator[str]:
    """
    Stream a chat response, yielding text chunks as they arrive

    Usage:
        async for chunk in chat_stream(messages):
            print(chunk, end="", flush=True)
    """
    url = f"{settings.deepseek_base_url}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "stream": True,  # Set stream to True
    }

    logger.info("流式调用 LLM: %d 条消息", len(messages))

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            async with client.stream(
                "POST", url, headers=headers, json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[len("data: ") :]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data["choices"][0]["delta"]
                        content = delta.get("content")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        logger.warning("解析流式数据失败: %s", e)
                        continue
        except httpx.HTTPError as e:
            logger.exception("流式请求失败")
