from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .config import (
    DATABASE_PATH, DATASET_PATH, KNOWLEDGE_BASE_DIR, REPORTS_DIR,
    ensure_runtime_directories, load_quality_gates,
)
from .database import EvaluationDatabase
from .evaluation import evaluate_case, load_dataset
from .generation import ExtractiveAnswerGenerator
from .ingestion import chunk_documents, load_documents
from .metrics import aggregate_metrics, compare_runs, evaluate_gate
from .reporting import generate_reports
from .retrieval import TfidfRetriever


ensure_runtime_directories()
database = EvaluationDatabase(DATABASE_PATH)
generator = ExtractiveAnswerGenerator()
app = FastAPI(
    title="RAG Quality Evaluation & Regression Pipeline",
    version="1.0.0",
    description="Deterministic local RAG evaluation API for portfolio demonstration.",
)


Scenario = Literal["good", "hallucination", "missing_citation", "timeout", "malformed", "empty_retrieval"]


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    case_id: str | None = None
    chunk_size: int = Field(default=90, ge=10, le=500)
    overlap: int = Field(default=15, ge=0, le=200)
    top_k: int = Field(default=3, ge=1, le=10)
    scenario: Scenario = "good"


class CaseEvaluationRequest(BaseModel):
    case_id: str
    response: dict[str, Any]


class RunRequest(BaseModel):
    name: str = Field(default="evaluation-run", min_length=1, max_length=80)
    chunk_size: int = Field(default=90, ge=10, le=500)
    overlap: int = Field(default=15, ge=0, le=200)
    top_k: int = Field(default=3, ge=1, le=10)
    scenario: Scenario = "good"
    scenario_overrides: dict[str, Scenario] = Field(default_factory=dict)
    set_as_baseline: bool = False


class ResultsRunRequest(BaseModel):
    name: str = "n8n-run"
    parameters: dict[str, Any] = Field(default_factory=dict)
    results: list[dict[str, Any]]
    set_as_baseline: bool = False


class CompareRequest(BaseModel):
    baseline_run_id: str | None = None
    baseline_name: str | None = None
    candidate_run_id: str | None = None
    candidate_name: str | None = None


def rag_query(request: QueryRequest) -> dict[str, Any]:
    documents = load_documents(KNOWLEDGE_BASE_DIR)
    chunks = chunk_documents(documents, request.chunk_size, request.overlap)
    retrieved = TfidfRetriever(chunks).retrieve(request.question, request.top_k)
    response = generator.generate(request.question, retrieved, request.scenario)
    response["case_id"] = request.case_id
    response["parameters"] = {
        "chunk_size": request.chunk_size,
        "overlap": request.overlap,
        "top_k": request.top_k,
        "scenario": request.scenario,
    }
    return response


def build_run(name: str, parameters: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = aggregate_metrics(results)
    gate_status, violations = evaluate_gate(metrics, load_quality_gates())
    return {
        "run_id": f"rag-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}",
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "parameters": parameters,
        "metrics": metrics,
        "gate_status": gate_status,
        "violations": violations,
        "results": results,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag-evaluation", "database": str(DATABASE_PATH)}


@app.post("/api/v1/ingest")
def ingest(chunk_size: int = 90, overlap: int = 15) -> dict[str, Any]:
    documents = load_documents(KNOWLEDGE_BASE_DIR)
    chunks = chunk_documents(documents, chunk_size, overlap)
    return {
        "document_count": len(documents), "chunk_count": len(chunks),
        "document_ids": [document.document_id for document in documents],
        "sample_chunk": chunks[0].to_dict(),
    }


@app.get("/api/v1/dataset")
def dataset() -> dict[str, Any]:
    cases = load_dataset(DATASET_PATH)
    return {"count": len(cases), "cases": cases}


@app.post("/api/v1/rag/query")
def query(request: QueryRequest) -> dict[str, Any]:
    return rag_query(request)


@app.post("/api/v1/evaluation/case")
def evaluate_single_case(request: CaseEvaluationRequest) -> dict[str, Any]:
    cases = {case["id"]: case for case in load_dataset(DATASET_PATH)}
    case = cases.get(request.case_id)
    if case is None:
        raise HTTPException(404, f"Unknown case_id: {request.case_id}")
    return {"case": case, "response": request.response, "metrics": evaluate_case(case, request.response)}


@app.post("/api/v1/evaluation/runs")
def execute_run(request: RunRequest) -> dict[str, Any]:
    results = []
    for case in load_dataset(DATASET_PATH):
        scenario = request.scenario_overrides.get(case["id"], request.scenario)
        response = rag_query(QueryRequest(
            question=case["question"], case_id=case["id"],
            chunk_size=request.chunk_size, overlap=request.overlap,
            top_k=request.top_k, scenario=scenario,
        ))
        results.append({"case": case, "response": response, "metrics": evaluate_case(case, response)})
    parameters = request.model_dump(exclude={"name", "set_as_baseline"})
    run = build_run(request.name, parameters, results)
    database.save_run(run, request.set_as_baseline)
    paths = generate_reports(run, REPORTS_DIR)
    return {**run, "report_paths": paths, "ci_exit_code": 0 if run["gate_status"] == "PASS" else 1}


@app.post("/api/v1/evaluation/runs/from-results")
def store_results_run(request: ResultsRunRequest) -> dict[str, Any]:
    run = build_run(request.name, request.parameters, request.results)
    database.save_run(run, request.set_as_baseline)
    paths = generate_reports(run, REPORTS_DIR)
    return {**run, "report_paths": paths, "ci_exit_code": 0 if run["gate_status"] == "PASS" else 1}


@app.get("/api/v1/evaluation/runs")
def list_runs() -> list[dict[str, Any]]:
    return database.list_runs()


@app.get("/api/v1/evaluation/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    run = database.get_run(run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return run


@app.post("/api/v1/evaluation/compare")
def compare(request: CompareRequest) -> dict[str, Any]:
    baseline = (
        database.get_run(request.baseline_run_id) if request.baseline_run_id
        else database.latest_by_name(request.baseline_name) if request.baseline_name
        else database.baseline()
    )
    candidate = (
        database.get_run(request.candidate_run_id) if request.candidate_run_id
        else database.latest_by_name(request.candidate_name) if request.candidate_name
        else None
    )
    if baseline is None or candidate is None:
        raise HTTPException(404, "Baseline or candidate run not found")
    return compare_runs(baseline, candidate)


@app.get("/api/v1/reports/{run_id}/{format_name}")
def report(run_id: str, format_name: Literal["json", "csv", "md", "html"]):
    run = database.get_run(run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    paths = generate_reports(run, REPORTS_DIR)
    key = "markdown" if format_name == "md" else format_name
    path = Path(paths[key])
    media_types = {"json": "application/json", "csv": "text/csv", "md": "text/markdown", "html": "text/html"}
    return FileResponse(path, media_type=media_types[format_name], filename=path.name)


@app.post("/api/v1/control/reset")
def reset() -> dict[str, bool]:
    database.reset()
    return {"reset": True}

