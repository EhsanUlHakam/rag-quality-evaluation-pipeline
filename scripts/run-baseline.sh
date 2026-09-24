#!/usr/bin/env sh
response="$(curl -fsS -X POST http://localhost:8003/api/v1/evaluation/runs -H 'Content-Type: application/json' -d '{"name":"baseline","chunk_size":90,"overlap":15,"top_k":3,"scenario":"good","set_as_baseline":true}')"
printf '%s\n' "$response"
printf '%s' "$response" | python3 -c 'import json,sys; raise SystemExit(json.load(sys.stdin)["ci_exit_code"])'
