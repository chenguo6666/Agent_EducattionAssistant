$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendDir ".venv\\Scripts\\python.exe"
$envExample = Join-Path $backendDir ".env.example"
$envFile = Join-Path $backendDir ".env"

if (-not (Test-Path $venvPython)) {
    throw "Backend virtual environment not found. Create backend\\.venv and install requirements first."
}

if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
    Copy-Item $envExample $envFile
}

Set-Location $backendDir
& $venvPython -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
