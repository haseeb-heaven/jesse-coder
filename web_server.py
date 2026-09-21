"""
JesseCoder Web Server module.
Provides a FastAPI backend with SSE streaming, code execution,
and static file serving for the TypeScript WebApp.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from bot import JesseCodingBot
    from config import JesseConfig
    from exceptions import JesseBotError
    from executor import CodeExecutor, ExecutionResult
    from code_extractor import ExtractedCodeBlock, get_primary_code_block
except ImportError:
    from .bot import JesseCodingBot
    from .config import JesseConfig
    from .exceptions import JesseBotError
    from .executor import CodeExecutor, ExecutionResult
    from .code_extractor import ExtractedCodeBlock, get_primary_code_block

logger = logging.getLogger("jesse_coder.web_server")
logging.basicConfig(level=logging.INFO)

# Global bot instance
bot: Optional[JesseCodingBot] = None


def get_bot() -> JesseCodingBot:
    """Lazy initialize and retrieve singleton bot instance."""
    global bot
    if bot is None:
        cfg = JesseConfig()
        cfg.validate()
        bot = JesseCodingBot(config=cfg)
    return bot


app = FastAPI(
    title="JesseCoder WebApp API",
    description="High-performance backend for JesseCoder coding bot with streaming and live execution.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = BASE_DIR / "web" / "static"


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="User prompt text")
    model: Optional[str] = Field(None, description="Model override (e.g. jesse-prod)")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")


class ExecuteRequest(BaseModel):
    code: str = Field(..., description="Code to execute")
    language: str = Field(default="python", description="Programming language (python, bash, javascript)")
    timeout: Optional[float] = Field(default=15.0, ge=1.0, le=120.0, description="Execution timeout in seconds")


class ModelSwitchRequest(BaseModel):
    model: str = Field(..., description="Target model identifier (jesse-prod, jesse-pristine, jesse)")


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint with current bot state."""
    active_bot = get_bot()
    return {
        "status": "online",
        "model": active_bot.config.model,
        "base_url": active_bot.config.base_url,
        "history_count": len(active_bot.get_history()),
        "has_last_code": active_bot.last_extracted_code is not None,
        "has_last_execution": active_bot.last_execution_result is not None,
    }


@app.post("/api/model")
async def switch_model(req: ModelSwitchRequest) -> Dict[str, Any]:
    """Switch the active default model on the bot."""
    active_bot = get_bot()
    active_bot.switch_model(req.model)
    logger.info("Active model switched to: %s", active_bot.config.model)
    return {"status": "ok", "model": active_bot.config.model}


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    """
    Stream Jesse API response token-by-token via Server-Sent Events (SSE).
    Followed by a 'done' event with extracted code and raw API payload.
    """
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    active_bot = get_bot()

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Yield streaming token chunks
            for token in active_bot.ask_stream(
                user_prompt=req.prompt,
                model=req.model,
                temperature=req.temperature,
            ):
                payload = json.dumps({"event": "token", "token": token})
                yield f"data: {payload}\n\n"

            # Package completion data
            code_block: Optional[Dict[str, str]] = None
            if active_bot.last_extracted_code:
                code_block = {
                    "code": active_bot.last_extracted_code.code,
                    "language": active_bot.last_extracted_code.language,
                }

            done_payload = json.dumps({
                "event": "done",
                "full_text": active_bot.last_assistant_response or "",
                "extracted_code": code_block,
                "raw_response": active_bot.last_raw_api_response or "",
            })
            yield f"data: {done_payload}\n\n"

        except Exception as exc:
            logger.exception("Error during chat stream: %s", exc)
            error_payload = json.dumps({
                "event": "error",
                "message": str(exc),
            })
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/execute")
async def execute_code(req: ExecuteRequest) -> Dict[str, Any]:
    """
    Execute extracted or custom code in an isolated subprocess.
    Returns standard output, standard error, exit code, and execution time.
    """
    active_bot = get_bot()
    try:
        res: ExecutionResult = active_bot.execute_code(
            code=req.code,
            language=req.language,
            timeout=req.timeout,
        )
        return {
            "success": res.is_success,
            "exit_code": res.exit_code if res.exit_code is not None else -1,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "execution_time_ms": round(res.duration_ms, 2),
            "timed_out": res.timed_out,
            "command": [active_bot.executor.python_bin, "script.py"] if req.language == "python" else [req.language],
        }
    except Exception as exc:
        logger.exception("Execution error: %s", exc)
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Execution failed: {exc}",
            "execution_time_ms": 0.0,
            "timed_out": False,
            "command": [],
        }


@app.post("/api/reset")
async def reset_conversation() -> Dict[str, str]:
    """Reset the current conversation context and memory."""
    active_bot = get_bot()
    active_bot.reset_conversation()
    return {"status": "ok", "message": "Conversation context cleared"}


@app.get("/api/history")
async def get_history() -> Dict[str, Any]:
    """Return current conversation history turns."""
    active_bot = get_bot()
    return {"messages": active_bot.get_history()}



@app.get("/api/raw")
async def get_raw() -> Dict[str, Any]:
    """Return the raw unmodified Jesse API response."""
    active_bot = get_bot()
    raw = active_bot.last_raw_api_response or ""
    return {
        "raw": raw,
        "char_count": len(raw),
    }


# Mount static directory if present
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    fav_path = STATIC_DIR / "favicon.svg"
    if fav_path.exists():
        return FileResponse(str(fav_path), media_type="image/svg+xml")
    raise HTTPException(status_code=404)


@app.get("/")
async def serve_index() -> FileResponse:
    """Serve single-page application entry HTML."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found. Please build frontend first.")
    return FileResponse(str(index_path))
