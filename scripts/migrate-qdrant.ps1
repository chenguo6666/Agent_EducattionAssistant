$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendDir ".venv\\Scripts\\python.exe"

if (-not (Test-Path $venvPython)) {
    throw "Backend virtual environment not found. Create backend\\.venv first."
}

Set-Location $backendDir
$env:VECTOR_STORE_PROVIDER = if ($env:VECTOR_STORE_PROVIDER) { $env:VECTOR_STORE_PROVIDER } else { "qdrant" }
$env:VECTOR_STORE_URL = if ($env:VECTOR_STORE_URL) { $env:VECTOR_STORE_URL } else { "http://127.0.0.1:6333" }
$env:VECTOR_STORE_COLLECTION = if ($env:VECTOR_STORE_COLLECTION) { $env:VECTOR_STORE_COLLECTION } else { "education_agent_chunks" }

& $venvPython ".\\migrate_qdrant.py"
