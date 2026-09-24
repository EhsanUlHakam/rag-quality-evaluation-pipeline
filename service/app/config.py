from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


ROOT_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_DIR = Path(os.getenv("KNOWLEDGE_BASE_DIR", ROOT_DIR / "knowledge-base"))
DATASET_PATH = Path(os.getenv("EVAL_DATASET_PATH", ROOT_DIR / "evaluation-data" / "eval_dataset.json"))
QUALITY_GATES_PATH = Path(os.getenv("QUALITY_GATES_PATH", ROOT_DIR / "config" / "quality-gates.yaml"))
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT_DIR / "data"))
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", ROOT_DIR / "reports"))
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", DATA_DIR / "rag-evaluation.db"))


def ensure_runtime_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_quality_gates() -> dict[str, Any]:
    with QUALITY_GATES_PATH.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    return value["quality_gates"]
