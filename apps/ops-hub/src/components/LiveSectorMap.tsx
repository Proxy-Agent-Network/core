import React, { useEffect, useState, useRef, useCallback } from 'react';
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

const agentIcon = new L.Icon({
    iconUrl: '/assets/azure-dot.svg',
    iconSize: [20, 20],
    iconAnchor: [10, 10],   
    popupAnchor: [0, -10],  
    className: 'pulsing-agent-marker'
});

const distressIcon = new L.Icon({
    iconUrl: '/assets/red-alert.svg',
    iconSize: [30, 30],
    iconAnchor: [15, 30],   
    popupAnchor: [0, -30],  
    className: 'critical-distress-marker'
});

const MESA_CENTER: [number, number] = [33.415184, -111.831459];

// Type assertion for Vite's import.meta.env to avoid TS errors without extra config
const WS_URL = (import.meta as any).env?.VITE_TELEMETRY_WS_URL ?? 'ws://127.0.0.1:8000/api/v1/telemetry/stream?token=dev-token-777';

interface AgentTelemetry {
    agent_id: string;
    lat: number;
    lon: number;
    status: 'ONLINE' | 'EN_ROUTE' | 'ON_SCENE' | 'OFFLINE';
    heading: number; 
    remaining_route?: [number, number][];
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
    const [pendingDispatch, setPendingDispatch] = useState<DistressSignal | null>(null);
    
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
    
    // 🛠️ THE FIX 3: Store map reference to invalidate size later
    const mapRef = useRef<L.Map | null>(null);

    const connectWebSocket = useCallback(() => {
        // Prevent opening multiple connections if one is already open or connecting
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

        ws.onerror = (error) => {
            console.error("WebSocket Error: ", error);
            // Don't close immediately here; let onclose handle reconnect logic
        };

        ws.onclose = () => {
            setConnectionStatus('DISCONNECTED');
            wsRef.current = null; // Clear the ref
            reconnectTimeout.current = setTimeout(connectWebSocket, 3000);
        };
    }, []);

    useEffect(() => {
        connectWebSocket();
        return () => {
            if (wsRef.current) {
                // Remove listeners before closing to prevent cleanup loops
                wsRef.current.onclose = null; 
                wsRef.current.onerror = null;
                wsRef.current.onmessage = null;
                wsRef.current.onopen = null;
                wsRef.current.close();
                wsRef.current = null;
            }
            if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
        };
    }, [connectWebSocket]);

    // 🛠️ THE FIX 3: Invalidate map size after a short delay to ensure DOM is fully rendered
    useEffect(() => {
        if (mapRef.current) {
            setTimeout(() => {
                mapRef.current?.invalidateSize();
            }, 100);
        }
    }, [mapRef.current]);

    const executeDispatch = () => {
        if (!pendingDispatch || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.warn("WebSocket not ready. Cannot dispatch.");
            return;
        }

        const payload = {
            action: 'DISPATCH_AGENT',
            payload: {
                task_id: pendingDispatch.task_id,
                routing_strategy: 'BALANCED',
                lat: pendingDispatch.lat,
                lon: pendingDispatch.lon
            }
        };

        wsRef.current.send(JSON.stringify(payload));
        setPendingDispatch(null);
    };

    return (
        <div style={{ display: 'flex', height: '100vh', width: '100vw', position: 'relative', backgroundColor: '#121212', color: 'white', fontFamily: 'sans-serif' }}>
            
            <style>
                {`
                body, html {
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }
                @keyframes mapPulse {
                    0% { opacity: 1; filter: drop-shadow(0 0 2px rgba(0, 188, 212, 0.5)); }
                    50% { opacity: 0.6; filter: drop-shadow(0 0 12px rgba(0, 188, 212, 1)); }
                    100% { opacity: 1; filter: drop-shadow(0 0 2px rgba(0, 188, 212, 0.5)); }
                }
                @keyframes alertPulse {
                    0% { opacity: 1; filter: drop-shadow(0 0 4px rgba(239, 68, 68, 0.8)); }
                    50% { opacity: 0.5; filter: drop-shadow(0 0 16px rgba(239, 68, 68, 1)); }
                    100% { opacity: 1; filter: drop-shadow(0 0 4px rgba(239, 68, 68, 0.8)); }
                }
                .pulsing-agent-marker { animation: mapPulse 2s infinite ease-in-out; }
                .critical-distress-marker { animation: alertPulse 1s infinite ease-in-out; }
                .animate-pulse { animation: mapPulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
                `}
            </style>

            <div style={{ width: '320px', borderRight: '1px solid #333', display: 'flex', flexDirection: 'column', backgroundColor: '#000', zIndex: 10 }}>
                <div style={{ padding: '24px', borderBottom: '1px solid #333' }}>
                    <h1 style={{ fontSize: '1.25rem', fontWeight: 900, letterSpacing: '0.1em', color: '#00BCD4', margin: 0 }}>PAN COMMAND</h1>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
                        <div className="animate-pulse" style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: connectionStatus === 'LIVE' ? '#22c55e' : '#ef4444' }} />
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

            <div style={{ flex: 1, position: 'relative' }}>
                {/* 🛠️ THE FIX 3: Add ref to MapContainer */}
                <MapContainer 
                    center={MESA_CENTER} 
                    zoom={13} 
                    style={{ height: '100%', width: '100%', zIndex: 1 }}
                    ref={mapRef}
                >
                    <TileLayer 
                        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" 
                        attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
                    />

                    {Array.from(distressSignals.values()).map((signal) => (
                        <Marker key={`distress-${signal.task_id}`} position={[signal.lat, signal.lon]} icon={distressIcon}>
                            <Popup><strong>VIN: {signal.vin}</strong><br/>Fault: {signal.fault_code}<br/>Bounty: ${signal.bounty_usd}</Popup>
                        </Marker>
                    ))}
                    
                    {Array.from(agents.values()).map((agent) => (
                        <React.Fragment key={`agent-group-${agent.agent_id}`}>
                            <Marker position={[agent.lat, agent.lon]} icon={agentIcon}>
                                <Popup><strong>{agent.agent_id}</strong><br/>Status: {agent.status}</Popup>
                            </Marker>
                            
                            {agent.status === 'EN_ROUTE' && agent.remaining_route && agent.remaining_route.length > 0 && (
                                <Polyline 
                                    positions={agent.remaining_route} 
                                    color="#eab308" 
                                    dashArray="8, 8" 
                                    weight={3} 
                                    opacity={0.8} 
                                />
                            )}
                        </React.Fragment>
                    ))}
                </MapContainer>
            </div>

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