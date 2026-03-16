// pan_command_center/js/forensics/replay.js
console.log("[DVR SCRIPT LOADED] Version 999 is actively running!");

window.isReplayMode = false;
window.isGlobalReplay = false;
window.replayData = [];
window.replayEntities = {};
window.replayVehicles = {}; 
window.replayLines = {};    
window.missionDestinations = {}; 
window.isPlaying = false;
window.playbackSpeed = 1;
window.currentPlaybackTime = 0;
window.animationFrameId = null;
window.lastFrameTime = null;

window.loadCustomReplay = async function() {
    console.log("[DVR ENGINE] loadCustomReplay triggered.");
    const dateVal = document.getElementById('dvr-date').value;
    const startVal = document.getElementById('dvr-start').value;
    const endVal = document.getElementById('dvr-end').value;

    if (!dateVal || !startVal || !endVal) {
        console.error("[DVR ENGINE] Missing input fields!");
        window.showDemoAlert("⚠️ Please select a valid Date, Start Time, and End Time.", 3000);
        return;
    }

    const startTs = new Date(`${dateVal}T${startVal}`).getTime() / 1000;
    const endTs = new Date(`${dateVal}T${endVal}`).getTime() / 1000;

    console.log(`[DVR ENGINE] Querying timestamps: Start=${startTs}, End=${endTs}`);

    let url = `/api/v1/telemetry/history?start_time=${startTs}&end_time=${endTs}&global=true`;
    await window.executeReplayFetch(url, true);
};

window.executeReplayFetch = async function(url, isGlobal) {
    window.showDemoAlert("⏳ Fetching & parsing forensic telemetry...", 2000);
    console.log("[DVR ENGINE] Fetching from:", url);
    
    try {
        let res = await fetch(url);
        if (!res.ok) throw new Error("API returned status " + res.status);
        let data = await res.json();
        
        if (!data || data.length === 0) {
            console.warn("[DVR ENGINE] Data array returned empty.");
            window.showDemoAlert("⚠️ No telemetry data found for these parameters.", 3000);
            return;
        }

        console.log(`[DVR ENGINE] Received ${data.length} rows of telemetry.`);

        window.isReplayMode = true;
        window.isGlobalReplay = isGlobal;
        window.replayData = data;
        
        window.missionDestinations = {};
        data.forEach(d => {
            if (d.current_mission_id && d.status === 'BUSY_ON_SITE') {
                window.missionDestinations[d.current_mission_id] = { lat: parseFloat(d.latitude), lng: parseFloat(d.longitude) };
            }
        });
        
        window.clearLiveMapForReplay();
        
        let minTime = Number(data[0].timestamp);
        let maxTime = Number(data[data.length - 1].timestamp);
        console.log(`[DVR ENGINE] MinTime: ${minTime} | MaxTime: ${maxTime} | Type: ${typeof minTime}`);
        
        let slider = document.getElementById('replay-slider');
        slider.step = "any"; 
        slider.min = minTime;
        slider.max = maxTime;
        slider.value = minTime; 
        
        window.currentPlaybackTime = minTime;

        let bounds = new google.maps.LatLngBounds();
        data.forEach(d => bounds.extend({ lat: parseFloat(d.latitude), lng: parseFloat(d.longitude) }));
        window.map.fitBounds(bounds);
        
        window.updateReplayUI(minTime);
        window.showDemoAlert("✅ DVR Loaded. Press Play.", 2000);

    } catch (err) {
        console.error("[DVR ENGINE] Fetch Error:", err);
        window.showDemoAlert("❌ Error fetching telemetry from server.", 3000);
    }
};

window.togglePlay = function() {
    console.log("[DVR ENGINE] togglePlay clicked.");
    if (!window.replayData || window.replayData.length === 0) {
        console.warn("[DVR ENGINE] Cannot play, replayData is empty.");
        return;
    }
    
    window.isPlaying = !window.isPlaying;
    const btn = document.getElementById('btn-play');
    
    if (window.isPlaying) {
        console.log("[DVR ENGINE] Starting playback...");
        btn.innerHTML = '⏸ PAUSE';
        btn.style.background = '#444';
        btn.style.color = '#fff';
        
        window.lastFrameTime = performance.now(); 
        window.animationFrameId = requestAnimationFrame(window.playbackLoop);
    } else {
        console.log("[DVR ENGINE] Pausing playback...");
        btn.innerHTML = '▶ PLAY';
        btn.style.background = 'transparent';
        btn.style.color = '#fff';
        if (window.animationFrameId) cancelAnimationFrame(window.animationFrameId);
    }
};

window.changeSpeed = function() {
    window.playbackSpeed = parseFloat(document.getElementById('dvr-speed').value) || 1;
    console.log("[DVR ENGINE] Speed changed to:", window.playbackSpeed);
};

window.playbackLoop = function() {
    if (!window.isPlaying) return;

    let now = performance.now();
    let deltaTime = (now - window.lastFrameTime) / 1000; 
    window.lastFrameTime = now;

    // Only process frame if delta is reasonable (prevents huge jumps)
    if (deltaTime > 0 && deltaTime < 0.25) { 
        let speed = parseFloat(document.getElementById('dvr-speed').value) || 1;
        let increment = (deltaTime * speed);
        window.currentPlaybackTime += increment;
        
        console.log(`[DVR MATH] Delta: ${deltaTime.toFixed(4)}s | Speed: ${speed}x | Added: +${increment.toFixed(2)}s | New Time: ${window.currentPlaybackTime}`);

        if (isNaN(window.currentPlaybackTime)) {
            console.error("[CRITICAL ERROR] currentPlaybackTime became NaN!");
            window.togglePlay(); 
            return;
        }

        let maxTime = parseFloat(document.getElementById('replay-slider').max);
        
        if (window.currentPlaybackTime >= maxTime) {
            console.log("[DVR ENGINE] Reached end of timeline. Stopping.");
            window.currentPlaybackTime = maxTime;
            window.updateReplayUI(maxTime);
            document.getElementById('replay-slider').value = maxTime;
            window.togglePlay(); 
            return;
        }

        document.getElementById('replay-slider').value = window.currentPlaybackTime;
        window.updateReplayUI(window.currentPlaybackTime);
    }
    
    window.animationFrameId = requestAnimationFrame(window.playbackLoop);
};

window.scrubReplay = function() {
    if (window.isPlaying) window.togglePlay();
    let val = parseFloat(document.getElementById('replay-slider').value);
    console.log("[DVR ENGINE] User scrubbed to:", val);
    if (!isNaN(val)) {
        window.currentPlaybackTime = val;
        window.updateReplayUI(window.currentPlaybackTime);
    }
};

window.updateReplayUI = function(targetTs) {
    if (!window.replayData || window.replayData.length === 0) return;

    let date = new Date(targetTs * 1000);
    document.getElementById('replay-time-display').innerText = date.toLocaleTimeString();

    let currentStates = {};
    for (let i = 0; i < window.replayData.length; i++) {
        let d = window.replayData[i];
        if (Number(d.timestamp) > targetTs) break; 
        currentStates[d.agent_id] = d;
    }

    let activeMissions = {}; 
    let safeFallbackIcon = { path: google.maps.SymbolPath.CIRCLE, scale: 6, fillColor: '#FF9800', fillOpacity: 1, strokeWeight: 2, strokeColor: '#fff' };
    let yCar = window.yellowCarIcon || safeFallbackIcon;
    let oCar = window.orangeCarIcon || safeFallbackIcon;

    if (!window.replayCircles) window.replayCircles = {};

    Object.keys(currentStates).forEach(agentId => {
        try {
            let state = currentStates[agentId];
            let lat = parseFloat(state.latitude);
            let lng = parseFloat(state.longitude);
            
            let ghostColor = state.status === 'ONLINE' ? '#00BCD4' : (state.status === 'BUSY_ON_SITE' ? '#FFEB3B' : '#FF9800');
            let iconDef = window.getMarkerIcon ? window.getMarkerIcon(ghostColor) : { path: google.maps.SymbolPath.CIRCLE, scale: 5, fillColor: ghostColor };

            if (!window.replayEntities[agentId]) {
                window.replayEntities[agentId] = new google.maps.Marker({
                    position: {lat: lat, lng: lng}, map: window.map,
                    icon: iconDef, title: agentId, zIndex: 2000
                });
            } else {
                window.replayEntities[agentId].setPosition({lat: lat, lng: lng});
                window.replayEntities[agentId].setIcon(iconDef);
            }

            if (state.current_mission_id) {
                activeMissions[state.current_mission_id] = true;
                let dest = window.missionDestinations[state.current_mission_id];
                
                if (dest) {
                    // 1. Draw the Vehicle
                    if (!window.replayVehicles[state.current_mission_id]) {
                        window.replayVehicles[state.current_mission_id] = new google.maps.Marker({
                            position: dest, map: window.map, 
                            icon: state.status === 'BUSY_ON_SITE' ? yCar : oCar, zIndex: 1100
                        });
                    } else {
                        window.replayVehicles[state.current_mission_id].setIcon(state.status === 'BUSY_ON_SITE' ? yCar : oCar);
                    }

                    // 2. Draw the Active Job Radar Circle
                    if (!window.replayCircles[state.current_mission_id]) {
                        window.replayCircles[state.current_mission_id] = new google.maps.Circle({
                            strokeColor: state.status === 'BUSY_ON_SITE' ? '#FFEB3B' : '#FF9800',
                            strokeOpacity: 0.8, strokeWeight: 2,
                            fillColor: state.status === 'BUSY_ON_SITE' ? '#FFEB3B' : '#F44336',
                            fillOpacity: 0.15, map: window.map, center: dest, radius: 800, zIndex: 800
                        });
                    } else {
                        window.replayCircles[state.current_mission_id].setOptions({
                            strokeColor: state.status === 'BUSY_ON_SITE' ? '#FFEB3B' : '#FF9800',
                            fillColor: state.status === 'BUSY_ON_SITE' ? '#FFEB3B' : '#F44336'
                        });
                    }

                    // 3. Draw the High-Visibility Dashed Manhattan Route Line
                    if (state.status === 'BUSY_ON_WAY') {
                        let path = [{lat: lat, lng: lng}, {lat: lat, lng: dest.lng}, dest];
                        let lineSymbol = { path: 'M 0,-1 0,1', strokeOpacity: 1, scale: 3 }; // Creates the dash
                        
                        if (!window.replayLines[agentId]) {
                            window.replayLines[agentId] = new google.maps.Polyline({
                                path: path, strokeOpacity: 0, strokeColor: '#FF9800', strokeWeight: 3, 
                                icons: [{ icon: lineSymbol, offset: '0', repeat: '15px' }], map: window.map, zIndex: 900
                            });
                        } else {
                            window.replayLines[agentId].setPath(path);
                            window.replayLines[agentId].setMap(window.map);
                        }
                    } else {
                        if (window.replayLines[agentId]) window.replayLines[agentId].setMap(null);
                    }
                }
            } else {
                if (window.replayLines[agentId]) window.replayLines[agentId].setMap(null);
            }
        } catch (e) {
            console.error(`Render fail for ${agentId}:`, e);
        }
    });

    Object.keys(window.replayEntities).forEach(agentId => {
        if (!currentStates[agentId]) {
            window.replayEntities[agentId].setMap(null);
            delete window.replayEntities[agentId];
        }
    });

    Object.keys(window.replayVehicles).forEach(missionId => {
        if (!activeMissions[missionId]) {
            window.replayVehicles[missionId].setMap(null);
            delete window.replayVehicles[missionId];
            if (window.replayCircles[missionId]) {
                window.replayCircles[missionId].setMap(null);
                delete window.replayCircles[missionId];
            }
        }
    });
};

window.exitReplay = function() {
    if (window.isPlaying) window.togglePlay();
    window.isReplayMode = false;
    window.isGlobalReplay = false;
    document.getElementById('replay-panel').style.display = 'none';
    
    if (window.replayEntities) Object.values(window.replayEntities).forEach(m => m.setMap(null));
    if (window.replayVehicles) Object.values(window.replayVehicles).forEach(m => m.setMap(null));
    if (window.replayLines) Object.values(window.replayLines).forEach(m => m.setMap(null));
    if (window.replayCircles) Object.values(window.replayCircles).forEach(m => m.setMap(null));
    
    window.replayData = [];
    window.replayEntities = {};
    window.replayVehicles = {};
    window.replayLines = {};
    window.replayCircles = {};
    
    window.mergeAndRender(); 
};

window.clearLiveMapForReplay = function() {
    Object.values(window.agentMarkers || {}).forEach(m => m.setMap(null));
    Object.values(window.avMarkers || {}).forEach(m => m.setMap(null));
    Object.values(window.agentLines || {}).forEach(m => m.setMap(null));
    Object.values(window.agentCircles || {}).forEach(m => m.setMap(null));
    if (window.selectedFaultCircle) window.selectedFaultCircle.setMap(null);
    try {
        if (window.infoWindow) window.infoWindow.close();
    } catch (e) {}
};