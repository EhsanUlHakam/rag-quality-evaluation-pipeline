from __future__ import annotations

import math
from statistics import mean, median
from typing import Any


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(0, math.ceil(percentile_value * len(ordered)) - 1)
    return float(ordered[rank])


def aggregate_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    answerable = [item for item in results if item["case"]["answerable"]]
    latencies = [float(item["response"].get("latency_ms", 0)) for item in results]
    total_tokens = sum(
        int(item["response"].get("usage", {}).get("total_tokens_approx", 0))
        for item in results
    )
    return {
        "case_count": len(results),
        "retrieval_hit_rate_at_k": round(mean(item["metrics"]["retrieval_hit_at_k"] for item in answerable), 4),
        "expected_source_match_rate": round(mean(item["metrics"]["expected_source_match"] for item in answerable), 4),
        "fact_coverage": round(mean(item["metrics"]["keyword_coverage"] for item in answerable), 4),
        "answerability_handling": round(mean(item["metrics"]["answerability_correct"] for item in results), 4),
        "citation_validity": round(mean(item["metrics"]["citation_validity"] for item in results), 4),
        "groundedness_heuristic": round(mean(item["metrics"]["groundedness"] for item in answerable), 4),
        "error_rate": round(mean(item["metrics"]["error"] for item in results), 4),
        "average_latency_ms": round(mean(latencies), 3),
        "p50_latency_ms": round(median(latencies), 3),
        "p95_latency_ms": round(percentile(latencies, 0.95), 3),
        "estimated_tokens": total_tokens,
        "estimated_cost_usd": round(sum(float(item["response"].get("estimated_cost_usd", 0)) for item in results), 6),
        "overall_pass_rate": round(mean(item["metrics"]["case_pass"] for item in results), 4),
    }


def evaluate_gate(metrics: dict[str, Any], gates: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    violations: list[dict[str, Any]] = []
    for metric, threshold in gates.get("minimum", {}).items():
        actual = metrics[metric]
        if actual < threshold:
            violations.append({"metric": metric, "operator": ">=", "threshold": threshold, "actual": actual})
    for metric, threshold in gates.get("maximum", {}).items():
        actual = metrics[metric]
        if actual > threshold:
            violations.append({"metric": metric, "operator": "<=", "threshold": threshold, "actual": actual})
    return ("PASS" if not violations else "FAIL", violations)


def _case_score(metrics: dict[str, Any]) -> float:
    values = [
        1.0 if metrics["retrieval_hit_at_k"] is not False else 0.0,
        float(metrics["keyword_coverage"]),
        float(metrics["answerability_correct"]),
        float(metrics["citation_validity"]),
        float(metrics["groundedness"]),
        0.0 if metrics["error"] else 1.0,
    ]
    return mean(values)


def compare_runs(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    baseline_by_id = {item["case"]["id"]: item for item in baseline["results"]}
    candidate_by_id = {item["case"]["id"]: item for item in candidate["results"]}
    cases = []
    counts = {"improved": 0, "unchanged": 0, "regressed": 0}
    for case_id in sorted(set(baseline_by_id) & set(candidate_by_id)):
        before = _case_score(baseline_by_id[case_id]["metrics"])
        after = _case_score(candidate_by_id[case_id]["metrics"])
        delta = after - before
        classification = "improved" if delta > 0.05 else "regressed" if delta < -0.05 else "unchanged"
        counts[classification] += 1
        cases.append({
            "case_id": case_id,
            "baseline_pass": baseline_by_id[case_id]["metrics"]["case_pass"],
            "candidate_pass": candidate_by_id[case_id]["metrics"]["case_pass"],
            "score_delta": round(delta, 4),
            "classification": classification,
        })
    metric_deltas = {
        key: round(float(candidate["metrics"][key]) - float(baseline["metrics"][key]), 4)
        for key in baseline["metrics"]
        if isinstance(baseline["metrics"][key], (int, float))
    }
    return {
        "baseline_run_id": baseline["run_id"],
        "candidate_run_id": candidate["run_id"],
        "baseline_gate": baseline["gate_status"],
        "candidate_gate": candidate["gate_status"],
        "classification_counts": counts,
        "metric_deltas": metric_deltas,
        "per_question": cases,
    }

