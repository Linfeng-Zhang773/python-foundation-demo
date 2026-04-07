from app.models import InvalidQueryError
from app.services.user_service import process_query


def main():
    # valid input
    print("--- 测试 1: 合法输入 ---")
    result = process_query({"question": "什么是 RAG?", "top_k": 3})
    print("结果:", result)

    # Invalid input, question as empty
    print("\n--- 测试 2: question 为空 ---")
    try:
        process_query({"question": "", "top_k": 3})
    except InvalidQueryError as e:
        print("捕获到异常(预期):", type(e).__name__)
    # Invalid:top_k out of range
    print("\n--- 测试 3: top_k 超范围 ---")
    try:
        process_query({"question": "你好", "top_k": 999})
    except InvalidQueryError as e:
        print("捕获到异常(预期):", type(e).__name__)


if __name__ == "__main__":
    main()
