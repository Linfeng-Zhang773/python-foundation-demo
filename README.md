# python-foundation-demo
Python engineering fundamentals
Set up a standard project skeleton covering type hints, Pydantic validation, configuration management, and logging.

## Project structure

- `app/config.py` — Configuration management based on pydantic-settings
- `app/logger.py` — Unified logger factory
- `app/models.py` — Internal domain models (dataclass + Pydantic)
- `app/services/user_service.py` — Example business logic
- `app/services/llm_client.py` — Async LLM client (DeepSeek, with retry & streaming)
- `app/api/schemas.py` — API request/response schemas
- `app/api/routes.py` — HTTP route handlers
- `main.py` — Day 1 demo entry
- `chat_cli.py` — Day 2 interactive CLI chat
- `server.py` — Day 3 FastAPI entry (run with `uvicorn server:app --reload`)

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your DeepSeek API key
python main.py         # Day 1 demo
python chat_cli.py     # Day 2 interactive chat
```
Inside the chat:
- Type your message and press Enter
- `/reset` clears conversation history
- `/exit` or Ctrl+C quits

### Run the HTTP API (Day 3)

```bash
uvicorn server:app --reload
```

Then open http://127.0.0.1:8000/docs for interactive API docs.

Endpoints:
- `GET /health` — liveness probe
- `POST /chat` — full reply, non-streaming
- `POST /chat/stream` — Server-Sent Events streaming

## What I Learned

### Day 1 — Python foundations
- When to use dataclass (internal structures) vs Pydantic (boundary validation)
- Centralizing configuration with pydantic-settings, validated at startup
- Standard logging patterns; `logger.exception` automatically includes the traceback
- The role of `.env` vs `.env.example`

### Day 2 — Async & LLM API
- `async`/`await` and the role of the event loop; why I/O-bound work benefits most from async
- `httpx.AsyncClient` with timeout, connection pooling via `async with`
- Custom `LLMError` to wrap `httpx.HTTPError`, keeping HTTP details out of upstream code
- Hand-rolled exponential backoff retry (1s → 2s → 4s) and when *not* to retry (e.g. 4xx auth errors)
- Streaming with Server-Sent Events: parsing `data: ...` lines, handling `[DONE]`, skipping malformed chunks without killing the stream
- Async generators (`async def` + `yield`) consumed by `async for`
- Multi-turn chat state: appending user/assistant messages to history, rolling back on failure to keep state consistent

### Day 3 — FastAPI fundamentals
- Routing with `APIRouter`, keeping route files independent of the app entry
- Pydantic models at the API boundary give free validation + auto-generated `/docs`
- Separation between domain models (`app/models.py`) and API schemas (`app/api/schemas.py`)
- Translating business exceptions (`LLMError`) into HTTP exceptions (`HTTPException(502)`)
- Streaming responses via `StreamingResponse` + async generator + SSE format (`data: ...\n\n`)
- Why error handling in a streaming endpoint must `yield` the error, not `raise` it
- CORS middleware basics and the `allow_origins=["*"]` + credentials constraint
- Global exception handler for defense-in-depth: opaque message to clients, full traceback in logs