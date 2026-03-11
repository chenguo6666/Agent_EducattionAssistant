$ErrorActionPreference = "Stop"

function Wait-ForUrl {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 45
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -Uri $Url -UseBasicParsing | Out-Null
            return
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }

    throw "Service timeout: $Url"
}

Wait-ForUrl -Url "http://127.0.0.1:8000/health"
Wait-ForUrl -Url "http://127.0.0.1:5173"

$suffix = Get-Date -Format "HHmmss"
$phoneSuffix = "{0:D10}" -f (Get-Random -Minimum 0 -Maximum 10000000000)
$registerBody = @{
    username = "student_live_$suffix"
    phone = "1$phoneSuffix"
    password = "123456"
} | ConvertTo-Json

$registerResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/register" -Method Post -ContentType "application/json" -Body $registerBody
$loginBody = @{
    account = "student_live_$suffix"
    password = "123456"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/login" -Method Post -ContentType "application/json" -Body $loginBody
$headers = @{
    Authorization = "Bearer $($loginResponse.token)"
}

$meResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/me" -Headers $headers -Method Get
$chatBody = @{
    message = "Please summary this history lesson and generate 5 quiz questions about the Industrial Revolution."
} | ConvertTo-Json

$chatResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/chat/execute" -Headers $headers -Method Post -ContentType "application/json" -Body $chatBody

[pscustomobject]@{
    RegisterMessage = $registerResponse.message
    LoginUser = $loginResponse.user.username
    MeUser = $meResponse.username
    ChatIntent = $chatResponse.intent
    ChatStatus = $chatResponse.status
    QuizCount = @($chatResponse.result.quiz).Count
    TimelineCount = @($chatResponse.timeline).Count
} | Format-List
