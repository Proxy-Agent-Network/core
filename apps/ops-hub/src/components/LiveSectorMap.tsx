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

// --- Tactical Icons ---
const agentIcon = new L.Icon({
    iconUrl: '/assets/azure-dot.svg',
    iconSize: [20, 20],
    className: 'pulsing-agent-marker'
});

const distressIcon = new L.Icon({
    iconUrl: '/assets/red-alert.svg',
    iconSize: [30, 30],
    className: 'critical-distress-marker'
});

const MESA_CENTER: [number, number] = [33.415184, -111.831459];

// 🛠️ THE FIX: Removed process.env entirely to prevent the browser from crashing!
const WS_URL = 'ws://127.0.0.1:8000/api/v1/telemetry/stream';

// --- Types ---
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
    
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

    const connectWebSocket = useCallback(() => {
        setConnectionStatus('CONNECTING');
        wsRef.current = new WebSocket(WS_URL);

        wsRef.current.onopen = () => {
            setConnectionStatus('LIVE');
            console.log("🟢 [OPS_HUB] Tactical Telemetry Stream Connected.");
            if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
        };

        wsRef.current.onmessage = (event: MessageEvent) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === 'AGENT_LOCATION') {
                    setAgents((prev: Map<string, AgentTelemetry>) => {
                        const next = new Map(prev);
                        next.set(data.payload.agent_id, data.payload);
                        return next;
                    });
                } else if (data.type === 'DISTRESS_ALERT') {
                    setDistressSignals((prev: Map<string, DistressSignal>) => {
                        const next = new Map(prev);
                        next.set(data.payload.task_id, data.payload);
                        return next;
                    });
                } else if (data.type === 'MISSION_CLEARED') {
                    setDistressSignals((prev: Map<string, DistressSignal>) => {
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
            console.warn("🔴 [OPS_HUB] Telemetry Stream Lost. Attempting reconnect in 3s...");
            reconnectTimeout.current = setTimeout(connectWebSocket, 3000);
        };

        wsRef.current.onerror = (error: Event) => {
            console.error("WebSocket Error: ", error);
            wsRef.current?.close(); 
        };
    }, []);

    useEffect(() => {
        connectWebSocket();

        return () => {
            if (wsRef.current) {
                wsRef.current.onclose = null; 
                wsRef.current.close();
            }
            if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
        };
    }, [connectWebSocket]);

    return (
        // 🛠️ THE FIX: Hardcoded inline CSS to guarantee a full-screen dark layout
        <div style={{ display: 'flex', height: '100vh', width: '100vw', backgroundColor: '#121212', color: 'white', fontFamily: 'sans-serif' }}>
            
            <div style={{ width: '320px', borderRight: '1px solid #333', display: 'flex', flexDirection: 'column', backgroundColor: '#000' }}>
                <div style={{ padding: '24px', borderBottom: '1px solid #333' }}>
                    <h1 style={{ fontSize: '1.25rem', fontWeight: 900, letterSpacing: '0.1em', color: '#00BCD4', margin: 0 }}>PAN COMMAND</h1>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
                        <div style={{ 
                            width: '12px', height: '12px', borderRadius: '50%', 
                            backgroundColor: connectionStatus === 'LIVE' ? '#22c55e' : '#ef4444' 
                        }} />
                        <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: '#9ca3af' }}>
                            SECTOR 1: {connectionStatus}
                        </span>
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
                            <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '4px', fontFamily: 'monospace' }}>VIN: {signal.vin}</div>
                        </div>
                    ))}
                    {distressSignals.size === 0 && (
                        <div style={{ fontSize: '0.875rem', color: '#4b5563', fontStyle: 'italic' }}>No active faults in sector.</div>
                    )}
                </div>
            </div>

            <div style={{ flex: 1, position: 'relative' }}>
                <MapContainer 
                    center={MESA_CENTER} 
                    zoom={13} 
                    style={{ height: '100%', width: '100%' }}
                >
                    <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                    />

                    {Array.from(distressSignals.values()).map((signal: DistressSignal) => (
                        <Marker 
                            key={`distress-${signal.task_id}`}
                            position={[signal.lat, signal.lon]}
                            icon={distressIcon}
                        >
                            <Popup className="tactical-popup">
                                <strong>VIN: {signal.vin}</strong><br/>
                                Fault: {signal.fault_code}<br/>
                                Bounty: ${signal.bounty_usd}
                            </Popup>
                        </Marker>
                    ))}

                    {Array.from(agents.values()).map((agent: AgentTelemetry) => (
                        <Marker 
                            key={`agent-${agent.agent_id}`}
                            position={[agent.lat, agent.lon]}
                            icon={agentIcon}
                        >
                            <Popup className="tactical-popup">
                                <strong>{agent.agent_id}</strong><br/>
                                Status: {agent.status}
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>
            </div>
        </div>
    );
};