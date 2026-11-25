import logging
import os
import subprocess
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ai.chatbot.app import router as ai_router
from app.ai.rag import config as rag_config
from app.ai.rag import embeddings as rag_embeddings
from app.ai.rag.routes.rag import router as rag_router
from app.authentication.routes.auth.auth_user import router as auth_router
from app.ai.planner.router import router as planner_router
from app.authentication.security.rate_limit import (
    RateLimitUnavailable,
    close_rate_limiters,
)

load_dotenv(Path(__file__).resolve().parent / ".env")

logger = logging.getLogger(__name__)


def _watch_session(launcher_pid: int) -> None:
    while True:
        time.sleep(0.5)
        try:
            os.kill(launcher_pid, 0)
        except OSError:
            logger.warning("Session process %s exited; shutting down.", launcher_pid)
            os._exit(0)


_launcher_pid = os.getenv("FOCUSFLOW_LAUNCHER_PID")
if _launcher_pid and _launcher_pid.isdigit():
    threading.Thread(
        target=_watch_session,
        args=(int(_launcher_pid),),
        name="focusflow-session-watch",
        daemon=True,
    ).start()


def _start_local_redis() -> None:
    enabled = os.getenv("LOCAL_START_REDIS", "").strip().lower()
    if enabled not in {"1", "true", "yes", "on"}:
        return

    compose_file = Path(__file__).resolve().parent / "compose.redis.yml"
    try:
        subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "up", "-d", "--wait", "redis"],
            check=True,
            timeout=90,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "LOCAL_START_REDIS is enabled, but Docker is not installed or available on PATH."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Timed out while starting local Redis with Docker Compose.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Could not start local Redis. Make sure Docker Desktop is running."
        ) from exc

    logger.info("Local Redis is running.")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _start_local_redis()
    if rag_config.WARMUP:
        try:
            rag_embeddings.warmup()
        except Exception:
            logger.exception("RAG embedding warm-up failed")
    try:
        yield
    finally:
        logger.info("FocusFlow API is shutting down")
        close_rate_limiters()

APP_NAME = os.getenv("APP_NAME", "FocusFlow")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app = FastAPI(title=APP_NAME, lifespan=lifespan)


@app.exception_handler(RateLimitUnavailable)
async def rate_limit_unavailable_handler(_request, exc: RateLimitUnavailable):
    return JSONResponse(
        status_code=503,
        content={"error": str(exc)},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    # The API authenticates with Bearer tokens, not cookies.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(ai_router, prefix="/ai")
app.include_router(rag_router)
app.include_router(planner_router, prefix="/ai/planner")


@app.get("/")
def home():
    return {"message": "FocusFlow API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
