$ErrorActionPreference = "Stop"
$runs = Invoke-RestMethod "http://localhost:8003/api/v1/evaluation/runs"
$runs |
    Select-Object run_id, name, created_at, gate_status, is_baseline,
        @{Name="pass_rate";Expression={$_.metrics.overall_pass_rate}},
        @{Name="fact_coverage";Expression={$_.metrics.fact_coverage}} |
    Format-Table -AutoSize

Write-Host "`nSQLite tables:" -ForegroundColor Cyan
$pythonCode = @'
import sqlite3
c = sqlite3.connect("/app/data/rag-evaluation.db")
print(c.execute("select name from sqlite_master where type='table' order by name").fetchall())
'@
docker.exe compose exec rag-service python -c $pythonCode
