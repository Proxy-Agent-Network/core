import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  RotateCcw, 
  Cpu, 
  Lock, 
  Fingerprint, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  ShieldCheck, 
  Terminal, 
  Binary, 
  Activity, 
  History, 
  ChevronRight, 
  ArrowRight, 
  Info, 
  AlertTriangle,
  Layers,
  FileText,
  Unplug,
  Box,
  Smartphone
} from 'lucide-react';

/**
 * PROXY PROTOCOL - QUARANTINE RECOVERY CEREMONY (v1.0)
 * "The path to due process: Hardware-attested appeals for biological nodes."
 * -----------------------------------------------------------------------
 */

const App = () => {
  const [step, setStep] = useState(1); // 1: NOTIFICATION, 2: APPEAL, 3: ATTESTATION, 4: PENDING
  const [isProcessing, setIsProcessing] = useState(false);
  const [appealText, setAppealText] = useState('');

  // Mock Identity & Ban Data
  const [banData] = useState({
    did: "did:proxy:8A2E1C",
    node_id: "SENTRY-JP-001",
    reason: "ITERATIVE_PROBING_DETECTED",
    probing_probability: 0.94,
    forensic_distance: 0.12,
    timestamp: "2026-02-12T14:22:05Z",
    reputation_impact: -50
  });

  const nextStep = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setStep(prev => prev + 1);
    }, 1500);
  };

  const handleAttestation = () => {
    setIsProcessing(true);
    // Simulate TPM 2.0 Quote generation
    // Proves the hardware chip is still physically present and the firmware hasn't drifted
    setTimeout(() => {
      setIsProcessing(false);
      setStep(4);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-red-500/30 overflow-x-hidden">
      
      {/* Background Warning Mesh */}
      <div className={`fixed inset-0 pointer-events-none transition-opacity duration-1000 ${step === 1 ? 'opacity-10' : 'opacity-[0.02]'} z-0`} 
           style={{ backgroundImage: 'radial-gradient(#ff3333 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-2xl w-full relative z-10">
        
        {/* Progress Stepper */}
        <div className="flex justify-between mb-12 px-10 relative">
           <div className="absolute top-1/2 left-0 w-full h-px bg-white/5 -z-10" />
           {[1, 2, 3, 4].map((s) => (
             <div key={s} className={`w-8 h-8 rounded-full flex items-center justify-center border-2 text-[10px] font-black transition-all duration-500 ${
               step >= s ? 'bg-red-600 border-red-500 text-white shadow-[0_0_15px_rgba(239,68,68,0.4)]' : 'bg-black border-white/10 text-gray-700'
             }`}>
               0{s}
             </div>
           ))}
        </div>

        <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
          
          {/* Header Bar */}
          <div className="p-8 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
             <div className="flex items-center gap-4">
                <div className="p-2 bg-red-500/10 rounded border border-red-500/20">
                   <ShieldAlert className={`w-5 h-5 text-red-500 ${step === 1 ? 'animate-pulse' : ''}`} />
                </div>
                <div>
                   <h1 className="text-lg font-black text-white uppercase tracking-tight leading-none">Recovery Ceremony</h1>
                   <p className="text-[9px] text-gray-600 uppercase tracking-widest font-bold mt-1">Status: {step === 4 ? 'Awaiting Court' : 'Quarantined'}</p>
                </div>
             </div>
             <div className="text-right">
                <span className="text-[9px] text-gray-700 uppercase font-black block">Incident Ref</span>
                <span className="text-xs text-gray-400 font-bold tracking-tighter">PX-QRN-8829</span>
             </div>
          </div>

          <div className="p-10 min-h-[450px] flex flex-col justify-between">
            
            {/* STEP 1: NOTIFICATION (The Ban) */}
            {step === 1 && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="text-center space-y-4">
                   <h2 className="text-2xl font-black text-white uppercase tracking-tighter">Identity Quarantined</h2>
                   <p className="text-xs text-gray-500 leading-relaxed max-w-sm mx-auto italic">
                     "The Differential Forensic Engine has detected an iterative probing pattern linked to your DID. All network routing has been suspended."
                   </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                   <div className="p-5 bg-black border border-white/5 rounded-xl">
                      <span className="text-[9px] text-gray-600 uppercase font-black block mb-2">Probe Probability</span>
                      <span className="text-xl font-black text-red-500 tracking-tighter">{(banData.probing_probability * 100).toFixed(0)}%</span>
                   </div>
                   <div className="p-5 bg-black border border-white/5 rounded-xl">
                      <span className="text-[9px] text-gray-600 uppercase font-black block mb-2">Forensic Distance</span>
                      <span className="text-xl font-black text-white tracking-tighter">{banData.forensic_distance}</span>
                   </div>
                </div>

                <div className="p-6 bg-red-500/5 border border-red-500/10 rounded-xl space-y-3">
                   <div className="flex items-center gap-3 text-red-500">
                      <AlertTriangle className="w-4 h-4" />
                      <span className="text-[10px] font-black uppercase tracking-widest">Enforcement Trigger</span>
                   </div>
                   <p className="text-[11px] text-gray-400 leading-relaxed">
                     Reason: {banData.reason.replace(/_/g, ' ')}. Mismatch between task T-9901 and T-9884 indicates manual telemetry manipulation.
                   </p>
                </div>

                <button 
                  onClick={nextStep}
                  className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-red-500 hover:text-white transition-all rounded-lg flex items-center justify-center gap-3 shadow-xl"
                >
                  Initiate Formal Appeal <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* STEP 2: APPEAL DRAFT */}
            {step === 2 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                <div>
                   <h3 className="text-xs font-black text-white uppercase tracking-widest mb-4 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-indigo-500" /> Operator Statement
                   </h3>
                   <textarea 
                     value={appealText}
                     onChange={(e) => setAppealText(e.target.value)}
                     placeholder="Provide technical context for the detected drift (e.g., unexpected kernel update, network jitter)..."
                     className="w-full bg-black border border-white/10 rounded-xl p-6 text-sm text-white focus:outline-none focus:border-indigo-500 h-40 resize-none placeholder:text-gray-800 leading-relaxed"
                   />
                </div>

                <div className="p-4 bg-indigo-500/5 border border-indigo-500/10 rounded-xl flex items-start gap-4">
                   <Info className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
                   <p className="text-[10px] text-gray-500 leading-relaxed">
                     Appeals are reviewed by a 7-juror High Court quorum. Misleading statements in an appeal constitute a secondary protocol violation and will result in permanent reputation burning.
                   </p>
                </div>

                <button 
                  onClick={nextStep}
                  disabled={appealText.length < 20 || isProcessing}
                  className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-indigo-500 hover:text-white transition-all rounded-lg flex items-center justify-center gap-3 shadow-xl disabled:opacity-20"
                >
                  Confirm Statement <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* STEP 3: ATTESTATION CEREMONY */}
            {step === 3 && (
              <div className="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
                 <div className="text-center">
                    <div className="w-20 h-20 bg-indigo-500/10 border border-indigo-500/20 rounded-full flex items-center justify-center mx-auto mb-6 relative">
                       <Cpu className={`w-10 h-10 text-indigo-500 ${isProcessing ? 'animate-pulse' : ''}`} />
                       {isProcessing && <div className="absolute inset-0 bg-indigo-500/20 rounded-full animate-ping" />}
                    </div>
                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-2">Hardware Proof</h2>
                    <p className="text-xs text-gray-500">Generating fresh TPM 2.0 attestation quote...</p>
                 </div>

                 <div className="bg-[#050505] border border-white/5 rounded-xl p-6 h-40 flex flex-col font-mono text-[10px] shadow-inner">
                    <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
                       <span className="text-gray-700 font-black uppercase tracking-widest flex items-center gap-2"><Terminal className="w-3 h-3" /> Secure_Enclave</span>
                       <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                    </div>
                    <div className="space-y-2 text-gray-500 overflow-y-auto flex-1 scrollbar-hide">
                       <p>[*] LOADING AK_HANDLE: 0x81010002...</p>
                       <p>[*] REQUESTING PCR QUOTE [NONCE: PX_APPEAL_8829]...</p>
                       {isProcessing && <p className="text-indigo-400 font-bold">[*] SIGNING APPEAL_MANIFEST WITH SILICON IDENTITY...</p>}
                       {isProcessing && <p className="text-indigo-400 font-bold">[*] BINDING FRESH TELEMETRY SNAPSHOT...</p>}
                       <p className="animate-pulse">[*] WAITING_HSM_COMMITMENT...</p>
                    </div>
                 </div>

                 <button 
                  onClick={handleAttestation}
                  disabled={isProcessing}
                  className="w-full py-5 bg-indigo-500 text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-400 transition-all rounded-xl shadow-[0_0_40px_rgba(99,102,241,0.2)] flex items-center justify-center gap-3"
                >
                  {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Fingerprint className="w-5 h-5" />}
                  Finalize hardware sign-off
                </button>
              </div>
            )}

            {/* STEP 4: PENDING REVIEW */}
            {step === 4 && (
              <div className="text-center py-10 animate-in zoom-in-95 duration-700 space-y-10">
                <div className="relative inline-block">
                   <ShieldCheck className="w-24 h-24 text-green-500 drop-shadow-[0_0_30px_rgba(34,197,94,0.4)] animate-bounce" />
                </div>
                <div>
                   <h2 className="text-3xl font-black text-white uppercase tracking-tighter mb-3">Appeal Broadcast</h2>
                   <p className="text-xs text-gray-500 mb-10 max-w-sm mx-auto leading-relaxed uppercase tracking-widest font-bold">
                      Your forensic bundle has been submitted. Status: <span className="text-indigo-400">PENDING_HIGH_COURT</span>
                   </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                   <div className="p-4 bg-black border border-white/5 rounded-xl flex items-center gap-4">
                      <Clock className="w-5 h-5 text-indigo-500" />
                      <div className="text-left">
                         <span className="text-[9px] text-gray-600 uppercase font-black block">Resolution ETA</span>
                         <span className="text-xs font-bold text-white uppercase">48 HOURS</span>
                      </div>
                   </div>
                   <div className="p-4 bg-black border border-white/5 rounded-xl flex items-center gap-4">
                      <Layers className="w-5 h-5 text-green-500" />
                      <div className="text-left">
                         <span className="text-[9px] text-gray-600 uppercase font-black block">Court Queue</span>
                         <span className="text-xs font-bold text-white uppercase">#12 in DOCKET</span>
                      </div>
                   </div>
                </div>

                <button 
                  onClick={() => window.location.reload()}
                  className="px-12 py-4 bg-white/5 border border-white/10 rounded-lg text-xs font-black uppercase tracking-widest hover:text-white transition-all"
                >
                  Monitor Case Ledger
                </button>
              </div>
            )}

          </div>

          {/* Footer Metadata */}
          <div className="p-4 bg-black border-t border-white/5 flex items-center justify-between px-10 text-[9px] font-black text-gray-700 uppercase tracking-widest">
             <div className="flex items-center gap-3">
                <Smartphone className="w-3.5 h-3.5" />
                <span>SSI Protocol: did:proxy:v1</span>
             </div>
             <div className="flex gap-6">
                <span>TPM_AUTH: OK</span>
                <span>HW_ID: {banData.node_id}</span>
             </div>
          </div>
        </div>

        {/* Global Support Help */}
        <div className="mt-8 flex justify-between items-center px-4 opacity-50 hover:opacity-100 transition-opacity">
           <div className="flex items-center gap-2 text-gray-600">
              <Info className="w-4 h-4" />
              <span className="text-[10px] font-black uppercase tracking-widest leading-none mt-0.5">Need legal assistance?</span>
           </div>
           <button className="text-[10px] font-black text-gray-600 hover:text-white uppercase tracking-tighter flex items-center gap-1.5 transition-all">
             View Bill of Rights <ChevronRight className="w-3 h-3" />
           </button>
        </div>

      </main>

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
