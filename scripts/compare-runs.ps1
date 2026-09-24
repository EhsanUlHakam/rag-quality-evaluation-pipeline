$ErrorActionPreference = "Stop"
$body = @{
    baseline_name = "baseline"
    candidate_name = "candidate-small-chunks"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8003/api/v1/evaluation/compare" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body |
    ConvertTo-Json -Depth 10
