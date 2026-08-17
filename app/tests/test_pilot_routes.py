from fastapi.testclient import TestClient

from service.main import app
from test_pilot import payload


client = TestClient(app)


def test_pilot_workspace_create_list_and_readiness():
    created = client.post("/api/pilot/workspaces", json=payload())
    assert created.status_code == 200
    workspace = created.json()
    listing = client.get("/api/pilot/workspaces").json()
    assert any(row["workspace_id"] == workspace["workspace_id"] for row in listing["workspaces"])
    readiness = client.get("/api/pilot/readiness").json()
    assert readiness["public_data_policy"] == "fictional-synthetic-only"
    assert "not represented as a student-record" in readiness["claim"]
    unacknowledged = payload()
    unacknowledged.pop("synthetic_acknowledgement")
    assert client.post("/api/pilot/workspaces", json=unacknowledged).status_code == 422
