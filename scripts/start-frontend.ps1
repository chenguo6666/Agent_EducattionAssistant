$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $repoRoot "frontend"
$envExample = Join-Path $frontendDir ".env.example"
$envFile = Join-Path $frontendDir ".env"

if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    throw "Frontend dependencies not found. Run npm install in frontend first."
}

if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
    Copy-Item $envExample $envFile
}

Set-Location $frontendDir
npm run dev -- --host 127.0.0.1 --port 5173
