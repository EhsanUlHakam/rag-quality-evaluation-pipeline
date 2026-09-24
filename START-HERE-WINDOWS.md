# Start Here on Windows

This guide assumes no Bash knowledge.

## 1. Extract the ZIP

Extract the project to:

```text
C:\Users\YOUR_NAME\Projects\rag-quality-evaluation-pipeline
```

Do not run commands from `C:\Windows\System32`.

## 2. Start Docker Desktop

Open Docker Desktop and wait until the bottom-left status says **Engine running**.

## 3. Open PowerShell in the project

```powershell
Set-Location "$env:USERPROFILE\Projects\rag-quality-evaluation-pipeline"
```

Confirm the location:

```powershell
Get-Location
Get-ChildItem
```

## 4. Check ports

```powershell
Get-NetTCPConnection -State Listen -LocalPort 5681,8003 -ErrorAction SilentlyContinue
```

No output means the ports are available. If another application owns either port, stop it or change the corresponding value after copying `.env.example` to `.env`.

## 5. Start the system

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\start-demo.ps1
```

The first build downloads container images and Python dependencies. Later starts reuse them.

## 6. Verify health

```powershell
Invoke-RestMethod "http://localhost:8003/health" | ConvertTo-Json
Invoke-RestMethod "http://localhost:5681/healthz" | ConvertTo-Json
```

## 7. Run the complete deterministic proof

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\verify-first-run.ps1
```

This performs unit tests, ingestion, a passing baseline, an intentionally failing candidate, regression comparison, report generation, and persistence checks.

## 8. Import n8n

1. Open <http://localhost:5681>.
2. Create the local owner account if this is a new n8n data volume.
3. Choose **Import from File**.
4. Select `n8n\rag-evaluation-workflow.json`.
5. Select **Execute workflow**.
6. Open the final **Evaluation Summary** node.

Do not replace `rag-service` with `localhost` inside n8n. Both containers share a Docker network, and `rag-service` is the service DNS name.

## 9. Open generated evidence

```powershell
Get-ChildItem .\reports | Sort-Object LastWriteTime -Descending
```

Open the newest HTML report:

```powershell
$report = Get-ChildItem .\reports\*.html | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Start-Process $report.FullName
```

## 10. Stop and restart

Stop containers without deleting data:

```powershell
docker.exe compose stop
```

Restart:

```powershell
docker.exe compose up -d
```

Clean shutdown while preserving named volumes:

```powershell
docker.exe compose down
```

Do not add `-v` unless you intentionally want to delete the n8n and SQLite volumes.
