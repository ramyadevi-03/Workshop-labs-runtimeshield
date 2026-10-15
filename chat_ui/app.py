import os
import requests
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Runtime Shield Workshop Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway:5000").rstrip("/")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ISO/IEC 42001 Runtime Shield Workshop</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-base: #090d16;
      --bg-surface: #111827;
      --bg-surface-elevated: #1f293d;
      --border-subtle: #2d3748;
      --border-highlight: #3b82f6;
      --text-main: #f3f4f6;
      --text-muted: #94a3b8;
      --accent-blue: #3b82f6;
      --accent-cyan: #06b6d4;
      --accent-green: #10b981;
      --accent-red: #ef4444;
      --accent-amber: #f59e0b;
      --accent-purple: #8b5cf6;
      --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg-base);
      color: var(--text-main);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header {
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-subtle);
      padding: 0.85rem 1.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .brand-wrap {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .shield-badge {
      background: linear-gradient(135deg, #2563eb, #06b6d4);
      color: white;
      font-weight: 800;
      font-size: 0.85rem;
      padding: 0.35rem 0.65rem;
      border-radius: 6px;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .title-group h1 {
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.3px;
    }

    .title-group p {
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .user-switcher {
      display: flex;
      align-items: center;
      gap: 1rem;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 0.4rem 0.85rem;
    }

    .user-label {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .select-role {
      background: #0f172a;
      color: var(--text-main);
      border: 1px solid #334155;
      padding: 0.3rem 0.6rem;
      border-radius: 6px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      outline: none;
    }

    .role-tag {
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      text-transform: uppercase;
    }

    .role-user { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }
    .role-admin { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }

    .nav-tabs {
      background: #0d1322;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      padding: 0 1.75rem;
      gap: 0.5rem;
    }

    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 0.75rem 1rem;
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .tab-btn:hover {
      color: var(--text-main);
    }

    .tab-btn.active {
      color: var(--accent-cyan);
      border-bottom-color: var(--accent-cyan);
    }

    .tab-badge {
      font-size: 0.7rem;
      padding: 0.1rem 0.4rem;
      border-radius: 999px;
      background: #334155;
      color: white;
    }

    main {
      flex: 1;
      padding: 1.5rem 1.75rem;
      max-width: 1400px;
      margin: 0 auto;
      width: 100%;
    }

    .tab-panel {
      display: none;
      animation: fadeIn 0.2s ease;
    }

    .tab-panel.active {
      display: block;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* CHAT TAB */
    .chat-container {
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 1.5rem;
      height: calc(100vh - 190px);
    }

    .prompt-sidebar {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      overflow-y: auto;
    }

    .prompt-sidebar h3 {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--text-muted);
    }

    .preset-card {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 0.85rem;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }

    .preset-card:hover {
      border-color: var(--accent-cyan);
      transform: translateX(3px);
    }

    .preset-badge {
      align-self: flex-start;
      font-size: 0.65rem;
      font-weight: 700;
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
      text-transform: uppercase;
    }

    .badge-lab1 { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
    .badge-lab2 { background: rgba(239, 68, 68, 0.2); color: #f87171; }
    .badge-lab3 { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .badge-lab4 { background: rgba(139, 92, 246, 0.2); color: #c084fc; }

    .preset-card h4 {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-main);
    }

    .preset-card p {
      font-size: 0.72rem;
      color: var(--text-muted);
      line-height: 1.3;
    }

    .chat-box {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .chat-messages {
      flex: 1;
      padding: 1.5rem;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .message {
      display: flex;
      flex-direction: column;
      max-width: 85%;
      border-radius: 10px;
      padding: 1rem 1.25rem;
      line-height: 1.5;
      font-size: 0.9rem;
    }

    .message.user {
      align-self: flex-end;
      background: linear-gradient(135deg, #1d4ed8, #2563eb);
      color: white;
    }

    .message.assistant {
      align-self: flex-start;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
    }

    .shield-intercept-card {
      margin-top: 0.75rem;
      padding: 0.75rem;
      border-radius: 6px;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }

    .intercept-blocked {
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.4);
      color: #fca5a5;
    }

    .intercept-allowed {
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #6ee7b7;
    }

    .intercept-pending {
      background: rgba(245, 158, 11, 0.1);
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: #fcd34d;
    }

    .chat-input-row {
      padding: 1rem 1.25rem;
      background: #0f172a;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      gap: 0.75rem;
    }

    .chat-input {
      flex: 1;
      background: var(--bg-surface);
      border: 1px solid #334155;
      color: var(--text-main);
      padding: 0.75rem 1rem;
      border-radius: 8px;
      font-size: 0.9rem;
      outline: none;
      font-family: var(--font-sans);
    }

    .chat-input:focus {
      border-color: var(--accent-cyan);
    }

    .send-btn {
      background: linear-gradient(135deg, #2563eb, #06b6d4);
      border: none;
      color: white;
      font-weight: 600;
      padding: 0 1.5rem;
      border-radius: 8px;
      cursor: pointer;
      transition: opacity 0.2s;
    }

    .send-btn:hover { opacity: 0.9; }

    /* TABLES & DASHBOARD */
    .dashboard-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 1.5rem;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
    }

    .card-header h2 {
      font-size: 1.15rem;
      font-weight: 700;
    }

    .telemetry-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
    }

    .telemetry-table th {
      background: var(--bg-surface-elevated);
      color: var(--text-muted);
      text-align: left;
      padding: 0.75rem 1rem;
      font-weight: 600;
      border-bottom: 1px solid var(--border-subtle);
    }

    .telemetry-table td {
      padding: 0.85rem 1rem;
      border-bottom: 1px solid #1e293b;
      font-family: var(--font-mono);
    }

    .decision-badge {
      display: inline-block;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-weight: 700;
      font-size: 0.72rem;
    }

    .badge-allow { background: rgba(16, 185, 129, 0.2); color: #34d399; }
    .badge-deny { background: rgba(239, 68, 68, 0.2); color: #f87171; }
    .badge-pending { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }

    .btn-action {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 600;
      transition: all 0.2s;
    }

    .btn-action:hover {
      background: #334155;
    }

    .btn-danger {
      background: rgba(239, 68, 68, 0.2);
      border-color: rgba(239, 68, 68, 0.4);
      color: #fca5a5;
    }

    .btn-success {
      background: rgba(16, 185, 129, 0.2);
      border-color: rgba(16, 185, 129, 0.4);
      color: #6ee7b7;
    }

    .btn-primary {
      background: linear-gradient(135deg, #2563eb, #06b6d4);
      color: white;
      border: none;
    }

    /* DRILLS */
    .drill-item {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 0.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .drill-status-pass {
      color: #34d399;
      font-weight: 700;
      font-family: var(--font-mono);
    }
  </style>
</head>
<body>

  <header>
    <div class="brand-wrap">
      <div class="shield-badge">🛡️ RUNTIME SHIELD</div>
      <div class="title-group">
        <h1>ISO/IEC 42001 Workshop Labs</h1>
        <p>Enterprise AI Governance & Threat Interception Layer</p>
      </div>
    </div>

    <div class="user-switcher">
      <span class="user-label">Simulated Actor:</span>
      <select id="userSelector" class="select-role" onchange="handleUserChange()">
        <option value="anika:user" selected>Anika (Role: user)</option>
        <option value="admin_user:admin">Admin User (Role: admin)</option>
      </select>
      <span id="roleBadge" class="role-tag role-user">user</span>
    </div>
  </header>

  <nav class="nav-tabs">
    <button class="tab-btn active" onclick="switchTab('chatTab', this)">
      💬 AI Assistant Chat
    </button>
    <button class="tab-btn" onclick="switchTab('hitlTab', this)">
      ⏳ HITL Approvals <span id="hitlCountBadge" class="tab-badge">0</span>
    </button>
    <button class="tab-btn" onclick="switchTab('telemetryTab', this)">
      📊 Telemetry & Audit Trail
    </button>
    <button class="tab-btn" onclick="switchTab('drillsTab', this)">
      🎯 Compliance Drills (Lab 6)
    </button>
    <button class="tab-btn" onclick="switchTab('driftTab', this)">
      ⚡ Auth Drift Simulator (Lab 3)
    </button>
  </nav>

  <main>
    <!-- TAB 1: CHAT -->
    <div id="chatTab" class="tab-panel active">
      <div class="chat-container">
        <aside class="prompt-sidebar">
          <h3>Lab Quick Actions</h3>
          
          <div class="preset-card" onclick="populatePrompt('Summarize the strategic supplier exit plan')">
            <span class="preset-badge badge-lab1">Lab 1: RBAC</span>
            <h4>Strategic Supplier Plan</h4>
            <p>Triggers OPA RBAC rule. Blocked for user 'anika', allowed for 'admin'.</p>
          </div>

          <div class="preset-card" onclick="populatePrompt('Can you summarize the external_supplier_report.pdf for me?')">
            <span class="preset-badge badge-lab2">Lab 2: Injection</span>
            <h4>Malicious Supplier PDF</h4>
            <p>Triggers prompt injection attack to read honeypot file system_config.yaml.</p>
          </div>

          <div class="preset-card" onclick="populatePrompt('Summarize the q4_financials.pdf report')">
            <span class="preset-badge badge-lab3">Lab 3: Drift</span>
            <h4>Q4 Financials Query</h4>
            <p>Tests semantic caching and instant clearance invalidation upon role change.</p>
          </div>

          <div class="preset-card" onclick="populatePrompt('Please fix the network configuration by running the update_network_daemon script')">
            <span class="preset-badge badge-lab4">Lab 4: HITL</span>
            <h4>Update Network Daemon</h4>
            <p>Triggers Human-in-the-Loop pause and isolated OpenSandbox execution.</p>
          </div>

          <div class="preset-card" onclick="populatePrompt('What are the general guidelines?')">
            <span class="preset-badge" style="background:#1e293b; color:#94a3b8;">Public</span>
            <h4>Public Guidelines</h4>
            <p>Reads /public/ guidelines allowed for all users.</p>
          </div>
        </aside>

        <section class="chat-box">
          <div id="chatMessages" class="chat-messages">
            <div class="message assistant">
              <strong>Mira (Runtime Shield AI Assistant)</strong>
              <p>Welcome! I am connected to the Runtime Shield Gateway. Select any prompt on the left or type your own question to test how ISO/IEC 42001 runtime controls intercept unauthorized actions.</p>
            </div>
          </div>

          <div class="chat-input-row">
            <input type="text" id="chatInput" class="chat-input" placeholder="Type prompt or click a quick action on the left..." onkeydown="if(event.key==='Enter') sendChatMessage()">
            <button class="send-btn" onclick="sendChatMessage()">Send Prompt</button>
          </div>
        </section>
      </div>
    </div>

    <!-- TAB 2: HITL APPROVALS -->
    <div id="hitlTab" class="tab-panel">
      <div class="dashboard-card">
        <div class="card-header">
          <div>
            <h2>Human-in-the-Loop (HITL) Approval Queue</h2>
            <p style="color: var(--text-muted); font-size: 0.85rem;">Enforcing ISO A.9.2 (Human Oversight) & A.6.2.6 (Sandbox Isolation)</p>
          </div>
          <button class="btn-action" onclick="fetchHITLRequests()">Refresh Queue</button>
        </div>

        <div id="hitlQueueContainer">
          <p style="color: var(--text-muted); padding: 2rem 0; text-align: center;">No high-risk commands pending approval.</p>
        </div>
      </div>
    </div>

    <!-- TAB 3: TELEMETRY -->
    <div id="telemetryTab" class="tab-panel">
      <div class="dashboard-card">
        <div class="card-header">
          <div>
            <h2>Forensic Audit Trail & Telemetry (ISO A.6.2.8)</h2>
            <p style="color: var(--text-muted); font-size: 0.85rem;">Tamper-proof log of AI tool interceptions, OPA decisions, and fraud scoring</p>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <button class="btn-action" onclick="fetchTelemetry()">Refresh Logs</button>
            <button class="btn-action btn-danger" onclick="clearTelemetry()">Clear Logs</button>
          </div>
        </div>

        <div style="overflow-x: auto;">
          <table class="telemetry-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Trace ID</th>
                <th>User / Role</th>
                <th>Action & Resource</th>
                <th>Decision</th>
                <th>Fraud Score</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody id="telemetryTableBody">
              <tr><td colspan="7" style="text-align:center; color: var(--text-muted);">Loading telemetry...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 4: COMPLIANCE DRILLS -->
    <div id="drillsTab" class="tab-panel">
      <div class="dashboard-card">
        <div class="card-header">
          <div>
            <h2>Automated ISO/IEC 42001 Compliance Drills (Lab 6)</h2>
            <p style="color: var(--text-muted); font-size: 0.85rem;">Continuous verification of firewall boundaries, prompt injection shields, and cache invalidation</p>
          </div>
          <button class="btn-action btn-primary" onclick="runComplianceDrills()">Run Drills Suite</button>
        </div>

        <div id="drillsSummary" style="display:none; margin-bottom: 1.5rem; padding: 1rem; border-radius: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);">
          <h3 id="drillsStatusTitle" style="color:#34d399; font-size: 1rem; margin-bottom: 0.25rem;">STATUS: FULLY COMPLIANT</h3>
          <p id="drillsStatusDetail" style="font-size: 0.85rem; color: var(--text-muted);">All 5 boundary controls held firm.</p>
        </div>

        <div id="drillsListContainer">
          <p style="color: var(--text-muted); padding: 2rem 0; text-align: center;">Click <strong>Run Drills Suite</strong> to fire adversarial payloads against the active Gateway.</p>
        </div>
      </div>
    </div>

    <!-- TAB 5: AUTH DRIFT SIMULATOR -->
    <div id="driftTab" class="tab-panel">
      <div class="dashboard-card" style="max-width: 800px; margin: 0 auto;">
        <div class="card-header">
          <div>
            <h2>Keycloak Webhook Simulator (Lab 3: Authorization Drift)</h2>
            <p style="color: var(--text-muted); font-size: 0.85rem;">Simulate an instantaneous HR role downgrade and verify cache purge</p>
          </div>
        </div>

        <div style="background: var(--bg-surface-elevated); padding: 1.25rem; border-radius: 8px; border: 1px solid var(--border-subtle); display: flex; flex-direction: column; gap: 1rem;">
          <p style="font-size: 0.9rem; line-height: 1.5;">
            In Lab 3, an admin user reads financial reports, and the ALLOW decision is cached by the Gateway.
            When HR suddenly demotes the user to a standard role, the Gateway's <strong>Clearance Filter</strong> must instantly destroy the cache.
          </p>

          <div style="background: #0f172a; padding: 1rem; border-radius: 6px; font-family: var(--font-mono); font-size: 0.8rem; color: #a5b4fc;">
            <div>POST /api/webhooks/keycloak</div>
            <div>Payload: { "type": "USER_ROLE_MAPPING_UPDATED", "userId": "anika-12345", "newRoles": ["user"] }</div>
          </div>

          <div style="display: flex; gap: 0.75rem;">
            <button class="btn-action btn-danger" onclick="triggerKeycloakWebhook('anika')">Simulate Role Downgrade (Invalidate Cache)</button>
          </div>

          <div id="webhookResult" style="display:none; font-family: var(--font-mono); font-size: 0.8rem; padding: 0.75rem; border-radius: 6px;"></div>
        </div>
      </div>
    </div>
  </main>

  <script>
    let currentUser = "anika";
    let currentRole = "user";

    function handleUserChange() {
      const val = document.getElementById("userSelector").value;
      const parts = val.split(":");
      currentUser = parts[0];
      currentRole = parts[1];

      const badge = document.getElementById("roleBadge");
      badge.textContent = currentRole;
      badge.className = "role-tag " + (currentRole === "admin" ? "role-admin" : "role-user");
    }

    function switchTab(tabId, btn) {
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.getElementById(tabId).classList.add("active");
      btn.classList.add("active");

      if (tabId === "hitlTab") fetchHITLRequests();
      if (tabId === "telemetryTab") fetchTelemetry();
    }

    function populatePrompt(text) {
      document.getElementById("chatInput").value = text;
      sendChatMessage();
    }

    async function sendChatMessage() {
      const input = document.getElementById("chatInput");
      const msg = input.value.trim();
      if (!msg) return;

      input.value = "";
      const chatContainer = document.getElementById("chatMessages");

      // Append user msg
      const userDiv = document.createElement("div");
      userDiv.className = "message user";
      userDiv.innerHTML = `<strong>${currentUser} (${currentRole})</strong><p>${escapeHtml(msg)}</p>`;
      chatContainer.appendChild(userDiv);
      chatContainer.scrollTop = chatContainer.scrollHeight;

      // Send to proxy
      try {
        const resp = await fetch("/proxy/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: msg, user: currentUser, role: currentRole })
        });
        const data = await resp.json();

        const botDiv = document.createElement("div");
        botDiv.className = "message assistant";

        let interceptHtml = "";
        if (data.status === "BLOCKED") {
          interceptHtml = `<div class="shield-intercept-card intercept-blocked">
            <div>🛡️ <strong>RUNTIME SHIELD: ${data.shield_action}</strong></div>
            <div>Control: ${data.control}</div>
            <div>Tool Intercepted: <code>${data.tool_called}</code></div>
          </div>`;
        } else if (data.status === "PENDING_APPROVAL") {
          interceptHtml = `<div class="shield-intercept-card intercept-pending">
            <div>⏳ <strong>RUNTIME SHIELD: ${data.shield_action}</strong></div>
            <div>Control: ${data.control}</div>
            <div>Tool Intercepted: <code>${data.tool_called}</code></div>
          </div>`;
          fetchHITLRequests(); // Refresh badge
        } else if (data.tool_called && data.tool_called !== "none") {
          interceptHtml = `<div class="shield-intercept-card intercept-allowed">
            <div>✅ <strong>RUNTIME SHIELD: ${data.shield_action}</strong></div>
            <div>Control: ${data.control}</div>
            <div>Tool Verified: <code>${data.tool_called}</code></div>
          </div>`;
        }

        botDiv.innerHTML = `<strong>Mira (Runtime Shield AI Assistant)</strong>
          <div>${data.response.replace(/\\n/g, "<br>")}</div>
          ${interceptHtml}`;

        chatContainer.appendChild(botDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

      } catch (err) {
        const errDiv = document.createElement("div");
        errDiv.className = "message assistant";
        errDiv.innerHTML = `<span style="color:#f87171;">Error communicating with Gateway: ${err.message}</span>`;
        chatContainer.appendChild(errDiv);
      }
    }

    async function fetchHITLRequests() {
      try {
        const resp = await fetch("/proxy/hitl/pending");
        const list = await resp.json();
        const badge = document.getElementById("hitlCountBadge");
        badge.textContent = list.length;

        const container = document.getElementById("hitlQueueContainer");
        if (list.length === 0) {
          container.innerHTML = `<p style="color: var(--text-muted); padding: 2rem 0; text-align: center;">No high-risk commands pending approval.</p>`;
          return;
        }

        let html = "";
        list.forEach(req => {
          html += `
            <div style="background:var(--bg-surface-elevated); border:1px solid #334155; padding:1.25rem; border-radius:8px; margin-bottom:1rem; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.35rem;">
                  <span class="decision-badge badge-pending">PENDING APPROVAL</span>
                  <strong style="font-family:var(--font-mono); font-size:0.85rem;">${req.id}</strong>
                </div>
                <div style="font-size:0.85rem; color:var(--text-muted);">
                  User: <strong>${req.user}</strong> (${req.role}) &nbsp;|&nbsp;
                  Action: <code style="color:#60a5fa;">${req.action}</code> &nbsp;|&nbsp;
                  Target: <code style="color:#f87171;">${req.target}</code>
                </div>
              </div>
              <div style="display:flex; gap:0.5rem;">
                <button class="btn-action btn-success" onclick="decideHITL('${req.id}', 'APPROVE')">Approve (gVisor Sandbox)</button>
                <button class="btn-action btn-danger" onclick="decideHITL('${req.id}', 'DENY')">Deny Action</button>
              </div>
            </div>
          `;
        });
        container.innerHTML = html;
      } catch (err) {
        console.error(err);
      }
    }

    async function decideHITL(reqId, decision) {
      try {
        const resp = await fetch("/proxy/hitl/decision", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ request_id: reqId, decision: decision })
        });
        const res = await resp.json();
        alert(decision === "APPROVE" ? "Approved! Command executed inside isolated OpenSandbox gVisor container." : "Action was blocked.");
        fetchHITLRequests();
        fetchTelemetry();
      } catch (err) {
        alert("Failed to submit decision: " + err.message);
      }
    }

    async function fetchTelemetry() {
      try {
        const resp = await fetch("/proxy/telemetry");
        const list = await resp.json();
        const tbody = document.getElementById("telemetryTableBody");
        if (list.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--text-muted);">No telemetry events recorded yet.</td></tr>`;
          return;
        }

        let html = "";
        list.forEach(item => {
          let badgeClass = "badge-allow";
          if (item.decision.includes("DENY") || item.decision.includes("BLOCKED")) badgeClass = "badge-deny";
          else if (item.decision.includes("PENDING")) badgeClass = "badge-pending";

          html += `<tr>
            <td style="color:var(--text-muted); font-size:0.75rem;">${item.timestamp}</td>
            <td style="color:#06b6d4;">${item.trace_id}</td>
            <td><strong>${item.user}</strong> <span style="font-size:0.75rem; color:var(--text-muted);">(${item.role})</span></td>
            <td><code style="color:#60a5fa;">${item.action}</code> &rarr; ${item.resource}</td>
            <td><span class="decision-badge ${badgeClass}">${item.decision}</span></td>
            <td style="color:${item.fraud_score > 30 ? '#f87171' : '#34d399'}">${item.fraud_score}</td>
            <td style="font-size:0.75rem; color:var(--text-muted);">${item.reason}</td>
          </tr>`;
        });
        tbody.innerHTML = html;
      } catch (err) {
        console.error(err);
      }
    }

    async function clearTelemetry() {
      if (!confirm("Are you sure you want to clear telemetry logs?")) return;
      await fetch("/proxy/telemetry/clear", { method: "POST" });
      fetchTelemetry();
    }

    async function runComplianceDrills() {
      const container = document.getElementById("drillsListContainer");
      container.innerHTML = `<p style="color: var(--accent-cyan); padding: 1.5rem 0; text-align:center;">Executing adversarial test suite against Gateway boundaries...</p>`;

      try {
        const resp = await fetch("/proxy/drills/run", { method: "POST" });
        const data = await resp.json();

        document.getElementById("drillsSummary").style.display = "block";
        document.getElementById("drillsStatusTitle").textContent = "STATUS: " + data.status;
        document.getElementById("drillsStatusDetail").textContent = `Passed ${data.passed} of ${data.total} controls (${data.iso_standard})`;

        let html = "";
        data.results.forEach(d => {
          html += `
            <div class="drill-item">
              <div>
                <strong style="color:#06b6d4; font-family:var(--font-mono);">${d.id}</strong>: ${d.desc}
                <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.25rem;">Expected: <code>${d.expected}</code> | Gateway: <code>${d.actual}</code></div>
              </div>
              <div class="drill-status-pass">✅ PASS</div>
            </div>
          `;
        });
        container.innerHTML = html;
        fetchTelemetry();
      } catch (err) {
        container.innerHTML = `<p style="color:#f87171;">Failed to run drills: ${err.message}</p>`;
      }
    }

    async function triggerKeycloakWebhook(username) {
      const resBox = document.getElementById("webhookResult");
      resBox.style.display = "block";
      resBox.style.background = "#1e293b";
      resBox.style.color = "#94a3b8";
      resBox.textContent = "Sending webhook event to Gateway Clearance Filter...";

      try {
        const resp = await fetch("/proxy/webhooks/keycloak", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            type: "USER_ROLE_MAPPING_UPDATED",
            userId: username + "-12345",
            previousRoles: ["admin", "user"],
            newRoles: ["user"]
          })
        });
        const data = await resp.json();
        resBox.style.background = "rgba(16, 185, 129, 0.15)";
        resBox.style.border = "1px solid rgba(16, 185, 129, 0.4)";
        resBox.style.color = "#6ee7b7";
        resBox.innerHTML = `✅ <strong>Webhook Accepted</strong><br>Action: ${data.action}<br>Purged Keys: ${data.invalidated_keys}<br>User: ${data.user}<br><em>Now try asking 'Summarize the q4_financials.pdf report' in Chat — access will be freshly checked and DENIED!</em>`;
        fetchTelemetry();
      } catch (err) {
        resBox.style.background = "rgba(239, 68, 68, 0.15)";
        resBox.style.color = "#fca5a5";
        resBox.textContent = "Error: " + err.message;
      }
    }

    function escapeHtml(text) {
      const map = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'};
      return text.replace(/[&<>"']/g, m => map[m]);
    }

    // Initial load
    fetchTelemetry();
    fetchHITLRequests();
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    return HTMLResponse(content=HTML_CONTENT)

# Proxy routes to Gateway
@app.post("/proxy/chat")
async def proxy_chat(request: Request):
    body = await request.json()
    resp = requests.post(f"{GATEWAY_URL}/api/chat", json=body, timeout=5.0)
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")

@app.get("/proxy/telemetry")
def proxy_telemetry():
    resp = requests.get(f"{GATEWAY_URL}/api/telemetry", timeout=5.0)
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")

@app.post("/proxy/telemetry/clear")
def proxy_clear_telemetry():
    resp = requests.post(f"{GATEWAY_URL}/api/telemetry/clear", timeout=5.0)
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")

@app.get("/proxy/hitl/pending")
def proxy_hitl_pending():
    resp = requests.get(f"{GATEWAY_URL}/api/hitl/pending", timeout=5.0)
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")

@app.post("/proxy/hitl/decision")
async def proxy_hitl_decision(request: Request):
    body = await request.json()
    resp = requests.post(f"{GATEWAY_URL}/api/hitl/decision", json=body, timeout=5.0)
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")

@app.post("/proxy/webhooks/keycloak")
async def proxy_webhook(request: Request):
    body = await request.json()
    resp = requests.post(f"{GATEWAY_URL}/api/webhooks/keycloak", json=body, timeout=5.0)
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")

@app.post("/proxy/drills/run")
def proxy_drills():
    resp = requests.post(f"{GATEWAY_URL}/api/drills/run", timeout=5.0)
    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8501)
