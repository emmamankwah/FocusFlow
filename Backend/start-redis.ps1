# Backend/start-redis.ps1
# Starts the FocusFlow Redis container. Safe to run when already running.
param()
Set-Location $PSScriptRoot
docker compose -f compose.redis.yml up -d --wait redis
Write-Host "Redis is ready at redis://127.0.0.1:6379"
