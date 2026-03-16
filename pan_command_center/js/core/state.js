// pan_command_center/js/core/state.js

// --- 1. FORMATTING HELPERS ---
window.formatMoney = function(num) {
    let isNeg = num < 0;
    let str = '$' + Math.abs(num).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    return isNeg ? '-' + str : str;
};

window.escapeHTML = function(str) {
    if (str === null || str === undefined) return '';
    return String(str).replace(/[&<>'"]/g, tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag]));
};

window.formatDuration = function(ms) {
    let m = Math.floor(ms / 60000);
    let s = Math.floor((ms % 60000) / 1000);
    return m + " MIN " + s + " SEC";
};

// --- 2. GLOBAL STATE VARIABLES ---
window.realAgents = {};
window.simAgents = {};
window.allAgents = {};
window.simFaults = {}; 
window.selectedFaultId = null; 
window.selectedFaultCircle = null; 
window.infoWindow = null;
window.faultToCancel = null; 
window.dispatchTargetId = null; 
window.demoAlertTimeout = null;

window.fleetBalance = 25000.00;
window.fleetLedger = [];
window.autoPilotActive = false;
window.autoPilotLimit = 0;
window.autoPilotEndTime = null;
window.lastSpawnTime = 0;

window.routingStrategy = 'BALANCED'; 

// --- 3. REPLAY STATE VARIABLES ---
window.isReplayMode = false;
window.replayData = [];
window.replayPath = null;
window.replayGhostMarker = null;

// --- 4. CONFIGURATION CONSTANTS ---
window.capNames = {
    "door_securing": "Door Securing", "cabin_sweep": "Cabin Sweep", "lost_item": "Lost Item", "path_clearing": "Path Clearing",
    "spill_remediation": "Spill Remediation", "tire_pressure": "Tire Pressure", "battery_jump": "Battery Jump", "passenger_escort": "Passenger Escort",
    "sensor_cleaning": "Sensor Cleaning", "scene_securement": "Scene Securement", "tire_replacement": "Tire Replacement", "manual_override": "Manual Override"
};

// Converted to a window variable so all future modules can access it
window.faultPrices = {
    "door_securing": 15.00, "cabin_sweep": 15.00, "lost_item": 25.00, "path_clearing": 25.00,
    "spill_remediation": 55.00, "tire_pressure": 55.00, "battery_jump": 55.00, "passenger_escort": 55.00,
    "sensor_cleaning": 85.00, "scene_securement": 85.00, "tire_replacement": 85.00, "manual_override": 85.00
};