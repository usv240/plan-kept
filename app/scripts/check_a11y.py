"""Static accessibility gate; rendered browser review is a separate release gate."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
landing = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
judges = (ROOT / "web" / "judges.html").read_text(encoding="utf-8")
styles = (ROOT / "web" / "styles.css").read_text(encoding="utf-8")

checks = {
    "landing has one h1": landing.count("<h1") == 1,
    "judge page has one h1": judges.count("<h1") == 1,
    "skip links exist": "skip-link" in landing and "skip-link" in judges,
    "theme controls are buttons": 'id="theme-toggle"' in landing and 'id="theme-toggle"' in judges,
    "live updates are announced": 'aria-live="polite"' in landing,
    "tabs expose roles": 'role="tablist"' in landing and 'role="tabpanel"' in landing,
    "reduced motion is respected": "prefers-reduced-motion" in styles,
    "mobile breakpoint exists": "max-width:760px" in styles,
    "focus visible is styled": ":focus-visible" in styles,
    "privacy is stated in text": "Private responses never enter synthesis" in landing,
}

for name, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'}  {name}")
raise SystemExit(0 if all(checks.values()) else 1)
