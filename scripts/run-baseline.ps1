$ErrorActionPreference = "Stop"
$body = @{
    name = "baseline"
    chunk_size = 90
    overlap = 15
    top_k = 3
    scenario = "good"
    set_as_baseline = $true
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:8003/api/v1/evaluation/runs" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$response | Select-Object run_id, name, gate_status, ci_exit_code, metrics, violations | ConvertTo-Json -Depth 10
Write-Host "Baseline gate: $($response.gate_status)" -ForegroundColor Cyan
exit $response.ci_exit_code
