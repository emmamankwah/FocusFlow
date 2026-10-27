import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth.auth_user import router as auth_router

load_dotenv(Path(__file__).resolve().parent / ".env")

APP_NAME = os.getenv("APP_NAME", "FocusFlow")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    # The API authenticates with Bearer tokens, not cookies.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "FocusFlow API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)