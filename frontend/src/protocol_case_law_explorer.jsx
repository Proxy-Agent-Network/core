import React, { useState, useMemo } from 'react';
import { 
  Scale, 
  Search, 
  Archive, 
  Database, 
  Binary, 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Fingerprint, 
  Layers, 
  ExternalLink, 
  RefreshCw, 
  Info, 
  ChevronRight, 
  Gavel, 
  FileText,
  BarChart3,
  Hash,
  Download,
  Filter,
  Users,
  History,
  Zap
} from 'lucide-react';

/**
 * PROXY PROTOCOL - CASE LAW EXPLORER (v1.0)
 * "Auditing the immutable record of decentralized justice."
 * ----------------------------------------------------
 */

const App = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterResult, setFilterResult] = useState('ALL');
  const [selectedCase, setSelectedCase] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock Archived Case Law (Reflecting core/ops/adjudication_archivist_api.py data)
  const [archive] = useState([
    {
      id: "CASE-8829-APP",
      title: "Protocol Breach: Metadata Forgery",
      verdict: "REJECTED",
      consensus: "6/7",
      timestamp: "2026-02-11T20:15:00Z",
      economic_impact: "-1.8M SATS (Bond Slashes)",
      manifest_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      precedent_summary: "Confirmed that visual proofs must match the PCR state-root at the time of execution. Deviations in metadata constitute a high-severity violation.",
      forensic_path: "ipfs://QmForensic_Bundle_8829"
    },
    {
      id: "CASE-8772-APP",
      title: "Dispute: Notary Seal Validity",
      verdict: "APPROVED",
      consensus: "7/7",
      timestamp: "2026-02-08T11:22:00Z",
      economic_impact: "+500k SATS (Payout Released)",
      manifest_hash: "3b7c89f...9a21",
      precedent_summary: "Determined that digital seals generated via certified RON hardware are equivalent to physical embossed seals under SG ETA-2010.",
      forensic_path: "ipfs://QmForensic_Bundle_8772"
    },
    {
      id: "CASE-8421-APP",
      title: "Task Contest: Geofence Drift",
      verdict: "REJECTED",
      consensus: "5/7",
      timestamp: "2026-01-14T09:42:00Z",
      economic_impact: "-600k SATS (Bond Slashes)",
      manifest_hash: "8a2e1c...f91c",
      precedent_summary: "Stationary Tier 2 nodes must maintain a zero-drift locality proof. 500m deviations are not permitted without manual policy override.",
      forensic_path: "ipfs://QmForensic_Bundle_8421"
    }
  ]);

  const filteredArchive = useMemo(() => {
    return archive.filter(item => {
      const matchesQuery = item.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
                           item.title.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = filterResult === 'ALL' || item.verdict === filterResult;
      return matchesQuery && matchesFilter;
    });
  }, [searchQuery, filterResult, archive]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-amber-500/30 overflow-x-hidden">
      
      {/* Background Matrix Mesh */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl w-full relative z-10 space-y-8 flex-1 flex flex-col">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/5 border border-white/10 rounded-xl shadow-2xl">
              <Archive className="w-8 h-8 text-white animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Case Law Explorer</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2 font-mono">
                Decentralized Precedent Archive // Protocol <span className="text-indigo-400">v3.5.9</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Archive Depth</span>
                   <span className="text-xl font-black text-white tracking-tighter">842 <span className="text-[10px] text-gray-700">CASES</span></span>
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

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start flex-1">
          
          {/* Main Feed Column */}
          <div className="col-span-12 lg:col-span-7 space-y-6">
             
             {/* Search & Filter Bar */}
             <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                   <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
                   <input 
                     type="text" 
                     placeholder="SEARCH BY ID OR KEYWORD..."
                     value={searchQuery}
                     onChange={(e) => setSearchQuery(e.target.value)}
                     className="w-full bg-[#0a0a0a] border border-white/5 rounded-lg py-3 pl-10 pr-4 text-xs text-white focus:outline-none focus:border-indigo-500/50 uppercase tracking-widest placeholder:text-gray-800"
                   />
                </div>
                <div className="flex bg-[#0a0a0a] border border-white/5 p-1 rounded-lg">
                   {['ALL', 'APPROVED', 'REJECTED'].map(f => (
                     <button 
                       key={f}
                       onClick={() => setFilterResult(f)}
                       className={`px-4 py-2 text-[9px] font-black rounded transition-all ${filterResult === f ? 'bg-white/10 text-white shadow-xl' : 'text-gray-600 hover:text-gray-400'}`}
                     >
                        {f}
                     </button>
                   ))}
                </div>
             </div>

             {/* Result List */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-8">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <History className="w-4 h-4 text-indigo-500" /> Audit Sequence
                   </h3>
                   <span className="text-[9px] text-gray-700 font-bold uppercase">{filteredArchive.length} Records In-Range</span>
                </div>

                <div className="divide-y divide-white/5">
                   {filteredArchive.map((item) => (
                      <div 
                        key={item.id} 
                        onClick={() => setSelectedCase(item)}
                        className={`p-6 hover:bg-white/[0.01] transition-all cursor-pointer group ${selectedCase?.id === item.id ? 'bg-indigo-500/[0.03]' : ''}`}
                      >
                         <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center gap-4">
                               <div className={`w-10 h-10 rounded border flex items-center justify-center transition-all ${item.verdict === 'APPROVED' ? 'bg-green-500/5 border-green-500/20 text-green-500' : 'bg-red-500/5 border-red-500/20 text-red-500'}`}>
                                  <Gavel className="w-5 h-5" />
                               </div>
                               <div>
                                  <span className="text-xs font-black text-white uppercase tracking-tighter group-hover:text-indigo-400 transition-colors">{item.id}</span>
                                  <p className="text-[10px] text-gray-600 font-bold uppercase mt-1">{item.title}</p>
                               </div>
                            </div>
                            <div className="text-right">
                               <span className={`text-[10px] font-black uppercase tracking-widest ${item.verdict === 'APPROVED' ? 'text-green-500' : 'text-red-500'}`}>{item.verdict}</span>
                               <span className="text-[9px] text-gray-700 block font-bold mt-1">{new Date(item.timestamp).toLocaleDateString()}</span>
                            </div>
                         </div>
                         <div className="flex justify-between items-center text-[9px] font-black text-gray-700 uppercase tracking-tighter">
                            <span className="flex items-center gap-1.5"><Users className="w-3 h-3" /> Consensus: {item.consensus}</span>
                            <span className="flex items-center gap-1.5 hover:text-white transition-colors">Forensic Manifest <ExternalLink className="w-3 h-3" /></span>
                         </div>
                      </div>
                   ))}
                </div>
             </div>
          </div>

          {/* Detail Column (Sidebar) */}
          <div className="col-span-12 lg:col-span-5">
             {selectedCase ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 shadow-2xl animate-in slide-in-from-right-4 duration-300 h-full flex flex-col gap-8">
                   <div className="flex justify-between items-start border-b border-white/5 pb-6">
                      <div>
                         <span className="text-[10px] text-indigo-500 font-black uppercase tracking-[0.2em] block mb-1">Precedent Detail</span>
                         <h2 className="text-2xl font-black text-white tracking-tighter uppercase leading-tight">{selectedCase.id}</h2>
                      </div>
                      <button onClick={() => setSelectedCase(null)} className="p-2 text-gray-700 hover:text-white transition-colors">
                        <XCircle className="w-6 h-6" />
                      </button>
                   </div>

                   <div className="space-y-6 flex-1">
                      <div>
                         <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-3 flex items-center gap-2">
                            <Info className="w-3.5 h-3.5 text-amber-500" /> Ruling Abstract
                         </h4>
                         <div className="p-5 bg-black border border-white/5 rounded-xl text-sm text-gray-400 leading-relaxed italic font-medium">
                            "{selectedCase.precedent_summary}"
                         </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                         <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                            <span className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Consensus Reach</span>
                            <div className="flex items-center gap-2">
                               <ShieldCheck className="w-4 h-4 text-indigo-500" />
                               <span className="text-sm font-black text-white">{selectedCase.consensus} Jurors</span>
                            </div>
                         </div>
                         <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                            <span className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">SLA Impact</span>
                            <span className="text-sm font-black text-green-500 uppercase tracking-tighter">PRESERVED</span>
                         </div>
                      </div>

                      <div>
                         <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-3 flex items-center gap-2">
                            <Binary className="w-3.5 h-3.5 text-indigo-500" /> Cryptographic Manifest
                         </h4>
                         <div className="p-4 bg-black border border-white/5 rounded-xl font-mono text-[10px] text-gray-500 break-all space-y-4">
                            <div>
                               <span className="text-gray-700 block mb-1">SHA-256 HASH:</span>
                               <code className="text-indigo-400">{selectedCase.manifest_hash}</code>
                            </div>
                            <div className="pt-2 border-t border-white/5 flex justify-between items-center">
                               <span className="text-[8px] font-black uppercase text-gray-700">Root Node: 0x8A2E...F91C</span>
                               <button className="flex items-center gap-1.5 hover:text-white transition-colors uppercase text-[9px] font-black">
                                  Verify Proof <ChevronRight className="w-3 h-3" />
                                </button>
                            </div>
                         </div>
                      </div>

                      <div className="p-5 border border-amber-500/20 bg-amber-500/5 rounded-xl flex items-center gap-6">
                         <Scale className="w-10 h-10 text-amber-500" />
                         <div>
                            <p className="text-[11px] text-white font-black uppercase tracking-tighter">Economic Recap</p>
                            <p className="text-sm font-black text-white tracking-tighter">{selectedCase.economic_impact}</p>
                         </div>
                      </div>
                   </div>

                   <div className="pt-6 border-t border-white/5 flex gap-4">
                      <button className="flex-1 py-4 bg-white text-black font-black text-xs uppercase tracking-widest hover:bg-indigo-500 hover:text-white transition-all rounded shadow-xl flex items-center justify-center gap-2">
                         <Download className="w-4 h-4" /> Export Case Shard
                      </button>
                      <button className="p-4 bg-white/5 border border-white/10 rounded hover:bg-white/10 transition-colors">
                         <ExternalLink className="w-4 h-4 text-gray-500" />
                      </button>
                   </div>
                </div>
             ) : (
                <div className="h-full border-2 border-white/5 border-dashed rounded-3xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale transition-all duration-700">
                   <Gavel className="w-20 h-20 text-gray-800 mb-8 animate-pulse" />
                   <h2 className="text-2xl font-black text-gray-600 uppercase tracking-[0.3em] mb-4">Adjudication Point</h2>
                   <p className="text-xs text-gray-800 font-bold uppercase tracking-widest max-w-sm mx-auto leading-relaxed">
                      Select a historical verdict from the archive to view its forensic manifest, consensus statistics, and the legal precedent established by the biological network.
                   </p>
                </div>
             )}
          </div>

        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-6xl mx-auto w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Protocol Precedent Engine Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Truth is anchored in silicon; justice is defined by humans."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] ARCHIVE_STATE: SYNCHRONIZED</span>
            <span>[*] TOTAL_PRECEDENTS: 842</span>
            <span>[*] VERSION: v3.5.9</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
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
