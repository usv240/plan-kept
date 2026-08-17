"""Input-driven fictional plan intake for the public hackathon sandbox."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from plan_kept.workflow import SOURCES, _append, create_workspace


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_pilot_workspace(intake: dict[str, Any]) -> dict[str, Any]:
    """Create a fictional workspace while retaining only exact-quoted plan promises."""

    if intake.get("data_class") != "synthetic":
        raise ValueError("the public sandbox accepts fictional synthetic data only")
    transcription = str(intake["plan_transcription"]).strip()
    promises = intake.get("promises") or []
    if not 1 <= len(promises) <= 6:
        raise ValueError("provide between one and six fictional plan promises")
    if any(str(row["quote"]).strip() not in transcription for row in promises):
        raise ValueError("every retained promise quote must appear exactly in the supplied plan transcription")

    workspace = create_workspace()
    workspace.update(
        {
            "origin": "pilot_input",
            "data_class": "synthetic",
            "clock_mode": "realtime",
            "created_at": _iso_now(),
            "case_reference": str(intake["case_reference"]).strip(),
        }
    )
    student_name = str(intake["student_reference"]).strip()
    workspace["student"] = {"display_name": student_name, "record_is_real": False}
    normalized_promises = [
        {
            "promise_id": f"promise-{index}",
            "title": str(row["title"]).strip(),
            "quote": str(row["quote"]).strip(),
            "category": str(row.get("category", "support")).strip() or "support",
            "status": "unreviewed",
        }
        for index, row in enumerate(promises, start=1)
    ]
    workspace["plan"] = {
        "transcription": transcription,
        "model": "none",
        "mode": "user-supplied-fictional-plan",
        "promises": normalized_promises,
        "accuracy": {"matched": len(normalized_promises), "total": len(normalized_promises), "invented": 0},
    }
    names = intake["participants"]
    for participant in workspace["participants"]:
        participant["display_name"] = str(names[participant["participant_id"]]).strip()
    focus = normalized_promises[0]
    workspace["questions"] = {
        "student": {"question_id": "q-student-focus", "text": f"When you needed {focus['title']}, what happened next?", "why": "Your experience helps the team check whether the written support was available in practice.", "promise_id": focus["promise_id"]},
        "family": {"question_id": "q-family-focus", "text": f"What did you observe or learn about {focus['title']}?", "why": "A separate perspective can identify agreement, missing information, or a need for clarification.", "promise_id": focus["promise_id"]},
        "teacher": {"question_id": "q-teacher-focus", "text": f"What did you observe when {focus['title']} was needed?", "why": "The system preserves separate accounts rather than choosing which person is right.", "promise_id": focus["promise_id"]},
        "aide": {"question_id": "q-aide-focus", "text": f"What operational evidence could clarify whether {focus['title']} was available?", "why": "A record may clarify implementation without producing an automated truth judgment.", "promise_id": focus["promise_id"]},
    }
    workspace["sources"] = deepcopy(SOURCES)
    workspace["timeline"] = []
    _append(
        workspace,
        "Fictional plan intake",
        f"{len(normalized_promises)} exact-quoted promise(s) verified",
        "Every retained promise appears verbatim in the user-supplied fictional plan. No real education record is accepted.",
    )
    return workspace
