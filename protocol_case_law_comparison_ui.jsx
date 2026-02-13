import React, { useState } from 'react';
import { 
  Split, 
  ShieldCheck, 
  Binary, 
  Activity, 
  Zap, 
  History, 
  Scale, 
  Fingerprint, 
  ChevronRight, 
  ArrowRight, 
  Info, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Layers, 
  Cpu, 
  Database,
  BarChart3,
  Search,
  Maximize2,
  X,
  Target,
  FileText,
  Users,
  Hash
} from 'lucide-react';

/**
 * PROXY PROTOCOL - CASE LAW COMPARISON UI (v1.0)
 * "Differential forensics: Identifying patterns in decentralized justice."
 * -----------------------------------------------------------------------
 */

const App = () => {
  const [isComparing, setIsComparing] = useState(false);
  const [selectedCaseA, setSelectedCaseA] = useState(null);
  const [selectedCaseB, setSelectedCaseB] = useState(null);
  
  const caseId = "CASE-DIFF-ANALYSIS";

  // Mock Archive Data
  const archivedCases = [
    {
      id: "CASE-8829-APP",
      title: "Metadata Forgery",
      verdict: "REJECTED",
      consensus: "6/7",
      region: "ASIA_SE",
      pcr_state: "DRIFT_PCR_7",
      payout: "0 SATS",
      manifest_hash: "0x8A2E...F91C"
    },
    {
      id: "CASE-8421-APP",
      title: "Geofence Drift",
      verdict: "REJECTED",
      consensus: "5/7",
      region: "US_WEST",
      pcr_state: "STABLE",
      payout: "0 SATS",
      manifest_hash: "0xE3B0...427A"
    },
    {
      id: "CASE-8772-APP",
      title: "Notary Validity",
      verdict: "APPROVED",
      consensus: "7/7",
      region: "GLOBAL",
      pcr_state: "STABLE",
      payout: "500k SATS",
      manifest_hash: "0x3B7C...D2A1"
    }
  ];

  const handleCompare = () => {
    setIsComparing(true);
    setTimeout(() => setIsComparing(false), 1500);
  };

  const renderCaseSelector = (slot, current, set) => (
    <div className="flex-1 flex flex-col gap-4">
      <div className="flex justify-between items-center px-2">
        <span className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Analysis Slot {slot}</span>
        {current && <button onClick={() => set(null)} className="text-gray-700 hover:text-white"><X className="w-3 h-3" /></button>}
      </div>
      {!current ? (
        <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-4 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-700" />
            <input 
              type="text" 
              placeholder="SELECT CASE..."
              className="w-full bg-black border border-white/5 rounded-lg py-2 pl-9 pr-3 text-[10px] text-white focus:outline-none focus:border-indigo-500/50 uppercase"
              readOnly
            />
          </div>
          <div className="space-y-2">
            {archivedCases.filter(c => c.id !== selectedCaseA?.id && c.id !== selectedCaseB?.id).map(c => (
              <button 
                key={c.id}
                onClick={() => set(c)}
                className="w-full text-left p-3 rounded-lg border border-white/5 hover:border-white/20 hover:bg-white/[0.02] transition-all flex justify-between items-center group"
              >
                <div>
                   <span className="text-[10px] font-black text-white group-hover:text-indigo-400 transition-colors">{c.id}</span>
                   <p className="text-[9px] text-gray-600 font-bold uppercase">{c.title}</p>
                </div>
                <ChevronRight className="w-3 h-3 text-gray-800" />
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-[#0a0a0a] border border-indigo-500/30 rounded-xl p-6 shadow-2xl animate-in zoom-in-95 duration-300">
           <div className="flex justify-between items-start mb-6">
              <div>
                 <span className="text-[9px] text-indigo-400 font-black uppercase tracking-widest block mb-1">Target Identity</span>
                 <h3 className="text-lg font-black text-white tracking-tighter uppercase">{current.id}</h3>
              </div>
              <div className={`px-2 py-0.5 rounded border text-[8px] font-black uppercase ${current.verdict === 'APPROVED' ? 'bg-green-500/10 border-green-500/20 text-green-500' : 'bg-red-500/10 border-red-500/20 text-red-500'}`}>
                {current.verdict}
              </div>
           </div>
           <div className="grid grid-cols-2 gap-4 text-[10px] font-bold text-gray-500 uppercase tracking-tighter">
              <div>Consensus: <span className="text-white">{current.consensus}</span></div>
              <div className="text-right">Region: <span className="text-white">{current.region}</span></div>
           </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-indigo-500/30 overflow-x-hidden">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl w-full relative z-10 space-y-8 flex-1 flex flex-col">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
              <Split className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Forensic Differential</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Comparative Case Analysis // Quorum Alignment // Protocol <span className="text-indigo-400">v3.6.1</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Compare Mode</span>
                   <span className="text-xl font-black text-white tracking-tighter uppercase">DELTA_SCAN</span>
                </div>
             </div>
          </div>
        </header>

        {/* Comparison Setup Area */}
        <section className="flex flex-col lg:flex-row gap-8 items-start relative">
           {renderCaseSelector("A", selectedCaseA, setSelectedCaseA)}
           
           <div className="hidden lg:flex items-center justify-center pt-12">
              <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-full flex items-center justify-center shadow-2xl relative">
                 <Zap className={`w-5 h-5 ${selectedCaseA && selectedCaseB ? 'text-indigo-500 animate-pulse' : 'text-gray-800'}`} />
                 {selectedCaseA && selectedCaseB && <div className="absolute inset-0 bg-indigo-500/10 rounded-full animate-ping" />}
              </div>
           </div>

           {renderCaseSelector("B", selectedCaseB, setSelectedCaseB)}
        </section>

        {/* Analysis Results */}
        <div className="flex-1">
           {selectedCaseA && selectedCaseB ? (
             <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                
                {/* Visual Differential Grid */}
                <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl overflow-hidden shadow-2xl flex flex-col">
                   <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-8">
                      <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                        <Binary className="w-4 h-4 text-indigo-500" /> Forensic Delta Matrix
                      </h3>
                      <div className="flex items-center gap-4">
                         <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 bg-red-500 rounded-full" />
                            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-widest">Conflict Detected</span>
                         </div>
                         <div className="h-4 w-px bg-white/10" />
                         <button onClick={handleCompare} className="text-[9px] font-black text-indigo-400 hover:text-white uppercase transition-colors">Re-Calculate</button>
                      </div>
                   </div>

                   <div className="divide-y divide-white/5">
                      {[
                        { label: 'Hardware Attestation', valA: selectedCaseA.pcr_state, valB: selectedCaseB.pcr_state, isMismatch: selectedCaseA.pcr_state !== selectedCaseB.pcr_state, icon: Cpu },
                        { label: 'Quorum Majority', valA: selectedCaseA.consensus, valB: selectedCaseB.consensus, isMismatch: selectedCaseA.consensus !== selectedCaseB.consensus, icon: Users },
                        { label: 'Satoshi Payout', valA: selectedCaseA.payout, valB: selectedCaseB.payout, isMismatch: selectedCaseA.payout !== selectedCaseB.payout, icon: Zap },
                        { label: 'Root Manifest', valA: selectedCaseA.manifest_hash, valB: selectedCaseB.manifest_hash, isMismatch: true, icon: Database }
                      ].map((row, i) => (
                        <div key={i} className={`grid grid-cols-1 md:grid-cols-12 p-8 items-center gap-8 group transition-all ${isComparing ? 'opacity-20 blur-sm' : 'opacity-100'}`}>
                           <div className="md:col-span-3 flex items-center gap-4">
                              <div className={`p-2 bg-white/5 rounded border border-white/10 transition-colors ${row.isMismatch ? 'text-amber-500 border-amber-500/30' : 'text-gray-700'}`}>
                                 <row.icon className="w-4 h-4" />
                              </div>
                              <span className="text-[11px] font-black text-gray-500 uppercase tracking-tighter">{row.label}</span>
                           </div>

                           <div className="md:col-span-4 flex justify-center">
                              <code className={`text-[10px] p-2 rounded w-full text-center transition-all ${row.isMismatch && row.label !== 'Root Manifest' ? 'bg-red-500/5 text-red-400 border border-red-500/20' : 'text-gray-500'}`}>
                                {row.valA}
                              </code>
                           </div>

                           <div className="md:col-span-1 flex justify-center">
                              <ArrowRight className={`w-4 h-4 ${row.isMismatch ? 'text-amber-500 animate-pulse' : 'text-gray-800'}`} />
                           </div>

                           <div className="md:col-span-4 flex justify-center">
                              <code className={`text-[10px] p-2 rounded w-full text-center transition-all ${row.isMismatch && row.label !== 'Root Manifest' ? 'bg-green-500/5 text-green-400 border border-green-500/20' : 'text-gray-500'}`}>
                                {row.valB}
                              </code>
                           </div>
                        </div>
                      ))}
                   </div>
                </div>

                {/* Consensus Pattern Analysis */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                   <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl flex flex-col justify-between">
                      <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                         <BarChart3 className="w-4 h-4 text-indigo-500" /> Consensus Drift
                      </h3>
                      <div className="space-y-6">
                         <p className="text-[11px] text-gray-500 leading-relaxed italic">
                           "Case {selectedCaseA.id} showing higher juror alignment (85.7%) compared to {selectedCaseB.id} (71.4%). Correlation analysis suggests {selectedCaseB.id} was processed during a peak network congestion epoch."
                         </p>
                         <div className="pt-4 border-t border-white/5 flex justify-between items-center">
                            <span className="text-[9px] text-gray-700 font-black uppercase">Historical Parity</span>
                            <span className="text-xs font-black text-green-500">NOMINAL_DRIFT</span>
                         </div>
                      </div>
                   </div>

                   <div className="p-8 border border-white/10 bg-indigo-500/5 rounded-xl flex flex-col justify-between relative overflow-hidden group">
                      <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:scale-110 transition-transform">
                         <ShieldCheck className="w-24 h-24 text-white" />
                      </div>
                      <div>
                         <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Info className="w-3.5 h-3.5" /> Adjudicator Tip
                         </h4>
                         <p className="text-xs text-gray-500 leading-relaxed font-medium">
                            Comparative analysis reveals that both cases involve Asia-SE nodes. Auditors should inspect the routing topology for potential jurisdictional hub instability.
                         </p>
                      </div>
                      <button className="w-full mt-8 py-4 bg-white text-black font-black text-[10px] uppercase tracking-widest rounded hover:bg-indigo-500 hover:text-white transition-all shadow-xl flex items-center justify-center gap-2">
                         <FileText className="w-4 h-4" /> Export Differential Report
                      </button>
                   </div>
                </div>
             </div>
           ) : (
             <div className="h-[400px] border-2 border-white/5 border-dashed rounded-3xl flex flex-col items-center justify-center p-20 text-center opacity-30 grayscale transition-all duration-700">
                <Split className="w-20 h-20 text-gray-800 mb-8 animate-pulse" />
                <h2 className="text-2xl font-black text-gray-600 uppercase tracking-[0.3em] mb-4">Select Two Cases</h2>
                <p className="text-sm text-gray-800 font-bold uppercase tracking-widest max-w-sm mx-auto leading-relaxed">
                   Establish a forensic baseline by selecting two historical verdicts to generate a differential manifest of hardware telemetry and consensus alignment.
                </p>
             </div>
           )}
        </div>
      </main>

      {/* Global Status Footer */}
      <footer className="max-w-6xl mx-auto w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-ping shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Comparison Engine Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10 hidden md:block" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic hidden md:block">"Identifying silicon-level variances through comparative audit."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] ANALYSIS_MODE: DIFF</span>
            <span>[*] DATA_PRECEDENT: ACTIVE</span>
            <span>[*] SESSION: {caseId}</span>
            <span>[*] VERSION: v3.6.1</span>
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
        .animate-spin-slow {
          animation: spin 15s linear infinite;
        }
      `}} />

    </div>
  );
};

export default App;
