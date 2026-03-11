$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Output "Starting public tunnel for http://127.0.0.1:8000 ..."
npx localtunnel --port 8000
