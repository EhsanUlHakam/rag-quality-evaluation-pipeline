# Architecture

## Design objective

The system keeps four responsibilities separate:

1. RAG execution produces observations.
2. Evaluation compares those observations with explicit expectations.
3. Persistence creates an audit trail.
4. Orchestration coordinates the boundaries without owning scoring logic.

This prevents n8n expressions, retrieval code, and metric formulas from becoming one untestable block.

## Components

| Component | Responsibility |
|---|---|
| Markdown knowledge base | Version-controlled fictional source truth |
| Evaluation JSON | Questions, expected sources/facts, answerability, latency budgets |
| Ingestion | Normalize text and emit metadata-rich chunks |
| TF-IDF retriever | Rank chunks by deterministic cosine similarity |
| Generator adapter | Produce extractive answer, citations, timing, usage, and errors |
| Evaluator | Calculate per-question signals independently of generation |
| Metrics/gate | Aggregate results and compare them with YAML thresholds |
| SQLite | Preserve runs and question-level evidence |
| Reporting | Emit machine-readable and human-readable artifacts |
| n8n | Iterate cases and coordinate API calls |

## Trust boundary

The answer generator is treated as an untrusted system under test. It cannot decide whether its own answer is correct. Expected facts live in a separate dataset, and evaluation code calculates the verdict.

## Docker routing

The Windows host uses `localhost:8003` and `localhost:5681`. Inside Compose, n8n calls `http://rag-service:8003`; container-local `localhost` would point back to the n8n container.
