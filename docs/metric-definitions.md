# Metric Definitions

All percentage metrics are stored as values from `0.0` to `1.0`.

| Metric | Calculation | What it can tell us | What it cannot prove |
|---|---|---|---|
| Retrieval hit rate at K | Answerable cases where expected source appears in top K / answerable cases | Retriever found the expected document | The selected chunk contains every needed fact |
| Expected-source match | Same source-membership signal, retained explicitly per case | Source-routing correctness | Answer correctness |
| Fact coverage | Expected normalized phrases found in answer / expected phrases | Required facts are present | Facts are used correctly in every grammatical context |
| Answerability handling | Correct answer/refusal decisions / all cases | Known versus unknown behavior | Broad open-world truth |
| Citation validity | Citations point to retrieved source/chunk IDs | Citation is real and traceable | Cited text truly supports every claim |
| Groundedness heuristic | Minimum token-overlap ratio across answer sentences against retrieved context | Detects one clearly unsupported sentence | Semantic entailment or truth |
| Error rate | Cases with structured error / all cases | Operational stability | Silent logical errors |
| Average latency | Arithmetic mean of case latencies | Overall response-time tendency | Tail behavior |
| P50 latency | Median latency | Typical case | Worst-user experience |
| P95 latency | Nearest-rank 95th percentile | Tail latency | Maximum latency in very small samples |
| Estimated tokens | Approximate characters divided by four | Relative usage trend | Provider invoice accuracy |
| Estimated cost | Adapter-provided estimate | Relative hosted-model cost when configured | Infrastructure cost; deterministic mode reports zero |
| Overall pass rate | Cases satisfying all required checks / all cases | Release-level regression signal | Universal RAG correctness |

## Why multiple signals are necessary

A correct source with a bad answer is a generation failure. A polished answer based on the wrong source is a retrieval failure. A grounded answer that omits a required fact is a completeness failure. Collapsing these into one score hides the layer that needs repair.

## LLM-as-a-judge

It is intentionally absent from the default gate. A future judge can score semantics or style, but it introduces model bias, prompt sensitivity, nondeterminism, provider cost, and possible preference for fluent unsupported answers. It should supplement—not replace—deterministic checks.

