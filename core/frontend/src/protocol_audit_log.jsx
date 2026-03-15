import React, { useState, useMemo } from 'react';
import { 
  ClipboardCheck, 
  History, 
  BarChart3, 
  ShieldCheck, 
  ShieldAlert, 
  Search, 
  Filter, 
  ArrowUpRight, 
  ExternalLink, 
  Clock, 
  RefreshCw, 
  ChevronRight, 
  Database,
  Lock,
  Wallet,
  Activity,
  Info,
  CheckCircle2,
  FileText,
  Binary,
  XCircle
} from 'lucide-react';

/**
 * PROXY PROTOCOL - PROTOCOL AUDIT LOG UI (v1.0)
 * "Visualizing the 6-hour financial triple-check."
 * ----------------------------------------------------
 */

const App = () => {
  const [activeAudit, setActiveAudit] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Mock Audit History Data (6-hour intervals)
  const [audits] = useState([
    {
      id: "AUDIT-1707684000",
      timestamp: "2026-02-11T21:00:00Z",
      status: "SYNCHRONIZED",
      summary: "All three pillars aligned within 42 sats.",
      metrics: {
        api_reported: 10450200,
        physical_lnd: 10450158,
        ledger_sum: 10450200
      },
      variance: 42
    },
    {
      id: "AUDIT-1707662400",
      timestamp: "2026-02-11T15:00:00Z",
      status: "SYNCHRONIZED",
      summary: "Reserves verified. 100% parity across rails.",
      metrics: {
        api_reported: 10448000,
        physical_lnd: 10448000,
        ledger_sum: 10448000
      },
      variance: 0
    },
    {
      id: "AUDIT-1707640800",
      timestamp: "2026-02-11T09:00:00Z",
      status: "DESYNC_DETECTED",
      summary: "Manual adjustment required: LND wallet reports 12,000 sats less than API state.",
      metrics: {
        api_reported: 10442000,
        physical_lnd: 10430000,
        ledger_sum: 10442000
      },
      variance: 12000
    },
    {
      id: "AUDIT-1707619200",
      timestamp: "2026-02-11T03:00:00Z",
      status: "SYNCHRONIZED",
      summary: "Nightly sweep successful. Liquidity stable.",
      metrics: {
        api_reported: 10438000,
        physical_lnd: 10438000,
        ledger_sum: 10438000
      },
      variance: 0
    }
  ]);

  const filteredAudits = audits.filter(a => 
    a.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
    a.status.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col selection:bg-indigo-500/30">
      
      {/* Background Decorative Grid */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl mx-auto w-full relative z-10 flex flex-col gap-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl shadow-2xl">
              <ClipboardCheck className="w-8 h-8 text-emerald-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Protocol Audit Log</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Treasury Monitoring // Triple-Check Frequency: <span className="text-emerald-500">6 HOURS</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Sync Status</span>
                   <span className="text-xs font-black text-green-500 uppercase tracking-widest">Synchronized</span>
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
          
          {/* Left Column: Historical Ledger */}
          <div className="col-span-12 lg:col-span-7 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                     <History className="w-4 h-4 text-gray-500" /> Audit Sequence
                   </h3>
                   <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-700" />
                      <input 
                        type="text" 
                        placeholder="FILTER BY ID..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="bg-black border border-white/5 rounded py-1 pl-8 pr-3 text-[10px] text-white focus:outline-none focus:border-emerald-500/30 w-32 uppercase"
                      />
                   </div>
                </div>

                <div className="divide-y divide-white/5">
                   {filteredAudits.map((audit) => (
                      <div 
                        key={audit.id} 
                        onClick={() => setActiveAudit(audit)}
                        className={`p-6 hover:bg-white/[0.01] transition-all cursor-pointer group flex justify-between items-center ${activeAudit?.id === audit.id ? 'bg-emerald-500/[0.03]' : ''}`}
                      >
                         <div className="flex items-center gap-6">
                            <div className={`w-10 h-10 rounded-lg border flex items-center justify-center ${audit.status === 'SYNCHRONIZED' ? 'bg-green-500/5 border-green-500/20 text-green-500' : 'bg-red-500/5 border-red-500/20 text-red-500 animate-pulse'}`}>
                               {audit.status === 'SYNCHRONIZED' ? <CheckCircle2 className="w-5 h-5" /> : <ShieldAlert className="w-5 h-5" />}
                            </div>
                            <div>
                               <span className="text-[11px] font-black text-white group-hover:text-emerald-400 transition-colors uppercase tracking-tight block mb-0.5">{audit.id}</span>
                               <span className="text-[9px] text-gray-600 uppercase font-bold tracking-widest">
                                 {new Date(audit.timestamp).toLocaleString()}
                               </span>
                            </div>
                         </div>
                         <div className="flex items-center gap-6">
                            <div className="text-right flex flex-col items-end">
                               <span className="text-[9px] text-gray-700 uppercase font-black mb-1">Variance</span>
                               <span className={`text-[11px] font-black tracking-tighter ${audit.variance > 0 ? 'text-red-400' : 'text-emerald-500'}`}>
                                 {audit.variance > 0 ? `±${audit.variance.toLocaleString()}` : '0'} <span className="text-[8px] text-gray-700 font-bold uppercase">Sats</span>
                               </span>
                            </div>
                            <ChevronRight className={`w-4 h-4 transition-all ${activeAudit?.id === audit.id ? 'translate-x-1 text-emerald-500' : 'text-gray-800'}`} />
                         </div>
                      </div>
                   ))}
                </div>
             </div>

             {/* Pillar Alignment Visualization */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
                <h3 className="text-xs font-black text-white uppercase tracking-widest mb-10 flex items-center gap-3">
                  <Binary className="w-4 h-4 text-indigo-500" /> Multi-Source Consistency
                </h3>
                <div className="h-40 flex items-end gap-12 justify-center px-8 relative">
                   {/* Background Target Line */}
                   <div className="absolute top-0 w-full h-px border-t border-dashed border-white/5" />
                   
                   {[
                     { label: 'DASHBOARD API', color: 'bg-indigo-500', val: 100 },
                     { label: 'PHYSICAL LND', color: 'bg-emerald-500', val: activeAudit ? (activeAudit.metrics.physical_lnd / activeAudit.metrics.api_reported * 100) : 100 },
                     { label: 'RESERVE LEDGER', color: 'bg-blue-500', val: activeAudit ? (activeAudit.metrics.ledger_sum / activeAudit.metrics.api_reported * 100) : 100 }
                   ].map((pillar, i) => (
                      <div key={i} className="flex-1 flex flex-col items-center gap-4">
                         <div className="w-full relative flex flex-col justify-end h-32">
                            <div className={`w-full ${pillar.color} opacity-20 rounded-t-lg transition-all duration-1000`} style={{ height: `${pillar.val}%` }} />
                            <div className={`absolute bottom-0 w-full ${pillar.color} h-1 rounded-full shadow-[0_0_10px_rgba(255,255,255,0.1)]`} />
                         </div>
                         <span className="text-[8px] font-black text-gray-600 uppercase tracking-[0.2em] text-center">{pillar.label}</span>
                      </div>
                   ))}
                </div>
             </div>
          </div>

          {/* Right Column: Detail Drilldown */}
          <div className="col-span-12 lg:col-span-5">
             {activeAudit ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-8 shadow-2xl animate-in slide-in-from-right-4 duration-300 space-y-8 h-full flex flex-col">
                   <div className="flex justify-between items-start">
                      <div>
                         <span className="text-[10px] text-emerald-500 font-black uppercase tracking-widest block mb-1">Audit Breakdown</span>
                         <h2 className="text-2xl font-black text-white tracking-tighter uppercase">{activeAudit.id}</h2>
                      </div>
                      <button onClick={() => setActiveAudit(null)} className="text-gray-700 hover:text-white transition-colors">
                        <XCircle className="w-5 h-5" />
                      </button>
                   </div>

                   <div className="bg-black border border-white/5 p-6 rounded-xl relative overflow-hidden group">
                      <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:scale-110 transition-transform">
                        <Database className="w-24 h-24 text-white" />
                      </div>
                      <div className="space-y-6 relative z-10">
                         <div>
                            <span className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Audit Status</span>
                            <div className="flex items-center gap-3">
                               <div className={`w-2 h-2 rounded-full ${activeAudit.status === 'SYNCHRONIZED' ? 'bg-green-500' : 'bg-red-500 animate-pulse'}`} />
                               <span className={`text-sm font-black uppercase ${activeAudit.status === 'SYNCHRONIZED' ? 'text-white' : 'text-red-400'}`}>{activeAudit.status}</span>
                            </div>
                         </div>
                         <div className="p-4 bg-white/5 border border-white/5 rounded text-xs text-gray-400 leading-relaxed italic">
                            "{activeAudit.summary}"
                         </div>
                      </div>
                   </div>

                   <div className="space-y-4">
                      <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest">Satoshi Balance Drilldown</h4>
                      <div className="space-y-3">
                        {[
                          { label: 'API Reported State', val: activeAudit.metrics.api_reported, icon: Activity },
                          { label: 'Physical LND Wallet', val: activeAudit.metrics.physical_lnd, icon: Wallet },
                          { label: 'Insurance Ledger Sum', val: activeAudit.metrics.ledger_sum, icon: FileText }
                        ].map((item, i) => (
                           <div key={i} className="flex justify-between items-center p-4 bg-white/[0.02] border border-white/5 rounded-lg group hover:border-emerald-500/30 transition-all">
                              <div className="flex items-center gap-4">
                                 <item.icon className="w-4 h-4 text-gray-700 group-hover:text-emerald-500 transition-colors" />
                                 <span className="text-[10px] text-gray-500 font-bold uppercase tracking-tight">{item.label}</span>
                              </div>
                              <span className="text-sm font-black text-white tracking-tighter">{item.val.toLocaleString()} <span className="text-[9px] text-gray-700">S</span></span>
                           </div>
                        ))}
                      </div>
                   </div>

                   <div className="mt-auto pt-8 border-t border-white/5 flex gap-4">
                      <button className="flex-1 py-4 bg-white text-black font-black text-xs uppercase tracking-widest hover:bg-emerald-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-xl">
                         <ShieldCheck className="w-4 h-4" /> Export Proof
                      </button>
                      <button className="p-4 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-all">
                         <ExternalLink className="w-4 h-4 text-gray-400" />
                      </button>
                   </div>
                </div>
             ) : (
                <div className="h-full border-2 border-white/5 border-dashed rounded-xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale">
                   <Lock className="w-16 h-16 text-gray-800 mb-6" />
                   <h3 className="text-xs font-black text-gray-600 uppercase tracking-[0.2em] mb-2">Audit Selection Required</h3>
                   <p className="text-[10px] text-gray-800 uppercase font-bold tracking-tighter max-w-xs">Select a 6-hour window from the sequence to drill into liquidity metrics.</p>
                </div>
             )}
          </div>

        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-6xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Protocol Audit Engine Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Drift Tolerance: ±1,000 SATS</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] TOTAL_RESERVES: 0.71 BTC</span>
            <span>[*] STATUS: SYNCHRONIZED</span>
            <span>[*] VERSION: v2.8.8</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
