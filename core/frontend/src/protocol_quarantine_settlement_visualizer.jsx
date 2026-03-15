import React, { useState, useEffect } from 'react';
import { 
  Gavel, 
  ShieldCheck, 
  ShieldX, 
  Fingerprint, 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  Zap, 
  Database, 
  Lock, 
  Unlock, 
  Activity, 
  Award, 
  Flame, 
  Binary, 
  Layers, 
  ChevronRight, 
  Info,
  History,
  Scale,
  Skull
} from 'lucide-react';

/**
 * PROXY PROTOCOL - QUARANTINE SETTLEMENT VISUALIZER (v1.0)
 * "Visualizing the final cryptographic seal of judgment."
 * --------------------------------------------------------
 */

const App = () => {
  const [signatures, setSignatures] = useState([]);
  const [phase, setPhase] = useState('COLLECTING'); // COLLECTING, TALLYING, FINALIZED
  const [verdict, setVerdict] = useState(null); // RESTORE, BAN
  const [isProcessing, setIsProcessing] = useState(false);

  // Mock Appeal Context
  const appealId = "APL-8829-X29";
  const nodeId = "did:proxy:8A2E1C";

  // Simulate incoming signatures
  const triggerAggregation = () => {
    setIsProcessing(true);
    setSignatures([]);
    setPhase('COLLECTING');
    setVerdict(null);

    let count = 0;
    const interval = setInterval(() => {
      count++;
      const newSig = {
        id: `J-8829-${count}`,
        verdict: Math.random() > 0.3 ? 'RESTORE' : 'BAN',
        timestamp: new Date().toLocaleTimeString()
      };
      
      setSignatures(prev => [...prev, newSig]);

      if (count >= 7) {
        clearInterval(interval);
        setTimeout(() => setPhase('TALLYING'), 1000);
        
        setTimeout(() => {
          const restores = [ ...signatures, newSig ].filter(s => s.verdict === 'RESTORE').length;
          const finalResult = restores >= 5 ? 'RESTORE' : 'BAN';
          setVerdict(finalResult);
          setPhase('FINALIZED');
          setIsProcessing(false);
        }, 3000);
      }
    }, 600);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-indigo-500/30 overflow-x-hidden">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl w-full relative z-10 space-y-8 flex-1 flex flex-col">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
              <History className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Settlement Portal</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2 font-mono">
                Quorum Aggregation // Finality Engine // Protocol <span className="text-indigo-400">v3.7.0</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Appeal ID</span>
                   <span className="text-xl font-black text-white tracking-tighter uppercase">{appealId}</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <button 
                  onClick={triggerAggregation}
                  disabled={isProcessing}
                  className="bg-indigo-600 text-white px-6 py-2 rounded font-black text-[10px] uppercase tracking-widest hover:bg-indigo-500 transition-all disabled:opacity-20"
                >
                  Simulate Aggregation
                </button>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 flex-1 items-stretch">
          
          {/* Main Visualizer Arena */}
          <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative overflow-hidden flex flex-col justify-center min-h-[550px]">
             
             {/* Progress Status Bar */}
             <div className="absolute top-0 left-0 w-full p-6 border-b border-white/5 bg-white/[0.01] flex justify-between items-center z-20">
                <div className="flex items-center gap-3">
                   <div className={`w-2 h-2 rounded-full ${phase === 'COLLECTING' ? 'bg-indigo-500 animate-ping' : 'bg-green-500'}`} />
                   <span className="text-[10px] font-black text-white uppercase tracking-widest">{phase.replace('_', ' ')}</span>
                </div>
                <span className="text-[10px] text-gray-700 font-bold uppercase tabular-nums">Signatures: {signatures.length} / 7</span>
             </div>

             {/* Dynamic Center Stage */}
             <div className="relative flex flex-col items-center justify-center py-20">
                {phase === 'COLLECTING' && (
                  <div className="space-y-12 w-full max-w-lg text-center animate-in fade-in duration-700">
                     <div className="relative">
                        <div className="w-32 h-32 rounded-full border-2 border-dashed border-white/10 mx-auto flex items-center justify-center animate-spin-slow" />
                        <Fingerprint className="w-12 h-12 text-indigo-500 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
                     </div>
                     <div className="grid grid-cols-7 gap-4">
                        {[...Array(7)].map((_, i) => (
                           <div 
                            key={i} 
                            className={`h-1 rounded-full transition-all duration-700 ${i < signatures.length ? 'bg-indigo-500 shadow-[0_0_10px_#6366f1]' : 'bg-white/5'}`} 
                           />
                        ))}
                     </div>
                     <p className="text-xs text-gray-600 uppercase font-black tracking-widest">Awaiting Quorum Hardware Sign-off...</p>
                  </div>
                )}

                {phase === 'TALLYING' && (
                  <div className="text-center animate-in zoom-in-95 duration-500">
                     <RefreshCw className="w-20 h-20 text-amber-500 animate-spin mx-auto mb-8" />
                     <h2 className="text-3xl font-black text-white uppercase tracking-tighter">Calculating Schelling Point</h2>
                     <p className="text-xs text-gray-500 mt-2 uppercase tracking-widest">Aggregating TPM_AK Signatures</p>
                  </div>
                )}

                {phase === 'FINALIZED' && (
                  <div className="text-center animate-in zoom-in-95 duration-700">
                     <div className={`p-8 rounded-full border-4 inline-block mb-8 ${verdict === 'RESTORE' ? 'border-green-500 bg-green-500/10 shadow-[0_0_50px_rgba(34,197,94,0.2)]' : 'border-red-600 bg-red-600/10 shadow-[0_0_50px_rgba(220,38,38,0.2)]'}`}>
                        {verdict === 'RESTORE' ? <Award className="w-20 h-20 text-green-500 animate-bounce" /> : <Skull className="w-20 h-20 text-red-600 animate-pulse" />}
                     </div>
                     <h2 className={`text-5xl font-black uppercase tracking-tighter ${verdict === 'RESTORE' ? 'text-green-500' : 'text-red-600'}`}>
                        {verdict === 'RESTORE' ? 'Restoration Sealed' : 'Identity Revoked'}
                     </h2>
                     <p className="text-sm text-gray-500 mt-4 max-w-sm mx-auto leading-relaxed italic">
                        {verdict === 'RESTORE' 
                          ? "The High Court has cleared the node for duty. Reputation has been migrated to the new hardware vessel."
                          : "The appeal has been rejected. The node DID and physical TPM keys are permanently blacklisted."}
                     </p>
                  </div>
                )}
             </div>

             {/* Bottom Information Footer */}
             <div className="mt-auto border-t border-white/5 pt-8 grid grid-cols-2 gap-8 relative z-10">
                <div className="p-4 bg-white/[0.02] border border-white/5 rounded-xl">
                   <span className="text-[9px] text-gray-600 font-black uppercase tracking-widest block mb-2">Subject Standing</span>
                   <div className="flex items-center gap-3">
                      <span className="text-sm font-black text-white uppercase tracking-tighter">{nodeId}</span>
                      <ShieldCheck className="w-4 h-4 text-indigo-400" />
                   </div>
                </div>
                <div className="p-4 bg-white/[0.02] border border-white/5 rounded-xl">
                   <span className="text-[9px] text-gray-600 font-black uppercase tracking-widest block mb-2">Verification Anchor</span>
                   <div className="flex items-center gap-3">
                      <code className="text-xs text-gray-400 font-mono">0x8A2E...F91C</code>
                      <Binary className="w-4 h-4 text-emerald-500" />
                   </div>
                </div>
             </div>
          </div>

          {/* Sidebar: Signature Log & Economic Outcome */}
          <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
             
             {/* Economic Impact Panel */}
             <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 shadow-2xl">
                <h3 className="text-xs font-black text-white uppercase tracking-widest mb-10 flex items-center gap-2 border-b border-white/10 pb-4">
                  <Zap className="w-4 h-4 text-amber-500" /> Outcome Impact
                </h3>
                
                <div className="space-y-8">
                   <div className="flex justify-between items-center text-[11px] font-bold">
                      <span className="text-gray-500 uppercase tracking-tighter">Bond State</span>
                      <span className={verdict === 'BAN' ? 'text-red-500 font-black' : 'text-green-500'}>
                         {phase === 'FINALIZED' ? (verdict === 'BAN' ? 'BURNED (-2.0M)' : 'RESTORED') : 'ESCROWED'}
                      </span>
                   </div>
                   <div className="flex justify-between items-center text-[11px] font-bold">
                      <span className="text-gray-500 uppercase tracking-tighter">Reputation standing</span>
                      <span className={verdict === 'BAN' ? 'text-red-500 font-black' : 'text-white'}>
                         {phase === 'FINALIZED' ? (verdict === 'BAN' ? 'REVOKED' : '884 REP (-10%)') : '982 REP'}
                      </span>
                   </div>
                   
                   <div className="pt-6 border-t border-white/5">
                      <div className={`p-4 rounded-xl flex items-start gap-4 transition-all duration-1000 ${phase === 'FINALIZED' ? 'bg-indigo-500/10 border border-indigo-500/20' : 'bg-black opacity-30'}`}>
                         <Info className={`w-5 h-5 ${phase === 'FINALIZED' ? 'text-indigo-400' : 'text-gray-600'} shrink-0`} />
                         <p className="text-[10px] text-gray-500 leading-relaxed italic">
                           {phase === 'FINALIZED' 
                             ? "Judgment broadcast to 84,000 nodes. All jurisdictional hubs have updated their blacklists via Threat Intelligence API."
                             : "Waiting for quorum finality to execute protocol-level enforcement."}
                         </p>
                      </div>
                   </div>
                </div>
             </div>

             {/* Real-time Signature Log */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl flex-1 flex flex-col shadow-2xl overflow-hidden min-h-[250px]">
                <div className="p-4 bg-white/[0.02] border-b border-white/5 flex justify-between items-center px-6">
                   <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest">Signature Ledger</h3>
                   <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                </div>
                <div className="p-6 font-mono text-[10px] space-y-3 overflow-y-auto flex-1 scrollbar-hide">
                   {signatures.length === 0 && (
                     <div className="text-gray-800 italic">[*] Awaiting aggregation signal...</div>
                   )}
                   {signatures.map((sig, i) => (
                      <div key={i} className="flex justify-between items-center animate-in fade-in slide-in-from-right-2 duration-300">
                         <div className="flex items-center gap-2">
                            <span className="text-indigo-400 font-bold">{sig.id}</span>
                            <ShieldCheck className="w-3 h-3 text-gray-700" />
                         </div>
                         <span className={`font-black ${sig.verdict === 'RESTORE' ? 'text-green-600' : 'text-red-900'}`}>{sig.verdict}</span>
                      </div>
                   ))}
                </div>
             </div>

          </div>

        </div>

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-6xl mx-auto w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-5 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <Activity className="w-4 h-4 text-indigo-500 animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Finality Oracle v1.0.4 Online</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Mathematical finality through human consensus."</span>
         </div>
         <div className="flex gap-10 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] SCHELLING_POINT: ACTIVE</span>
            <span>[*] MAJORITY_THRESHOLD: 5/7</span>
            <span>[*] VERSION: v3.7.0</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scan {
          0% { transform: translateY(-400px); }
          50% { transform: translateY(400px); }
          100% { transform: translateY(-400px); }
        }
        .animate-scan {
          animation: scan 4s ease-in-out infinite;
        }
        .animate-spin-slow {
          animation: spin 15s linear infinite;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
      `}} />

    </div>
  );
};

export default App;
