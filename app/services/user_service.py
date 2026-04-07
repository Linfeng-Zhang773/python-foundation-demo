from pydantic import ValidationError

from app.config import settings
from app.logger import setup_logger
from app.models import UserQuery, InvalidQueryError

# Create a module-level logger using the configured log level
logger = setup_logger(__name__, settings.log_level)


def process_query(raw_input: dict) -> dict:
    """
    Process a user query:
    validate input -> log request -> return a mock response

    In the future RAG project, this function can be replaced with real
    retrieval and LLM invocation logic
    """
    # Log the raw incoming requests data
    logger.info("收到请求: %s", raw_input)

    try:
        # Validate and parse external input with Pydantic
        query = UserQuery(**raw_input)
    except ValidationError as e:
        # Log the validation error with traceback information
        logger.exception("输入校验失败")
        # Raise a custom business exception for invalid user input
        raise InvalidQueryError(str(e)) from e

    # Log which model is being used
    logger.info("使用模型: %s", settings.llm_model)

    # Return a mock result for now
    return {
        "question": query.question,
        "model": settings.llm_model,
        "answer": f"[mock] 你问的是: {query.question}",
        "top_k": query.top_k,
    }
