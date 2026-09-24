from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS evaluation_runs (
    run_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    parameters_json TEXT NOT NULL,
    metrics_json TEXT NOT NULL,
    gate_status TEXT NOT NULL,
    violations_json TEXT NOT NULL,
    is_baseline INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_runs_name_created ON evaluation_runs(name, created_at DESC);
CREATE TABLE IF NOT EXISTS evaluation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    case_id TEXT NOT NULL,
    question TEXT NOT NULL,
    case_json TEXT NOT NULL,
    response_json TEXT NOT NULL,
    metrics_json TEXT NOT NULL,
    case_pass INTEGER NOT NULL,
    FOREIGN KEY(run_id) REFERENCES evaluation_runs(run_id)
);
CREATE INDEX IF NOT EXISTS idx_results_run_case ON evaluation_results(run_id, case_id);
"""


class EvaluationDatabase:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def save_run(self, run: dict[str, Any], set_as_baseline: bool = False) -> None:
        with self.connect() as connection:
            if set_as_baseline:
                connection.execute("UPDATE evaluation_runs SET is_baseline = 0")
            connection.execute(
                """
                INSERT INTO evaluation_runs
                (run_id, name, created_at, parameters_json, metrics_json, gate_status, violations_json, is_baseline)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run["run_id"], run["name"], run["created_at"],
                    json.dumps(run["parameters"], sort_keys=True),
                    json.dumps(run["metrics"], sort_keys=True),
                    run["gate_status"], json.dumps(run["violations"], sort_keys=True),
                    int(set_as_baseline),
                ),
            )
            connection.executemany(
                """
                INSERT INTO evaluation_results
                (run_id, case_id, question, case_json, response_json, metrics_json, case_pass)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        run["run_id"], item["case"]["id"], item["case"]["question"],
                        json.dumps(item["case"], sort_keys=True),
                        json.dumps(item["response"], sort_keys=True),
                        json.dumps(item["metrics"], sort_keys=True),
                        int(item["metrics"]["case_pass"]),
                    )
                    for item in run["results"]
                ],
            )

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM evaluation_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if row is None:
                return None
            result_rows = connection.execute(
                "SELECT * FROM evaluation_results WHERE run_id = ? ORDER BY case_id", (run_id,)
            ).fetchall()
        return self._hydrate_run(row, result_rows)

    def latest_by_name(self, name: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM evaluation_runs WHERE name = ? ORDER BY created_at DESC LIMIT 1", (name,)
            ).fetchone()
        return self.get_run(row["run_id"]) if row else None

    def baseline(self) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT run_id FROM evaluation_runs WHERE is_baseline = 1 ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
        return self.get_run(row["run_id"]) if row else None

    def list_runs(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM evaluation_runs ORDER BY created_at DESC"
            ).fetchall()
        return [
            {
                "run_id": row["run_id"], "name": row["name"], "created_at": row["created_at"],
                "parameters": json.loads(row["parameters_json"]),
                "metrics": json.loads(row["metrics_json"]),
                "gate_status": row["gate_status"],
                "violations": json.loads(row["violations_json"]),
                "is_baseline": bool(row["is_baseline"]),
            }
            for row in rows
        ]

    @staticmethod
    def _hydrate_run(row: sqlite3.Row, result_rows: list[sqlite3.Row]) -> dict[str, Any]:
        return {
            "run_id": row["run_id"], "name": row["name"], "created_at": row["created_at"],
            "parameters": json.loads(row["parameters_json"]),
            "metrics": json.loads(row["metrics_json"]),
            "gate_status": row["gate_status"],
            "violations": json.loads(row["violations_json"]),
            "is_baseline": bool(row["is_baseline"]),
            "results": [
                {
                    "case": json.loads(result["case_json"]),
                    "response": json.loads(result["response_json"]),
                    "metrics": json.loads(result["metrics_json"]),
                }
                for result in result_rows
            ],
        }

    def reset(self) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM evaluation_results")
            connection.execute("DELETE FROM evaluation_runs")
