"""
Gmail Agent Dashboard — Flask Web Server
Localhost dashboard for the Digital FTE Gmail Autonomous Agent.
Runs on http://localhost:5050
"""

from flask import Flask, jsonify, render_template_string, request
from pathlib import Path
from datetime import datetime
import json, re, os

app = Flask(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).parent
VAULT       = ROOT / "AI_Employee_Vault"
INBOX_DIR     = VAULT / "Inbox"
NEEDS_ACTION  = ROOT / "Needs_Action"
APPROVAL_DIR  = ROOT / "02_Pending_Approvals"
DONE_DIR      = VAULT / "Done"
LOGS_DIR      = VAULT / "Logs"
AUDIT_DIR     = VAULT / "Audit"
GMAIL_LOG     = LOGS_DIR / "Gmail_Log.md"

# ══════════════════════════════════════════════════════════════════════════════
# DATA HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def parse_inbox_notes():
    notes = []
    # Search in all relevant folders where Gmail notes might exist or migrate to
    search_dirs = [INBOX_DIR, NEEDS_ACTION, DONE_DIR]
    
    unique_files = {} # {filename: Path} to avoid duplicates if file exists in multiple (unlikely)
    
    for d in search_dirs:
        if d.exists():
            for f in d.glob("gmail-*.md"):
                # Use filename as unique key, keep the newest version/path if conflict
                if f.name not in unique_files:
                    unique_files[f.name] = f
                elif f.stat().st_mtime > unique_files[f.name].stat().st_mtime:
                    unique_files[f.name] = f

    # Convert to list and sort by modification time
    sorted_paths = sorted(unique_files.values(), key=lambda x: x.stat().st_mtime, reverse=True)

    for f in sorted_paths:
        try:
            text = f.read_text(encoding="utf-8")
            def extract(label):
                m = re.search(rf"\*\*{label}\*\*\s*\|\s*(.+)", text)
                return m.group(1).strip() if m else "—"
            
            # Extract subject from H1
            subject_match = re.search(r"# 📧 Email — (.+)", text)
            subject = subject_match.group(1).strip() if subject_match else f.name
            
            notes.append({
                "file"     : f.name,
                "subject"  : subject,
                "sender"   : extract("From"),
                "date"     : extract("Date"),
                "category" : extract("Category").strip("`"),
                "reply"    : "Yes" in extract("Reply Required"),
                "mtime"    : datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "location" : f.parent.name # Show which folder it is in (Inbox/Done/Needs_Action)
            })
        except Exception:
            pass
    return notes


def parse_approvals():
    pending = []
    if not APPROVAL_DIR.exists():
        return pending
    for f in sorted(APPROVAL_DIR.glob("reply-*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            text = f.read_text(encoding="utf-8")
            def extract(label):
                m = re.search(rf"\*\*{label}\*\*\s*\|\s*(.+)", text)
                return m.group(1).strip() if m else "—"
            status = "PENDING"
            if "APPROVAL_STATUS: APPROVED" in text: status = "APPROVED"
            elif "APPROVAL_STATUS: REJECTED" in text: status = "REJECTED"
            pending.append({
                "file"    : f.name,
                "to"      : extract("To"),
                "subject" : extract("Subject"),
                "category": extract("Category").strip("`"),
                "status"  : status,
                "mtime"   : datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            })
        except Exception:
            pass
    return pending


def parse_log_tail(lines=60):
    if not GMAIL_LOG.exists():
        return []
    try:
        all_lines = GMAIL_LOG.read_text(encoding="utf-8").splitlines()
        return [l for l in all_lines if l.strip() and not l.startswith("#") and not l.startswith("---")][-lines:]
    except Exception:
        return []


def compute_stats(notes):
    cats = {"Sales": 0, "Client Support": 0, "Personal": 0}
    for n in notes:
        c = n["category"]
        cats[c] = cats.get(c, 0) + 1
    return cats


def get_latest_audit():
    if not AUDIT_DIR.exists():
        return None
    reports = sorted(AUDIT_DIR.glob("Email_Summary_*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not reports:
        return None
    try:
        return reports[0].read_text(encoding="utf-8")
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/emails")
def api_emails():
    return jsonify(parse_inbox_notes())

@app.route("/api/approvals")
def api_approvals():
    return jsonify(parse_approvals())

@app.route("/api/log")
def api_log():
    return jsonify(parse_log_tail(80))

@app.route("/api/stats")
def api_stats():
    notes = parse_inbox_notes()
    cats  = compute_stats(notes)
    return jsonify({
        "total"   : len(notes),
        "sales"   : cats.get("Sales", 0),
        "support" : cats.get("Client Support", 0),
        "personal": cats.get("Personal", 0),
        "pending" : sum(1 for a in parse_approvals() if a["status"] == "PENDING"),
    })

@app.route("/api/approve/<filename>", methods=["POST"])
def api_approve(filename):
    f = APPROVAL_DIR / filename
    if not f.exists():
        return jsonify({"error": "File not found"}), 404
    text = f.read_text(encoding="utf-8")
    text = text.replace("APPROVAL_STATUS: PENDING", "APPROVAL_STATUS: APPROVED")
    f.write_text(text, encoding="utf-8")
    return jsonify({"status": "APPROVED"})

@app.route("/api/reject/<filename>", methods=["POST"])
def api_reject(filename):
    f = APPROVAL_DIR / filename
    if not f.exists():
        return jsonify({"error": "File not found"}), 404
    text = f.read_text(encoding="utf-8")
    text = text.replace("APPROVAL_STATUS: PENDING", "APPROVAL_STATUS: REJECTED")
    f.write_text(text, encoding="utf-8")
    return jsonify({"status": "REJECTED"})

@app.route("/api/audit")
def api_audit():
    return jsonify({"content": get_latest_audit() or "No audit report yet."})

# ══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════════════════════════

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gmail Agent Dashboard — Digital FTE</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2235;
    --border: #1e2d45;
    --accent: #4f8ef7;
    --accent2: #7c3aed;
    --green: #10b981;
    --yellow: #f59e0b;
    --red: #ef4444;
    --orange: #f97316;
    --text: #e2e8f0;
    --muted: #64748b;
    --card-shadow: 0 4px 24px rgba(0,0,0,0.4);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; min-height: 100vh; }

  /* ── Header ── */
  .header {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
    display: flex; align-items: center; justify-content: space-between;
    height: 64px; position: sticky; top: 0; z-index: 100;
    box-shadow: 0 2px 20px rgba(79,142,247,0.1);
  }
  .logo { display: flex; align-items: center; gap: 12px; }
  .logo-icon { width: 36px; height: 36px; background: linear-gradient(135deg, #4f8ef7, #7c3aed); border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 18px; }
  .logo-text { font-size: 1.1rem; font-weight: 700; letter-spacing: -0.02em; }
  .logo-sub { font-size: 0.75rem; color: var(--muted); font-weight: 400; }
  .header-right { display: flex; align-items: center; gap: 12px; }
  .status-pill { background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3);
    color: var(--green); border-radius: 999px; padding: 4px 12px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em; }
  .status-dot { width: 7px; height: 7px; background: var(--green); border-radius: 50%; display: inline-block; margin-right: 6px;
    animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
  .refresh-btn { background: var(--surface2); border: 1px solid var(--border); color: var(--text);
    padding: 6px 14px; border-radius: 8px; cursor: pointer; font-size: 0.8rem; transition: all 0.2s; }
  .refresh-btn:hover { background: var(--accent); border-color: var(--accent); }

  /* ── Layout ── */
  .main { padding: 2rem; max-width: 1400px; margin: 0 auto; }
  .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }
  .grid-3 { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; }

  /* ── Stat Cards ── */
  .stat-card {
    background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
    padding: 1.25rem 1.5rem; position: relative; overflow: hidden; transition: transform 0.2s;
  }
  .stat-card:hover { transform: translateY(-2px); }
  .stat-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:16px 16px 0 0; }
  .stat-card.blue::before { background: linear-gradient(90deg, #4f8ef7, #7c3aed); }
  .stat-card.green::before { background: linear-gradient(90deg, #10b981, #059669); }
  .stat-card.orange::before { background: linear-gradient(90deg, #f97316, #f59e0b); }
  .stat-card.red::before { background: linear-gradient(90deg, #ef4444, #dc2626); }
  .stat-icon { font-size: 2rem; margin-bottom: 0.5rem; }
  .stat-value { font-size: 2.2rem; font-weight: 800; line-height: 1; margin-bottom: 4px; }
  .stat-label { font-size: 0.8rem; color: var(--muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
  .stat-card.blue .stat-value { color: var(--accent); }
  .stat-card.green .stat-value { color: var(--green); }
  .stat-card.orange .stat-value { color: var(--orange); }
  .stat-card.red .stat-value { color: var(--red); }

  /* ── Panel ── */
  .panel { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; }
  .panel-header { padding: 1rem 1.5rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
  .panel-title { font-size: 0.9rem; font-weight: 600; display: flex; align-items: center; gap: 8px; }
  .panel-badge { background: var(--surface2); border: 1px solid var(--border); border-radius: 999px; padding: 2px 10px; font-size: 0.72rem; color: var(--muted); }
  .panel-body { padding: 0; }

  /* ── Email Table ── */
  table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  th { padding: 0.6rem 1rem; background: var(--surface2); color: var(--muted); font-weight: 600; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; text-align: left; }
  td { padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); vertical-align: middle; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(255,255,255,0.02); }
  .subject-cell { font-weight: 500; max-width: 260px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .sender-cell { color: var(--muted); font-size: 0.78rem; max-width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .date-cell { color: var(--muted); font-size: 0.75rem; white-space: nowrap; }

  /* ── Category Badge ── */
  .badge { padding: 3px 10px; border-radius: 999px; font-size: 0.7rem; font-weight: 600; white-space: nowrap; }
  .badge-sales { background: rgba(79,142,247,0.15); color: #4f8ef7; border: 1px solid rgba(79,142,247,0.3); }
  .badge-support { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
  .badge-personal { background: rgba(100,116,139,0.15); color: #94a3b8; border: 1px solid rgba(100,116,139,0.2); }
  .badge-pending { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
  .badge-approved { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
  .badge-rejected { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

  /* ── Action buttons ── */
  .btn-approve { background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.4); color: var(--green);
    padding: 4px 12px; border-radius: 6px; cursor: pointer; font-size: 0.75rem; font-weight: 600; transition: all 0.2s; }
  .btn-approve:hover { background: var(--green); color: #fff; }
  .btn-reject { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); color: var(--red);
    padding: 4px 12px; border-radius: 6px; cursor: pointer; font-size: 0.75rem; font-weight: 600; transition: all 0.2s; margin-left: 6px; }
  .btn-reject:hover { background: var(--red); color: #fff; }
  .btn-disabled { opacity: 0.4; cursor: not-allowed; pointer-events: none; }

  /* ── Log ── */
  .log-box { background: #080d1a; border: 1px solid var(--border); border-radius: 12px; padding: 1rem;
    font-family: 'Courier New', monospace; font-size: 0.75rem; height: 280px; overflow-y: auto; line-height: 1.7; }
  .log-info  { color: #7dd3fc; }
  .log-warn  { color: #fbbf24; }
  .log-error { color: #f87171; }
  .log-server{ color: #a78bfa; }
  .log-ok    { color: #34d399; }
  .log-sent  { color: #86efac; font-weight: bold; }

  /* ── Scrollbars ── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: var(--surface); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  /* ── Empty state ── */
  .empty { padding: 3rem; text-align: center; color: var(--muted); }
  .empty-icon { font-size: 3rem; margin-bottom: 0.75rem; }
  .empty-text { font-size: 0.85rem; }

  /* ── Audit ── */
  .audit-box { padding: 1.25rem; font-size: 0.82rem; line-height: 1.8; white-space: pre-wrap; color: var(--text);
    background: #080d1a; border-radius: 0 0 16px 16px; max-height: 340px; overflow-y: auto; }

  /* ── Toast ── */
  #toast { position: fixed; bottom: 2rem; right: 2rem; background: var(--green); color: #fff;
    padding: 0.75rem 1.5rem; border-radius: 10px; font-size: 0.85rem; font-weight: 600;
    opacity: 0; transform: translateY(20px); transition: all 0.3s; z-index: 9999; pointer-events: none; }
  #toast.show { opacity: 1; transform: translateY(0); }
  #toast.error { background: var(--red); }

  /* ── Tabs ── */
  .tabs { display: flex; gap: 4px; padding: 0.75rem 1.5rem; border-bottom: 1px solid var(--border); }
  .tab { padding: 5px 14px; border-radius: 7px; font-size: 0.8rem; cursor: pointer; color: var(--muted); font-weight: 500; transition: all 0.2s; }
  .tab.active { background: var(--accent); color: #fff; }
  .tab:hover:not(.active) { background: var(--surface2); color: var(--text); }

  .tab-content { display: none; }
  .tab-content.active { display: block; }

  @media(max-width:900px) { .grid-4{grid-template-columns:repeat(2,1fr)} .grid-2,.grid-3{grid-template-columns:1fr} }
</style>
</head>
<body>

<header class="header">
  <div class="logo">
    <div class="logo-icon">📧</div>
    <div>
      <div class="logo-text">Gmail Agent Dashboard</div>
      <div class="logo-sub">Digital FTE — Gold Tier</div>
    </div>
  </div>
  <div class="header-right">
    <span class="status-pill"><span class="status-dot"></span>LIVE</span>
    <button class="refresh-btn" onclick="loadAll()">⟳ Refresh</button>
  </div>
</header>

<main class="main">

  <!-- Stats Row -->
  <div class="grid-4" id="stats-row">
    <div class="stat-card blue"><div class="stat-icon">📬</div><div class="stat-value" id="s-total">—</div><div class="stat-label">Total Processed</div></div>
    <div class="stat-card green"><div class="stat-icon">💼</div><div class="stat-value" id="s-sales">—</div><div class="stat-label">Sales</div></div>
    <div class="stat-card orange"><div class="stat-icon">🛟</div><div class="stat-value" id="s-support">—</div><div class="stat-label">Client Support</div></div>
    <div class="stat-card red"><div class="stat-icon">⏳</div><div class="stat-value" id="s-pending">—</div><div class="stat-label">Pending Approval</div></div>
  </div>

  <!-- Emails + Approvals -->
  <div class="grid-2">

    <!-- Email Inbox Notes -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">📥 Processed Emails <span class="panel-badge" id="email-count">0</span></div>
      </div>
      <div class="tabs">
        <div class="tab active" onclick="showTab('all')">All</div>
        <div class="tab" onclick="showTab('Sales')">Sales</div>
        <div class="tab" onclick="showTab('Client Support')">Support</div>
        <div class="tab" onclick="showTab('Personal')">Personal</div>
      </div>
      <div class="panel-body">
        <div id="email-table-wrap">
          <div class="empty"><div class="empty-icon">📭</div><div class="empty-text">No emails yet</div></div>
        </div>
      </div>
    </div>

    <!-- Approval Queue -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">✅ Approval Queue <span class="panel-badge" id="appr-count">0</span></div>
      </div>
      <div class="panel-body">
        <div id="approval-table-wrap">
          <div class="empty"><div class="empty-icon">🎉</div><div class="empty-text">No pending approvals</div></div>
        </div>
      </div>
    </div>

  </div>

  <!-- Log + Audit -->
  <div class="grid-3">

    <!-- Live Log -->
    <div class="panel">
      <div class="panel-header"><div class="panel-title">🖥 Live Event Log</div></div>
      <div style="padding:1rem">
        <div class="log-box" id="log-box">Loading…</div>
      </div>
    </div>

    <!-- Audit Report -->
    <div class="panel">
      <div class="panel-header"><div class="panel-title">📊 Latest Audit Report</div></div>
      <div class="audit-box" id="audit-box">Loading…</div>
    </div>

  </div>

</main>

<div id="toast"></div>

<script>
let allEmails = [];
let currentTab = 'all';

function toast(msg, type='ok') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = type === 'error' ? 'show error' : 'show';
  setTimeout(() => el.className = '', 2500);
}

function catBadge(c) {
  if (c === 'Sales') return '<span class="badge badge-sales">💼 Sales</span>';
  if (c === 'Client Support') return '<span class="badge badge-support">🛟 Support</span>';
  return '<span class="badge badge-personal">👤 Personal</span>';
}

function statusBadge(s) {
  if (s === 'APPROVED') return '<span class="badge badge-approved">✅ Approved</span>';
  if (s === 'REJECTED') return '<span class="badge badge-rejected">🚫 Rejected</span>';
  return '<span class="badge badge-pending">⏳ Pending</span>';
}

function showTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');
  renderEmails();
}

function renderEmails() {
  const list = currentTab === 'all' ? allEmails : allEmails.filter(e => e.category === currentTab);
  const wrap = document.getElementById('email-table-wrap');
  if (!list.length) { wrap.innerHTML = '<div class="empty"><div class="empty-icon">📭</div><div class="empty-text">No emails in this category</div></div>'; return; }
  wrap.innerHTML = `<table>
    <thead><tr><th>Subject</th><th>Sender</th><th>Category</th><th>Date</th></tr></thead>
    <tbody>${list.map(e => `<tr>
      <td class="subject-cell" title="${e.subject}">${e.subject}</td>
      <td class="sender-cell" title="${e.sender}">${e.sender}</td>
      <td>${catBadge(e.category)}</td>
      <td class="date-cell">${e.mtime}</td>
    </tr>`).join('')}</tbody>
  </table>`;
}

async function loadEmails() {
  const r = await fetch('/api/emails');
  allEmails = await r.json();
  document.getElementById('email-count').textContent = allEmails.length;
  renderEmails();
}

async function loadApprovals() {
  const r = await fetch('/api/approvals');
  const list = await r.json();
  document.getElementById('appr-count').textContent = list.length;
  const wrap = document.getElementById('approval-table-wrap');
  if (!list.length) { wrap.innerHTML = '<div class="empty"><div class="empty-icon">🎉</div><div class="empty-text">No pending approvals</div></div>'; return; }
  wrap.innerHTML = `<table>
    <thead><tr><th>Subject</th><th>Category</th><th>Status</th><th>Action</th></tr></thead>
    <tbody>${list.map(a => `<tr>
      <td class="subject-cell" title="${a.subject}">${a.subject}</td>
      <td>${catBadge(a.category)}</td>
      <td>${statusBadge(a.status)}</td>
      <td>${a.status === 'PENDING'
        ? `<button class="btn-approve" onclick="doApprove('${a.file}')">✅ Approve</button>
           <button class="btn-reject"  onclick="doReject('${a.file}')">🚫 Reject</button>`
        : '<span style="color:var(--muted);font-size:0.75rem">Done</span>'
      }</td>
    </tr>`).join('')}</tbody>
  </table>`;
}

async function doApprove(file) {
  await fetch('/api/approve/' + file, {method:'POST'});
  toast('✅ Reply approved — agent will send shortly!');
  setTimeout(loadApprovals, 500);
}
async function doReject(file) {
  await fetch('/api/reject/' + file, {method:'POST'});
  toast('🚫 Reply rejected and discarded.', 'error');
  setTimeout(loadApprovals, 500);
}

async function loadLog() {
  const r = await fetch('/api/log');
  const lines = await r.json();
  const box = document.getElementById('log-box');
  box.innerHTML = lines.map(l => {
    let cls = 'log-info';
    if (l.includes('[WARN]') || l.includes('WARN')) cls = 'log-warn';
    else if (l.includes('[ERROR]') || l.includes('FATAL')) cls = 'log-error';
    else if (l.includes('[GMAIL_SERVER]')) cls = 'log-server';
    else if (l.includes('✅') || l.includes('COMPLETE')) cls = 'log-ok';
    else if (l.includes('✉️') || l.includes('SENT')) cls = 'log-sent';
    return `<div class="${cls}">${l}</div>`;
  }).join('');
  box.scrollTop = box.scrollHeight;
}

async function loadStats() {
  const r = await fetch('/api/stats');
  const s = await r.json();
  document.getElementById('s-total').textContent   = s.total;
  document.getElementById('s-sales').textContent   = s.sales;
  document.getElementById('s-support').textContent = s.support;
  document.getElementById('s-pending').textContent = s.pending;
}

async function loadAudit() {
  const r = await fetch('/api/audit');
  const d = await r.json();
  document.getElementById('audit-box').textContent = d.content;
}

async function loadAll() {
  await Promise.all([loadStats(), loadEmails(), loadApprovals(), loadLog(), loadAudit()]);
}

// Auto-refresh every 10 seconds
loadAll();
setInterval(loadAll, 10000);
</script>
</body>
</html>'''

@app.route("/")
def index():
    return HTML

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  📧  Gmail Agent Dashboard")
    print("  🌐  http://localhost:5050")
    print("  Press Ctrl+C to stop")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=5050, debug=False)
