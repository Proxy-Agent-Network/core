import React, { useState, useEffect } from 'react';
import { 
  Trash2, 
  Clock, 
  ShieldCheck, 
  AlertTriangle, 
  Wind, 
  Database, 
  RefreshCw, 
  CheckCircle2, 
  Lock, 
  ChevronRight, 
  Info, 
  Activity, 
  Zap, 
  ShieldX,
  History,
  Binary,
  Ghost,
  EyeOff,
  ShieldAlert
} from 'lucide-react';

/**
 * PROXY PROTOCOL - DATA PURGE DASHBOARD (v1.0)
 * "Enforcing the 24h retention window for toxic data."
 * ----------------------------------------------------
 */

const App = () => {
  const [lastSweep, setLastSweep] = useState(new Date());
  const [isPurging, setIsPurging] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock Evidence Queue (Linked to core/ops/proof_archive_api.py)
  const [queue, setQueue] = useState([
    { id: 'T-9901', node_id: 'NODE_ELITE_X29', dhash: '0x8A2E...F91C', expires_in: 3420, size: '2.4MB', status: 'LOCKED' },
    { id: 'T-9905', node_id: 'NODE_ALPHA_001', dhash: '0x3B7C...D2A1', expires_in: 12402, size: '1.8MB', status: 'LOCKED' },
    { id: 'T-9912', node_id: 'NODE_GAMMA_992', dhash: '0xE772...B31C', expires_in: 54201, size: '4.2MB', status: 'REVIEW_HOLD' },
    { id: 'T-9920', node_id: 'NODE_WHALE_04', dhash: '0x442F...9928', expires_in: 82100, size: '0.9MB', status: 'LOCKED' }
  ]);

  // Handle Real-time Countdown
  useEffect(() => {
    const timer = setInterval(() => {
      setQueue(prev => prev.map(item => ({
        ...item,
        expires_in: Math.max(0, item.expires_in - 1)
      })).filter(item => item.expires_in > 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h}h ${m}m ${s}s`;
  };

  const executeScorchedEarth = () => {
    setIsPurging(true);
    setTimeout(() => {
      setQueue([]);
      setLastSweep(new Date());
      setIsPurging(false);
    }, 3000);
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-red-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl mx-auto relative z-10 space-y-8">
        
        {/* Header: Compliance Center */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
              <Ghost className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Vaporization Queue</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Compliance Desk // Retention Policy: <span className="text-indigo-400">24H_PURGE</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Active Proofs</span>
                   <span className="text-xl font-black text-white tracking-tighter">{queue.length} <span className="text-[10px] text-gray-700">IN VAULT</span></span>
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
          
          {/* Main Queue: The Deletion Timeline */}
          <div className="col-span-12 lg:col-span-8 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-8">
                   <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                     <Clock className="w-4 h-4 text-indigo-500" /> Destruction Countdown
                   </h3>
                   <span className="text-[9px] text-gray-700 font-bold uppercase tracking-widest">Last Sweep: {lastSweep.toLocaleTimeString()}</span>
                </div>

                <div className="divide-y divide-white/5">
                   {queue.length > 0 ? (
                     queue.map((item) => (
                      <div key={item.id} className="p-6 hover:bg-red-500/[0.02] transition-all group flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                         <div className="flex items-center gap-6">
                            <div className="w-12 h-12 rounded bg-white/5 border border-white/10 flex items-center justify-center text-gray-600 group-hover:text-red-500 group-hover:border-red-500/20 transition-all">
                               <Database className="w-6 h-6" />
                            </div>
                            <div>
                               <div className="flex items-center gap-3 mb-1">
                                  <span className="text-sm font-black text-white uppercase tracking-tighter">{item.id}</span>
                                  <span className={`text-[9px] px-1.5 py-0.5 rounded border border-white/10 font-bold ${item.status === 'REVIEW_HOLD' ? 'text-yellow-500 bg-yellow-500/5' : 'text-gray-600 bg-black'}`}>
                                    {item.status}
                                  </span>
                               </div>
                               <div className="flex items-center gap-4 text-[9px] text-gray-600 font-black uppercase tracking-widest">
                                  <span>Node: {item.node_id}</span>
                                  <span>|</span>
                                  <span>Hash: {item.dhash}</span>
                               </div>
                            </div>
                         </div>
                         <div className="text-right">
                            <span className={`text-lg font-black tracking-tighter tabular-nums ${item.expires_in < 3600 ? 'text-red-500 animate-pulse' : 'text-white'}`}>
                               {formatTime(item.expires_in)}
                            </span>
                            <span className="text-[8px] text-gray-700 block font-black uppercase tracking-widest">VAPORIZATION_ETA</span>
                         </div>
                      </div>
                     ))
                   ) : (
                     <div className="p-20 text-center flex flex-col items-center justify-center opacity-40">
                        <Wind className="w-16 h-16 text-gray-800 mb-6 animate-pulse" />
                        <h4 className="text-xs font-black text-gray-600 uppercase tracking-widest">Vault Empty</h4>
                        <p className="text-[10px] text-gray-800 uppercase font-bold tracking-tighter">All physical evidence has been scrubbed</p>
                     </div>
                   )}
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-indigo-500/5 rounded-xl shadow-inner relative overflow-hidden group">
                <div className="absolute -bottom-6 -right-6 opacity-5 group-hover:scale-110 transition-transform">
                   <Lock className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <ShieldCheck className="w-3.5 h-3.5" /> Retention Mechanism
                </h4>
                <p className="text-xs text-gray-500 leading-relaxed italic mb-4">
                   "Evidence is archived for the sole purpose of dispute resolution. Upon task finalization, the retention clock begins a 24-hour countdown. At zero, the 'core/ops/proof_archive_api.py' executes a sector-level overwrite."
                </p>
                <div className="flex justify-between items-center text-[9px] font-black uppercase text-gray-700 border-t border-white/5 pt-4">
                   <span>GDPR_ENFORCED</span>
                   <span className="text-green-500">OPTIMIZED</span>
                </div>
             </div>
          </div>

          {/* Right Sidebar: Controls & Analytics */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl flex flex-col min-h-[300px]">
                <h3 className="text-xs font-black text-white uppercase tracking-widest mb-8 border-b border-white/5 pb-4">
                   Containment Stats
                </h3>
                
                <div className="space-y-6">
                   <div className="p-4 bg-white/5 border border-white/5 rounded-lg flex justify-between items-center group hover:border-indigo-500/30 transition-all">
                      <div>
                         <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Lifetime Purged</span>
                         <span className="text-xl font-black text-white tracking-tighter">1,242 <span className="text-[9px] text-gray-700 font-bold">ASSETS</span></span>
                      </div>
                      <History className="w-5 h-5 text-gray-700 group-hover:text-indigo-400 transition-colors" />
                   </div>

                   <div className="p-4 bg-white/5 border border-white/5 rounded-lg flex justify-between items-center group hover:border-red-500/30 transition-all">
                      <div>
                         <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Scrub Effectiveness</span>
                         <span className="text-xl font-black text-white tracking-tighter">100%</span>
                      </div>
                      <ShieldX className="w-5 h-5 text-gray-700 group-hover:text-red-500 transition-colors" />
                   </div>
                </div>

                <div className="mt-auto pt-10">
                   <button 
                     onClick={executeScorchedEarth}
                     disabled={isPurging || queue.length === 0}
                     className="w-full py-5 bg-red-600 text-white font-black text-xs uppercase tracking-[0.2em] hover:bg-red-500 transition-all rounded shadow-2xl flex items-center justify-center gap-3 disabled:opacity-20 disabled:grayscale"
                   >
                     {isPurging ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                     {isPurging ? 'Executing Wipe...' : 'Scorched Earth Purge'}
                   </button>
                   <p className="text-[8px] text-red-500/60 text-center font-black uppercase tracking-widest mt-4">
                     *WARNING: IRREVERSIBLE DATA DESTRUCTION
                   </p>
                </div>
             </div>

             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:rotate-12 transition-transform">
                   <Binary className="w-24 h-24 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5 text-indigo-500" /> Compliance Audit
                </h4>
                <div className="space-y-4">
                   <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-tighter">
                      <span className="text-gray-700">Audit Protocol</span>
                      <span className="text-indigo-400 flex items-center gap-1">
                         <ChevronRight className="w-3 h-3" /> ZK_RECORDS
                      </span>
                   </div>
                   <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-tighter">
                      <span className="text-gray-700">Scrub Method</span>
                      <span className="text-white">SHRED_TRIPLE_PASS</span>
                   </div>
                </div>
             </div>

             <div className="p-6 border border-red-500/10 bg-red-500/5 rounded-xl flex items-center gap-4">
                <ShieldAlert className="w-6 h-6 text-red-500 shrink-0" />
                <p className="text-[11px] text-gray-500 leading-relaxed font-bold">
                   If a dispute is escalated to the <span className="text-red-400">High Court</span>, the vaporization timer for that specific task is paused until finality is reached.
                </p>
             </div>
          </div>

        </div>

      </main>

      {/* Global Compliance Footer */}
      <footer className="max-w-6xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Privacy Engine Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Biological work must be ephemeral to protect human nodes."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] RETENTION_ZONE: 24H</span>
            <span>[*] SCRUB_INTEGRITY: 1.0</span>
            <span>[*] VERSION: v3.1.5</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
