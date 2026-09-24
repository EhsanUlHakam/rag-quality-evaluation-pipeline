# Portfolio Package

## Upwork portfolio title

RAG Quality Evaluation & AI Regression Testing Pipeline

## Upwork description

Built a locally runnable quality-engineering pipeline for testing retrieval-augmented generation systems without paid AI services. The system evaluates retrieval hit rate, required-fact coverage, answerability, citation validity, groundedness heuristics, errors, latency, approximate token usage, and estimated cost. It stores question-level evidence in SQLite, compares named baseline and candidate runs, produces HTML/Markdown/CSV/JSON reports, and returns a CI-ready PASS/FAIL quality gate. A self-hosted n8n workflow orchestrates all twelve cases. Controlled hallucination, missing-citation, timeout, and empty-retrieval modes prove that the checks detect known faults. All measurements shown are from a fictional local dataset; no production or customer outcome is claimed.

## Five Upwork skills

1. AI Quality Assurance
2. Retrieval-Augmented Generation Testing
3. Python Test Automation
4. API Testing
5. n8n Workflow Automation

## Business value

- Detect retrieval or answer regressions before release.
- Separate retrieval failures from generation failures.
- Make evidence and thresholds reviewable instead of relying on impressive demos.
- Preserve failed questions for diagnosis and audit.
- Add a repeatable quality gate to AI delivery pipelines.

## Reliability mechanisms

- Version-controlled knowledge, dataset, and thresholds
- Deterministic baseline before optional probabilistic models
- Structured errors and controlled failure injection
- Traceable chunk/source citations
- SQLite audit history
- Per-case evidence plus aggregate metrics
- Named regression baselines
- CI-ready exit status
- Human-readable and machine-readable reports

## Screenshot checklist

Capture only locally measured evidence:

1. FastAPI `/docs` showing the RAG and evaluation endpoints.
2. n8n canvas showing dataset → RAG → evaluation → storage → summary.
3. Baseline HTML report with `PASS` and aggregate metrics.
4. Candidate report showing `FAIL` and exact threshold violations.
5. Regression comparison showing regressed question count.
6. Controlled hallucination result with groundedness failure.
7. SQLite run list from `scripts/show-data.ps1`.
8. GitHub repository README and successful automated test run.

Never include passwords, tokens, browser bookmarks, work-project information, or unrelated desktop content.

## 90-second demonstration script

**0–15 seconds:** “This project tests whether a RAG system retrieves the expected evidence and produces supported answers. It runs locally with no API key or paid model.”

**15–30 seconds:** Show the five fictional Markdown sources and twelve evaluation cases. Explain that expected sources and required facts form the test oracle and are hidden from generation.

**30–45 seconds:** Run the baseline. Show retrieved chunk IDs, scores, answer, citations, latency, approximate usage, and deterministic per-case metrics.

**45–60 seconds:** Open the baseline report. Point to the PASS gate while acknowledging the individual failed multi-fact case and explaining why the aggregate gate still passes.

**60–75 seconds:** Run the small-chunk/top-1 candidate. Show the FAIL gate, fact-coverage drop, and per-question regressions.

**75–90 seconds:** Show the hallucination/missing-citation/timeout demo, SQLite audit history, and n8n workflow. Finish: “The mock evaluator identifies probable quality failures; it does not claim absolute truth or production accuracy.”

## Interview questions and model answers

### Why start with TF-IDF instead of embeddings?

It produces a transparent, deterministic baseline with no model download or vector service. After the measurement contracts are stable, embeddings can be added and compared against the same dataset.

### Why is retrieval hit rate insufficient?

The correct document may be present while the answer omits required facts, cites the wrong chunk, or adds unsupported claims. Retrieval and generation need independent checks.

### What makes citation validation meaningful?

The citation must reference a source and chunk that were actually retrieved. This proves traceability, but not semantic support, so groundedness and expected-fact checks remain separate.

### Why use a weakest-sentence groundedness heuristic?

A global overlap average can hide one unsupported sentence inside a long extractive answer. The weakest sentence makes the controlled hallucination visible, though it remains a lexical heuristic.

### Why can the baseline pass with one failed question?

Quality gates express explicit product risk tolerance across a test set. Individual failures are still reported. High-risk categories could later require 100% even when the global threshold is lower.

### How is regression determined?

Each question receives a composite of retrieval, fact, answerability, citation, groundedness, and error signals. Candidate-minus-baseline movement classifies it as improved, unchanged, or regressed, while aggregate thresholds decide release status.

### What is the difference between offline evaluation and monitoring?

Offline evaluation compares controlled releases against versioned cases. Monitoring observes real traffic, data drift, latency, cost, safety, and user feedback. Both are necessary.

### How would you test a nondeterministic hosted LLM?

Record model and prompt versions, run repeated samples, retain distributions rather than one outcome, use deterministic checks first, add calibrated human/LLM judge signals, and gate on risk-appropriate confidence.

### How does traditional SDET experience transfer?

Datasets become parameterized tests, expected facts become assertions, traces become evidence, gates become release criteria, and failure categorization directs debugging. The difference is that exact-string equality is often replaced by multiple probabilistic and deterministic signals.

### What would you secure before production?

Document-level authorization, PII redaction, prompt-injection defenses, secret management, authenticated APIs, rate limits, encrypted persistence, audit policy, and tenant isolation.

## Honest limitations

This is a deterministic local demonstration using fictional documents. It does not prove production accuracy, semantic understanding, real provider cost, or business impact. The groundedness and token metrics are heuristics and are labeled accordingly.

