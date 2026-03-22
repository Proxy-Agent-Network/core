import React, { useState, useEffect } from 'react';
import { 
  Network, 
  Globe, 
  Map, 
  Activity, 
  Zap, 
  ShieldCheck, 
  RefreshCw, 
  ArrowRight, 
  ChevronRight, 
  Info, 
  Lock, 
  Cpu, 
  Box,
  Split,
  Target,
  Signal,
  AlertTriangle
} from 'lucide-react';

/**
 * PROXY PROTOCOL - ROUTING TOPOLOGY UI (v1.0)
 * "Visualizing dynamic network paths and automated failover."
 * ----------------------------------------------------
 */

const App = () => {
  const [lastTick, setLastTick] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeHub, setActiveHub] = useState(null);

  // Hub Position Configuration (Normalized 0-100)
  const hubs = {
    'CORE': { x: 50, y: 15, label: 'AGENT_GATEWAY', type: 'SOURCE' },
    'US_EAST': { x: 30, y: 45, label: 'US-EAST (DE)', status: 'OPTIMAL', weight: '1.0x', latency: 18 },
    'US_WEST': { x: 20, y: 75, label: 'US-WEST (AZ)', status: 'OPTIMAL', weight: '1.0x', latency: 84 },
    'EU_WEST': { x: 70, y: 45, label: 'EU-WEST (LDN)', status: 'OPTIMAL', weight: '1.0x', latency: 142 },
    'ASIA_SE': { x: 80, y: 75, label: 'ASIA-SE (SG)', status: 'DEGRADED', weight: '0.2x', latency: 1240 }
  };

  const connections = [
    { from: 'CORE', to: 'US_EAST', id: 'c1' },
    { from: 'CORE', to: 'EU_WEST', id: 'c2' },
    { from: 'US_EAST', to: 'US_WEST', id: 'c3' },
    { from: 'EU_WEST', to: 'ASIA_SE', id: 'c4' },
    // Failover path when Asia is critical
    { from: 'EU_WEST', to: 'US_EAST', id: 'f1', isFailover: true }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setLastTick(new Date());
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1200);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30 overflow-hidden">
      
      {/* Background Decorative Matrix */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
              <Network className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Routing Topology</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Logical Failover Map // Synchronized Tick: <span className="text-indigo-400">{lastTick.toLocaleTimeString()}</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Active Paths</span>
                   <span className="text-xl font-black text-white tracking-tighter">05_ENABLED</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <button 
                  onClick={handleRefresh}
                  className={`p-2 border border-white/10 rounded hover:bg-white/10 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
                >
                  <RefreshCw className="w-4 h-4 text-gray-500" />
                </button>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Main Network Graph View */}
          <div className="col-span-12 lg:col-span-9 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative h-[600px] overflow-hidden">
             <div className="absolute inset-0 opacity-[0.02]" 
                  style={{ backgroundImage: 'linear-gradient(to right, #333 1px, transparent 1px), linear-gradient(to bottom, #333 1px, transparent 1px)', backgroundSize: '50px 50px' }} />

             <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                {/* Dynamic Connection Lines */}
                {connections.map((conn) => {
                  const start = hubs[conn.from];
                  const end = hubs[conn.to];
                  const isDegraded = end.status === 'DEGRADED' || end.status === 'CRITICAL';
                  
                  return (
                    <g key={conn.id}>
                      <line 
                        x1={start.x} y1={start.y} 
                        x2={end.x} y2={end.y} 
                        stroke={conn.isFailover ? '#6366f1' : isDegraded ? '#ef4444' : '#22c55e'} 
                        strokeWidth={conn.isFailover ? '0.2' : '0.4'}
                        strokeDasharray={conn.isFailover ? '1, 1' : 'none'}
                        opacity={conn.isFailover ? '0.3' : '0.2'}
                      />
                      {/* Flow Animation for Active Paths */}
                      {!conn.isFailover && !isDegraded && (
                        <circle r="0.3" fill="#22c55e">
                          <animateMotion dur="3s" repeatCount="indefinite" path={`M ${start.x} ${start.y} L ${end.x} ${end.y}`} />
                        </circle>
                      )}
                    </g>
                  );
                })}
             </svg>

             {/* Hub Nodes */}
             {Object.entries(hubs).map(([id, hub]) => (
                <div 
                  key={id}
                  onClick={() => setActiveHub({ id, ...hub })}
                  className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-300 hover:scale-110 z-20 group"
                  style={{ left: `${hub.x}%`, top: `${hub.y}%` }}
                >
                   <div className={`p-4 rounded-xl border-2 shadow-2xl flex items-center justify-center bg-black transition-colors ${
                     hub.type === 'SOURCE' ? 'border-white' : 
                     hub.status === 'OPTIMAL' ? 'border-green-500/40 group-hover:border-green-500' :
                     hub.status === 'DEGRADED' ? 'border-yellow-500/40 group-hover:border-yellow-500 animate-pulse' :
                     'border-red-500/40 group-hover:border-red-500 animate-ping'
                   }`}>
                      {hub.type === 'SOURCE' ? <Box className="w-6 h-6 text-white" /> : <Globe className={`w-5 h-5 ${hub.status === 'OPTIMAL' ? 'text-green-500' : hub.status === 'DEGRADED' ? 'text-yellow-500' : 'text-red-500'}`} />}
                   </div>
                   <div className="absolute top-full left-1/2 -translate-x-1/2 mt-3 whitespace-nowrap">
                      <span className="text-[10px] font-black text-white uppercase tracking-widest bg-black/80 px-2 py-1 rounded border border-white/5">
                        {hub.label}
                      </span>
                   </div>
                </div>
             ))}

             {/* Graph Legend */}
             <div className="absolute bottom-8 left-8 flex flex-col gap-3">
                <div className="flex items-center gap-3">
                   <div className="w-2 h-2 bg-green-500 rounded-full" />
                   <span className="text-[9px] text-gray-500 font-black uppercase tracking-widest">Optimal Path</span>
                </div>
                <div className="flex items-center gap-3">
                   <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
                   <span className="text-[9px] text-gray-500 font-black uppercase tracking-widest">Degraded / Shedding</span>
                </div>
                <div className="flex items-center gap-3">
                   <div className="w-2 h-2 border border-indigo-500/40 border-dashed rounded-full" />
                   <span className="text-[9px] text-gray-500 font-black uppercase tracking-widest">Secondary Failover</span>
                </div>
             </div>

             <div className="absolute top-8 right-8 text-right">
                <div className="flex items-center gap-2 justify-end mb-1">
                   <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                   <span className="text-[10px] text-green-500 font-black uppercase tracking-widest">Real-time Topo Active</span>
                </div>
                <span className="text-[9px] text-gray-700 font-bold uppercase tracking-tighter">Controller Engine v1.0.2</span>
             </div>
          </div>

          {/* Right Sidebar: Hub Details & Failover Logic */}
          <div className="col-span-12 lg:col-span-3 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-6 shadow-2xl min-h-[300px] flex flex-col">
                <h3 className="text-xs font-black text-white uppercase tracking-widest mb-8 flex items-center gap-2 border-b border-white/5 pb-4">
                   <Target className="w-4 h-4 text-indigo-500" /> Hub Inspection
                </h3>

                {activeHub ? (
                  <div className="space-y-6 animate-in fade-in slide-in-from-right-2 duration-300">
                     <div>
                        <span className="text-[9px] text-indigo-400 font-black uppercase tracking-widest block mb-1">Identity</span>
                        <h4 className="text-lg font-black text-white tracking-tight uppercase">{activeHub.id}</h4>
                     </div>

                     <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-white/[0.02] border border-white/5 rounded text-center">
                           <span className="text-[8px] text-gray-600 uppercase font-black block mb-1">Weight</span>
                           <span className="text-sm font-black text-white">{activeHub.weight}</span>
                        </div>
                        <div className="p-3 bg-white/[0.02] border border-white/5 rounded text-center">
                           <span className="text-[8px] text-gray-600 uppercase font-black block mb-1">RTT</span>
                           <span className={`text-sm font-black ${activeHub.latency > 500 ? 'text-red-400' : 'text-green-500'}`}>{activeHub.latency}ms</span>
                        </div>
                     </div>

                     <div className="p-4 border border-indigo-500/20 bg-indigo-500/5 rounded-lg">
                        <h5 className="text-[9px] font-black text-indigo-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                           <Split className="w-3 h-3" /> Routing Rule
                        </h5>
                        <p className="text-[10px] text-gray-500 leading-relaxed italic">
                           {activeHub.status === 'OPTIMAL' 
                             ? "Accepting standard 1.0x priority traffic across regional backbones." 
                             : "SLA compromised. Diverting 80% of task volume to US-EAST hub."}
                        </p>
                     </div>
                  </div>
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center text-center opacity-40">
                     <Info className="w-12 h-12 text-gray-800 mb-4 animate-pulse" />
                     <p className="text-[10px] text-gray-700 font-black uppercase tracking-tighter max-w-[150px]">
                       Select a hub on the topology graph to view active routing rules
                     </p>
                  </div>
                )}
             </div>

             <div className="p-8 border border-white/10 bg-[#0a0a0a] rounded-xl relative overflow-hidden group shadow-2xl">
                <div className="absolute -top-4 -right-4 opacity-[0.03] group-hover:scale-110 transition-transform">
                   <Signal className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <ShieldCheck className="w-3.5 h-3.5 text-indigo-500" /> Failover Policy
                </h4>
                <p className="text-xs text-gray-500 leading-relaxed mb-6">
                   "If a regional hub exceeds 1,500ms P50 latency for 3 consecutive ticks, the protocol initiates a 100% traffic drain to the next best geographic path."
                </p>
                <div className="flex justify-between items-center text-[9px] font-black uppercase text-gray-600 border-t border-white/5 pt-4">
                   <span>Redirection Mode</span>
                   <span className="text-green-500">AUTOMATED</span>
                </div>
             </div>
          </div>

        </div>

        {/* Diagnostic Action Bar */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
           <div className="p-6 border border-white/5 bg-indigo-500/5 rounded-xl flex items-center gap-6 group hover:border-indigo-500/30 transition-all cursor-pointer">
              <div className="p-3 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500 group-hover:text-black transition-all">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Network Re-Sync</p>
                 <p className="text-[9px] text-indigo-400 font-bold">Flush Routing Table</p>
              </div>
           </div>
           <div className="p-6 border border-white/5 bg-yellow-500/5 rounded-xl flex items-center gap-6 group hover:border-yellow-500/30 transition-all cursor-pointer">
              <div className="p-3 bg-yellow-500/10 rounded-lg group-hover:bg-yellow-500 group-hover:text-black transition-all">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Hub Quarantine</p>
                 <p className="text-[9px] text-yellow-500 font-bold">Force Manual Drain</p>
              </div>
           </div>
           <div className="p-6 border border-white/5 bg-blue-500/5 rounded-xl flex items-center gap-6 group hover:border-blue-500/30 transition-all cursor-pointer">
              <div className="p-3 bg-blue-500/10 rounded-lg group-hover:bg-blue-500 group-hover:text-black transition-all">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Backbone Audit</p>
                 <p className="text-[9px] text-blue-400 font-bold">Verify RTT Proofs</p>
              </div>
           </div>
        </div>

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Routing Mesh v1.8 Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Global Converge: 114ms</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] HUB_COUNT: 04</span>
            <span>[*] MULTIPATH: ENABLED</span>
            <span>[*] VERSION: v2.9.6</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
