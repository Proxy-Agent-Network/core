// pan_command_center/js/map/renderer.js

window.agentMarkers = window.agentMarkers || {};
window.agentCircles = window.agentCircles || {}; 
window.agentLines = window.agentLines || {}; 
window.avMarkers = window.avMarkers || {}; 
window.cyanCarIcon = null;
window.orangeCarIcon = null;
window.yellowCarIcon = null;
window.greyCarIcon = null; 
window.silverCarIcon = null;

window.clearSelection = function() {
    if (window.selectedFaultId) {
        window.selectedFaultId = null;
        window.mergeAndRender();
    }
    if (typeof window.closeDossier === 'function') {
        window.closeDossier();
    }
};

window.initMap = function() {
    window.ds = new google.maps.DirectionsService();
    window.geocoder = new google.maps.Geocoder(); 
    
    const carSvg = 'M29.8,12.6l-5.3-3.6c-0.8-0.5-1.8-0.9-2.8-0.9h-8.5c-2.3,0-4.3,1.5-5,3.7L6.8,16H3c-1.7,0-3,1.3-3,3v4c0,1.1,0.9,2,2,2h1.2 c0.4,2.3,2.4,4,4.8,4s4.4-1.7,4.8-4h6.4c0.4,2.3,2.4,4,4.8,4s4.4-1.7,4.8-4h1.2c1.1,0,2-0.9,2-2v-5.6C32,15.7,31.2,14.1,29.8,12.6z M8,23c-1.1,0-2-0.9-2-2s0.9-2,2-2s2,0.9,2,2S9.1,23,8,23z M24,23c-1.1,0-2-0.9-2-2s0.9-2,2-2s2,0.9,2,2S25.1,23,24,23z M12.5,14 l2.1-4.7C14.8,9.1,15.1,9,15.4,9h6c0.5,0,0.9,0.3,1.2,0.7l4,5.3H12.5z';
    window.cyanCarIcon = { path: carSvg, fillColor: '#00BCD4', fillOpacity: 1, strokeColor: '#121212', strokeWeight: 1, scale: 0.9, anchor: new google.maps.Point(16, 16) };
    window.orangeCarIcon = { path: carSvg, fillColor: '#FF9800', fillOpacity: 1, strokeColor: '#121212', strokeWeight: 1, scale: 0.9, anchor: new google.maps.Point(16, 16) };
    window.yellowCarIcon = { path: carSvg, fillColor: '#FFEB3B', fillOpacity: 1, strokeColor: '#121212', strokeWeight: 1, scale: 0.9, anchor: new google.maps.Point(16, 16) };
    window.greyCarIcon = { path: carSvg, fillColor: '#555555', fillOpacity: 1, strokeColor: '#121212', strokeWeight: 1, scale: 0.9, anchor: new google.maps.Point(16, 16) };
    window.silverCarIcon = { path: carSvg, fillColor: '#EEEEEE', fillOpacity: 0.5, strokeColor: '#121212', strokeWeight: 1, scale: 0.7, anchor: new google.maps.Point(16, 16) };
    
    window.healthyAVMarkers = window.healthyAVMarkers || {};

    const tacticalStyle = [
        { elementType: "geometry", stylers: [{ color: "#212121" }] },
        { elementType: "labels.icon", stylers: [{ visibility: "off" }] },
        { elementType: "labels.text.fill", stylers: [{ color: "#757575" }] },
        { elementType: "labels.text.stroke", stylers: [{ color: "#212121" }] },
        { featureType: "road", elementType: "geometry", stylers: [{ color: "#383838" }] },
        { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#212121" }] },
        { featureType: "water", elementType: "geometry", stylers: [{ color: "#000000" }] }
    ];

    window.map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 33.415, lng: -111.831 }, zoom: 11, styles: tacticalStyle, disableDefaultUI: true, zoomControl: true
    });
    
    window.map.addListener('click', window.clearSelection);

    if (window.generateSimulatedAgents) window.generateSimulatedAgents();
};

window.startTelemetryLink = function() {
    if (!window.firebaseDb || !window.firebaseRef || !window.firebaseOnValue) {
        setTimeout(window.startTelemetryLink, 500);
        return;
    }
    const agentsRef = window.firebaseRef(window.firebaseDb, 'agents');
    window.firebaseOnValue(agentsRef, (snapshot) => {
        window.realAgents = snapshot.val() || {};
        window.mergeAndRender();
    });
};

window.showOnMap = function(faultId) {
    if (window.simFaults[faultId]) {
        let f = window.simFaults[faultId];
        window.map.panTo({lat: f.lat, lng: f.lon});
        window.map.setZoom(14);
        window.selectedFaultId = faultId;
        if (window.avMarkers && window.avMarkers[faultId]) {
            new google.maps.event.trigger(window.avMarkers[faultId], 'click');
        }
        window.mergeAndRender();
    }
};

window.mergeAndRender = function() {
    if (window.isReplayMode) return;

    window.allAgents = { ...window.simAgents, ...window.realAgents };
    const faultListDiv = document.getElementById('fault-list');
    if (!faultListDiv) return;
    
    let faultArr = Object.values(window.simFaults);
    if (faultArr.length > 0) {
        let p = faultListDiv.querySelector('#empty-msg');
        if (p) p.style.display = 'none';
    }

    let unassignedCount = faultArr.filter(f => f.status === "UNASSIGNED").length;
    let deployBtn = document.getElementById('deploy-all-btn');
    if (deployBtn) {
        deployBtn.innerText = `DEPLOY ALL (${unassignedCount})`;
        deployBtn.disabled = unassignedCount === 0 || window.autoPilotActive;
    }

    const getRank = (f) => {
        if (f.status === "RESOLVED") return 3;
        if (f.status === "UNASSIGNED") return 0;
        let agent = window.allAgents[f.assignedAgent];
        if (agent && agent.status.status === "BUSY_ON_SITE") return 2;
        return 1;
    };

    faultArr.sort((a, b) => {
        let rankA = getRank(a);
        let rankB = getRank(b);
        if (rankA !== rankB) return rankA - rankB;
        return a.timestamp - b.timestamp; 
    });

    faultArr.forEach((f, index) => {
        let isResolved = f.status === "RESOLVED";
        let isCanceled = f.canceled === true;
        let isAssigned = f.status === "ASSIGNED";
        let isSelected = window.selectedFaultId === f.id;
        
        let agentOnSite = false;
        if (isAssigned && f.assignedAgent && window.allAgents[f.assignedAgent]) {
            if (window.allAgents[f.assignedAgent].status.status === "BUSY_ON_SITE") agentOnSite = true;
        }

        let cardClass = isResolved ? "fault-grey" : (isAssigned ? (agentOnSite ? "fault-yellow" : "fault-orange") : "fault-cyan");
        if (isSelected && !isResolved) cardClass += isAssigned ? (agentOnSite ? " selected-yellow" : " selected-orange") : " selected-cyan";
        if (isSelected && isResolved) cardClass += " selected-grey";
        
        let tierStr = "TIER 1";
        if (['spill_remediation', 'tire_pressure', 'battery_jump', 'passenger_escort'].includes(f.errorCode)) tierStr = "TIER 2";
        if (['sensor_cleaning', 'scene_securement', 'tire_replacement', 'manual_override'].includes(f.errorCode)) tierStr = "TIER 3";

        let shortAgentId = isAssigned && f.assignedAgent ? f.assignedAgent.replace('SIM-VANGUARD-', 'VAN-') : '';
        let titleTxt = `${f.id} (UNASSIGNED ${tierStr})`;
        if (isAssigned) titleTxt = `${f.id} ASSIGNED TO ${shortAgentId}`;
        if (isResolved) titleTxt = isCanceled ? `${f.id} (CANCELLED)` : `${f.id} (RESOLVED)`;

        let etaHtml = "";
        if (isAssigned && f.assignedAgent) {
            let agent = window.allAgents[f.assignedAgent];
            if (agent && agent.status.status === "BUSY_ON_WAY") {
                let p1 = new google.maps.LatLng(agent.status.latitude, agent.status.longitude);
                let p2 = new google.maps.LatLng(f.lat, f.lon);
                let distMeters = google.maps.geometry.spherical.computeDistanceBetween(p1, p2);
                let etaMinutes = Math.max(1, Math.ceil(distMeters / 600));
                etaHtml = `<div class="fault-eta">${etaMinutes} MINUTES UNTIL ARRIVAL</div>`;
            } else if (agent && agent.status.status === "BUSY_ON_SITE") {
                etaHtml = `<div class="fault-eta arrived">AGENT ON SITE</div>`;
            }
        }

        let btnTheme = isResolved ? "btn-map-grey" : (isAssigned ? (agentOnSite ? "btn-map-yellow" : "btn-map-orange") : "btn-map-cyan");

        let actionsHtml = `<div class="sidebar-actions">`;
        if (isAssigned && !isResolved) {
            actionsHtml += `<button class="btn-action-small btn-cancel-small" onclick="event.stopPropagation(); window.openCancelModal('${f.id}')">CANCEL</button>`;
            actionsHtml += `<button class="btn-action-small ${btnTheme}" onclick="event.stopPropagation(); window.showOnMap('${f.id}')">SHOW ON MAP</button>`;
        } else if (!isAssigned && !isResolved) {
            actionsHtml += `<button class="btn-action-small btn-deploy-cyan" onclick="event.stopPropagation(); window.openDispatchModal('${f.id}')">DEPLOY AGENT</button>`;
            actionsHtml += `<button class="btn-action-small ${btnTheme}" onclick="event.stopPropagation(); window.showOnMap('${f.id}')">SHOW ON MAP</button>`;
        } else {
            actionsHtml += `<button class="btn-action-small ${btnTheme}" style="flex: 2;" onclick="event.stopPropagation(); window.showOnMap('${f.id}')">SHOW ON MAP</button>`;
        }
        actionsHtml += `</div>`;

        let timerHtml = "";
        if (isResolved) {
            let endWord = isCanceled ? "CANCELLED" : "CLEARED";
            let feeText = isCanceled && f.cancelFee > 0 ? ` (FEE: $${f.cancelFee.toFixed(2)})` : "";
            timerHtml = `<span style="color:#888;">${endWord} IN ${window.formatDuration(f.resolvedAt - f.timestamp)}${feeText}</span>`;
        } else {
            timerHtml = `<span class="live-timer" data-timestamp="${f.timestamp}">${window.formatDuration(Date.now() - f.timestamp)}</span>`;
        }

        let cardId = 'card-' + f.id;
        let card = document.getElementById(cardId);
        
        if (!card) {
            card = document.createElement('div');
            card.id = cardId;
            card.onclick = () => window.showOnMap(f.id);
            faultListDiv.appendChild(card);
        }

        let expectedClass = `fault-card ${cardClass}`;
        if (card.className !== expectedClass) card.className = expectedClass;

        let stateHash = `${f.status}_${isSelected}_${etaHtml}_${f.canceled}_${actionsHtml}`;
        if (card.getAttribute('data-state') !== stateHash) {
            card.setAttribute('data-state', stateHash);
            card.innerHTML = `
                <h4>${window.escapeHTML(titleTxt)}</h4>
                <div class="fault-detail">ERROR CODE: ${window.capNames[f.errorCode] ? window.capNames[f.errorCode].toUpperCase() : f.errorCode}</div>
                ${etaHtml}
                <div class="fault-time">TIME ELAPSED: ${timerHtml}</div>
                ${actionsHtml}
            `;
        }

        if (faultListDiv.children[index] !== card) faultListDiv.insertBefore(card, faultListDiv.children[index]);
    });

    const currentIds = new Set(faultArr.map(f => 'card-' + f.id));
    Array.from(faultListDiv.children).forEach(child => {
        if (child.tagName && child.tagName.toLowerCase() === 'div' && !currentIds.has(child.id)) {
            faultListDiv.removeChild(child);
        }
    });

    const activeFilterEl = document.getElementById('filter-cap');
    const activeFilter = activeFilterEl ? activeFilterEl.value : 'ALL';
    const showOnline = document.getElementById('leg-online') ? document.getElementById('leg-online').checked : true;
    const showFoot = document.getElementById('leg-foot') ? document.getElementById('leg-foot').checked : true;
    const showOnWay = document.getElementById('leg-onway') ? document.getElementById('leg-onway').checked : true;
    const showOnSite = document.getElementById('leg-onsite') ? document.getElementById('leg-onsite').checked : true;

    const renderedUIDs = new Set();
    const renderedFaultIDs = new Set();

    if (!window.map) return; 

    // 🟢 DRAW ACTIVE & RESOLVED FAULTS
    Object.keys(window.simFaults).forEach(faultId => {
        const fault = window.simFaults[faultId];
        renderedFaultIDs.add(faultId);

        const pos = { lat: fault.lat, lng: fault.lon };
        const isAssigned = fault.status === "ASSIGNED";
        const isResolved = fault.status === "RESOLVED";
        
        let agentOnSite = false;
        if (isAssigned && fault.assignedAgent && window.allAgents[fault.assignedAgent]) {
            if (window.allAgents[fault.assignedAgent].status.status === "BUSY_ON_SITE") agentOnSite = true;
        }

        let iconToUse = window.cyanCarIcon;
        if (isAssigned) iconToUse = agentOnSite ? window.yellowCarIcon : window.orangeCarIcon; 
        if (isResolved) iconToUse = window.greyCarIcon;

        window.avMarkers = window.avMarkers || {};

        if (!window.avMarkers[faultId]) {
            window.avMarkers[faultId] = new google.maps.Marker({
                position: pos, map: window.map, icon: iconToUse, zIndex: 1100
            });

            // 🟢 FAULT MARKER CLICK LISTENER
            window.avMarkers[faultId].addListener('click', () => {
                window.selectedFaultId = faultId;
                window.mergeAndRender(); // Ensure glowing circle highlights
                
                // Pre-fill Dispatch Panel for convenience
                const filterCap = document.getElementById('filter-cap');
                if (filterCap) filterCap.value = fault.errorCode;
                let dropdown = document.getElementById('disp-error');
                if (dropdown) {
                    for(let i=0; i<dropdown.options.length; i++) {
                        if(dropdown.options[i].value.startsWith(fault.errorCode)) { dropdown.selectedIndex = i; break; }
                    }
                    if (window.updateBounty) window.updateBounty();
                }
                const dispLoc = document.getElementById('disp-loc');
                if (dispLoc) dispLoc.value = "Locating Address...";
                if (window.geocoder && dispLoc) {
                    window.geocoder.geocode({ location: pos }, (results, status) => {
                        if (status === "OK" && results[0]) dispLoc.value = results[0].formatted_address.split(',')[0];
                        else dispLoc.value = `GPS: ${fault.lat.toFixed(4)}, ${fault.lon.toFixed(4)}`;
                    });
                }
                
                // Open new Dossier panel
                if (typeof window.openFaultDossier === 'function') {
                    window.openFaultDossier(faultId);
                }
            });
        } else {
            window.avMarkers[faultId].setPosition(pos);
            window.avMarkers[faultId].setIcon(iconToUse);
        }
    });

    if (window.selectedFaultId && window.simFaults[window.selectedFaultId]) {
        let sf = window.simFaults[window.selectedFaultId];
        let pos = { lat: sf.lat, lng: sf.lon };
        let agentOnSite = false;
        if (sf.status === "ASSIGNED" && sf.assignedAgent && window.allAgents[sf.assignedAgent]) {
            if (window.allAgents[sf.assignedAgent].status.status === "BUSY_ON_SITE") agentOnSite = true;
        }
        let glowColor = sf.status === "RESOLVED" ? "#555555" : (sf.status === "ASSIGNED" ? (agentOnSite ? "#FFEB3B" : "#FF9800") : "#00BCD4");
        
        if (!window.selectedFaultCircle) {
            window.selectedFaultCircle = new google.maps.Circle({
                strokeColor: glowColor, strokeOpacity: 0.8, strokeWeight: 2, fillColor: glowColor, fillOpacity: 0.25,
                map: window.map, center: pos, radius: 450, clickable: false
            });
        } else {
            window.selectedFaultCircle.setOptions({ strokeColor: glowColor, fillColor: glowColor, center: pos, map: window.map });
        }
    } else {
        if (window.selectedFaultCircle) {
            window.selectedFaultCircle.setMap(null); window.selectedFaultCircle = null;
        }
    }

    // 🟢 DRAW AGENTS
    Object.keys(window.allAgents).forEach(uid => {
        try {
            const agent = window.allAgents[uid];
            if (!agent || !agent.status) return;

            let caps = agent.capabilities || [];
            if (agent.status.loadout) caps = Object.keys(agent.status.loadout);
            agent.resolvedCaps = caps;

            if (activeFilter !== 'ALL' && !caps.includes(activeFilter)) return; 

            const currentStatus = agent.status.status;
            const patrolMode = agent.status.patrolMode || "VEHICLE";
            
            let isVisible = false;
            if (currentStatus === "ONLINE" && patrolMode === "VEHICLE" && showOnline) isVisible = true;
            if (currentStatus === "ONLINE" && patrolMode === "FOOT" && showFoot) isVisible = true;
            if (currentStatus === "BUSY_ON_WAY" && showOnWay) isVisible = true;
            if (currentStatus === "BUSY_ON_SITE" && showOnSite) isVisible = true;
            if (currentStatus === "PENDING" || currentStatus === "OFFLINE") isVisible = true; 
            
            if (!isVisible) return;
            renderedUIDs.add(uid);

            const lat = Number(agent.status.latitude);
            const lon = Number(agent.status.longitude);
            const radiusMeters = Number(agent.status.radius || 0) * 1609.34; 

            if (!isNaN(lat) && !isNaN(lon)) {
                const position = { lat: lat, lng: lon };
                let agentColor = "#F44336"; 

                if (currentStatus === "ONLINE" && patrolMode === "FOOT") agentColor = "#00BCD4"; 
                else if (currentStatus === "ONLINE") agentColor = "#4CAF50"; // Use green internally for standard online
                else if (currentStatus === "BUSY_ON_WAY") agentColor = "#FF9800";
                else if (currentStatus === "BUSY_ON_SITE") agentColor = "#FFEB3B";
                else if (currentStatus === "PENDING") agentColor = "#E040FB";
                else if (currentStatus === "OFFLINE") agentColor = "#888888";
                
                // Always render standard online as RED on the map (per previous style) unless foot patrol
                let mapColor = (currentStatus === "ONLINE" && patrolMode === "VEHICLE") ? "#F44336" : agentColor;

                window.agentMarkers = window.agentMarkers || {};

                if (!window.agentMarkers[uid]) {
                    window.agentMarkers[uid] = new google.maps.Marker({
                        position: position, map: window.map, title: "Agent: " + window.escapeHTML(uid), icon: window.getMarkerIcon(mapColor), zIndex: 1000 
                    });
                    
                    // 🟢 AGENT MARKER CLICK LISTENER
                    window.agentMarkers[uid].addListener('click', () => {
                        // Crucial: Do NOT call clearSelection() here, or targeted dispatch breaks!
                        const dispUid = document.getElementById('disp-uid');
                        if (dispUid) dispUid.value = window.escapeHTML(uid);
                        
                        if (typeof window.openAgentDossier === 'function') {
                            window.openAgentDossier(uid);
                        }
                    });
                } else {
                    window.agentMarkers[uid].setPosition(position);
                    window.agentMarkers[uid].setIcon(window.getMarkerIcon(mapColor));
                }

                if (currentStatus === "ONLINE" || currentStatus === "PENDING") {
                    window.agentCircles = window.agentCircles || {};
                    if (window.agentCircles[uid]) {
                        window.agentCircles[uid].setCenter(position);
                        window.agentCircles[uid].setRadius(radiusMeters);
                        window.agentCircles[uid].setOptions({ fillColor: mapColor, strokeColor: mapColor });
                    } else {
                        window.agentCircles[uid] = new google.maps.Circle({
                            strokeColor: mapColor, strokeOpacity: 0.3, strokeWeight: 1, fillColor: mapColor, fillOpacity: 0.10, 
                            map: window.map, center: position, radius: radiusMeters, clickable: false 
                        });
                    }
                } else {
                    if (window.agentCircles && window.agentCircles[uid]) { window.agentCircles[uid].setMap(null); delete window.agentCircles[uid]; }
                }

                if (currentStatus === "BUSY_ON_WAY" && agent.route && agent.route.length > 0) {
                    let remainingPath = agent.route.slice(agent.routeIndex);
                    remainingPath.unshift(position); 
                    window.agentLines = window.agentLines || {};
                    if (!window.agentLines[uid]) {
                        window.agentLines[uid] = new google.maps.Polyline({
                            path: remainingPath, strokeColor: '#FF9800', strokeOpacity: 0.9, strokeWeight: 4, zIndex: 900, map: window.map
                        });
                    } else {
                        window.agentLines[uid].setPath(remainingPath); window.agentLines[uid].setMap(window.map);
                    }
                } else {
                    if (window.agentLines && window.agentLines[uid]) { window.agentLines[uid].setMap(null); delete window.agentLines[uid]; }
                }
            }
        } catch (e) { console.error("Failed to render agent: " + uid, e); }
    });
    
    if (window.agentMarkers) {
        Object.keys(window.agentMarkers).forEach(uid => {
            if (!renderedUIDs.has(uid)) {
                window.agentMarkers[uid].setMap(null); delete window.agentMarkers[uid];
                if (window.agentCircles && window.agentCircles[uid]) { window.agentCircles[uid].setMap(null); delete window.agentCircles[uid]; }
                if (window.agentLines && window.agentLines[uid]) { window.agentLines[uid].setMap(null); delete window.agentLines[uid]; }
            }
        });
    }

    if (window.avMarkers) {
        Object.keys(window.avMarkers).forEach(fid => {
            if (!renderedFaultIDs.has(fid)) {
                window.avMarkers[fid].setMap(null); delete window.avMarkers[fid];
            }
        });
    }

    // 🟢 RENDER HEALTHY FLEET
    let showHealthy = document.getElementById('filter-healthy') ? document.getElementById('filter-healthy').checked : true;
    
    if (window.healthyFleet && showHealthy) {
        Object.keys(window.healthyFleet).forEach(avId => {
            let av = window.healthyFleet[avId];
            if (!window.healthyAVMarkers[avId]) {
                window.healthyAVMarkers[avId] = new google.maps.Marker({
                    position: {lat: av.lat, lng: av.lng}, map: window.map, icon: window.silverCarIcon, title: `Healthy AV: ${avId}`, zIndex: 500
                });

                // 🟢 HEALTHY CAR CLICK LISTENER
                window.healthyAVMarkers[avId].addListener('click', () => {
                    window.clearSelection(); 
                    if (typeof window.openHealthyAVDossier === 'function') {
                        window.openHealthyAVDossier(avId, av.lastErrorCode, av.lastErrorTime);
                    }
                });
            } else {
                window.healthyAVMarkers[avId].setPosition({lat: av.lat, lng: av.lng});
            }
        });
    } else {
        Object.values(window.healthyAVMarkers || {}).forEach(m => m.setMap(null));
        window.healthyAVMarkers = {};
    }
};

window.getMarkerIcon = function(color) {
    return { path: google.maps.SymbolPath.CIRCLE, fillColor: color, fillOpacity: 1, strokeColor: "#ffffff", strokeWeight: 2, scale: 8 };
};