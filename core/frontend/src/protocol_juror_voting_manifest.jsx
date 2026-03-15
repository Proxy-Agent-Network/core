import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Gavel, 
  Users, 
  Lock, 
  Unlock, 
  RefreshCw, 
  Fingerprint, 
  Activity, 
  TrendingUp, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Info, 
  Binary, 
  Database, 
  Zap,
  ArrowRight,
  ShieldAlert,
  Flame,
  Award
} from 'lucide-react';

/**
 * PROXY PROTOCOL - JUROR VOTING MANIFEST (v1.0)
 * "Visualizing the 7-Signature Quorum for final settlement."
 * --------------------------------------------------------
 */

const App = () => {
  const caseId = "CASE-8829-APP";
  const [signedCount, setSignedCount] = useState(4);
  const [isFinalizing, setIsFinalizing] = useState(false);
  const [isSettled, setIsSettled] = useState(false);
  
  // Mock Juror Slots
  const jurors = [
    { id: 'J-88293X', status: 'SIGNED', verdict: 'APPROVE' },
    { id: 'J-77141Y', status: 'SIGNED', verdict: 'APPROVE' },
    { id: 'J-00421Z', status: 'SIGNED', verdict: 'REJECT' },
    { id: 'J-11294A', status: 'SIGNED', verdict: 'APPROVE' },
    { id: 'J-PENDING-05', status: 'WAITING', verdict: null },
    { id: 'J-PENDING-06', status: 'WAITING', verdict: null },
    { id: 'J-PENDING-07', status: 'WAITING', verdict: null }
  ];

  const triggerSimulation = () => {
    setIsFinalizing(true);
    // Simulate final signatures arriving
    setTimeout(() => {
      setSignedCount(7);
      setIsSettled(true);
      setIsFinalizing(false);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-amber-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-5xl w-full relative z-10 space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl shadow-2xl">
              <Gavel className="w-8 h-8 text-amber-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none text-glow">Voting Manifest</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Quorum Finalization // Protocol <span className="text-amber-500">v3.5.7</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Case ID</span>
                   <span className="text-xl font-black text-white tracking-tighter">{caseId}</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Signatures</span>
                   <span className="text-xl font-black text-amber-500 tracking-tighter tabular-nums">{signedCount}<span className="text-gray-700">/7</span></span>
                </div>
             </div>
          </div>
        </header>

        {/* Voting Arena */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-stretch">
           
           {/* The 7 Slots */}
           <div className="md:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative overflow-hidden flex flex-col justify-between h-[500px]">
              <div className="flex justify-between items-start mb-8">
                 <div>
                    <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-2">
                      <Users className="w-4 h-4 text-indigo-500" /> Multi-Sig Quorum Grid
                    </h3>
                    <p className="text-[10px] text-gray-600 uppercase font-bold mt-1">Blinded Identity Attribution</p>
                 </div>
                 {isSettled && (
                   <div className="bg-green-500/10 border border-green-500/20 px-4 py-1.5 rounded flex items-center gap-3 animate-in zoom-in-95 duration-500">
                      <ShieldCheck className="w-4 h-4 text-green-500" />
                      <span className="text-[10px] text-green-500 font-black uppercase tracking-widest">Consensus Locked</span>
                   </div>
                 )}
              </div>

              <div className="grid grid-cols-4 md:grid-cols-7 gap-6 mb-12">
                 {jurors.map((j, i) => {
                   const isSigned = i < signedCount;
                   return (
                     <div key={i} className="flex flex-col items-center gap-4">
                        <div className={`w-14 h-14 rounded-2xl border-2 flex items-center justify-center transition-all duration-700 relative ${
                          isSigned 
                            ? 'bg-amber-500/10 border-amber-500 shadow-[0_0_20px_rgba(245,158,11,0.2)]' 
                            : 'bg-black border-white/5 opacity-40'
                        }`}>
                           <Fingerprint className={`w-7 h-7 ${isSigned ? 'text-amber-500' : 'text-gray-800'}`} />
                           {isSigned && (
                             <div className="absolute -top-1 -right-1">
                                <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center border-2 border-black">
                                   <CheckCircle2 className="w-2.5 h-2.5 text-black" />
                                </div>
                             </div>
                           )}
                        </div>
                        <span className={`text-[8px] font-black uppercase tracking-tighter ${isSigned ? 'text-white' : 'text-gray-800'}`}>
                           {j.id.slice(0, 8)}
                        </span>
                     </div>
                   );
                 })}
              </div>

              <div className="mt-auto pt-8 border-t border-white/5">
                 {!isSettled ? (
                   <div className="space-y-6">
                      <div className="flex justify-between items-end mb-2">
                         <span className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Majority Progress (57.1%)</span>
                         <span className="text-[10px] text-indigo-400 font-black">Awaiting 3 Jurors</span>
                      </div>
                      <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                         <div className="h-full bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.5)] transition-all duration-1000" style={{ width: '57.1%' }} />
                      </div>
                      <button 
                        onClick={triggerSimulation}
                        disabled={isFinalizing}
                        className="w-full py-4 bg-white/5 border border-white/10 text-gray-500 hover:text-white transition-all text-[10px] font-black uppercase tracking-widest rounded-xl"
                      >
                         Simulate Final Sign-Off
                      </button>
                   </div>
                 ) : (
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center animate-in slide-in-from-bottom-4 duration-700">
                      <div className="flex items-center gap-6">
                         <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-2xl">
                            <Award className="w-10 h-10 text-green-500 animate-bounce" />
                         </div>
                         <div>
                            <h4 className="text-lg font-black text-white uppercase tracking-tight">Verdict Finalized</h4>
                            <p className="text-[10px] text-gray-500 italic uppercase">Majority APPROVE (6 / 7)</p>
                         </div>
                      </div>
                      <div className="text-right">
                         <span className="text-[9px] text-gray-600 font-black uppercase block mb-1">Audit Anchor</span>
                         <code className="text-xs text-indigo-400 font-mono">0x8A2E...F91C</code>
                      </div>
                   </div>
                 )}
              </div>
           </div>

           {/* Sidebar: Economic Tally */}
           <div className="md:col-span-4 flex flex-col gap-6">
              <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-8 shadow-2xl flex flex-col flex-1 h-full">
                 <h3 className="text-xs font-black text-white uppercase tracking-widest mb-10 border-b border-white/10 pb-4 flex items-center gap-2">
                   <Zap className="w-4 h-4 text-amber-500" /> Economic Resolution
                 </h3>
                 
                 <div className="space-y-10 flex-1">
                    <div>
                       <span className="text-[10px] text-gray-600 font-black uppercase block mb-4 tracking-widest">Schelling Tally</span>
                       <div className="space-y-4">
                          <div className="flex justify-between items-center text-xs">
                             <span className="text-green-500 font-bold uppercase tracking-widest">Approve</span>
                             <span className="text-white font-black">{isSettled ? 6 : 3}</span>
                          </div>
                          <div className="flex justify-between items-center text-xs">
                             <span className="text-red-500 font-bold uppercase tracking-widest">Reject</span>
                             <span className="text-white font-black">1</span>
                          </div>
                       </div>
                    </div>

                    <div className="pt-8 border-t border-white/5">
                       <div className={`p-4 rounded-xl border flex flex-col gap-2 ${isSettled ? 'bg-red-500/10 border-red-500/30' : 'bg-white/5 border-white/10 opacity-30'}`}>
                          <div className="flex justify-between items-center">
                             <span className="text-[9px] text-gray-500 uppercase font-black tracking-widest">Punitive Slashes</span>
                             {isSettled && <Flame className="w-4 h-4 text-red-500 animate-pulse" />}
                          </div>
                          <span className={`text-sm font-black uppercase ${isSettled ? 'text-red-500' : 'text-gray-700'}`}>
                             {isSettled ? '1 Juror Slashed (-600k S)' : 'Awaiting Finality'}
                          </span>
                       </div>
                    </div>
                 </div>

                 <div className="mt-8 pt-8 border-t border-white/5">
                    <button 
                      className={`w-full py-4 rounded-lg font-black text-xs uppercase tracking-widest transition-all ${
                        isSettled ? 'bg-indigo-600 text-white shadow-xl hover:bg-indigo-500' : 'bg-white/5 border border-white/10 text-gray-700 cursor-not-allowed'
                      }`}
                      disabled={!isSettled}
                    >
                       View Final Forensic Report
                    </button>
                 </div>
              </div>
           </div>
        </div>

        {/* Global Security Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 relative z-10">
           <div className="p-6 bg-white/[0.02] border border-white/5 rounded-xl flex items-center gap-6 group hover:border-indigo-500/30 transition-all">
              <div className="p-3 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500 group-hover:text-black transition-all">
                <Database className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">Registry Lock</p>
                 <p className="text-sm font-bold text-white uppercase tracking-tighter truncate">EPOCH_88294_SYNC</p>
              </div>
           </div>
           <div className="p-6 bg-white/[0.02] border border-white/5 rounded-xl flex items-center gap-6 group hover:border-green-500/30 transition-all">
              <div className="p-3 bg-green-500/10 rounded-lg group-hover:bg-green-500 group-hover:text-black transition-all">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">Signature Integrity</p>
                 <p className="text-sm font-bold text-white uppercase tracking-tighter truncate">RSA_PSS_VERIFIED</p>
              </div>
           </div>
           <div className="p-6 bg-white/[0.02] border border-white/5 rounded-xl flex items-center gap-6 group hover:border-amber-500/30 transition-all">
              <div className="p-3 bg-amber-500/10 rounded-lg group-hover:bg-amber-500 group-hover:text-black transition-all">
                <Binary className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">Consensus Mode</p>
                 <p className="text-sm font-bold text-white uppercase tracking-tighter truncate">SCHELLING_POINT_V1</p>
              </div>
           </div>
        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-5xl w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className={`w-1.5 h-1.5 rounded-full animate-pulse ${isSettled ? 'bg-green-500' : 'bg-amber-500'}`} />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Verdict Aggregator v1.0.4 Online</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter hidden md:block italic">"Mathematical finality achieved through biological consensus."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] QUORUM_SIZE: 7</span>
            <span>[*] VERSION: v3.5.7</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scan {
          0% { transform: translateY(-80px); }
          50% { transform: translateY(80px); }
          100% { transform: translateY(-80px); }
        }
        .animate-scan {
          animation: scan 3s ease-in-out infinite;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
      `}} />

    </div>
  );
};

export default App;
