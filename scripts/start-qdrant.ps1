$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $repoRoot ".runtime"
$qdrantDataDir = Join-Path $runtimeDir "qdrant"
$containerName = "education-agent-qdrant"
$imageName = if ($env:QDRANT_IMAGE) { $env:QDRANT_IMAGE } else { "qdrant/qdrant:latest" }

function Wait-ForQdrant {
    param([int]$TimeoutSeconds = 45)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:6333/collections" | Out-Null
            return
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }

    throw "Qdrant startup timed out."
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is required to run Qdrant locally. Install Docker Desktop first."
}

New-Item -ItemType Directory -Force $runtimeDir | Out-Null
New-Item -ItemType Directory -Force $qdrantDataDir | Out-Null

$existing = docker ps -a --filter "name=^/${containerName}$" --format "{{.Names}}"
if ($existing -contains $containerName) {
    $running = docker ps --filter "name=^/${containerName}$" --format "{{.Names}}"
    if ($running -contains $containerName) {
        Wait-ForQdrant
        Write-Output "Qdrant is already running at http://127.0.0.1:6333"
        exit 0
    }

    docker start $containerName | Out-Null
    Wait-ForQdrant
    Write-Output "Started existing Qdrant container: $containerName"
    exit 0
}

docker run -d `
    --name $containerName `
    -p 6333:6333 `
    -p 6334:6334 `
    -v "${qdrantDataDir}:/qdrant/storage" `
    $imageName | Out-Null

Wait-ForQdrant
Write-Output "Started Qdrant container: $containerName"
Write-Output "Qdrant URL: http://127.0.0.1:6333"
