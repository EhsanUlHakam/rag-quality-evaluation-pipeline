from __future__ import annotations

import json
from pathlib import Path


root = Path(__file__).resolve().parents[1]
path = root / "n8n" / "rag-evaluation-workflow.json"
workflow = json.loads(path.read_text(encoding="utf-8"))
nodes = workflow.get("nodes", [])
names = [node["name"] for node in nodes]
if len(names) != len(set(names)):
    raise SystemExit("Workflow node names must be unique")
if "Manual Trigger" not in names or "Evaluation Summary" not in names:
    raise SystemExit("Workflow is missing its required start or summary node")

reachable = {"Manual Trigger"}
changed = True
while changed:
    changed = False
    for source, outputs in workflow.get("connections", {}).items():
        if source not in reachable:
            continue
        for branch in outputs.get("main", []):
            for connection in branch:
                if connection["node"] not in reachable:
                    reachable.add(connection["node"])
                    changed = True

missing = sorted(set(names) - reachable)
if missing:
    raise SystemExit(f"Unreachable workflow nodes: {missing}")
print(f"Workflow JSON valid: {len(nodes)} unique and reachable nodes.")
