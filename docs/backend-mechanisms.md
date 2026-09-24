# Backend Mechanisms and Boundary Trace

## What RAG is

Retrieval-augmented generation first searches a controlled knowledge source and then asks a generator to answer using the selected context. Retrieval exists because model parameters are not a trustworthy, current, or auditable database.

## End-to-end trace: `rag-007`

### 1. Dataset boundary

Input:

```json
{
  "id": "rag-007",
  "question": "Which plans support SAML single sign-on?",
  "expected_source_id": "sso_account_access",
  "expected_answer_facts": ["Pro and Enterprise plans", "SAML 2.0"],
  "answerable": true
}
```

Expected facts are test-oracle data. They are never passed to the answer generator.

### 2. Ingestion boundary

Markdown is normalized and split by word count. Each chunk receives:

```json
{
  "chunk_id": "sso_account_access::chunk-000",
  "document_id": "sso_account_access",
  "chunk_index": 0,
  "word_start": 0,
  "word_end": 90
}
```

Overlap reduces the chance that a sentence crossing a boundary loses necessary context, but it increases index size and repeated text.

### 3. Retrieval boundary

The retriever tokenizes the question and chunks, calculates inverse-document-frequency weights, normalizes the vectors, and ranks chunks by cosine similarity. Top-k is a recall-versus-noise control: larger K can recover more evidence but can also distract generation and consume context.

### 4. Generation boundary

The deterministic adapter selects high-overlap sentences. It returns the answer plus the exact source and chunk IDs. Expected answers remain hidden, preventing evaluation leakage.

### 5. Evaluation boundary

The evaluator independently checks:

- expected source in retrieved top K;
- expected facts present in the answer;
- answer/refusal decision;
- citations reference retrieved IDs;
- every answer sentence overlaps the supplied context;
- error and latency conditions.

### 6. Persistence boundary

SQLite stores run configuration, aggregate metrics, gate violations, full response evidence, per-question metrics, and pass/fail decisions. This makes later regression comparison reproducible.

### 7. Aggregate and gate boundary

The metrics layer aggregates all cases. The gate reads thresholds from YAML and returns every violation rather than only a boolean.

### 8. CI/CD boundary

The API emits `ci_exit_code: 0` for PASS and `1` for FAIL. CI uses the signal to prevent a weaker candidate from being promoted while reports remain available for diagnosis.

## Embeddings versus TF-IDF

TF-IDF matches words and is cheap, deterministic, transparent, and weak on paraphrases. Embeddings encode semantic similarity and better match paraphrases, but introduce model choice, vector dimensions, infrastructure, version drift, and harder-to-explain scores. This MVP starts with the measurable baseline before adding semantic retrieval.

## Offline evaluation versus production monitoring

Offline evaluation uses a controlled versioned dataset to compare releases. Production monitoring observes real traffic, latency, cost, retrieval drift, user feedback, safety, and changing source data. Passing offline evaluation is necessary evidence, not a production guarantee.

## How SDET thinking transfers

- Expected facts are assertions.
- Dataset cases are parameterized tests.
- RAG responses are test evidence.
- Quality thresholds are release criteria.
- Baselines act like approved snapshots.
- Failure categories direct debugging to retrieval, generation, citation, or infrastructure.
- Statistical and heuristic signals replace the assumption that one exact output string is always correct.

