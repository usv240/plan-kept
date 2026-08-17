from fastapi.testclient import TestClient

from service.main import app
from test_pilot import payload


client = TestClient(app)


def post(path, body=None):
    return client.post(path, json=body or {})


def test_custom_fictional_workspace_completes_with_user_perspectives():
    workspace = post("/api/pilot/workspaces", payload()).json()
    workspace_id = workspace["workspace_id"]
    post(f"/api/workspaces/{workspace_id}/open-perspectives")
    responses = {
        "student": "I requested the fictional support, but it was unavailable at that moment.",
        "family": "The fictional handoff appeared incomplete.",
        "teacher": "I understood that the fictional support had been offered.",
        "aide": "The fictional access record shows availability later in the period.",
    }
    for participant_id, answer in responses.items():
        post(
            f"/api/workspaces/{workspace_id}/responses",
            {
                "participant_id": participant_id,
                "answer": answer,
                "sharing": "team" if participant_id == "family" else "facilitator",
                "skipped": False,
            },
        )
    synthesized = post(f"/api/workspaces/{workspace_id}/synthesize").json()
    assert synthesized["ledger"][0]["promise_id"] == "promise-1"
    assert synthesized["ledger"][0]["system_truth_decision"] is None
    post(
        f"/api/workspaces/{workspace_id}/clarification",
        {"answer": "A fictional operational record was reviewed for the promised support.", "facilitator": "Sandbox facilitator - fictional"},
    )
    repaired = post(
        f"/api/workspaces/{workspace_id}/repair",
        {"decision": "implementation_gap", "facilitator": "Sandbox facilitator - fictional"},
    ).json()
    assert "Quiet workspace access" in repaired["actions"][0]["title"]
    post(f"/api/workspaces/{workspace_id}/followup")
    closed = post(
        f"/api/workspaces/{workspace_id}/confirm",
        {"experienced": True, "note": "The fictional support was available during review."},
    ).json()
    assert closed["status"] == "closed"
    assert closed["student"]["record_is_real"] is False
    assert post("/api/reset").status_code == 403
