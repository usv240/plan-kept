"""Live, fail-closed model evidence for the public fictional support workflow."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from time import perf_counter
from typing import Any

from plan_kept.reader import PlanReader, VertexPlanClient
from spine.semantic_routing import VertexSemanticRouter


class LiveEvidenceRunner:
    def __init__(self, project: str, web_root: Path, reader=None, router=None):
        self.reader = reader or PlanReader(VertexPlanClient(project))
        self.router = router or VertexSemanticRouter(project)
        self.fixture = web_root / "plan-fixture.png"

    def apply(self, workspace: dict[str, Any]) -> dict[str, Any]:
        artifact = self.fixture.read_bytes()
        started = perf_counter()
        result = self.reader.read(artifact, "image/png")
        if len(result.fields) < 4:
            raise RuntimeError("live plan extraction retained fewer than four verified fields")
        route = self.router.rank(
            result.transcription,
            {row["promise_id"]: f'{row["title"]}: {row["quote"]}' for row in workspace["plan"]["promises"]},
        )
        workspace["plan"].update({
            "transcription": result.transcription,
            "model": "gemini-3.5-flash",
            "mode": "live-vertex-ai",
            "accuracy": {"matched": len(result.fields), "total": len(result.fields) + len(result.dropped), "invented": 0},
            "verified_fields": result.fields,
        })
        workspace["semantic_focus_promise"] = route["winner"]
        workspace["participants"].sort(key=lambda row: workspace["questions"][row["participant_id"]]["promise_id"] != route["winner"])
        workspace["model_execution"] = {
            "live": True,
            "model": "gemini-3.5-flash",
            "artifact_sha256": sha256(artifact).hexdigest(),
            "verified_fields": len(result.fields),
            "dropped_fields": len(result.dropped),
            "latency_ms": round((perf_counter() - started) * 1000),
        }
        workspace["semantic_routing"] = route
        workspace["timeline"].append({
            "sequence": len(workspace["timeline"]) + 1,
            "at": workspace["created_at"],
            "actor": "Live plan reader",
            "action": "Promises verified and first perspective routed",
            "detail": "Gemini retained exact-quoted plan fields; embeddings selected the first support focus without judging any participant.",
            "status": "complete",
            "visible_to": ["facilitator", "auditor"],
            "evidence_ids": ["fictional-support-plan", route["winner"]],
        })
        return workspace
