"""Explicit live Vertex recording for the synthetic Plan Kept fixture."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from plan_kept.reader import PlanReader, VertexPlanClient

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--mime-type", default="image/png")
    args = parser.parse_args()
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT is required")
    result = PlanReader(VertexPlanClient(project)).read(args.image.read_bytes(), args.mime_type)
    truth = json.loads((ROOT / "fixtures" / "plan.truth.json").read_text(encoding="utf-8"))
    supports = [field for field in result.fields if field["key"] == "support"]
    report = {
        "model": "gemini-3.5-flash",
        "mode": "live-vertex-recording",
        "project": project,
        "transcription": result.transcription,
        "fields": result.fields,
        "dropped": result.dropped,
        "grade": {
            "expected_support_quotes": truth["expected_support_quotes"],
            "retained_support_quotes": len(supports),
            "all_quotes_verified": all(f["quote"] in result.transcription for f in result.fields),
        },
    }
    target = ROOT / "fixtures" / "plan.recording.json"
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["grade"], indent=2))
    print(f"recorded {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


