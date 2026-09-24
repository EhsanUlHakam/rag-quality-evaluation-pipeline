# Project Demonstration and Concept Guide

## The one-sentence explanation

This system treats a RAG application as a testable pipeline: it checks the evidence retrieved, the answer generated from it, the citations returned, the operational behavior, and whether a candidate release regressed against an approved baseline.

## Vocabulary

| Term | Plain meaning |
|---|---|
| RAG | Retrieve relevant private/current text before generating an answer |
| Ingestion | Convert source documents into searchable units |
| Normalization | Remove formatting variation that should not affect search |
| Chunk | A bounded piece of a document used for retrieval |
| Metadata | IDs and positions that make a chunk traceable |
| TF-IDF | Weigh words higher when important to one document and rarer across documents |
| Cosine similarity | Compare the direction of query and chunk vectors |
| Top-k | Number of highest-ranked chunks supplied as context |
| Context window | Text available to the generator for one answer |
| Grounded | Claims are supported by supplied context |
| Hallucination | Unsupported or fabricated output presented as an answer |
| Citation | Pointer to the source/chunk used as evidence |
| Baseline | Approved reference run |
| Candidate | New configuration being evaluated |
| Quality gate | Threshold-based release decision |
| Regression | Candidate becomes materially worse than baseline |
| P50/P95 | Typical and tail latency percentiles |
| Idempotency | Repeating an operation does not create unintended duplicate state |

## Demonstration order

1. Show `knowledge-base/` and explain controlled source truth.
2. Show `evaluation-data/eval_dataset.json` and explain test oracles.
3. Show `/api/v1/ingest` and one chunk's metadata.
4. Run the baseline and open its HTML report.
5. Trace `rag-007` using `docs/backend-mechanisms.md`.
6. Run the candidate and show exact gate violations.
7. Compare baseline and candidate per question.
8. Run the controlled failure demo.
9. Show the n8n workflow and SQLite history.
10. Close with limitations and the production roadmap.

## Important distinctions

### Retrieval quality versus generation quality

Retrieval asks whether the correct evidence was found. Generation asks whether the response used that evidence correctly. A single end-to-end accuracy number cannot tell which layer failed.

### Retry versus regression

Retry is appropriate for transient timeouts or connection failures. A factual, citation, or groundedness failure should remain visible; retrying until it passes can hide nondeterminism.

### Deterministic versus probabilistic testing

Traditional functions often have a single exact output. Generative systems can produce many acceptable answers and change across runs or model versions. Evaluation therefore uses invariant requirements—source, facts, citations, safety, latency—plus distributions for nondeterministic modes.

### Cost and latency

Increasing top-k can improve recall while increasing prompt size, latency, and model cost. Smaller chunks can improve precision but split facts. Larger chunks preserve context but add noise. Quality engineering measures the trade-off instead of choosing settings by intuition.

## Questions to ask before accepting any RAG metric

- What exact failure does this metric detect?
- What failure can it miss?
- Is its denominator answerable cases or all cases?
- Is the threshold based on risk or convenience?
- Can the model under test see the expected answer?
- Was the corpus, chunking, prompt, and model version recorded?
- Are low-frequency critical cases hidden by aggregate averages?
- Does a cited source actually support each claim?
- Are retries hiding nondeterministic failures?
- Is the test dataset representative, reviewed, and protected from leakage?

## Upgrade story

The deterministic components are interfaces, not dead ends. Replace TF-IDF with a hybrid semantic retriever and the extractive generator with Ollama or a hosted model. Keep the dataset, evidence schema, evaluator, regression comparison, audit store, and gates so the upgraded system remains measurable.
