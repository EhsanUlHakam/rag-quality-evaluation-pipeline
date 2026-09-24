#!/usr/bin/env sh
response="$(curl -fsS -X POST http://localhost:8003/api/v1/evaluation/runs -H 'Content-Type: application/json' -d '{"name":"candidate-small-chunks","chunk_size":18,"overlap":0,"top_k":1,"scenario":"good","set_as_baseline":false}')"
printf '%s\n' "$response"
printf '%s' "$response" | python3 -c 'import json,sys; raise SystemExit(json.load(sys.stdin)["ci_exit_code"])'
