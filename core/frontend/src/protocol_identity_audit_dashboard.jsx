import React, { useState, useEffect } from 'react';
import { 
  Fingerprint, 
  ShieldAlert, 
  Activity, 
  RefreshCw, 
  Globe, 
  Lock, 
  UserX, 
  Zap, 
  Binary, 
  MapPin, 
  AlertTriangle, 
  ChevronRight, 
  Search, 
  Info,
  Layers,
  LayoutGrid,
  ShieldCheck,
  Smartphone,
  Cpu,
  Unplug,
  History,
  XCircle,
  Clock
} from 'lucide-react';

/**
 * PROXY PROTOCOL - IDENTITY AUDIT DASHBOARD (v1.0)
 * "Neutralizing the Sybil: Visualizing identity-to-hardware integrity."
 * -------------------------------------------------------------------
 */

const App = () => {
  const [selectedConflict, setSelectedConflict] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // Mock Identity Conflict Data (Linked to core/ops/identity_auditor_api.py)
  const [conflicts, setConflicts] = useState([
    {
      id: "CON-8821-SSI",
      did: "did:proxy:8A2E1C",
      risk: "CRITICAL",
      type: "DOUBLE_SIGN_DETECTED",
      unit_a: "SENTRY-JP-001 (Tokyo)",
      unit_b: "SENTRY-VA-099 (Ashburn)",
      timestamp: "2026-02-12T00:42:15Z",
      reputation: 982
    },
    {
      id: "CON-7714-SSI",
      did: "did:proxy:F91C3B",
      risk: "ELEVATED",
      type: "IDENTITY_JITTER",
      unit_a: "SENTRY-LDN-012 (London)",
      unit_b: "SENTRY-BER-004 (Berlin)",
      timestamp: "2026-02-11T22:15:00Z",
      reputation: 845
    }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1200);
  };

  const handleQuarantine = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setConflicts(prev => prev.filter(c => c.id !== selectedConflict.id));
      setSelectedConflict(null);
      setIsProcessing(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-red-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header: Security Desk */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl shadow-2xl">
              <ShieldAlert className="w-8 h-8 text-red-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Identity Sentinel</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Anti-Sybil Watchdog // Protocol <span className="text-red-500">v3.2.4</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Conflicts</span>
                   <span className="text-xl font-black text-white tracking-tighter">{conflicts.length} <span className="text-[10px] text-red-500">PENDING</span></span>
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
          
          {/* Conflict Stream (Left Column) */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <Activity className="w-4 h-4 text-red-500" /> Detection Stream
                   </h3>
                   <span className="text-[9px] text-gray-700 font-bold uppercase tracking-widest">Anti-Clone v1.0</span>
                </div>

                <div className="divide-y divide-white/5">
                   {conflicts.length > 0 ? (
                     conflicts.map((item) => (
                      <div 
                        key={item.id} 
                        onClick={() => setSelectedConflict(item)}
                        className={`p-6 hover:bg-red-500/[0.02] transition-all cursor-pointer group ${selectedConflict?.id === item.id ? 'bg-red-500/[0.04]' : ''}`}
                      >
                         <div className="flex justify-between items-start mb-4">
                            <div>
                               <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-red-400 transition-colors">{item.id}</span>
                               <p className="text-[9px] text-gray-600 font-bold uppercase mt-1">DID: {item.did.substring(10)}</p>
                            </div>
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border border-red-500/20 bg-red-500/10 text-red-500`}>
                               {item.risk}
                            </span>
                         </div>
                         <div className="flex justify-between items-center mt-4 text-[9px] font-black text-gray-700 uppercase tracking-tighter">
                            <span>{item.type}</span>
                            <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                         </div>
                      </div>
                     ))
                   ) : (
                     <div className="p-20 text-center flex flex-col items-center opacity-30">
                        <ShieldCheck className="w-12 h-12 mb-4" />
                        <span className="text-[10px] font-black uppercase tracking-widest">Registry Stable</span>
                     </div>
                   )}
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-indigo-500/5 rounded-xl shadow-inner relative overflow-hidden group">
                <div className="absolute -bottom-6 -right-6 opacity-5 group-hover:scale-110 transition-transform">
                   <Lock className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5" /> Identity Spec
                </h4>
                <p className="text-[11px] text-gray-500 leading-relaxed italic">
                   "A single Decentralized Identifier (DID) is cryptographically restricted to one physical Proxy Sentry unit per epoch. Simultaneous heartbeat signatures from distinct hardware IDs trigger an immediate SEV-1 identity freeze."
                </p>
             </div>
          </div>

          {/* Forensic Resolver (Right Column) */}
          <div className="col-span-12 lg:col-span-8 flex flex-col h-full">
             {selectedConflict ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 shadow-2xl animate-in slide-in-from-right-4 duration-300 flex-1 flex flex-col gap-10">
                   <div className="flex justify-between items-start border-b border-white/5 pb-6">
                      <div>
                         <span className="text-[10px] text-red-500 font-black uppercase tracking-[0.2em] block mb-1">Double-Sign Conflict</span>
                         <h2 className="text-3xl font-black text-white tracking-tighter uppercase">{selectedConflict.did}</h2>
                      </div>
                      <button onClick={() => setSelectedConflict(null)} className="p-3 text-gray-600 hover:text-white transition-colors">
                         <XCircle className="w-6 h-6" />
                      </button>
                   </div>

                   {/* Collision Visualizer */}
                   <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center relative">
                      <div className="md:col-span-5 space-y-4">
                         <div className="p-6 bg-black border border-white/5 rounded-xl flex items-center gap-6 relative overflow-hidden">
                            <div className="absolute top-0 right-0 p-2 opacity-5"><Cpu className="w-12 h-12" /></div>
                            <div className="p-3 bg-white/5 rounded-lg"><Smartphone className="w-6 h-6 text-gray-400" /></div>
                            <div>
                               <span className="text-[9px] text-gray-600 font-black uppercase block">Active Vessel A</span>
                               <span className="text-xs font-black text-white">{selectedConflict.unit_a}</span>
                            </div>
                         </div>
                      </div>

                      <div className="md:col-span-2 flex flex-col items-center gap-4">
                         <div className="h-px w-full bg-red-500/20 hidden md:block" />
                         <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-full animate-pulse shadow-[0_0_20px_rgba(239,68,68,0.2)]">
                            <Zap className="w-6 h-6 text-red-500" />
                         </div>
                         <div className="h-px w-full bg-red-500/20 hidden md:block" />
                      </div>

                      <div className="md:col-span-5 space-y-4">
                         <div className="p-6 bg-black border-2 border-red-500/30 rounded-xl flex items-center gap-6 relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-2 opacity-10"><Cpu className="w-12 h-12 text-red-500 animate-pulse" /></div>
                            <div className="p-3 bg-red-500/10 rounded-lg"><Smartphone className="w-6 h-6 text-red-500" /></div>
                            <div>
                               <span className="text-[9px] text-red-500 font-black uppercase block">Conflicting Vessel B</span>
                               <span className="text-xs font-black text-white">{selectedConflict.unit_b}</span>
                            </div>
                         </div>
                      </div>
                   </div>

                   {/* Forensic Metrics */}
                   <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="p-6 bg-black border border-white/5 rounded-xl">
                         <span className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Time Overlap</span>
                         <div className="flex items-center gap-3">
                            <Clock className="w-5 h-5 text-red-500" />
                            <span className="text-xl font-black text-white tracking-tighter">00:04:12</span>
                         </div>
                      </div>
                      <div className="p-6 bg-black border border-white/5 rounded-xl">
                         <span className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Proof of Cloning</span>
                         <div className="flex items-center gap-3">
                            <Binary className="w-5 h-5 text-indigo-400" />
                            <code className="text-[10px] text-gray-400 font-mono truncate">0x8A2E...F91C</code>
                         </div>
                      </div>
                      <div className="p-6 bg-black border border-white/5 rounded-xl">
                         <span className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Reputation at Risk</span>
                         <div className="flex items-center gap-3">
                            <History className="w-5 h-5 text-amber-500" />
                            <span className="text-xl font-black text-white tracking-tighter">{selectedConflict.reputation} <span className="text-[9px] text-red-500 font-bold ml-1">SUSPENDED</span></span>
                         </div>
                      </div>
                   </div>

                   {/* Decision Controls */}
                   <div className="mt-auto pt-8 border-t border-white/5 flex flex-col md:flex-row gap-6 items-center">
                      <div className="flex items-center gap-4 flex-1 bg-red-500/5 border border-red-500/10 p-4 rounded-xl">
                         <AlertTriangle className="w-10 h-10 text-red-500 shrink-0" />
                         <p className="text-[11px] text-gray-500 leading-relaxed font-bold">
                           Quarantining this identity will revoke all active task authorities and freeze the <span className="text-white">2,000,000 SAT bond</span> until a High Court manual review is completed.
                         </p>
                      </div>
                      <div className="flex gap-4 w-full md:w-auto">
                         <button 
                           onClick={handleQuarantine}
                           disabled={isProcessing}
                           className="px-8 py-5 bg-red-600 text-white font-black text-xs uppercase tracking-[0.2em] hover:bg-red-500 transition-all rounded shadow-2xl flex items-center justify-center gap-3 whitespace-nowrap"
                         >
                            {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <UserX className="w-4 h-4" />}
                            Execute Quarantine
                         </button>
                         <button 
                           className="px-8 py-5 bg-white/5 border border-white/10 text-gray-500 font-black text-xs uppercase tracking-widest hover:text-white transition-all rounded"
                         >
                            Authorized Move
                         </button>
                      </div>
                   </div>
                </div>
             ) : (
                <div className="h-full border-2 border-white/5 border-dashed rounded-2xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale">
                   <Fingerprint className="w-20 h-20 text-gray-800 mb-8 animate-pulse" />
                   <h3 className="text-lg font-black text-gray-600 uppercase tracking-[0.3em] mb-3">Registry Audit Ready</h3>
                   <p className="text-xs text-gray-800 font-bold uppercase tracking-widest max-w-sm">Select an identity conflict from the detection stream to initiate forensic isolation and reputation protection.</p>
                </div>
             )}
          </div>

        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Anti-Sybil Engine Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"One Human. One Box. Zero Exceptions."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] REGISTRY_QUORUM: OK</span>
            <span>[*] DOUBLE_SIGN_CHECK: ACTIVE</span>
            <span>[*] VERSION: v3.2.4</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
