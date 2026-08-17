from plan_kept.pilot import create_pilot_workspace


def payload():
    quote = "Student A may request a quiet workspace during transitions."
    return {
        "synthetic_acknowledgement": True,
        "data_class": "synthetic",
        "case_reference": "Fictional support review A-17",
        "student_reference": "Student A - fictional",
        "plan_transcription": f"FICTIONAL PLAN\n{quote}\nThis is not a real education record.",
        "promises": [{"title": "Quiet workspace access", "quote": quote, "category": "environment"}],
        "participants": {
            "student": "Student A - fictional",
            "family": "Family participant - fictional",
            "teacher": "Teacher participant - fictional",
            "aide": "Support participant - fictional",
        },
    }


def test_custom_workspace_uses_supplied_fictional_plan():
    workspace = create_pilot_workspace(payload())
    assert workspace["origin"] == "pilot_input"
    assert workspace["student"]["record_is_real"] is False
    assert workspace["plan"]["promises"][0]["title"] == "Quiet workspace access"
    assert workspace["plan"]["promises"][0]["quote"] in workspace["plan"]["transcription"]
    assert workspace["questions"]["student"]["promise_id"] == "promise-1"
    assert len(workspace["workspace_id"]) > 30


def test_custom_workspace_rejects_nonfictional_or_unquoted_promise():
    bad = payload()
    bad["data_class"] = "real"
    try:
        create_pilot_workspace(bad)
        assert False
    except ValueError as exc:
        assert "fictional" in str(exc)
    bad = payload()
    bad["promises"][0]["quote"] = "This sentence is absent."
    try:
        create_pilot_workspace(bad)
        assert False
    except ValueError as exc:
        assert "exactly" in str(exc)
