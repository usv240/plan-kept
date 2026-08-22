"""Stable authenticated API for Plan Kept integrations."""
from __future__ import annotations
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException

from plan_kept.pilot import create_pilot_workspace
from plan_kept.store import WorkspaceStore
from plan_kept.workflow import advance_followup, advance_safe_automation, answer_clarification, approve_finding_and_repair, confirm_student_experience, create_workspace, public_view, record_response, revise_response, run_full_demo
from service.pilot_routes import PilotWorkspaceRequest
from service.routes import ClarificationRequest, ConfirmationRequest, RepairRequest, ResponseRequest, RevisionRequest
from spine.developer_access import DeveloperAccessManager, api_key_guard
from spine.public_trace import public_action_trace


def build_developer_router(store: WorkspaceStore, access: DeveloperAccessManager, scheduler=None, *, model_runner=None) -> APIRouter:
    router = APIRouter(prefix="/v1", tags=["Plan Kept v1"], dependencies=[Depends(api_key_guard(access))])

    def require(workspace_id: str) -> dict[str, Any]:
        workspace = store.get(workspace_id)
        if workspace is None:
            raise HTTPException(status_code=404, detail=f"no workspace {workspace_id}")
        return workspace

    def save(workspace: dict[str, Any]) -> dict[str, Any]:
        store.put(workspace)
        return public_view(workspace)

    def mutate(workspace_id: str, operation: Any) -> dict[str, Any]:
        workspace = require(workspace_id)
        try:
            operation(workspace)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return save(workspace)

    @router.post("/workspaces", status_code=201)
    def create(payload: PilotWorkspaceRequest) -> dict[str, Any]:
        try:
            workspace = create_pilot_workspace(payload.model_dump())
            advance_safe_automation(workspace)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return save(workspace)

    @router.get("/workspaces/{workspace_id}")
    def read(workspace_id: str) -> dict[str, Any]:
        return public_view(require(workspace_id))

    @router.post("/workspaces/{workspace_id}/responses")
    def response(workspace_id: str, payload: ResponseRequest) -> dict[str, Any]:
        return mutate(workspace_id, lambda w: (record_response(w, payload.participant_id, payload.answer, payload.sharing, payload.skipped), advance_safe_automation(w)))

    @router.post("/workspaces/{workspace_id}/responses/{participant_id}/revisions")
    def revision(workspace_id: str, participant_id: str, payload: RevisionRequest) -> dict[str, Any]:
        return mutate(workspace_id, lambda w: revise_response(w, participant_id, payload.revised_answer, payload.reason))

    @router.post("/workspaces/{workspace_id}/clarification-evidence")
    def clarification(workspace_id: str, payload: ClarificationRequest) -> dict[str, Any]:
        return mutate(workspace_id, lambda w: answer_clarification(w, payload.answer, payload.facilitator))

    @router.post("/workspaces/{workspace_id}/repair-decisions")
    def repair(workspace_id: str, payload: RepairRequest) -> dict[str, Any]:
        def approve(workspace: dict[str, Any]) -> None:
            approve_finding_and_repair(workspace, payload.decision, payload.facilitator)
            if scheduler is not None:
                wake = scheduler.sleep_for(workspace_id, "student_followup", timedelta(days=7))
                workspace["followup"]["wake_id"] = wake.wake_id
            workspace["last_autonomy_run"] = {"actions": ["student_followup_scheduled"], "stopped_at": "repair_approved", "waiting_for": "scheduled_student_followup"}
            workspace.setdefault("autonomy_runs", []).append(dict(workspace["last_autonomy_run"]))
        return mutate(workspace_id, approve)

    @router.post("/workspaces/{workspace_id}/followup-wake-events")
    def followup(workspace_id: str) -> dict[str, Any]:
        return mutate(workspace_id, advance_followup)

    @router.post("/workspaces/{workspace_id}/student-confirmations")
    def confirmation(workspace_id: str, payload: ConfirmationRequest) -> dict[str, Any]:
        return mutate(workspace_id, lambda w: confirm_student_experience(w, payload.experienced, payload.note))

    @router.get("/workspaces/{workspace_id}/trace")
    def trace(workspace_id: str) -> dict[str, Any]:
        return public_action_trace(require(workspace_id), "workspace_id")

    @router.get("/workspaces/{workspace_id}/autonomy-proof")
    def autonomy(workspace_id: str) -> dict[str, Any]:
        return public_view(require(workspace_id))["autonomy_proof"]

    @router.post("/tabletop-runs", status_code=201)
    def tabletop() -> dict[str, Any]:
        workspace = create_workspace()
        if model_runner is not None:
            try:
                model_runner.apply(workspace)
            except Exception as exc:
                raise HTTPException(status_code=503, detail="live Gemini evidence unavailable; no replay substituted") from exc
        result = run_full_demo(workspace)
        store.put(workspace)
        return result

    return router
