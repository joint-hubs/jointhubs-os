<#
.SYNOPSIS
    Remove jointhubs-os scheduled tasks from Windows Task Scheduler.
.DESCRIPTION
    Removes:
      - jointhubs-ThoughtMap
      - jointhubs-Graphify
    Requires Administrator privileges.
#>

$ErrorActionPreference = "Stop"

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Run this script as Administrator." -ForegroundColor Red
    exit 1
}

$tasks = @("jointhubs-ThoughtMap", "jointhubs-Graphify")

foreach ($task in $tasks) {
    $existing = Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
    if ($existing) {
        Unregister-ScheduledTask -TaskName $task -Confirm:$false
        Write-Host "[OK] Removed $task" -ForegroundColor Green
    }
    else {
        Write-Host "[SKIP] $task not found" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "All jointhubs scheduled tasks removed."
