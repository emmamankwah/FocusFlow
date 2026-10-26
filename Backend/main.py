from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth.auth_user import router as auth_router
from settings.env import validate_settings

# Fail at startup, with one readable message, instead of on the first request.
validate_settings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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