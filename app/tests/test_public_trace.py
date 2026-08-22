from fastapi.testclient import TestClient

from service.main import app


def test_public_trace_is_useful_and_redacted():
    client = TestClient(app)
    workspace = client.post("/api/demo/full").json()
    trace = client.get(f'/api/workspaces/{workspace["workspace_id"]}/trace').json()
    assert trace["event_count"] == len(workspace["timeline"])
    serialized = str(trace).lower()
    assert "raw prompts" in serialized
    assert "student_note" not in serialized and "answer" not in serialized
