from __future__ import annotations
from datetime import timedelta
from typing import Any
from fastapi import APIRouter,HTTPException,Query
from pydantic import BaseModel,Field
from plan_kept.store import WorkspaceStore
from spine.public_trace import public_action_trace
from plan_kept.workflow import advance_safe_automation,answer_clarification,approve_finding_and_repair,advance_followup,collect_demo_perspectives,confirm_student_experience,create_workspace,open_perspectives,public_view,record_response,revise_response,role_view,run_full_demo,synthesize

class ResponseRequest(BaseModel):
 participant_id:str
 answer:str=Field(default="",max_length=1500)
 sharing:str="facilitator"
 skipped:bool=False
class RevisionRequest(BaseModel):
 revised_answer:str=Field(min_length=2,max_length=1500)
 reason:str=Field(min_length=2,max_length=500)
class ClarificationRequest(BaseModel):
 answer:str=Field(min_length=8,max_length=1500)
 facilitator:str=Field(min_length=3,max_length=140)
class RepairRequest(BaseModel):
 decision:str
 facilitator:str=Field(min_length=3,max_length=140)
class ConfirmationRequest(BaseModel):
 experienced:bool
 note:str=Field(min_length=2,max_length=800)

def build_router(store:WorkspaceStore,scheduler=None,allow_global_reset:bool=False,model_runner=None)->APIRouter:
 router=APIRouter(prefix="/api",tags=["plan-kept"])
 def require(workspace_id):
  workspace=store.get(workspace_id)
  if workspace is None:raise HTTPException(status_code=404,detail=f"no workspace {workspace_id}")
  return workspace
 def mutate(workspace_id,operation):
  workspace=require(workspace_id)
  try:operation(workspace)
  except ValueError as exc:raise HTTPException(status_code=409,detail=str(exc)) from exc
  store.put(workspace);return public_view(workspace)
 @router.post("/workspaces")
 def open_workspace():
  workspace=create_workspace();advance_safe_automation(workspace);store.put(workspace);return public_view(workspace)
 @router.get("/workspaces/{workspace_id}")
 def get_workspace(workspace_id:str,role:str|None=Query(default=None)):
  workspace=require(workspace_id)
  try:return role_view(workspace,role) if role else public_view(workspace)
  except ValueError as exc:raise HTTPException(status_code=400,detail=str(exc)) from exc
 @router.get("/workspaces/{workspace_id}/trace")
 def get_workspace_trace(workspace_id:str):return public_action_trace(require(workspace_id),"workspace_id")
 @router.get("/workspaces/{workspace_id}/autonomy-proof")
 def get_workspace_autonomy_proof(workspace_id:str):return public_view(require(workspace_id))["autonomy_proof"]
 @router.post("/workspaces/{workspace_id}/autopilot")
 def autopilot(workspace_id:str):return mutate(workspace_id,advance_safe_automation)
 @router.post("/workspaces/{workspace_id}/open-perspectives")
 def perspectives(workspace_id:str):return mutate(workspace_id,open_perspectives)
 @router.post("/workspaces/{workspace_id}/demo-perspectives")
 def demo_perspectives(workspace_id:str):return mutate(workspace_id,lambda w:(collect_demo_perspectives(w),advance_safe_automation(w)))
 @router.post("/workspaces/{workspace_id}/responses")
 def response(workspace_id:str,request:ResponseRequest):return mutate(workspace_id,lambda w:(record_response(w,request.participant_id,request.answer,request.sharing,request.skipped),advance_safe_automation(w)))
 @router.post("/workspaces/{workspace_id}/responses/{participant_id}/revise")
 def revise(workspace_id:str,participant_id:str,request:RevisionRequest):return mutate(workspace_id,lambda w:revise_response(w,participant_id,request.revised_answer,request.reason))
 @router.post("/workspaces/{workspace_id}/synthesize")
 def synthesis(workspace_id:str):return mutate(workspace_id,synthesize)
 @router.post("/workspaces/{workspace_id}/clarification")
 def clarification(workspace_id:str,request:ClarificationRequest):return mutate(workspace_id,lambda w:answer_clarification(w,request.answer,request.facilitator))
 @router.post("/workspaces/{workspace_id}/repair")
 def repair(workspace_id:str,request:RepairRequest):
  def approve_and_schedule(workspace):
   approve_finding_and_repair(workspace,request.decision,request.facilitator)
   if scheduler is not None:
    wake=scheduler.sleep_for(workspace_id,"student_followup",timedelta(days=7))
    workspace["followup"]["wake_id"]=wake.wake_id
   workspace["last_autonomy_run"]={"actions":["student_followup_scheduled"],"stopped_at":"repair_approved","waiting_for":"scheduled_student_followup"}
  return mutate(workspace_id,approve_and_schedule)
 @router.post("/workspaces/{workspace_id}/followup")
 def followup(workspace_id:str):return mutate(workspace_id,advance_followup)
 @router.post("/workspaces/{workspace_id}/confirm")
 def confirm(workspace_id:str,request:ConfirmationRequest):return mutate(workspace_id,lambda w:confirm_student_experience(w,request.experienced,request.note))
 @router.post("/demo/full")
 def full_demo():
  workspace=create_workspace()
  if model_runner is not None:
   try:model_runner.apply(workspace)
   except Exception as exc:raise HTTPException(status_code=503,detail="live model evidence unavailable; no replay substituted") from exc
  workspace=run_full_demo(workspace);store.put(workspace);return workspace
 @router.get("/model-evidence")
 def model_evidence():
  return {"execution":"POST /api/demo/full returns live, fail-closed model receipts","models":[{"name":"gemini-3.5-flash","purpose":"quote-grounded fictional artifact extraction","docs":"https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-5-flash"},{"name":"gemini-embedding-001","purpose":"semantic evidence routing without truth or authority decisions","docs":"https://docs.cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings"}],"replay_policy":"recorded outputs are test-only; deployed full workflows do not silently substitute them"}
 @router.post("/reset")
 def reset():
  if not allow_global_reset:raise HTTPException(status_code=403,detail="global reset is disabled in this deployment")
  store.clear();return {"ok":True}
 @router.get("/research")
 def research():
  workspace=create_workspace();return {"sources":list(workspace["sources"].values()),"prior_art":[{"title":"RecordHQ","url":"https://recordhq.co.uk/","boundary":"pupil/staff debrief, actions, notifications, analytics"},{"title":"Cairn","url":"https://cairn.school/","boundary":"conversational incident reporting, follow-up, and analytics"},{"title":"MangoApps restraint/seclusion template","url":"https://www.mangoapps.com/templates/forms/seclusion-and-restraint-incident-reporting-and-debrief-form","boundary":"incident documentation, debrief, prevention, and follow-up"}],"our_boundary":"promise-to-reality ledger for existing supports, participant-controlled sharing, conflict without truth scoring, and lived-experience repair confirmation","claim_boundary":"Research supports the problem and collaborative/trauma-informed principles. It does not validate Plan Kept or prove incident prevention."}
 @router.get("/proof")
 def proof():
  checks=[]
  def check(name,passed,detail=""):checks.append({"check":name,"pass":bool(passed),"detail":detail})
  workspace=create_workspace();check("all promises have exact plan quotes",all(p["quote"] in workspace["plan"]["transcription"] for p in workspace["plan"]["promises"]));check("no prohibited prediction or recommendation is produced",all(workspace["safety"][key] is None for key in ["risk_score","diagnosis","legal_conclusion","discipline_recommendation","restraint_recommendation"]));open_perspectives(workspace);record_response(workspace,"student","A private statement","private");check("private response is absent from facilitator view",not role_view(workspace,"facilitator")["responses"]);record_response(workspace,"family","Substitute did not receive the summary","team");record_response(workspace,"teacher","The room was offered","facilitator");record_response(workspace,"aide","The access log shows later availability","facilitator");synthesize(workspace);check("private response is excluded from synthesis",not workspace["responses"][0]["included_in_synthesis"]);check("conflict creates no system truth decision",workspace["ledger"][0]["state"]=="conflicting" and workspace["ledger"][0]["system_truth_decision"] is None);check("conflict creates a targeted clarification",workspace["clarifications"][0]["status"]=="open");answer_clarification(workspace,"The access log confirms the room was unavailable until 10:25.","Riley Shah - synthetic");approve_finding_and_repair(workspace,"implementation_gap","Riley Shah - synthetic");check("finding records named human authority",workspace["decisions"][0]["made_by_ai"] is False);check("repair actions have owners and due dates",all(a["owner"] and a["due_on"] for a in workspace["actions"]));advance_followup(workspace);confirm_student_experience(workspace,True,"It was available this time.");check("student experience closes the repair loop",workspace["status"]=="closed" and workspace["followup"]["student_confirmation"] is True);check("timeline is ordered",[r["sequence"] for r in workspace["timeline"]]==list(range(1,len(workspace["timeline"])+1)));return {"passed":sum(r["pass"] for r in checks),"total":len(checks),"checks":checks}
 @router.get("/conformance")
 def conformance():return {"category":"The Collaborative Partner","requirements":[{"requirement":"asks clarifying questions","implementation":"one role-appropriate question at a time plus conflict-targeted clarification","proof":"questions and clarification state"},{"requirement":"captures feedback and adapts","implementation":"skip, sharing, revision history, communication preferences, student confirmation","proof":"response and role-view tests"},{"requirement":"persistent memory","implementation":"bounded preferences, promises, decisions, and actions rather than transcript replay","proof":"workspace document"},{"requirement":"guides step-by-step","implementation":"plan -> perspectives -> synthesis -> clarification -> human decision -> repair -> follow-up","proof":"live workspace and demo script"}],"limitations":["All people, school, plan, responses, records, and actions are fictional.","The system does not diagnose, predict danger, recommend discipline or restraint, decide legality, or modify a support plan.","Some cited intervention evidence comes from clinical rather than ordinary K-12 settings.","No prevention outcome has been validated."]}
 return router

