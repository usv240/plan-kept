"""Executable Plan Kept acceptance flow against a local or deployed service."""

from __future__ import annotations

import argparse
import json
from urllib.request import Request, urlopen


def call(base: str, method: str, path: str, body: dict | None = None):
    payload = json.dumps(body or {}).encode("utf-8") if method == "POST" else None
    request = Request(
        f"{base.rstrip('/')}{path}", data=payload, method=method,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=20) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    checks: list[bool] = []

    def check(name: str, condition: bool):
        checks.append(bool(condition))
        print(f"{'PASS' if condition else 'FAIL'}  {name}")

    _, health = call(args.url, "GET", "/health")
    check("health identifies Plan Kept", health["project"] == "plan-kept")
    check("decisions stay human-only", health["decisions"] == "qualified-human-only")
    _, workspace = call(args.url, "POST", "/api/workspaces")
    workspace_id = workspace["workspace_id"]
    check("fictional plan has four quote-grounded promises", workspace["plan"]["accuracy"] == {"matched": 4, "total": 4, "invented": 0})
    for endpoint in ["open-perspectives", "demo-perspectives", "synthesize"]:
        _, workspace = call(args.url, "POST", f"/api/workspaces/{workspace_id}/{endpoint}")
    check("conflict becomes clarification, not truth score", workspace["ledger"][0]["state"] == "conflicting" and workspace["ledger"][0]["system_truth_decision"] is None)
    _, workspace = call(args.url, "POST", f"/api/workspaces/{workspace_id}/clarification", {"answer": "The access log confirms the room was unavailable until 10:25.", "facilitator": "Riley Shah - synthetic"})
    _, workspace = call(args.url, "POST", f"/api/workspaces/{workspace_id}/repair", {"decision": "implementation_gap", "facilitator": "Riley Shah - synthetic"})
    check("named facilitator, not AI, approves repair", workspace["decisions"][0]["made_by_ai"] is False)
    check("every action has an owner and due date", all(a["owner"] and a["due_on"] for a in workspace["actions"]))
    _, workspace = call(args.url, "POST", f"/api/workspaces/{workspace_id}/followup")
    _, workspace = call(args.url, "POST", f"/api/workspaces/{workspace_id}/confirm", {"experienced": True, "note": "It was available this time."})
    check("student experience closes the loop", workspace["status"] == "closed")
    _, proof = call(args.url, "GET", "/api/proof")
    check("executable privacy and safety proof is green", proof["passed"] == proof["total"])
    print(f"\n{sum(checks)}/{len(checks)} checks passed")
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
