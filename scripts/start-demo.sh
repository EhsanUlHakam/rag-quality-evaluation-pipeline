#!/usr/bin/env sh
set -eu
[ -f .env ] || cp .env.example .env
docker compose up -d --build
echo "RAG API: http://localhost:8003/docs"
echo "n8n:     http://localhost:5681"

