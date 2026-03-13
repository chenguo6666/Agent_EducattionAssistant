$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $repoRoot ".runtime"
$pidFiles = @(
    (Join-Path $runtimeDir "backend.pid"),
    (Join-Path $runtimeDir "frontend.pid")
)

foreach ($pidFile in $pidFiles) {
    if (-not (Test-Path $pidFile)) {
        continue
    }

    $pidValue = Get-Content $pidFile -Raw
    if (-not [string]::IsNullOrWhiteSpace($pidValue)) {
        $process = Get-Process -Id ([int]$pidValue) -ErrorAction SilentlyContinue
        if ($null -ne $process) {
            & taskkill /PID $process.Id /T /F | Out-Null
            Write-Output "Stopped PID $($process.Id)"
        }
    }

    Remove-Item $pidFile -Force
}
