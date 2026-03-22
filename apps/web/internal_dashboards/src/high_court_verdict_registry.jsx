import React, { useState, useMemo } from 'react';
import { 
  Archive, 
  Search, 
  Scale, 
  CheckCircle2, 
  XCircle, 
  ExternalLink, 
  ShieldCheck, 
  Hash, 
  Users, 
  ArrowRight, 
  Filter, 
  FileText, 
  Database, 
  Clock,
  ChevronRight,
  RefreshCw,
  Info,
  Binary,
  Gavel
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HIGH COURT VERDICT REGISTRY (v1.0)
 * "The immutable ledger of decentralized case law."
 * ----------------------------------------------------
 */

const App = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterResult, setFilterResult] = useState('ALL');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock Verdict Data
  const [verdicts] = useState([
    {
      id: "CASE-8829-APP",
      title: "Protocol Breach: Metadata Forgery",
      timestamp: "2026-02-11T20:15:00Z",
      result: "REJECTED",
      action: "BURN_AND_REFUND",
      consensus: "6/7",
      value: "2,500,000 SATS",
      manifest_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    {
      id: "CASE-8772-APP",
      title: "Dispute: Notary Seal Verification",
      timestamp: "2026-02-08T11:22:00Z",
      result: "APPROVED",
      action: "RELEASE_TO_NODE",
      consensus: "7/7",
      value: "500,000 SATS",
      manifest_hash: "3b7c89f...9a21"
    },
    {
      id: "CASE-8701-APP",
      title: "Liveness Failure: Deepfake Detection",
      timestamp: "2026-02-04T09:12:00Z",
      result: "REJECTED",
      action: "BURN_AND_REFUND",
      consensus: "5/7",
      value: "1,200,000 SATS",
      manifest_hash: "8a2e1c...f91c"
    }
  ]);

  const filteredVerdicts = useMemo(() => {
    return verdicts.filter(v => {
      const matchesSearch = v.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
                            v.title.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = filterResult === 'ALL' || v.result === filterResult;
      return matchesSearch && matchesFilter;
    });
  }, [searchQuery, filterResult, verdicts]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-amber-500/30">
      
      {/* Background Grid */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl mx-auto relative z-10">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 border-b border-white/10 pb-8 gap-6">
          <div>
            <div className="flex items-center gap-4 mb-3">
              <div className="p-3 bg-white/5 border border-white/10 rounded-xl shadow-2xl">
                <Archive className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Verdict Registry</h1>
                <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold">Public Case Law // Protocol v2.7.3</p>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Total Verdicts</span>
                   <span className="text-xl font-black text-white tracking-tighter">842</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Consensus Mean</span>
                   <span className="text-xl font-black text-green-500 tracking-tighter">94.2%</span>
                </div>
             </div>
          </div>
        </header>

        {/* Search & Filtration */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-8">
           <div className="md:col-span-6 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
              <input 
                type="text" 
                placeholder="SEARCH CASE_ID OR TITLE..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#0a0a0a] border border-white/5 rounded-lg py-3 pl-12 pr-4 text-xs text-white focus:outline-none focus:border-indigo-500/50 uppercase tracking-widest placeholder:text-gray-800"
              />
           </div>
           <div className="md:col-span-4 flex bg-[#0a0a0a] border border-white/5 p-1 rounded-lg">
              {['ALL', 'APPROVED', 'REJECTED'].map(f => (
                <button 
                  key={f}
                  onClick={() => setFilterResult(f)}
                  className={`flex-1 py-2 text-[9px] font-black rounded transition-all ${filterResult === f ? 'bg-white/5 text-white' : 'text-gray-600 hover:text-gray-400'}`}
                >
                  {f}
                </button>
              ))}
           </div>
           <button 
             onClick={handleRefresh}
             className="md:col-span-2 flex items-center justify-center gap-3 bg-white/5 border border-white/10 rounded-lg py-3 text-[10px] font-black text-gray-500 hover:text-white transition-all"
           >
             <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} /> REFRESH
           </button>
        </div>

        {/* Registry Table */}
        <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl mb-12">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/[0.02] border-b border-white/5 text-[10px] font-black text-gray-600 uppercase tracking-widest">
                <th className="p-6">Case Identification</th>
                <th className="p-6 text-center">Consensus</th>
                <th className="p-6 text-center">Outcome</th>
                <th className="p-6 text-right">Settlement Value</th>
                <th className="p-6 text-right">Finality</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredVerdicts.map((v) => (
                <tr key={v.id} className="group hover:bg-white/[0.01] transition-all">
                  <td className="p-6">
                    <div className="flex items-center gap-4">
                       <div className={`w-10 h-10 rounded border flex items-center justify-center ${v.result === 'APPROVED' ? 'bg-green-500/5 border-green-500/20 text-green-500' : 'bg-red-500/5 border-red-500/20 text-red-500'}`}>
                          <FileText className="w-5 h-5" />
                       </div>
                       <div>
                          <span className="text-xs font-black text-white block mb-0.5 group-hover:text-indigo-400 transition-colors uppercase tracking-tight">{v.id}</span>
                          <span className="text-[10px] text-gray-600 font-bold uppercase tracking-widest">{v.title}</span>
                       </div>
                    </div>
                  </td>
                  <td className="p-6 text-center">
                     <div className="flex flex-col items-center gap-1">
                        <span className="text-xs font-black text-white">{v.consensus}</span>
                        <div className="flex gap-0.5">
                           {[...Array(7)].map((_, i) => (
                             <div key={i} className={`w-1 h-1 rounded-full ${i < parseInt(v.consensus) ? 'bg-indigo-500' : 'bg-white/10'}`} />
                           ))}
                        </div>
                     </div>
                  </td>
                  <td className="p-6 text-center">
                     <span className={`text-[9px] font-black uppercase px-2 py-1 rounded border ${v.result === 'APPROVED' ? 'bg-green-500/10 border-green-500/20 text-green-500' : 'bg-red-500/10 border-red-500/20 text-red-500'}`}>
                        {v.result}
                     </span>
                  </td>
                  <td className="p-6 text-right">
                     <span className="text-xs font-black text-gray-400">{v.value}</span>
                  </td>
                  <td className="p-6 text-right">
                     <div className="flex items-center justify-end gap-3">
                        <button className="p-2 bg-white/5 border border-white/10 rounded hover:bg-white/10 transition-all text-gray-500 hover:text-white" title="View Manifest">
                           <Binary className="w-4 h-4" />
                        </button>
                        <ChevronRight className="w-4 h-4 text-gray-800 group-hover:text-white transition-colors" />
                     </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {filteredVerdicts.length === 0 && (
            <div className="p-20 text-center flex flex-col items-center">
              <Info className="w-12 h-12 text-gray-800 mb-4 animate-pulse" />
              <h3 className="text-xs font-black text-gray-600 uppercase tracking-widest">No historical records found</h3>
              <p className="text-[10px] text-gray-800 mt-2">Adjust your search parameters to explore the ledger.</p>
            </div>
          )}
        </div>

        {/* Verification Tools */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
           <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-8 flex items-start gap-6">
              <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl">
                 <ShieldCheck className="w-8 h-8 text-indigo-500" />
              </div>
              <div>
                 <h3 className="text-lg font-black text-white uppercase tracking-tight mb-2">Cryptographic Continuity</h3>
                 <p className="text-xs text-gray-500 leading-relaxed mb-6">
                    Every verdict in this registry is cryptographically bound to the 7 hardware-signatures of the selected jurors. This ensures that even the Foundation cannot overwrite protocol case law.
                 </p>
                 <button className="text-[9px] font-black text-indigo-400 uppercase tracking-widest flex items-center gap-2 hover:text-white transition-colors">
                    Download Root Merkle Proof <ArrowRight className="w-3 h-3" />
                 </button>
              </div>
           </div>

           <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 flex items-start gap-6">
              <div className="p-4 bg-white/5 border border-white/10 rounded-2xl">
                 <Scale className="w-8 h-8 text-gray-400" />
              </div>
              <div>
                 <h3 className="text-lg font-black text-white uppercase tracking-tight mb-2">Precedent & Appeals</h3>
                 <p className="text-xs text-gray-500 leading-relaxed mb-6">
                    Agents use this registry to calibrate their risk thresholds. If you are a Node Operator disputing a slash, these cases serve as the canonical reference for High Court standards.
                 </p>
                 <button className="text-[9px] font-black text-gray-500 uppercase tracking-widest flex items-center gap-2 hover:text-white transition-colors">
                    Protocol Legal Charter <ExternalLink className="w-3 h-3" />
                 </button>
              </div>
           </div>
        </div>

      </main>

      {/* Footer Status Bar */}
      <footer className="max-w-6xl mx-auto mt-20 py-8 border-t border-white/5 flex items-center justify-between opacity-50 grayscale hover:grayscale-0 transition-all duration-700">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Ledger Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Block Hash: 0x8a2e...f91c</span>
         </div>
         <span className="text-[9px] font-black uppercase text-gray-700 tracking-widest">© 2026 Proxy Protocol Foundation</span>
      </footer>

    </div>
  );
};

export default App;
