"""Privacy-aware, multi-perspective promise-to-reality workflow."""

from __future__ import annotations
from copy import deepcopy
from datetime import datetime,timedelta,timezone
from typing import Any
from uuid import uuid4

BASE_TIME=datetime(2026,8,16,13,0,tzinfo=timezone.utc)
SHARING={"private","facilitator","team"}
DECISIONS={"implementation_gap","confirmed_available","needs_more_information","not_relevant"}

SOURCES={
 "doe":{"title":"U.S. Department of Education Restraint and Seclusion Resource Document","url":"https://www.ed.gov/teaching-and-administration/safe-learning-environments/school-safety-and-security/school-climate-and-student-discipline/restraint-and-seclusion-resource-document","use":"Safety framing; does not validate this product."},
 "pbis":{"title":"Center on PBIS: Restraint/Seclusion","url":"https://www.pbis.org/topics/restraintseclusion","use":"Prevention-oriented debrief and environmental adjustment rationale."},
 "cps":{"title":"Collaborative problem solving five-year study","url":"https://pubmed.ncbi.nlm.nih.gov/19033167/","use":"Mechanism inspiration from a child psychiatric setting, not ordinary K-12 validation."},
 "review":{"title":"Trauma-informed interventions systematic review","url":"https://pubmed.ncbi.nlm.nih.gov/37593061/","use":"Trauma-informed design principles and evidence limitations."}
}

PLAN_TRANSCRIPTION="""RIVERLIGHT SCHOOL — SYNTHETIC SUPPORT PLAN
Student: Kai R. — fictional
1. Kai may request access to the Calm Room during escalating noise or transitions.
2. A visual schedule must be available at the start of each class.
3. Noise-reducing headphones must travel with Kai between classrooms.
4. Substitute staff must receive the one-page support summary before working with Kai.
Review date: 2026-09-01
This fixture is not a real education record."""

PROMISES=[
 {"promise_id":"calm_room","title":"Access to the Calm Room","quote":"Kai may request access to the Calm Room during escalating noise or transitions.","category":"environment","status":"unreviewed"},
 {"promise_id":"visual_schedule","title":"Visual schedule at class start","quote":"A visual schedule must be available at the start of each class.","category":"communication","status":"unreviewed"},
 {"promise_id":"headphones","title":"Headphones travel between classrooms","quote":"Noise-reducing headphones must travel with Kai between classrooms.","category":"equipment","status":"unreviewed"},
 {"promise_id":"substitute_summary","title":"Support summary for substitute staff","quote":"Substitute staff must receive the one-page support summary before working with Kai.","category":"staffing","status":"unreviewed"},
]

PARTICIPANTS=[
 {"participant_id":"student","role":"student","display_name":"Kai — fictional","session_status":"not_started","preference":{"term":"Calm Room","mode":"short text","why_explanations":True}},
 {"participant_id":"family","role":"family","display_name":"Morgan — fictional family member","session_status":"not_started","preference":{"mode":"text","why_explanations":True}},
 {"participant_id":"teacher","role":"teacher","display_name":"Ms. Ortiz — fictional","session_status":"not_started","preference":{"mode":"text","why_explanations":False}},
 {"participant_id":"aide","role":"support_staff","display_name":"Mr. Bell — fictional","session_status":"not_started","preference":{"mode":"text","why_explanations":False}},
]

QUESTIONS={
 "student":{"question_id":"q-student-room","text":"When you needed the Calm Room, what happened next?","why":"Your experience helps the team check whether the support was available in practice.","promise_id":"calm_room"},
 "family":{"question_id":"q-family-sub","text":"What did you learn about the substitute's access to the support summary?","why":"The plan promises that staff receive it before working with Kai.","promise_id":"substitute_summary"},
 "teacher":{"question_id":"q-teacher-room","text":"What did you observe about the Calm Room request and availability?","why":"A separate account helps the team identify agreement, conflict, or missing evidence.","promise_id":"calm_room"},
 "aide":{"question_id":"q-aide-log","text":"What operational record can confirm when the Calm Room was available?","why":"A record may clarify differing accounts without asking the system to choose who is right.","promise_id":"calm_room"},
}

def _iso(moment):return moment.astimezone(timezone.utc).isoformat().replace("+00:00","Z")
def _append(workspace,actor,action,detail,status="complete",visible_to=None):
 workspace["timeline"].append({"sequence":len(workspace["timeline"])+1,"at":_iso(BASE_TIME+timedelta(minutes=len(workspace["timeline"])*6)),"actor":actor,"action":action,"detail":detail,"status":status,"visible_to":visible_to or ["facilitator","auditor"]})

def create_workspace():
 workspace={"workspace_id":f"pk-{uuid4().hex[:8]}","synthetic":True,"status":"plan_loaded","student":{"display_name":"Kai — fictional","record_is_real":False},"plan":{"transcription":PLAN_TRANSCRIPTION,"model":"gemini-3.5-flash","mode":"recorded-replay","promises":deepcopy(PROMISES),"accuracy":{"matched":4,"total":4,"invented":0}},"participants":deepcopy(PARTICIPANTS),"questions":deepcopy(QUESTIONS),"responses":[],"ledger":[],"clarifications":[],"decisions":[],"actions":[],"followup":{"status":"not_scheduled"},"sources":deepcopy(SOURCES),"timeline":[],"safety":{"risk_score":None,"diagnosis":None,"legal_conclusion":None,"discipline_recommendation":None,"restraint_recommendation":None,"automatic_plan_change":False,"disclosure":"Plan Kept surfaces implementation evidence and disagreement. Qualified humans decide findings and repair actions."}}
 _append(workspace,"Plan reader","Four support promises verified","Each retained promise has an exact quote in the synthetic source plan.")
 return workspace

def open_perspectives(workspace):
 if workspace["status"]!="plan_loaded":raise ValueError("perspectives require a verified support plan")
 for participant in workspace["participants"]:participant["session_status"]="ready"
 workspace["status"]="perspectives_open";_append(workspace,"Partner","Four private sessions opened","Each participant sees one role-appropriate question and an explicit sharing choice.")
 return workspace

def record_response(workspace,participant_id,answer,sharing="facilitator",skipped=False):
 if workspace["status"] not in {"perspectives_open","perspectives_collected"}:raise ValueError("perspective sessions are not open")
 if sharing not in SHARING:raise ValueError("unsupported sharing choice")
 participant=next((p for p in workspace["participants"] if p["participant_id"]==participant_id),None)
 if not participant:raise ValueError("unknown participant")
 if participant["session_status"]=="complete":raise ValueError("participant response already recorded")
 question=workspace["questions"][participant_id]
 if not skipped and len(answer.strip())<2:raise ValueError("answer or explicit skip is required")
 response={"response_id":f"r-{participant_id}","participant_id":participant_id,"role":participant["role"],"question_id":question["question_id"],"promise_id":question["promise_id"],"answer":answer.strip() if not skipped else "","sharing":sharing,"skipped":skipped,"version":1,"previous":[],"included_in_synthesis":sharing!="private" and not skipped}
 workspace["responses"].append(response);participant["session_status"]="complete"
 completed=sum(p["session_status"]=="complete" for p in workspace["participants"])
 workspace["status"]="perspectives_collected" if completed==len(workspace["participants"]) else "perspectives_open"
 _append(workspace,participant["display_name"],"Perspective recorded",f"Response saved with {sharing} sharing.",visible_to=[participant_id,"facilitator"] if sharing!="private" else [participant_id])
 return workspace

def revise_response(workspace,participant_id,revised_answer,reason):
 response=next((r for r in workspace["responses"] if r["participant_id"]==participant_id),None)
 if not response:raise ValueError("response does not exist")
 if len(revised_answer.strip())<2 or len(reason.strip())<2:raise ValueError("revision and reason are required")
 response["previous"].append({"version":response["version"],"answer":response["answer"],"reason":reason.strip()});response["version"]+=1;response["answer"]=revised_answer.strip()
 _append(workspace,next(p["display_name"] for p in workspace["participants"] if p["participant_id"]==participant_id),"Response corrected","The previous version and reason were preserved.",visible_to=[participant_id,"facilitator"] if response["sharing"]!="private" else [participant_id])
 return workspace

def collect_demo_perspectives(workspace):
 if workspace["status"]!="perspectives_open":raise ValueError("open perspectives first")
 record_response(workspace,"student","I asked for the Calm Room after the hallway got loud, but the door was locked.","facilitator")
 record_response(workspace,"family","The substitute told me they did not receive the one-page support summary.","team")
 record_response(workspace,"teacher","I offered the Calm Room at 10:10 and understood that it was available.","facilitator")
 record_response(workspace,"aide","The room access log shows maintenance release at 10:25. I also noticed the headphones were in another building.","facilitator")
 return workspace

def synthesize(workspace):
 if workspace["status"]!="perspectives_collected":raise ValueError("all perspective sessions must finish before synthesis")
 usable=[r for r in workspace["responses"] if r["included_in_synthesis"]]
 if any(r["sharing"]=="private" for r in workspace["responses"] if r in usable):raise ValueError("private responses cannot enter synthesis")
 workspace["ledger"]=[
  {"promise_id":"calm_room","state":"conflicting","summary":"Student reports locked access; teacher reports an offer; staff record indicates later availability.","evidence_ids":["r-student","r-teacher","r-aide-log"],"system_truth_decision":None},
  {"promise_id":"visual_schedule","state":"unknown","summary":"No shared response addressed the visual schedule.","evidence_ids":[],"system_truth_decision":None},
  {"promise_id":"headphones","state":"reported_unavailable","summary":"Support staff reports the equipment was in another building.","evidence_ids":["r-aide-log"],"system_truth_decision":None},
  {"promise_id":"substitute_summary","state":"reported_unavailable","summary":"Family reports that the substitute did not receive the promised summary.","evidence_ids":["r-family"],"system_truth_decision":None},
 ]
 workspace["clarifications"]=[{"clarification_id":"clarify-room-access","promise_id":"calm_room","question":"Can the facilitator confirm the room-access log and substitute instructions for 10:10–10:25?","reason":"Shared accounts conflict; operational evidence may clarify availability without deciding who is truthful.","status":"open","answer":None}]
 workspace["status"]="clarification_ready";_append(workspace,"Synthesis partner","Conflict surfaced without a truth score","The partner classified agreement, conflict, and unknown; it did not identify a liar.",status="waiting")
 return workspace

def answer_clarification(workspace,answer,facilitator):
 if workspace["status"]!="clarification_ready":raise ValueError("an open clarification is required")
 if len(answer.strip())<8 or len(facilitator.strip())<3:raise ValueError("facilitator and evidence answer are required")
 clarification=workspace["clarifications"][0];clarification.update({"status":"answered","answer":answer.strip(),"answered_by":facilitator.strip()});workspace["status"]="facilitator_review"
 _append(workspace,facilitator.strip(),"Operational evidence added",answer.strip())
 return workspace

def approve_finding_and_repair(workspace,decision,facilitator):
 if workspace["status"]!="facilitator_review":raise ValueError("facilitator review is required")
 if decision not in DECISIONS or len(facilitator.strip())<3:raise ValueError("supported decision and facilitator are required")
 workspace["decisions"].append({"promise_id":"calm_room","decision":decision,"approved_by":facilitator.strip(),"made_by_ai":False,"at":_iso(BASE_TIME+timedelta(minutes=65))})
 workspace["actions"]=[
  {"action_id":"act-access","title":"Verify Calm Room access before each school day","owner":"Operations lead — synthetic","due_on":"2026-08-18","status":"approved","approved_by":facilitator.strip()},
  {"action_id":"act-substitute","title":"Add access status to the substitute support handoff","owner":"Student support lead — synthetic","due_on":"2026-08-19","status":"approved","approved_by":facilitator.strip()},
  {"action_id":"act-student","title":"Ask Kai whether the repair was available in practice","owner":"Facilitator — synthetic","due_on":"2026-08-23","status":"scheduled","approved_by":facilitator.strip()},
 ]
 workspace["followup"]={"status":"scheduled","due_on":"2026-08-23","student_confirmation":None};workspace["status"]="repair_approved"
 _append(workspace,facilitator.strip(),"Finding and repair approved",f"Human selected {decision}; three owned actions were created.")
 return workspace

def advance_followup(workspace):
 if workspace["status"]!="repair_approved":raise ValueError("approved repair is required")
 for action in workspace["actions"][:2]:action["status"]="completed_synthetic"
 workspace["followup"]["status"]="awaiting_student";workspace["status"]="followup_due"
 _append(workspace,"Follow-up agent","Student check scheduled","Two synthetic operational actions are marked complete; lived availability still requires student confirmation.",status="waiting")
 return workspace

def confirm_student_experience(workspace,experienced,note):
 if workspace["status"]!="followup_due":raise ValueError("student follow-up is not due")
 if len(note.strip())<2:raise ValueError("student note is required")
 workspace["followup"].update({"status":"complete","student_confirmation":bool(experienced),"student_note":note.strip()});workspace["actions"][2]["status"]="completed";workspace["status"]="closed"
 _append(workspace,"Kai — fictional","Repair experience recorded",note.strip(),visible_to=["student","facilitator"])
 return workspace

def role_view(workspace,role):
 if role not in {"student","family","teacher","aide","facilitator","auditor"}:raise ValueError("unknown role")
 view=public_view(workspace);allowed=[]
 for response in workspace["responses"]:
  if response["participant_id"]==role or response["sharing"]=="team" or (role=="facilitator" and response["sharing"]=="facilitator"):allowed.append(deepcopy(response))
 view["responses"]=allowed;view["timeline"]=[deepcopy(row) for row in workspace["timeline"] if role in row["visible_to"] or role in {"facilitator","auditor"} and "facilitator" in row["visible_to"]]
 return view

def public_view(workspace):
 view=deepcopy(workspace);view["metrics"]={"promises":len(workspace["plan"]["promises"]),"perspectives_complete":sum(p["session_status"]=="complete" for p in workspace["participants"]),"conflicts":sum(r["state"]=="conflicting" for r in workspace["ledger"]),"repair_actions":len(workspace["actions"]),"private_responses":sum(r["sharing"]=="private" for r in workspace["responses"]),"ai_truth_decisions":0};return view

def run_full_demo():
 workspace=create_workspace();open_perspectives(workspace);collect_demo_perspectives(workspace);synthesize(workspace);answer_clarification(workspace,"The access log confirms the room was unavailable until 10:25, and the substitute handoff omitted access status.","Riley Shah, facilitator — synthetic");approve_finding_and_repair(workspace,"implementation_gap","Riley Shah, facilitator — synthetic");advance_followup(workspace);confirm_student_experience(workspace,True,"The Calm Room was unlocked when I asked this time.");return public_view(workspace)

