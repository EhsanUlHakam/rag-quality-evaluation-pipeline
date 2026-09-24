# Controlled Failure Modes

| Scenario | Injected behavior | Expected detection |
|---|---|---|
| `good` | Deterministic extractive response | Normal scoring |
| `hallucination` | Adds an unsupported unlimited-storage claim | Weakest-sentence groundedness falls below threshold |
| `missing_citation` | Clears citations from an otherwise supported answer | Citation validity fails |
| `timeout` | Adds controlled delay and returns a structured timeout error | Error, answerability, and possibly latency checks fail |
| `malformed` | Returns malformed-looking answer text and structured error | Error/no-error and other response checks fail |
| `empty_retrieval` | Removes all retrieved chunks | Retrieval, answerability, fact, and error checks fail |

These faults are controlled test inputs. They are not claims about real LLM failure rates.

## Retry versus correctness

Transient HTTP failures may be retried. A semantically unsupported answer should not be retried until it passes; that would hide nondeterminism and bias results. Record the failure, diagnose it, and change retrieval, prompts, data, or model behavior deliberately.

