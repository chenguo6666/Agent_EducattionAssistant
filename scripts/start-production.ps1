$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendDir ".venv\\Scripts\\python.exe"

if (-not (Test-Path $venvPython)) {
    throw "Backend virtual environment not found. Create backend\\.venv first."
}

Set-Location $repoRoot
powershell -ExecutionPolicy Bypass -File ".\\scripts\\build-production.ps1"

Set-Location $backendDir
& $venvPython -m uvicorn app.main:app --host 0.0.0.0 --port 8000
