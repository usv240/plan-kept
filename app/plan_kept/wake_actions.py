from __future__ import annotations

from plan_kept.workflow import advance_followup


class PlanKeptWakeExecutor:
    def __init__(self, store): self.store = store

    def execute(self, wake):
        workspace = self.store.get(wake.run_id)
        if workspace is None: raise ValueError(f"missing workspace {wake.run_id}")
        actions = workspace.setdefault("wake_actions", [])
        if any(row["wake_id"] == wake.wake_id for row in actions): return
        if wake.kind != "student_followup": raise ValueError(f"unsupported wake kind {wake.kind}")
        advance_followup(workspace)
        actions.append({"wake_id": wake.wake_id, "kind": wake.kind, "external_contact": False, "student_answer_inferred": False})
        self.store.put(workspace)

