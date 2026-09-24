#!/usr/bin/env sh
response="$(curl -fsS -X POST http://localhost:8003/api/v1/evaluation/runs -H 'Content-Type: application/json' -d '{"name":"controlled-failure-demo","chunk_size":90,"overlap":15,"top_k":3,"scenario":"good","scenario_overrides":{"rag-012":"hallucination","rag-001":"missing_citation","rag-008":"timeout"}}')"
printf '%s\n' "$response"
printf '%s' "$response" | python3 -c 'import json,sys; raise SystemExit(json.load(sys.stdin)["ci_exit_code"])'
