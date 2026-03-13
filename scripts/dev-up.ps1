$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $repoRoot ".runtime"
$logsDir = Join-Path $runtimeDir "logs"
$backendPidFile = Join-Path $runtimeDir "backend.pid"
$frontendPidFile = Join-Path $runtimeDir "frontend.pid"

New-Item -ItemType Directory -Force $runtimeDir | Out-Null
New-Item -ItemType Directory -Force $logsDir | Out-Null

function Stop-ExistingProcess {
    param([string]$PidFile)

    if (-not (Test-Path $PidFile)) {
        return
    }

    $pidValue = Get-Content $PidFile -Raw
    if ([string]::IsNullOrWhiteSpace($pidValue)) {
        Remove-Item $PidFile -Force
        return
    }

    $process = Get-Process -Id ([int]$pidValue) -ErrorAction SilentlyContinue
    if ($null -ne $process) {
        & taskkill /PID $process.Id /T /F | Out-Null
    }

    Remove-Item $PidFile -Force
}

Stop-ExistingProcess -PidFile $backendPidFile
Stop-ExistingProcess -PidFile $frontendPidFile

$backendScript = Join-Path $repoRoot "scripts\\start-backend.ps1"
$frontendScript = Join-Path $repoRoot "scripts\\start-frontend.ps1"
$backendLog = Join-Path $logsDir "backend.out.log"
$backendErrLog = Join-Path $logsDir "backend.err.log"
$frontendLog = Join-Path $logsDir "frontend.out.log"
$frontendErrLog = Join-Path $logsDir "frontend.err.log"

$backendProcess = Start-Process powershell -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $backendScript
) -WorkingDirectory $repoRoot -RedirectStandardOutput $backendLog -RedirectStandardError $backendErrLog -PassThru

$frontendProcess = Start-Process powershell -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $frontendScript
) -WorkingDirectory $repoRoot -RedirectStandardOutput $frontendLog -RedirectStandardError $frontendErrLog -PassThru

$backendProcess.Id | Set-Content $backendPidFile
$frontendProcess.Id | Set-Content $frontendPidFile

Write-Output "Backend PID: $($backendProcess.Id)"
Write-Output "Frontend PID: $($frontendProcess.Id)"
Write-Output "Backend URL: http://127.0.0.1:8000"
Write-Output "Frontend URL: http://127.0.0.1:5173"
Write-Output "Backend stdout: $backendLog"
Write-Output "Backend stderr: $backendErrLog"
Write-Output "Frontend stdout: $frontendLog"
Write-Output "Frontend stderr: $frontendErrLog"
