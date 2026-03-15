import React, { useState, useMemo } from 'react';
import { 
  Eye, 
  Search, 
  Split, 
  Layers, 
  History, 
  Binary, 
  Fingerprint, 
  Activity, 
  RefreshCw, 
  ShieldAlert, 
  ShieldCheck, 
  Clock, 
  MapPin, 
  Globe, 
  ChevronRight, 
  ArrowRight, 
  Info, 
  Lock, 
  Database,
  ImageIcon,
  Maximize2,
  Trash2,
  AlertTriangle,
  Zap,
  Network,
  XCircle,
  FileSearch
} from 'lucide-react';

/**
 * PROXY PROTOCOL - FORENSIC INVESTIGATION PORTAL (v1.0)
 * "The Private Eye: Mapping the lineage of a fraudulent proof."
 * ----------------------------------------------------
 */

const App = () => {
  const [assetQuery, setAssetQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [activeAnalysis, setActiveAnalysis] = useState(null);

  // Mock Lineage Data (Reflecting core/ops/fraud_investigation_api.py results)
  const mockLineage = {
    '0x8A2E': {
      hash: "0x8A2E1C3B2E9928310D2A1E772B31C442",
      type: "DELAWARE_POA_TEMPLATE",
      first_seen: "2026-01-15T12:00:00Z",
      total_occurrences: 14,
      affected_nodes: 8,
      risk_level: "CRITICAL",
      lineage: [
        { id: "ORIGIN", node: "NODE_ELITE_X29", region: "US_EAST", action: "INITIAL_CAPTURE", ts: "2026-01-15 12:00" },
        { id: "GEN_02", node: "NODE_ELITE_X29", region: "US_EAST", action: "RESIZED_90%", ts: "2026-01-15 14:42" },
        { id: "GEN_03", node: "NODE_BETA_004", region: "ASIA_SE", action: "COMPRESSION_FILTER", ts: "2026-02-01 09:12" },
        { id: "GEN_04", node: "NODE_GHOST_88", region: "EU_NORTH", action: "REPLAY_ATTEMPT", ts: "2026-02-11 22:15" }
      ]
    }
  };

  const handleAudit = (e) => {
    e.preventDefault();
    setIsSearching(true);
    setTimeout(() => {
      setActiveAnalysis(mockLineage[assetQuery.toUpperCase()] || null);
      setIsSearching(false);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col selection:bg-red-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto w-full relative z-10 space-y-8 flex-1 flex flex-col">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl shadow-[0_0_20px_rgba(239,68,68,0.1)]">
              <FileSearch className="w-8 h-8 text-red-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Forensic Eye</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2 font-mono">
                Asset Lineage Analysis // Deep-Dive // Protocol <span className="text-red-500">v3.4.2</span>
              </p>
            </div>
          </div>

          <form onSubmit={handleAudit} className="flex gap-2 w-full md:w-auto">
             <div className="relative flex-1 md:w-80">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-700" />
                <input 
                  type="text" 
                  placeholder="SEARCH ASSET HASH (e.g. 0x8A2E)..."
                  value={assetQuery}
                  onChange={(e) => setAssetQuery(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-white/5 rounded-xl py-3 pl-12 pr-4 text-xs text-white focus:outline-none focus:border-red-500/50 uppercase tracking-widest"
                />
             </div>
             <button 
               type="submit"
               disabled={isSearching}
               className="px-8 bg-white text-black font-black text-[10px] uppercase tracking-widest rounded-xl hover:bg-red-500 hover:text-white transition-all shadow-2xl flex items-center gap-2"
             >
                {isSearching ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Layers className="w-4 h-4" />}
                Audit
             </button>
          </form>
        </header>

        {activeAnalysis ? (
          <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700 flex-1">
             
             {/* Left Column: Asset Intelligence */}
             <div className="col-span-12 lg:col-span-4 space-y-6">
                <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative overflow-hidden group">
                   <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:scale-110 transition-transform duration-[2000ms]">
                      <Fingerprint className="w-48 h-48 text-white" />
                   </div>
                   
                   <div className="relative z-10">
                      <span className="text-[10px] text-red-500 font-black uppercase tracking-widest block mb-1">Asset Fingerprint</span>
                      <h2 className="text-xl font-black text-white truncate break-all mb-6">{activeAnalysis.hash}</h2>
                      
                      <div className="grid grid-cols-2 gap-4">
                         <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                            <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Risk Rating</span>
                            <span className="text-xl font-black text-red-500 tracking-tighter">{activeAnalysis.risk_level}</span>
                         </div>
                         <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                            <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Total Hits</span>
                            <span className="text-xl font-black text-white tracking-tighter">{activeAnalysis.total_occurrences}</span>
                         </div>
                      </div>
                   </div>

                   <div className="mt-8 pt-8 border-t border-white/5 relative z-10 space-y-4">
                      <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest">
                         <span className="text-gray-500">First Capture</span>
                         <span className="text-white">{new Date(activeAnalysis.first_seen).toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest">
                         <span className="text-gray-500">Affected Nodes</span>
                         <span className="text-indigo-400">{activeAnalysis.affected_nodes} Hubs</span>
                      </div>
                      <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest">
                         <span className="text-gray-500">Category</span>
                         <span className="text-white">{activeAnalysis.type}</span>
                      </div>
                   </div>
                </div>

                <div className="p-8 border border-red-500/20 bg-red-500/5 rounded-2xl shadow-xl">
                   <div className="flex items-center gap-3 text-red-500 mb-6">
                      <ShieldAlert className="w-6 h-6 animate-pulse" />
                      <h3 className="text-xs font-black uppercase tracking-[0.2em]">Forensic Conclusion</h3>
                   </div>
                   <p className="text-[11px] text-gray-400 leading-relaxed font-bold italic mb-8">
                     "Visual analysis confirms this asset is part of a shared 'Sybil Library.' The occurrences across multiple unique Node IDs in different regions indicate a coordinated Bot-Farm operation."
                   </p>
                   <button className="w-full py-4 bg-red-600 text-white font-black text-xs uppercase tracking-widest rounded-xl hover:bg-red-500 transition-all flex items-center justify-center gap-2 shadow-2xl">
                      <Trash2 className="w-4 h-4" /> Global Blacklist Asset
                   </button>
                </div>
             </div>

             {/* Right Column: Lineage Visualizer */}
             <div className="col-span-12 lg:col-span-8 flex flex-col h-full space-y-6">
                
                {/* Visual Lineage Map */}
                <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl flex-1 flex flex-col relative overflow-hidden">
                   <div className="flex justify-between items-center mb-12 relative z-10">
                      <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                         <Split className="w-4 h-4 text-indigo-500" /> Evidence Lineage
                      </h3>
                      <div className="flex items-center gap-2">
                         <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                         <span className="text-[9px] text-green-500 font-bold uppercase">dHash Tracking Active</span>
                      </div>
                   </div>

                   <div className="relative flex-1 flex flex-col justify-between py-4">
                      {/* Vertical Connecting Line */}
                      <div className="absolute left-[22px] top-6 bottom-6 w-px bg-white/10" />
                      
                      {activeAnalysis.lineage.map((event, i) => (
                        <div key={i} className="flex items-start gap-8 relative z-10 group">
                           <div className={`w-12 h-12 rounded-xl border-2 flex items-center justify-center bg-black transition-all group-hover:scale-110 ${
                             i === 0 ? 'border-green-500 text-green-500 shadow-[0_0_15px_rgba(34,197,94,0.3)]' : 'border-white/10 text-gray-600 group-hover:border-red-500/50 group-hover:text-red-500'
                           }`}>
                              <Activity className="w-5 h-5" />
                           </div>
                           
                           <div className="flex-1 bg-white/[0.02] border border-white/5 p-6 rounded-2xl group-hover:border-white/10 transition-all grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
                              <div className="md:col-span-3">
                                 <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Time Marker</span>
                                 <span className="text-xs font-bold text-white whitespace-nowrap">{event.ts}</span>
                              </div>
                              <div className="md:col-span-3">
                                 <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Node Origin</span>
                                 <span className="text-xs font-black text-indigo-400">{event.node}</span>
                              </div>
                              <div className="md:col-span-3 flex items-center gap-2">
                                 <MapPin className="w-3.5 h-3.5 text-gray-700" />
                                 <span className="text-[10px] font-bold text-gray-400 uppercase">{event.region}</span>
                              </div>
                              <div className="md:col-span-3 text-right">
                                 <span className={`text-[10px] font-black uppercase px-2 py-1 rounded border ${i === 0 ? 'border-green-500/20 text-green-500' : 'border-red-500/20 text-red-500'}`}>
                                   {event.action}
                                 </span>
                              </div>
                           </div>
                        </div>
                      ))}
                   </div>
                </div>

                {/* Technical Forensics Panel */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
                      <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                         <Binary className="w-4 h-4 text-indigo-500" /> Manipulation Delta
                      </h3>
                      <div className="space-y-6">
                         <div>
                            <span className="text-[9px] text-gray-600 uppercase font-black block mb-4 tracking-widest">Similarity Graph</span>
                            <div className="flex items-end gap-1 h-12">
                               {[...Array(20)].map((_, i) => (
                                 <div key={i} className="flex-1 bg-red-500/20 border-t border-red-500/40" style={{ height: `${90 + Math.random() * 8}%` }} />
                               ))}
                            </div>
                         </div>
                         <div className="pt-4 border-t border-white/5 flex justify-between items-center">
                            <span className="text-[10px] font-bold text-gray-500 uppercase">Avg Confidence</span>
                            <span className="text-lg font-black text-white">96.4%</span>
                         </div>
                      </div>
                   </div>

                   <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl flex flex-col justify-between">
                      <div>
                         <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                            <Database className="w-4 h-4 text-emerald-500" /> Global Hits
                         </h3>
                         <div className="space-y-4 font-mono text-[11px]">
                            <div className="flex justify-between items-center">
                               <span className="text-gray-600 uppercase">First Hub</span>
                               <span className="text-white font-bold">US_EAST_01</span>
                            </div>
                            <div className="flex justify-between items-center">
                               <span className="text-gray-600 uppercase">Last Detected</span>
                               <span className="text-red-500 font-bold uppercase animate-pulse">LIVE_MATCH</span>
                            </div>
                            <div className="flex justify-between items-center pt-2 border-t border-white/5">
                               <span className="text-gray-600 uppercase">Cluster Tag</span>
                               <span className="text-indigo-400 font-bold uppercase">BOT_FARM_ASIA_04</span>
                            </div>
                         </div>
                      </div>
                      <button className="w-full mt-6 py-2 border border-white/10 rounded text-[9px] font-black text-gray-500 hover:text-white uppercase tracking-widest transition-all">
                         Export Full Report (JSON) &rarr;
                      </button>
                   </div>
                </div>
             </div>

          </div>
        ) : (
          <div className="flex-1 border-2 border-white/5 border-dashed rounded-3xl flex flex-col items-center justify-center p-20 text-center opacity-30 grayscale transition-all">
             <Eye className="w-24 h-24 text-gray-800 mb-8 animate-pulse" />
             <h2 className="text-2xl font-black text-gray-600 uppercase tracking-[0.3em] mb-4">Registry Ready</h2>
             <p className="text-sm text-gray-800 font-bold uppercase tracking-widest max-w-md mx-auto leading-relaxed">
                Enter an asset hash or perceptual signature to reconstruct its manipulation history across the global fleet.
             </p>
          </div>
        )}

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-7xl mx-auto w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Asset Watchdog Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Reconstructing the history of every pixel."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] LINEAGE_ENGINE: v1.0.2</span>
            <span>[*] DHASH_CORRELATION: ON</span>
            <span>[*] VERSION: v3.4.2</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
