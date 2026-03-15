import React, { useState, useEffect } from 'react';
import { 
  Gavel, 
  ShieldAlert, 
  Activity, 
  Zap, 
  Cpu, 
  Fingerprint, 
  CheckCircle2, 
  XCircle, 
  Lock, 
  Unlock, 
  RefreshCw, 
  Info, 
  Binary, 
  FileText, 
  Scale, 
  History, 
  ChevronRight, 
  ArrowRight, 
  Search,
  Layers,
  Terminal,
  Database,
  UserCheck,
  ShieldCheck
} from 'lucide-react';

/**
 * PROXY PROTOCOL - QUARANTINE PEER-REVIEW UI (v1.1)
 * "The High Court Bench: Auditing automated detection anomalies."
 * ---------------------------------------------------------------
 * v1.1 Fix: Added missing ShieldCheck icon import to resolve ReferenceError.
 * Optimized view transitions and ensured all forensic icons are mapped.
 */

const App = () => {
  const [view, setView] = useState('DOCKET'); // DOCKET, REVIEW, SIGNING
  const [isProcessing, setIsProcessing] = useState(false);
  const [hasVoted, setHasVoted] = useState(false);
  const [verdict, setVerdict] = useState(null);

  // Mock Appellate Docket
  const [docket] = useState([
    {
      id: "APL-8829-X29",
      did: "did:proxy:8A2E1C",
      node_id: "SENTRY-JP-001",
      reason: "ITERATIVE_PROBING_DETECTED",
      probing_probability: 0.94,
      forensic_distance: 0.12,
      submitted_at: "2h ago",
      reputation: 982,
      statement: "The detected drift was caused by a kernel upgrade (v6.6.1) which modified the PCR 7 PCR_EXTEND behavior. Attached is the hardware manifest for the new kernel state."
    }
  ]);

  const [selectedCase, setSelectedCase] = useState(null);

  const handleStartReview = (c) => {
    setSelectedCase(c);
    setView('REVIEW');
  };

  const castVote = (v) => {
    setVerdict(v);
    setView('SIGNING');
  };

  const handleHardwareSign = () => {
    setIsProcessing(true);
    // Simulate TPM 2.0 RSA-PSS Signing of the verdict
    setTimeout(() => {
      setIsProcessing(false);
      setHasVoted(true);
    }, 2000);
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
              <Scale className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Appellate Bench</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Quarantine Peer-Review // Juror Standing: <span className="text-amber-500">SUPER-ELITE</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Pending Appeals</span>
                   <span className="text-xl font-black text-white tracking-tighter">{docket.length} CASES</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Active Quorum</span>
                   <span className="text-xl font-black text-green-500 tracking-tighter uppercase">SYNCED</span>
                </div>
             </div>
          </div>
        </header>

        {/* VIEW: CASE DOCKET */}
        {view === 'DOCKET' && (
          <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl overflow-hidden shadow-2xl animate-in fade-in duration-500">
             <div className="p-6 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-10">
                <h2 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                  <Activity className="w-4 h-4 text-indigo-500" /> Appeal Queue
                </h2>
                <span className="text-[9px] text-gray-700 font-bold uppercase tracking-widest">High Court v3.6.8</span>
             </div>
             
             <div className="divide-y divide-white/5">
                {docket.map((c) => (
                  <div key={c.id} className="p-10 flex flex-col md:flex-row items-center justify-between hover:bg-white/[0.01] transition-all group gap-8">
                     <div className="flex items-center gap-8 flex-1">
                        <div className="w-16 h-16 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-center justify-center text-red-500 shadow-inner">
                           <ShieldAlert className="w-8 h-8" />
                        </div>
                        <div className="space-y-1">
                           <div className="flex items-center gap-3">
                              <span className="text-lg font-black text-white uppercase tracking-tighter">{c.id}</span>
                              <span className="text-[9px] bg-red-500/10 px-2 py-0.5 rounded text-red-500 font-black uppercase tracking-widest border border-red-500/20">{(c.probing_probability * 100).toFixed(0)}% PROBE</span>
                           </div>
                           <p className="text-sm text-gray-500 font-medium">Origin: {c.node_id} // Subscribed: {c.submitted_at}</p>
                        </div>
                     </div>
                     <button 
                       onClick={() => handleStartReview(c)}
                       className="px-10 py-4 bg-indigo-500 text-black font-black text-xs uppercase tracking-widest hover:bg-indigo-400 transition-all shadow-xl rounded-lg"
                     >
                       Begin Review &rarr;
                     </button>
                  </div>
                ))}
             </div>
          </div>
        )}

        {/* VIEW: REVIEW (Evidence vs Statement) */}
        {view === 'REVIEW' && selectedCase && (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 animate-in fade-in slide-in-from-right-4 duration-500 flex-1">
             {/* Left Pane: Automated Forensic Logic */}
             <div className="md:col-span-6 space-y-6 flex flex-col">
                <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl flex-1 flex flex-col relative overflow-hidden">
                   <div className="absolute top-0 right-0 p-4 opacity-5">
                      <Binary className="w-32 h-32 text-white" />
                   </div>
                   <h3 className="text-xs font-black text-red-500 uppercase tracking-widest mb-10 flex items-center gap-2 border-b border-red-500/10 pb-4">
                     <Zap className="w-4 h-4" /> The Charge: Automated Anomaly
                   </h3>
                   
                   <div className="space-y-8 flex-1">
                      <div className="p-6 bg-black border border-white/5 rounded-xl space-y-4">
                         <div className="flex justify-between items-center text-[10px] font-black uppercase text-gray-500 tracking-widest">
                            <span>Probing Probability</span>
                            <span className="text-red-500">{(selectedCase.probing_probability * 100).toFixed(1)}%</span>
                         </div>
                         <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                            <div className="h-full bg-red-500 shadow-[0_0_10px_#ef4444]" style={{ width: `${selectedCase.probing_probability * 100}%` }} />
                         </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                         <div className="p-5 bg-white/[0.02] border border-white/5 rounded-xl">
                            <span className="text-[9px] text-gray-700 font-black uppercase block mb-1 tracking-widest">Distance</span>
                            <span className="text-sm font-black text-white uppercase">{selectedCase.forensic_distance} <span className="text-[9px] text-gray-700">SIGMA</span></span>
                         </div>
                         <div className="p-5 bg-white/[0.02] border border-white/5 rounded-xl">
                            <span className="text-[9px] text-gray-700 font-black uppercase block mb-1 tracking-widest">Detection Code</span>
                            <span className="text-xs font-black text-red-500 uppercase">PX_DIFF_77</span>
                         </div>
                      </div>

                      <div className="p-6 border border-white/5 bg-black/40 rounded-xl">
                         <h4 className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-2">Automated Heuristic Conclusion</h4>
                         <p className="text-xs text-gray-400 leading-relaxed italic">
                           "Analytical correlation detects micro-adjustments in faked dHash telemetry below the 15% distance threshold, suggesting deliberate probing of the High Court's detection zoning."
                         </p>
                      </div>
                   </div>
                </div>
             </div>

             {/* Right Pane: Human Appeal Statement */}
             <div className="md:col-span-6 space-y-6 flex flex-col">
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 shadow-2xl flex-1 flex flex-col relative overflow-hidden">
                   <h3 className="text-xs font-black text-indigo-500 uppercase tracking-widest mb-10 flex items-center gap-2 border-b border-indigo-500/10 pb-4">
                     <UserCheck className="w-4 h-4" /> The Defense: Operator Statement
                   </h3>
                   
                   <div className="space-y-8 flex-1">
                      <div className="p-8 bg-indigo-500/5 border border-indigo-500/10 rounded-2xl min-h-[160px]">
                         <p className="text-sm text-gray-300 leading-relaxed italic font-medium">
                           "{selectedCase.statement}"
                         </p>
                      </div>

                      <div className="space-y-4">
                         <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest flex items-center gap-2">
                           <Layers className="w-3.5 h-3.5 text-indigo-500" /> Attached Forensic Evidence
                         </h4>
                         <div className="grid grid-cols-1 gap-3">
                            <div className="p-4 bg-black border border-white/5 rounded-xl flex items-center justify-between group hover:border-indigo-500/30 transition-all cursor-pointer">
                               <div className="flex items-center gap-4">
                                  <Database className="w-4 h-4 text-gray-700 group-hover:text-indigo-400" />
                                  <span className="text-[10px] text-gray-500 font-bold uppercase">Kernel_Attestation_Log.bin</span>
                               </div>
                               <ChevronRight className="w-3 h-3 text-gray-800" />
                            </div>
                            <div className="p-4 bg-black border border-white/5 rounded-xl flex items-center justify-between group hover:border-indigo-500/30 transition-all cursor-pointer">
                               <div className="flex items-center gap-4">
                                  <Cpu className="w-4 h-4 text-gray-700 group-hover:text-indigo-400" />
                                  <span className="text-[10px] text-gray-500 font-bold uppercase">TPM_Quote_Fresh_v2.sig</span>
                               </div>
                               <ChevronRight className="w-3 h-3 text-gray-800" />
                            </div>
                         </div>
                      </div>
                   </div>

                   <div className="pt-10 border-t border-white/5 flex gap-4 mt-8">
                      <button 
                        onClick={() => castVote('RESTORE')}
                        className="flex-1 py-4 bg-green-500 text-black font-black text-xs uppercase tracking-widest hover:bg-green-400 transition-all rounded shadow-xl flex items-center justify-center gap-2"
                      >
                         <ShieldCheck className="w-4 h-4" /> Restore Node
                      </button>
                      <button 
                        onClick={() => castVote('BAN')}
                        className="flex-1 py-4 bg-red-600 text-white font-black text-xs uppercase tracking-widest hover:bg-red-500 transition-all rounded shadow-xl flex items-center justify-center gap-2"
                      >
                         <XCircle className="w-4 h-4" /> Confirm Ban
                      </button>
                   </div>
                </div>
             </div>
          </div>
        )}

        {/* VIEW: SIGNING (Hardware Ceremony) */}
        {view === 'SIGNING' && (
          <div className="flex-1 flex items-center justify-center animate-in zoom-in-95 duration-500">
             <div className="bg-[#0a0a0a] border border-white/10 rounded-3xl p-12 max-w-lg w-full shadow-2xl text-center flex flex-col items-center">
                {!hasVoted ? (
                  <>
                    <div className="w-24 h-24 bg-indigo-500/10 border border-indigo-500/20 rounded-full flex items-center justify-center mb-8 relative">
                       <Fingerprint className={`w-10 h-10 text-indigo-500 ${isProcessing ? 'animate-pulse' : ''}`} />
                       {isProcessing && <div className="absolute inset-0 bg-indigo-500/20 rounded-full animate-ping" />}
                    </div>
                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-4">Hardware Finality</h2>
                    <p className="text-xs text-gray-500 mb-10 leading-relaxed italic max-w-xs">
                      "Confirming verdict: <span className={verdict === 'RESTORE' ? 'text-green-500' : 'text-red-500'}>{verdict}</span>. This judgment will be signed by your non-exportable TPM identity key."
                    </p>
                    <button 
                      onClick={handleHardwareSign}
                      disabled={isProcessing}
                      className="w-full py-5 bg-indigo-500 text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-400 transition-all rounded-xl shadow-2xl flex items-center justify-center gap-3"
                    >
                       {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
                       {isProcessing ? 'Generating RSA-PSS Proof...' : 'Authorize Verdict Signature'}
                    </button>
                    <button onClick={() => setView('REVIEW')} className="mt-6 text-[10px] font-black uppercase text-gray-700 hover:text-white transition-colors tracking-widest">
                       Back to Evidence
                    </button>
                  </>
                ) : (
                  <div className="animate-in fade-in duration-700">
                     <div className="w-24 h-24 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mx-auto mb-8">
                        <CheckCircle2 className="w-12 h-12 text-green-500 animate-bounce" />
                     </div>
                     <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-2">Verdict Broadcast</h2>
                     <p className="text-xs text-gray-500 mb-10 uppercase tracking-widest font-black">
                        Signature Anchored // Waiting for Quorum
                     </p>
                     <div className="p-4 bg-black border border-white/5 rounded-xl mono text-[10px] text-gray-700 mb-10">
                        RECEIPT: 0x8A2E...{Math.random().toString(16).slice(2, 10).toUpperCase()}
                     </div>
                     <button onClick={() => window.location.reload()} className="px-12 py-4 bg-white text-black font-black text-xs uppercase tracking-[0.2em] rounded-lg shadow-2xl hover:bg-indigo-500 hover:text-white transition-all">
                        Exit Chamber
                     </button>
                  </div>
                )}
             </div>
          </div>
        )}

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-6xl mx-auto w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-6 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Adjudication Quorum Active</span>
            </div>
            <div className="h-4 w-px bg-white/10 hidden md:block" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic hidden md:block">"Pruning the network through biological consensus."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest shrink-0">
            <span>[*] HUB_VITALITY: 100%</span>
            <span>[*] SIGNATURE: RSA_PSS_2048</span>
            <span>[*] VERSION: v3.6.8</span>
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
          animation: spin 8s linear infinite;
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
