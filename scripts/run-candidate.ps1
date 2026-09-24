$ErrorActionPreference = "Stop"
$body = @{
    name = "candidate-small-chunks"
    chunk_size = 18
    overlap = 0
    top_k = 1
    scenario = "good"
    set_as_baseline = $false
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:8003/api/v1/evaluation/runs" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$response | Select-Object run_id, name, gate_status, ci_exit_code, metrics, violations | ConvertTo-Json -Depth 10
Write-Host "Candidate gate: $($response.gate_status)" -ForegroundColor Cyan
Write-Host "A non-zero exit code is expected when the quality gate detects regression." -ForegroundColor Yellow
exit $response.ci_exit_code
