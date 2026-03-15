import React, { useState, useEffect, useMemo } from 'react';
import { 
  Gavel, 
  Target, 
  Users, 
  ShieldCheck, 
  ShieldAlert, 
  Clock, 
  Fingerprint, 
  RefreshCw, 
  Binary, 
  Database, 
  Cpu, 
  ChevronRight, 
  Search, 
  Hash, 
  Zap, 
  AlertTriangle,
  Globe,
  LayoutGrid,
  Scale,
  XCircle,
  Activity,
  Award,
  CheckCircle2,
  Info,
  Box
} from 'lucide-react';

/**
 * PROXY PROTOCOL - JUROR SELECTION VISUALIZER (v1.1)
 * "The Consensus Draft: Deterministic selection from the biological pool."
 * ----------------------------------------------------------------------
 * v1.1 Fix: Resolved layout overlap by removing rigid height constraints.
 * Implemented auto-scaling for the finalized manifest block.
 */

const App = () => {
  const [phase, setPhase] = useState('WAITING'); // WAITING, REVEAL_HASH, SELECTING, FINALIZED
  const [isProcessing, setIsProcessing] = useState(false);
  const [blockHash, setBlockHash] = useState('');
  const [selectedJurors, setSelectedJurors] = useState([]);

  // Mock Candidate Pool (Super-Elite 950+ REP)
  const [candidates] = useState([
    { id: "NODE_ELITE_X29", rep: 998, region: "US_EAST", status: "CANDIDATE" },
    { id: "NODE_ALPHA_001", rep: 985, region: "EU_WEST", status: "CANDIDATE" },
    { id: "NODE_GAMMA_992", rep: 978, region: "ASIA_SE", status: "CANDIDATE" },
    { id: "NODE_WHALE_04", rep: 992, region: "US_WEST", status: "CANDIDATE" },
    { id: "NODE_SIGMA_77", rep: 962, region: "LATAM", status: "CANDIDATE" },
    { id: "NODE_OMRON_02", rep: 955, region: "JP_EAST", status: "CANDIDATE" },
    { id: "NODE_BETA_82", rep: 968, region: "EU_NORTH", status: "CANDIDATE" },
    { id: "NODE_DELTA_09", rep: 952, region: "US_SOUTH", status: "CANDIDATE" },
    { id: "NODE_KAPPA_41", rep: 974, region: "ASIA_NE", status: "CANDIDATE" },
    { id: "NODE_ZETA_01", rep: 990, region: "ME_NORTH", status: "CANDIDATE" },
  ]);

  const startsIn = "14m 22s";

  const triggerDraft = () => {
    setPhase('REVEAL_HASH');
    setIsProcessing(true);
    
    // Step 1: Reveal Entropy (Bitcoin Block Hash)
    setTimeout(() => {
      setBlockHash('0000000000000000000b9231...f91c');
      setPhase('SELECTING');
      
      // Step 2: Deterministic Selection Logic Simulation
      let currentSelected = [];
      const interval = setInterval(() => {
        if (currentSelected.length < 7) {
          const remaining = candidates.filter(c => !currentSelected.includes(c.id));
          const randomIdx = Math.floor(Math.random() * remaining.length);
          currentSelected.push(remaining[randomIdx].id);
          setSelectedJurors([...currentSelected]);
        } else {
          clearInterval(interval);
          setPhase('FINALIZED');
          setIsProcessing(false);
        }
      }, 600);
    }, 2500);
  };

  const getStatusColor = (id) => {
    if (phase === 'FINALIZED' && selectedJurors.includes(id)) return 'border-amber-500 bg-amber-500/10 text-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.2)]';
    if (phase === 'SELECTING' && selectedJurors.includes(id)) return 'border-indigo-500 bg-indigo-500/10 text-indigo-400 animate-pulse';
    return 'border-white/5 bg-black/40 text-gray-700';
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-amber-500/30 overflow-x-hidden">
      
      {/* Background matrix pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl w-full relative z-10 space-y-10 flex flex-col">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl shadow-2xl">
              <Scale className="w-8 h-8 text-amber-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none text-glow">High Court Draft</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Deterministic Selection // VRF Protocol <span className="text-indigo-400">v3.5.3</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Candidate Pool</span>
                   <span className="text-xl font-black text-white tracking-tighter">58 <span className="text-[10px] text-indigo-500">NODES</span></span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Court Seats</span>
                   <span className="text-xl font-black text-white tracking-tighter">07 <span className="text-[10px] text-amber-500">SLOTS</span></span>
                </div>
             </div>
          </div>
        </header>

        {/* The Draft Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Main Visualizer: The Draft Arena */}
          <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative overflow-hidden flex flex-col min-h-[500px]">
             
             {/* Progress Status Layer */}
             <div className="flex justify-between items-start mb-12 relative z-10">
                <div>
                   <h3 className="text-xs font-black text-white uppercase tracking-[0.2em] mb-2 flex items-center gap-2">
                     <Target className="w-4 h-4 text-amber-500" /> Selection Ceremony
                   </h3>
                   <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${isProcessing ? 'bg-indigo-500 animate-ping' : 'bg-gray-800'}`} />
                      <span className="text-[10px] text-gray-500 font-black uppercase tracking-widest">{phase.replace('_', ' ')}</span>
                   </div>
                </div>
                {phase === 'WAITING' && (
                  <div className="text-right">
                     <span className="text-[9px] text-gray-700 uppercase font-black block mb-1">Next Block Estimated</span>
                     <span className="text-2xl font-black text-white tracking-tighter tabular-nums">{startsIn}</span>
                  </div>
                )}
             </div>

             {/* The Deterministic Shuffle Grid */}
             <div className="flex-1 flex flex-col justify-center gap-12 relative z-10 mb-6">
                {phase === 'WAITING' ? (
                  <div className="text-center py-12 animate-in fade-in duration-1000">
                     <div className="p-8 border border-white/5 bg-white/[0.01] rounded-3xl inline-block mb-8 shadow-inner group hover:border-amber-500/20 transition-all">
                        <Clock className="w-16 h-16 text-gray-800 group-hover:text-amber-500 transition-colors" />
                     </div>
                     <h2 className="text-3xl font-black text-white uppercase tracking-tighter mb-4">Awaiting Entropy</h2>
                     <p className="text-sm text-gray-500 max-w-sm mx-auto leading-relaxed italic mb-8">
                        "The High Court cannot be convened until a future block hash is anchored."
                     </p>
                     <button 
                       onClick={triggerDraft}
                       className="px-12 py-4 bg-white text-black font-black text-xs uppercase tracking-[0.3em] rounded hover:bg-amber-500 hover:text-white transition-all shadow-2xl"
                     >
                        Force Manual Draw (SIM)
                     </button>
                  </div>
                ) : (
                  <div className="space-y-12">
                     {/* Entropy Reveal Bar */}
                     <div className={`p-6 border rounded-xl transition-all duration-700 ${blockHash ? 'bg-indigo-500/5 border-indigo-500/30' : 'bg-black border-white/5'}`}>
                        <div className="flex justify-between items-center mb-4">
                           <span className="text-[9px] text-gray-600 font-black uppercase tracking-widest">Entropy Source: BTC_BLOCK_882932</span>
                           {blockHash && <CheckCircle2 className="w-4 h-4 text-indigo-500" />}
                        </div>
                        <div className="font-mono text-[10px] md:text-xs overflow-hidden whitespace-nowrap relative py-2">
                           {!blockHash ? (
                             <div className="flex gap-2 opacity-20">
                                {[...Array(64)].map((_, i) => <span key={i} className="animate-pulse">?</span>)}
                             </div>
                           ) : (
                             <div className="flex gap-1 text-indigo-400 font-bold animate-in slide-in-from-left duration-1000">
                                <span className="text-white opacity-40">0x</span>
                                {blockHash.split('').map((char, i) => (
                                  <span key={i} className="hover:text-white transition-colors" style={{ animationDelay: `${i * 10}ms` }}>{char}</span>
                                ))}
                             </div>
                           )}
                        </div>
                     </div>

                     {/* Candidate Nodes Cluster */}
                     <div className="grid grid-cols-5 md:grid-cols-10 gap-3">
                        {candidates.map((cand) => (
                          <div 
                            key={cand.id}
                            className={`aspect-square rounded-lg border-2 flex items-center justify-center transition-all duration-500 relative group ${getStatusColor(cand.id)}`}
                          >
                             <Cpu className={`w-5 h-5 ${selectedJurors.includes(cand.id) ? 'opacity-100' : 'opacity-20'}`} />
                             <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-30">
                                <div className="bg-black border border-white/10 px-2 py-1 rounded text-[7px] font-black uppercase text-white shadow-2xl">
                                   {cand.id} // {cand.rep} REP
                                </div>
                             </div>
                          </div>
                        ))}
                     </div>
                  </div>
                )}
             </div>

             {/* Final Manifest (Bottom Overlay) */}
             {phase === 'FINALIZED' && (
               <div className="mt-6 pt-8 border-t border-white/5 animate-in slide-in-from-bottom-4 duration-700 flex flex-col md:flex-row gap-8 items-center bg-black/40 p-6 rounded-xl">
                  <div className="flex items-center gap-6 flex-1">
                     <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-2xl shrink-0">
                        <Award className="w-10 h-10 text-green-500 animate-bounce" />
                     </div>
                     <div>
                        <h4 className="text-lg font-black text-white uppercase tracking-tight">Draft Manifest Finalized</h4>
                        <p className="text-[10px] text-gray-500 italic max-w-sm mt-1">"The Appellate Court for Case SEV-1 has been deterministically seeded."</p>
                     </div>
                  </div>
                  <button className="px-8 py-4 bg-white text-black font-black text-xs uppercase tracking-[0.2em] rounded shadow-2xl hover:bg-amber-500 hover:text-white transition-all whitespace-nowrap">
                     Verify Merkle Proof
                  </button>
               </div>
             )}
          </div>

          {/* Sidebar: Juror List & Quorum Context */}
          <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl flex flex-col shadow-2xl min-h-[400px]">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-8">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <Users className="w-4 h-4 text-indigo-500" /> Court Roster
                   </h3>
                   <span className="text-[9px] text-gray-700 font-bold uppercase tracking-widest">7 Seats</span>
                </div>

                <div className="p-6 flex-1 space-y-4 max-h-[400px] overflow-y-auto scrollbar-hide">
                   {selectedJurors.length > 0 ? (
                     selectedJurors.map((jid, i) => (
                       <div key={jid} className="flex items-center justify-between p-4 bg-white/5 border border-white/5 rounded-xl animate-in slide-in-from-right-2 duration-300" style={{ animationDelay: `${i * 100}ms` }}>
                          <div className="flex items-center gap-4">
                             <div className="text-[10px] font-black text-gray-800">0{i+1}</div>
                             <span className="text-[11px] font-bold text-white uppercase tracking-tighter">{jid}</span>
                          </div>
                          <ShieldCheck className="w-4 h-4 text-green-500" />
                       </div>
                     ))
                   ) : (
                     <div className="h-full flex flex-col items-center justify-center opacity-20 py-20">
                        <Users className="w-12 h-12 mb-4" />
                        <span className="text-[9px] font-black uppercase tracking-widest">Awaiting Roster</span>
                     </div>
                   )}
                </div>

                <div className="p-6 border-t border-white/5 bg-black/40">
                   <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                      <Info className="w-3.5 h-3.5" /> Selection Rule 2.1
                   </h4>
                   <p className="text-[11px] text-gray-500 leading-relaxed italic">
                      "Selection is a one-way deterministic function of the Bitcoin block hash."
                   </p>
                </div>
             </div>
          </div>

        </div>

        {/* Global Security Grid: Fixed responsive card layouts to prevent overlap */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 relative z-10 pb-12">
           <div className="p-6 bg-[#0a0a0a] border border-white/5 rounded-xl flex items-center gap-5 group hover:border-indigo-500/30 transition-all overflow-hidden min-h-[100px]">
              <div className="p-3 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500 group-hover:text-black transition-all shrink-0">
                <Hash className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">Hash Seed</p>
                 <p className="text-[11px] font-bold text-white uppercase tracking-tighter truncate">BLOCK_882932_SHA256</p>
              </div>
           </div>
           <div className="p-6 bg-[#0a0a0a] border border-white/5 rounded-xl flex items-center gap-5 group hover:border-amber-500/30 transition-all overflow-hidden min-h-[100px]">
              <div className="p-3 bg-amber-500/10 rounded-lg group-hover:bg-amber-500 group-hover:text-black transition-all shrink-0">
                <Zap className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">Verification</p>
                 <p className="text-[11px] font-bold text-white uppercase tracking-tighter truncate">STABLE_SHUFFLE_v2</p>
              </div>
           </div>
           <div className="p-6 bg-[#0a0a0a] border border-white/5 rounded-xl flex items-center gap-5 group hover:border-emerald-500/30 transition-all overflow-hidden min-h-[100px]">
              <div className="p-3 bg-emerald-500/10 rounded-lg group-hover:bg-emerald-500 group-hover:text-black transition-all shrink-0">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">Consensus State</p>
                 <p className="text-[11px] font-bold text-white uppercase tracking-tighter truncate">QUORUM_COLLECTING</p>
              </div>
           </div>
        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-6xl w-full mt-auto bg-[#0a0a0a] border border-white/5 rounded-lg p-6 flex flex-col md:flex-row items-center justify-between gap-4 opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-ping shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">VRF Selection Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10 hidden md:block" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic text-center md:text-left">"Randomness is the anchor of decentralized integrity."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest shrink-0">
            <span>[*] EPOCH: 88294</span>
            <span>[*] SEED: SHA256</span>
            <span>[*] VERSION: v3.5.3</span>
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
        .text-glow {
          text-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}} />

    </div>
  );
};

export default App;
