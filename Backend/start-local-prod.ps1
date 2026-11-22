$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (-not (Test-Path (Join-Path $PSScriptRoot ".env"))) {
    throw "Backend/.env is missing. Create it from .env.example and set your local database and JWT settings."
}

$jwtSecret = $env:JWT_SECRET
if (-not $jwtSecret) {
    foreach ($line in Get-Content (Join-Path $PSScriptRoot ".env")) {
        if ($line -match '^\s*JWT_SECRET\s*=\s*(.*?)\s*$') {
            $jwtSecret = $Matches[1].Trim('"').Trim("'")
            break
        }
    }
}
if (-not $jwtSecret -or $jwtSecret.Length -lt 32 -or $jwtSecret -eq "replace-with-a-long-random-secret") {
    throw "Set a private JWT_SECRET of at least 32 characters in Backend/.env before starting the local production-style API."
}

$postgres = Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet -WarningAction SilentlyContinue
if (-not $postgres) {
    throw "PostgreSQL is not reachable at localhost:5432. Start your local PostgreSQL service first."
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is required to start local Redis. Install and start Docker Desktop, then run this script again."
}

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker is installed but its engine is not running. Start Docker Desktop, then run this script again."
}

docker compose -f compose.redis.yml up -d --wait redis
if ($LASTEXITCODE -ne 0) {
    throw "Could not start Redis. Check Docker Desktop and try again."
}

python -m uvicorn main:app --host 127.0.0.1 --port 8000
exit $LASTEXITCODE
