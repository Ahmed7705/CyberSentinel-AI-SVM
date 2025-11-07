"""Lightweight result reporter for the verification suite."""
from __future__ import annotations

from typing import Dict

_STATUS_OK = "OK"
_STATUS_FAIL = "FAIL"
_STATUS_PENDING = "PENDING"

_ORDER = [
    "Auth",
    "Role-based access",
    "Dashboards (admin/user)",
    "Database connectivity & FKs",
    "AI training",
    "AI detection (late-night, mass-copy, remote-script)",
    "Alerts persisted with risk levels",
    "Instant notifications",
    "Templates UTF-8 & static assets",
    "Overall system integrity",
]

_statuses: Dict[str, Dict[str, str]] = {name: {"status": _STATUS_PENDING, "suggestion": ""} for name in _ORDER}


def mark_ok(name: str) -> None:
    _statuses[name] = {"status": _STATUS_OK, "suggestion": ""}


def mark_fail(name: str, suggestion: str) -> None:
    _statuses[name] = {"status": _STATUS_FAIL, "suggestion": suggestion}


def pending_items() -> Dict[str, Dict[str, str]]:
    return _statuses


def emit_final_report(overall_success: bool) -> None:
    if overall_success:
        mark_ok("Overall system integrity")
    elif _statuses["Overall system integrity"]["status"] == _STATUS_PENDING:
        mark_fail("Overall system integrity", "See failing tests above.")

    for name in _ORDER:
        entry = _statuses[name]
        if entry["status"] == _STATUS_OK:
            print(f"? {name}: OK")
        elif entry["status"] == _STATUS_FAIL:
            suggestion = entry["suggestion"] or "Investigate failing tests."
            print(f"? {name}: FAIL — Suggested fix: {suggestion}")
        else:
            print(f"?? {name}: Pending — Suggested fix: ensure corresponding tests set reporter status.")

    if overall_success:
        print("? Overall system integrity: PASSED")
    else:
        print("? Overall system integrity: FAILED")
