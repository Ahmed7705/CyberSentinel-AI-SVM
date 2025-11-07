from __future__ import annotations

import os
import pytest

from app import create_app
from scripts.seed_scenarios import seed as seed_scenarios
from tests import _reporter as reporter


@pytest.fixture(scope="session", autouse=True)
def seed_database() -> None:
    seed_scenarios()


@pytest.fixture(scope="session")
def flask_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="function")
def client(flask_app):
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client


def pytest_sessionfinish(session, exitstatus):  # pragma: no cover - pytest hook
    reporter.emit_final_report(exitstatus == 0)
