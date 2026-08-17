from pathlib import Path


WEB = Path(__file__).resolve().parent.parent / "web"


def test_public_ui_has_custom_queue_perspectives_and_no_global_reset():
    html = (WEB / "index.html").read_text(encoding="utf-8")
    js = (WEB / "app.js").read_text(encoding="utf-8")
    pilot = (WEB / "pilot.js").read_text(encoding="utf-8")
    assert "New workspace" in html and 'id="workspace-select"' in html
    assert 'id="workspace-dialog"' in html and 'id="perspective-dialog"' in html
    assert "/api/pilot/readiness" in html and "/api/reset" not in js + pilot
    assert "For judges" not in html and "Judge brief" not in html
