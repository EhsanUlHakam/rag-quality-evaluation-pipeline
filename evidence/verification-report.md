# Local Verification Report

Verification date: 2026-09-19 UTC

## Environment used for packaged verification

- Python 3.12
- FastAPI TestClient for HTTP boundary verification
- Temporary SQLite database
- Deterministic extractive mode
- No paid model, API key, vector database, or external knowledge source

Docker was not available inside the packaging environment. Docker Compose files and health checks were inspected, while container startup remains part of the Windows first-run procedure.

## Results

- Unit tests: **6 passed**
- Workflow JSON: **9 unique, reachable nodes**
- Documents loaded: **5**
- Evaluation cases: **12**
- JSON, CSV, Markdown, and HTML report endpoints: **verified**
- SQLite run/result persistence: **verified through the HTTP service**

### Baseline

| Metric | Measured value |
|---|---:|
| Quality gate | PASS |
| Retrieval hit rate at K | 1.0000 |
| Fact coverage | 0.9545 |
| Answerability handling | 1.0000 |
| Citation validity | 1.0000 |
| Groundedness heuristic | 1.0000 |
| Error rate | 0.0000 |
| Overall pass rate | 0.9167 |

One of twelve cases failed because both refund facts were not selected by the extractive generator. The gate still passed under the version-controlled thresholds, and the individual failure remained visible.

### Weak candidate

Configuration: chunk size `18`, overlap `0`, top-k `1`.

| Metric | Measured value |
|---|---:|
| Quality gate | FAIL |
| Retrieval hit rate at K | 1.0000 |
| Fact coverage | 0.5455 |
| Overall pass rate | 0.5000 |

Violations:

- Fact coverage required `>= 0.80`; measured `0.5455`.
- Overall pass rate required `>= 0.75`; measured `0.5000`.

Regression comparison classified six questions as regressed and six as unchanged.

### Controlled failures

- The unsupported unlimited-storage sentence produced groundedness `0.7143`, below the per-case `0.75` requirement.
- Missing citation reduced aggregate citation validity to `0.8333`.
- Controlled timeout produced structured error evidence.
- Failure run quality gate: **FAIL**.

Latency values from this packaging environment are not representative of Docker, network, Ollama, hosted LLM, or production performance and should not be marketed as performance benchmarks.


## Verified Windows Docker Execution — 2026-09-25

The packaged system was subsequently executed on Windows 11 using Docker Desktop 29.7.2.

### Runtime verification

- FastAPI RAG evaluation service: healthy on port 8003
- Self-hosted n8n: healthy on port 5681
- Python unit tests: 6 passed
- Knowledge-base documents: 5
- Evaluation dataset cases: 12
- Reports generated: HTML, Markdown, CSV, and JSON
- Persistence: SQLite-backed run history verified

### Direct baseline

- Quality gate: PASS
- Overall pass rate: 0.9167
- Retrieval hit rate at K: 1.0000
- Fact coverage: 0.9545

### Weak candidate

- Quality gate: FAIL
- Overall pass rate: 0.5000
- Regressed cases: 6
- Configuration: chunk size 18, overlap 0, top-k 1

### n8n-orchestrated run

- Quality gate: PASS
- Cases processed: 12
- Retrieval hit rate at K: 1.0000
- Expected-source match rate: 1.0000
- Fact coverage: 0.9545
- Citation validity: 1.0000
- Groundedness heuristic: 1.0000
- Error rate: 0.0000
- Estimated deterministic cost: USD 0.00

Local deterministic latency values are not representative of hosted LLM, Ollama, network, or production performance.
