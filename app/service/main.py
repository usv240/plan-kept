from __future__ import annotations
import os
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from plan_kept.store import FirestoreWorkspaceStore,MemoryWorkspaceStore
from plan_kept.live_evidence import LiveEvidenceRunner
from service.hardening_routes import build_hardening_router
from service.pilot_routes import build_pilot_router
from service.routes import build_router
from service.runtime import build_runtime
from service.scheduler_routes import build_scheduler_router
from spine.http_trace import install_http_tracing

PROJECT=os.environ.get("GOOGLE_CLOUD_PROJECT","local")
USE_FIRESTORE=os.environ.get("USE_FIRESTORE","").lower() in {"1","true","yes"}
ALLOW_GLOBAL_RESET=os.environ.get("ALLOW_GLOBAL_RESET","").lower() in {"1","true","yes"}
ENABLE_LIVE_MODELS=os.environ.get("ENABLE_LIVE_MODELS","").lower() in {"1","true","yes"}
GOOGLE_SERVICES=[
 {"name":"Gemini 3.5 Flash on Vertex AI","role":"Live fail-closed grounded plan extraction"},
 {"name":"Google Gen AI SDK","role":"Required Google agent framework"},
 {"name":"Gemini Embedding 001","role":"Semantic support-focus routing; never truth or authority decisions"},
 {"name":"Cloud Run","role":"Public collaborative workspace service"},
 {"name":"Firestore","role":"Durable workspaces and transactional wake state"},
 {"name":"Cloud Scheduler","role":"OIDC-authenticated follow-up wake scans"},
 {"name":"Cloud Trace","role":"End-to-end request observability"},
]
if USE_FIRESTORE:
 from google.cloud import firestore
 workspace_store=FirestoreWorkspaceStore(firestore.Client(project=PROJECT));persistence="firestore"
else: workspace_store=MemoryWorkspaceStore();persistence="memory-local"
clock,wake_scheduler=build_runtime(PROJECT,USE_FIRESTORE)
app=FastAPI(title="Plan Kept",description="Privacy-aware promise-to-reality partner for existing student supports.",version="0.2.0")
trace_status=install_http_tracing(app,PROJECT,"plan-kept")
model_runner=LiveEvidenceRunner(PROJECT,Path(__file__).resolve().parent.parent/"web") if ENABLE_LIVE_MODELS else None
app.include_router(build_router(workspace_store,wake_scheduler,ALLOW_GLOBAL_RESET,model_runner));app.include_router(build_pilot_router(workspace_store));app.include_router(build_hardening_router(workspace_store,wake_scheduler,clock))
app.include_router(build_scheduler_router(workspace_store,wake_scheduler))
WEB=Path(__file__).resolve().parent.parent/"web";app.mount("/static",StaticFiles(directory=WEB),name="static")

@app.get("/health")
def health()->dict[str,Any]:
 return {"ok":True,"project":"plan-kept","google_cloud_project":PROJECT,"persistence":persistence,"synthetic_demo":True,"operating_mode":"public-fictional-sandbox","public_data_policy":"fictional-synthetic-only","global_reset":ALLOW_GLOBAL_RESET,"decisions":"qualified-human-only","model":"gemini-3.5-flash","models":["gemini-3.5-flash","gemini-embedding-001"],"model_mode":"live-fail-closed" if ENABLE_LIVE_MODELS else "local-test-no-model","tracing":trace_status,"durable_wakes":"firestore-transactional" if USE_FIRESTORE else "memory-transactional","simulation_clock":True,"autonomy":"adaptive-partner-auto-continuation","role_views":"token-gated-demo","google_services":GOOGLE_SERVICES}
@app.get("/",include_in_schema=False)
def index():return FileResponse(WEB/"index.html")
