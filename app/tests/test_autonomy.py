from pathlib import Path

from fastapi.testclient import TestClient

from service.main import app


client = TestClient(app)


def test_one_request_demo_completes_full_collaborative_cycle():
    workspace = client.post("/api/demo/full").json()
    assert workspace["status"] == "closed"
    assert workspace["autonomy"]["complete"] is True
    assert workspace["metrics"]["ai_truth_decisions"] == 0
    assert workspace["followup"]["student_confirmation"] is True


def test_verified_plan_automatically_opens_role_sessions():
    workspace = client.post("/api/workspaces").json()
    assert workspace["status"] == "perspectives_open"
    assert workspace["autonomy"]["last_run_actions"] == ["role_sessions_opened"]
    assert workspace["autonomy"]["current_wait"] == "participant_perspectives"


def test_final_perspective_automatically_triggers_safe_synthesis():
    workspace = client.post("/api/workspaces").json()
    workspace = client.post(f"/api/workspaces/{workspace['workspace_id']}/demo-perspectives").json()
    assert workspace["status"] == "clarification_ready"
    assert workspace["autonomy"]["last_run_actions"] == ["shared_evidence_synthesized"]
    assert workspace["ledger"][0]["system_truth_decision"] is None


def test_repair_approval_automatically_schedules_return_to_student():
    workspace = client.post("/api/workspaces").json()
    workspace_id = workspace["workspace_id"]
    client.post(f"/api/workspaces/{workspace_id}/demo-perspectives")
    client.post(
        f"/api/workspaces/{workspace_id}/clarification",
        json={
            "answer": "The fictional access log confirms the support was unavailable.",
            "facilitator": "Riley Shah - synthetic",
        },
    )
    workspace = client.post(
        f"/api/workspaces/{workspace_id}/repair",
        json={"decision": "implementation_gap", "facilitator": "Riley Shah - synthetic"},
    ).json()
    assert workspace["status"] == "repair_approved"
    assert workspace["autonomy"]["last_run_actions"] == ["student_followup_scheduled"]
    assert workspace["autonomy"]["current_wait"] == "scheduled_student_followup"


def test_autopilot_does_not_invent_participant_input():
    workspace = client.post("/api/workspaces").json()
    resumed = client.post(f"/api/workspaces/{workspace['workspace_id']}/autopilot").json()
    assert resumed["status"] == "perspectives_open"
    assert resumed["autonomy"]["last_run_actions"] == []

def test_primary_demo_is_one_server_request_with_distinct_receipt():
    web = Path(__file__).resolve().parents[1] / "web"
    html = (web / "index.html").read_text(encoding="utf-8")
    script = (web / "app.js").read_text(encoding="utf-8")
    css = (web / "autonomy.css").read_text(encoding="utf-8")
    assert 'id="autonomy-receipt"' in html and 'aria-live="polite"' in html
    assert "/static/autonomy.css" in html and "Complete fictional tabletop" in html
    assert 'api("/api/demo/full"' in script
    assert "while (" not in script and "while(" not in script
    assert ".autonomy-note" in css

def test_health_declares_autonomy_mode():
    assert client.get("/health").json()["autonomy"] == "adaptive-partner-auto-continuation"
