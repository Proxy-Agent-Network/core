// pan_command_center/js/ui/dossier_ui.js

window.initDossierUI = function() {
    if (document.getElementById('side-dossier')) return;

    const panel = document.createElement('div');
    panel.id = 'side-dossier';
    panel.className = 'dossier-drawer hidden';
    document.body.appendChild(panel);
};

// Seeded hash for deterministic mock data (keeps stats consistent per ID)
function hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) hash = Math.imul(31, hash) + str.charCodeAt(i) | 0;
    return Math.abs(hash);
}

window.closeDossier = function() {
    const panel = document.getElementById('side-dossier');
    if (panel) panel.classList.add('hidden');
};

// ==========================================
// 🟢 HEALTHY AV DOSSIER
// ==========================================
window.openHealthyAVDossier = function(avId, lastErrorCode, lastErrorHoursAgo) {
    const panel = document.getElementById('side-dossier');
    if (!panel) return;

    const seed = hashString(avId);
    const soc = 15 + (seed % 85); 
    const uptime = (97 + ((seed % 30) / 10)).toFixed(2); 
    const calib = 85 + (seed % 15); 
    const swVer = `WaymoOS v4.${seed % 9}.${seed % 15}`;

    let socColor = soc < 20 ? '#F44336' : (soc < 50 ? '#FFEB3B' : '#4CAF50');
    let calibColor = calib < 90 ? '#FF9800' : '#4CAF50';
    let errName = window.capNames && window.capNames[lastErrorCode] ? window.capNames[lastErrorCode] : lastErrorCode;

    panel.innerHTML = `
        <div class="dossier-header">
            <h2>HEALTHY ASSET</h2>
            <button class="btn-dossier-close" onclick="window.closeDossier()">✖</button>
        </div>
        <div class="dossier-content">
            <div style="margin-bottom: 20px;">
                <div style="font-size: 18px; color: #fff; font-weight: bold;">${avId}</div>
                <div style="color: #4CAF50; font-size: 12px; font-weight: bold; margin-top: 4px;">IN SERVICE (AUTONOMOUS)</div>
            </div>
            <div class="dossier-section">
                <h3>CORE TELEMETRY</h3>
                <div class="dossier-grid">
                    <div class="dossier-stat"><span class="label">STATE OF CHARGE</span><span class="val" style="color:${socColor}">${soc}%</span></div>
                    <div class="dossier-stat"><span class="label">LIFETIME UPTIME</span><span class="val">${uptime}%</span></div>
                    <div class="dossier-stat"><span class="label">CALIBRATION</span><span class="val" style="color:${calibColor}">${calib}%</span></div>
                    <div class="dossier-stat"><span class="label">FIRMWARE</span><span class="val">${swVer}</span></div>
                </div>
            </div>
            <div class="dossier-section">
                <h3>LAST LOGGED FAULT</h3>
                <div class="dossier-list">
                    <div class="dossier-hist-item">
                        <div class="hist-time">${lastErrorHoursAgo} hours ago</div>
                        <div class="hist-err">${errName.toUpperCase()}</div>
                        <div class="hist-res">Resolved & Cleared</div>
                    </div>
                </div>
            </div>
            <button class="btn-dossier-action" onclick="window.showDemoAlert('Pinging AV Telemetry...', 2000)">RUN DIAGNOSTICS</button>
        </div>
    `;
    panel.classList.remove('hidden');
};

// ==========================================
// 🟠 FAULT / INCIDENT DOSSIER
// ==========================================
window.openFaultDossier = function(faultId) {
    const panel = document.getElementById('side-dossier');
    if (!panel) return;

    let f = window.simFaults[faultId];
    if (!f) return;

    const seed = hashString(faultId);
    const soc = 5 + (seed % 40); 
    const uptime = (92 + ((seed % 50) / 10)).toFixed(2); 
    const calib = 40 + (seed % 45); 

    let socColor = soc < 20 ? '#F44336' : '#FFEB3B';
    let calibColor = calib < 90 ? '#FF9800' : '#4CAF50';
    
    let isAssigned = f.status === "ASSIGNED";
    let isResolved = f.status === "RESOLVED";
    let statusText = isResolved ? "MISSION RESOLVED" : (isAssigned ? "MISSION IN PROGRESS" : "UNASSIGNED FAULT");
    let statusColor = isResolved ? "#555" : (isAssigned ? "#FF9800" : "#00BCD4");

    let actionsHtml = '';
    let agentText = '';

    if (isResolved) {
        actionsHtml = `<button class="btn-dossier-action" style="border-color: #E040FB; color: #E040FB;" onclick="window.loadReplay(null, '${f.id}')">⏪ REWIND INCIDENT</button>`;
    } else if (isAssigned) {
        let shortAgent = f.assignedAgent ? f.assignedAgent.replace('SIM-VANGUARD-', 'VAN-') : 'Unknown';
        agentText = `<div style="margin-top: 8px; font-size: 12px; color: #ccc;">Assigned Agent: <strong style="color: #fff;">${shortAgent}</strong></div>`;
        actionsHtml = `
            <button class="btn-dossier-action" style="border-color: #F44336; color: #F44336; margin-bottom: 10px;" onclick="window.openCancelModal('${f.id}')">CANCEL DISPATCH</button>
            <button class="btn-dossier-action" style="border-color: #E040FB; color: #E040FB;" onclick="window.loadReplay(null, '${f.id}')">⏪ REWIND INCIDENT</button>
        `;
    } else {
        actionsHtml = `
            <button class="btn-dossier-action" style="background: #00BCD4; color: #000; margin-bottom: 10px;" onclick="window.openDispatchModal('${f.id}')">QUICK DEPLOY AGENT</button>
            <button class="btn-dossier-action" style="border-color: #E040FB; color: #E040FB;" onclick="window.loadReplay(null, '${f.id}')">⏪ REWIND INCIDENT</button>
        `;
    }

    panel.innerHTML = `
        <div class="dossier-header">
            <h2 style="color:${statusColor}">${statusText}</h2>
            <button class="btn-dossier-close" onclick="window.closeDossier()">✖</button>
        </div>
        <div class="dossier-content">
            <div style="margin-bottom: 20px;">
                <div style="font-size: 18px; color: #fff; font-weight: bold;">${faultId}</div>
                <div style="color: #FF9800; font-size: 13px; font-weight: bold; margin-top: 4px;">ERR: ${window.capNames[f.errorCode] ? window.capNames[f.errorCode].toUpperCase() : f.errorCode}</div>
                ${agentText}
            </div>
            <div class="dossier-section">
                <h3>ASSET VITALS</h3>
                <div class="dossier-grid">
                    <div class="dossier-stat"><span class="label">STATE OF CHARGE</span><span class="val" style="color:${socColor}">${soc}%</span></div>
                    <div class="dossier-stat"><span class="label">LIFETIME UPTIME</span><span class="val">${uptime}%</span></div>
                    <div class="dossier-stat"><span class="label">CALIBRATION</span><span class="val" style="color:${calibColor}">${calib}%</span></div>
                </div>
            </div>
            <div style="margin-top: 20px;">
                ${actionsHtml}
            </div>
        </div>
    `;
    panel.classList.remove('hidden');
};

// ==========================================
// 🔵 FIELD AGENT DOSSIER
// ==========================================
window.openAgentDossier = function(agentId) {
    const panel = document.getElementById('side-dossier');
    if (!panel) return;

    let a = window.allAgents[agentId] || window.simAgents[agentId];
    if (!a || !a.status) return;

    const seed = hashString(agentId);
    
    // Agent Metrics
    const rep = (4.6 + ((seed % 40) / 100)).toFixed(1); 
    const compRate = 92 + (seed % 8); 
    const avgResp = (3 + (seed % 6)) + "m " + (seed % 60) + "s";
    const totalMissions = 150 + (seed % 300);

    const currentStatus = a.status.status;
    let statusColor = "#F44336"; 
    let displayStatus = "ONLINE";

    if (currentStatus === "ONLINE") {
        statusColor = a.status.patrolMode === "FOOT" ? "#00BCD4" : "#4CAF50"; 
        displayStatus = "ONLINE (READY)";
    } else if (currentStatus === "BUSY_ON_WAY") {
        statusColor = "#FF9800"; displayStatus = "BUSY - EN ROUTE";
    } else if (currentStatus === "BUSY_ON_SITE") {
        statusColor = "#FFEB3B"; displayStatus = "BUSY - ON SCENE";
    }

    let humanCaps = a.resolvedCaps ? a.resolvedCaps.map(c => window.capNames[c] || c) : [];
    let capsHtml = humanCaps.map(c => `<span style="background:#222;color:#ccc;padding:4px 8px;margin:3px;border-radius:4px;font-size:11px;border:1px solid #444;">${c}</span>`).join('');

    // Agent History Log
    const capKeys = Object.keys(window.capNames || {});
    let historyHtml = '';
    for (let i = 1; i <= 3; i++) {
        let rErr = capKeys[(seed + i * 3) % capKeys.length];
        let errName = window.capNames && window.capNames[rErr] ? window.capNames[rErr] : rErr;
        let timeAgo = i === 1 ? (seed % 5 + 1) + " hrs ago" : (i + (seed % 3)) + " days ago";
        historyHtml += `
            <div class="dossier-hist-item" style="border-left-color: #00BCD4;">
                <div class="hist-time">${timeAgo}</div>
                <div class="hist-err">Resolved ${errName.toUpperCase()}</div>
                <div class="hist-res" style="color: #888;">Rating: 5.0 ⭐</div>
            </div>
        `;
    }

    let dispatchBtn = '';
    if (currentStatus === "ONLINE" && window.selectedFaultId) {
        dispatchBtn = `<button class="btn-dossier-action" style="background: #4CAF50; color: #000; margin-bottom: 10px;" onclick="window.sendDispatch()">TARGETED DISPATCH TO ${window.selectedFaultId}</button>`;
    }

    panel.innerHTML = `
        <div class="dossier-header">
            <h2 style="color:${statusColor}">FIELD AGENT</h2>
            <button class="btn-dossier-close" onclick="window.closeDossier()">✖</button>
        </div>
        <div class="dossier-content">
            <div style="margin-bottom: 20px;">
                <div style="font-size: 18px; color: #fff; font-weight: bold;">${agentId.replace('SIM-VANGUARD-', 'VAN-')}</div>
                <div style="color: ${statusColor}; font-size: 13px; font-weight: bold; margin-top: 4px;">${displayStatus}</div>
            </div>
            
            <div class="dossier-section">
                <h3>PERFORMANCE METRICS</h3>
                <div class="dossier-grid">
                    <div class="dossier-stat"><span class="label">REPUTATION</span><span class="val" style="color:#FFEB3B">${rep} ⭐</span></div>
                    <div class="dossier-stat"><span class="label">COMPLETION RATE</span><span class="val" style="color:#4CAF50">${compRate}%</span></div>
                    <div class="dossier-stat"><span class="label">AVG RESPONSE</span><span class="val">${avgResp}</span></div>
                    <div class="dossier-stat"><span class="label">TOTAL MISSIONS</span><span class="val">${totalMissions}</span></div>
                </div>
            </div>

            <div class="dossier-section">
                <h3>VERIFIED LOADOUT</h3>
                <div style="display:flex; flex-wrap:wrap; margin-top: 10px;">
                    ${capsHtml}
                </div>
            </div>

            <div class="dossier-section">
                <h3>RECENT ACTIVITY</h3>
                <div class="dossier-list">
                    ${historyHtml}
                </div>
            </div>

            <div style="margin-top: 20px;">
                ${dispatchBtn}
                <button class="btn-dossier-action" style="border-color: #E040FB; color: #E040FB;" onclick="window.loadReplay('${agentId}', null)">⏪ REWIND AGENT HISTORY</button>
            </div>
        </div>
    `;
    panel.classList.remove('hidden');
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initDossierUI);
} else {
    window.initDossierUI();
}