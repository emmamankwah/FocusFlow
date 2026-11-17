import logging
import os
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
from app.authentication.security.rate_limit import RateLimitUnavailable

load_dotenv(Path(__file__).resolve().parent / ".env")

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if rag_config.WARMUP:
        try:
            rag_embeddings.warmup()
        except Exception:
            logger.exception("RAG embedding warm-up failed")
    yield

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
        reload=True,
    )
