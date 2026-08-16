"""Participant-controlled sharing and withdrawal with visible audit history."""

from __future__ import annotations

from plan_kept.workflow import SHARING, _append
from spine.untrusted import sanitise


def change_sharing(workspace, participant_id, sharing):
    if sharing not in SHARING:
        raise ValueError("unsupported sharing choice")
    response = next((row for row in workspace["responses"] if row["participant_id"] == participant_id), None)
    if response is None:
        raise ValueError("response does not exist")
    old = response["sharing"]
    response["previous"].append({"version": response["version"], "sharing": old, "reason": "participant changed sharing"})
    response["version"] += 1
    response["sharing"] = sharing
    response["included_in_synthesis"] = sharing != "private" and not response["skipped"] and not response.get("withdrawn", False)
    _invalidate_synthesis(workspace)
    _append(workspace, participant_id, "Sharing changed", f"Participant changed sharing from {old} to {sharing}.", visible_to=[participant_id])
    return workspace


def withdraw_response(workspace, participant_id, reason):
    response = next((row for row in workspace["responses"] if row["participant_id"] == participant_id), None)
    if response is None or len(reason.strip()) < 2:
        raise ValueError("existing response and withdrawal reason are required")
    response["previous"].append({"version": response["version"], "answer": response["answer"], "reason": reason.strip()})
    response["version"] += 1
    response["answer"] = ""
    response["withdrawn"] = True
    response["included_in_synthesis"] = False
    _invalidate_synthesis(workspace)
    _append(workspace, participant_id, "Response withdrawn", "Content was removed from active views and future synthesis.", visible_to=[participant_id])
    return workspace


def secure_response_text(text):
    cleaned, spans = sanitise(text)
    return cleaned, [{"threat": row.threat.value, "text": row.text, "explanation": row.explanation} for row in spans]


def _invalidate_synthesis(workspace):
    if workspace["ledger"] or workspace["clarifications"]:
        workspace["ledger"] = []
        workspace["clarifications"] = []
        workspace["status"] = "perspectives_collected"
        workspace["synthesis_invalidated"] = True

