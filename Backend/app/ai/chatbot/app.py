"""AI chatbot routes.

The same routes are exposed two ways:

- ``router`` is mounted by ``main.py`` at ``/ai``, so the running API serves
  ``GET /ai/health`` and ``POST /ai/chat``.
- ``app`` keeps the chatbot runnable on its own:
  ``uvicorn app.ai.chatbot.app:app``.
"""

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.authentication.security.current_user import get_current_user_id

from . import chat_service, models

router = APIRouter(tags=["ai"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/chat")
def chat(
    request: models.ChatRequest,
    _user_id: int = Depends(get_current_user_id),
) -> models.ChatResponse:
    reply = chat_service.get_reply(
        messages=request.messages,
        context=request.context,
    )
    return models.ChatResponse(reply=reply)


app = FastAPI(
    title="AI Chatbot API",
    version="0.1.0",
    description="AI chatbot backend with optional grounding in document context.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
