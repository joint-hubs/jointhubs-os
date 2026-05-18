<#
.SYNOPSIS
    Install Windows Task Scheduler tasks for jointhubs-os automation.
.DESCRIPTION
    Creates two scheduled tasks:
      - jointhubs-ThoughtMap: nightly at 2:00 AM
      - jointhubs-Graphify:   weekly Sunday at 3:00 AM
    Requires Administrator privileges to create tasks.
.NOTES
    Run as Administrator:  powershell -ExecutionPolicy Bypass -File install-schedules.ps1
    Uninstall:             .github/automation/uninstall-schedules.ps1
#>

$ErrorActionPreference = "Stop"

# Check admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Run this script as Administrator." -ForegroundColor Red
    Write-Host "  Right-click PowerShell -> Run as Administrator, then run this script again."
    exit 1
}

$ScriptDir = $PSScriptRoot
$RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

Write-Host "Installing jointhubs-os scheduled tasks..." -ForegroundColor Cyan
Write-Host "Repo root: $RepoRoot"
Write-Host ""

# --- ThoughtMap Nightly ---
$tmScript = Join-Path $ScriptDir "thoughtmap-nightly.ps1"
if (Test-Path $tmScript) {
    $tmAction = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$tmScript`""

    $tmTrigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"

    $tmSettings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
        -RestartCount 1 `
        -RestartInterval (New-TimeSpan -Minutes 5)

    Register-ScheduledTask `
        -TaskName "jointhubs-ThoughtMap" `
        -Description "Nightly ThoughtMap pipeline: embed daily notes, update vector store, generate visualization" `
        -Action $tmAction `
        -Trigger $tmTrigger `
        -Settings $tmSettings `
        -Force | Out-Null

    Write-Host "[OK] jointhubs-ThoughtMap - daily at 2:00 AM" -ForegroundColor Green
}
else {
    Write-Host "[SKIP] thoughtmap-nightly.ps1 not found" -ForegroundColor Yellow
}

# --- Graphify Weekly ---
$gfScript = Join-Path $ScriptDir "graphify-weekly.ps1"
if (Test-Path $gfScript) {
    $gfAction = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$gfScript`""

    $gfTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "3:00AM"

    $gfSettings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
        -RestartCount 1 `
        -RestartInterval (New-TimeSpan -Minutes 5)

    Register-ScheduledTask `
        -TaskName "jointhubs-Graphify" `
        -Description "Weekly graphify refresh: update knowledge graphs for active Second Brain projects" `
        -Action $gfAction `
        -Trigger $gfTrigger `
        -Settings $gfSettings `
        -Force | Out-Null

    Write-Host "[OK] jointhubs-Graphify - weekly Sunday at 3:00 AM" -ForegroundColor Green
}
else {
    Write-Host "[SKIP] graphify-weekly.ps1 not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done. Verify with:" -ForegroundColor Cyan
Write-Host "  Get-ScheduledTask -TaskName 'jointhubs-*' | Format-Table TaskName, State, NextRunTime"
Write-Host ""
Write-Host "To run manually:" -ForegroundColor Cyan
Write-Host "  Start-ScheduledTask -TaskName 'jointhubs-ThoughtMap'"
Write-Host "  Start-ScheduledTask -TaskName 'jointhubs-Graphify'"
