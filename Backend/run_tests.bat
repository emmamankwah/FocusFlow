@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m pytest test\test_connections.py test\test_ingest.py test\test_rag.py test\test_auth.py test\test_prompts.py -v --tb=short 2>&1
