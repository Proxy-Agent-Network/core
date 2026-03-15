import React, { useState, useEffect } from 'react';
import { 
  Globe, 
  ShieldAlert, 
  ShieldX, 
  ShieldCheck, 
  Zap, 
  Activity, 
  RefreshCw, 
  Lock, 
  Unlock, 
  MapPin, 
  Navigation, 
  Terminal, 
  Wifi, 
  Unplug, 
  History, 
  ChevronRight, 
  Skull, 
  Network,
  Radio,
  Binary,
  AlertTriangle,
  Info
} from 'lucide-react';

/**
 * PROXY PROTOCOL - GLOBAL BAN-LIST VISUALIZER (v1.0)
 * "Visualizing the network's immune response in real-time."
 * --------------------------------------------------------
 */

const App = () => {
  const [isBroadcasting, setIsBroadcasting] = useState(false);
  const [syncedHubs, setSyncedHubs] = useState([]);
  const [lastBan, setLastBan] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Regional Hub Configuration
  const hubs = [
    { id: 'US_EAST', name: 'US-EAST (VA)', x: 30, y: 35 },
    { id: 'US_WEST', name: 'US-WEST (OR)', x: 18, y: 40 },
    { id: 'EU_WEST', name: 'EU-WEST (LDN)', x: 48, y: 28 },
    { id: 'ASIA_SE', name: 'ASIA-SE (SG)', x: 78, y: 62 }
  ];

  const foundation = { x: 40, y: 15, label: 'FOUNDATION_CORE' };

  // Mock Global Ban History
  const [history] = useState([
    { id: "BAN-8829-X", target: "45.15.22.0/24", hardware: "8A2E...F91C", reason: "PROBING_SEQUENCE", ts: "14m ago" },
    { id: "BAN-7714-Y", target: "103.22.201.0/24", hardware: "3B7C...D2A1", reason: "ITERATIVE_FARMING", ts: "2h ago" }
  ]);

  const triggerGlobalSync = () => {
    setIsBroadcasting(true);
    setSyncedHubs([]);
    setLastBan({ id: "BAN-" + Math.floor(Math.random()*9000), target: "192.168." + Math.floor(Math.random()*255) + ".0/24" });

    // Simulate propagation delay to each hub
    hubs.forEach((hub, index) => {
      setTimeout(() => {
        setSyncedHubs(prev => [...prev, hub.id]);
        if (index === hubs.length - 1) {
          setTimeout(() => setIsBroadcasting(false), 1000);
        }
      }, 500 * (index + 1));
    });
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-red-500/30 overflow-x-hidden">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl w-full relative z-10 space-y-8 flex-1 flex flex-col">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl shadow-2xl">
              <Network className="w-8 h-8 text-red-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Firewall Sync</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2 font-mono">
                Real-time Propagation // Protocol <span className="text-red-500">v3.7.2</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Hub Sync State</span>
                   <span className="text-xl font-black text-green-500 tracking-tighter uppercase">Operational</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <button 
                  onClick={triggerGlobalSync}
                  disabled={isBroadcasting}
                  className="bg-red-600 text-white px-6 py-2 rounded font-black text-[10px] uppercase tracking-widest hover:bg-red-500 transition-all shadow-2xl disabled:opacity-20"
                >
                  Broadcast New Ban
                </button>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 flex-1 items-stretch">
          
          {/* Main Visualizer: World Map Broadcast */}
          <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative overflow-hidden flex flex-col h-[550px]">
             
             {/* Status Header Overlay */}
             <div className="absolute top-0 left-0 w-full p-6 border-b border-white/5 bg-white/[0.01] flex justify-between items-center z-20">
                <div className="flex items-center gap-3">
                   <div className={`w-2 h-2 rounded-full ${isBroadcasting ? 'bg-red-500 animate-ping' : 'bg-green-500'}`} />
                   <span className="text-[10px] font-black text-white uppercase tracking-widest">{isBroadcasting ? 'Broadcasting_Excision_Signal' : 'Sentinel_Idle'}</span>
                </div>
                <span className="text-[10px] text-gray-700 font-bold uppercase tracking-widest">
                   {syncedHubs.length} / {hubs.length} Hubs Synced
                </span>
             </div>

             {/* World Map SVG / Animation Layer */}
             <div className="relative flex-1 mt-10">
                <svg className="absolute inset-0 w-full h-full opacity-[0.05] pointer-events-none fill-white" viewBox="0 0 100 100" preserveAspectRatio="none">
                   <path d="M10,25 Q15,15 25,25 T40,35 T55,25 T70,35 T85,25 T95,35 L95,75 Q85,85 70,75 T55,85 T40,75 T25,85 T10,75 Z" />
                </svg>

                {/* Broadcast Waves */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none z-10" viewBox="0 0 100 100" preserveAspectRatio="none">
                   {isBroadcasting && hubs.map((hub) => (
                      <line 
                        key={hub.id}
                        x1={foundation.x} y1={foundation.y}
                        x2={hub.x} y2={hub.y}
                        stroke="#ef4444"
                        strokeWidth="0.2"
                        strokeDasharray="1,1"
                        className="animate-pulse"
                      >
                         <animate attributeName="stroke-dashoffset" from="10" to="0" dur="1s" repeatCount="indefinite" />
                      </line>
                   ))}
                </svg>

                {/* Regional Hubs */}
                {hubs.map((hub) => {
                  const isSynced = syncedHubs.includes(hub.id);
                  return (
                    <div 
                      key={hub.id}
                      className="absolute transform -translate-x-1/2 -translate-y-1/2 z-20 group"
                      style={{ left: `${hub.x}%`, top: `${hub.y}%` }}
                    >
                       <div className={`p-3 rounded-lg border-2 transition-all duration-500 shadow-2xl ${
                         isSynced ? 'bg-red-500/10 border-red-500 shadow-red-500/30' : 'bg-black border-white/10'
                       }`}>
                          <ShieldCheck className={`w-5 h-5 ${isSynced ? 'text-red-500' : 'text-gray-800'}`} />
                       </div>
                       <div className="absolute top-full left-1/2 -translate-x-1/2 mt-3 whitespace-nowrap">
                          <span className="text-[9px] font-black text-white uppercase tracking-widest bg-black/80 px-2 py-1 rounded border border-white/5 opacity-0 group-hover:opacity-100 transition-opacity">
                             {hub.name}
                          </span>
                       </div>
                    </div>
                  );
                })}

                {/* Foundation Center */}
                <div 
                  className="absolute transform -translate-x-1/2 -translate-y-1/2 z-30"
                  style={{ left: `${foundation.x}%`, top: `${foundation.y}%` }}
                >
                   <div className="p-4 bg-white text-black rounded-2xl shadow-[0_0_30px_rgba(255,255,255,0.2)] border-2 border-white group">
                      <Lock className="w-6 h-6" />
                      <div className="absolute -top-12 left-1/2 -translate-x-1/2 bg-black border border-white/20 p-2 rounded text-[8px] font-black whitespace-nowrap opacity-0 group-hover:opacity-100 transition-all uppercase tracking-widest">
                         Master_HSM_Root
                      </div>
                   </div>
                </div>
             </div>

             {/* Dynamic Footer for current ban */}
             <div className="mt-auto border-t border-white/5 pt-8 flex justify-between items-center relative z-10">
                {lastBan ? (
                  <div className="flex items-center gap-6 animate-in slide-in-from-left-4 duration-500">
                     <div className="p-3 bg-red-500/10 rounded-xl border border-red-500/20">
                        <Skull className="w-6 h-6 text-red-500" />
                     </div>
                     <div>
                        <span className="text-[10px] text-red-500 font-black uppercase tracking-widest block">Broadcast Priority: Critical</span>
                        <h4 className="text-sm font-black text-white uppercase tracking-tight">Revoking Identity: {lastBan.id}</h4>
                        <p className="text-[9px] text-gray-600 font-bold uppercase mt-1">Target Subnet: {lastBan.target}</p>
                     </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-4 text-gray-700 italic text-xs">
                     <Radio className="w-4 h-4 animate-pulse" />
                     <span>Awaiting next judicial banishment signal...</span>
                  </div>
                )}
                <div className="text-right">
                   <span className="text-[9px] text-gray-700 uppercase font-black block mb-1">Audit Anchor</span>
                   <code className="text-xs text-indigo-400 font-mono">0x8A2E...F91C</code>
                </div>
             </div>
          </div>

          {/* Sidebar: Global Ban Ledger */}
          <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl flex flex-col shadow-2xl flex-1 overflow-hidden min-h-[300px]">
                <div className="p-4 bg-white/[0.02] border-b border-white/5 flex justify-between items-center px-6">
                   <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest flex items-center gap-2">
                      <History className="w-4 h-4 text-red-500" /> Global Block-List
                   </h3>
                   <span className="text-[9px] text-gray-800 font-bold uppercase">v3.7.2 Sync</span>
                </div>

                <div className="p-4 space-y-4 overflow-y-auto scrollbar-hide flex-1">
                   {history.map((ban, i) => (
                      <div key={i} className="p-4 bg-white/[0.01] border border-white/5 rounded-xl group hover:border-red-500/30 transition-all">
                         <div className="flex justify-between items-start mb-3">
                            <span className="text-[10px] font-black text-white group-hover:text-red-500 transition-colors uppercase tracking-tight">{ban.id}</span>
                            <span className="text-[8px] text-gray-700 font-black uppercase">{ban.ts}</span>
                         </div>
                         <div className="space-y-2">
                            <div className="flex justify-between text-[9px] font-bold uppercase">
                               <span className="text-gray-600">Subnet</span>
                               <span className="text-gray-400">{ban.target}</span>
                            </div>
                            <div className="flex justify-between text-[9px] font-bold uppercase">
                               <span className="text-gray-600">Violation</span>
                               <span className="text-red-900">{ban.reason}</span>
                            </div>
                         </div>
                      </div>
                   ))}
                </div>

                <div className="p-6 border-t border-white/5 bg-black/40">
                   <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                      <Info className="w-3.5 h-3.5" /> Propagation Logic
                   </h4>
                   <p className="text-[11px] text-gray-500 leading-relaxed italic">
                      "Excision signals travel via encrypted hub-to-hub backbones. Consensus-driven banishment is enforced at the network edge in &lt; 2 seconds."
                   </p>
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-red-600/5 rounded-xl flex flex-col justify-between shadow-2xl relative overflow-hidden group min-h-[160px]">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:scale-110 transition-transform">
                   <AlertTriangle className="w-24 h-24 text-white" />
                </div>
                <div>
                   <h4 className="text-[10px] font-black text-red-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                      <Zap className="w-4 h-4" /> Global Flush
                   </h4>
                   <p className="text-xs text-gray-500 leading-relaxed font-medium">
                      Manually force a full firewall re-sync across all 4 jurisdictional hubs.
                   </p>
                </div>
                <button className="w-full mt-6 py-3 bg-red-600 text-white font-black text-[10px] uppercase tracking-widest rounded hover:bg-red-500 transition-all shadow-xl">
                   Trigger Hub Sweep
                </button>
             </div>
          </div>

        </div>

        {/* Tactical Vitals Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 relative z-10 pb-12">
           <div className="p-6 bg-[#0a0a0a] border border-white/5 rounded-xl flex items-center gap-5 group hover:border-red-500/30 transition-all overflow-hidden min-h-[100px]">
              <div className="p-3 bg-red-500/10 rounded-lg group-hover:bg-red-500 group-hover:text-black transition-all shrink-0">
                <Wifi className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">Mean Latency</p>
                 <p className="text-sm font-bold text-white uppercase tracking-tighter truncate">114ms (GLOBAL)</p>
              </div>
           </div>
           <div className="p-6 bg-[#0a0a0a] border border-white/5 rounded-xl flex items-center gap-5 group hover:border-emerald-500/30 transition-all overflow-hidden min-h-[100px]">
              <div className="p-3 bg-emerald-500/10 rounded-lg group-hover:bg-emerald-500 group-hover:text-black transition-all shrink-0">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">Hub Convergence</p>
                 <p className="text-sm font-bold text-white uppercase tracking-tighter truncate">SYNCHRONIZED</p>
              </div>
           </div>
           <div className="p-6 bg-[#0a0a0a] border border-white/5 rounded-xl flex items-center gap-5 group hover:border-indigo-500/30 transition-all overflow-hidden min-h-[100px]">
              <div className="p-3 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500 group-hover:text-black transition-all shrink-0">
                <Binary className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">Enforcement Log</p>
                 <p className="text-sm font-bold text-white uppercase tracking-tighter truncate">SHA256_ANCHORED</p>
              </div>
           </div>
        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-6xl mx-auto w-full mt-auto bg-[#0a0a0a] border border-white/5 rounded-lg p-6 flex flex-col md:flex-row items-center justify-between gap-4 opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Global Excision Engine Active</span>
            </div>
            <div className="h-4 w-px bg-white/10 hidden md:block" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic text-center md:text-left">"Justice is immediate; the firewall is the sentence."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest shrink-0">
            <span>[*] HUB_VITALITY: 100%</span>
            <span>[*] DATA_PRECEDENT: ACTIVE</span>
            <span>[*] VERSION: v3.7.2</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 20s linear infinite;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        @keyframes scan {
          0% { transform: translateY(-300px); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateY(300px); opacity: 0; }
        }
        .animate-scan {
          animation: scan 4s linear infinite;
        }
      `}} />

    </div>
  );
};

export default App;
