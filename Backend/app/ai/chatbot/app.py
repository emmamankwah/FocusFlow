from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import chat_service, models

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


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat")
def chat(request: models.ChatRequest) -> models.ChatResponse:
    reply = chat_service.get_reply(
        messages=request.messages,
        context=request.context,
    )
    return models.ChatResponse(reply=reply)
