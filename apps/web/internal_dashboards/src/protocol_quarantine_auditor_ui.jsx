import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Unplug, 
  Skull, 
  RefreshCw, 
  Search, 
  ShieldCheck, 
  Activity, 
  Terminal, 
  Database, 
  Lock, 
  Unlock, 
  AlertTriangle, 
  History, 
  ChevronRight, 
  Zap, 
  Globe, 
  UserX, 
  XCircle,
  Bomb,
  Radio,
  Fingerprint,
  Info,
  ExternalLink,
  Binary
} from 'lucide-react';

/**
 * PROXY PROTOCOL - QUARANTINE AUDITOR UI (v1.2)
 * "Foundation Security Desk: Oversight for automated enforcement."
 * ---------------------------------------------------------------
 * v1.2 Fix: Resolved ReferenceError for Binary icon.
 * Refactored dynamic icon rendering in vitals grid.
 * Removed redundant global function.
 */

const App = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isWiping, setIsWiping] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedAction, setSelectedAction] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Mock Quarantine Ledger (Linked to core/ops/probing_quarantine_api.py)
  const [history, setHistory] = useState([
    {
      id: "QRN-8829-1707684000",
      target: "45.15.22.0/24",
      node_id: "NODE_ELITE_X29",
      type: "SUBNET_BLACKLIST",
      reason: "PROBING_SEQUENCE_DETECTED",
      probability: 0.98,
      status: "ENFORCED",
      timestamp: "2h ago",
      tpm_revoked: true
    },
    {
      id: "QRN-7714-1707662400",
      target: "103.22.201.0/24",
      node_id: "NODE_ALPHA_004",
      type: "SUBNET_BLACKLIST",
      reason: "ITERATIVE_DHASH_TRIAL",
      probability: 0.92,
      status: "ENFORCED",
      timestamp: "5h ago",
      tpm_revoked: true
    },
    {
      id: "QRN-6602-1707640800",
      target: "did:proxy:F91C3B",
      node_id: "NODE_BETA_009",
      type: "TPM_REVOCATION",
      reason: "GEOFENCE_BYPASS_PROBE",
      probability: 0.85,
      status: "ESCALATED",
      timestamp: "8h ago",
      tpm_revoked: false
    }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const handleRestore = (id) => {
    setIsProcessing(true);
    setTimeout(() => {
      setHistory(prev => prev.map(h => h.id === id ? { ...h, status: 'RESTORED', tpm_revoked: false } : h));
      setIsProcessing(false);
      setSelectedAction(null);
    }, 1500);
  };

  const executeScorchedEarth = () => {
    setIsWiping(true);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-red-500/30 overflow-x-hidden">
      
      {/* Background Warning Mesh */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#ff3333 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl w-full relative z-10 space-y-8 flex-1 flex flex-col">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl shadow-2xl">
              <ShieldAlert className="w-8 h-8 text-red-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Quarantine Auditor</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2 font-mono">
                Automated Containment Oversight // Protocol <span className="text-red-500">v3.6.3</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Global Blacklist</span>
                   <span className="text-xl font-black text-white tracking-tighter uppercase">842_SUBNETS</span>
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

        {/* Tactical Vitals Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
           {[
             { label: 'Auto-Quarantines', val: '14', sub: 'LAST 24H', icon: Zap, color: 'text-red-500' },
             { label: 'TPM Revocations', val: '08', sub: 'BRICKED', icon: Skull, color: 'text-red-500' },
             { label: 'Enforcement Ratio', val: '100%', sub: 'REAL-TIME', icon: ShieldCheck, color: 'text-green-500' },
             { label: 'Escalated Reviews', val: '03', sub: 'PENDING', icon: Activity, color: 'text-indigo-500' }
           ].map((kpi, i) => {
             const Icon = kpi.icon;
             return (
               <div key={i} className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl relative overflow-hidden group">
                  <div className={`absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform duration-500`}>
                    <Icon className="w-20 h-20 text-white" />
                  </div>
                  <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">{kpi.label}</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-white tracking-tighter">{kpi.val}</span>
                    <span className={`text-[9px] font-black uppercase ${kpi.color} ml-1`}>{kpi.sub}</span>
                  </div>
               </div>
             );
           })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start flex-1">
          
          {/* Main Table Column */}
          <div className="col-span-12 lg:col-span-7 space-y-6">
             
             {/* Search & Action Bar */}
             <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                   <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
                   <input 
                     type="text" 
                     placeholder="FILTER BY SUBNET OR ID..."
                     value={searchQuery}
                     onChange={(e) => setSearchQuery(e.target.value)}
                     className="w-full bg-[#0a0a0a] border border-white/5 rounded-lg py-3 pl-10 pr-4 text-xs text-white focus:outline-none focus:border-red-500/50 uppercase tracking-widest"
                   />
                </div>
                <button 
                  onClick={executeScorchedEarth}
                  className="bg-red-600 text-white px-6 py-2 rounded-lg font-black text-[10px] uppercase tracking-widest hover:bg-red-500 transition-all flex items-center gap-2 shadow-2xl"
                >
                  <Bomb className="w-4 h-4" /> Global Wipe
                </button>
             </div>

             {/* Ledger List */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-8">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <History className="w-4 h-4 text-red-500" /> Containment Ledger
                   </h3>
                   <span className="text-[9px] text-gray-700 font-bold uppercase">v1.0 Strict Mode</span>
                </div>

                <div className="divide-y divide-white/5">
                   {history.filter(h => h.target.includes(searchQuery)).map((item) => (
                      <div 
                        key={item.id} 
                        onClick={() => setSelectedAction(item)}
                        className={`p-6 hover:bg-red-500/[0.01] transition-all cursor-pointer group ${selectedAction?.id === item.id ? 'bg-red-500/[0.03]' : ''}`}
                      >
                         <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center gap-4">
                               <div className={`w-10 h-10 rounded border flex items-center justify-center transition-all ${item.status === 'ENFORCED' ? 'bg-red-500/5 border-red-500/20 text-red-500' : 'bg-white/5 border-white/10 text-gray-600'}`}>
                                  <Unplug className="w-5 h-5" />
                               </div>
                               <div>
                                  <span className="text-xs font-black text-white uppercase tracking-tighter group-hover:text-red-400 transition-colors">{item.target}</span>
                                  <p className="text-[10px] text-gray-600 font-bold uppercase mt-1">Origin: {item.node_id}</p>
                               </div>
                            </div>
                            <div className="text-right">
                               <span className={`text-[10px] font-black uppercase tracking-widest ${item.status === 'ENFORCED' ? 'text-red-500 animate-pulse' : 'text-gray-500'}`}>{item.status}</span>
                               <span className="text-[9px] text-gray-700 block font-bold mt-1 uppercase tracking-tighter">{item.timestamp}</span>
                            </div>
                         </div>
                         <div className="flex justify-between items-center text-[9px] font-black text-gray-700 uppercase tracking-tighter">
                            <span className="flex items-center gap-1.5"><Zap className="w-3 h-3" /> Probe Prob: {(item.probability * 100).toFixed(0)}%</span>
                            <span className="flex items-center gap-1.5">{item.tpm_revoked ? 'TPM_BRICKED' : 'TPM_ACTIVE'}</span>
                         </div>
                      </div>
                   ))}
                </div>
             </div>
          </div>

          {/* Right Column: Forensic Detail & Override */}
          <div className="col-span-12 lg:col-span-5">
             {selectedAction ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 shadow-2xl animate-in slide-in-from-right-4 duration-300 flex flex-col gap-8 h-full">
                   <div className="flex justify-between items-start border-b border-white/5 pb-6">
                      <div>
                         <span className="text-[10px] text-red-500 font-black uppercase tracking-[0.2em] block mb-1">Containment Detail</span>
                         <h2 className="text-2xl font-black text-white tracking-tighter uppercase leading-tight">{selectedAction.id}</h2>
                      </div>
                      <button onClick={() => setSelectedAction(null)} className="p-2 text-gray-700 hover:text-white transition-colors">
                        <XCircle className="w-6 h-6" />
                      </button>
                   </div>

                   <div className="space-y-6 flex-1">
                      <div>
                         <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-3 flex items-center gap-2">
                            <Info className="w-3.5 h-3.5 text-red-500" /> Evidence Summary
                         </h4>
                         <div className="p-5 bg-black border border-white/5 rounded-xl text-sm text-gray-400 leading-relaxed italic font-medium">
                            "{selectedAction.reason}: Analytical correlation between 3 disparate failed tasks in ASIA_SE regional hub. Iterative dHash modifications detected below 15% distance threshold."
                         </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                         <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                            <span className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Enforcement Type</span>
                            <div className="flex items-center gap-2">
                               <Radio className="w-4 h-4 text-red-500" />
                               <span className="text-sm font-black text-white uppercase">{selectedAction.type}</span>
                            </div>
                         </div>
                         <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                            <span className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Identity Status</span>
                            <span className={`text-sm font-black uppercase tracking-tighter ${selectedAction.tpm_revoked ? 'text-red-500' : 'text-green-500'}`}>
                               {selectedAction.tpm_revoked ? 'REVOKED' : 'VALID'}
                            </span>
                         </div>
                      </div>

                      <div>
                         <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-3 flex items-center gap-2">
                            <Binary className="w-3.5 h-3.5 text-indigo-500" /> Forensic Link
                         </h4>
                         <div className="p-4 bg-black border border-white/5 rounded-xl font-mono text-[10px] text-gray-500 break-all space-y-4">
                            <div>
                               <span className="text-gray-700 block mb-1">DIFF_ANALYSIS_HASH:</span>
                               <code className="text-indigo-400">0x8A2E1C3B...F91C</code>
                            </div>
                            <div className="pt-2 border-t border-white/5 flex justify-between items-center">
                               <span className="text-[8px] font-black uppercase text-gray-700">Audit Proof: Merkle Verified</span>
                               <button className="flex items-center gap-1.5 hover:text-white transition-colors uppercase text-[9px] font-black">
                                  Inspect Data <ExternalLink className="w-3 h-3" />
                                </button>
                            </div>
                         </div>
                      </div>
                   </div>

                   <div className="pt-6 border-t border-white/5 flex flex-col gap-4">
                      {selectedAction.status === 'ENFORCED' && (
                        <button 
                          onClick={() => handleRestore(selectedAction.id)}
                          disabled={isProcessing}
                          className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-widest hover:bg-green-500 hover:text-white transition-all rounded shadow-xl flex items-center justify-center gap-2"
                        >
                           {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
                           Restore White-list (Manual Override)
                        </button>
                      )}
                      <button className="w-full py-4 bg-white/5 border border-white/10 text-gray-500 font-black text-xs uppercase tracking-widest hover:text-white transition-all rounded">
                         Export Forensic Report
                      </button>
                   </div>
                </div>
             ) : (
                <div className="h-full border-2 border-white/5 border-dashed rounded-3xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale">
                   <Lock className="w-16 h-16 text-gray-800 mb-8 animate-pulse" />
                   <h2 className="text-xl font-black text-gray-600 uppercase tracking-widest mb-4">Focus Required</h2>
                   <p className="text-[10px] text-gray-800 uppercase font-bold tracking-tighter max-w-sm mx-auto leading-relaxed">
                      Select a containment event from the detection stream to initiate manual override or forensic deep-dive into coordinated probing patterns.
                   </p>
                </div>
             )}
          </div>

        </div>

      </main>

      {/* Scorched Earth Modal */}
      {isWiping && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-red-600/10 backdrop-blur-md animate-in fade-in duration-300">
           <div className="bg-black border-2 border-red-500 rounded-3xl max-w-md w-full p-10 shadow-[0_0_100px_rgba(239,68,68,0.3)] text-center relative overflow-hidden">
              <div className="absolute top-0 right-0 p-10 opacity-[0.03]">
                 <Skull className="w-64 h-64 text-white" />
              </div>
              <div className="relative z-10">
                 <AlertTriangle className="w-20 h-20 text-red-500 mx-auto mb-6 animate-bounce" />
                 <h2 className="text-3xl font-black text-white uppercase tracking-tighter mb-4">Scorched Earth</h2>
                 <p className="text-sm text-gray-400 mb-10 leading-relaxed font-bold italic">
                   "Initiating a global network wipe will instantly revoke ALL un-bonded node identities and freeze ALL active Lightning channels. This is an irreversible protocol-level lockdown."
                 </p>
                 <div className="space-y-4">
                    <button className="w-full py-5 bg-red-600 text-white font-black text-xs uppercase tracking-[0.4em] rounded shadow-2xl hover:bg-red-500 transition-all flex items-center justify-center gap-3">
                       <Zap className="w-4 h-4" /> Finalize Lockdown
                    </button>
                    <button 
                      onClick={() => setIsWiping(false)}
                      className="w-full py-4 border border-white/10 text-gray-600 hover:text-white transition-all text-[10px] font-black uppercase"
                    >
                       Abort Command
                    </button>
                 </div>
              </div>
           </div>
        </div>
      )}

      {/* Global Status Footer */}
      <footer className="max-w-6xl mx-auto w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Enforcement Logic Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Pruning the network to preserve biological fidelity."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] BLACKLIST_MODE: AUTO</span>
            <span>[*] RECOVERY_PROTOCOL: V1.0</span>
            <span>[*] VERSION: v3.6.3</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        @keyframes scan { 0% { transform: translateY(-300px); opacity: 0; } 50% { opacity: 1; } 100% { transform: translateY(300px); opacity: 0; } }
        .animate-scan { animation: scan 4s linear infinite; }
        .animate-spin-slow { animation: spin 15s linear infinite; }
      `}} />

    </div>
  );
};

export default App;
