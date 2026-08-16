import pytest
from plan_kept.workflow import answer_clarification,approve_finding_and_repair,advance_followup,collect_demo_perspectives,confirm_student_experience,create_workspace,open_perspectives,record_response,revise_response,role_view,run_full_demo,synthesize

def test_plan_promises_are_quote_grounded_and_synthetic():
 w=create_workspace();assert w["synthetic"];assert all(p["quote"] in w["plan"]["transcription"] for p in w["plan"]["promises"]);assert w["plan"]["accuracy"]=={"matched":4,"total":4,"invented":0}
def test_perspectives_are_separate_and_one_question_each():
 w=create_workspace();open_perspectives(w);assert all(p["session_status"]=="ready" for p in w["participants"]);assert len(w["questions"])==4
def test_private_response_never_enters_facilitator_view_or_synthesis():
 w=create_workspace();open_perspectives(w);record_response(w,"student","Keep this private","private");record_response(w,"family","Family response","team");record_response(w,"teacher","Teacher response","facilitator");record_response(w,"aide","Aide response","facilitator");assert not role_view(w,"facilitator")["responses"][0]["participant_id"]=="student" if role_view(w,"facilitator")["responses"] else True;synthesize(w);assert not w["responses"][0]["included_in_synthesis"]
def test_revision_preserves_history():
 w=create_workspace();open_perspectives(w);record_response(w,"student","First answer","facilitator");revise_response(w,"student","Corrected answer","I remembered more");r=w["responses"][0];assert r["version"]==2 and r["previous"][0]["answer"]=="First answer"
def test_synthesis_requires_all_sessions():
 w=create_workspace();open_perspectives(w);record_response(w,"student","One answer","facilitator");
 with pytest.raises(ValueError):synthesize(w)
def test_synthesis_classifies_conflict_without_truth_score():
 w=create_workspace();open_perspectives(w);collect_demo_perspectives(w);synthesize(w);row=w["ledger"][0];assert row["state"]=="conflicting";assert row["system_truth_decision"] is None;assert w["clarifications"][0]["status"]=="open"
@pytest.mark.parametrize("decision",["blame_staff","student_lied","automatic_change",""])
def test_unsupported_facilitator_decisions_are_blocked(decision):
 w=create_workspace();open_perspectives(w);collect_demo_perspectives(w);synthesize(w);answer_clarification(w,"The log confirms a temporary access gap.","Facilitator")
 with pytest.raises(ValueError):approve_finding_and_repair(w,decision,"Facilitator")
def test_full_flow_closes_only_after_student_experience():
 w=run_full_demo();assert w["status"]=="closed";assert w["decisions"][0]["made_by_ai"] is False;assert w["followup"]["student_confirmation"] is True;assert len(w["actions"])==3
def test_followup_cannot_run_without_approved_repair():
 with pytest.raises(ValueError):advance_followup(create_workspace())
def test_student_confirmation_requires_due_followup():
 with pytest.raises(ValueError):confirm_student_experience(create_workspace(),True,"Yes")

