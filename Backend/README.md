# FocusFlow Backend

## Database schema updates

For an existing database, apply numbered SQL updates from `schema` in order.
The `schema/003_user_type.sql` migration adds the signup user type to verified
and pending accounts. Fresh databases should be initialized from
`schema/000_auth.sql` and the remaining schema files.

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
variable names). From this directory, run:

```powershell
./start-local-prod.ps1
```

The script starts Docker Desktop from the terminal if its engine is not already
running, checks that PostgreSQL is listening on port 5432, and runs Uvicorn on
`127.0.0.1:8000` without development reload mode. FastAPI startup reads
`LOCAL_START_REDIS=true` from `.env`, starts Redis with Docker Compose, and
waits for it before serving requests. Redis stays running if the API process
stops; stop it with `./stop-dev.ps1`.
The same automatic Redis startup applies if you launch the backend directly
with `python main.py` or `python -m uvicorn main:app` from the `Backend`
directory. Docker Desktop’s engine must be running first.

The start scripts bind Uvicorn to a Windows job object and pass the session
PID to the backend, so children that escape the job also exit. Pressing Ctrl+C,
closing the terminal, or the script exiting or being killed terminates the
whole process tree and releases port 8000; no separate cleanup is needed after
a normal shutdown. If an older session left a stale
listener behind, run `./clean-port8000.ps1` to stop the server process and any
orphaned workers and free port 8000 (`./clean-port8000.ps1 -WhatIf` previews
the targets). Redis keeps running independently; stop it with `./stop-dev.ps1`.

### Development run

For development with automatic reload, use:

```powershell
./start-dev.ps1
```

This uses the same setup and starts Docker Desktop from the terminal if needed,
but runs Uvicorn with automatic reload. The reload subprocess belongs to the
same job object, so it is stopped together with the server when the session
ends.
