"""Generate interactive HTML visualization — graphify-inspired force graph."""

from __future__ import annotations

import json
from pathlib import Path

import thoughtmap.config as config
from thoughtmap.core.cluster import ThoughtMapResult


# Tableau-10 palette (same as graphify)
_PALETTE = [
    "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
    "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC",
]

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ThoughtMap</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0f0f1a; color: #e0e0e0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; display: flex; height: 100vh; overflow: hidden; }
  #graph { flex: 1; }
  #sidebar { width: 300px; background: #1a1a2e; border-left: 1px solid #2a2a4e; display: flex; flex-direction: column; overflow: hidden; }
  #search-wrap { padding: 12px; border-bottom: 1px solid #2a2a4e; }
  #search { width: 100%; background: #0f0f1a; border: 1px solid #3a3a5e; color: #e0e0e0; padding: 7px 10px; border-radius: 6px; font-size: 13px; outline: none; }
  #search:focus { border-color: #4E79A7; }
  #search-results { max-height: 160px; overflow-y: auto; padding: 4px 12px; border-bottom: 1px solid #2a2a4e; display: none; }
  .search-item { padding: 4px 6px; cursor: pointer; border-radius: 4px; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .search-item:hover { background: #2a2a4e; }
  #filter-wrap { padding: 10px 12px; border-bottom: 1px solid #2a2a4e; display: flex; flex-direction: column; gap: 6px; }
  #filter-wrap label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }
  #filter-wrap select { background: #0f0f1a; border: 1px solid #3a3a5e; color: #e0e0e0; padding: 5px 8px; border-radius: 4px; font-size: 12px; }
  #info-panel { padding: 14px; border-bottom: 1px solid #2a2a4e; min-height: 140px; max-height: 300px; overflow-y: auto; }
  #info-panel h3 { font-size: 13px; color: #aaa; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; }
  #info-content { font-size: 13px; color: #ccc; line-height: 1.6; }
  #info-content .field { margin-bottom: 5px; }
  #info-content .field b { color: #e0e0e0; }
  #info-content .empty { color: #555; font-style: italic; }
  .tag { display: inline-block; border-radius: 3px; padding: 1px 6px; font-size: 11px; margin-right: 4px; margin-bottom: 2px; background: #2a2a4e; }
  .tag.note { background: #238636; color: #fff; }
  .tag.coding { background: #1f6feb; color: #fff; }
  .tag.browsing { background: #8957e5; color: #fff; }
  .tag.communication { background: #d29922; color: #000; }
  #legend-wrap { flex: 1; overflow-y: auto; padding: 12px; }
  #legend-wrap h3 { font-size: 13px; color: #aaa; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.05em; }
  .legend-item { display: flex; align-items: center; gap: 8px; padding: 4px 0; cursor: pointer; border-radius: 4px; font-size: 12px; }
  .legend-item:hover { background: #2a2a4e; padding-left: 4px; }
  .legend-item.dimmed { opacity: 0.35; }
  .legend-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
  .legend-label { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .legend-count { color: #666; font-size: 11px; }
  #stats { padding: 10px 14px; border-top: 1px solid #2a2a4e; font-size: 11px; color: #555; }
  #view-toggle { padding: 8px 12px; border-bottom: 1px solid #2a2a4e; display: flex; gap: 6px; }
  #view-toggle button { flex: 1; background: #0f0f1a; border: 1px solid #3a3a5e; color: #e0e0e0; padding: 6px; border-radius: 4px; cursor: pointer; font-size: 12px; }
  #view-toggle button.active { background: #4E79A7; border-color: #4E79A7; color: #fff; }
  .entity-hl { background: rgba(255, 200, 50, 0.25); color: #ffd866; border-radius: 2px; padding: 0 2px; cursor: pointer; border-bottom: 1px dashed #ffd866; }
  .entity-hl:hover { background: rgba(255, 200, 50, 0.45); }
  .entity-hl.person { background: rgba(56, 166, 56, 0.25); color: #6fcf6f; border-color: #6fcf6f; }
  .entity-hl.organization { background: rgba(31, 111, 235, 0.25); color: #6fadff; border-color: #6fadff; }
  .entity-hl.project { background: rgba(137, 87, 229, 0.25); color: #b89eff; border-color: #b89eff; }
  .entity-hl.tool { background: rgba(210, 153, 34, 0.25); color: #e6c44d; border-color: #e6c44d; }
  .entity-hl.location { background: rgba(228, 87, 87, 0.25); color: #f28585; border-color: #f28585; }
  #entity-detail { display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1a1a2e; border: 1px solid #3a3a5e; border-radius: 10px; padding: 20px 24px; max-width: 440px; width: 90vw; max-height: 70vh; overflow-y: auto; z-index: 1000; box-shadow: 0 8px 32px rgba(0,0,0,0.6); }
  #entity-detail h2 { font-size: 16px; margin-bottom: 4px; }
  #entity-detail .etype { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
  #entity-detail .esummary { font-size: 13px; color: #ccc; line-height: 1.6; margin-bottom: 12px; }
  #entity-detail .efield { font-size: 12px; margin-bottom: 6px; color: #aaa; }
  #entity-detail .efield b { color: #e0e0e0; }
  #entity-detail .eclose { position: absolute; top: 12px; right: 14px; background: none; border: none; color: #666; font-size: 18px; cursor: pointer; }
  #entity-detail .eclose:hover { color: #fff; }
  #entity-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); z-index: 999; }
  #note-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1001; }
  #note-modal { display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1a1a2e; border: 1px solid #3a3a5e; border-radius: 10px; padding: 24px; width: 440px; max-width: 90vw; z-index: 1002; box-shadow: 0 8px 32px rgba(0,0,0,0.6); }
  #note-modal h2 { font-size: 16px; margin-bottom: 16px; }
  #note-modal .nclose { position: absolute; top: 12px; right: 14px; background: none; border: none; color: #666; font-size: 18px; cursor: pointer; }
  #note-modal .nclose:hover { color: #fff; }
  #note-modal label { display: block; font-size: 12px; color: #888; margin-bottom: 4px; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
  #note-modal input, #note-modal textarea, #note-modal select { width: 100%; background: #0f0f1a; border: 1px solid #3a3a5e; color: #e0e0e0; padding: 8px 10px; border-radius: 6px; font-size: 13px; font-family: inherit; margin-bottom: 12px; outline: none; }
  #note-modal input:focus, #note-modal textarea:focus, #note-modal select:focus { border-color: #4E79A7; }
  #note-modal textarea { height: 120px; resize: vertical; }
  #note-modal .nbtn { background: #238636; border: none; color: #fff; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 13px; }
  #note-modal .nbtn:hover { background: #2ea043; }
  #note-modal .nbtn:disabled { opacity: 0.5; cursor: not-allowed; }
  #note-modal .nfeedback { font-size: 12px; margin-top: 8px; min-height: 18px; }
  #note-modal .nfeedback.ok { color: #3fb950; }
  #note-modal .nfeedback.err { color: #f85149; }
  .add-note-btn { background: #238636; border: none; color: #fff; padding: 5px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; margin-top: 8px; }
  .add-note-btn:hover { background: #2ea043; }
</style>
</head>
<body>
<div id="graph"></div>
<div id="sidebar">
  <div id="search-wrap">
    <input id="search" type="text" placeholder="Search thoughts..." autocomplete="off">
    <div id="search-results"></div>
  </div>
  <div id="view-toggle">
    <button id="btn-graph" class="active" onclick="setView('graph')">Graph</button>
    <button id="btn-scatter" onclick="setView('scatter')">Scatter</button>
  </div>
  <div id="filter-wrap">
    <label>Source <select id="filter-source" onchange="applyFilter()">
      <option value="all">All sources</option>
      <option value="obsidian-daily">Obsidian Daily</option>
      <option value="obsidian-root">Obsidian Topics</option>
      <option value="jointhubs-review">AI Reviews</option>
      <option value="wispr-flow">Wispr Flow</option>
    </select></label>
    <label>Category <select id="filter-cat" onchange="applyFilter()">
      <option value="all">All categories</option>
      <option value="coding">Coding</option>
      <option value="browsing">Browsing</option>
      <option value="note-taking">Note-taking</option>
      <option value="communication">Communication</option>
      <option value="general">General</option>
    </select></label>
  </div>
  <div id="info-panel">
    <h3>Thought Info</h3>
    <div id="info-content"><span class="empty">Click a node to inspect it</span></div>
  </div>
  <div id="legend-wrap">
    <h3>Clusters</h3>
    <div id="legend"></div>
  </div>
  <div id="stats"></div>
</div>
<div id="entity-overlay" onclick="closeEntityDetail()"></div>
<div id="entity-detail">
  <button class="eclose" onclick="closeEntityDetail()">&times;</button>
  <h2 id="ename"></h2>
  <div class="etype" id="etype"></div>
  <div class="esummary" id="esummary"></div>
  <div id="edetails"></div>
</div>
<div id="note-overlay" onclick="closeCreateNote()"></div>
<div id="note-modal">
  <button class="nclose" onclick="closeCreateNote()">&times;</button>
  <h2>Add Note</h2>
  <label>Directory</label>
  <select id="note-dir"></select>
  <label>Title</label>
  <input id="note-title" type="text" placeholder="Note title..." autocomplete="off">
  <label>Content</label>
  <textarea id="note-content" placeholder="Write your thought..."></textarea>
  <button class="nbtn" id="note-submit" onclick="submitNote()">Create Note</button>
  <div class="nfeedback" id="note-feedback"></div>
</div>

<script>
const DATA = __DATA__;
const CLUSTERS = __CLUSTERS__;
const PALETTE = __PALETTE__;
const ENTITIES = __ENTITIES__;

let currentView = 'graph';
let network = null;
let nodesDS, edgesDS;
let activeClusterFilter = null;

// Build nodes
function makeNodes(data) {
  return data.map(d => {
    const color = d.cluster >= 0 ? PALETTE[d.cluster % PALETTE.length] : '#484f58';
    const baseSize = Math.max(8, Math.min(22, (d.token_estimate || 50) / 15));
    const repeatBoost = d.repeat_count > 1 ? 1 + Math.log2(d.repeat_count) * 0.15 : 1;
    const size = (d.intent === 'note' ? baseSize * 1.3 : baseSize) * repeatBoost;
    const label = d.text.substring(0, 40).replace(/\\n/g, ' ');
    return {
      id: d.idx, label: label,
      color: { background: color, border: color, highlight: { background: '#ffffff', border: color } },
      size: size,
      font: { size: size > 12 ? 10 : 0, color: '#ffffff' },
      title: d.text.substring(0, 120),
      x: d.x * 200, y: d.y * 200,
      _data: d,
    };
  });
}

// Build edges — connect chunks within same cluster that are close in embedding space
function makeEdges(data) {
  const edges = [];
  let edgeId = 0;
  // Group by cluster
  const clusterMap = {};
  data.forEach(d => {
    if (d.cluster < 0) return;
    if (!clusterMap[d.cluster]) clusterMap[d.cluster] = [];
    clusterMap[d.cluster].push(d);
  });

  for (const [cid, members] of Object.entries(clusterMap)) {
    const color = PALETTE[parseInt(cid) % PALETTE.length];
    // Connect each member to its 2 nearest neighbors within cluster (by 2D distance)
    for (let i = 0; i < members.length; i++) {
      const dists = [];
      for (let j = 0; j < members.length; j++) {
        if (i === j) continue;
        const dx = members[i].x - members[j].x;
        const dy = members[i].y - members[j].y;
        dists.push({ j, dist: Math.sqrt(dx*dx + dy*dy) });
      }
      dists.sort((a, b) => a.dist - b.dist);
      const k = Math.min(2, dists.length);
      for (let n = 0; n < k; n++) {
        // Avoid duplicate edges
        const from = members[i].idx;
        const to = members[dists[n].j].idx;
        if (from < to) {
          edges.push({
            id: edgeId++, from, to,
            color: { opacity: 0.25, color: color },
            width: 1,
          });
        }
      }
    }
  }
  return edges;
}

function buildNetwork() {
  const container = document.getElementById('graph');
  const data = getFilteredData();
  const nodes = makeNodes(data);
  const edges = currentView === 'graph' ? makeEdges(data) : [];

  nodesDS = new vis.DataSet(nodes);
  edgesDS = new vis.DataSet(edges);

  if (network) network.destroy();
  network = new vis.Network(container, { nodes: nodesDS, edges: edgesDS }, {
    physics: currentView === 'graph' ? {
      enabled: true,
      solver: 'forceAtlas2Based',
      forceAtlas2Based: {
        gravitationalConstant: -40,
        centralGravity: 0.005,
        springLength: 100,
        springConstant: 0.06,
        damping: 0.4,
        avoidOverlap: 0.6,
      },
      stabilization: { iterations: 150, fit: true },
    } : { enabled: false },
    interaction: { hover: true, tooltipDelay: 150, hideEdgesOnDrag: true },
    nodes: { shape: 'dot', borderWidth: 1.5 },
    edges: { smooth: { type: 'continuous' } },
  });

  // If scatter mode, use UMAP positions directly
  if (currentView === 'scatter') {
    network.fit();
  }

  network.on('click', params => {
    if (params.nodes.length > 0) {
      const node = nodesDS.get(params.nodes[0]);
      showInfo(node._data);
    }
  });

  updateStats(data);
}

function getFilteredData() {
  const src = document.getElementById('filter-source').value;
  const cat = document.getElementById('filter-cat').value;
  return DATA.filter(d => {
    if (src !== 'all' && d.source !== src) return false;
    if (cat !== 'all' && d.category !== cat) return false;
    if (activeClusterFilter !== null && d.cluster !== activeClusterFilter) return false;
    return true;
  });
}

function applyFilter() { buildNetwork(); }

function setView(v) {
  currentView = v;
  document.getElementById('btn-graph').classList.toggle('active', v === 'graph');
  document.getElementById('btn-scatter').classList.toggle('active', v === 'scatter');
  buildNetwork();
}

function showInfo(d) {
  const tags = [];
  if (d.intent === 'note') tags.push('<span class="tag note">note</span>');
  if (d.category) tags.push('<span class="tag ' + d.category + '">' + d.category + '</span>');
  if (d.project_tag) tags.push('<span class="tag">#' + d.project_tag + '</span>');
  if (d.source) tags.push('<span class="tag">' + d.source + '</span>');

  const cluster = CLUSTERS.find(c => c.cluster_id === d.cluster);
  const clusterLabel = cluster ? cluster.label : 'Unclustered';
  const clusterColor = d.cluster >= 0 ? PALETTE[d.cluster % PALETTE.length] : '#484f58';

  document.getElementById('info-content').innerHTML =
    '<div class="field"><b>Time:</b> ' + (d.timestamp || 'N/A') + '</div>' +
    '<div class="field"><b>Cluster:</b> <span style="color:' + clusterColor + '">' + clusterLabel + '</span></div>' +
    (d.repeat_count > 1 ? '<div class="field"><b>Appears in:</b> ' + d.repeat_count + ' notes</div>' : '') +
    (d.wispr_app ? '<div class="field"><b>App:</b> ' + d.wispr_app + '</div>' : '') +
    '<div style="margin:6px 0">' + tags.join(' ') + '</div>' +
    '<div style="margin-top:8px;color:#ccc;line-height:1.5">' + highlightEntities(d.text.substring(0, 500)) +
    (d.text.length > 500 ? '...' : '') + '</div>' +
    (d.cluster >= 0 ? '<button class="add-note-btn" onclick="openCreateNote(' + d.cluster + ')">+ Add Note</button>' : '');
}

// Search
const searchInput = document.getElementById('search');
const searchResults = document.getElementById('search-results');
searchInput.addEventListener('input', () => {
  const q = searchInput.value.toLowerCase().trim();
  if (q.length < 2) { searchResults.style.display = 'none'; return; }
  const matches = DATA.filter(d => d.text.toLowerCase().includes(q)).slice(0, 15);
  if (matches.length === 0) { searchResults.style.display = 'none'; return; }
  searchResults.innerHTML = matches.map(d =>
    '<div class="search-item" onclick="focusNode(' + d.idx + ')">' +
    d.text.substring(0, 60).replace(/</g, '&lt;') + '</div>'
  ).join('');
  searchResults.style.display = 'block';
});

function focusNode(idx) {
  searchResults.style.display = 'none';
  if (network) {
    network.focus(idx, { scale: 1.5, animation: true });
    network.selectNodes([idx]);
    const node = nodesDS.get(idx);
    if (node) showInfo(node._data);
  }
}

// Legend
function buildLegend() {
  const legend = document.getElementById('legend');
  legend.innerHTML = '';
  CLUSTERS.forEach(c => {
    const color = PALETTE[c.cluster_id % PALETTE.length];
    const div = document.createElement('div');
    div.className = 'legend-item';
    div.innerHTML = '<div class="legend-dot" style="background:' + color + '"></div>' +
      '<span class="legend-label">' + c.label + '</span>' +
      '<span class="legend-count">' + c.size + '</span>';
    div.onclick = () => {
      if (activeClusterFilter === c.cluster_id) {
        activeClusterFilter = null;
        div.classList.remove('dimmed');
        document.querySelectorAll('.legend-item').forEach(el => el.classList.remove('dimmed'));
      } else {
        activeClusterFilter = c.cluster_id;
        document.querySelectorAll('.legend-item').forEach(el => el.classList.add('dimmed'));
        div.classList.remove('dimmed');
      }
      buildNetwork();
    };
    legend.appendChild(div);
  });
  // Unclustered
  const unclustered = DATA.filter(d => d.cluster === -1).length;
  if (unclustered > 0) {
    const div = document.createElement('div');
    div.className = 'legend-item';
    div.innerHTML = '<div class="legend-dot" style="background:#484f58"></div>' +
      '<span class="legend-label">Unclustered</span>' +
      '<span class="legend-count">' + unclustered + '</span>';
    legend.appendChild(div);
  }
}

function updateStats(data) {
  const nClusters = CLUSTERS.length;
  document.getElementById('stats').textContent =
    data.length + ' thoughts \\u00b7 ' + nClusters + ' clusters';
}

// Entity highlighting
const _entityIndex = {};
ENTITIES.forEach(e => {
  const names = [e.name, ...(e.aliases || [])];
  names.forEach(n => { if (n && n.length > 1) _entityIndex[n.toLowerCase()] = e; });
});
const _entityNames = Object.keys(_entityIndex).sort((a, b) => b.length - a.length);

function highlightEntities(text) {
  if (!_entityNames.length) return text.replace(/</g, '&lt;');
  let safe = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const pattern = _entityNames.map(n => n.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&')).join('|');
  const re = new RegExp('\\\\b(' + pattern + ')\\\\b', 'gi');
  return safe.replace(re, (match) => {
    const e = _entityIndex[match.toLowerCase()];
    const cls = e ? e.type : '';
    const ename = e ? e.name : match;
    return '<span class="entity-hl ' + cls + '" onclick="showEntityDetail(\\'' +
      ename.replace(/'/g, "\\\\'") + '\\')">' + match + '</span>';
  });
}

function showEntityDetail(name) {
  const e = ENTITIES.find(en => en.name === name) || _entityIndex[name.toLowerCase()];
  if (!e) return;
  document.getElementById('ename').textContent = e.name;
  document.getElementById('etype').textContent = e.type + ' \\u00b7 ' + e.mention_count + ' mentions';
  document.getElementById('esummary').textContent = e.summary || '(No summary)';
  let details = '';
  if (e.aliases && e.aliases.length) details += '<div class="efield"><b>Aliases:</b> ' + e.aliases.join(', ') + '</div>';
  if (e.cluster_ids && e.cluster_ids.length) {
    const labels = e.cluster_ids.map(id => { const c = CLUSTERS.find(cl => cl.cluster_id === id); return c ? c.label : 'Cluster ' + id; });
    details += '<div class="efield"><b>Clusters:</b> ' + labels.join(', ') + '</div>';
  }
  if (e.boundaries) details += '<div class="efield" style="margin-top:8px"><b>Boundaries:</b><br>' + e.boundaries.replace(/\\n/g, '<br>') + '</div>';
  document.getElementById('edetails').innerHTML = details;
  document.getElementById('entity-overlay').style.display = 'block';
  document.getElementById('entity-detail').style.display = 'block';
}

function closeEntityDetail() {
  document.getElementById('entity-overlay').style.display = 'none';
  document.getElementById('entity-detail').style.display = 'none';
}

// \u2500\u2500 Create Note \u2500\u2500
let _noteClusterId = null;
let _noteDirs = null;

async function loadDirectories() {
  if (_noteDirs) return _noteDirs;
  try {
    const r = await fetch('/api/directories');
    const d = await r.json();
    _noteDirs = d.directories || [];
    return _noteDirs;
  } catch(e) { return []; }
}

function suggestDirectory(clusterId) {
  const IGNORE = new Set(['obsidian-daily', 'wispr-flow', 'jointhubs-review']);
  const members = DATA.filter(d => d.cluster === clusterId && !IGNORE.has(d.source));
  const scores = {};
  members.forEach(d => {
    if (d.project_tag) scores[d.project_tag] = (scores[d.project_tag] || 0) + 2;
    const sf = d.source_file || '';
    const m = sf.match(/Projects\/([\w-]+)\//i);
    if (m) scores[m[1]] = (scores[m[1]] || 0) + 1;
  });
  const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  if (sorted.length === 0 || !_noteDirs) return null;
  const best = sorted[0][0].toLowerCase();
  return _noteDirs.find(d => d.toLowerCase().includes(best)) || null;
}

async function openCreateNote(clusterId) {
  _noteClusterId = clusterId;
  const dirs = await loadDirectories();
  const select = document.getElementById('note-dir');
  select.innerHTML = dirs.map(d => '<option value="' + d + '">' + d + '</option>').join('');
  const suggested = suggestDirectory(clusterId);
  if (suggested) select.value = suggested;
  document.getElementById('note-title').value = '';
  document.getElementById('note-content').value = '';
  document.getElementById('note-feedback').textContent = '';
  document.getElementById('note-feedback').className = 'nfeedback';
  document.getElementById('note-submit').disabled = false;
  document.getElementById('note-overlay').style.display = 'block';
  document.getElementById('note-modal').style.display = 'block';
  document.getElementById('note-title').focus();
}

function closeCreateNote() {
  document.getElementById('note-overlay').style.display = 'none';
  document.getElementById('note-modal').style.display = 'none';
}

async function submitNote() {
  const title = document.getElementById('note-title').value.trim();
  const content = document.getElementById('note-content').value.trim();
  const directory = document.getElementById('note-dir').value;
  const feedback = document.getElementById('note-feedback');
  const btn = document.getElementById('note-submit');
  if (!title || !content) {
    feedback.textContent = 'Title and content are required.';
    feedback.className = 'nfeedback err';
    return;
  }
  btn.disabled = true;
  feedback.textContent = 'Creating...';
  feedback.className = 'nfeedback';
  try {
    const r = await fetch('/api/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content, directory }),
    });
    const d = await r.json();
    if (d.ok) {
      feedback.textContent = '\u2713 Created: ' + d.path;
      feedback.className = 'nfeedback ok';
      setTimeout(closeCreateNote, 2000);
    } else {
      feedback.textContent = d.error || 'Failed to create note.';
      feedback.className = 'nfeedback err';
      btn.disabled = false;
    }
  } catch(e) {
    feedback.textContent = 'Network error.';
    feedback.className = 'nfeedback err';
    btn.disabled = false;
  }
}

buildLegend();
buildNetwork();
</script>
</body>
</html>"""


def generate_viz(result: ThoughtMapResult) -> Path:
    """Generate the interactive HTML visualization."""
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Prepare data for the template
    data_points = []
    for i, item in enumerate(result.items):
        point = {
            "idx": i,
            "text": item.get("text", ""),
            "timestamp": item.get("timestamp", ""),
            "source": item.get("source", ""),
            "source_file": item.get("source_file", ""),
            "section": item.get("section"),
            "project_tag": item.get("project_tag"),
            "intent": item.get("intent"),
            "category": item.get("category"),
            "wispr_app": item.get("wispr_app"),
            "token_estimate": item.get("token_estimate", 50),
            "repeat_count": item.get("repeat_count", 1),
            "x": result.embeddings_2d[i][0],
            "y": result.embeddings_2d[i][1],
            "cluster": -1,
        }
        # Find which cluster this item belongs to
        for c in result.clusters:
            if i in c.member_indices:
                point["cluster"] = c.cluster_id
                break
        data_points.append(point)

    clusters_data = [
        {
            "cluster_id": c.cluster_id,
            "label": c.label,
            "size": c.size,
            "centroid": c.centroid,
        }
        for c in result.clusters
    ]

    html = _HTML_TEMPLATE.replace("__DATA__", json.dumps(data_points))
    html = html.replace("__CLUSTERS__", json.dumps(clusters_data))
    html = html.replace("__PALETTE__", json.dumps(_PALETTE))

    # Load entities if available
    entities_path = config.OUTPUT_DIR / "entities.json"
    if entities_path.exists():
        entities_data = json.loads(entities_path.read_text(encoding="utf-8"))
    else:
        entities_data = []
    html = html.replace("__ENTITIES__", json.dumps(entities_data))

    path = config.OUTPUT_DIR / "thoughtmap.html"
    path.write_text(html, encoding="utf-8")
    return path
