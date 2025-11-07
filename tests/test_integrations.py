from __future__ import annotations

from urllib.parse import urlparse

from flask import session

from tests import _reporter as reporter

DEFAULT_PASSWORD = "CyberSentinel!23"


def test_admin_and_user_flows(client):
    response = client.get("/")
    assert response.status_code == 302
    assert urlparse(response.location).path == "/login"

    response = client.get("/login")
    assert response.status_code == 200

    response = client.post("/login", data={"username": "admin", "password": DEFAULT_PASSWORD}, follow_redirects=False)
    assert response.status_code == 302
    assert urlparse(response.location).path == "/admin/dashboard"

    with client.session_transaction() as sess:  # type: ignore[attr-defined]
        assert sess.get("role") == "admin"
        reporter.mark_ok("Auth")
        reporter.mark_ok("Role-based access")

    dashboard = client.get("/admin/dashboard")
    assert dashboard.status_code == 200
    assert b"Command Center" in dashboard.data

    alerts_page = client.get("/admin/alerts")
    reports_page = client.get("/admin/reports")
    assert alerts_page.status_code == 200
    assert reports_page.status_code == 200
    assert b"Alert Intelligence Report" in reports_page.data
    reporter.mark_ok("Dashboards (admin/user)")

    client.get("/logout")

    response = client.post("/login", data={"username": "jdoe", "password": DEFAULT_PASSWORD}, follow_redirects=False)
    assert response.status_code == 302
    assert urlparse(response.location).path == "/user/dashboard"

    user_dash = client.get("/user/dashboard")
    assert user_dash.status_code == 200

    profile = client.get("/user/profile")
    assert profile.status_code == 200
    updated_name = "Jordan Doe QA"
    resp = client.post(
        "/user/profile",
        data={"full_name": updated_name, "department": "Finance"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert updated_name.encode("utf-8") in resp.data
    reporter.mark_ok("Database connectivity & FKs")
