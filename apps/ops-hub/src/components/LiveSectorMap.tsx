import React, { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerIcon2x,
    shadowUrl: markerShadow,
});

// PAN Custom Markers
const createPulseIcon = (color: string) => L.divIcon({
    className: 'custom-div-icon',
    html: `<div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #fff; box-shadow: 0 0 10px ${color};"></div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9]
});

const agentIconOnline = createPulseIcon('#00BCD4'); // Cyan
const agentIconEnRoute = createPulseIcon('#FF9800'); // Orange
const agentIconOnScene = createPulseIcon('#FFEB3B'); // Yellow
const agentIconOffline = createPulseIcon('#555555'); // Grey

const distressIconOK = createPulseIcon('#F44336'); // Red
const distressIconWarning = createPulseIcon('#E91E63'); // Pink/Warning
const distressIconBreach = createPulseIcon('#9C27B0'); // Purple/Breach

const getDistressIcon = (status?: 'OK' | 'WARNING' | 'BREACH') => {
    if (status === 'BREACH') return distressIconBreach;
    if (status === 'WARNING') return distressIconWarning;
    return distressIconOK;
};

const MESA_CENTER: [number, number] = [33.415184, -111.831459];
const WS_URL = (import.meta as any).env?.VITE_TELEMETRY_WS_URL ?? 'ws://127.0.0.1:5000/api/v1/telemetry/stream?token=dev-token-777';

interface AgentTelemetry {
    agent_id: string;
    lat: number;
    lon: number;
    status: 'ONLINE' | 'EN_ROUTE' | 'ON_SCENE' | 'OFFLINE';
    heading: number; 
    // TODO: OSRM route streaming pending Phase 5 backend update
    remaining_route?: [number, number][];
}

interface DistressSignal {
    task_id: string;
    vin: string;
    fault_code: string;
    lat: number;
    lon: number;
    bounty_usd: number;
    sla_status?: 'OK' | 'WARNING' | 'BREACH';
}

export const LiveSectorMap: React.FC = () => {
    // Core State
    const [agents, setAgents] = useState<Map<string, AgentTelemetry>>(new Map());
    const [distressSignals, setDistressSignals] = useState<Map<string, DistressSignal>>(new Map());
    const [connectionStatus, setConnectionStatus] = useState<'CONNECTING' | 'LIVE' | 'DISCONNECTED'>('CONNECTING');
    
    // Ops Hub UI State
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [showLegend, setShowLegend] = useState(true);
    
    // 🟢 THE FIX 1: Zeroed out the cosmetic balance. Needs real LND wiring.
    const [fleetBalance, setFleetBalance] = useState(0.00);
    
    // 🟢 THE FIX 2: Locked to SPEED since matching_engine.py only uses OSRM fastest route.
    const [routingStrategy, setRoutingStrategy] = useState<'SPEED' | 'BALANCED' | 'COST'>('SPEED');
    const [pendingDispatch, setPendingDispatch] = useState<DistressSignal | null>(null);
    const [autoPilotActive, setAutoPilotActive] = useState(false);

    // Filters
    const [filters, setFilters] = useState({ showOnline: true, showEnRoute: true, showOnScene: true });
    
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

    const mapCallbackRef = useCallback((map: L.Map | null) => {
        if (map) setTimeout(() => map.invalidateSize(), 300);
    }, [sidebarCollapsed]);

    const connectWebSocket = useCallback(() => {
        if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
            return;
        }

        setConnectionStatus('CONNECTING');
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
            setConnectionStatus('LIVE');
            if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
        };

        ws.onmessage = (event: MessageEvent) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'AGENT_LOCATION') {
                    setAgents(prev => new Map(prev).set(data.payload.agent_id, data.payload));
                } else if (data.type === 'DISTRESS_ALERT') {
                    setDistressSignals(prev => new Map(prev).set(data.payload.task_id, { ...data.payload, sla_status: 'OK' }));
                } else if (data.type === 'MISSION_CLEARED') {
                    setDistressSignals(prev => {
                        const next = new Map(prev);
                        next.delete(data.payload.task_id);
                        return next;
                    });
                } else if (data.type === 'SLA_WARNING' || data.type === 'SLA_BREACH') {
                    setDistressSignals(prev => {
                        const next = new Map(prev);
                        const taskId = data.payload.mission_id;
                        const signal = next.get(taskId);
                        if (signal) {
                            next.set(taskId, { ...signal, sla_status: data.type === 'SLA_BREACH' ? 'BREACH' : 'WARNING' });
                        }
                        return next;
                    });
                }
            } catch (err) { console.error("Telemetry parse error:", err); }
        };

        ws.onclose = () => {
            setConnectionStatus('DISCONNECTED');
            wsRef.current = null;
            reconnectTimeout.current = setTimeout(connectWebSocket, 3000);
        };
    }, []);

    useEffect(() => {
        connectWebSocket();
        return () => {
            wsRef.current?.close();
            if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
        };
    }, [connectWebSocket]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => { if (e.key === 'Escape') setPendingDispatch(null); };
        if (pendingDispatch) window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [pendingDispatch]);

    const executeDispatch = () => {
        if (!pendingDispatch || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

        const payload = {
            action: 'DISPATCH_AGENT',
            payload: { task_id: pendingDispatch.task_id, routing_strategy: routingStrategy, lat: pendingDispatch.lat, lon: pendingDispatch.lon }
        };

        wsRef.current.send(JSON.stringify(payload));
        
        // Optimistic UI update for escrow (Displays negative until wallet is synced)
        setFleetBalance(prev => prev - pendingDispatch.bounty_usd);
        setPendingDispatch(null);
    };

    // Filtered Agents
    const visibleAgents = useMemo(() => {
        return Array.from(agents.values()).filter(a => {
            if (a.status === 'ONLINE' && !filters.showOnline) return false;
            if (a.status === 'EN_ROUTE' && !filters.showEnRoute) return false;
            if (a.status === 'ON_SCENE' && !filters.showOnScene) return false;
            return true;
        });
    }, [agents, filters]);

    const formatMoney = (num: number) => {
        const isNeg = num < 0;
        const str = '$' + Math.abs(num).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
        return isNeg ? '-' + str : str;
    };

    return (
        <div style={{ display: 'flex', height: '100vh', width: '100vw', backgroundColor: '#121212', color: '#fff', fontFamily: '"Courier New", Courier, monospace', overflow: 'hidden' }}>
            
            <style>
                {`
                body, html { margin: 0; padding: 0; overflow: hidden; color-scheme: dark; }
                .btn-routing { flex: 1; background: #222; color: #888; border: none; padding: 8px 0; font-size: 11px; font-family: monospace; font-weight: bold; cursor: pointer; transition: 0.2s; border-right: 1px solid #444; }
                .btn-routing.active { background: #00BCD4; color: #000; }
                .btn-routing:disabled { background: #1a1a1a; color: #555; cursor: not-allowed; }
                .fault-card { background-color: #000; border: 2px solid transparent; border-radius: 8px; padding: 15px; cursor: pointer; transition: 0.2s ease; margin-bottom: 15px; }
                .fault-card:hover { border-color: #00BCD4; box-shadow: 0 0 10px rgba(0, 188, 212, 0.2); }
                .sidebar { transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1); flex-shrink: 0; }
                .sidebar.collapsed { margin-left: -380px; }
                .legend-item input { margin-right: 10px; cursor: pointer; }
                `}
            </style>

            {/* SIDEBAR */}
            <div className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`} style={{ width: '380px', backgroundColor: '#1E1E1E', borderRight: '2px solid #00BCD4', display: 'flex', flexDirection: 'column', zIndex: 10, position: 'relative' }}>
                <div onClick={() => setSidebarCollapsed(!sidebarCollapsed)} style={{ position: 'absolute', right: '-30px', top: '15px', width: '30px', height: '45px', background: '#1E1E1E', border: '2px solid #00BCD4', borderLeft: 'none', color: '#00BCD4', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', borderRadius: '0 6px 6px 0', zIndex: 2000 }}>
                    {sidebarCollapsed ? '▶' : '◀'}
                </div>

                <div style={{ padding: '20px', backgroundColor: '#000', borderBottom: '1px solid #333' }}>
                    <h1 style={{ margin: 0, color: '#00BCD4', fontSize: '24px', fontWeight: 900, letterSpacing: '2px' }}>PAN COMMAND</h1>
                    <p style={{ margin: '5px 0 0 0', color: connectionStatus === 'LIVE' ? '#4CAF50' : '#F44336', fontSize: '12px', fontWeight: 'bold' }}>
                        {connectionStatus === 'LIVE' ? '🟢 SATELLITE UPLINK ACTIVE' : '🔴 OFFLINE'}
                    </p>
                </div>

                {/* FLEET WALLET */}
                <div style={{ backgroundColor: '#111', borderBottom: '1px solid #333', padding: '15px 20px' }}>
                    <div style={{ fontSize: '10px', color: '#F44336', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 'bold' }}>
                        FLEET RETAINER BALANCE (WALLET OFFLINE)
                    </div>
                    {/* 🟢 THE FIX 1: Displaying offline state */}
                    <div style={{ fontSize: '28px', fontWeight: 900, color: '#888', margin: '2px 0', letterSpacing: '1px' }}>
                        {formatMoney(fleetBalance)}
                    </div>
                </div>

                {/* ROUTING MODULE */}
                <div style={{ padding: '15px 20px', background: '#1E1E1E', borderBottom: '1px solid #333' }}>
                    <span style={{ fontSize: '10px', color: '#888', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>ROUTING ALGORITHM:</span>
                    <div style={{ display: 'flex', border: '1px solid #444', borderRadius: '4px', overflow: 'hidden' }}>
                        <button className={`btn-routing ${routingStrategy === 'SPEED' ? 'active' : ''}`} onClick={() => setRoutingStrategy('SPEED')}>⚡ FASTEST</button>
                        {/* 🟢 THE FIX 2: Visually disabled placebo buttons until backend support is added */}
                        <button className="btn-routing" disabled title="Requires Phase 5 Backend Update">⚖️ BALANCED</button>
                        <button className="btn-routing" disabled title="Requires Phase 5 Backend Update">💰 LOWEST COST</button>
                    </div>
                </div>

                {/* AUTO PILOT TOGGLE */}
                <div style={{ padding: '15px 20px', display: 'flex', gap: '10px' }}>
                    <button onClick={() => setAutoPilotActive(!autoPilotActive)} style={{ flex: 1, padding: '12px', fontWeight: 'bold', cursor: 'pointer', borderRadius: '4px', fontFamily: 'monospace', fontSize: '12px', transition: '0.2s', background: autoPilotActive ? '#4CAF50' : 'rgba(76, 175, 80, 0.1)', color: autoPilotActive ? '#000' : '#4CAF50', border: '2px solid #4CAF50' }}>
                        {autoPilotActive ? '🟢 AUTO-PILOT ACTIVE' : 'AUTO-PILOT OFF'}
                    </button>
                </div>

                {/* FAULT LIST */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '0 20px 20px 20px' }}>
                    {distressSignals.size === 0 ? (
                        <p style={{ textAlign: 'center', color: '#666', fontSize: '12px', marginTop: '20px' }}>AWAITING SATELLITE UPLINK...</p>
                    ) : (
                        Array.from(distressSignals.values()).map(signal => (
                            <div key={signal.task_id} className="fault-card" style={{ borderColor: signal.sla_status === 'BREACH' ? '#F44336' : '#333' }}>
                                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', letterSpacing: '0.5px', color: signal.sla_status === 'BREACH' ? '#F44336' : '#fff' }}>
                                    {signal.sla_status === 'BREACH' ? '🚨 SLA BREACH ' : ''}{signal.task_id.substring(0, 12)}...
                                </h4>
                                <div style={{ color: '#00BCD4', fontSize: '12px', marginBottom: '12px', fontWeight: 'bold' }}>CODE: {signal.fault_code.toUpperCase()}</div>
                                <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#4CAF50' }}>BOUNTY: ${signal.bounty_usd.toFixed(2)}</div>
                                
                                <div style={{ display: 'flex', gap: '10px', marginTop: '12px' }}>
                                    <button onClick={() => setPendingDispatch(signal)} style={{ flex: 1, padding: '8px', background: 'transparent', border: '1px solid #00BCD4', color: '#00BCD4', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>DEPLOY AGENT</button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* MAP AREA */}
            <div style={{ flex: 1, position: 'relative', display: 'flex' }}>
                {/* MAP LEGEND */}
                <div style={{ position: 'absolute', top: '20px', right: '20px', background: 'rgba(18, 18, 18, 0.9)', border: '1px solid #333', borderRadius: '6px', padding: '15px', boxShadow: '0 4px 15px rgba(0,0,0,0.5)', zIndex: 1000, minWidth: '220px' }}>
                    <div onClick={() => setShowLegend(!showLegend)} style={{ display: 'flex', justifyContent: 'space-between', cursor: 'pointer', borderBottom: '1px solid #444', paddingBottom: '10px', marginBottom: '10px' }}>
                        <h4 style={{ margin: 0, fontSize: '12px', letterSpacing: '1px' }}>LIVE MAP FILTERS</h4>
                        <span>{showLegend ? '▼' : '▲'}</span>
                    </div>
                    {showLegend && (
                        <div style={{ fontSize: '12px', color: '#ccc' }}>
                            <label className="legend-item" style={{ display: 'block', margin: '8px 0' }}><input type="checkbox" checked={filters.showOnline} onChange={(e) => setFilters({...filters, showOnline: e.target.checked})} /> <span style={{ color: '#00BCD4' }}>●</span> Online Agents</label>
                            <label className="legend-item" style={{ display: 'block', margin: '8px 0' }}><input type="checkbox" checked={filters.showEnRoute} onChange={(e) => setFilters({...filters, showEnRoute: e.target.checked})} /> <span style={{ color: '#FF9800' }}>●</span> Agents En Route</label>
                            <label className="legend-item" style={{ display: 'block', margin: '8px 0' }}><input type="checkbox" checked={filters.showOnScene} onChange={(e) => setFilters({...filters, showOnScene: e.target.checked})} /> <span style={{ color: '#FFEB3B' }}>●</span> Agents On Scene</label>
                            <hr style={{ borderColor: '#333', margin: '10px 0' }}/>
                            <div style={{ margin: '8px 0' }}><span style={{ color: '#F44336' }}>●</span> Active Distress Signal</div>
                            <div style={{ margin: '8px 0' }}><span style={{ color: '#9C27B0' }}>●</span> SLA Breach Fault</div>
                        </div>
                    )}
                </div>

                <MapContainer center={MESA_CENTER} zoom={12} style={{ height: '100%', width: '100%', zIndex: 1 }} ref={mapCallbackRef}>
                    <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" attribution='&copy; CARTO' />

                    {/* Render Distress Signals */}
                    {Array.from(distressSignals.values()).map(signal => (
                        <Marker key={`distress-${signal.task_id}`} position={[signal.lat, signal.lon]} icon={getDistressIcon(signal.sla_status)}>
                            <Popup>
                                <strong>VIN: {signal.vin}</strong><br/>
                                Fault: {signal.fault_code}<br/>
                                Bounty: ${signal.bounty_usd}<br/>
                                SLA Status: {signal.sla_status || 'OK'}
                            </Popup>
                        </Marker>
                    ))}
                    
                    {/* Render Filtered Agents */}
                    {visibleAgents.map(agent => {
                        let icon = agentIconOnline;
                        if (agent.status === 'EN_ROUTE') icon = agentIconEnRoute;
                        else if (agent.status === 'ON_SCENE') icon = agentIconOnScene;
                        else if (agent.status === 'OFFLINE') icon = agentIconOffline;

                        return (
                            <React.Fragment key={`agent-group-${agent.agent_id}`}>
                                <Marker position={[agent.lat, agent.lon]} icon={icon}>
                                    <Popup><strong>{agent.agent_id}</strong><br/>Status: {agent.status}</Popup>
                                </Marker>
                                
                                {/* 🟢 THE FIX 3: Defensive render for future OSRM streaming integration */}
                                {agent.status === 'EN_ROUTE' && agent.remaining_route && agent.remaining_route.length > 0 && (
                                    <Polyline positions={agent.remaining_route} color="#FF9800" dashArray="8, 8" weight={3} opacity={0.8} />
                                )}
                            </React.Fragment>
                        );
                    })}
                </MapContainer>
            </div>

            {/* DISPATCH MODAL OVERLAY */}
            {pendingDispatch && (
                <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.85)', zIndex: 3000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(4px)' }}>
                    <div style={{ background: '#121212', border: '2px solid #00BCD4', borderRadius: '8px', padding: '30px', width: '500px', boxShadow: '0 10px 40px rgba(0, 188, 212, 0.4)' }}>
                        <h2 style={{ margin: '0 0 20px 0', color: '#00BCD4', textAlign: 'center', letterSpacing: '1px' }}>DISPATCH ESCROW</h2>
                        
                        <div style={{ background: '#000', border: '1px solid #333', padding: '15px', borderRadius: '4px', marginBottom: '20px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px', color: '#ccc', fontSize: '14px' }}>
                                <span>TARGET ASSET:</span> <span style={{ color: '#fff', fontWeight: 'bold' }}>{pendingDispatch.vin}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#ccc', fontSize: '14px' }}>
                                <span>FAULT DETECTED:</span> <span style={{ color: '#00BCD4', fontWeight: 'bold' }}>{pendingDispatch.fault_code}</span>
                            </div>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1A1A1A', padding: '15px', borderRadius: '4px', marginBottom: '25px', border: '1px solid #4CAF50' }}>
                            <span style={{ fontSize: '16px', fontWeight: 'bold', color: '#fff' }}>MAX AUTHORIZATION:</span>
                            <span style={{ fontSize: '24px', fontWeight: 900, color: '#4CAF50' }}>${pendingDispatch.bounty_usd.toFixed(2)}</span>
                        </div>

                        <div style={{ display: 'flex', gap: '15px' }}>
                            <button onClick={executeDispatch} style={{ flex: 2, background: '#00BCD4', color: '#000', fontSize: '16px', border: 'none', cursor: 'pointer', borderRadius: '4px', fontWeight: 'bold', padding: '12px' }}>
                                AUTHORIZE & DEPLOY
                            </button>
                            <button onClick={() => setPendingDispatch(null)} style={{ flex: 1, background: '#333', color: '#fff', border: 'none', cursor: 'pointer', borderRadius: '4px', fontWeight: 'bold', padding: '12px' }}>
                                CANCEL
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};