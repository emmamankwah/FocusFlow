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

For local development on Windows, install and start Docker Desktop, then start
the API and its Redis rate-limit service together from this directory:

```powershell
./start-dev.ps1
```

The script starts Redis from `compose.redis.yml` and then runs the API. Redis
stays running if the API process stops; stop it with `./stop-dev.ps1`. The
default backend URL (`redis://localhost:6379/0`) connects to this local Redis
container. You can still run the API directly with `python -m uvicorn
main:app --reload` when Redis is already running.
