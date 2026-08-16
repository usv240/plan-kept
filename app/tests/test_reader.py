import json
from pathlib import Path

import pytest

from plan_kept.reader import PlanReader, ReplayPlanClient

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "plan.recording.json"


def test_recorded_read_keeps_only_exact_quotes():
    result = PlanReader(ReplayPlanClient.from_path(FIXTURE)).read(b"synthetic")
    assert len(result.fields) == 7
    assert not result.dropped
    assert all(field["quote"] in result.transcription for field in result.fields)


def test_reader_drops_hallucinated_quote_and_bad_key():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["fields"].extend(
        [
            {"key": "support", "value": "invented", "quote": "not present", "confidence": 0.8},
            {"key": "diagnosis", "value": "forbidden", "quote": "Student", "confidence": 0.8},
        ]
    )
    result = PlanReader(ReplayPlanClient(payload)).read(b"synthetic")
    assert len(result.fields) == 7
    assert len(result.dropped) == 2


def test_reader_requires_document_and_transcription():
    with pytest.raises(ValueError):
        PlanReader(ReplayPlanClient({})).read(b"")
    with pytest.raises(ValueError):
        PlanReader(ReplayPlanClient({"transcription": "", "fields": []})).read(b"x")


