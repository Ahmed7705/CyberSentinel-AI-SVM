from __future__ import annotations

from pathlib import Path

from tests import _reporter as reporter

TEMPLATES = [
    "base.html",
    "login.html",
    "admin-dashboard.html",
    "user-dashboard.html",
    "alerts.html",
    "reports.html",
    "users.html",
]

ASSETS = [
    Path("static/assets/bootstrap/css/bootstrap.min.css"),
    Path("static/assets/bootstrap/js/bootstrap.bundle.min.js"),
    Path("static/assets/font-awesome/css/all.min.css"),
]


def test_templates_are_utf8():
    for template in TEMPLATES:
        path = Path("templates") / template
        raw = path.read_bytes()
        raw.decode("utf-8")
    reporter.mark_ok("Templates UTF-8 & static assets")


def test_static_assets_exist():
    for asset in ASSETS:
        assert asset.exists(), f"Missing asset: {asset}"
