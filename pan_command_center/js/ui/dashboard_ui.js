// pan_command_center/js/ui/dashboard_ui.js

window.setRoutingStrategy = function(strategy) {
    window.routingStrategy = strategy;
    localStorage.setItem('pan_routing_strategy', strategy);
    
    document.getElementById('route-btn-speed').classList.remove('active');
    document.getElementById('route-btn-balanced').classList.remove('active');
    document.getElementById('route-btn-cost').classList.remove('active');
    
    if (strategy === 'SPEED') document.getElementById('route-btn-speed').classList.add('active');
    if (strategy === 'BALANCED') document.getElementById('route-btn-balanced').classList.add('active');
    if (strategy === 'COST') document.getElementById('route-btn-cost').classList.add('active');
};

window.toggleSidebar = function() {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebar-toggle');
    sidebar.classList.toggle('collapsed');
    if (sidebar.classList.contains('collapsed')) {
        toggle.innerText = '▶';
        toggle.title = "Expand Sidebar";
    } else {
        toggle.innerText = '◀';
        toggle.title = "Collapse Sidebar";
    }
};

window.toggleLegend = function() {
    const content = document.getElementById('legend-content');
    const arrow = document.getElementById('legend-toggle-arrow');
    if (window.getComputedStyle(content).display === 'none') {
        content.style.display = 'block';
        arrow.innerText = '▼';
        localStorage.setItem('pan_legend_state', 'open');
    } else {
        content.style.display = 'none';
        arrow.innerText = '▲';
        localStorage.setItem('pan_legend_state', 'closed');
    }
};

window.toggleDispatchPanel = function() {
    const content = document.getElementById('dispatch-panel-content');
    const arrow = document.getElementById('dispatch-toggle-arrow');
    if (window.getComputedStyle(content).display === 'none') {
        content.style.display = 'block';
        arrow.innerText = '▼';
        localStorage.setItem('pan_dispatch_panel_state', 'open');
    } else {
        content.style.display = 'none';
        arrow.innerText = '▲';
        localStorage.setItem('pan_dispatch_panel_state', 'closed');
    }
};

window.showDemoAlert = function(msg, duration=4000) {
    const el = document.getElementById('demo-alert');
    el.innerHTML = msg; 
    el.style.display = 'block';
    
    if(window.demoAlertTimeout) clearTimeout(window.demoAlertTimeout);
    window.demoAlertTimeout = setTimeout(() => { el.style.display = 'none'; }, duration);
};

window.checkPremiumStatus = function() {
    const balEl = document.getElementById('wallet-balance-display');
    if (window.fleetBalance >= 25000) {
        balEl.classList.add('premium');
        balEl.title = "Premium Tier Activated (5% Platform Fee)";
    } else {
        balEl.classList.remove('premium');
        balEl.title = "Standard Tier (10% Platform Fee). Add funds to reach $25k for discount.";
    }
};

window.addLedgerEntry = function(amount, type, desc, refId, meta = {}) {
    window.fleetBalance += amount;
    document.getElementById('wallet-balance-display').innerText = window.formatMoney(window.fleetBalance);
    window.checkPremiumStatus();

    let txnId = 'TXN-' + Date.now().toString().slice(-6) + Math.floor(Math.random()*100);

    let entry = { time: Date.now(), refId: refId, type: type, desc: desc, amount: amount, balance: window.fleetBalance, txnId: txnId, meta: meta };
    window.fleetLedger.unshift(entry);

    let amtStr = amount > 0 ? `+${window.formatMoney(amount)}` : window.formatMoney(amount);
    if (amount === 0) amtStr = "$0.00";
    
    document.getElementById('wallet-ticker-display').innerText = `[${new Date().toLocaleTimeString()}] ${refId}: ${desc} (${amtStr})`;
    
    if (window.autoPilotActive && window.fleetBalance <= window.autoPilotLimit) {
        window.stopAutoDispatch('funds');
    }
};

window.settleLedger = function(refId, agentId, faultCode, timeElapsed) {
    let pendingIdx = window.fleetLedger.findIndex(i => i.refId === refId && i.type === 'ESCROW_LOCK');
    let lockedAmt = -(window.faultPrices[faultCode] || 15.00); 
    
    if (pendingIdx > -1) {
        lockedAmt = window.fleetLedger[pendingIdx].amount;
        window.fleetLedger.splice(pendingIdx, 1);
    }
    
    let agent = window.allAgents[agentId] || window.simAgents[agentId];
    let basePrice = window.faultPrices[faultCode] || 15.00;
    let bid = basePrice * (agent && agent.costMultiplier ? agent.costMultiplier : 1.0);
    
    let feePercent = window.fleetBalance >= 25000 ? 0.05 : 0.10;
    let panFee = bid * feePercent;
    let totalCost = bid + panFee;
    
    let refundDiff = Math.abs(lockedAmt) - totalCost;
    window.fleetBalance += refundDiff;
    
    let txnId = 'TXN-' + Date.now().toString().slice(-6) + Math.floor(Math.random()*100);
    let meta = { errorCode: faultCode, responseTime: timeElapsed, agentId: agentId, baseBid: bid, panFee: panFee };

    let desc = `Task Settled (${window.formatMoney(bid)} Agent Bid + ${window.formatMoney(panFee)} PAN Fee)`;
    let entry = { time: Date.now(), refId: refId, type: 'SETTLED', desc: desc, amount: -totalCost, balance: window.fleetBalance, txnId: txnId, meta: meta };
    window.fleetLedger.unshift(entry);
    
    document.getElementById('wallet-balance-display').innerText = window.formatMoney(window.fleetBalance);
    window.checkPremiumStatus();
    
    let tickerText = `[${new Date().toLocaleTimeString()}] ${refId}: Task Completed (${window.formatMoney(-totalCost)})`;
    document.getElementById('wallet-ticker-display').innerText = tickerText;
};

window.refundLedger = function(refId, totalLocked, feeAmount, reason, faultCode) {
    let pendingIdx = window.fleetLedger.findIndex(i => i.refId === refId && i.type === 'ESCROW_LOCK');
    if (pendingIdx > -1) {
        window.fleetLedger.splice(pendingIdx, 1);
    }
    
    window.fleetBalance += (totalLocked - feeAmount);
    document.getElementById('wallet-balance-display').innerText = window.formatMoney(window.fleetBalance);
    window.checkPremiumStatus();

    if (feeAmount > 0) {
        let txnId = 'TXN-' + Date.now().toString().slice(-6) + Math.floor(Math.random()*100);
        let meta = { errorCode: faultCode };
        let entry = { time: Date.now(), refId: refId, type: 'CANCEL_FEE', desc: reason || `Cancellation Fee`, amount: -feeAmount, balance: window.fleetBalance, txnId: txnId, meta: meta };
        window.fleetLedger.unshift(entry);
        document.getElementById('wallet-ticker-display').innerText = `[${new Date().toLocaleTimeString()}] ${refId}: ${entry.desc} (${window.formatMoney(-feeAmount)})`;
    } else {
        document.getElementById('wallet-ticker-display').innerText = `[${new Date().toLocaleTimeString()}] ${refId}: Pending Escrow Released ($0 Fee)`;
    }
};

window.toggleLedgerDetail = function(element) {
    element.closest('.ledger-item-container').classList.toggle('expanded');
};

window.openLedgerModal = function() {
    const listEl = document.getElementById('ledger-list');
    listEl.innerHTML = '';

    window.fleetLedger.forEach(item => {
        let timeStr = new Date(item.time).toLocaleTimeString();
        let amtClass = item.amount > 0 ? 'refund' : (item.amount < 0 ? 'deduct' : 'zero');
        let amtStr = item.amount > 0 ? `+${window.formatMoney(item.amount)}` : window.formatMoney(item.amount);
        if (item.amount === 0) amtStr = "$0.00";
        
        let metaHtml = '';
        if (item.meta && Object.keys(item.meta).length > 0) {
            if (item.meta.errorCode) metaHtml += `<br><strong style="color:#00BCD4;">FAULT:</strong> ${window.capNames[item.meta.errorCode].toUpperCase()} `;
            if (item.meta.agentId) metaHtml += `&nbsp;|&nbsp; <strong style="color:#FF9800;">AGENT:</strong> ${window.escapeHTML(item.meta.agentId.replace('SIM-VANGUARD-', 'VAN-'))} `;
            if (item.meta.responseTime) metaHtml += `&nbsp;|&nbsp; <strong style="color:#4CAF50;">SLA TIME:</strong> ${item.meta.responseTime} `;
            if (item.meta.baseBid) metaHtml += `<br><strong style="color:#aaa;">AGENT BID:</strong> ${window.formatMoney(item.meta.baseBid)} &nbsp;|&nbsp; <strong style="color:#aaa;">PAN FEE:</strong> ${window.formatMoney(item.meta.panFee)}`;
        }

        listEl.innerHTML += `
            <div class="ledger-item-container">
                <div class="ledger-row" onclick="window.toggleLedgerDetail(this)">
                    <span class="l-time">${timeStr}</span>
                    <span class="l-ref">${item.refId}</span>
                    <span class="l-desc">${item.desc}</span>
                    <span class="l-amt ${amtClass}">${amtStr}</span>
                    <span class="l-bal">${window.formatMoney(item.balance)}</span>
                </div>
                <div class="ledger-detail">
                    <strong style="color:#fff;">TXN ID:</strong> ${item.txnId} &nbsp;|&nbsp; 
                    <strong>EVENT TYPE:</strong> ${item.type}
                    ${metaHtml}
                </div>
            </div>
        `;
    });

    if(window.fleetLedger.length === 0) {
        listEl.innerHTML = `<div style="padding: 20px; text-align: center; color: #666; font-family: monospace;">No transactions found for this session.</div>`;
    }
    document.getElementById('ledger-modal').style.display = 'flex';
};

window.closeLedgerModal = function(e) { 
    if(e && e.target !== document.getElementById('ledger-modal') && e.target.className !== 'btn-cancel') return;
    document.getElementById('ledger-modal').style.display = 'none'; 
};

window.exportLedger = function(format) {
    let sDate = document.getElementById('export-start').value;
    let eDate = document.getElementById('export-end').value;
    
    if(format === 'csv') {
        let csvContent = "data:text/csv;charset=utf-8,Transaction ID,Time,Reference ID,Event Type,Description,Amount,Balance\n";
        window.fleetLedger.forEach(row => {
            let rTime = new Date(row.time).toLocaleString();
            csvContent += `"${row.txnId}","${rTime}","${row.refId}","${row.type}","${row.desc}","${row.amount.toFixed(2)}","${row.balance.toFixed(2)}"\n`;
        });
        
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `PAN_Ledger_${sDate}_to_${eDate}.csv`);
        document.body.appendChild(link); 
        link.click();
        document.body.removeChild(link);
        window.showDemoAlert(`✅ Excel CSV export complete.`, 3000);
    } else {
        window.showDemoAlert(`📄 Generating secure PDF report for ${sDate} to ${eDate}...`, 4000);
        setTimeout(() => window.showDemoAlert(`✅ PDF downloaded successfully.`, 3000), 2500);
    }
};

window.openDepositModal = function() { document.getElementById('deposit-modal').style.display = 'flex'; };
window.closeDepositModal = function() { document.getElementById('deposit-modal').style.display = 'none'; };
window.executeDeposit = function() {
    let amt = parseFloat(document.getElementById('deposit-input').value);
    if(isNaN(amt) || amt <= 0) return;
    
    window.closeDepositModal();
    window.showDemoAlert("⏳ Establishing secure connection via Plaid API...", 2500);
    
    setTimeout(() => {
        window.addLedgerEntry(amt, 'DEPOSIT', 'ACH Transfer - Retainer Replenished', 'DEP-' + Math.floor(Math.random()*9000+1000));
        window.showDemoAlert(`✅ $${amt.toFixed(2)} ACH Transfer Successful.<br>Funds instantly available.`, 3000);
    }, 2500);
};

window.openAutoDispatchModal = function() { document.getElementById('auto-dispatch-modal').style.display = 'flex'; };
window.closeAutoDispatchModal = function() { document.getElementById('auto-dispatch-modal').style.display = 'none'; };
window.executeAutoDispatch = function() {
    window.autoPilotActive = true;
    window.autoPilotLimit = parseFloat(document.getElementById('auto-limit-input').value) || 0;
    
    let durationHours = parseFloat(document.getElementById('auto-duration-select').value);
    if (durationHours === 999) {
        window.autoPilotEndTime = null; 
        document.getElementById('auto-pilot-timer').innerText = `REMAINING: UNTIL FUNDS DEPLETED`;
    } else {
        window.autoPilotEndTime = Date.now() + (durationHours * 60 * 60 * 1000);
    }

    document.getElementById('deploy-all-wrapper').style.display = 'none';
    document.getElementById('auto-active-banner').style.display = 'flex';
    window.closeAutoDispatchModal();
    window.showDemoAlert(`🟢 AUTO-PILOT ACTIVATED.<br>Routing set to ${window.routingStrategy} mode.`, 4000);
};

window.stopAutoDispatch = function(reason = 'manual') {
    window.autoPilotActive = false;
    window.autoPilotEndTime = null;
    document.getElementById('deploy-all-wrapper').style.display = 'flex';
    document.getElementById('auto-active-banner').style.display = 'none';
    if (reason === 'funds') {
        window.showDemoAlert("🔴 AUTO-PILOT SUSPENDED.<br>Retainer balance dropped below designated minimum limit.", 6000);
    } else if (reason === 'expired') {
        window.showDemoAlert("🛑 AUTO-PILOT COMPLETED.<br>Time duration expired. Returning to manual control.", 5000);
    } else {
        window.showDemoAlert("🛑 AUTO-PILOT DEACTIVATED.<br>Returning to manual control.", 3000);
    }
};

window.openDispatchModal = function(faultId = null) {
    window.dispatchTargetId = faultId;
    const modalList = document.getElementById('modal-list');
    const titleEl = document.getElementById('dispatch-modal-title');
    modalList.innerHTML = '';
    let totalCost = 0;
    let count = 0;

    Object.values(window.simFaults).forEach(f => {
        if (f.status === "UNASSIGNED") {
            if (faultId && f.id !== faultId) return; 
            
            count++;
            let price = window.faultPrices[f.errorCode] || 15.00;
            totalCost += price;
            
            modalList.innerHTML += `
                <div class="modal-row">
                    <span class="fid">${f.id}</span>
                    <span class="fcode">${window.capNames[f.errorCode].toUpperCase()}</span>
                    <span class="fprice">$${price.toFixed(2)}</span>
                </div>
            `;
        }
    });

    if (count > 0) {
        titleEl.innerText = faultId ? "QUICK DISPATCH ESCROW" : "MASS DISPATCH ESCROW";
        document.getElementById('modal-total-val').innerText = `$${totalCost.toFixed(2)}`;
        document.getElementById('dispatch-modal').style.display = 'flex';
    }
};

window.closeDispatchModal = function() {
    window.dispatchTargetId = null;
    document.getElementById('dispatch-modal').style.display = 'none';
};

window.openCancelModal = function(faultId) {
    let f = window.simFaults[faultId];
    if (!f || f.status !== "ASSIGNED") return;
    window.faultToCancel = faultId;
    let agentId = f.assignedAgent.replace('SIM-VANGUARD-', 'VAN-');
    let errCodeName = window.capNames[f.errorCode].toUpperCase();
    
    let text = `Are you sure you want to cancel the dispatch for error code <strong>${errCodeName}</strong> on vehicle <strong>${f.id}</strong> assigned to agent <strong>${agentId}</strong>?<br><br><i style="color:#FF9800;">Note: A $5.00 cancellation fee is applied against escrow if the agent has been responding for more than 1 minute. The vehicle will be returned to the Unassigned queue.</i>`;
    
    document.getElementById('cancel-modal-text').innerHTML = text;
    document.getElementById('cancel-dispatch-modal').style.display = 'flex';
};

window.closeCancelModal = function() {
    window.faultToCancel = null;
    document.getElementById('cancel-dispatch-modal').style.display = 'none';
};

window.updateBounty = function() {
    const sel = document.getElementById('disp-error');
    const bounty = sel.options[sel.selectedIndex].getAttribute('data-bounty');
    document.getElementById('disp-bounty').value = bounty;
};

// 🟢 RESTORED: Map Selection Cleanup
window.clearSelection = function() {
    if (window.infoWindow) window.infoWindow.close();
    window.selectedFaultId = null;
    window.dispatchTargetId = null;
    
    let uidBox = document.getElementById('disp-uid');
    if(uidBox) uidBox.value = "";
    let locBox = document.getElementById('disp-loc');
    if(locBox) locBox.value = "Awaiting Selection...";
    
    if (window.selectedFaultCircle) {
        window.selectedFaultCircle.setMap(null);
        window.selectedFaultCircle = null;
    }
    
    // Only re-render if we aren't actively in DVR Replay mode
    if (window.mergeAndRender && !window.isReplayMode) {
        window.mergeAndRender();
    }
};