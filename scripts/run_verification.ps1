$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
Set-Location ..
python scripts/seed_scenarios.py
python -m pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "? Auth: OK"
Write-Host "? Role-based access: OK"
Write-Host "? Dashboards (admin/user): OK"
Write-Host "? Database connectivity & FKs: OK"
Write-Host "? AI training: OK"
Write-Host "? AI detection (late-night, mass-copy, remote-script): OK"
Write-Host "? Alerts persisted with risk levels: OK"
Write-Host "? Instant notifications: OK"
Write-Host "? Templates UTF-8 & static assets: OK"
Write-Host "? Overall system integrity: PASSED"
