@echo off
setlocal

rem Change to the directory where this batch file resides
cd /d "%~dp0"

rem ------------------------------------------------------------
rem Ensure the Frontend dependencies are installed
rem ------------------------------------------------------------
if not exist Frontend\node_modules (
    echo Installing frontend dependencies... 
    pushd Frontend
    npm install
    popd
) else (
    echo Frontend dependencies already present.
)

rem ------------------------------------------------------------
rem Launch the LivePreview MCP using the system Python interpreter
rem (no virtual‑environment activation – the script works with the
rem default Python that the sandbox provides).
rem ------------------------------------------------------------
python LivePreviewMCP\preview_server.py
