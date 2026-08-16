from __future__ import annotations
import os
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from plan_kept.store import FirestoreWorkspaceStore,MemoryWorkspaceStore
from service.hardening_routes import build_hardening_router
from service.routes import build_router
from service.runtime import build_runtime
from spine.http_trace import install_http_tracing

PROJECT=os.environ.get("GOOGLE_CLOUD_PROJECT","local")
USE_FIRESTORE=os.environ.get("USE_FIRESTORE","").lower() in {"1","true","yes"}
if USE_FIRESTORE:
 from google.cloud import firestore
 workspace_store=FirestoreWorkspaceStore(firestore.Client(project=PROJECT));persistence="firestore"
else: workspace_store=MemoryWorkspaceStore();persistence="memory-local"
clock,wake_scheduler=build_runtime(PROJECT,USE_FIRESTORE)
app=FastAPI(title="Plan Kept",description="Privacy-aware promise-to-reality partner for existing student supports.",version="0.2.0")
trace_status=install_http_tracing(app,PROJECT,"plan-kept")
app.include_router(build_router(workspace_store));app.include_router(build_hardening_router(workspace_store,wake_scheduler,clock))
WEB=Path(__file__).resolve().parent.parent/"web";app.mount("/static",StaticFiles(directory=WEB),name="static")

@app.get("/health")
def health()->dict[str,Any]:
 return {"ok":True,"project":"plan-kept","google_cloud_project":PROJECT,"persistence":persistence,"synthetic_demo":True,"decisions":"qualified-human-only","model":"gemini-3.5-flash","tracing":trace_status,"durable_wakes":"firestore-transactional" if USE_FIRESTORE else "memory-transactional","simulation_clock":True,"role_views":"token-gated-demo"}
@app.get("/",include_in_schema=False)
def index():return FileResponse(WEB/"index.html")
@app.get("/judges",include_in_schema=False)
def judges():return FileResponse(WEB/"hardening.html")
@app.get("/judges/architecture",include_in_schema=False)
def architecture_brief():return FileResponse(WEB/"judges.html")

