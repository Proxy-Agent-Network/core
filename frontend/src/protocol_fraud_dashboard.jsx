import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  Search, 
  Image as ImageIcon, 
  ArrowRight, 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  History, 
  Fingerprint, 
  Binary, 
  Activity, 
  Eye, 
  RefreshCw, 
  FileWarning,
  Gavel,
  ShieldCheck,
  Split,
  Maximize2,
  ChevronRight,
  Info,
  Layers,
  LayoutGrid,
  Zap
} from 'lucide-react';

/**
 * PROXY PROTOCOL - FRAUD DASHBOARD (v1.0)
 * "Visualizing visual collisions and proof-of-work reuse."
 * ----------------------------------------------------
 */

const App = () => {
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // Mock Anomaly Data (Collisions detected by perceptual hashing)
  const [anomalies] = useState([
    {
      id: "COL-882-X29",
      timestamp: "2026-02-11T22:15:00Z",
      status: "PENDING_AUDIT",
      node_id: "NODE_ELITE_X29",
      similarity_score: 98.4,
      dhash: "0x8A2E1C...F91C",
      original_task: "T-9004 (2026.01.15)",
      current_task: "T-9982 (ACTIVE)",
      type: "PROOF_REPLAY"
    },
    {
      id: "COL-771-B04",
      timestamp: "2026-02-11T19:42:00Z",
      status: "UNDER_REVIEW",
      node_id: "NODE_ALPHA_004",
      similarity_score: 92.1,
      dhash: "0x3B7C89...D2A1",
      original_task: "T-8411 (2026.02.01)",
      current_task: "T-9975 (ACTIVE)",
      type: "TEMPLATE_FARMING"
    }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const executeSlash = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setSelectedAnomaly(null);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-red-500/30">
      
      {/* Background Warning Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#ff3333 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl shadow-[0_0_20px_rgba(239,68,68,0.1)]">
              <ShieldAlert className="w-8 h-8 text-red-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Fraud Sentinel</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Visual Collision Audit // Protocol <span className="text-red-500">v3.1.3</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Active Flags</span>
                   <span className="text-xl font-black text-white tracking-tighter">{anomalies.length}</span>
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
          
          {/* Anomaly Feed (Left Column) */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <Activity className="w-4 h-4 text-red-500" /> Detection Stream
                   </h3>
                   <span className="text-[9px] text-gray-700 font-bold uppercase">v1.1 dHash Active</span>
                </div>

                <div className="divide-y divide-white/5">
                   {anomalies.map((item) => (
                      <div 
                        key={item.id} 
                        onClick={() => setSelectedAnomaly(item)}
                        className={`p-6 hover:bg-white/[0.01] transition-all cursor-pointer group ${selectedAnomaly?.id === item.id ? 'bg-red-500/[0.03]' : ''}`}
                      >
                         <div className="flex justify-between items-start mb-4">
                            <div>
                               <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-red-400 transition-colors">{item.id}</span>
                               <p className="text-[9px] text-gray-600 font-bold uppercase mt-1">Node: {item.node_id}</p>
                            </div>
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${item.similarity_score > 95 ? 'bg-red-500/10 border-red-500/20 text-red-500' : 'bg-yellow-500/10 border-yellow-500/20 text-yellow-500'}`}>
                               {item.similarity_score}% MATCH
                            </span>
                         </div>
                         <div className="w-full bg-white/5 h-0.5 rounded-full overflow-hidden">
                            <div className={`h-full bg-red-500 transition-all duration-1000`} style={{ width: `${item.similarity_score}%` }} />
                         </div>
                         <div className="flex justify-between items-center mt-4 text-[9px] font-black text-gray-700 uppercase tracking-tighter">
                            <span>{item.type}</span>
                            <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                         </div>
                      </div>
                   ))}
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-indigo-500/5 rounded-xl shadow-inner relative overflow-hidden group">
                <div className="absolute -bottom-4 -right-4 opacity-5 group-hover:scale-110 transition-transform">
                   <ShieldCheck className="w-24 h-24 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5" /> Perception Specs
                </h4>
                <p className="text-[11px] text-gray-500 leading-relaxed italic">
                   "Difference Hashing (dHash) is scale-invariant and resistant to brightness adjustments. Matches exceeding 90% visual similarity trigger an immediate SEV-2 hold on task settlement."
                </p>
             </div>
          </div>

          {/* Forensic Viewer (Right Column) */}
          <div className="col-span-12 lg:col-span-8 flex flex-col h-full">
             {selectedAnomaly ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 shadow-2xl animate-in slide-in-from-right-4 duration-300 flex-1 flex flex-col gap-10">
                   <div className="flex justify-between items-start border-b border-white/5 pb-6">
                      <div>
                         <span className="text-[10px] text-red-500 font-black uppercase tracking-[0.2em] block mb-1">Collision Breakdown</span>
                         <h2 className="text-3xl font-black text-white tracking-tighter uppercase">{selectedAnomaly.id}</h2>
                      </div>
                      <div className="flex items-center gap-4">
                         <button className="p-3 bg-white/5 border border-white/10 rounded hover:bg-white/10 transition-all text-gray-400"><Maximize2 className="w-4 h-4" /></button>
                         <button onClick={() => setSelectedAnomaly(null)} className="p-3 text-gray-600 hover:text-white transition-colors"><XCircle className="w-6 h-6" /></button>
                      </div>
                   </div>

                   {/* Side-by-Side Comparison */}
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div className="space-y-4">
                         <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest text-gray-500">
                            <span>Reference Proof</span>
                            <span className="text-white font-mono">{selectedAnomaly.original_task}</span>
                         </div>
                         <div className="aspect-[4/3] bg-black/60 rounded-xl border border-white/5 flex items-center justify-center relative overflow-hidden grayscale group">
                            <ImageIcon className="w-12 h-12 text-gray-800" />
                            <div className="absolute inset-0 bg-green-500/5 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                               <CheckCircle2 className="w-8 h-8 text-green-500" />
                            </div>
                         </div>
                      </div>
                      <div className="space-y-4">
                         <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest text-red-500">
                            <span>Suspected Duplicate</span>
                            <span className="text-white font-mono">{selectedAnomaly.current_task}</span>
                         </div>
                         <div className="aspect-[4/3] bg-black/60 rounded-xl border border-red-500/30 flex items-center justify-center relative overflow-hidden group">
                            <ImageIcon className="w-12 h-12 text-red-900/30 animate-pulse" />
                            <div className="absolute inset-0 bg-red-500/5 flex items-center justify-center">
                               <FileWarning className="w-8 h-8 text-red-500 animate-bounce" />
                            </div>
                         </div>
                      </div>
                   </div>

                   {/* Evidence Metrics */}
                   <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="p-6 bg-black border border-white/5 rounded-xl">
                         <span className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Similarity Proof</span>
                         <div className="flex items-center gap-3">
                            <Binary className="w-5 h-5 text-red-500" />
                            <span className="text-xl font-black text-white tracking-tighter">{selectedAnomaly.similarity_score}%</span>
                         </div>
                      </div>
                      <div className="p-6 bg-black border border-white/5 rounded-xl">
                         <span className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Collision Hash</span>
                         <div className="flex items-center gap-3">
                            <Fingerprint className="w-5 h-5 text-indigo-400" />
                            <code className="text-[10px] text-gray-400 font-mono truncate">{selectedAnomaly.dhash}</code>
                         </div>
                      </div>
                      <div className="p-6 bg-black border border-white/5 rounded-xl">
                         <span className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Node Reputation</span>
                         <div className="flex items-center gap-3">
                            <History className="w-5 h-5 text-amber-500" />
                            <span className="text-xl font-black text-white tracking-tighter">982 <span className="text-[9px] text-red-500 font-bold ml-1">-50 PENDING</span></span>
                         </div>
                      </div>
                   </div>

                   {/* Decision Controls */}
                   <div className="mt-auto pt-8 border-t border-white/5 flex flex-col md:flex-row gap-6 items-center">
                      <div className="flex items-center gap-4 flex-1 bg-red-500/5 border border-red-500/10 p-4 rounded-xl">
                         <Gavel className="w-10 h-10 text-red-500 shrink-0" />
                         <p className="text-[11px] text-gray-500 leading-relaxed font-bold">
                           By confirming this collision, the node's <span className="text-white">2,000,000 SAT bond</span> will be subject to a standard 30% slash and the task payment will be refunded to the agent.
                         </p>
                      </div>
                      <div className="flex gap-4 w-full md:w-auto">
                         <button 
                           onClick={executeSlash}
                           disabled={isProcessing}
                           className="px-8 py-5 bg-red-600 text-white font-black text-xs uppercase tracking-[0.2em] hover:bg-red-500 transition-all rounded shadow-2xl flex items-center justify-center gap-3 whitespace-nowrap"
                         >
                            {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                            Confirm Fraud & Slash
                         </button>
                         <button 
                           className="px-8 py-5 bg-white/5 border border-white/10 text-gray-500 font-black text-xs uppercase tracking-widest hover:text-white transition-all rounded"
                         >
                            False Positive
                         </button>
                      </div>
                   </div>
                </div>
             ) : (
                <div className="h-full border-2 border-white/5 border-dashed rounded-2xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale">
                   <Eye className="w-20 h-20 text-gray-800 mb-8 animate-pulse" />
                   <h3 className="text-lg font-black text-gray-600 uppercase tracking-[0.3em] mb-3">Auditor Focus Required</h3>
                   <p className="text-xs text-gray-800 font-bold uppercase tracking-widest max-w-sm">Select a flagged collision from the detection stream to initiate visual forensics and bond arbitration.</p>
                </div>
             )}
          </div>

        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Fraud Engine v1.1 Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Detecting artificial patterns in biological work."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] REUSE_DETECTION: ON</span>
            <span>[*] SLASH_READY: TRUE</span>
            <span>[*] VERSION: v3.1.3</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
