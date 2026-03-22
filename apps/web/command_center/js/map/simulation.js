// pan_command_center/js/map/simulation.js

window.healthyFleet = window.healthyFleet || {};

window.getBestAgent = function(qualifiedAgents, faultPos, basePrice) {
    if (!qualifiedAgents || qualifiedAgents.length === 0) return null;
    
    qualifiedAgents.forEach(q => {
        q.bid = basePrice * (q.agent.costMultiplier || 1.0);
    });

    if (window.routingStrategy === 'SPEED') {
        qualifiedAgents.sort((a, b) => a.distance - b.distance);
    } else if (window.routingStrategy === 'COST') {
        qualifiedAgents.sort((a, b) => a.bid - b.bid);
    } else { 
        let maxDist = Math.max(...qualifiedAgents.map(q => q.distance));
        let maxBid = Math.max(...qualifiedAgents.map(q => q.bid));
        if(maxDist === 0) maxDist = 1; if(maxBid === 0) maxBid = 1;
        
        qualifiedAgents.sort((a, b) => {
            let scoreA = (a.distance / maxDist) + (a.bid / maxBid);
            let scoreB = (b.distance / maxDist) + (b.bid / maxBid);
            return scoreA - scoreB;
        });
    }
    return qualifiedAgents[0];
};

window.executeDispatch = function() {
    let tid = window.dispatchTargetId; 
    window.closeDispatchModal();
    
    let targetFaults = [];
    if (tid) {
        if (window.simFaults[tid]) {
            targetFaults.push(window.simFaults[tid]);
        }
        window.showDemoAlert(`🚀 QUICK DISPATCH INITIATED...<br>Routing best agent based on ${window.routingStrategy} algorithm.`, 3500);
    } else {
        targetFaults = Object.values(window.simFaults).filter(f => f.status === "UNASSIGNED");
        window.showDemoAlert(`🚀 MASS DISPATCH INITIATED...<br>Routing best agents based on ${window.routingStrategy} algorithm.`, 4000);
    }

    targetFaults.forEach((fault, index) => {
        let delay = tid ? 0 : index * 400; 
        
        setTimeout(() => {
            const faultPos = new google.maps.LatLng(fault.lat, fault.lon);
            let qualifiedAgents = [];

            Object.keys(window.simAgents).forEach(agentId => {
                let a = window.simAgents[agentId];
                if (a.status.status === "ONLINE" && a.capabilities.includes(fault.errorCode)) {
                    let agentPos = new google.maps.LatLng(a.status.latitude, a.status.longitude);
                    let dist = google.maps.geometry.spherical.computeDistanceBetween(faultPos, agentPos);
                    qualifiedAgents.push({ id: agentId, agent: a, distance: dist });
                }
            });

            let target = window.getBestAgent(qualifiedAgents, faultPos, window.faultPrices[fault.errorCode] || 15.00);

            if (target) {
                let agent = target.agent;
                
                agent.status.status = "BUSY_ON_WAY";
                agent.status.currentFaultId = fault.id;
                fault.status = "ASSIGNED";
                fault.assignedAgent = target.id;
                fault.assignedAt = Date.now();
                
                let maxPrice = window.faultPrices[fault.errorCode] || 15.00;
                fault.lockedPrice = maxPrice; 
                
                fault.history = fault.history || [];
                fault.history.push({ time: Date.now(), event: tid ? 'ASSIGNED_QUICK' : 'ASSIGNED_MASS', agentId: target.id });

                window.addLedgerEntry(-maxPrice, 'ESCROW_LOCK', `Escrow Locked: ${window.capNames[fault.errorCode]}`, fault.id, { errorCode: fault.errorCode });

                let p1 = new google.maps.LatLng(agent.status.latitude, agent.status.longitude);
                let p2 = new google.maps.LatLng(fault.lat, fault.lon);

                window.ds.route({ origin: p1, destination: p2, travelMode: 'DRIVING' }, (res, status) => {
                    if (status === 'OK') {
                        agent.route = res.routes[0].overview_path;
                        agent.routeIndex = 0;
                    } else {
                        agent.route = [p1, p2];
                        agent.routeIndex = 0;
                    }
                });
            } else if (tid) {
                window.showDemoAlert(`🚨 No qualified agents currently online for ${fault.id}.`, 4000);
            }
            window.mergeAndRender();
        }, delay); 
    });
};

window.executeCancelDispatch = function() {
    let faultId = window.faultToCancel;
    let f = window.simFaults[faultId];
    
    if (f && f.status === "ASSIGNED") {
        let agentId = f.assignedAgent;
        let a = window.allAgents[agentId];
        
        let timeResponded = Date.now() - (f.assignedAt || f.timestamp);
        let fee = timeResponded > 60000 ? 5.00 : 0.00;
        let price = f.lockedPrice || (window.faultPrices[f.errorCode] || 15.00);
        
        if (a) {
            a.status.status = "ONLINE";
            a.status.currentFaultId = null;
            a.route = null;
        }
        
        f.status = "UNASSIGNED"; 
        f.assignedAgent = null;

        f.history = f.history || [];
        f.history.push({ time: Date.now(), event: 'CANCELLED_BY_DISPATCH', fee: fee });
        
        if (fee > 0) {
            window.refundLedger(f.id, price, fee, `Dispatcher Cancelled ($5.00 Fee applied)`, f.errorCode);
            window.showDemoAlert(`❌ Dispatch Cancelled.<br>Agent paid $5.00 response fee. Vehicle returned to Unassigned.`, 4000);
        } else {
            window.refundLedger(f.id, price, 0, `Dispatcher Cancelled ($0 Fee)`, f.errorCode);
            window.showDemoAlert(`❌ Dispatch Cancelled.<br>Full escrow refunded ($0 fee). Vehicle returned to Unassigned.`, 4000);
        }
        
        if (window.selectedFaultId === faultId) window.clearSelection();
    }
    window.closeCancelModal();
    window.mergeAndRender();
};

window.agentAbortsMission = function(agentId, faultId) {
    let agent = window.simAgents[agentId];
    let fault = window.simFaults[faultId];
    if (!agent || !fault) return;

    fault.history = fault.history || [];
    fault.history.push({ time: Date.now(), event: 'AGENT_ABORTED', agentId: agentId });

    let lockedAmt = fault.lockedPrice || (window.faultPrices[fault.errorCode] || 15.00);
    window.refundLedger(fault.id, lockedAmt, 0, `Agent Flaked - Auto-Refunded`, fault.errorCode);

    agent.status.status = "ONLINE";
    agent.status.currentFaultId = null;
    agent.route = null;

    fault.status = "UNASSIGNED";
    fault.assignedAgent = null;
    fault.lockedPrice = null;

    window.showDemoAlert(`⚠️ Agent ${agentId.replace('SIM-VANGUARD-', 'VAN-')} aborted mission!<br>Auto-rerouting next closest agent...`, 3500);
    window.mergeAndRender();

    setTimeout(() => {
        let qualifiedAgents = [];
        const faultPos = new google.maps.LatLng(fault.lat, fault.lon);
        
        Object.keys(window.simAgents).forEach(id => {
            if (id === agentId) return; 
            let a = window.simAgents[id];
            if (a.status.status === "ONLINE" && a.capabilities.includes(fault.errorCode)) {
                let agentPos = new google.maps.LatLng(a.status.latitude, a.status.longitude);
                let dist = google.maps.geometry.spherical.computeDistanceBetween(faultPos, agentPos);
                qualifiedAgents.push({ id: id, agent: a, distance: dist });
            }
        });

        let target = window.getBestAgent(qualifiedAgents, faultPos, window.faultPrices[fault.errorCode] || 15.00);

        if (target) {
            target.agent.status.status = "BUSY_ON_WAY";
            target.agent.status.currentFaultId = fault.id;
            fault.status = "ASSIGNED";
            fault.assignedAgent = target.id;
            fault.assignedAt = Date.now();
            
            let newPrice = window.faultPrices[fault.errorCode] || 15.00;
            fault.lockedPrice = newPrice;
            window.addLedgerEntry(-newPrice, 'ESCROW_LOCK', `Escrow Re-Locked for Auto-Routing`, fault.id, { errorCode: fault.errorCode });

            fault.history.push({ time: Date.now(), event: 'AUTO_REASSIGN', newAgent: target.id });

            let p1 = new google.maps.LatLng(target.agent.status.latitude, target.agent.status.longitude);
            let p2 = new google.maps.LatLng(fault.lat, fault.lon);
            
            window.ds.route({ origin: p1, destination: p2, travelMode: 'DRIVING' }, (res, status) => {
                if (status === 'OK') {
                    target.agent.route = res.routes[0].overview_path;
                    target.agent.routeIndex = 0;
                } else {
                    target.agent.route = [p1, p2];
                    target.agent.routeIndex = 0;
                }
            });
            window.mergeAndRender();
        } else {
            window.showDemoAlert(`🚨 No backup agents available for ${fault.id}. Escalate to fleet.`, 4000);
        }
    }, 2500); 
};

window.sendDispatch = function() {
    const uid = document.getElementById('disp-uid').value;
    
    if (!uid) { 
        if (!window.selectedFaultId || !window.simFaults[window.selectedFaultId]) {
            alert("DEMO MODE: First click a Cyan AV car on the map to target it.");
            return;
        }

        const fault = window.simFaults[window.selectedFaultId];
        const faultPos = new google.maps.LatLng(fault.lat, fault.lon);

        let qualifiedAgents = [];
        Object.keys(window.simAgents).forEach(agentId => {
            let a = window.simAgents[agentId];
            if (a.status.status === "ONLINE" && a.capabilities.includes(fault.errorCode)) {
                let agentPos = new google.maps.LatLng(a.status.latitude, a.status.longitude);
                let dist = google.maps.geometry.spherical.computeDistanceBetween(faultPos, agentPos);
                qualifiedAgents.push({ id: agentId, agent: a, distance: dist });
            }
        });

        if (qualifiedAgents.length === 0) {
            alert("No qualified agents are currently online for this task!");
            return;
        }

        let target = window.getBestAgent(qualifiedAgents, faultPos, window.faultPrices[fault.errorCode] || 15.00);

        if (target) {
            let agent = target.agent;
            let agentId = target.id;

            agent.status.status = "PENDING";
            window.mergeAndRender();
            
            let milesAway = (target.distance / 1609.34).toFixed(1);
            window.showDemoAlert(`Auto-Dispatching closest agent (${agentId.replace('SIM-VANGUARD-', 'VAN-')}) - ${milesAway}mi away<br>Waiting for Acceptance...`, 3500);

            setTimeout(() => {
                let didAccept = Math.random() > 0.10; 
                
                if (didAccept) {
                    agent.status.status = "BUSY_ON_WAY";
                    agent.status.currentFaultId = window.selectedFaultId;
                    fault.status = "ASSIGNED";
                    fault.assignedAgent = agentId;
                    fault.assignedAt = Date.now();
                    
                    let price = window.faultPrices[fault.errorCode] || 15.00;
                    fault.lockedPrice = price;
                    window.addLedgerEntry(-price, 'ESCROW_LOCK', `Escrow Locked: ${window.capNames[fault.errorCode]}`, fault.id, { errorCode: fault.errorCode });

                    fault.history.push({ time: Date.now(), event: 'ASSIGNED_MANUAL', agentId: agentId });

                    let p1 = new google.maps.LatLng(agent.status.latitude, agent.status.longitude);
                    let p2 = new google.maps.LatLng(fault.lat, fault.lon);

                    window.ds.route({ origin: p1, destination: p2, travelMode: 'DRIVING' }, (res, status) => {
                        if (status === 'OK') {
                            agent.route = res.routes[0].overview_path;
                            agent.routeIndex = 0;
                        } else {
                            agent.route = [];
                            for (let j = 0; j <= 20; j++) {
                                agent.route.push(google.maps.geometry.spherical.interpolate(p1, p2, j/20));
                            }
                            agent.routeIndex = 0;
                        }
                    });

                    window.selectedFaultId = null; 
                    window.showDemoAlert(`✅ Agent ${agentId.replace('SIM-VANGUARD-', 'VAN-')} Accepted!<br>En route to stranded AV.`, 3000);
                    window.mergeAndRender();
                } else {
                    agent.status.status = "ONLINE"; 
                    window.mergeAndRender();
                    window.showDemoAlert(`❌ Agent ${agentId.replace('SIM-VANGUARD-', 'VAN-')} declined or timed out.<br>Please re-deploy.`, 2500);
                }
            }, 3500);
        }
        return; 
    }

    if (uid.startsWith("SIM-")) { 
        if (!window.selectedFaultId || !window.simFaults[window.selectedFaultId]) {
            alert("DEMO MODE: First click a Cyan AV car on the map to target it.");
            return;
        }

        let agent = window.simAgents[uid];
        let fault = window.simFaults[window.selectedFaultId];

        if (agent.status.status !== "ONLINE") {
            alert("This agent is currently busy. Please select an ONLINE agent.");
            return;
        }

        agent.status.status = "PENDING";
        document.getElementById('disp-uid').value = ""; 
        
        window.mergeAndRender();
        window.showDemoAlert(`Targeting specific agent (${uid.replace('SIM-VANGUARD-', 'VAN-')})...<br>Waiting for Acceptance.`, 3500);

        setTimeout(() => {
            agent.status.status = "BUSY_ON_WAY";
            agent.status.currentFaultId = window.selectedFaultId;
            fault.status = "ASSIGNED";
            fault.assignedAgent = uid;
            fault.assignedAt = Date.now();
            
            let price = window.faultPrices[fault.errorCode] || 15.00;
            fault.lockedPrice = price;
            window.addLedgerEntry(-price, 'ESCROW_LOCK', `Escrow Locked: Targeted Dispatch`, fault.id, { errorCode: fault.errorCode });

            fault.history.push({ time: Date.now(), event: 'ASSIGNED_MANUAL_UID', agentId: uid });

            let p1 = new google.maps.LatLng(agent.status.latitude, agent.status.longitude);
            let p2 = new google.maps.LatLng(fault.lat, fault.lon);

            window.ds.route({ origin: p1, destination: p2, travelMode: 'DRIVING' }, (res, status) => {
                if (status === 'OK') {
                    agent.route = res.routes[0].overview_path;
                    agent.routeIndex = 0;
                } else {
                    agent.route = [];
                    for (let j = 0; j <= 20; j++) {
                        agent.route.push(google.maps.geometry.spherical.interpolate(p1, p2, j/20));
                    }
                    agent.routeIndex = 0;
                }
            });

            window.selectedFaultId = null; 
            window.showDemoAlert(`✅ Agent ${uid.replace('SIM-VANGUARD-', 'VAN-')} Accepted!<br>En route to stranded AV.`, 3000);
            window.mergeAndRender();
        }, 3500);

        return; 
    }

    const center = window.map.getCenter();
    const payload = {
        type: "MISSION", lat: Number(center.lat()), lon: Number(center.lng()),
        errorCode: String(document.getElementById('disp-error').value), bounty: String(document.getElementById('disp-bounty').value),
        intersection: String(document.getElementById('disp-loc').value), timestamp: Date.now()
    };
    
    window.firebaseSet(window.firebaseRef(window.firebaseDb, 'dispatch/' + window.escapeHTML(uid)), payload).then(() => {
        alert("MISSION DEPLOYED TO " + window.escapeHTML(uid).substring(0,8) + "...");
        document.getElementById('disp-uid').value = ""; 
    }).catch(error => { alert("SECURITY BLOCK: Dispatch failed."); });
};

window.spawnFault = function(forceAutoAssign = false, forceState = "BUSY_ON_WAY") {
    let healthyIds = Object.keys(window.healthyFleet || {});
    let lat, lon;

    if (healthyIds.length > 0) {
        let victimId = healthyIds[Math.floor(Math.random() * healthyIds.length)];
        let victimCar = window.healthyFleet[victimId];

        lat = victimCar.lat;
        lon = victimCar.lng;

        delete window.healthyFleet[victimId];
        if (window.healthyAVMarkers && window.healthyAVMarkers[victimId]) {
            window.healthyAVMarkers[victimId].setMap(null);
            delete window.healthyAVMarkers[victimId];
        }
    } else {
        lat = 33.37 + Math.random() * 0.09; 
        lon = -111.87 + Math.random() * 0.19;
    }

    const faultId = "FLT-" + Math.floor(Math.random() * 90000 + 10000);
    const capKeys = Object.keys(window.capNames);
    const errorCode = capKeys[Math.floor(Math.random() * capKeys.length)];

    const randomPastTime = Math.floor(Math.random() * 120000); 
    window.simFaults[faultId] = { 
        id: faultId, lat: lat, lon: lon, errorCode: errorCode, 
        status: "UNASSIGNED", assignedAgent: null, 
        timestamp: Date.now() - randomPastTime,
        history: [{ time: Date.now() - randomPastTime, event: 'CREATED' }]
    };

    if (forceAutoAssign) {
        let availableAgents = Object.keys(window.simAgents).filter(uid => {
            let a = window.simAgents[uid];
            return a.status.status === "ONLINE" && a.capabilities.includes(errorCode);
        });

        if (availableAgents.length > 0) {
            let uid = availableAgents[Math.floor(Math.random() * availableAgents.length)];
            let agent = window.simAgents[uid];
            
            agent.status.status = forceState;
            agent.status.currentFaultId = faultId;
            window.simFaults[faultId].status = "ASSIGNED";
            window.simFaults[faultId].assignedAgent = uid;
            window.simFaults[faultId].assignedAt = Date.now() - randomPastTime; 
            
            let price = window.faultPrices[errorCode] || 15.00;
            window.simFaults[faultId].lockedPrice = price;
            
            window.addLedgerEntry(-price, 'ESCROW_LOCK', `Escrow Locked: System Auto-Spawn`, faultId, { errorCode: errorCode });
            window.simFaults[faultId].history.push({ time: Date.now() - randomPastTime, event: 'ASSIGNED_SEED', agentId: uid });

            if (forceState === "BUSY_ON_SITE") {
                agent.status.latitude = lat;
                agent.status.longitude = lon;
            } else {
                let p1 = new google.maps.LatLng(agent.status.latitude, agent.status.longitude);
                let p2 = new google.maps.LatLng(lat, lon);

                window.ds.route({ origin: p1, destination: p2, travelMode: 'DRIVING' }, (res, status) => {
                    if (status === 'OK') {
                        agent.route = res.routes[0].overview_path;
                        agent.routeIndex = 0;
                    } else {
                        agent.route = [];
                        for (let j = 0; j <= 20; j++) {
                            agent.route.push(google.maps.geometry.spherical.interpolate(p1, p2, j/20));
                        }
                        agent.routeIndex = 0;
                    }
                });
            }
        }
    }
    window.mergeAndRender();
};

window.autoPilotSweep = function() {
    let unassignedFaults = Object.values(window.simFaults).filter(f => f.status === "UNASSIGNED" && (Date.now() - f.timestamp > 2000));
    if (unassignedFaults.length === 0) return;

    let handledAny = false;

    unassignedFaults.forEach(fault => {
        let qualifiedAgents = [];
        Object.keys(window.simAgents).forEach(agentId => {
            let a = window.simAgents[agentId];
            if (a.status.status === "ONLINE" && a.capabilities.includes(fault.errorCode)) {
                let agentPos = new google.maps.LatLng(a.status.latitude, a.status.longitude);
                let faultPos = new google.maps.LatLng(fault.lat, fault.lon);
                let dist = google.maps.geometry.spherical.computeDistanceBetween(faultPos, agentPos);
                qualifiedAgents.push({ id: agentId, agent: a, distance: dist });
            }
        });

        let target = window.getBestAgent(qualifiedAgents, new google.maps.LatLng(fault.lat, fault.lon), window.faultPrices[fault.errorCode] || 15.00);

        if (target) {
            let agent = target.agent;
            agent.status.status = "BUSY_ON_WAY";
            agent.status.currentFaultId = fault.id;
            fault.status = "ASSIGNED";
            fault.assignedAgent = target.id;
            fault.assignedAt = Date.now();

            let maxPrice = window.faultPrices[fault.errorCode] || 15.00;
            fault.lockedPrice = maxPrice;
            fault.history = fault.history || [];
            fault.history.push({ time: Date.now(), event: 'ASSIGNED_AUTOPILOT', agentId: target.id });

            window.addLedgerEntry(-maxPrice, 'ESCROW_LOCK', `Auto-Pilot Assigned: ${window.capNames[fault.errorCode]}`, fault.id, { errorCode: fault.errorCode });

            let p1 = new google.maps.LatLng(agent.status.latitude, agent.status.longitude);
            let p2 = new google.maps.LatLng(fault.lat, fault.lon);

            window.ds.route({ origin: p1, destination: p2, travelMode: 'DRIVING' }, (res, status) => {
                if (status === 'OK') {
                    agent.route = res.routes[0].overview_path;
                    agent.routeIndex = 0;
                } else {
                    agent.route = [p1, p2];
                    agent.routeIndex = 0;
                }
            });
            handledAny = true;
        }
    });
    if (handledAny) window.mergeAndRender();
};

window.continuousSimulationLoop = function() {
    let onWayCount = 0;
    let unassignedCount = 0;

    Object.values(window.simAgents).forEach(a => { 
        if (a.status.status === "BUSY_ON_WAY") onWayCount++; 
        
        if (a.status.status === "BUSY_ON_SITE") {
            if (Math.random() < 0.1) {
                a.status.status = "ONLINE";
                if (a.status.currentFaultId) {
                    let f = window.simFaults[a.status.currentFaultId];
                    if (f && !f.canceled) {
                        f.status = "RESOLVED";
                        f.resolvedAt = Date.now(); 
                        f.history.push({ time: Date.now(), event: 'COMPLETED' });
                        
                        let shortAgentId = f.assignedAgent ? f.assignedAgent.replace('SIM-VANGUARD-', 'VAN-') : 'Agent';
                        window.settleLedger(f.id, shortAgentId, f.errorCode, window.formatDuration(f.resolvedAt - f.timestamp));
                    }
                    a.status.currentFaultId = null;
                }
            }
        }
    });

    let unassignedFaults = [];
    Object.values(window.simFaults).forEach(f => { 
        if (f.status === "UNASSIGNED") {
            unassignedCount++; 
            unassignedFaults.push(f);
        }
        if (f.status === "RESOLVED" && (Date.now() - f.resolvedAt > 300000)) {
            delete window.simFaults[f.id]; 
        }
    });

    window.lastSpawnTime = window.lastSpawnTime || 0;
    let timeSinceLastSpawn = Date.now() - window.lastSpawnTime;
    let spawnCooldown = window.autoPilotActive ? 60000 : 0; 

    if (onWayCount < 2) window.spawnFault(true, "BUSY_ON_WAY");
    
    if (unassignedCount < 2 && timeSinceLastSpawn >= spawnCooldown) {
        window.spawnFault(false);
        window.lastSpawnTime = Date.now();
    }

    if (window.autoPilotActive) {
        window.autoPilotSweep();
    }
    
    window.mergeAndRender();
};

window.generateSimulatedAgents = function() {
    const tiers = [
        ['door_securing', 'cabin_sweep', 'lost_item', 'path_clearing'],
        ['spill_remediation', 'tire_pressure', 'battery_jump', 'passenger_escort'],
        ['sensor_cleaning', 'scene_securement', 'tire_replacement', 'manual_override']
    ];

    const locations = [
        { lat: 33.426, lon: -111.932, name: "ASU Stadium", mode: "FOOT" },
        { lat: 33.422, lon: -111.940, name: "Mill Ave", mode: "FOOT" },
        { lat: 33.492, lon: -111.926, name: "Old Town", mode: "FOOT" },
        { lat: 33.550, lon: -111.900, name: "McCormick Ranch", mode: "VEHICLE" },
        { lat: 33.352, lon: -111.789, name: "Downtown Gilbert", mode: "FOOT" },
        { lat: 33.308, lon: -111.743, name: "San Tan Village", mode: "VEHICLE" },
        { lat: 33.306, lon: -111.841, name: "Downtown Chandler", mode: "FOOT" },
        { lat: 33.432, lon: -111.865, name: "Mesa Riverview", mode: "VEHICLE" },
        { lat: 33.391, lon: -111.876, name: "MCC Campus", mode: "FOOT" },
        { lat: 33.385, lon: -111.683, name: "Superstition Springs", mode: "VEHICLE" },
        { lat: 33.481, lon: -111.683, name: "Las Sendas", mode: "VEHICLE" }
    ];

    for(let i = 0; i < 25; i++) {
        let lat, lon, mode, radius;
        
        if (i < 11) {
            lat = locations[i].lat; lon = locations[i].lon; mode = locations[i].mode;
        } else {
            lat = 33.37 + Math.random() * 0.09; lon = -111.87 + Math.random() * 0.19; mode = "VEHICLE"; 
        }

        radius = mode === "FOOT" ? (Math.random() * 0.5) + 0.5 : (Math.random() * 3.0) + 3.0; 

        let caps = [...tiers[0]]; 
        if (Math.random() > 0.3) caps.push(...tiers[1].filter(() => Math.random() > 0.4)); 
        if (i < 6 || Math.random() > 0.8) caps.push(...tiers[2]); 

        let costMultiplier = 0.7 + (Math.random() * 0.6);

        window.simAgents[`SIM-VANGUARD-${(i+1).toString().padStart(3, '0')}`] = {
            status: { status: "ONLINE", patrolMode: mode, latitude: lat, longitude: lon, radius: radius, timestamp: Date.now() },
            capabilities: caps,
            costMultiplier: costMultiplier
        };
    }

    // 🟢 SPAWN HEALTHY FLEET WITH MOCK HISTORY
    window.healthyFleet = {};
    
    // We need the fault types to pick random historical errors
    const capKeys = Object.keys(window.capNames || {
        'door_securing': 'Door Securing',
        'cabin_sweep': 'Cabin Sweep & Trash',
        'sensor_cleaning': 'Sensor Cleaning',
        'tire_pressure': 'Tire Pressure',
        'spill_remediation': 'Bio/Liquid Remediation'
    });

    for (let i = 0; i < 25; i++) {
        let id = "AV-ACT-" + Math.floor(Math.random() * 90000 + 10000);
        let startLat = 33.415 + (Math.random() - 0.5) * 0.12;
        let startLng = -111.831 + (Math.random() - 0.5) * 0.12;
        
        let randomErr = capKeys[Math.floor(Math.random() * capKeys.length)];
        let hoursAgo = Math.floor(Math.random() * 72) + 1; // 1 to 72 hours ago

        window.healthyFleet[id] = {
            id: id,
            lat: startLat,
            lng: startLng,
            targetLat: startLat + (Math.random() - 0.5) * 0.02,
            targetLng: startLng + (Math.random() - 0.5) * 0.02,
            speed: 0.0001 + (Math.random() * 0.0001),
            lastErrorCode: randomErr,
            lastErrorTime: hoursAgo
        };
    }

    window.spawnFault(true, "BUSY_ON_WAY"); 
    window.spawnFault(true, "BUSY_ON_WAY"); 
    window.spawnFault(true, "BUSY_ON_SITE"); 
    window.spawnFault(true, "BUSY_ON_SITE"); 
    window.spawnFault(false); 
    window.spawnFault(false);

    setInterval(window.animateAgents, 150);
    setInterval(window.continuousSimulationLoop, 4000);
};

window.animateAgents = function() {
    let needsUpdate = false;
    
    if (window.autoPilotActive && window.autoPilotEndTime) {
        let remaining = window.autoPilotEndTime - Date.now();
        if (remaining <= 0) {
            window.stopAutoDispatch('expired');
        } else {
            let h = Math.floor(remaining / 3600000);
            let m = Math.floor((remaining % 3600000) / 60000);
            let timeStr = "";
            if (h > 0) timeStr += `${h} HR `;
            timeStr += `${m} MIN`;
            document.getElementById('auto-pilot-timer').innerText = `REMAINING: ${timeStr}`;
        }
    }

    if (window.healthyFleet) {
        Object.keys(window.healthyFleet).forEach(avId => {
            let av = window.healthyFleet[avId];
            let latDist = av.targetLat - av.lat;
            let lngDist = av.targetLng - av.lng;
            
            if (Math.abs(latDist) > av.speed || Math.abs(lngDist) > av.speed) {
                let angle = Math.atan2(lngDist, latDist);
                av.lat += Math.cos(angle) * av.speed;
                av.lng += Math.sin(angle) * av.speed;
            } else {
                av.targetLat = av.lat + (Math.random() - 0.5) * 0.04;
                av.targetLng = av.lng + (Math.random() - 0.5) * 0.04;
            }
            needsUpdate = true;
        });
    }

    Object.keys(window.simAgents).forEach(uid => {
        let a = window.simAgents[uid];
        if (a.status.status === "BUSY_ON_WAY" && a.route && a.route.length > 0) {
            
            if (Math.random() < 0.0003) { 
                window.agentAbortsMission(uid, a.status.currentFaultId);
                return; 
            }

            let p1 = new google.maps.LatLng(a.status.latitude, a.status.longitude);
            let p2 = a.route[a.routeIndex];
            if (!p2) return;
            
            let dist = google.maps.geometry.spherical.computeDistanceBetween(p1, p2); 
            let speed = Math.random() < 0.1 ? 0 : 25; 
            
            if (dist <= speed) {
                a.status.latitude = p2.lat();
                a.status.longitude = p2.lng();
                a.routeIndex++;
                if (a.routeIndex >= a.route.length) {
                    a.status.status = "BUSY_ON_SITE"; 
                }
            } else {
                let heading = google.maps.geometry.spherical.computeHeading(p1, p2);
                let newPos = google.maps.geometry.spherical.computeOffset(p1, speed, heading);
                a.status.latitude = newPos.lat();
                a.status.longitude = newPos.lng();
            }
            needsUpdate = true;
        }
    });
    if (needsUpdate) window.mergeAndRender();

    document.querySelectorAll('.live-timer').forEach(timerEl => {
        let ts = parseInt(timerEl.getAttribute('data-timestamp'));
        timerEl.innerText = window.formatDuration(Date.now() - ts);
    });
};