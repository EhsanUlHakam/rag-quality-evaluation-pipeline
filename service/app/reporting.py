from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any


def generate_reports(run: dict[str, Any], reports_dir: Path) -> dict[str, str]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(character if character.isalnum() or character in "-_" else "-" for character in run["name"])
    prefix = reports_dir / f"{safe_name}-{run['run_id']}"
    paths = {
        "json": str(prefix.with_suffix(".json")),
        "csv": str(prefix.with_suffix(".csv")),
        "markdown": str(prefix.with_suffix(".md")),
        "html": str(prefix.with_suffix(".html")),
    }

    Path(paths["json"]).write_text(json.dumps(run, indent=2), encoding="utf-8")
    with Path(paths["csv"]).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "case_id", "question", "pass", "retrieval_hit_at_k", "keyword_coverage",
            "answerability_correct", "citation_validity", "groundedness", "latency_ms", "error",
        ])
        for item in run["results"]:
            metric = item["metrics"]
            writer.writerow([
                item["case"]["id"], item["case"]["question"], metric["case_pass"],
                metric["retrieval_hit_at_k"], metric["keyword_coverage"],
                metric["answerability_correct"], metric["citation_validity"],
                metric["groundedness"], metric["latency_ms"], metric["error"],
            ])

    metric_lines = "\n".join(f"- **{key}**: {value}" for key, value in run["metrics"].items())
    violation_lines = "\n".join(
        f"- `{item['metric']}` expected {item['operator']} {item['threshold']}, actual {item['actual']}"
        for item in run["violations"]
    ) or "- None"
    case_rows = "\n".join(
        f"| {item['case']['id']} | {'PASS' if item['metrics']['case_pass'] else 'FAIL'} | "
        f"{item['metrics']['keyword_coverage']:.2f} | {item['metrics']['groundedness']:.2f} | "
        f"{item['response']['latency_ms']:.2f} |"
        for item in run["results"]
    )
    markdown = f"""# RAG Evaluation Report: {run['name']}

- Run ID: `{run['run_id']}`
- Created: {run['created_at']}
- Quality gate: **{run['gate_status']}**

## Aggregate metrics

{metric_lines}

## Threshold violations

{violation_lines}

## Per-question results

| Case | Result | Fact coverage | Groundedness heuristic | Latency ms |
|---|---:|---:|---:|---:|
{case_rows}

> Groundedness is a deterministic token-overlap heuristic, not a confirmed measure of factual truth.
"""
    Path(paths["markdown"]).write_text(markdown, encoding="utf-8")

    metric_html = "".join(
        f"<tr><td>{html.escape(key)}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in run["metrics"].items()
    )
    result_html = "".join(
        "<tr>"
        f"<td>{html.escape(item['case']['id'])}</td>"
        f"<td>{html.escape(item['case']['question'])}</td>"
        f"<td class={'pass' if item['metrics']['case_pass'] else 'fail'}>{'PASS' if item['metrics']['case_pass'] else 'FAIL'}</td>"
        f"<td>{item['metrics']['keyword_coverage']:.2f}</td>"
        f"<td>{item['metrics']['groundedness']:.2f}</td>"
        "</tr>"
        for item in run["results"]
    )
    document = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>RAG Evaluation {html.escape(run['name'])}</title>
<style>body{{font-family:Segoe UI,Arial;margin:2rem;max-width:1100px}}table{{border-collapse:collapse;width:100%;margin:1rem 0}}th,td{{border:1px solid #ddd;padding:.55rem;text-align:left}}th{{background:#152238;color:white}}.pass{{color:#087830;font-weight:bold}}.fail{{color:#b42318;font-weight:bold}}code{{background:#eee;padding:.15rem}}</style></head>
<body><h1>RAG Quality Evaluation</h1><p>Run <code>{html.escape(run['run_id'])}</code></p>
<h2>Quality gate: <span class="{'pass' if run['gate_status'] == 'PASS' else 'fail'}">{run['gate_status']}</span></h2>
<h2>Aggregate metrics</h2><table><tr><th>Metric</th><th>Value</th></tr>{metric_html}</table>
<h2>Per-question evidence</h2><table><tr><th>Case</th><th>Question</th><th>Result</th><th>Fact coverage</th><th>Groundedness</th></tr>{result_html}</table>
<p><em>Groundedness is a token-overlap heuristic and must not be treated as confirmed truth.</em></p></body></html>"""
    Path(paths["html"]).write_text(document, encoding="utf-8")
    return paths

