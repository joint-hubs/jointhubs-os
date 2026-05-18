<#
.SYNOPSIS
    ThoughtMap nightly pipeline runner.
.DESCRIPTION
    Starts Docker Compose for ThoughtMap, waits for the pipeline to complete,
    then stops containers. Designed to run via Windows Task Scheduler at 2 AM.
.NOTES
    Install:  .github/automation/install-schedules.ps1
    Logs:     Second Brain/Operations/automation-logs/thoughtmap-*.log
#>

$ErrorActionPreference = "Stop"

# --- Paths ---
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$ProjectDir = Join-Path (Join-Path (Join-Path $RepoRoot "Second Brain") "Projects") "thoughtmap"
$LogDir = Join-Path (Join-Path (Join-Path $RepoRoot "Second Brain") "Operations") "automation-logs"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$LogFile = Join-Path $LogDir "thoughtmap-$Timestamp.log"

# Ensure log directory exists
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message)
    $entry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $Message"
    Add-Content -Path $LogFile -Value $entry
    Write-Host $entry
}

# --- Pre-flight checks ---
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Log "ERROR: docker not found in PATH"
    exit 1
}

if (-not (Test-Path (Join-Path $ProjectDir "docker-compose.yml"))) {
    Write-Log "ERROR: docker-compose.yml not found in $ProjectDir"
    exit 1
}

# Check Docker daemon is running (wait up to 60s for Docker Desktop to start)
$dockerReady = $false
for ($i = 0; $i -lt 6; $i++) {
    $ErrorActionPreference = "Continue"
    $null = docker info 2>&1
    $ErrorActionPreference = "Stop"
    if ($LASTEXITCODE -eq 0) {
        $dockerReady = $true
        break
    }
    Write-Log "Waiting for Docker daemon... (attempt $($i+1)/6)"
    Start-Sleep -Seconds 10
}
if (-not $dockerReady) {
    Write-Log "ERROR: Docker daemon not responding after 60s. Is Docker Desktop running?"
    exit 1
}

# --- Run ---
Write-Log "Starting ThoughtMap pipeline"
Write-Log "Project dir: $ProjectDir"

Push-Location $ProjectDir
try {
    # Start containers (use Continue to prevent stderr from terminating script)
    Write-Log "Starting Docker Compose..."
    $ErrorActionPreference = "Continue"
    $buildOutput = docker compose up -d --build 2>&1 | Out-String
    $buildExit = $LASTEXITCODE
    $ErrorActionPreference = "Stop"
    if ($buildOutput.Trim()) { Write-Log $buildOutput.Trim() }

    if ($buildExit -ne 0) {
        Write-Log "ERROR: Docker Compose failed to start (exit code $buildExit)"
        exit 1
    }

    # Wait for pipeline to complete (poll /api/status)
    $maxWait = 3600  # 60 minutes max (large corpus with GPU embedding)
    $elapsed = 0
    $pollInterval = 10
    $statusUrl = "http://localhost:8585/api/status"

    Write-Log "Waiting for pipeline to complete (max ${maxWait}s)..."

    # Give the server a moment to start
    Start-Sleep -Seconds 5
    $elapsed += 5

    while ($elapsed -lt $maxWait) {
        try {
            $response = Invoke-RestMethod -Uri $statusUrl -TimeoutSec 5
            $phase = $response.phase
            $detail = if ($response.detail) { " - $($response.detail)" } else { "" }
            Write-Log "Status: $phase$detail"

            if ($phase -eq "done") {
                Write-Log "Pipeline completed successfully"
                break
            }
            if ($phase -eq "error") {
                Write-Log "ERROR: Pipeline failed - $($response.detail)"
                break
            }
        }
        catch {
            Write-Log "Waiting for server... ($elapsed s)"
        }

        Start-Sleep -Seconds $pollInterval
        $elapsed += $pollInterval
    }

    if ($elapsed -ge $maxWait) {
        Write-Log "WARNING: Pipeline timed out after ${maxWait}s"
    }

    # Leave containers running (restart: unless-stopped keeps them alive)
    Write-Log "Pipeline done - containers left running"
}
finally {
    Pop-Location
}

# --- Cleanup old logs (keep last 30) ---
$oldLogs = Get-ChildItem -Path $LogDir -Filter "thoughtmap-*.log" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -Skip 30
if ($oldLogs) {
    $oldLogs | Remove-Item -Force
    Write-Log "Cleaned up $($oldLogs.Count) old log files"
}
