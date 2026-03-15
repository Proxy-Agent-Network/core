import React, { useState, useEffect, useMemo } from 'react';
import { 
  ShieldCheck, 
  Database, 
  Trash2, 
  FileCheck, 
  Globe, 
  Clock, 
  Activity, 
  RefreshCw, 
  Lock, 
  Binary, 
  History, 
  BarChart3, 
  TrendingUp, 
  ChevronRight, 
  Download, 
  Info, 
  ShieldAlert, 
  Layers,
  LayoutGrid,
  FileText,
  Search,
  Zap,
  Ghost,
  Fingerprint,
  ExternalLink
} from 'lucide-react';

/**
 * PROXY PROTOCOL - MASTER COMPLIANCE DASHBOARD (v1.0)
 * "The high-level oversight for network-wide data vaporization."
 * ----------------------------------------------------
 */

const App = () => {
  const [lastSync, setLastSync] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('OVERVIEW');

  // Mock Master State (Aggregated from Auditor, Archive, and Export APIs)
  const [masterState] = useState({
    total_assets_vaporized: 18429,
    active_containment_count: 42,
    compliance_score: 100,
    active_certificates: 842,
    epoch_id: "EPOCH_88294",
    hsm_status: "LOCKED_SECURE"
  });

  // Recent Destruction Certificates
  const [recentCerts] = useState([
    { id: "CERT-9901-8A2E", task_id: "T-9901", timestamp: "2026-02-11T21:00:00Z", method: "SHRED_TRIPLE", status: "SIGNED" },
    { id: "CERT-9884-F91C", task_id: "T-9884", timestamp: "2026-02-11T18:12:00Z", method: "SHRED_TRIPLE", status: "SIGNED" },
    { id: "CERT-9872-D2A1", task_id: "T-9872", timestamp: "2026-02-11T15:45:00Z", method: "SHRED_TRIPLE", status: "SIGNED" }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setLastSync(new Date());
      setIsRefreshing(false);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-emerald-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header: Foundation Master Control */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl shadow-2xl">
              <ShieldCheck className="w-8 h-8 text-emerald-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none text-glow">Compliance Master</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2 font-mono">
                Network Privacy Oversight // Standing: <span className="text-emerald-400">NOMINAL</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Master HSM</span>
                   <span className="text-xs font-black text-white tracking-tighter">{masterState.hsm_status}</span>
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

        {/* Top-Level KPI Matrix */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
           {[
             { label: 'Total Vaporized', val: masterState.total_assets_vaporized.toLocaleString(), sub: 'ASSETS', icon: Trash2, color: 'emerald' },
             { label: 'Active Vault', val: masterState.active_containment_count, sub: 'PENDING_WIPE', icon: Database, color: 'indigo' },
             { label: 'Compliance Index', val: `${masterState.compliance_score}%`, sub: 'VERIFIED', icon: FileCheck, color: 'green' },
             { label: 'Certified Epochs', val: 142, sub: 'BATCH_SIGNED', icon: Layers, color: 'blue' }
           ].map((kpi, i) => (
             <div key={i} className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
                  <kpi.icon className="w-20 h-20" />
                </div>
                <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">{kpi.label}</span>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-black text-white tracking-tighter">{kpi.val}</span>
                  <span className={`text-[9px] font-black text-${kpi.color}-500 uppercase tracking-widest`}>{kpi.sub}</span>
                </div>
             </div>
           ))}
        </div>

        {/* Tabs for Module Switching */}
        <div className="flex bg-[#0a0a0a] border border-white/5 p-1 rounded-xl w-fit">
           {['OVERVIEW', 'ACTIVE_VAULT', 'LEDGER', 'REPORTING'].map(tab => (
             <button 
               key={tab} 
               onClick={() => setActiveTab(tab)}
               className={`px-6 py-2 text-[10px] font-black tracking-widest rounded-lg transition-all ${activeTab === tab ? 'bg-emerald-500 text-black shadow-lg shadow-emerald-500/20' : 'text-gray-500 hover:text-white'}`}
             >
                {tab}
             </button>
           ))}
        </div>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Main Module Content */}
          <div className="col-span-12 lg:col-span-8 space-y-8">
             
             {activeTab === 'OVERVIEW' && (
               <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative overflow-hidden h-[450px]">
                  <div className="flex justify-between items-center mb-10">
                     <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                        <TrendingUp className="w-4 h-4 text-emerald-500" /> Vaporization Velocity
                     </h3>
                     <span className="text-[9px] text-gray-600 font-bold uppercase">Last 24 Hours // Samples: 4.2k</span>
                  </div>

                  <div className="h-64 flex items-end gap-1 px-4 relative">
                     <div className="absolute top-0 w-full h-px border-t border-dashed border-white/5" />
                     {[...Array(60)].map((_, i) => {
                        const h = 20 + Math.random() * 60;
                        return (
                          <div 
                            key={i} 
                            className="flex-1 bg-emerald-500/20 rounded-t-sm group relative" 
                            style={{ height: `${h}%` }}
                          >
                             <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                        );
                     })}
                  </div>
                  
                  <div className="flex justify-between mt-8 text-[9px] font-black uppercase text-gray-700 tracking-widest border-t border-white/5 pt-4">
                     <span>T-24h</span>
                     <span>Current Cycle</span>
                     <span>Next Maintenance Sweep</span>
                  </div>
               </div>
             )}

             {activeTab === 'ACTIVE_VAULT' && (
               <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl overflow-hidden shadow-2xl animate-in fade-in duration-500">
                  <div className="p-4 bg-white/[0.02] border-b border-white/5 flex justify-between items-center px-8">
                     <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                        <Ghost className="w-4 h-4 text-indigo-500" /> Containment Pool
                     </h3>
                     <span className="text-[9px] text-gray-600 font-bold uppercase tracking-widest">42 Active Evidence Shards</span>
                  </div>
                  <div className="divide-y divide-white/5">
                     {[...Array(5)].map((_, i) => (
                        <div key={i} className="p-6 flex justify-between items-center hover:bg-white/[0.01] transition-all group">
                           <div className="flex items-center gap-6">
                              <div className="w-10 h-10 rounded border border-white/10 flex items-center justify-center text-gray-700">
                                 <Database className="w-5 h-5" />
                              </div>
                              <div>
                                 <span className="text-xs font-black text-white group-hover:text-indigo-400 transition-colors uppercase tracking-tighter">T-990{i+1} // NODE_ALPHA_00{i}</span>
                                 <p className="text-[9px] text-gray-600 font-bold uppercase tracking-widest mt-1">Status: LOCKED_FOR_AUDIT</p>
                              </div>
                           </div>
                           <div className="text-right">
                              <span className="text-xs font-black text-red-400 tabular-nums">03h 42m 12s</span>
                              <span className="text-[8px] text-gray-800 block font-black uppercase">Vaporization_ETA</span>
                           </div>
                        </div>
                     ))}
                  </div>
               </div>
             )}

             {activeTab === 'LEDGER' && (
               <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl overflow-hidden shadow-2xl animate-in fade-in duration-500">
                  <div className="p-4 bg-white/[0.02] border-b border-white/5 flex justify-between items-center px-8">
                     <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                        <History className="w-4 h-4 text-blue-500" /> Destruction Ledger
                     </h3>
                     <Search className="w-4 h-4 text-gray-700" />
                  </div>
                  <div className="divide-y divide-white/5">
                     {recentCerts.map((cert) => (
                        <div key={cert.id} className="p-6 flex justify-between items-center hover:bg-white/[0.01] transition-all group">
                           <div className="flex items-center gap-6">
                              <div className="w-10 h-10 rounded bg-emerald-500/5 border border-emerald-500/20 flex items-center justify-center text-emerald-500">
                                 <FileCheck className="w-5 h-5" />
                              </div>
                              <div>
                                 <span className="text-xs font-black text-white group-hover:text-emerald-400 transition-colors uppercase tracking-tighter">{cert.id}</span>
                                 <p className="text-[9px] text-gray-600 font-bold uppercase tracking-widest mt-1">Verified: {cert.task_id} via {cert.method}</p>
                              </div>
                           </div>
                           <button className="p-2 border border-white/10 rounded hover:bg-white/10 transition-all">
                              <ExternalLink className="w-3.5 h-3.5 text-gray-600" />
                           </button>
                        </div>
                     ))}
                  </div>
                  <button className="w-full py-4 text-[9px] font-black text-gray-700 hover:text-white uppercase tracking-[0.3em] border-t border-white/5 transition-all">
                     View All 18,429 Proofs of Destruction &rarr;
                  </button>
               </div>
             )}
          </div>

          {/* Right Sidebar: Operational Context & HSM Control */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:scale-110 transition-transform duration-1000">
                   <Lock className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-6 flex items-center gap-2">
                   <Fingerprint className="w-3.5 h-3.5 text-emerald-500" /> HSM Authentication
                </h4>
                <div className="space-y-4 mb-10">
                   <div className="flex justify-between items-center text-[11px] font-bold uppercase tracking-tighter">
                      <span className="text-gray-700">Audit Proof Status</span>
                      <span className="text-green-500 font-black">SYNCHRONIZED</span>
                   </div>
                   <div className="flex justify-between items-center text-[11px] font-bold uppercase tracking-tighter">
                      <span className="text-gray-700">Root Signing Key</span>
                      <span className="text-white font-mono">0x8A2E...F91C</span>
                   </div>
                </div>
                <button className="w-full py-4 bg-white text-black font-black text-[10px] uppercase tracking-widest rounded-lg hover:bg-emerald-500 hover:text-white transition-all shadow-2xl flex items-center justify-center gap-3">
                   <Lock className="w-4 h-4" /> Rotate Master Secret
                </button>
             </div>

             <div className="p-8 border border-white/10 bg-indigo-500/5 rounded-xl shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                   <Globe className="w-6 h-6 text-indigo-500" />
                   <h4 className="text-xs font-black text-white uppercase tracking-widest leading-none">Global Policy Engine</h4>
                </div>
                <div className="space-y-3">
                   <div className="flex justify-between items-center text-[10px] font-bold uppercase">
                      <span className="text-gray-600 tracking-tighter">GDPR Right to Erasure</span>
                      <span className="text-green-500">ENFORCED</span>
                   </div>
                   <div className="flex justify-between items-center text-[10px] font-bold uppercase">
                      <span className="text-gray-600 tracking-tighter">Retention Threshold</span>
                      <span className="text-white font-black">24 HOURS</span>
                   </div>
                   <div className="flex justify-between items-center text-[10px] font-bold uppercase">
                      <span className="text-gray-600 tracking-tighter">Scrub Method</span>
                      <span className="text-white font-black">3-PASS_SHRED</span>
                   </div>
                </div>
             </div>

             <div className="p-6 border border-red-500/10 bg-red-500/5 rounded-xl flex flex-col gap-4">
                <div className="flex items-center gap-3 text-red-500">
                   <ShieldAlert className="w-5 h-5" />
                   <h4 className="text-[10px] font-black uppercase tracking-widest">Emergency Override</h4>
                </div>
                <p className="text-[11px] text-gray-500 font-bold leading-relaxed">
                   Immediate vaporization of the entire active containment pool across all nodes. This action is recorded on the hardware ledger.
                </p>
                <button className="w-full py-2 bg-red-600 text-white font-black text-[9px] uppercase tracking-widest rounded hover:bg-red-500 transition-all flex items-center justify-center gap-2">
                   <Zap className="w-3 h-3" /> Scorched Earth Purge
                </button>
             </div>
          </div>

        </div>

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Master Compliance Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Zero-Knowledge means Zero-Trace."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] PRIVACY_SPEC: v1.2</span>
            <span>[*] AUDIT_ENGINE: v3.1.2</span>
            <span>[*] VERSION: v3.2.0</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
