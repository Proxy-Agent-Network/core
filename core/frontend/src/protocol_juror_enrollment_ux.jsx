import React, { useState, useEffect } from 'react';
import { 
  Gavel, 
  ShieldCheck, 
  Fingerprint, 
  Cpu, 
  RefreshCw, 
  Lock, 
  ChevronRight, 
  ArrowRight, 
  CheckCircle2, 
  Zap, 
  Info, 
  AlertTriangle, 
  Binary, 
  Database, 
  Coins, 
  Target,
  Scale,
  XCircle,
  Activity,
  Award,
  Box,
  Shield,
  Terminal
} from 'lucide-react';

/**
 * PROXY PROTOCOL - JUROR ENROLLMENT UI (v1.0)
 * "The Draft Ceremony: Joining the High Court."
 * ----------------------------------------------------
 */

const App = () => {
  const [step, setStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  // Mock Node Standing
  const [node] = useState({
    id: "NODE_ELITE_X29",
    rep: 982,
    bond: 2000000,
    tier: "SUPER-ELITE"
  });

  const isEligible = node.rep >= 951 && node.bond >= 2000000;

  const nextStep = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setStep(prev => prev + 1);
    }, 1500);
  };

  const handleTpmBinding = () => {
    setIsProcessing(true);
    // Simulate TPM 2.0 Key Generation & Blinded ID broadcast
    setTimeout(() => {
      setIsProcessing(false);
      setIsSuccess(true);
      setStep(4);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-amber-500/30">
      
      {/* Background matrix pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-2xl w-full relative z-10">
        
        {/* Progress Stepper */}
        <div className="flex justify-between mb-12 px-10 relative">
           <div className="absolute top-1/2 left-0 w-full h-px bg-white/5 -z-10" />
           {[1, 2, 3, 4].map((s) => (
             <div key={s} className={`w-10 h-10 rounded-full flex items-center justify-center border-2 text-xs font-black transition-all duration-500 ${
               step >= s ? 'bg-amber-500 border-amber-400 text-black shadow-[0_0_20px_rgba(245,158,11,0.5)]' : 'bg-black border-white/10 text-gray-700'
             }`}>
               0{s}
             </div>
           ))}
        </div>

        <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
          
          {/* Header */}
          <div className="p-8 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
             <div className="flex items-center gap-4">
                <div className="p-3 bg-amber-500/10 rounded-xl border border-amber-500/20">
                   <Gavel className="w-6 h-6 text-amber-500" />
                </div>
                <div>
                   <h1 className="text-xl font-black text-white uppercase tracking-tighter leading-none">Draft Ceremony</h1>
                   <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-1">Appellate Court Onboarding</p>
                </div>
             </div>
             <div className="text-right">
                <span className="text-[9px] text-gray-700 uppercase font-black block">Status</span>
                <span className="text-xs font-black text-amber-500 uppercase tracking-widest animate-pulse">
                   {step === 4 ? 'Enrolled' : 'Awaiting Input'}
                </span>
             </div>
          </div>

          <div className="p-10 min-h-[450px] flex flex-col justify-between">
            
            {/* STEP 1: ELIGIBILITY AUDIT */}
            {step === 1 && (
              <div className="space-y-10 animate-in fade-in duration-500">
                <div className="text-center">
                   <div className="p-4 bg-white/5 border border-white/10 rounded-full inline-block mb-4">
                      <Target className="w-12 h-12 text-gray-500" />
                   </div>
                   <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-4">Verify Qualifications</h2>
                   <p className="text-xs text-gray-500 leading-relaxed max-sm mx-auto italic">
                      "Entry into the High Court is restricted to nodes that maintain structural stability and significant economic commitment."
                   </p>
                </div>

                <div className="grid grid-cols-2 gap-6">
                   <div className={`p-6 rounded-xl border transition-all ${node.rep >= 951 ? 'bg-green-500/5 border-green-500/20' : 'bg-red-500/5 border-red-500/20'}`}>
                      <div className="flex justify-between items-center mb-4">
                         <span className="text-[9px] font-black uppercase text-gray-500 tracking-widest">Reputation</span>
                         {node.rep >= 951 ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <XCircle className="w-4 h-4 text-red-500" />}
                      </div>
                      <span className="text-2xl font-black text-white">{node.rep}</span>
                      <span className="text-[9px] text-gray-600 font-bold block mt-1 uppercase">Threshold: 951+</span>
                   </div>
                   <div className={`p-6 rounded-xl border transition-all ${node.bond >= 2000000 ? 'bg-green-500/5 border-green-500/20' : 'bg-red-500/5 border-red-500/20'}`}>
                      <div className="flex justify-between items-center mb-4">
                         <span className="text-[9px] font-black uppercase text-gray-500 tracking-widest">Locked Bond</span>
                         {node.bond >= 2000000 ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <XCircle className="w-4 h-4 text-red-500" />}
                      </div>
                      <span className="text-2xl font-black text-white">2.0M</span>
                      <span className="text-[9px] text-gray-600 font-bold block mt-1 uppercase">SATS Required</span>
                   </div>
                </div>

                <button 
                  onClick={nextStep}
                  disabled={!isEligible}
                  className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-amber-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-xl disabled:opacity-20"
                >
                  Proceed to Drafting <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* STEP 2: BOND COMMITMENT */}
            {step === 2 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                 <div className="p-8 border border-amber-500/20 bg-amber-500/5 rounded-2xl flex items-center gap-8 shadow-inner">
                    <div className="p-5 bg-amber-500/10 border border-amber-500/20 rounded-2xl">
                       <Coins className="w-12 h-12 text-amber-500 animate-pulse" />
                    </div>
                    <div>
                       <h3 className="text-xl font-black text-white uppercase tracking-tighter mb-2">Legal Commitment</h3>
                       <p className="text-xs text-gray-500 leading-relaxed max-w-sm italic">
                         "As a High Court Juror, you commit your 2,000,000 Satoshi bond as collateral against bad-faith voting. Dissenting against the Schelling Point triggers a 30% slash."
                       </p>
                    </div>
                 </div>

                 <div className="bg-black/40 border border-white/5 rounded-xl p-6">
                    <div className="flex justify-between items-center mb-6 border-b border-white/5 pb-4">
                       <span className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Protocol Rules</span>
                       <span className="text-[9px] text-amber-500 font-bold">Rule 8.4 Enforced</span>
                    </div>
                    <ul className="space-y-4">
                       <li className="flex items-center gap-4 text-[10px] text-gray-400 font-bold uppercase tracking-tight">
                          <CheckCircle2 className="w-4 h-4 text-green-500" /> Instant slash on quorum drift
                       </li>
                       <li className="flex items-center gap-4 text-[10px] text-gray-400 font-bold uppercase tracking-tight">
                          <CheckCircle2 className="w-4 h-4 text-green-500" /> Mandatory 4h response window
                       </li>
                       <li className="flex items-center gap-4 text-[10px] text-gray-400 font-bold uppercase tracking-tight">
                          <CheckCircle2 className="w-4 h-4 text-green-500" /> Yield: 5% pro-rata share of fees
                       </li>
                    </ul>
                 </div>

                 <button 
                  onClick={nextStep}
                  className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-amber-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-xl"
                >
                  Accept Terms & Sign <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* STEP 3: TPM BINDING */}
            {step === 3 && (
              <div className="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
                 <div className="text-center">
                    <div className="w-20 h-20 bg-indigo-500/10 border border-indigo-500/20 rounded-full flex items-center justify-center mx-auto mb-6 relative">
                       <Cpu className={`w-10 h-10 text-indigo-500 ${isProcessing ? 'animate-pulse' : ''}`} />
                       {isProcessing && <div className="absolute inset-0 bg-indigo-500/20 rounded-full animate-ping" />}
                    </div>
                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-2">Blinded Identity Binding</h2>
                    <p className="text-xs text-gray-500">Generating hardware-bound anonymous juror handle...</p>
                 </div>

                 <div className="bg-[#050505] border border-white/5 rounded-xl p-6 h-40 flex flex-col font-mono text-[10px]">
                    <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
                       <span className="text-gray-700 font-black uppercase tracking-widest flex items-center gap-2"><Terminal className="w-3 h-3" /> System_Daemon_Log</span>
                       <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                    </div>
                    <div className="space-y-2 text-gray-500 overflow-y-auto flex-1 scrollbar-hide">
                       <p>[*] INVOKING TPM2_CREATEPRIMARY...</p>
                       <p>[*] HASHING HARDWARE_ID WITH BLINDING_SECRET...</p>
                       {isProcessing && <p className="text-indigo-400 font-bold">[*] BROADCASTING JWS_MANIFEST TO GOVERNANCE_API...</p>}
                       {isProcessing && <p className="text-indigo-400 font-bold">[*] AWAITING ORACLE_BINDING_TOKEN...</p>}
                       <p className="animate-pulse">[*] WAITING_ATTESTATION...</p>
                    </div>
                 </div>

                 <button 
                  onClick={handleTpmBinding}
                  disabled={isProcessing}
                  className="w-full py-5 bg-indigo-500 text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-400 transition-all flex items-center justify-center gap-3 shadow-[0_0_40px_rgba(99,102,241,0.2)]"
                >
                  {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Fingerprint className="w-5 h-5" />}
                  {isProcessing ? 'Binding Silicon Identity...' : 'Initiate Hardware Binding'}
                </button>
              </div>
            )}

            {/* STEP 4: SUCCESS */}
            {step === 4 && (
              <div className="text-center py-10 animate-in zoom-in-95 duration-700 space-y-10">
                <div className="relative inline-block">
                   <ShieldCheck className="w-24 h-24 text-green-500 drop-shadow-[0_0_30px_rgba(34,197,94,0.4)] animate-bounce" />
                </div>
                <div>
                   <h2 className="text-4xl font-black text-white uppercase tracking-tighter mb-4">Juror Activated</h2>
                   <p className="text-sm text-gray-500 uppercase tracking-[0.2em] font-bold">Protocol v3.5.2 // Draft Epoch: 88294</p>
                </div>

                <div className="bg-black/60 border border-white/5 rounded-2xl p-8 text-left space-y-6">
                   <div className="flex justify-between items-center">
                      <span className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Anonymous Handle</span>
                      <span className="text-sm font-black text-amber-500 tracking-tighter">J-88293X-ELITE</span>
                   </div>
                   <div className="flex justify-between items-center border-t border-white/5 pt-6">
                      <span className="text-[10px] text-gray-600 font-black uppercase tracking-widest">VRF Candidate Pool</span>
                      <span className="text-sm font-black text-green-500 uppercase">ENROLLED</span>
                   </div>
                </div>

                <button 
                  onClick={() => window.location.reload()}
                  className="px-12 py-4 bg-white/5 border border-white/10 rounded-lg text-xs font-black uppercase tracking-widest hover:text-white hover:border-white transition-all"
                >
                  Return to Command Center
                </button>
              </div>
            )}

          </div>

          {/* Forensic Status Footer */}
          <div className="p-4 bg-black border-t border-white/5 flex items-center justify-between px-10 text-[9px] font-black text-gray-700 uppercase tracking-widest">
             <div className="flex items-center gap-3">
                <Box className="w-3.5 h-3.5" />
                <span>Protocol: High Court v3</span>
             </div>
             <div className="flex gap-6">
                <span>TPM_QUORUM: OK</span>
                <span>HW_ID: 0x8A2E...F91C</span>
             </div>
          </div>
        </div>

        {/* Global Help Disclaimer */}
        <div className="mt-8 flex justify-between items-center px-4 opacity-50 hover:opacity-100 transition-opacity">
           <div className="flex items-center gap-2 text-gray-600">
              <Shield className="w-4 h-4" />
              <span className="text-[10px] font-black uppercase tracking-widest leading-none">Draft Window Ends: 14h 22m</span>
           </div>
           <button className="text-[9px] font-black text-gray-600 hover:text-white uppercase tracking-tighter flex items-center gap-1.5 transition-all">
             View High Court Charter <ChevronRight className="w-3 h-3" />
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
