$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot
docker compose -f compose.redis.yml stop redis
exit $LASTEXITCODE
