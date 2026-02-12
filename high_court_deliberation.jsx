import React, { useState, useEffect } from 'react';
import { 
  Gavel, 
  ShieldCheck, 
  EyeOff, 
  Lock, 
  Fingerprint, 
  Users, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  RefreshCw, 
  AlertTriangle, 
  Info,
  ChevronRight,
  Database,
  Binary,
  ShieldAlert,
  Send
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HIGH COURT DELIBERATION (v1.0)
 * "Double-blind adjudication for protocol finality."
 * ----------------------------------------------------
 */

const App = () => {
  const [isDecrypting, setIsDecrypting] = useState(false);
  const [isEvidenceUnlocked, setIsEvidenceUnlocked] = useState(false);
  const [vote, setVote] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasVoted, setHasVoted] = useState(false);

  // Mock Case Data
  const [caseData] = useState({
    id: "CASE-8829-APP",
    type: "PROTOCOL_BREACH",
    severity: "CRITICAL",
    dispute_value: "2,500,000 SATS",
    opened_at: "2026-02-11T19:30:00Z",
    evidence: {
      instruction: "Sign Delaware Incorporation Document for Genesis AI LLC.",
      proof_summary: "Human Node submitted a photograph of a blank sheet instead of the signed deed.",
      telemetry_hash: "e3b0c442...98fc",
      tpm_status: "VALID_HARDWARE"
    }
  });

  // Mock Quorum Status
  const [quorum] = useState({
    total: 7,
    signed: 4,
    required: 5
  });

  const handleDecrypt = () => {
    setIsDecrypting(true);
    // Simulate TPM 2.0 Unseal Handshake
    setTimeout(() => {
      setIsDecrypting(false);
      setIsEvidenceUnlocked(true);
    }, 2000);
  };

  const handleSubmitVote = () => {
    setIsSubmitting(true);
    // Simulate Hardware Signature (RSA-PSS)
    setTimeout(() => {
      setIsSubmitting(false);
      setHasVoted(true);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-indigo-500/30">
      
      {/* Background Decorative Element */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-5xl w-full relative z-10 space-y-8">
        
        {/* Header: High Court Identity */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl shadow-[0_0_20px_rgba(245,158,11,0.1)]">
              <Gavel className="w-8 h-8 text-amber-500" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase">High Court Chamber</h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Epoch 88294 // Juror <span className="text-amber-500">NODE_ELITE_X29</span></p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-2xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Quorum Progress</span>
                   <span className="text-xl font-black text-white tracking-tighter">
                     {quorum.signed}<span className="text-gray-600">/{quorum.total}</span>
                   </span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Status</span>
                   <span className="text-xs font-black text-amber-500 uppercase tracking-widest animate-pulse">Awaiting Decision</span>
                </div>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Left Column: Blind Evidence Locker */}
          <div className="col-span-12 lg:col-span-8 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/10 rounded-xl overflow-hidden shadow-2xl min-h-[500px] flex flex-col">
                <div className="p-4 border-b border-white/5 bg-white/[0.02] flex justify-between items-center px-8">
                   <h3 className="text-[10px] uppercase font-black text-gray-400 tracking-widest flex items-center gap-2">
                      <Lock className="w-3.5 h-3.5" /> Hardware-Encrypted Shard
                   </h3>
                   <div className="flex items-center gap-2 text-[9px] text-indigo-400 font-bold uppercase">
                      <ShieldCheck className="w-3 h-3" /> RSA-OAEP Active
                   </div>
                </div>

                <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
                   {!isEvidenceUnlocked ? (
                     <div className="max-w-md animate-in fade-in duration-700">
                        <div className="w-20 h-20 bg-white/5 border border-white/10 rounded-full flex items-center justify-center mx-auto mb-8 shadow-inner group">
                           <EyeOff className={`w-8 h-8 ${isDecrypting ? 'text-amber-500 animate-pulse' : 'text-gray-700 group-hover:text-gray-500 transition-colors'}`} />
                        </div>
                        <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-4">Evidence Restricted</h2>
                        <p className="text-xs text-gray-500 mb-8 leading-relaxed">
                           The evidence for Case {caseData.id} is sealed within your node's private buffer. You must invoke your hardware TPM to finalize the blind deliberation.
                        </p>
                        <button 
                          onClick={handleDecrypt}
                          disabled={isDecrypting}
                          className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-amber-500 transition-all flex items-center justify-center gap-3 shadow-[0_0_30px_rgba(255,255,255,0.1)] disabled:opacity-50"
                        >
                          {isDecrypting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Fingerprint className="w-4 h-4" />}
                          {isDecrypting ? 'Initializing TPM...' : 'Sign to Decrypt'}
                        </button>
                     </div>
                   ) : (
                     <div className="w-full h-full text-left space-y-10 animate-in zoom-in-95 duration-500">
                        <div className="grid grid-cols-2 gap-8">
                           <div>
                              <h4 className="text-[10px] font-black text-gray-600 uppercase mb-3 tracking-widest">Incident Category</h4>
                              <p className="text-sm font-bold text-white uppercase">{caseData.type}</p>
                           </div>
                           <div className="text-right">
                              <h4 className="text-[10px] font-black text-gray-600 uppercase mb-3 tracking-widest">Escrow at Stake</h4>
                              <p className="text-sm font-bold text-red-500">{caseData.dispute_value}</p>
                           </div>
                        </div>

                        <div className="space-y-6">
                           <div>
                              <h4 className="text-[10px] font-black text-amber-500 uppercase mb-3 flex items-center gap-2">
                                <Info className="w-3.5 h-3.5" /> Agent Intent
                              </h4>
                              <div className="bg-black border border-white/5 p-5 rounded-lg text-sm text-gray-400 italic">
                                 "{caseData.evidence.instruction}"
                              </div>
                           </div>

                           <div>
                              <h4 className="text-[10px] font-black text-green-500 uppercase mb-3 flex items-center gap-2">
                                <Database className="w-3.5 h-3.5" /> Proof Forensic Summary
                              </h4>
                              <div className="bg-black border border-white/5 p-5 rounded-lg text-sm text-gray-400">
                                 {caseData.evidence.proof_summary}
                              </div>
                           </div>
                        </div>

                        <div className="p-4 bg-indigo-500/5 border border-indigo-500/20 rounded-lg flex items-center justify-between">
                           <div className="flex items-center gap-4">
                              <Binary className="w-6 h-6 text-indigo-400" />
                              <div>
                                 <p className="text-[10px] text-white font-black uppercase">Hardware Root of Trust</p>
                                 <code className="text-[9px] text-gray-500 font-mono">NODE_SIG: {caseData.evidence.telemetry_hash.substring(0, 24)}...</code>
                              </div>
                           </div>
                           <span className="text-[9px] font-black text-indigo-400 bg-indigo-500/10 px-2 py-1 rounded">VERIFIED</span>
                        </div>
                     </div>
                   )}
                </div>
             </div>
          </div>

          {/* Right Column: Voting Console & Quorum */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             
             {/* Voting Block */}
             <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-8 shadow-2xl flex flex-col justify-between h-full">
                {!hasVoted ? (
                  <>
                    <div>
                       <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 border-b border-white/5 pb-4">
                          Secure Verdict
                       </h3>
                       <p className="text-[10px] text-gray-500 leading-relaxed mb-8 italic font-bold">
                          "You are voting as a Super-Elite node. Your decision will be aggregated after 7 signatures are collected."
                       </p>

                       <div className="space-y-4">
                          <button 
                            onClick={() => setVote('APPROVE')}
                            disabled={!isEvidenceUnlocked || isSubmitting}
                            className={`w-full py-4 border rounded-lg flex items-center justify-center gap-3 transition-all ${
                              vote === 'APPROVE' 
                                ? 'bg-green-500 border-green-400 text-black font-black' 
                                : 'bg-white/5 border-white/10 text-gray-600 hover:border-green-500/30 hover:text-green-500'
                            } disabled:opacity-20`}
                          >
                            <CheckCircle2 className="w-4 h-4" /> 
                            <span className="text-xs uppercase tracking-widest font-black">Uphold Task</span>
                          </button>

                          <button 
                            onClick={() => setVote('REJECT')}
                            disabled={!isEvidenceUnlocked || isSubmitting}
                            className={`w-full py-4 border rounded-lg flex items-center justify-center gap-3 transition-all ${
                              vote === 'REJECT' 
                                ? 'bg-red-500 border-red-400 text-black font-black' 
                                : 'bg-white/5 border-white/10 text-gray-600 hover:border-red-500/30 hover:text-red-500'
                            } disabled:opacity-20`}
                          >
                            <XCircle className="w-4 h-4" /> 
                            <span className="text-xs uppercase tracking-widest font-black">Slash Bond</span>
                          </button>
                       </div>
                    </div>

                    <div className="pt-10">
                       <button 
                         onClick={handleSubmitVote}
                         disabled={!vote || isSubmitting}
                         className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-amber-500 transition-all flex items-center justify-center gap-3 shadow-xl disabled:bg-gray-800 disabled:text-gray-600"
                       >
                         {isSubmitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                         {isSubmitting ? 'Signing Payload...' : 'Broadcast Verdict'}
                       </button>
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center text-center animate-in zoom-in-95 duration-500">
                     <div className="w-16 h-16 bg-indigo-500/10 border border-indigo-500/20 rounded-full flex items-center justify-center mb-6">
                        <ShieldCheck className="w-8 h-8 text-indigo-500 animate-pulse" />
                     </div>
                     <h3 className="text-xl font-black text-white uppercase tracking-tighter mb-2">Vote Recorded</h3>
                     <p className="text-xs text-gray-500 mb-8 max-w-[200px]">
                        Your hardware signature has been submitted. Case remains BLIND until {quorum.total} signatures are finalized.
                     </p>
                     <div className="p-3 bg-black border border-white/5 rounded mono text-[9px] text-gray-600">
                        RECEIPT: 0x8a2e...{Math.random().toString(16).slice(2, 8)}
                     </div>
                  </div>
                )}
             </div>

             {/* Quorum Progress Sidebar */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
                <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                   <Users className="w-4 h-4 text-indigo-500" /> Quorum Tracker
                </h3>
                <div className="space-y-4">
                   <div className="flex justify-between items-end mb-2">
                      <span className="text-[9px] text-gray-500 uppercase font-black">Consensus Threshold</span>
                      <span className="text-xs font-black text-white">{quorum.signed} / {quorum.total} SIGNED</span>
                   </div>
                   <div className="flex gap-1.5 h-2">
                      {[...Array(quorum.total)].map((_, i) => (
                        <div 
                          key={i} 
                          className={`flex-1 rounded-full transition-all duration-1000 ${
                            i < quorum.signed ? 'bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.4)]' : 'bg-white/5'
                          } ${i === quorum.signed && !hasVoted ? 'animate-pulse bg-indigo-500/30' : ''}`} 
                        />
                      ))}
                   </div>
                   <div className="flex justify-between text-[8px] font-bold text-gray-700 uppercase tracking-widest pt-2">
                      <span>Awaiting 3 Jurors</span>
                      <span className="text-indigo-400">Target: 5/7 Majority</span>
                   </div>
                </div>
             </div>
          </div>

        </div>

        {/* Security Warning Footer */}
        <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-6 flex items-start gap-4">
           <ShieldAlert className="w-6 h-6 text-red-500 shrink-0" />
           <p className="text-[10px] text-gray-500 leading-relaxed font-medium italic">
             "LEGAL NOTICE: High Court deliberations are recorded on the permanent hardware ledger. Any attempt to communicate with fellow jurors regarding Case {caseData.id} results in immediate revocation of Super-Elite status and bond liquidation."
           </p>
        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-5xl w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Protocol v2.7.1 Secure</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Case Lock: 0xDEADBEEF...</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] SCHELLING_CONVERGENCE: 94.2%</span>
            <span>[*] APPELLATE_VRF: READY</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
