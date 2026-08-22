"""Executable Plan Kept autonomy acceptance flow."""
from __future__ import annotations
import argparse,json
from urllib.request import Request,urlopen

def call(base,method,path,body=None):
 data=json.dumps(body or {}).encode() if method=="POST" else None
 with urlopen(Request(base.rstrip("/")+path,data=data,method=method,headers={"Content-Type":"application/json"}),timeout=20) as response:return response.status,json.loads(response.read())
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--url",default="http://127.0.0.1:8000");args=parser.parse_args();checks=[]
 def check(name,value):checks.append(bool(value));print(f"{'PASS' if value else 'FAIL'}  {name}")
 _,health=call(args.url,"GET","/health");check("health identifies Plan Kept",health["project"]=="plan-kept");check("health exposes adaptive partner autonomy",health["autonomy"]=="adaptive-partner-auto-continuation");check("qualified people retain decision authority",health["decisions"]=="qualified-human-only")
 _,workspace=call(args.url,"POST","/api/workspaces");workspace_id=workspace["workspace_id"];check("verified plan automatically opens role sessions",workspace["status"]=="perspectives_open" and workspace["autonomy"]["last_run_actions"]==["role_sessions_opened"])
 _,workspace=call(args.url,"POST",f"/api/workspaces/{workspace_id}/demo-perspectives");check("final perspective automatically triggers synthesis",workspace["status"]=="clarification_ready" and workspace["autonomy"]["last_run_actions"]==["shared_evidence_synthesized"]);check("conflict creates no system truth decision",workspace["ledger"][0]["state"]=="conflicting" and workspace["ledger"][0]["system_truth_decision"] is None)
 _,workspace=call(args.url,"POST",f"/api/workspaces/{workspace_id}/clarification",{"answer":"The access log confirms the room was unavailable until 10:25.","facilitator":"Riley Shah - synthetic"})
 _,workspace=call(args.url,"POST",f"/api/workspaces/{workspace_id}/repair",{"decision":"implementation_gap","facilitator":"Riley Shah - synthetic"});check("repair remains a named human decision",workspace["decisions"][0]["made_by_ai"] is False);check("repair automatically registers durable follow-up",workspace["status"]=="repair_approved" and bool(workspace["followup"].get("wake_id")))
 _,demo=call(args.url,"POST","/api/demo/full");check("one-request demo closes on student experience",demo["autonomy"]["complete"] and demo["followup"]["student_confirmation"] is True)
 _,proof=call(args.url,"GET","/api/proof");check("privacy and safety proof is green",proof["passed"]==proof["total"])
 print()
 print(f"{sum(checks)}/{len(checks)} checks passed");return 0 if all(checks) else 1
if __name__=="__main__":raise SystemExit(main())