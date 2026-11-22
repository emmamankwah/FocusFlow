param([switch]$Reload)

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

$docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) {
    throw "Docker CLI is not available on PATH. Install Docker Desktop, then open a new terminal."
}

docker info *> $null
$engineRunning = $LASTEXITCODE -eq 0
if (-not $engineRunning) {
    $dockerDesktop = Join-Path $env:ProgramFiles "Docker\Docker\Docker Desktop.exe"
    if (-not (Test-Path $dockerDesktop)) {
        throw "Docker Desktop was not found at the default install path: $dockerDesktop"
    }

    if (-not (Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue)) {
        Start-Process -FilePath $dockerDesktop
    }

    Write-Host "Waiting for Docker Desktop to start..."
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        Start-Sleep -Seconds 2
        docker info *> $null
        if ($LASTEXITCODE -eq 0) {
            $engineRunning = $true
            break
        }
    }
}

if (-not $engineRunning) {
    throw "Docker Desktop did not become ready within two minutes. Open it and check its status, then retry."
}

$uvicornArgs = @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000")
if ($Reload) {
    $uvicornArgs += "--reload"
}

$python = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Python was not found. Create the Backend virtual environment and install requirements.txt."
    }
    $python = $pythonCommand.Source
}

& $python @uvicornArgs
exit $LASTEXITCODE
