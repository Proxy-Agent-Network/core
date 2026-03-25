import React, { useEffect, useState, useRef, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerIcon2x,
    shadowUrl: markerShadow,
});

const agentIcon = new L.Icon({
    iconUrl: '/assets/azure-dot.svg',
    iconSize: [20, 20],
});

const distressIcon = new L.Icon({
    iconUrl: '/assets/red-alert.svg',
    iconSize: [30, 30],
});

const MESA_CENTER: [number, number] = [33.415184, -111.831459];

// 🛠️ THE FIX: Appended the token to pass the new auth gate
const WS_URL = 'ws://127.0.0.1:8000/api/v1/telemetry/stream?token=dev-token-777';

interface AgentTelemetry {
    agent_id: string;
    lat: number;
    lon: number;
    status: 'ONLINE' | 'EN_ROUTE' | 'ON_SCENE' | 'OFFLINE';
    heading: number; 
}

interface DistressSignal {
    task_id: string;
    vin: string;
    fault_code: string;
    lat: number;
    lon: number;
    bounty_usd: number;
}

export const LiveSectorMap: React.FC = () => {
    const [agents, setAgents] = useState<Map<string, AgentTelemetry>>(new Map());
    const [distressSignals, setDistressSignals] = useState<Map<string, DistressSignal>>(new Map());
    const [connectionStatus, setConnectionStatus] = useState<'CONNECTING' | 'LIVE' | 'DISCONNECTED'>('CONNECTING');
    
    // 🛠️ NEW: State for the V1 Escrow Modal
    const [pendingDispatch, setPendingDispatch] = useState<DistressSignal | null>(null);
    
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

    const connectWebSocket = useCallback(() => {
        setConnectionStatus('CONNECTING');
        wsRef.current = new WebSocket(WS_URL);

        wsRef.current.onopen = () => {
            setConnectionStatus('LIVE');
            if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
        };

        wsRef.current.onmessage = (event: MessageEvent) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === 'AGENT_LOCATION') {
                    setAgents(prev => {
                        const next = new Map(prev);
                        next.set(data.payload.agent_id, data.payload);
                        return next;
                    });
                } else if (data.type === 'DISTRESS_ALERT') {
                    setDistressSignals(prev => {
                        const next = new Map(prev);
                        next.set(data.payload.task_id, data.payload);
                        return next;
                    });
                } else if (data.type === 'MISSION_CLEARED') {
                    setDistressSignals(prev => {
                        const next = new Map(prev);
                        next.delete(data.payload.task_id);
                        return next;
                    });
                }
            } catch (err) {
                console.error("Failed to parse telemetry frame:", err);
            }
        };

        wsRef.current.onclose = () => {
            setConnectionStatus('DISCONNECTED');
            reconnectTimeout.current = setTimeout(connectWebSocket, 3000);
        };
    }, []);

    useEffect(() => {
        connectWebSocket();
        return () => {
            if (wsRef.current) wsRef.current.close();
            if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
        };
    }, [connectWebSocket]);

    // 🛠️ NEW: Function to send the dispatch command back to Python
    const executeDispatch = () => {
        if (!pendingDispatch || !wsRef.current) return;

        const payload = {
            action: 'DISPATCH_AGENT',
            payload: {
                task_id: pendingDispatch.task_id,
                routing_strategy: 'BALANCED' // Ported from V1 routing algorithm
            }
        };

        wsRef.current.send(JSON.stringify(payload));
        console.log(`🚀 [DISPATCH] Authorized agent deployment for ${pendingDispatch.task_id}`);
        
        // Optimistically remove from UI and close modal
        setDistressSignals(prev => {
            const next = new Map(prev);
            next.delete(pendingDispatch.task_id);
            return next;
        });
        setPendingDispatch(null);
    };

    return (
        <div style={{ display: 'flex', height: '100vh', width: '100vw', backgroundColor: '#121212', color: 'white', fontFamily: 'sans-serif' }}>
            
            {/* Sidebar */}
            <div style={{ width: '320px', borderRight: '1px solid #333', display: 'flex', flexDirection: 'column', backgroundColor: '#000', zIndex: 10 }}>
                <div style={{ padding: '24px', borderBottom: '1px solid #333' }}>
                    <h1 style={{ fontSize: '1.25rem', fontWeight: 900, letterSpacing: '0.1em', color: '#00BCD4', margin: 0 }}>PAN COMMAND</h1>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
                        <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: connectionStatus === 'LIVE' ? '#22c55e' : '#ef4444' }} />
                        <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: '#9ca3af' }}>SECTOR 1: {connectionStatus}</span>
                    </div>
                </div>

                <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <h2 style={{ fontSize: '0.75rem', fontWeight: 'bold', color: '#6b7280', letterSpacing: '0.05em', margin: 0 }}>ACTIVE DISTRESS SIGNALS</h2>
                    
                    {Array.from(distressSignals.values()).map((signal: DistressSignal) => (
                        <div key={signal.task_id} style={{ backgroundColor: 'rgba(127, 29, 29, 0.2)', border: '1px solid rgba(239, 68, 68, 0.5)', borderRadius: '4px', padding: '12px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span style={{ color: '#f87171', fontWeight: 'bold' }}>{signal.fault_code}</span>
                                <span style={{ color: '#4ade80', fontFamily: 'monospace' }}>${signal.bounty_usd.toFixed(2)}</span>
                            </div>
                            <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '4px', marginBottom: '12px', fontFamily: 'monospace' }}>VIN: {signal.vin}</div>
                            
                            {/* 🛠️ NEW: Deploy Button matching V1 aesthetics */}
                            <button 
                                onClick={() => setPendingDispatch(signal)}
                                style={{ width: '100%', padding: '8px', backgroundColor: '#00BCD4', color: '#000', border: 'none', borderRadius: '2px', fontWeight: 'bold', cursor: 'pointer', letterSpacing: '0.05em' }}
                            >
                                DEPLOY PROXY AGENT
                            </button>
                        </div>
                    ))}
                    
                    {distressSignals.size === 0 && (
                        <div style={{ fontSize: '0.875rem', color: '#4b5563', fontStyle: 'italic' }}>No active faults in sector.</div>
                    )}
                </div>
            </div>

            {/* Map Area */}
            <div style={{ flex: 1, position: 'relative' }}>
                <MapContainer center={MESA_CENTER} zoom={13} style={{ height: '100%', width: '100%', zIndex: 1 }}>
                    <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />

                    {Array.from(distressSignals.values()).map((signal) => (
                        <Marker key={`distress-${signal.task_id}`} position={[signal.lat, signal.lon]} icon={distressIcon}>
                            <Popup><strong>VIN: {signal.vin}</strong><br/>Fault: {signal.fault_code}<br/>Bounty: ${signal.bounty_usd}</Popup>
                        </Marker>
                    ))}
                    {Array.from(agents.values()).map((agent) => (
                        <Marker key={`agent-${agent.agent_id}`} position={[agent.lat, agent.lon]} icon={agentIcon}>
                            <Popup><strong>{agent.agent_id}</strong><br/>Status: {agent.status}</Popup>
                        </Marker>
                    ))}
                </MapContainer>
            </div>

            {/* 🛠️ NEW: V1 Parity - Dispatch Escrow Modal */}
            {pendingDispatch && (
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ backgroundColor: '#1A1A1A', border: '1px solid #333', borderRadius: '4px', padding: '24px', width: '400px' }}>
                        <h2 style={{ color: '#fff', margin: '0 0 20px 0', fontSize: '1.25rem' }}>DISPATCH ESCROW</h2>
                        
                        <div style={{ color: '#ccc', marginBottom: '8px', fontSize: '0.875rem' }}>Target: {pendingDispatch.vin}</div>
                        <div style={{ color: '#ccc', marginBottom: '24px', fontSize: '0.875rem' }}>Fault: {pendingDispatch.fault_code}</div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#000', padding: '15px', borderRadius: '4px', border: '1px solid #4CAF50', marginBottom: '24px' }}>
                            <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#fff' }}>MAX AUTHORIZATION:</span>
                            <span style={{ fontSize: '24px', fontWeight: 900, color: '#4CAF50' }}>${pendingDispatch.bounty_usd.toFixed(2)}</span>
                        </div>

                        <div style={{ display: 'flex', gap: '12px' }}>
                            <button 
                                onClick={executeDispatch}
                                style={{ flex: 1, padding: '12px', backgroundColor: '#00BCD4', color: '#000', border: 'none', fontWeight: 'bold', cursor: 'pointer' }}>
                                AUTHORIZE & DEPLOY
                            </button>
                            <button 
                                onClick={() => setPendingDispatch(null)}
                                style={{ flex: 1, padding: '12px', backgroundColor: 'transparent', color: '#fff', border: '1px solid #555', fontWeight: 'bold', cursor: 'pointer' }}>
                                CANCEL
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};