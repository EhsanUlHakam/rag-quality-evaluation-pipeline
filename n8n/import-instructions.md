# n8n Import and Execution

1. Start the project with `powershell -ExecutionPolicy Bypass -File .\scripts\start-demo.ps1`.
2. Open <http://localhost:5681> and create the local n8n owner account if prompted.
3. Select **Import from File** and choose `n8n/rag-evaluation-workflow.json`.
4. Open **Run Configuration** to review `chunk_size`, `overlap`, `top_k`, and `scenario`.
5. Select **Execute workflow**.
6. Inspect **Evaluation Summary** for the run ID, metrics, gate, violations, and report paths.

No credentials or community nodes are required. The workflow uses the Compose service name `rag-service`, because `localhost` inside the n8n container would refer to n8n itself.

## Manual-build fallback

Create and connect these nodes in order:

1. Manual Trigger
2. Code — produce run configuration
3. HTTP Request — GET `http://rag-service:8003/api/v1/dataset`
4. Code — return one n8n item per dataset case
5. HTTP Request — POST each item to `/api/v1/rag/query`
6. HTTP Request — POST each response to `/api/v1/evaluation/case`
7. Code in **Run Once for All Items** mode — collect evaluated results
8. HTTP Request — POST them to `/api/v1/evaluation/runs/from-results`
9. Code — expose the summary

## Important expressions

- RAG request body: `{{ JSON.stringify({ question: $json.case.question, case_id: $json.case.id, chunk_size: $json.chunk_size, overlap: $json.overlap, top_k: $json.top_k, scenario: $json.scenario }) }}`
- Case evaluation body: `{{ JSON.stringify({ case_id: $json.case_id, response: $json }) }}`
- Aggregate all incoming items: `$input.all().map(item => item.json)`

## Error behavior

The RAG and case-evaluation requests retry three times. They continue their regular output on terminal HTTP failure so that **Aggregate Case Evidence** can detect incomplete evidence and fail explicitly instead of silently producing a misleading PASS.
