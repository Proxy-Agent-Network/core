import React, { useState, useEffect, useMemo } from 'react';
import { 
  Gavel, 
  ShieldAlert, 
  ShieldCheck, 
  Clock, 
  Lock, 
  Unlock, 
  Fingerprint, 
  Database, 
  Activity, 
  RefreshCw, 
  ChevronRight, 
  ArrowRight, 
  CheckCircle2, 
  Binary, 
  Terminal, 
  Info,
  Layers,
  Zap,
  Eye,
  XCircle,
  AlertTriangle,
  Cpu
} from 'lucide-react';

/**
 * PROXY PROTOCOL - JUROR RESPONSE DASHBOARD (v1.0)
 * "The forensic workstation for drafted High Court nodes."
 * ----------------------------------------------------
 */

const App = () => {
  const [view, setView] = useState('SUMMONS'); // SUMMONS, UNLOCKING, WORKSTATION
  const [isProcessing, setIsProcessing] = useState(false);
  const [timeLeft, setTimeLeft] = useState(14200); // ~4 hours in seconds
  
  // Mock Case Data (Injected via PGP summons packet)
  const [caseData] = useState({
    id: "CASE-8829-APP",
    type: "PROTOCOL_BREACH",
    severity: "CRITICAL",
    potential_yield: 2500,
    evidence_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    summary: "Suspicion of coordinated dHash collision across 4 regional hubs."
  });

  // Handle Response Countdown
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => Math.max(0, prev - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h}h ${m}m ${s}s`;
  };

  const handleAccept = () => {
    setIsProcessing(true);
    // Simulate API call to juror_summoning_api/acknowledge
    setTimeout(() => {
      setIsProcessing(false);
      setView('UNLOCKING');
    }, 1500);
  };

  const handleUnseal = () => {
    setIsProcessing(true);
    // Simulate TPM 2.0 RSA-OAEP Decryption of the evidence shard
    setTimeout(() => {
      setIsProcessing(false);
      setView('WORKSTATION');
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-amber-500/30 overflow-x-hidden">
      
      {/* Background Warning Mesh */}
      <div className={`fixed inset-0 pointer-events-none transition-opacity duration-1000 ${view === 'SUMMONS' ? 'opacity-10' : 'opacity-[0.02]'} z-0`} 
           style={{ 
             backgroundImage: `radial-gradient(${view === 'SUMMONS' ? '#f59e0b' : '#fff'} 1px, transparent 1px)`, 
             backgroundSize: '40px 40px' 
           }} />

      <main className="max-w-4xl w-full relative z-10">
        
        {/* VIEW 1: THE SUMMONS (Call to Duty) */}
        {view === 'SUMMONS' && (
          <div className="space-y-8 animate-in fade-in zoom-in-95 duration-500">
             <div className="bg-[#0a0a0a] border-2 border-amber-500/40 rounded-2xl overflow-hidden shadow-[0_0_50px_rgba(245,158,11,0.1)]">
                <div className="bg-amber-500 p-3 text-black flex justify-between items-center px-10">
                   <span className="text-[10px] font-black uppercase tracking-[0.3em] flex items-center gap-2">
                     <ShieldAlert className="w-3 h-3" /> Mandatory Protocol Convocation
                   </span>
                   <span className="text-[10px] font-black uppercase tracking-widest tabular-nums">Expires: {formatTime(timeLeft)}</span>
                </div>

                <div className="p-10 md:p-14 text-center space-y-10">
                   <div className="w-24 h-24 bg-amber-500/10 border border-amber-500/20 rounded-3xl flex items-center justify-center mx-auto shadow-inner relative">
                      <Gavel className="w-12 h-12 text-amber-500 animate-pulse" />
                      <div className="absolute inset-0 bg-amber-500/5 rounded-3xl animate-ping" />
                   </div>

                   <div className="space-y-4">
                      <h2 className="text-3xl font-black text-white uppercase tracking-tighter">Draft Selection Confirmed</h2>
                      <p className="text-sm text-gray-500 leading-relaxed max-w-md mx-auto italic">
                        "Your hardware ID has been deterministically selected for High Court Adjudication on Case {caseData.id}. You have been summoned by the next-block entropy rule."
                      </p>
                   </div>

                   <div className="grid grid-cols-2 gap-6 text-left max-w-lg mx-auto">
                      <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                         <span className="text-[9px] text-gray-600 uppercase font-black block mb-1 tracking-widest">Case Category</span>
                         <span className="text-sm font-black text-white uppercase">{caseData.type}</span>
                      </div>
                      <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                         <span className="text-[9px] text-gray-600 uppercase font-black block mb-1 tracking-widest">Est. Reward</span>
                         <span className="text-sm font-black text-green-500 uppercase">{caseData.potential_yield} SATS</span>
                      </div>
                   </div>

                   <div className="pt-4 space-y-4">
                      <button 
                        onClick={handleAccept}
                        disabled={isProcessing}
                        className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.4em] hover:bg-amber-500 hover:text-white transition-all rounded-xl shadow-2xl flex items-center justify-center gap-3 disabled:opacity-20"
                      >
                         {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
                         Accept Summons & Sign
                      </button>
                      <p className="text-[9px] text-gray-700 font-bold uppercase tracking-widest">
                        *Failure to acknowledge within {formatTime(timeLeft)} triggers -50 REP decay.
                      </p>
                   </div>
                </div>
             </div>
          </div>
        )}

        {/* VIEW 2: UNLOCKING (Evidence Ceremony) */}
        {view === 'UNLOCKING' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
             <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-12 shadow-2xl text-center flex flex-col items-center">
                <div className="w-20 h-20 bg-indigo-500/10 border border-indigo-500/20 rounded-full flex items-center justify-center mb-8 relative">
                   <Lock className={`w-8 h-8 text-indigo-500 ${isProcessing ? 'animate-pulse' : ''}`} />
                   {isProcessing && <div className="absolute inset-0 bg-indigo-500/20 rounded-full animate-ping" />}
                </div>

                <div className="space-y-4 mb-12">
                   <h2 className="text-2xl font-black text-white uppercase tracking-tighter">Evidence Shard Encrypted</h2>
                   <p className="text-xs text-gray-500 max-w-sm leading-relaxed italic">
                     "To maintain absolute zero-knowledge, the evidence manifest is sealed with your node's public key. You must perform a hardware unseal to initiate deliberation."
                   </p>
                </div>

                <div className="w-full bg-black/40 border border-white/5 rounded-xl p-6 mb-10 flex flex-col items-center gap-4">
                   <Binary className="w-6 h-6 text-gray-700" />
                   <div className="w-full space-y-2">
                      <div className="flex justify-between text-[9px] font-black uppercase tracking-widest text-gray-600">
                         <span>TPM_Hierarchy_Access</span>
                         <span>Ready</span>
                      </div>
                      <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                         <div className="h-full bg-indigo-500 opacity-60" style={{ width: '100%' }} />
                      </div>
                   </div>
                </div>

                <button 
                  onClick={handleUnseal}
                  disabled={isProcessing}
                  className="w-full py-5 bg-indigo-500 text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-400 transition-all rounded-xl shadow-[0_0_40px_rgba(99,102,241,0.2)] flex items-center justify-center gap-3"
                >
                  {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Fingerprint className="w-4 h-4" />}
                  Invoke Hardware Unseal
                </button>
             </div>
          </div>
        )}

        {/* VIEW 3: WORKSTATION (Deliberation Ready) */}
        {view === 'WORKSTATION' && (
          <div className="space-y-8 animate-in fade-in zoom-in-95 duration-500">
             <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
                {/* Main Evidence Viewer */}
                <div className="md:col-span-8 space-y-6">
                   <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl flex flex-col h-[550px]">
                      <div className="flex justify-between items-start mb-8 border-b border-white/5 pb-6">
                         <div>
                            <span className="text-[10px] text-indigo-500 font-black uppercase tracking-widest block mb-1">Evidence Locker Unlocked</span>
                            <h2 className="text-xl font-black text-white uppercase tracking-tight">{caseData.id} Adjudication</h2>
                         </div>
                         <div className="p-3 bg-green-500/10 rounded-lg">
                            <Unlock className="w-5 h-5 text-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
                         </div>
                      </div>

                      <div className="flex-1 space-y-8 overflow-y-auto pr-2 scrollbar-hide">
                         <div className="space-y-4">
                            <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest flex items-center gap-2">
                               <Info className="w-3.5 h-3.5 text-amber-500" /> Executive Summary
                            </h4>
                            <div className="bg-black/60 border border-white/5 p-5 rounded-xl text-sm text-gray-400 leading-relaxed italic font-medium">
                               "{caseData.summary}"
                            </div>
                         </div>

                         <div className="space-y-4">
                            <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest flex items-center gap-2">
                               <Database className="w-3.5 h-3.5 text-indigo-500" /> Forensic Proof Blob
                            </h4>
                            <div className="bg-black border border-white/5 p-6 rounded-xl font-mono text-[10px] text-green-500/70 leading-relaxed break-all shadow-inner">
                               {`{ "event": "DHASH_COLLISION", "original_node": "0x442F", "similarity": 0.9842, "pcr_snapshot": "${caseData.evidence_hash.substring(0, 32)}...", "timestamp": ${Math.floor(Date.now()/1000)} }`}
                            </div>
                         </div>

                         <div className="p-5 border border-indigo-500/20 bg-indigo-500/5 rounded-xl flex items-center gap-6">
                            <Binary className="w-10 h-10 text-indigo-400" />
                            <div>
                               <p className="text-[11px] text-white font-black uppercase">Hardware Context Validated</p>
                               <p className="text-[10px] text-gray-600 font-bold">SHA256 Manifest: {caseData.evidence_hash.substring(0, 24)}...</p>
                            </div>
                         </div>
                      </div>

                      <div className="mt-8 pt-8 border-t border-white/5 flex justify-between items-center">
                         <span className="text-[9px] text-gray-600 font-black uppercase tracking-widest">Protocol Standing Check: OK</span>
                         <button className="flex items-center gap-2 text-[10px] text-gray-400 hover:text-white transition-colors uppercase font-black">
                            Enter Deliberation Chat <ArrowRight className="w-3 h-3" />
                         </button>
                      </div>
                   </div>
                </div>

                {/* Sidebar: Verdict Console */}
                <div className="md:col-span-4 space-y-6">
                   <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-8 shadow-2xl h-full flex flex-col justify-between">
                      <div>
                         <h3 className="text-xs font-black text-white uppercase tracking-widest mb-10 border-b border-white/10 pb-4 flex items-center gap-2">
                           <ShieldAlert className="w-4 h-4 text-amber-500" /> Decision Panel
                         </h3>
                         <p className="text-[10px] text-gray-500 leading-relaxed mb-8 italic font-bold">
                           "Your vote is blind. It will be aggregated once 7 signatures are anchored. Dissenting from the majority consensus triggers a bond slash."
                         </p>

                         <div className="space-y-4">
                            <button className="w-full py-4 border border-green-500/20 bg-green-500/5 text-green-500 font-black text-xs uppercase tracking-widest hover:bg-green-500 hover:text-black transition-all rounded-lg flex items-center justify-center gap-3">
                               <CheckCircle2 className="w-4 h-4" /> Uphold Task
                            </button>
                            <button className="w-full py-4 border border-red-500/20 bg-red-500/5 text-red-500 font-black text-xs uppercase tracking-widest hover:bg-red-500 hover:text-white transition-all rounded-lg flex items-center justify-center gap-3">
                               <XCircle className="w-4 h-4" /> Slash Bond
                            </button>
                         </div>
                      </div>

                      <div className="pt-8 space-y-3">
                         <button className="w-full py-3 bg-white/5 border border-white/10 text-gray-500 font-black text-[10px] uppercase tracking-widest hover:text-white transition-all rounded flex items-center justify-center gap-2">
                            <Layers className="w-3 h-3" /> Request Deep Dive
                         </button>
                         <p className="text-[8px] text-gray-700 text-center uppercase tracking-widest font-black">
                           *Signature will be bound to TPM_AK_X29
                         </p>
                      </div>
                   </div>
                </div>
             </div>
          </div>
        )}

      </main>

      {/* Industrial Footer Status Bar */}
      <footer className="fixed bottom-0 w-full bg-[#0a0a0a] border-t border-white/5 p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity z-50 px-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className={`w-1.5 h-1.5 rounded-full animate-pulse ${timeLeft < 3600 ? 'bg-red-500' : 'bg-indigo-500'}`} />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Juror Console Active</span>
            </div>
            <div className="h-4 w-px bg-white/10 hidden md:block" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter hidden md:block">"Integrity is the bedrock of the High Court."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] SESSION: {caseData.id}</span>
            <span>[*] HSM_STATUS: LOCKED</span>
            <span>[*] VERSION: v3.5.5</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scan {
          0% { transform: translateY(-120px); }
          50% { transform: translateY(120px); }
          100% { transform: translateY(-120px); }
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
