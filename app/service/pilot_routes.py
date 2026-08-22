"""Typed public-sandbox routes for custom fictional Plan Kept workspaces."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from plan_kept.pilot import create_pilot_workspace
from plan_kept.store import WorkspaceStore
from plan_kept.workflow import advance_safe_automation, public_view


class PromiseInput(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    quote: str = Field(min_length=8, max_length=1200)
    category: str = Field(default="support", min_length=2, max_length=80)


class ParticipantInput(BaseModel):
    student: str = Field(min_length=2, max_length=120)
    family: str = Field(min_length=2, max_length=120)
    teacher: str = Field(min_length=2, max_length=120)
    aide: str = Field(min_length=2, max_length=120)


class PilotWorkspaceRequest(BaseModel):
    synthetic_acknowledgement: Literal[True]
    data_class: Literal["synthetic"] = "synthetic"
    case_reference: str = Field(min_length=3, max_length=120)
    student_reference: str = Field(min_length=2, max_length=120)
    plan_transcription: str = Field(min_length=20, max_length=8000)
    promises: list[PromiseInput] = Field(min_length=1, max_length=6)
    participants: ParticipantInput


def _summary(workspace: dict[str, Any]) -> dict[str, Any]:
    return {
        "workspace_id": workspace["workspace_id"],
        "status": workspace["status"],
        "case_reference": workspace.get("case_reference", workspace["student"]["display_name"]),
        "student_reference": workspace["student"]["display_name"],
        "promises": len(workspace["plan"]["promises"]),
        "origin": workspace.get("origin", "sample_fixture"),
        "created_at": workspace.get("created_at", "2026-08-16T13:00:00Z"),
    }


def build_pilot_router(store: WorkspaceStore) -> APIRouter:
    router = APIRouter(prefix="/api/pilot", tags=["plan-kept-pilot"])

    @router.get("/workspaces")
    def list_workspaces() -> dict[str, Any]:
        workspaces = store.list_workspaces()
        return {"workspaces": [_summary(item) for item in workspaces], "count": len(workspaces)}

    @router.post("/workspaces")
    def open_workspace(request: PilotWorkspaceRequest) -> dict[str, Any]:
        try:
            workspace = create_pilot_workspace(request.model_dump())
            advance_safe_automation(workspace)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        store.put(workspace)
        return public_view(workspace)

    @router.get("/readiness")
    def readiness() -> dict[str, Any]:
        return {
            "level": "public fictional operational sandbox",
            "working_now": [
                "custom fictional plan intake",
                "exact-quote promise validation",
                "multiple durable workspaces",
                "participant-controlled response sharing",
                "human-only findings and repair approval",
            ],
            "public_data_policy": "fictional-synthetic-only",
            "required_for_education_records": [
                "school identity, role authorization, and tenant isolation",
                "contractual authority, consent, access, disclosure, retention, and deletion controls",
                "validated plan-system connectors and qualified stakeholder review",
            ],
            "claim": "Plan Kept is not represented as a student-record or plan-management system.",
        }

    return router
