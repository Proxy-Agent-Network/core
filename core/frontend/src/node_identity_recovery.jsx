import React, { useState } from 'react';
import { 
  RotateCcw, 
  Fingerprint, 
  Cpu, 
  ShieldCheck, 
  ArrowRight, 
  AlertTriangle, 
  CheckCircle2, 
  FileWarning, 
  RefreshCw, 
  Info, 
  Lock,
  ChevronRight,
  UserCheck,
  Binary,
  Activity
} from 'lucide-react';

/**
 * PROXY PROTOCOL - NODE IDENTITY RECOVERY (v1.0)
 * "Identity is persistent; hardware is transient."
 * ----------------------------------------------------
 */

const App = () => {
  const [step, setStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recoveryData] = useState({
    old_id: "NODE_ELITE_X29",
    old_rep: 982,
    old_bond: 2000000
  });

  const [newId] = useState("NODE_NEW_88293_PX");
  
  const penalty = Math.floor(recoveryData.old_rep * 0.10);
  const finalRep = recoveryData.old_rep - penalty;

  const nextStep = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setStep(prev => prev + 1);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-indigo-500/30">
      
      {/* Background Decorative Grid */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-2xl w-full relative z-10">
        
        {/* Progress Stepper */}
        <div className="flex justify-between mb-12 px-4 relative">
           <div className="absolute top-1/2 left-0 w-full h-px bg-white/5 -z-10" />
           {[1, 2, 3].map((s) => (
             <div key={s} className={`w-8 h-8 rounded-full flex items-center justify-center border text-[10px] font-black transition-all ${
               step >= s ? 'bg-indigo-500 border-indigo-400 text-black shadow-[0_0_15px_rgba(99,102,241,0.4)]' : 'bg-black border-white/10 text-gray-700'
             }`}>
               0{s}
             </div>
           ))}
        </div>

        <div className="bg-[#0a0a0a] border border-white/10 rounded-xl overflow-hidden shadow-2xl">
          
          {/* Header */}
          <div className="p-8 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
             <div>
                <h1 className="text-xl font-black text-white uppercase tracking-tight">Identity Recovery</h1>
                <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold">Protocol v2.6.7 // LOST_NODE_RECOVERY</p>
             </div>
             <RotateCcw className={`w-6 h-6 text-indigo-500 ${isProcessing ? 'animate-spin' : ''}`} />
          </div>

          <div className="p-8">
            
            {/* STEP 1: Diagnostic */}
            {step === 1 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                <div className="flex items-center gap-6 p-6 bg-red-500/5 border border-red-500/20 rounded-xl">
                   <div className="p-3 bg-red-500/10 rounded-lg"><FileWarning className="w-8 h-8 text-red-500" /></div>
                   <div>
                      <h3 className="text-white font-black text-xs uppercase mb-1">Decommissioned Hardware Detected</h3>
                      <p className="text-[11px] text-gray-500 leading-relaxed">Identity {recoveryData.old_id} has been marked as OFFLINE due to a TPM tamper event. No private keys can be recovered.</p>
                   </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                   <div className="p-5 bg-white/5 border border-white/5 rounded-lg">
                      <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Legacy Rep</span>
                      <span className="text-xl font-black text-white">{recoveryData.old_rep}</span>
                   </div>
                   <div className="p-5 bg-white/5 border border-white/5 rounded-lg">
                      <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Legacy Bond</span>
                      <span className="text-xl font-black text-white">2.0M <span className="text-xs opacity-40">SATS</span></span>
                   </div>
                </div>

                <div className="pt-4">
                  <button 
                    onClick={nextStep}
                    className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-500 hover:text-white transition-all flex items-center justify-center gap-3"
                  >
                    Initiate Recovery Ceremony <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            {/* STEP 2: Binding & Penalty */}
            {step === 2 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                <div>
                   <h3 className="text-xs font-black text-gray-500 uppercase tracking-widest mb-6">Linking New Hardware</h3>
                   <div className="p-6 bg-black border border-indigo-500/20 rounded-xl flex items-center gap-6">
                      <div className="p-3 bg-indigo-500/10 rounded-lg"><Cpu className="w-8 h-8 text-indigo-500 animate-pulse" /></div>
                      <div>
                         <span className="text-[9px] text-indigo-400 font-black uppercase">Replacement Unit ID</span>
                         <code className="text-sm font-bold text-white block truncate">{newId}</code>
                      </div>
                   </div>
                </div>

                <div className="p-6 border border-amber-500/20 bg-amber-500/5 rounded-xl">
                   <div className="flex items-center justify-between mb-4">
                      <h4 className="text-[10px] font-black text-amber-500 uppercase tracking-widest">Protocol Penalty Disclosure</h4>
                      <AlertTriangle className="w-4 h-4 text-amber-500" />
                   </div>
                   <p className="text-[11px] text-gray-400 leading-relaxed mb-6 italic">
                     "As per node_recovery.md Rule 3, recertified nodes receive a 10% Reputation reduction to reflect the risk of operational instability."
                   </p>
                   <div className="flex justify-between items-center py-3 border-t border-white/5">
                      <span className="text-[10px] text-gray-500 font-bold uppercase">Penalty applied</span>
                      <span className="text-red-400 font-black">-{penalty} REP</span>
                   </div>
                   <div className="flex justify-between items-center py-3 border-t border-white/5">
                      <span className="text-[10px] text-white font-bold uppercase">Migrated Score</span>
                      <span className="text-green-500 font-black">{finalRep} REP</span>
                   </div>
                </div>

                <button 
                  onClick={nextStep}
                  disabled={isProcessing}
                  className="w-full py-4 bg-indigo-500 text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-400 transition-all flex items-center justify-center gap-3 shadow-[0_0_30px_rgba(99,102,241,0.2)]"
                >
                  {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <UserCheck className="w-4 h-4" />}
                  Sign & Accept Recertification
                </button>
              </div>
            )}

            {/* STEP 3: Finality */}
            {step === 3 && (
              <div className="text-center py-8 animate-in zoom-in-95 duration-500">
                <div className="w-20 h-20 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_50px_rgba(34,197,94,0.1)]">
                   <CheckCircle2 className="w-10 h-10 text-green-500" />
                </div>
                <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-2">Recovery Complete</h2>
                <p className="text-xs text-gray-500 mb-8 max-w-xs mx-auto leading-relaxed uppercase tracking-widest">
                   Standing migrated to <span className="text-white font-bold">{newId}</span>
                </p>
                
                <div className="bg-black/60 border border-white/5 p-6 rounded-xl text-left space-y-4 mb-8">
                   <div className="flex justify-between items-center text-[10px]">
                      <span className="text-gray-600 font-black uppercase tracking-widest">Probation Window</span>
                      <span className="text-amber-500 font-bold">7 DAYS REMAINING</span>
                   </div>
                   <div className="flex gap-1 h-1.5">
                      <div className="flex-1 bg-amber-500/40 rounded-full" />
                      {[...Array(6)].map((_, i) => (
                        <div key={i} className="flex-1 bg-white/5 rounded-full" />
                      ))}
                   </div>
                   <p className="text-[9px] text-gray-700 italic">
                     *Recertified nodes are capped at 10% volume and subject to silent Double-Verification during probation.
                   </p>
                </div>

                <button 
                  onClick={() => window.location.reload()}
                  className="px-8 py-3 border border-white/10 text-gray-500 font-black text-[10px] uppercase tracking-widest hover:text-white transition-all rounded-lg"
                >
                  Return to Dashboard
                </button>
              </div>
            )}

          </div>

          {/* Forensic Status Footer */}
          <div className="p-4 bg-black border-t border-white/5 flex items-center justify-between text-[9px] text-gray-600 font-bold uppercase px-8">
             <div className="flex items-center gap-3">
                <ShieldCheck className="w-3.5 h-3.5" /> 
                <span>Hardware Link Verified</span>
             </div>
             <div className="flex gap-4">
                <span>TPM_QUORUM: OK</span>
                <span>SIGNATURE: RSA-PSS</span>
             </div>
          </div>
        </div>

        {/* Security Disclosure */}
        <div className="mt-8 p-6 bg-indigo-500/5 border border-indigo-500/10 rounded-lg flex items-start gap-4 opacity-60 hover:opacity-100 transition-opacity">
           <Info className="w-5 h-5 text-indigo-500 shrink-0" />
           <p className="text-[10px] text-gray-500 leading-relaxed italic">
             "Identity recovery binds your biological identity (from the mobile app) to a new hardware root of trust. This ceremony is logged permanently in the Reputation Oracle to prevent score-farming."
           </p>
        </div>

      </main>

    </div>
  );
};

export default App;
