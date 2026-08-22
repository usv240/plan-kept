from pathlib import Path
from types import SimpleNamespace

from plan_kept.live_evidence import LiveEvidenceRunner
from plan_kept.workflow import create_workspace


class Reader:
    def read(self, artifact, mime):
        return SimpleNamespace(transcription="Student Kai support Calm Room Visual schedule", fields=[
            {"key": "student", "value": "Kai", "quote": "Kai", "confidence": 1},
            {"key": "support", "value": "Calm Room", "quote": "Calm Room", "confidence": 1},
            {"key": "support", "value": "Visual schedule", "quote": "Visual schedule", "confidence": 1},
            {"key": "setting", "value": "school", "quote": "Student", "confidence": 1},
        ], dropped=[])


class Router:
    def rank(self, query, candidates):
        return {"model": "gemini-embedding-001", "mode": "live-vertex-ai", "winner": "calm_room", "scores": {key: 0.5 for key in candidates}, "live": True}


def test_live_models_choose_first_focus_without_truth_scoring():
    web = Path(__file__).resolve().parents[1] / "web"
    workspace = LiveEvidenceRunner("test", web, Reader(), Router()).apply(create_workspace())
    assert workspace["plan"]["mode"] == "live-vertex-ai"
    assert workspace["semantic_focus_promise"] == "calm_room"
    assert workspace["safety"]["risk_score"] is None
