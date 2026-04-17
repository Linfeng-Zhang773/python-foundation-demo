"""
FastAPI application entry point.
Run with:
    uvicorn server:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import router
from app.config import settings
from app.logger import setup_logger

logger = setup_logger(__name__, settings.log_level)

app = FastAPI(
    title="Python Foundation Demo API",
    description="Day 3: minimal FastAPI wrapping the async LLM client.",
    version="0.3.0",
)

# CORS: allow any origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected errors."""
    logger.exception("未处理异常: %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.include_router(router)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("服务启动, model=%s", settings.llm_model)
