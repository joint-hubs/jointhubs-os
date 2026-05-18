<#
.SYNOPSIS
    Graphify weekly refresh for active Second Brain projects.
.DESCRIPTION
    Runs graphify --update on each active project folder. Only re-extracts
    files that changed since the last run. Code-only changes skip LLM entirely.
    Designed to run via Windows Task Scheduler on Sunday nights.
.NOTES
    Install:  .github/automation/install-schedules.ps1
    Logs:     Second Brain/Operations/automation-logs/graphify-*.log
#>

$ErrorActionPreference = "Stop"

# --- Paths ---
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$ProjectsDir = Join-Path (Join-Path $RepoRoot "Second Brain") "Projects"
$LogDir = Join-Path (Join-Path (Join-Path $RepoRoot "Second Brain") "Operations") "automation-logs"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$LogFile = Join-Path $LogDir "graphify-$Timestamp.log"

# Active project folders to refresh (each must have graphify-out/ from a prior run)
$Projects = @(
    "thoughtmap",
    "office_ai",
    "fenix",
    "neurohubs"
)

# Ensure log directory exists
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message)
    $entry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $Message"
    Add-Content -Path $LogFile -Value $entry
    Write-Host $entry
}

# --- Pre-flight checks ---
try {
    python -c "import graphify" 2>$null
}
catch {
    Write-Log "ERROR: graphify Python package not installed. Run: pip install graphifyy"
    exit 1
}

# --- Process each project ---
Write-Log "Graphify weekly refresh starting"
Write-Log "Projects: $($Projects -join ', ')"

$results = @{}

foreach ($project in $Projects) {
    $projectPath = Join-Path $ProjectsDir $project
    $graphifyOut = Join-Path $projectPath "graphify-out"

    if (-not (Test-Path $projectPath)) {
        Write-Log "[$project] SKIP - folder not found: $projectPath"
        $results[$project] = "skipped (not found)"
        continue
    }

    # Check if this project has been graphified before
    $hasManifest = Test-Path (Join-Path $graphifyOut "manifest.json")

    Write-Log "[$project] Starting $(if ($hasManifest) { 'incremental update' } else { 'full build' })..."

    Push-Location $projectPath
    try {
        if ($hasManifest) {
            # --- Incremental mode ---
            $detectResult = python -c @"
import json
from graphify.detect import detect_incremental
from pathlib import Path
result = detect_incremental(Path('.'))
print(json.dumps(result))
"@ 2>&1

            $detect = $detectResult | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($detect -and $detect.new_total -eq 0) {
                Write-Log "[$project] No changes since last run - skipping"
                $results[$project] = "no changes"
                continue
            }
            $changedCount = if ($detect) { $detect.new_total } else { "unknown" }
            Write-Log "[$project] $changedCount file(s) changed"
        }

        # Run full graphify pipeline via Python
        $pipelineOutput = python -c @"
import json, sys
from pathlib import Path
from graphify.detect import detect, save_manifest
from graphify.extract import collect_files, extract
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json, to_html

# Detect
result = detect(Path('.'))
if result['total_files'] == 0:
    print('No files found')
    sys.exit(0)

# AST extraction for code
code_files = []
for f in result.get('files', {}).get('code', []):
    p = Path(f)
    code_files.extend(collect_files(p) if p.is_dir() else [p])

ast_result = extract(code_files) if code_files else {'nodes': [], 'edges': [], 'input_tokens': 0, 'output_tokens': 0}

# Check semantic cache
from graphify.cache import check_semantic_cache
all_files = [f for files in result['files'].values() for f in files]
cached_nodes, cached_edges, cached_hyperedges, uncached = check_semantic_cache(all_files)

# Merge AST + cached semantic (skip LLM for automation)
seen = {n['id'] for n in ast_result['nodes']}
merged_nodes = list(ast_result['nodes'])
for n in cached_nodes:
    if n['id'] not in seen:
        merged_nodes.append(n)
        seen.add(n['id'])

merged = {
    'nodes': merged_nodes,
    'edges': ast_result['edges'] + cached_edges,
    'hyperedges': cached_hyperedges,
    'input_tokens': 0,
    'output_tokens': 0,
}

# Build graph
G = build_from_json(merged)
if G.number_of_nodes() == 0:
    print('Graph empty after extraction')
    sys.exit(0)

communities = cluster(G)
cohesion = score_all(G, communities)
gods = god_nodes(G)
surprises = surprising_connections(G, communities)
labels = {cid: f'Community {cid}' for cid in communities}
questions = suggest_questions(G, communities, labels)

# Generate outputs
Path('graphify-out').mkdir(exist_ok=True)
tokens = {'input': 0, 'output': 0}
report = generate(G, communities, cohesion, labels, gods, surprises, result, tokens, '.', suggested_questions=questions)
Path('graphify-out/GRAPH_REPORT.md').write_text(report, encoding='utf-8')
to_json(G, communities, 'graphify-out/graph.json')

if G.number_of_nodes() <= 5000:
    to_html(G, communities, 'graphify-out/graph.html', community_labels=labels)

save_manifest(result['files'])
print(f'{G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities')
"@ 2>&1 | Out-String

        Write-Log "[$project] $($pipelineOutput.Trim())"
        $results[$project] = $pipelineOutput.Trim()
    }
    catch {
        Write-Log "[$project] ERROR: $_"
        $results[$project] = "error"
    }
    finally {
        # Clean up temp files
        Remove-Item -ErrorAction SilentlyContinue .graphify_detect.json, .graphify_extract.json, .graphify_ast.json, .graphify_semantic.json, .graphify_analysis.json, .graphify_labels.json, .graphify_python, .graphify_incremental.json
        Pop-Location
    }
}

# --- Summary ---
Write-Log ""
Write-Log "=== Summary ==="
foreach ($key in $results.Keys | Sort-Object) {
    Write-Log "  $key : $($results[$key])"
}

# --- Cleanup old logs (keep last 12) ---
$oldLogs = Get-ChildItem -Path $LogDir -Filter "graphify-*.log" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -Skip 12
if ($oldLogs) {
    $oldLogs | Remove-Item -Force
    Write-Log "Cleaned up $($oldLogs.Count) old log files"
}
