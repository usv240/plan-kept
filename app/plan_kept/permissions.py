from __future__ import annotations

import hmac

from plan_kept.workflow import role_view


DEMO_ROLE_TOKENS = {role: f"demo-{role}-token" for role in ("student", "family", "teacher", "aide", "facilitator", "auditor")}


def authenticated_role_view(workspace, role, token):
    expected = DEMO_ROLE_TOKENS.get(role)
    if expected is None or not hmac.compare_digest(token or "", expected):
        raise PermissionError("role token does not authorize this view")
    return role_view(workspace, role)

