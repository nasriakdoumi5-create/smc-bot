# install_agent.ps1
# Registers the NasriTools store agent as a daily Windows task.
# After this you never have to run anything — it watches the shop for you.
#
#   powershell -ExecutionPolicy Bypass -File install_agent.ps1
#
# Remove it later with:  schtasks /delete /tn "NasriTools Store Agent" /f

$ErrorActionPreference = "Stop"

$TaskName = "NasriTools Store Agent"
$Root     = $PSScriptRoot
$Script   = Join-Path $Root "agent_daemon.py"
$RunTime  = "09:30"          # daily, local time

Write-Host ""
Write-Host "==============================================================="
Write-Host "  NasriTools — installing the autonomous store agent"
Write-Host "==============================================================="
Write-Host ""

# --- find python -----------------------------------------------------------
$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) {
    $Python = (Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $Python) {
    Write-Host "  X Python not found on PATH. Install Python, then re-run." -ForegroundColor Red
    exit 1
}
Write-Host "  python : $Python"

if (-not (Test-Path $Script)) {
    Write-Host "  X agent_daemon.py not found next to this script." -ForegroundColor Red
    exit 1
}
Write-Host "  agent  : $Script"

# --- token present? --------------------------------------------------------
$TokenFile = Join-Path $env:USERPROFILE "etsy_token.json"
if (-not (Test-Path $TokenFile)) {
    Write-Host ""
    Write-Host "  ! No Etsy token yet. Run this first:" -ForegroundColor Yellow
    Write-Host "      python etsy_reauth.py"
    Write-Host ""
}

# --- register the scheduled task ------------------------------------------
schtasks /query /tn "$TaskName" *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ~ task already exists — replacing it"
    schtasks /delete /tn "$TaskName" /f *> $null
}

$Action = "`"$Python`" `"$Script`""
schtasks /create `
    /tn "$TaskName" `
    /tr $Action `
    /sc DAILY `
    /st $RunTime `
    /rl LIMITED `
    /f *> $null

if ($LASTEXITCODE -ne 0) {
    Write-Host "  X Could not register the task." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "  OK  Agent installed." -ForegroundColor Green
Write-Host ""
Write-Host "  It runs every day at $RunTime and will:"
Write-Host "    - check the shop is alive and not suspended"
Write-Host "    - watch your Etsy balance so fees never pile up again"
Write-Host "    - reactivate listings that get switched off"
Write-Host "    - tell you the moment a sale comes in"
Write-Host "    - write a report to agent_reports\"
Write-Host ""
Write-Host "  You only hear from it when something needs you."
Write-Host ""
Write-Host "  Test it right now:   python agent_daemon.py"
Write-Host "  Change the time:     schtasks /change /tn `"$TaskName`" /st 20:00"
Write-Host "  Remove it:           schtasks /delete /tn `"$TaskName`" /f"
Write-Host ""
Write-Host "==============================================================="
Write-Host ""
