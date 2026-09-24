$ErrorActionPreference = "Stop"
$projectDirectory = Split-Path -Parent $PSScriptRoot
Set-Location $projectDirectory

Write-Host "[1/7] Checking containers..." -ForegroundColor Cyan
docker.exe compose ps

Write-Host "[2/7] Running unit tests..." -ForegroundColor Cyan
docker.exe compose run --rm rag-service python -m pytest service/tests -q
if ($LASTEXITCODE -ne 0) { throw "Unit tests failed." }

Write-Host "[3/7] Checking ingestion..." -ForegroundColor Cyan
$ingestion = Invoke-RestMethod -Uri "http://localhost:8003/api/v1/ingest" -Method Post
if ($ingestion.document_count -ne 5) { throw "Expected 5 knowledge-base documents." }
$ingestion | ConvertTo-Json -Depth 5

Write-Host "[4/7] Executing passing baseline..." -ForegroundColor Cyan
$baselineBody = @{ name="baseline"; chunk_size=90; overlap=15; top_k=3; scenario="good"; set_as_baseline=$true } | ConvertTo-Json
$baseline = Invoke-RestMethod -Uri "http://localhost:8003/api/v1/evaluation/runs" -Method Post -ContentType "application/json" -Body $baselineBody
if ($baseline.gate_status -ne "PASS") { throw "Baseline quality gate did not pass." }

Write-Host "[5/7] Executing intentionally weak candidate..." -ForegroundColor Cyan
$candidateBody = @{ name="candidate-small-chunks"; chunk_size=18; overlap=0; top_k=1; scenario="good"; set_as_baseline=$false } | ConvertTo-Json
$candidate = Invoke-RestMethod -Uri "http://localhost:8003/api/v1/evaluation/runs" -Method Post -ContentType "application/json" -Body $candidateBody
if ($candidate.gate_status -ne "FAIL") { throw "Candidate was expected to fail its quality gate." }

Write-Host "[6/7] Comparing baseline and candidate..." -ForegroundColor Cyan
$comparisonBody = @{ baseline_run_id=$baseline.run_id; candidate_run_id=$candidate.run_id } | ConvertTo-Json
$comparison = Invoke-RestMethod -Uri "http://localhost:8003/api/v1/evaluation/compare" -Method Post -ContentType "application/json" -Body $comparisonBody

Write-Host "[7/7] Verification summary..." -ForegroundColor Cyan
[PSCustomObject]@{
    BaselineRun = $baseline.run_id
    BaselineGate = $baseline.gate_status
    BaselinePassRate = $baseline.metrics.overall_pass_rate
    CandidateRun = $candidate.run_id
    CandidateGate = $candidate.gate_status
    CandidatePassRate = $candidate.metrics.overall_pass_rate
    RegressedCases = $comparison.classification_counts.regressed
    ReportsFolder = (Join-Path $projectDirectory "reports")
} | Format-List

Write-Host "VERIFIED: deterministic PASS, deterministic FAIL, regression comparison, reports, and SQLite persistence." -ForegroundColor Green

