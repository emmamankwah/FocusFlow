$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is required for the bundled Redis service. Install and start Docker Desktop, then run this script again."
}

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker is installed but its engine is not running. Start Docker Desktop, then run this script again."
}

docker compose -f compose.redis.yml up -d --wait redis
if ($LASTEXITCODE -ne 0) {
    throw "Could not start Redis. Check Docker Desktop and try again."
}

python -m uvicorn main:app --reload
exit $LASTEXITCODE
