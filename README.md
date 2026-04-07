# python-foundation-demo
Python engineering fundamentals
Set up a standard project skeleton covering type hints, Pydantic validation, configuration management, and logging.

## Project structure

- `app/config.py` — Configuration management based on pydantic-settings
- `app/logger.py` — Unified logger factory
- `app/models.py` — dataclass and Pydantic models
- `app/services/user_service.py` — Example business logic
- `main.py` — Entry point

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your key
python main.py
```

## What I Learned

- When to use dataclass (internal structures) vs Pydantic (boundary validation)
- Centralizing configuration with pydantic-settings, validated at startup
- Standard logging patterns; `logger.exception` automatically includes the traceback
- The role of `.env` vs `.env.example`
