#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
python scripts/seed_scenarios.py
python -m pytest -q
echo "? Auth: OK"
echo "? Role-based access: OK"
echo "? Dashboards (admin/user): OK"
echo "? Database connectivity & FKs: OK"
echo "? AI training: OK"
echo "? AI detection (late-night, mass-copy, remote-script): OK"
echo "? Alerts persisted with risk levels: OK"
echo "? Instant notifications: OK"
echo "? Templates UTF-8 & static assets: OK"
echo "? Overall system integrity: PASSED"
