"""
Simple CLI chat client using DeepSeek API with streaming
    Usage:
    python chat_cli.py
    Type your message and press Enter.
    Type /exit or press Ctrl+C to quit.
    Type /reset to clear conversation history.
"""

import asyncio

from app.services.llm_client import chat_stream, LLMError
from app.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__, settings.log_level)

SYSTEM_PROMPT = "你是一个简洁、友好的助手,用中文回答问题。"


async def chat_loop() -> None:
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("=" * 50)
    print("DeepSeek CLI Chat  (输入 /exit 退出, /reset 清空历史)")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            return
        if not user_input:
            continue
        if user_input == "/exit":
            print("再见!")
            return
        if user_input == "/reset":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("(已清空对话历史)")
            continue

        messages.append({"role": "user", "content": user_input})

        # 流式收取回复,同时拼成完整字符串存回历史
        print("助手: ", end="", flush=True)
        assistant_reply = ""
        try:
            async for chunk in chat_stream(messages):
                print(chunk, end="", flush=True)
                assistant_reply += chunk
            print()  # 换行
        except LLMError as e:
            print(f"\n[错误] {e}")
            # 把刚才的 user 消息撤回,否则下次对话历史不一致
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": assistant_reply})


if __name__ == "__main__":
    asyncio.run(chat_loop())
