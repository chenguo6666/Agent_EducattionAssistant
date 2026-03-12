$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

Set-Location (Join-Path $repoRoot "frontend")
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}
npm run build

Set-Location (Join-Path $repoRoot "backend")
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

if (-not (Test-Path ".venv\\Scripts\\python.exe")) {
    throw "Backend virtual environment not found. Create backend\\.venv first."
}

Write-Output "Production build complete."
