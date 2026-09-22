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

# Ensure source and project root are in sys.path
GUI_DIR = Path(__file__).resolve().parent
_ROOT_DIR = GUI_DIR.parent.parent
_SOURCE_DIR = _ROOT_DIR / "source"
for _p in (str(_SOURCE_DIR), str(GUI_DIR), str(_ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from bot import JesseCodingBot
    from client import JesseClient
    from config import JesseConfig
    from exceptions import JesseBotError
    from executor import CodeExecutor, ExecutionResult
    from code_extractor import ExtractedCodeBlock, get_primary_code_block
except ImportError:
    from jesse_coder.bot import JesseCodingBot
    from jesse_coder.client import JesseClient
    from jesse_coder.config import JesseConfig
    from jesse_coder.exceptions import JesseBotError
    from jesse_coder.executor import CodeExecutor, ExecutionResult
    from jesse_coder.code_extractor import ExtractedCodeBlock, get_primary_code_block

try:
    from dotenv import load_dotenv
    _ENV_PATH = _ROOT_DIR / ".env"
    if _ENV_PATH.exists():
        load_dotenv(_ENV_PATH, override=True)
except ImportError:
    pass

logger = logging.getLogger("jesse_coder.web_server")
logging.basicConfig(level=logging.INFO)

# Global bot instance
bot: Optional[JesseCodingBot] = None


def extract_request_api_key(request: Request) -> Optional[str]:
    """Extract API key from custom header or Bearer authorization."""
    key = request.headers.get("x-jesse-api-key")
    if key and key.strip():
        return key.strip()
    auth = request.headers.get("authorization")
    if auth and auth.strip().lower().startswith("bearer "):
        token = auth.strip()[7:].strip()
        if token:
            return token
    return None


def mask_api_key(key: str) -> str:
    """Mask an API key for safe UI display (e.g. jesse_li••••••••3a2f)."""
    if not key or key == "unconfigured":
        return ""
    if len(key) <= 8:
        return "•" * len(key)
    prefix = key[:8]
    suffix = key[-4:] if len(key) >= 12 else key[-2:]
    return f"{prefix}{'•' * 8}{suffix}"


def is_vercel_env() -> bool:
    """Return True if running inside Vercel serverless environment."""
    return bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


def save_settings_to_env(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> bool:
    """Attempt to update or append settings in .env file if writable on disk."""
    try:
        env_path = _ROOT_DIR / ".env"
        lines = []
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()

        updates = {}
        if api_key is not None:
            updates["JESSE_API_KEY"] = api_key
        if base_url is not None:
            updates["JESSE_BASE_URL"] = base_url
        if model is not None:
            updates["JESSE_MODEL"] = model

        new_lines = []
        found_keys = set()
        for line in lines:
            line_str = line.strip()
            if "=" in line_str and not line_str.startswith("#"):
                k, _ = line_str.split("=", 1)
                k = k.strip()
                if k in updates:
                    new_lines.append(f"{k}={updates[k]}")
                    found_keys.add(k)
                    continue
            new_lines.append(line)

        for k, v in updates.items():
            if k not in found_keys:
                new_lines.append(f"{k}={v}")

        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return True
    except Exception as exc:
        logger.warning("Could not persist settings to .env: %s", exc)
        return False


def get_bot(api_key_override: Optional[str] = None) -> JesseCodingBot:
    """Lazy initialize and retrieve bot instance."""
    global bot
    env_path = _ROOT_DIR / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path, override=False)
        except ImportError:
            pass

    if bot is None:
        cfg = JesseConfig()
        if not cfg.api_key:
            cfg.api_key = "unconfigured"
        bot = JesseCodingBot(config=cfg)

    # If an explicit override header is passed that is not unconfigured
    if api_key_override and api_key_override.strip() and api_key_override.strip() != "unconfigured":
        if bot.config.api_key != api_key_override.strip():
            bot.config.api_key = api_key_override.strip()
            bot.client = JesseClient(config=bot.config)
    else:
        # Check if environment / .env has a real key and restore if needed
        env_key = os.getenv("JESSE_API_KEY", "").strip()
        if env_key and env_key != "unconfigured" and (not api_key_override):
            if bot.config.api_key != env_key:
                bot.config.api_key = env_key
                bot.client = JesseClient(config=bot.config)

    # Ensure base_url defaults to https://jesse.my/api/v1
    env_base = os.getenv("JESSE_BASE_URL", "https://jesse.my/api/v1").strip()
    if not bot.config.base_url or "solidsf.com" in bot.config.base_url:
        bot.config.base_url = env_base if env_base else "https://jesse.my/api/v1"
        bot.client = JesseClient(config=bot.config)

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

STATIC_DIR = GUI_DIR / "static"


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


class SettingsRequest(BaseModel):
    api_key: Optional[str] = Field(None, description="Jesse API Key")
    base_url: Optional[str] = Field(None, description="Jesse API Base URL")
    model: Optional[str] = Field(None, description="Default model identifier")


class VerifyRequest(BaseModel):
    api_key: Optional[str] = Field(None, description="API key to verify")
    base_url: Optional[str] = Field(None, description="Base URL to verify against")


@app.get("/api/health")
async def health_check(request: Request) -> Dict[str, Any]:
    """Health check endpoint with current bot state and configuration."""
    header_key = extract_request_api_key(request)
    active_bot = get_bot(api_key_override=header_key)
    current_key = active_bot.config.api_key
    has_key = bool(current_key and current_key != "unconfigured")
    return {
        "status": "online",
        "model": active_bot.config.model,
        "base_url": active_bot.config.base_url,
        "has_api_key": has_key,
        "api_key_masked": mask_api_key(current_key) if has_key else "",
        "is_vercel": is_vercel_env(),
        "history_count": len(active_bot.get_history()),
        "has_last_code": active_bot.last_extracted_code is not None,
        "has_last_execution": active_bot.last_execution_result is not None,
    }


@app.get("/api/settings")
async def get_settings(request: Request) -> Dict[str, Any]:
    """Retrieve current system settings with masked API key."""
    header_key = extract_request_api_key(request)
    active_bot = get_bot(api_key_override=header_key)
    current_key = active_bot.config.api_key
    has_key = bool(current_key and current_key != "unconfigured")
    return {
        "has_api_key": has_key,
        "api_key_masked": mask_api_key(current_key) if has_key else "",
        "base_url": active_bot.config.base_url,
        "model": active_bot.config.model,
        "is_vercel": is_vercel_env(),
    }


@app.post("/api/settings")
async def update_settings(req: SettingsRequest, request: Request) -> Dict[str, Any]:
    """Update system settings, persist to environment and .env if writable."""
    active_bot = get_bot()

    if req.api_key is not None and req.api_key.strip():
        new_key = req.api_key.strip()
        active_bot.config.api_key = new_key
        os.environ["JESSE_API_KEY"] = new_key
        active_bot.client = JesseClient(config=active_bot.config)
        logger.info("Updated API key via Settings endpoint")

    if req.base_url is not None and req.base_url.strip():
        new_url = req.base_url.strip().rstrip("/")
        active_bot.config.base_url = new_url
        os.environ["JESSE_BASE_URL"] = new_url
        active_bot.client = JesseClient(config=active_bot.config)
        logger.info("Updated Base URL to %s", new_url)

    if req.model is not None and req.model.strip():
        new_model = req.model.strip()
        active_bot.config.model = new_model
        os.environ["JESSE_MODEL"] = new_model
        logger.info("Updated default model to %s", new_model)

    saved_to_env = save_settings_to_env(
        api_key=req.api_key.strip() if req.api_key else None,
        base_url=req.base_url.strip() if req.base_url else None,
        model=req.model.strip() if req.model else None,
    )

    current_key = active_bot.config.api_key
    has_key = bool(current_key and current_key != "unconfigured")
    return {
        "status": "ok",
        "has_api_key": has_key,
        "api_key_masked": mask_api_key(current_key) if has_key else "",
        "base_url": active_bot.config.base_url,
        "model": active_bot.config.model,
        "saved_to_env": saved_to_env,
        "is_vercel": is_vercel_env(),
    }


@app.post("/api/settings/verify")
async def verify_settings(req: VerifyRequest, request: Request) -> Dict[str, Any]:
    """Verify API credentials against Jesse API by checking auth and querying model list."""
    # 1. Check explicit key in body
    key_to_test = req.api_key.strip() if req.api_key and req.api_key.strip() else None

    # 2. Check .env directly so local verification always works out of the box
    if not key_to_test:
        env_path = _ROOT_DIR / ".env"
        if env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path, override=True)
            except ImportError:
                pass
        env_key = os.getenv("JESSE_API_KEY", "").strip()
        if env_key and env_key != "unconfigured":
            key_to_test = env_key

    # 3. Check header key (for Vercel / serverless deployments)
    if not key_to_test:
        header_key = extract_request_api_key(request)
        if header_key and header_key != "unconfigured":
            key_to_test = header_key

    # 4. Fallback to active bot config
    if not key_to_test:
        active_bot = get_bot()
        key_to_test = active_bot.config.api_key

    if not key_to_test or key_to_test == "unconfigured":
        return {"valid": False, "error": "No API key provided or found in .env."}

    # Resolve base_url: prefer req.base_url, then .env, then https://jesse.my/api/v1
    raw_base = req.base_url.strip() if req.base_url and req.base_url.strip() else os.getenv("JESSE_BASE_URL", "https://jesse.my/api/v1").strip()
    base_url = raw_base.rstrip("/")
    if "solidsf.com" in base_url or not base_url:
        base_url = "https://jesse.my/api/v1"

    try:
        test_cfg = JesseConfig(api_key=key_to_test, base_url=base_url)
        test_client = JesseClient(config=test_cfg)
        # 1. Verify key authenticity with Jesse auth endpoint
        test_client.get_memory()
        # 2. Retrieve accessible models
        models = test_client.get_models()
        return {"valid": True, "models": models, "base_url": base_url}
    except Exception as exc:
        return {"valid": False, "error": str(exc), "base_url": base_url}


@app.post("/api/model")
async def switch_model(req: ModelSwitchRequest) -> Dict[str, Any]:
    """Switch the active default model on the bot."""
    active_bot = get_bot()
    active_bot.switch_model(req.model)
    logger.info("Active model switched to: %s", active_bot.config.model)
    return {"status": "ok", "model": active_bot.config.model}


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest, request: Request) -> StreamingResponse:
    """
    Stream Jesse API response token-by-token via Server-Sent Events (SSE).
    Followed by a 'done' event with extracted code and raw API payload.
    """
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    header_key = extract_request_api_key(request)
    active_bot = get_bot(api_key_override=header_key)

    if not active_bot.config.api_key or active_bot.config.api_key == "unconfigured":
        raise HTTPException(
            status_code=401,
            detail="Jesse API key is not configured. Please open Settings (gear icon in the top right) and enter your API key.",
        )

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


# ---------------------------------------------------------------------------
# Pydantic models for new Jesse API endpoints
# ---------------------------------------------------------------------------

class FeedbackRequest(BaseModel):
    message_id: str = Field(..., description="ID of the assistant message being rated")
    rating: str = Field(..., description="'thumbs_up' or 'thumbs_down'")
    correction: Optional[str] = Field(None, description="Optional corrected answer for learning")
    model: Optional[str] = Field(None, description="Model that produced the response")


class DocumentStoreRequest(BaseModel):
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document text content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional key/value metadata")


class DocumentQueryRequest(BaseModel):
    query: str = Field(..., description="Semantic search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")


# ---------------------------------------------------------------------------
# Feedback endpoint — jesse-prod learns from right/wrong ratings
# ---------------------------------------------------------------------------

@app.post("/api/feedback")
async def submit_feedback(req: FeedbackRequest, request: Request) -> Dict[str, Any]:
    """Mark an answer right (thumbs_up) or wrong (thumbs_down), with an optional correction.
    This trains jesse-prod to improve over time."""
    header_key = extract_request_api_key(request)
    active_bot = get_bot(api_key_override=header_key)
    if req.rating not in ("thumbs_up", "thumbs_down"):
        raise HTTPException(status_code=400, detail="rating must be 'thumbs_up' or 'thumbs_down'")
    try:
        result = active_bot.client.submit_feedback(
            message_id=req.message_id,
            rating=req.rating,
            correction=req.correction,
            model=req.model,
        )
        logger.info("Feedback submitted: %s for message %s", req.rating, req.message_id)
        return {"status": "ok", "detail": result}
    except Exception as exc:
        logger.warning("Feedback submission error: %s", exc)
        # Return a graceful degradation — Jesse API may not support feedback on all keys
        return {"status": "degraded", "detail": str(exc)}


# ---------------------------------------------------------------------------
# Memory endpoints — view and erase what Jesse remembers
# ---------------------------------------------------------------------------

@app.get("/api/memory")
async def get_memory(request: Request) -> Dict[str, Any]:
    """Retrieve all facts Jesse remembers for this API key."""
    header_key = extract_request_api_key(request)
    active_bot = get_bot(api_key_override=header_key)
    try:
        result = active_bot.client.get_memory()
        return {"status": "ok", "data": result}
    except Exception as exc:
        logger.warning("Memory fetch error: %s", exc)
        return {"status": "degraded", "data": {}, "detail": str(exc)}


@app.delete("/api/memory")
async def delete_memory(request: Request) -> Dict[str, Any]:
    """Erase everything Jesse remembers for this API key."""
    header_key = extract_request_api_key(request)
    active_bot = get_bot(api_key_override=header_key)
    try:
        result = active_bot.client.delete_memory()
        logger.info("Memory erased for API key")
        return {"status": "ok", "detail": result}
    except Exception as exc:
        logger.warning("Memory delete error: %s", exc)
        return {"status": "degraded", "detail": str(exc)}


# ---------------------------------------------------------------------------
# Document endpoints — store, list, and search documents
# ---------------------------------------------------------------------------

@app.post("/api/documents")
async def store_document(req: DocumentStoreRequest, request: Request) -> Dict[str, Any]:
    """Store a document so Jesse can retrieve it in future conversations."""
    header_key = extract_request_api_key(request)
    active_bot = get_bot(api_key_override=header_key)
    if not req.title.strip() or not req.content.strip():
        raise HTTPException(status_code=400, detail="title and content must not be empty")
    try:
        result = active_bot.client.store_document(
            title=req.title,
            content=req.content,
            metadata=req.metadata,
        )
        logger.info("Document stored: %s", req.title)
        return {"status": "ok", "detail": result}
    except Exception as exc:
        logger.warning("Document store error: %s", exc)
        return {"status": "degraded", "detail": str(exc)}


@app.get("/api/documents")
async def list_documents(request: Request) -> Dict[str, Any]:
    """List all stored documents for this API key."""
    header_key = extract_request_api_key(request)
    active_bot = get_bot(api_key_override=header_key)
    try:
        result = active_bot.client.list_documents()
        return {"status": "ok", "data": result}
    except Exception as exc:
        logger.warning("Document list error: %s", exc)
        return {"status": "degraded", "data": {}, "detail": str(exc)}


@app.post("/api/documents/query")
async def query_documents(req: DocumentQueryRequest, request: Request) -> Dict[str, Any]:
    """Semantic search over stored documents."""
    header_key = extract_request_api_key(request)
    active_bot = get_bot(api_key_override=header_key)
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")
    try:
        result = active_bot.client.query_documents(query=req.query, top_k=req.top_k)
        return {"status": "ok", "data": result}
    except Exception as exc:
        logger.warning("Document query error: %s", exc)
        return {"status": "degraded", "data": {}, "detail": str(exc)}


# ---------------------------------------------------------------------------
# Static files + index
# ---------------------------------------------------------------------------

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

