# FocusFlow Backend

## Install

From the backend directory, install the full application requirements:

```powershell
python -m pip install -r requirements.txt
```

The root requirements include the RAG dependencies. The equivalent RAG-specific
install is `python -m pip install -r app/ai/rag/requirements.txt`.

### Image OCR

Image uploads use `pytesseract` and Pillow, which are installed with the Python
requirements. `pytesseract` also needs the separate Tesseract OCR executable on
the host machine. Install Tesseract for your operating system and ensure the
`tesseract` command is available on `PATH`; check with:

```powershell
tesseract --version
```

If the command is not found, image ingestion will fail until Tesseract is
installed or added to `PATH`. Text, PDF, and Word ingestion do not use OCR.

### Embedding model

The FastEmbed model is downloaded on first use and cached under `.cache/fastembed`
by default. The first document ingestion can therefore take longer and needs
network access; later runs reuse the cached model.

## Run

### Local production-style run

Keep using your installed PostgreSQL service. Make sure `.env` has the local
PostgreSQL settings and a private `JWT_SECRET` (see `.env.example` for the
variable names), then start Docker Desktop. From this directory, run:

```powershell
./start-local-prod.ps1
```

This starts only Redis in Docker, checks that PostgreSQL is listening on port
5432, and runs Uvicorn on `127.0.0.1:8000` without development reload mode.
The backend reads PostgreSQL and Redis connection settings from `.env`. Redis
stays running if the API process stops; stop it with `./stop-dev.ps1`.

### Development run

For development with automatic reload, use:

```powershell
./start-dev.ps1
```

This also starts Redis from `compose.redis.yml` before running the API.
