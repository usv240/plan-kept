from fastapi.testclient import TestClient
from service.main import app
client=TestClient(app)
def post(path,body=None):return client.post(path,json=body or {})
def test_full_http_collaboration():
 assert client.get("/").status_code==200;w=post("/api/workspaces").json();wid=w["workspace_id"];w=post(f"/api/workspaces/{wid}/demo-perspectives").json();assert w["ledger"][0]["state"]=="conflicting";post(f"/api/workspaces/{wid}/clarification",{"answer":"The access log confirms the room was unavailable until 10:25.","facilitator":"Riley Shah - synthetic"});w=post(f"/api/workspaces/{wid}/repair",{"decision":"implementation_gap","facilitator":"Riley Shah - synthetic"}).json();assert w["status"]=="repair_approved";post("/api/hardening/advance",{"minutes":10080});w=post(f"/api/workspaces/{wid}/confirm",{"experienced":True,"note":"The room was available this time."}).json();assert w["status"]=="closed"
def test_private_role_view_and_revision_route():
 w=post("/api/workspaces").json();wid=w["workspace_id"];post(f"/api/workspaces/{wid}/responses",{"participant_id":"student","answer":"Private detail","sharing":"private"});fac=client.get(f"/api/workspaces/{wid}?role=facilitator").json();assert fac["responses"]==[];student=client.get(f"/api/workspaces/{wid}?role=student").json();assert student["responses"][0]["answer"]=="Private detail";post(f"/api/workspaces/{wid}/responses/student/revise",{"revised_answer":"Corrected private detail","reason":"Correction"});assert client.get(f"/api/workspaces/{wid}?role=student").json()["responses"][0]["version"]==2
def test_proof_research_and_conformance():
 proof=client.get("/api/proof").json();assert proof["passed"]==proof["total"]==10;research=client.get("/api/research").json();assert "does not validate Plan Kept" in research["claim_boundary"];assert len(research["prior_art"])==3;assert client.get("/api/conformance").json()["category"]=="The Collaborative Partner"
def test_no_prohibited_endpoint():
 paths=" ".join(app.openapi()["paths"])
 for forbidden in ["/diagnose","/risk-score","/restrain","/discipline","/legal","/change-plan"]:assert forbidden not in paths