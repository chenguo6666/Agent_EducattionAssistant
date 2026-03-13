$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$toolsDir = Join-Path $repoRoot ".runtime\tools"
$publicDir = Join-Path $repoRoot ".runtime\public"
$cloudflaredPath = Join-Path $toolsDir "cloudflared.exe"
$logPath = Join-Path $publicDir "cloudflared.log"

New-Item -ItemType Directory -Force $toolsDir | Out-Null
New-Item -ItemType Directory -Force $publicDir | Out-Null

if (-not (Test-Path $cloudflaredPath)) {
    Write-Output "Downloading cloudflared ..."
    Invoke-WebRequest `
        -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" `
        -OutFile $cloudflaredPath
}

Get-Process -Name cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
if (Test-Path $logPath) {
    Remove-Item $logPath -Force
}

Write-Output "Starting public tunnel for http://127.0.0.1:8000 ..."
Start-Process `
    -FilePath $cloudflaredPath `
    -ArgumentList "tunnel --url http://127.0.0.1:8000 --logfile `"$logPath`"" `
    -WindowStyle Hidden

$url = $null
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Seconds 1

    if (-not (Test-Path $logPath)) {
        continue
    }

    $match = Select-String -Path $logPath -Pattern "https://[a-z0-9-]+\.trycloudflare\.com" | Select-Object -Last 1
    if ($match) {
        $url = $match.Matches.Value
        break
    }
}

if (-not $url) {
    throw "Cloudflare tunnel started, but no public URL was found in $logPath"
}

Write-Output ""
Write-Output "Public URL:"
Write-Output $url
