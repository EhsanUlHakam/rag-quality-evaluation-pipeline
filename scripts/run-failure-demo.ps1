$ErrorActionPreference = "Stop"
$body = @{
    name = "controlled-failure-demo"
    chunk_size = 90
    overlap = 15
    top_k = 3
    scenario = "good"
    scenario_overrides = @{
        "rag-012" = "hallucination"
        "rag-001" = "missing_citation"
        "rag-008" = "timeout"
    }
    set_as_baseline = $false
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod `
    -Uri "http://localhost:8003/api/v1/evaluation/runs" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$failedCases = $response.results |
    Where-Object { -not $_.metrics.case_pass } |
    Select-Object @{Name="case_id";Expression={$_.case.id}},
        @{Name="scenario";Expression={$_.response.parameters.scenario}},
        @{Name="citation_validity";Expression={$_.metrics.citation_validity}},
        @{Name="groundedness";Expression={$_.metrics.groundedness}},
        @{Name="error";Expression={$_.response.error.code}}

$response | Select-Object run_id, gate_status, metrics, violations | ConvertTo-Json -Depth 10
$failedCases | Format-Table -AutoSize
Write-Host "The failures above are intentional evidence that the evaluator catches controlled faults." -ForegroundColor Yellow
exit $response.ci_exit_code
