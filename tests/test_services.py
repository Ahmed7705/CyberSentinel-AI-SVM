from __future__ import annotations

from database.database import fetch_one
from services import alert_service, auth_service, report_service
from tests import _reporter as reporter

DEFAULT_PASSWORD = "CyberSentinel!23"


def test_auth_hashing_roundtrip():
    hashed = auth_service.hash_password(DEFAULT_PASSWORD)
    assert auth_service.verify_password(DEFAULT_PASSWORD, hashed)


def test_admin_guard_denies_user(client):
    client.post("/login", data={"username": "jdoe", "password": DEFAULT_PASSWORD})
    response = client.get("/admin/dashboard", follow_redirects=False)
    assert response.status_code in {302, 401}


def test_alert_and_report_services(client):
    with client.session_transaction() as sess:  # type: ignore[attr-defined]
        sess["user_id"] = 2
        sess["role"] = "admin"
    with client.application.app_context():  # type: ignore[attr-defined]
        alert_id = alert_service.create_alert(
            user_id=2,
            alert_type="Verification",
            description="Automated verification alert test",
            risk_score=0.82,
            risk_level="high",
            metadata_json="{}",
        )
        alert = alert_service.get_alert(alert_id)
        assert alert is not None
        notification = fetch_one(
            "SELECT * FROM notifications WHERE title = %s ORDER BY id DESC LIMIT 1",
            ("High risk alert: Verification",),
        )
        assert notification is not None
        html = report_service.build_alert_report([alert])
        assert "CyberSentinel Alert Report" in html
        reporter.mark_ok("Alerts persisted with risk levels")
        reporter.mark_ok("Instant notifications")
