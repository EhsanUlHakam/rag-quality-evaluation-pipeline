from __future__ import annotations

import unittest

from app.config import DATASET_PATH, KNOWLEDGE_BASE_DIR, load_quality_gates
from app.evaluation import evaluate_case, load_dataset
from app.generation import ExtractiveAnswerGenerator
from app.ingestion import chunk_documents, load_documents
from app.metrics import aggregate_metrics, evaluate_gate
from app.retrieval import TfidfRetriever


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_dataset(DATASET_PATH)
        cls.generator = ExtractiveAnswerGenerator()

    def retriever(self, chunk_size: int = 90, overlap: int = 15) -> TfidfRetriever:
        documents = load_documents(KNOWLEDGE_BASE_DIR)
        return TfidfRetriever(chunk_documents(documents, chunk_size, overlap))

    def execute(self, chunk_size: int, overlap: int, top_k: int, overrides=None):
        retriever = self.retriever(chunk_size, overlap)
        results = []
        for case in self.cases:
            scenario = (overrides or {}).get(case["id"], "good")
            response = self.generator.generate(case["question"], retriever.retrieve(case["question"], top_k), scenario)
            results.append({"case": case, "response": response, "metrics": evaluate_case(case, response)})
        return results

    def test_ingestion_creates_traceable_chunks(self):
        documents = load_documents(KNOWLEDGE_BASE_DIR)
        chunks = chunk_documents(documents, 40, 5)
        self.assertEqual(5, len(documents))
        self.assertGreater(len(chunks), len(documents))
        self.assertIn("::chunk-", chunks[0].chunk_id)

    def test_baseline_passes_quality_gate(self):
        metrics = aggregate_metrics(self.execute(90, 15, 3))
        status, violations = evaluate_gate(metrics, load_quality_gates())
        self.assertEqual("PASS", status)
        self.assertEqual([], violations)
        self.assertGreaterEqual(metrics["retrieval_hit_rate_at_k"], 0.90)

    def test_weak_chunking_candidate_fails_gate(self):
        metrics = aggregate_metrics(self.execute(18, 0, 1))
        status, violations = evaluate_gate(metrics, load_quality_gates())
        self.assertEqual("FAIL", status)
        self.assertTrue(any(item["metric"] == "fact_coverage" for item in violations))

    def test_unanswerable_question_is_refused(self):
        case = next(item for item in self.cases if item["id"] == "rag-011")
        response = self.generator.generate(case["question"], self.retriever().retrieve(case["question"], 3))
        metrics = evaluate_case(case, response)
        self.assertTrue(metrics["answerability_correct"])
        self.assertEqual([], response["citations"])

    def test_hallucination_is_caught_by_weakest_sentence_overlap(self):
        case = next(item for item in self.cases if item["id"] == "rag-012")
        response = self.generator.generate(
            case["question"], self.retriever().retrieve(case["question"], 3), "hallucination"
        )
        metrics = evaluate_case(case, response)
        self.assertFalse(metrics["case_pass"])
        self.assertLess(metrics["groundedness"], 0.75)

    def test_missing_citation_is_caught(self):
        case = next(item for item in self.cases if item["id"] == "rag-001")
        response = self.generator.generate(
            case["question"], self.retriever().retrieve(case["question"], 3), "missing_citation"
        )
        self.assertFalse(evaluate_case(case, response)["citation_validity"])


if __name__ == "__main__":
    unittest.main()
