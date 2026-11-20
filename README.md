# FocusFlow AI

Run the frontend and backend as separate services during local development.
Backend setup and run instructions are in [Backend/README.md](Backend/README.md).

## Backend stack

- **API:** Python, FastAPI, Uvicorn, and Pydantic.
- **Data:** PostgreSQL with pgvector for application data and document embeddings; Redis for authentication rate limits.
- **Authentication:** JWT access tokens, Argon2 password hashing, email verification and password reset through SMTP.
- **AI:** OpenAI-compatible chat API and FastEmbed sentence embeddings.
- **Document processing:** PDF and Word extraction, text chunking and retrieval, plus image OCR through Tesseract and Pillow.
- **Configuration:** Environment variables loaded from `Backend/.env`; install Python packages with `Backend/requirements.txt`.

Image OCR also requires the Tesseract executable on the host. PostgreSQL, Redis, SMTP, and AI provider credentials are configured separately for local development.
