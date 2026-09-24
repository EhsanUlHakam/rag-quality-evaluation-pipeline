# Production Upgrade Roadmap

## Retrieval

- Add a versioned embedding adapter and record model name/dimension.
- Evaluate hybrid keyword plus semantic retrieval.
- Replace in-memory index with pgvector, Qdrant, Weaviate, or another approved store.
- Measure chunking variants by document type rather than adopting one global size.
- Track corpus and embedding-version fingerprints.

## Generation

- Implement Ollama behind the existing adapter for local experimentation.
- Add hosted providers only through secret-managed configuration.
- Record exact model, prompt-template version, sampling parameters, and token counts.
- Validate structured outputs and citation schemas.

## Evaluation

- Expand the curated golden set with subject-matter review.
- Add semantic answer similarity and claim-level entailment.
- Use LLM judges only as secondary signals and calibrate them against human labels.
- Run repeated samples for nondeterministic models and report confidence intervals.
- Segment metrics by category, difficulty, language, tenant, and risk.

## Monitoring and security

- Redact PII and secrets from prompts, traces, and reports.
- Enforce document-level access control before retrieval.
- Protect against prompt injection embedded in source documents.
- Add rate limits, authentication, audit retention, and encrypted persistence.
- Monitor retrieval drift, refusal rate, latency, token cost, model errors, and user feedback.

## CI/CD

- Run a small deterministic smoke set on every pull request.
- Run broader probabilistic suites on schedule or before release.
- Version baselines and require approval when thresholds change.
- Upload reports as CI artifacts and preserve the candidate configuration.
- Separate flaky infrastructure retries from model-quality failures.

