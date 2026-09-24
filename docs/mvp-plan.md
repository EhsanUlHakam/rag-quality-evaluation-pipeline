# Three-Hour MVP Sequence

## 0:00–0:30 — Contracts and deterministic source truth

- Create five fictional documents and twelve evaluation cases.
- Define response schema and version-controlled quality thresholds.
- Decide which metrics apply only to answerable cases.

Exit condition: source IDs, expected facts, answerability, and gate math are explicit.

## 0:30–1:15 — RAG execution

- Normalize and chunk Markdown.
- Build dependency-free TF-IDF vectors.
- Rank top-k chunks and preserve metadata.
- Generate extractive answers, citations, latency, usage, cost, and errors.

Exit condition: one question is traceable from query to cited chunk.

## 1:15–2:00 — Evaluation and persistence

- Calculate question-level signals.
- Aggregate metrics and apply the YAML gate.
- Store runs and results in SQLite.
- Generate JSON, CSV, Markdown, and HTML reports.

Exit condition: baseline PASS and controlled fault FAIL are both reproducible.

## 2:00–2:30 — Regression and orchestration

- Compare named baseline and candidate runs.
- Classify questions as improved, unchanged, or regressed.
- Import and execute the n8n workflow.

Exit condition: weaker chunking/top-k settings produce visible regression evidence.

## 2:30–3:00 — Packaging

- Run unit and end-to-end verification.
- Complete Windows instructions and architecture/metric documentation.
- Capture portfolio evidence and prepare GitHub/Upwork copy.

Optional Ollama, embeddings, dashboards, and hosted providers begin only after these exit conditions pass.
