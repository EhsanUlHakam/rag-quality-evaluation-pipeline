$ErrorActionPreference = "Stop"
$projectDirectory = Split-Path -Parent $PSScriptRoot
Set-Location $projectDirectory

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

docker.exe compose up -d --build
if ($LASTEXITCODE -ne 0) { throw "Docker Compose startup failed." }

Write-Host "Waiting for the RAG evaluation service..." -ForegroundColor Cyan
for ($attempt = 1; $attempt -le 30; $attempt++) {
    try {
        $health = Invoke-RestMethod "http://localhost:8003/health" -TimeoutSec 2
        if ($health.status -eq "ok") { break }
    }
    catch { Start-Sleep -Seconds 2 }
}

Invoke-RestMethod "http://localhost:8003/health" | ConvertTo-Json
Write-Host "RAG API: http://localhost:8003/docs" -ForegroundColor Green
Write-Host "n8n:     http://localhost:5681" -ForegroundColor Green
