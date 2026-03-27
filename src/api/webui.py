"""
p9i Web UI - Dashboard for monitoring and management
"""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import datetime
import secrets
import hashlib

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="p9i Dashboard",
    description="Web UI for p9i AI Prompt System",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# HTML Dashboard Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>p9i Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #eee;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .logo { font-size: 28px; font-weight: bold; color: #00d4ff; }
        .status-badge {
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        .status-running { background: #10b981; color: white; }
        .status-stopped { background: #ef4444; color: white; }

        .container { padding: 40px; max-width: 1400px; margin: 0 auto; }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .stat-card h3 {
            font-size: 14px;
            color: #888;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat-card .value {
            font-size: 36px;
            font-weight: bold;
            color: #00d4ff;
        }
        .stat-card .value.green { color: #10b981; }
        .stat-card .value.yellow { color: #f59e0b; }

        .section {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .section h2 {
            font-size: 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .section h2 span { color: #00d4ff; }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 16px;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
        }
        .info-item .label { color: #888; }
        .info-item .value { color: #fff; font-family: monospace; }

        .endpoints {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
        }
        .endpoint {
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            padding: 16px;
        }
        .endpoint .method {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 10px;
        }
        .method-get { background: #10b981; color: white; }
        .method-post { background: #3b82f6; color: white; }
        .endpoint .path { font-family: monospace; color: #00d4ff; }
        .endpoint .desc { color: #888; font-size: 14px; margin-top: 8px; }

        .logs {
            background: #0d1117;
            border-radius: 8px;
            padding: 16px;
            max-height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 13px;
        }
        .log-entry { padding: 4px 0; color: #888; }
        .log-entry .time { color: #555; margin-right: 10px; }
        .log-entry .msg { color: #aaa; }

        .footer {
            text-align: center;
            padding: 20px;
            color: #555;
            font-size: 14px;
        }

        /* Auth Styles */
        .auth-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        .auth-overlay.hidden { display: none; }
        .auth-box {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 40px;
            border-radius: 16px;
            border: 1px solid rgba(0,212,255,0.3);
            width: 100%;
            max-width: 360px;
            text-align: center;
        }
        .auth-box h2 {
            color: #00d4ff;
            margin-bottom: 24px;
        }
        .auth-input {
            width: 100%;
            padding: 12px 16px;
            margin-bottom: 16px;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
        }
        .auth-input:focus {
            outline: none;
            border-color: #00d4ff;
        }
        .auth-btn {
            width: 100%;
            padding: 12px;
            background: #00d4ff;
            color: #000;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .auth-btn:hover { background: #00b8e6; }
        .auth-error {
            color: #ef4444;
            margin-top: 12px;
            font-size: 14px;
        }
        .user-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .user-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #00d4ff;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-weight: bold;
            font-size: 14px;
        }
        .logout-btn {
            padding: 6px 12px;
            background: rgba(255,255,255,0.1);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
        }
        .logout-btn:hover { background: rgba(255,255,255,0.2); }

        .dashboard-content { display: block; }
        .dashboard-content.auth-required { display: none; }
    </style>
</head>
<body>
    <!-- Auth Overlay -->
    <div id="authOverlay" class="auth-overlay">
        <div class="auth-box">
            <h2>p9i Login</h2>
            <input type="text" id="authUsername" class="auth-input" placeholder="Username" autocomplete="username">
            <input type="password" id="authPassword" class="auth-input" placeholder="Password" autocomplete="current-password" onkeypress="if(event.key==='Enter')doLogin()">
            <button onclick="doLogin()" class="auth-btn">Sign In</button>
            <div id="authError" class="auth-error"></div>
        </div>
    </div>

    <div class="header">
        <div class="logo">p9i</div>
        <div id="userSection" class="user-info" style="display: none;">
            <div class="user-avatar" id="userAvatar">?</div>
            <span id="userName"></span>
            <button onclick="doLogout()" class="logout-btn">Logout</button>
        </div>
        <div id="loginBtn" class="status-badge" style="cursor: pointer;" onclick="showLogin()">Login</div>
    </div>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Uptime</h3>
                <div class="value" id="uptime">--</div>
            </div>
            <div class="stat-card">
                <h3>CPU Usage</h3>
                <div class="value" id="cpu">--%</div>
            </div>
            <div class="stat-card">
                <h3>Memory</h3>
                <div class="value" id="memory">--%</div>
            </div>
            <div class="stat-card">
                <h3>Requests</h3>
                <div class="value green" id="requests">0</div>
            </div>
        </div>

        <div class="section">
            <h2><span>▣</span> System Info</h2>
            <div class="info-grid">
                <div class="info-item">
                    <span class="label">Version</span>
                    <span class="value">1.0.0</span>
                </div>
                <div class="info-item">
                    <span class="label">Transport</span>
                    <span class="value">{{ transport }}</span>
                </div>
                <div class="info-item">
                    <span class="label">Port</span>
                    <span class="value">{{ port }}</span>
                </div>
                <div class="info-item">
                    <span class="label">Domain</span>
                    <span class="value">{{ domain }}</span>
                </div>
                <div class="info-item">
                    <span class="label">External IP</span>
                    <span class="value">{{ external_ip }}</span>
                </div>
                <div class="info-item">
                    <span class="label">JWT Auth</span>
                    <span class="value">{{ jwt_enabled }}</span>
                </div>
                <div class="info-item">
                    <span class="label">LLM Provider</span>
                    <span class="value">{{ llm_provider }}</span>
                </div>
                <div class="info-item">
                    <span class="label">Python</span>
                    <span class="value">{{ python_version }}</span>
                </div>
            </div>
        </div>

        <div class="section">
            <h2><span>▣</span> API Endpoints</h2>
            <div class="endpoints">
                <div class="endpoint">
                    <span class="method method-get">GET</span>
                    <span class="path">/health</span>
                    <div class="desc">Health check</div>
                </div>
                <div class="endpoint">
                    <span class="method method-get">GET</span>
                    <span class="path">/status</span>
                    <div class="desc">Full system status</div>
                </div>
                <div class="endpoint">
                    <span class="method method-get">GET</span>
                    <span class="path">/api/prompts</span>
                    <div class="desc">List available prompts</div>
                </div>
                <div class="endpoint">
                    <span class="method method-post</span>
                    <span class="path">/api/run</span>
                    <div class="desc">Execute a prompt</div>
                </div>
                <div class="endpoint">
                    <span class="method method-get">GET</span>
                    <span class="path">/api/memory</span>
                    <div class="desc">Project memory</div>
                </div>
                <div class="endpoint">
                    <span class="method method-get">GET</span>
                    <span class="path">/api/tools</span>
                    <div class="desc">List MCP tools</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2><span>▣</span> Projects & Environment</h2>
            <div style="margin-bottom: 16px; display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
                <select id="projectSelect" style="padding: 8px 12px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; min-width: 200px;">
                    <option value="">Select a project...</option>
                </select>
                <button onclick="loadFromEnvFile()" style="padding: 8px 16px; background: #00d4ff; color: #000; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">Load .env</button>
                <span id="envSource" style="color: #666; font-size: 12px;"></span>
            </div>

            <div id="projectEnvSection" style="display: none;">
                <div style="display: flex; gap: 12px; margin-bottom: 16px;">
                    <input type="text" id="envKey" placeholder="KEY" style="flex: 1; padding: 8px 12px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px;">
                    <input type="text" id="envValue" placeholder="value" style="flex: 2; padding: 8px 12px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px;">
                    <button onclick="addEnvVar()" style="padding: 8px 16px; background: #10b981; color: #fff; border: none; border-radius: 6px; cursor: pointer;">Add</button>
                </div>
                <div id="envVarsList" style="display: grid; gap: 8px;"></div>
            </div>

            <div id="projectActions" style="display: none; margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.1);">
                <input type="text" id="runCommand" placeholder="Command to run (e.g., npm run dev)" style="width: 100%; padding: 10px 12px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; margin-bottom: 12px; font-family: monospace;">
                <button onclick="runProjectCommand()" style="padding: 10px 20px; background: #3b82f6; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">Run Command</button>
                <div id="runOutput" style="margin-top: 12px; padding: 12px; background: #0d1117; border-radius: 8px; font-family: monospace; font-size: 12px; white-space: pre-wrap; display: none;"></div>
            </div>
        </div>

        <div class="section">
            <h2><span>🔑</span> API Keys</h2>
            <div style="margin-bottom: 16px;">
                <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
                    <input type="text" id="newKeyProject" placeholder="Project ID" style="flex: 1; padding: 8px 12px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px;">
                    <input type="text" id="newKeyPermissions" placeholder="permissions (default: read_prompts,run_prompt)" style="flex: 2; padding: 8px 12px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px;">
                    <button onclick="createApiKey()" style="padding: 8px 16px; background: #10b981; color: #fff; border: none; border-radius: 6px; cursor: pointer;">Generate Key</button>
                </div>
                <div id="newKeyResult" style="display: none; padding: 12px; background: #0d1117; border-radius: 8px; margin-bottom: 12px; font-family: monospace; font-size: 12px; word-break: break-all;"></div>
                <div id="apiKeysList" style="display: grid; gap: 8px;"></div>
            </div>
        </div>

        <div class="section">
            <h2><span>☁️</span> LLM Provider</h2>
            <div style="margin-bottom: 16px;">
                <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
                    <select id="providerSelect" style="flex: 1; padding: 10px 12px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; min-width: 200px;">
                        <option value="">Loading providers...</option>
                    </select>
                    <button onclick="selectProvider()" style="padding: 10px 20px; background: #10b981; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">Set Provider</button>
                </div>
                <div id="providerStatus" style="padding: 12px; background: rgba(0,0,0,0.3); border-radius: 6px; font-size: 13px;"></div>
            </div>
        </div>

        <div class="section">
            <h2><span>📊</span> Token Usage</h2>
            <div style="margin-bottom: 16px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 16px;">
                    <div style="padding: 12px; background: rgba(0,0,0,0.3); border-radius: 6px; text-align: center;">
                        <div style="color: #666; font-size: 11px; margin-bottom: 4px;">INPUT TOKENS</div>
                        <div style="color: #00d4ff; font-size: 18px; font-weight: 500;" id="inputTokens">-</div>
                    </div>
                    <div style="padding: 12px; background: rgba(0,0,0,0.3); border-radius: 6px; text-align: center;">
                        <div style="color: #666; font-size: 11px; margin-bottom: 4px;">OUTPUT TOKENS</div>
                        <div style="color: #10b981; font-size: 18px; font-weight: 500;" id="outputTokens">-</div>
                    </div>
                    <div style="padding: 12px; background: rgba(0,0,0,0.3); border-radius: 6px; text-align: center;">
                        <div style="color: #666; font-size: 11px; margin-bottom: 4px;">REQUESTS</div>
                        <div style="color: #f59e0b; font-size: 18px; font-weight: 500;" id="requestCount">-</div>
                    </div>
                </div>
                <div style="padding: 12px; background: rgba(0,0,0,0.3); border-radius: 6px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #666; font-size: 12px;">Usage: <span id="usagePercent">0%</span> of <span id="limitTokens">1,000,000</span></span>
                        <span style="color: #10b981; font-size: 12px;">$<span id="costUsd">0.00</span></span>
                    </div>
                    <div style="height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                        <div id="usageBar" style="height: 100%; width: 0%; background: linear-gradient(90deg, #10b981, #f59e0b); border-radius: 4px; transition: width 0.3s;"></div>
                    </div>
                </div>
                <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                    <input type="number" id="monthlyLimit" placeholder="Monthly limit (tokens)" style="flex: 1; padding: 8px 12px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px;">
                    <input type="number" id="alertPercent" placeholder="Alert %" value="80" style="width: 80px; padding: 8px 12px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px;">
                    <input type="number" id="blockPercent" placeholder="Block %" value="100" style="width: 80px; padding: 8px 12px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px;">
                    <button onclick="setTokenLimits()" style="padding: 8px 16px; background: #3b82f6; color: #fff; border: none; border-radius: 6px; cursor: pointer;">Set Limits</button>
                </div>
            </div>
        </div>

        <div class="section">
            <h2><span>▣</span> Recent Logs</h2>
            <div class="logs" id="logs">
                <div class="log-entry"><span class="time">--:--:--</span><span class="msg">Loading logs...</span></div>
            </div>
        </div>
    </div>

    <div class="footer">
        p9i AI Prompt System | <a href="/docs" style="color: #00d4ff;">API Docs</a>
    </div>

    <script>
        try {
        let startTime = Date.now();
        let requestCount = 0;
        let currentUser = null;

        // Auth functions
        function checkAuth() {
            const token = localStorage.getItem('p9i_token');
            const user = localStorage.getItem('p9i_user');
            if (token && user) {
                currentUser = JSON.parse(user);
                showDashboard();
            } else {
                showLogin();
            }
        }

        function showLogin() {
            document.getElementById('authOverlay').classList.remove('hidden');
            document.getElementById('authError').textContent = '';
        }

        function hideLogin() {
            document.getElementById('authOverlay').classList.add('hidden');
        }

        function showDashboard() {
            hideLogin();
            document.getElementById('userSection').style.display = 'flex';
            document.getElementById('loginBtn').style.display = 'none';
            document.getElementById('userAvatar').textContent = currentUser.username.charAt(0).toUpperCase();
            document.getElementById('userName').textContent = currentUser.username;
            // Load API keys, providers, and usage
            loadApiKeys();
            loadProviders();
            loadUsage();
        }

        function doLogin() {
            const username = document.getElementById('authUsername').value.trim();
            const password = document.getElementById('authPassword').value;

            if (!username || !password) {
                document.getElementById('authError').textContent = 'Please enter username and password';
                return;
            }

            fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            })
            .then(r => r.json())
            .then(data => {
                if (data.token) {
                    localStorage.setItem('p9i_token', data.token);
                    localStorage.setItem('p9i_user', JSON.stringify({username, role: data.role}));
                    currentUser = {username, role: data.role};
                    showDashboard();
                    loadProjectsList();
                } else {
                    document.getElementById('authError').textContent = data.error || 'Invalid credentials';
                }
            })
            .catch(err => {
                document.getElementById('authError').textContent = 'Connection error';
            });
        }

        function doLogout() {
            localStorage.removeItem('p9i_token');
            localStorage.removeItem('p9i_user');
            currentUser = null;
            document.getElementById('userSection').style.display = 'none';
            document.getElementById('loginBtn').style.display = 'block';
            showLogin();
        }

        // Auth check on load
        checkAuth();

        function updateStats() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    // Uptime
                    const uptime = Math.floor((Date.now() - startTime) / 1000);
                    const hours = Math.floor(uptime / 3600);
                    const mins = Math.floor((uptime % 3600) / 60);
                    const secs = uptime % 60;
                    document.getElementById('uptime').textContent =
                        hours + 'h ' + mins + 'm ' + secs + 's';

                    // CPU & Memory
                    document.getElementById('cpu').textContent = data.cpu + '%';
                    document.getElementById('memory').textContent = data.memory + '%';

                    // Requests
                    requestCount = data.requests || 0;
                    document.getElementById('requests').textContent = requestCount;
                })
                .catch(() => {});
        }

        // API Keys Management
        function loadApiKeys() {
            fetch('/api/keys')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('apiKeysList');
                    if (!container) return;
                    container.innerHTML = '';
                    data.keys.forEach(key => {
                        const div = document.createElement('div');
                        div.style.cssText = 'padding: 12px; background: rgba(0,0,0,0.3); border-radius: 6px; display: flex; justify-content: space-between; align-items: center;';
                        div.innerHTML = `
                            <div>
                                <span style="color: #00d4ff; font-weight: 500;">${key.project_id}</span>
                                <span style="color: #666; margin-left: 8px;">${key.key_prefix}</span>
                                <span style="color: #666; margin-left: 8px; font-size: 11px;">${key.permissions.join(', ')}</span>
                                ${key.is_main ? '<span style="color: #f59e0b; margin-left: 8px; font-size: 11px;">MAIN</span>' : ''}
                            </div>
                            ${!key.is_main ? '<button onclick="deleteApiKey(\'' + key.key_id + '\')" style="padding: 4px 12px; background: #ef4444; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">Delete</button>' : ''}
                        `;
                        container.appendChild(div);
                    });
                })
                .catch(() => {});
        }

        function createApiKey() {
            const projectId = document.getElementById('newKeyProject').value || 'default';
            const permissions = document.getElementById('newKeyPermissions').value || 'read_prompts,run_prompt';

            fetch('/api/keys', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({project_id: projectId, permissions: permissions})
            })
            .then(r => r.json())
            .then(data => {
                const resultDiv = document.getElementById('newKeyResult');
                resultDiv.style.display = 'block';
                if (data.api_key) {
                    resultDiv.innerHTML = '<span style="color: #10b981;">API Key:</span> ' + data.api_key + '<br><span style="color: #f59e0b;">Warning: ' + data.warning + '</span>';
                } else {
                    resultDiv.innerHTML = '<span style="color: #ef4444;">Error: ' + (data.error || 'Unknown error') + '</span>';
                }
                loadApiKeys();
            });
        }

        function deleteApiKey(keyId) {
            if (!confirm('Delete this API key?')) return;
            fetch('/api/keys/' + keyId, {method: 'DELETE'})
                .then(r => r.json())
                .then(data => {
                    loadApiKeys();
                });
        }

        // LLM Providers Management
        function loadProviders() {
            // Load provider selection API
            fetch('/api/provider')
                .then(r => r.json())
                .then(data => {
                    const select = document.getElementById('providerSelect');
                    if (!select) return;
                    select.innerHTML = '';

                    // Add available providers
                    if (data.available) {
                        data.available.forEach(p => {
                            const opt = document.createElement('option');
                            opt.value = p.id;
                            opt.textContent = p.name + (p.has_key ? ' ✓' : ' ✗');
                            opt.disabled = !p.has_key;
                            select.appendChild(opt);
                        });
                    }

                    // Set current selection
                    if (data.selected) {
                        select.value = data.selected;
                    }

                    // Update status
                    const status = document.getElementById('providerStatus');
                    if (status && data.provider_info) {
                        status.innerHTML = `
                            <span style="color: #10b981;">Current: ${data.provider_info.name}</span>
                            <span style="color: #666; margin-left: 12px;">Model: ${data.model || data.provider_info.model}</span>
                            ${!data.provider_info.has_key ? '<span style="color: #ef4444; margin-left: 12px;">⚠️ No API key</span>' : ''}
                        `;
                    }
                })
                .catch(() => {});
        }

        function selectProvider() {
            const select = document.getElementById('providerSelect');
            const providerId = select.value;
            if (!providerId) {
                alert('Please select a provider');
                return;
            }

            fetch('/api/provider', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({provider: providerId})
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Provider set to: ' + data.provider);
                    loadProviders();
                } else {
                    alert('Error: ' + (data.error || 'Failed to set provider'));
                }
            });
        }

        // Token Usage Tracking
        function loadUsage() {
            fetch('/api/usage')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('inputTokens').textContent = (data.input_tokens || 0).toLocaleString();
                    document.getElementById('outputTokens').textContent = (data.output_tokens || 0).toLocaleString();
                    document.getElementById('requestCount').textContent = (data.requests || 0).toLocaleString();

                    const limit = data.limits ? data.limits.monthly_limit : 1000000;
                    document.getElementById('limitTokens').textContent = limit.toLocaleString();

                    const percent = data.usage_percent || 0;
                    document.getElementById('usagePercent').textContent = percent + '%';
                    document.getElementById('usageBar').style.width = Math.min(percent, 100) + '%';

                    // Color based on percentage
                    const bar = document.getElementById('usageBar');
                    if (percent >= 90) bar.style.background = '#ef4444';
                    else if (percent >= 75) bar.style.background = '#f59e0b';
                    else bar.style.background = 'linear-gradient(90deg, #10b981, #00d4ff)';

                    document.getElementById('costUsd').textContent = (data.cost_usd || 0).toFixed(2);

                    // Set limit inputs
                    if (data.limits) {
                        document.getElementById('monthlyLimit').value = data.limits.monthly_limit;
                        document.getElementById('alertPercent').value = data.limits.alert_percent;
                        document.getElementById('blockPercent').value = data.limits.block_percent;
                    }
                })
                .catch(() => {});
        }

        function setTokenLimits() {
            const monthlyLimit = parseInt(document.getElementById('monthlyLimit').value) || 1000000;
            const alertPercent = parseInt(document.getElementById('alertPercent').value) || 80;
            const blockPercent = parseInt(document.getElementById('blockPercent').value) || 100;

            fetch('/api/usage/limits', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    monthly_limit: monthlyLimit,
                    alert_percent: alertPercent,
                    block_percent: blockPercent
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Token limits updated: ' + monthlyLimit.toLocaleString() + ' tokens/month');
                    loadUsage();
                } else {
                    alert('Error: ' + (data.error || 'Failed to set limits'));
                }
            });
        }

        // Project Environment Management
        let currentProjectId = null;
        let currentEnvVars = {};

        function loadProjectsList() {
            console.log('Loading projects...');
            fetch('/api/projects')
                .then(r => {
                    console.log('Response status:', r.status);
                    return r.json();
                })
                .then(data => {
                    console.log('Projects data:', data);
                    const select = document.getElementById('projectSelect');
                    select.innerHTML = '<option value="">Select a project...</option>';
                    if (data.projects && data.projects.length > 0) {
                        data.projects.forEach(p => {
                            const opt = document.createElement('option');
                            opt.value = p.id;
                            opt.textContent = p.id + (p.has_custom_env ? ' ✓' : '');
                            select.appendChild(opt);
                        });
                        console.log('Loaded', data.projects.length, 'projects');
                    } else {
                        console.log('No projects found');
                    }
                })
                .catch(err => {
                    console.error('Error loading projects:', err);
                });
        }

        function loadProjectEnv() {
            const projectId = document.getElementById('projectSelect').value;
            if (!projectId) return;

            currentProjectId = projectId;
            fetch('/api/projects/' + projectId + '/env')
                .then(r => r.json())
                .then(data => {
                    currentEnvVars = data.env || {};
                    renderEnvVars();
                    document.getElementById('projectEnvSection').style.display = 'block';
                    document.getElementById('projectActions').style.display = 'block';
                })
                .catch(() => {});
        }

        function renderEnvVars() {
            const container = document.getElementById('envVarsList');
            container.innerHTML = '';

            Object.entries(currentEnvVars).forEach(([key, value]) => {
                const div = document.createElement('div');
                div.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(0,0,0,0.2); border-radius: 6px;';

                const keySpan = document.createElement('span');
                keySpan.style.color = '#00d4ff';
                keySpan.style.fontFamily = 'monospace';
                keySpan.textContent = key;

                const valueSpan = document.createElement('span');
                valueSpan.style.color = '#888';
                valueSpan.style.fontFamily = 'monospace';
                valueSpan.style.flex = '1';
                valueSpan.style.margin = '0 12px';
                valueSpan.style.overflow = 'hidden';
                valueSpan.style.textOverflow = 'ellipsis';
                valueSpan.textContent = value;

                const delBtn = document.createElement('button');
                delBtn.textContent = 'Delete';
                delBtn.style.padding = '4px 8px';
                delBtn.style.background = '#ef4444';
                delBtn.style.color = '#fff';
                delBtn.style.border = 'none';
                delBtn.style.borderRadius = '4px';
                delBtn.style.cursor = 'pointer';
                delBtn.style.fontSize = '12px';
                delBtn.onclick = () => deleteEnvVar(key);

                div.appendChild(keySpan);
                div.appendChild(valueSpan);
                div.appendChild(delBtn);
                container.appendChild(div);
            });

            if (Object.keys(currentEnvVars).length === 0) {
                container.innerHTML = '<div style="color: #666; text-align: center; padding: 20px;">No custom env vars. Add some above!</div>';
            }
        }

        function addEnvVar() {
            const key = document.getElementById('envKey').value.trim();
            const value = document.getElementById('envValue').value;

            if (!key) return;

            currentEnvVars[key] = value;
            document.getElementById('envKey').value = '';
            document.getElementById('envValue').value = '';

            // Save to server
            fetch('/api/projects/' + currentProjectId + '/env', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(currentEnvVars)
            }).then(r => r.json()).then(data => {
                renderEnvVars();
            });
        }

        function deleteEnvVar(key) {
            if (!confirm('Delete ' + key + '?')) return;

            fetch('/api/projects/' + currentProjectId + '/env/' + key, {
                method: 'DELETE'
            }).then(r => r.json()).then(data => {
                delete currentEnvVars[key];
                renderEnvVars();
            });
        }

        function runProjectCommand() {
            const command = document.getElementById('runCommand').value;
            if (!command || !currentProjectId) return;

            const output = document.getElementById('runOutput');
            output.style.display = 'block';
            output.textContent = 'Running...';

            fetch('/api/projects/' + currentProjectId + '/run', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: command})
            }).then(r => r.json()).then(data => {
                if (data.stdout) {
                    output.textContent = data.stdout + (data.stderr ? ' -- STDERR: ' + data.stderr : '');
                } else if (data.error) {
                    output.textContent = 'Error: ' + data.error;
                } else {
                    output.textContent = JSON.stringify(data, null, 2);
                }
            });
        }

        function loadTemplate() {
            const template = document.getElementById('templateSelect').value;
            if (!template) {
                alert('Please select a template');
                return;
            }

            fetch('/api/templates/' + template)
                .then(r => r.json())
                .then(data => {
                    if (data.env) {
                        currentEnvVars = data.env;
                        // Show project name prompt if no project selected
                        if (!currentProjectId) {
                            currentProjectId = prompt('Enter project name to save template:');
                            if (!currentProjectId) return;
                        }
                        renderEnvVars();
                        document.getElementById('projectEnvSection').style.display = 'block';
                        document.getElementById('projectActions').style.display = 'block';

                        // Auto-save to server
                        fetch('/api/projects/' + currentProjectId + '/env', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(currentEnvVars)
                        }).then(r => r.json()).then(() => {
                            alert('Template "' + data.name + '" loaded and saved!');
                            loadProjectsList();
                        });
                    }
                });
        }

        function loadFromEnvFile() {
            const projectId = document.getElementById('projectSelect').value;
            if (!projectId) {
                alert('Select a project first');
                return;
            }

            currentProjectId = projectId;
            fetch('/api/projects/' + projectId + '/env-file')
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
                    if (data.env && Object.keys(data.env).length > 0) {
                        currentEnvVars = data.env;
                        renderEnvVars();
                        document.getElementById('projectEnvSection').style.display = 'block';
                        document.getElementById('projectActions').style.display = 'block';
                        document.getElementById('envSource').textContent = 'Loaded from: ' + (data.source_file || '.env');

                        // Auto-save to server
                        fetch('/api/projects/' + projectId + '/env', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(currentEnvVars)
                        }).then(r => r.json()).then(() => {
                            loadProjectsList();
                        });
                    } else {
                        alert('No .env or .env.example found');
                    }
                });
        }

        // Load projects on page load
        loadProjectsList();

        function updateLogs() {
            fetch('/api/logs')
                .then(r => r.json())
                .then(logs => {
                    const container = document.getElementById('logs');
                    if (!logs || logs.length === 0) {
                        container.innerHTML = '<div class="log-entry"><span class="time">--:--:--</span><span class="msg">No logs yet</span></div>';
                    } else {
                        container.innerHTML = logs.slice(0, 20).map(log =>
                            '<div class="log-entry"><span class="time">' + log.time + '</span><span class="msg">' + log.msg + '</span></div>'
                        ).join('');
                    }
                })
                .catch(err => {
                    console.error('Logs fetch error:', err);
                });
        }

        updateStats();
        updateLogs();
        setInterval(updateStats, 2000);
        setInterval(updateLogs, 5000);
        } catch(e) {
            console.error('Script error:', e);
        }
    </script>
</body>
</html>
"""


# Global state
_start_time = datetime.datetime.now()
_request_count = 0
_logs = []


def add_log(msg: str):
    """Add a log entry"""
    global _logs
    _logs.append({
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "msg": msg
    })
    # Keep only last 100 logs
    _logs = _logs[-100:]


@app.on_event("startup")
async def startup():
    add_log("p9i Web UI started")
    logger.info("p9i Dashboard started on port 8080")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    html = DASHBOARD_HTML
    html = html.replace("{{ transport }}", os.getenv("MCP_TRANSPORT", "streamable-http"))
    html = html.replace("{{ port }}", os.getenv("SERVER_PORT", "8000"))
    html = html.replace("{{ domain }}", os.getenv("DOMAIN", "localhost"))
    html = html.replace("{{ external_ip }}", os.getenv("EXTERNAL_IP", "127.0.0.1"))
    html = html.replace("{{ jwt_enabled }}", os.getenv("JWT_ENABLED", "false"))
    html = html.replace("{{ llm_provider }}", os.getenv("LLM_PROVIDER", "auto"))
    html = html.replace("{{ python_version }}", f"{os.sys.version_info.major}.{os.sys.version_info.minor}")
    return html


# ============================================================================
# Authentication
# ============================================================================

# Auth credentials from environment (comma-separated: user:pass,user2:pass2)
_AUTH_USERS = {}
_auth_config = os.getenv("WEBUI_USERS", "admin:p9i-admin")
for user_spec in _auth_config.split(","):
    if ":" in user_spec:
        u, p = user_spec.split(":", 1)
        _AUTH_USERS[u] = {"password": p, "role": "admin" if u == "admin" else "user"}


def _generate_simple_token(username: str, role: str) -> str:
    """Generate simple token (for demo - in production use proper JWT)"""
    import base64
    import json
    payload = {
        "sub": username,
        "role": role,
        "exp": int(datetime.datetime.now().timestamp()) + 86400
    }
    token = base64.b64encode(json.dumps(payload).encode()).decode()
    return f"p9i_{username}_{token}"


@app.post("/api/login")
async def login(request: Request):
    """Login endpoint"""
    data = await request.json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return {"error": "Username and password required"}

    # Check credentials
    user = _AUTH_USERS.get(username)
    if not user or user["password"] != password:
        return {"error": "Invalid credentials"}

    token = _generate_simple_token(username, user["role"])
    return {
        "token": token,
        "username": username,
        "role": user["role"]
    }


@app.post("/api/logout")
async def logout():
    """Logout endpoint"""
    return {"status": "success"}


@app.get("/api/auth-status")
async def auth_status():
    """Check auth status"""
    return {"authenticated": True}


@app.get("/health")
async def health():
    """Health check endpoint"""
    global _request_count
    _request_count += 1
    return {
        "status": "healthy",
        "service": "p9i",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    }


@app.get("/status")
async def status():
    """Full system status"""
    global _request_count
    _request_count += 1

    # Get system info
    try:
        if psutil:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
        else:
            cpu_percent = 0
            memory = type('obj', (object,), {'percent': 0, 'used': 0, 'total': 0})()
    except Exception:
        cpu_percent = 0
        memory = type('obj', (object,), {'percent': 0, 'used': 0, 'total': 0})()

    uptime = datetime.datetime.now() - _start_time

    return {
        "status": "running",
        "uptime_seconds": int(uptime.total_seconds()),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_mb": memory.used // (1024 * 1024),
            "memory_total_mb": memory.total // (1024 * 1024)
        },
        "config": {
            "transport": os.getenv("MCP_TRANSPORT", "streamable-http"),
            "port": os.getenv("SERVER_PORT", "8000"),
            "jwt_enabled": os.getenv("JWT_ENABLED", "false"),
            "llm_provider": os.getenv("LLM_PROVIDER", "auto"),
            "domain": os.getenv("DOMAIN", ""),
            "external_ip": os.getenv("EXTERNAL_IP", ""),
            "p9i_api_key_set": bool(os.getenv("P9I_API_KEY"))
        },
        "requests": _request_count
    }


@app.get("/api/stats")
async def stats():
    """JSON stats for dashboard"""
    global _request_count
    try:
        if psutil:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
        else:
            cpu = 0
            mem = type('obj', (object,), {'percent': 0})()
    except Exception:
        cpu = 0
        mem = type('obj', (object,), {'percent': 0})()

    return {
        "cpu": cpu,
        "memory": mem.percent,
        "requests": _request_count
    }


@app.get("/api/logs")
async def get_logs():
    """Get recent logs"""
    global _logs
    return _logs[-20:]


# ============================================================================
# API Key Management
# ============================================================================

# In-memory store for API keys (for web UI session)
_web_api_keys = {}


@app.get("/api/keys")
async def list_api_keys():
    """List API keys (without secrets)"""
    global _web_api_keys
    # Combine with P9I_API_KEY if set
    p9i_key = os.getenv("P9I_API_KEY", "")
    keys = list(_web_api_keys.values())
    if p9i_key:
        keys.append({
            "key_id": "p9i_main",
            "project_id": "p9i",
            "key_prefix": p9i_key[:12] + "...",
            "permissions": ["*"],
            "rate_limit": 1000,
            "is_main": True
        })
    return {"keys": keys, "count": len(keys)}


@app.post("/api/keys")
async def create_api_key(request: Request):
    """Create a new API key"""
    global _web_api_keys, _request_count
    _request_count += 1

    data = await request.json()
    project_id = data.get("project_id", "default")
    permissions = data.get("permissions", "read_prompts,run_prompt")
    rate_limit = data.get("rate_limit", 100)

    # Generate secure key
    key_bytes = secrets.token_bytes(32)
    api_key = f"sk-{hashlib.sha256(key_bytes).hexdigest()[:48]}"

    key_id = f"key_{len(_web_api_keys) + 1}"
    _web_api_keys[key_id] = {
        "key_id": key_id,
        "api_key": api_key,
        "project_id": project_id,
        "key_prefix": api_key[:12] + "...",
        "permissions": permissions.split(","),
        "rate_limit": rate_limit,
        "is_main": False
    }

    add_log(f"Created API key for project: {project_id}")
    return {
        "status": "success",
        "api_key": api_key,
        "warning": "Store this key securely - it cannot be retrieved again!"
    }


@app.delete("/api/keys/{key_id}")
async def delete_api_key(key_id: str):
    """Delete an API key"""
    global _web_api_keys

    if key_id == "p9i_main":
        return {"status": "error", "error": "Cannot delete main P9I_API_KEY"}

    if key_id in _web_api_keys:
        del _web_api_keys[key_id]
        add_log(f"Deleted API key: {key_id}")
        return {"status": "success"}

    return {"status": "error", "error": "Key not found"}


# ============================================================================
# LLM Provider Keys Management
# ============================================================================

LLM_PROVIDERS = [
    {"id": "minimax", "name": "MiniMax", "env_key": "MINIMAX_API_KEY", "enabled": True},
    {"id": "zai", "name": "Z.ai (GLM)", "env_key": "ZAI_API_KEY", "enabled": True},
    {"id": "deepseek", "name": "DeepSeek", "env_key": "DEEPSEEK_API_KEY", "enabled": True},
    {"id": "openrouter", "name": "OpenRouter", "env_key": "OPENROUTER_API_KEY", "enabled": True},
    {"id": "anthropic", "name": "Anthropic", "env_key": "ANTHROPIC_API_KEY", "enabled": False},
    {"id": "aihubmix", "name": "AIHubMix", "env_key": "AIHUBMIX_API_KEY", "enabled": False},
    {"id": "context7", "name": "Context7", "env_key": "CONTEXT7_API_KEY", "enabled": False},
    {"id": "github", "name": "GitHub", "env_key": "GITHUB_TOKEN", "enabled": False},
    {"id": "figma", "name": "Figma", "env_key": "FIGMA_TOKEN", "enabled": False},
]


@app.get("/api/providers")
async def list_providers():
    """List LLM providers and their status"""
    providers = []
    for p in LLM_PROVIDERS:
        key = os.getenv(p["env_key"], "")
        enabled = os.getenv(p["env_key"] + "_ENABLED", "true").lower() == "true"
        providers.append({
            "id": p["id"],
            "name": p["name"],
            "env_key": p["env_key"],
            "has_key": bool(key),
            "key_preview": key[:8] + "..." if key else "",
            "enabled": enabled
        })
    return {"providers": providers, "count": len(providers)}


@app.post("/api/providers/{provider_id}")
async def update_provider_key(provider_id: str, request: Request):
    """Update provider API key"""
    global _request_count
    _request_count += 1

    data = await request.json()
    api_key = data.get("api_key", "").strip()

    # Find provider
    provider = next((p for p in LLM_PROVIDERS if p["id"] == provider_id), None)
    if not provider:
        return {"status": "error", "error": "Provider not found"}

    # Note: In production, this would need to persist to .env or database
    # For now, we return instructions
    add_log(f"Provider key update requested: {provider_id}")
    return {
        "status": "info",
        "message": f"To update {provider['name']} API key, edit the .env file",
        "env_key": provider["env_key"],
        "env_value": api_key if api_key else "[YOUR_API_KEY]"
    }


@app.get("/api/providers/{provider_id}/test")
async def test_provider(provider_id: str):
    """Test provider API key"""
    global _request_count
    _request_count += 1

    provider = next((p for p in LLM_PROVIDERS if p["id"] == provider_id), None)
    if not provider:
        return {"status": "error", "error": "Provider not found"}

    api_key = os.getenv(provider["env_key"], "")
    if not api_key:
        return {"status": "error", "error": f"{provider['name']} API key not configured"}

    # Simple test - just check if key looks valid
    if len(api_key) < 10:
        return {"status": "error", "error": "API key seems too short"}

    add_log(f"Testing {provider['name']} provider")
    return {
        "status": "success",
        "provider": provider["name"],
        "message": "API key is configured (full test requires actual API call)"
    }


# ============================================================================
# Provider Selection (Dynamic)
# ============================================================================

@app.get("/api/provider")
async def get_provider_selection():
    """Get current provider selection for the project."""
    global _request_count
    _request_count += 1

    try:
        from src.services.provider_manager import get_provider_manager
        from src.storage.database import redis_client

        manager = get_provider_manager(redis_client)
        return await manager.get_current_selection()
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/provider")
async def set_provider(request: Request):
    """Set provider for the project."""
    global _request_count
    _request_count += 1

    data = await request.json()
    provider_id = data.get("provider")
    model = data.get("model")

    if not provider_id:
        return {"status": "error", "error": "provider is required"}

    try:
        from src.services.provider_manager import get_provider_manager
        from src.storage.database import redis_client

        manager = get_provider_manager(redis_client)
        result = await manager.set_provider("default", provider_id, model)
        add_log(f"Provider set to: {provider_id}")
        return result
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# Token Usage Tracking
# ============================================================================

@app.get("/api/usage")
async def get_token_usage():
    """Get token usage for the project."""
    global _request_count
    _request_count += 1

    try:
        from src.services.token_tracker import get_token_tracker
        from src.storage.database import redis_client

        tracker = get_token_tracker(redis_client)
        return await tracker.get_all_usage("default")
    except Exception as e:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "requests": 0,
            "cost_usd": 0,
            "usage_percent": 0,
            "error": str(e)
        }


@app.post("/api/usage/limits")
async def set_token_limits(request: Request):
    """Set token limits for the project."""
    global _request_count
    _request_count += 1

    data = await request.json()
    monthly_limit = int(data.get("monthly_limit", 1000000))
    alert_percent = int(data.get("alert_percent", 80))
    block_percent = int(data.get("block_percent", 100))

    try:
        from src.services.token_tracker import get_token_tracker
        from src.storage.database import redis_client

        tracker = get_token_tracker(redis_client)
        result = await tracker.set_limits("default", monthly_limit, alert_percent, block_percent)
        add_log(f"Token limits set: {monthly_limit} tokens/month")
        return {"status": "success", **result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/api/prompts")
async def list_prompts():
    """List available prompts"""
    global _request_count
    _request_count += 1
    add_log("List prompts requested")

    try:
        from src.storage.prompts_v2 import get_storage
        storage = get_storage()
        prompts = storage.list_prompts()
        return {"prompts": prompts, "count": len(prompts)}
    except Exception as e:
        add_log(f"Error listing prompts: {e}")
        return {"error": str(e), "prompts": [], "count": 0}


@app.get("/api/tools")
async def list_tools():
    """List MCP tools"""
    global _request_count
    _request_count += 1

    # Return basic tool info
    tools = [
        {"name": "ai_prompts", "description": "Universal router (use p9i)"},
        {"name": "run_prompt", "description": "Execute a prompt"},
        {"name": "run_prompt_chain", "description": "Execute prompt chain"},
        {"name": "list_prompts", "description": "List available prompts"},
        {"name": "get_project_memory", "description": "Get project memory"},
        {"name": "save_project_memory", "description": "Save project memory"},
        {"name": "generate_jwt_token", "description": "Generate JWT token"},
        {"name": "generate_tailwind", "description": "Generate TailwindCSS"},
        {"name": "generate_shadcn", "description": "Generate shadcn/ui"},
        {"name": "p9i_nl", "description": "Natural Language router"},
        {"name": "p9i", "description": "NL router (alias)"},
        {"name": "architect_design", "description": "Architecture design"},
        {"name": "developer_code", "description": "Code generation"},
        {"name": "reviewer_check", "description": "Code review"},
        # Browser automation tools
        {"name": "browser_navigate", "description": "Navigate to URL"},
        {"name": "browser_screenshot", "description": "Take screenshot"},
        {"name": "browser_click", "description": "Click element"},
        {"name": "browser_type", "description": "Type text into element"},
        {"name": "browser_evaluate", "description": "Execute JavaScript"},
        {"name": "browser_get_html", "description": "Get page HTML"},
        {"name": "browser_wait", "description": "Wait for element"},
        {"name": "browser_close", "description": "Close browser"},
        {"name": "browser_status", "description": "Browser status"},
    ]
    return {"tools": tools, "count": len(tools)}


@app.get("/api/memory")
async def get_memory():
    """Get project memory info"""
    global _request_count
    _request_count += 1

    memory_path = Path("/app/memory") if os.path.exists("/app/memory") else Path("./memory")

    if not memory_path.exists():
        return {"memory": [], "count": 0}

    memories = []
    try:
        for f in memory_path.glob("*.json"):
            memories.append({
                "project_id": f.stem,
                "path": str(f),
                "size_bytes": f.stat().st_size
            })
    except Exception as e:
        return {"error": str(e), "memory": [], "count": 0}

    return {"memory": memories, "count": len(memories)}


# ============================================================================
# Environment Templates
# ============================================================================

ENV_TEMPLATES = {
    "k8s": {
        "name": "K8s/DevOps",
        "env": {
            "K8S_PROVIDER": "aws",
            "NAMESPACE": "default",
            "ENVIRONMENT": "development",
            "STORAGE_PROVIDER": "s3",
            "CERT_ISSUER_TYPE": "letsencrypt",
            "LETSENCRYPT_EMAIL": "admin@example.com",
            "DOMAIN": "example.com",
            "EXTERNAL_IP": "",
            "REPLICAS": "2"
        }
    },
    "django": {
        "name": "Django/Python",
        "env": {
            "DEBUG": "true",
            "DJANGO_SECRET_KEY": "dev-secret-key-change-in-production",
            "ALLOWED_HOSTS": "localhost,127.0.0.1",
            "DATABASE_URL": "postgres://user:pass@localhost/dbname",
            "REDIS_URL": "redis://localhost:6379",
            "CELERY_BROKER_URL": "redis://localhost:6379",
            "CORS_ALLOWED_ORIGINS": "http://localhost:3000"
        }
    },
    "nextjs": {
        "name": "Next.js/React",
        "env": {
            "NEXT_PUBLIC_API_URL": "http://localhost:8000",
            "NEXT_PUBLIC_APP_URL": "http://localhost:3000",
            "DATABASE_URL": "postgres://user:pass@localhost/dbname",
            "NEXTAUTH_SECRET": "dev-secret-change-in-production",
            "NEXTAUTH_URL": "http://localhost:3000",
            "NODE_ENV": "development"
        }
    },
    "nodejs": {
        "name": "Node.js/Express",
        "env": {
            "NODE_ENV": "development",
            "PORT": "3000",
            "DATABASE_URL": "postgres://user:pass@localhost/dbname",
            "REDIS_URL": "redis://localhost:6379",
            "JWT_SECRET": "dev-secret-change-in-production",
            "API_KEY": "",
            "LOG_LEVEL": "debug"
        }
    },
    "codeshift": {
        "name": "CodeShift",
        "env": {
            "DOMAIN": "localhost",
            "ENVIRONMENT": "development",
            "K8S_PROVIDER": "local",
            "NAMESPACE": "codeshift",
            "STORAGE_PROVIDER": "local",
            "CERT_ISSUER_TYPE": "self-signed",
            "JWT_SECRET_KEY": "dev-secret-key-change-in-production"
        }
    }
}


@app.get("/api/templates")
async def list_templates():
    """List available env templates"""
    return {
        "templates": [
            {"id": k, "name": v["name"]} for k, v in ENV_TEMPLATES.items()
        ]
    }


@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific env template"""
    if template_id not in ENV_TEMPLATES:
        return {"error": "Template not found"}

    return ENV_TEMPLATES[template_id]


# ============================================================================
# Project Environment Variables Management
# ============================================================================

def _get_projects_dir() -> Path:
    """Get projects directory - uses /project mount or /home/worker"""
    if os.path.exists("/project"):
        return Path("/project")
    if os.path.exists("/home/worker"):
        return Path("/home/worker")
    return Path.cwd()


def _get_memory_dir() -> Path:
    """Get memory directory for storing env vars"""
    if os.path.exists("/app/memory"):
        return Path("/app/memory")
    return Path("./memory")


@app.get("/api/projects")
async def list_projects():
    """List available projects"""
    global _request_count
    _request_count += 1
    add_log("List projects requested")

    projects_dir = _get_projects_dir()
    memory_dir = _get_memory_dir()

    projects = []
    # Filter out non-project directories
    exclude_dirs = {'.git', '.cache', '.config', '.local', '.npm', '.venv', 'node_modules', '__pycache__', 'venv', 'env'}
    try:
        # Find all directories in projects folder
        if projects_dir.exists():
            for item in projects_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.') and item.name not in exclude_dirs:
                    # Check if project has env vars in memory
                    env_file = memory_dir / item.name / "env.json"
                    has_custom_env = env_file.exists()

                    projects.append({
                        "id": item.name,
                        "path": str(item),
                        "has_custom_env": has_custom_env
                    })
    except Exception as e:
        return {"error": str(e), "projects": [], "count": 0}

    return {"projects": projects, "count": len(projects)}


@app.get("/api/projects/{project_id}/env")
async def get_project_env(project_id: str):
    """Get environment variables for a project"""
    global _request_count
    _request_count += 1

    memory_dir = _get_memory_dir()
    env_file = memory_dir / project_id / "env.json"

    if not env_file.exists():
        return {"project_id": project_id, "env": {}, "count": 0}

    try:
        import json
        env_data = json.loads(env_file.read_text())
        return {
            "project_id": project_id,
            "env": env_data,
            "count": len(env_data)
        }
    except Exception as e:
        return {"error": str(e), "project_id": project_id, "env": {}, "count": 0}


@app.get("/api/projects/{project_id}/env-file")
async def get_project_env_file(project_id: str):
    """Read .env file from project directory"""
    global _request_count
    _request_count += 1
    add_log(f"Read .env file for project {project_id}")

    projects_dir = _get_projects_dir()
    project_path = projects_dir / project_id

    if not project_path.exists():
        return {"error": "Project not found", "project_id": project_id}

    # Try .env first, then .env.example
    env_file = project_path / ".env"
    if not env_file.exists():
        env_file = project_path / ".env.example"

    if not env_file.exists():
        return {"error": "No .env or .env.example file found", "project_id": project_id}

    try:
        env_data = {}
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                env_data[key.strip()] = value.strip()

        return {
            "project_id": project_id,
            "env": env_data,
            "source_file": env_file.name,
            "count": len(env_data)
        }
    except Exception as e:
        return {"error": str(e), "project_id": project_id, "env": {}}


@app.post("/api/projects/{project_id}/env")
async def save_project_env(project_id: str, request: dict = None):
    """Save environment variables for a project"""
    global _request_count
    _request_count += 1
    add_log(f"Save env for project {project_id}")

    if not request:
        return {"status": "error", "error": "No env data provided"}

    memory_dir = _get_memory_dir()
    project_dir = memory_dir / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    env_file = project_dir / "env.json"

    try:
        import json
        env_file.write_text(json.dumps(request, indent=2))
        return {
            "status": "success",
            "project_id": project_id,
            "env": request,
            "count": len(request)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.delete("/api/projects/{project_id}/env/{key}")
async def delete_project_env(project_id: str, key: str):
    """Delete an environment variable from a project"""
    global _request_count
    _request_count += 1
    add_log(f"Delete env {key} from project {project_id}")

    memory_dir = _get_memory_dir()
    env_file = memory_dir / project_id / "env.json"

    if not env_file.exists():
        return {"status": "error", "error": "No env file found"}

    try:
        import json
        env_data = json.loads(env_file.read_text())

        if key in env_data:
            del env_data[key]
            env_file.write_text(json.dumps(env_data, indent=2))
            return {"status": "success", "project_id": project_id, "key": key}
        else:
            return {"status": "error", "error": "Key not found"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/api/projects/{project_id}/run")
async def run_project_command(project_id: str, request: dict = None):
    """Run a command in a project with custom env vars"""
    global _request_count
    _request_count += 1

    if not request or "command" not in request:
        return {"status": "error", "error": "No command provided"}

    command = request["command"]
    projects_dir = _get_projects_dir()
    project_path = projects_dir / project_id

    if not project_path.exists():
        return {"status": "error", "error": "Project not found"}

    # Load custom env vars
    memory_dir = _get_memory_dir()
    env_file = memory_dir / project_id / "env.json"

    import subprocess
    import json

    env = os.environ.copy()
    if env_file.exists():
        try:
            custom_env = json.loads(env_file.read_text())
            env.update(custom_env)
            add_log(f"Running command in {project_id} with custom env")
        except Exception:
            pass

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(project_path),
            env=env,
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "status": "success",
            "project_id": project_id,
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
