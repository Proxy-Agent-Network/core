import React, { useState, useEffect } from 'react';
import { 
  RotateCcw, 
  Fingerprint, 
  Cpu, 
  ShieldCheck, 
  ArrowRight, 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw, 
  Lock, 
  ChevronRight, 
  UserCheck, 
  Binary, 
  Activity, 
  Scan, 
  Camera, 
  Info,
  Shield,
  Smartphone,
  X
} from 'lucide-react';

/**
 * PROXY PROTOCOL - IDENTITY MIGRATION UX (v1.0)
 * "Reputation is yours. The hardware is just a vessel."
 * ----------------------------------------------------
 */

const App = () => {
  const [step, setStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Mock State
  const [identity] = useState({
    did: "did:proxy:8A2E1C",
    reputation: 982,
    old_unit: "SENTRY-JP-001"
  });

  const [newUnit, setNewUnit] = useState(null);

  const nextStep = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setStep(prev => prev + 1);
    }, 1500);
  };

  const handleScanNewUnit = () => {
    setIsProcessing(true);
    // Simulate QR detection of new serial
    setTimeout(() => {
      setNewUnit({
        id: "SENTRY-VA-099",
        tpm_version: "2.0 (Infineon)",
        pcr_status: "NOMINAL"
      });
      setIsProcessing(false);
      setStep(3);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-indigo-500/30">
      
      {/* Background Decorative Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-xl w-full relative z-10">
        
        {/* Progress Stepper */}
        <div className="flex justify-between mb-12 px-6 relative">
           <div className="absolute top-1/2 left-0 w-full h-px bg-white/5 -z-10" />
           {[1, 2, 3, 4].map((s) => (
             <div key={s} className={`w-8 h-8 rounded-full flex items-center justify-center border text-[10px] font-black transition-all duration-500 ${
               step >= s ? 'bg-indigo-500 border-indigo-400 text-black shadow-[0_0_15px_rgba(99,102,241,0.5)]' : 'bg-black border-white/10 text-gray-700'
             }`}>
               0{s}
             </div>
           ))}
        </div>

        <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
          
          {/* Header */}
          <div className="p-6 border-b border-white/5 bg-white/[0.02] flex justify-between items-center px-10">
             <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-500/10 rounded border border-indigo-500/20">
                   <RotateCcw className={`w-4 h-4 text-indigo-500 ${isProcessing ? 'animate-spin' : ''}`} />
                </div>
                <div>
                   <h1 className="text-sm font-black text-white uppercase tracking-widest">Identity Migration</h1>
                   <p className="text-[9px] text-gray-600 font-bold uppercase tracking-widest mt-0.5">SSI Protocol v1.0</p>
                </div>
             </div>
             <div className="text-right">
                <span className="text-[9px] text-gray-700 uppercase font-black block">Status</span>
                <span className="text-[10px] text-indigo-400 font-bold tracking-widest">IN_PROGRESS</span>
             </div>
          </div>

          <div className="p-10 min-h-[400px] flex flex-col justify-between">
            
            {/* STEP 1: VERIFY SOVEREIGNTY */}
            {step === 1 && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="text-center">
                   <div className="p-4 bg-indigo-500/5 border border-indigo-500/10 rounded-full inline-block mb-6">
                      <Fingerprint className="w-12 h-12 text-indigo-500" />
                   </div>
                   <h2 className="text-xl font-black text-white uppercase tracking-tight mb-4">Confirm Identity Ownership</h2>
                   <p className="text-xs text-gray-500 leading-relaxed max-w-xs mx-auto italic">
                      "To migrate your standing, you must first sign a proof of authority using your Human Identity Key stored in this device."
                   </p>
                </div>

                <div className="p-5 bg-black border border-white/5 rounded-xl space-y-4">
                   <div className="flex justify-between items-center text-[10px]">
                      <span className="text-gray-600 font-black uppercase tracking-widest">DID Resolve</span>
                      <span className="text-white font-bold">{identity.did}</span>
                   </div>
                   <div className="flex justify-between items-center text-[10px]">
                      <span className="text-gray-600 font-black uppercase tracking-widest">Current Standing</span>
                      <span className="text-green-500 font-black">{identity.reputation} REP</span>
                   </div>
                </div>

                <button 
                  onClick={nextStep}
                  className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-indigo-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-xl"
                >
                  <Smartphone className="w-4 h-4" /> Sign Proof of Authority
                </button>
              </div>
            )}

            {/* STEP 2: SCAN NEW VESSEL */}
            {step === 2 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                <div className="text-center">
                   <div className="aspect-square w-48 mx-auto bg-black border-2 border-dashed border-white/10 rounded-3xl flex items-center justify-center relative overflow-hidden group">
                      {isProcessing ? (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-indigo-500/5">
                           <div className="w-full h-0.5 bg-indigo-500 animate-scan shadow-[0_0_15px_rgba(99,102,241,0.8)]" />
                           <RefreshCw className="w-6 h-6 text-indigo-500 animate-spin mt-4" />
                        </div>
                      ) : (
                        <Camera className="w-10 h-10 text-gray-700 group-hover:text-indigo-500 transition-colors" />
                      )}
                   </div>
                   <h2 className="text-xl font-black text-white uppercase tracking-tight mt-8 mb-2">Scan New Unit</h2>
                   <p className="text-xs text-gray-500">Align the QR code on the Proxy Sentry base.</p>
                </div>

                <button 
                  onClick={handleScanNewUnit}
                  disabled={isProcessing}
                  className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-indigo-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-xl"
                >
                  <Scan className="w-4 h-4" /> Initialize Camera
                </button>
              </div>
            )}

            {/* STEP 3: BIND & PENALTY */}
            {step === 3 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                <div className="p-6 bg-indigo-500/5 border border-indigo-500/20 rounded-xl flex items-center gap-6">
                   <div className="p-3 bg-indigo-500/10 rounded-lg"><Cpu className="w-8 h-8 text-indigo-500" /></div>
                   <div>
                      <span className="text-[9px] text-indigo-400 font-black uppercase tracking-widest block mb-0.5">New Hardware Binding</span>
                      <h3 className="text-lg font-black text-white uppercase tracking-tighter">{newUnit?.id}</h3>
                      <div className="flex items-center gap-2 mt-1">
                         <ShieldCheck className="w-3 h-3 text-green-500" />
                         <span className="text-[9px] text-gray-600 font-bold uppercase tracking-widest">TPM Integrity Verified</span>
                      </div>
                   </div>
                </div>

                <div className="p-6 border border-amber-500/20 bg-amber-500/5 rounded-xl">
                   <div className="flex items-center justify-between mb-4">
                      <h4 className="text-[10px] font-black text-amber-500 uppercase tracking-widest">Stability Adjustment</h4>
                      <AlertTriangle className="w-4 h-4 text-amber-500" />
                   </div>
                   <p className="text-[11px] text-gray-400 leading-relaxed mb-6 italic">
                     "Migration between hardware triggers a one-time 10% reputation stability adjustment (Rule 4.2) to mitigate risk during node warm-up."
                   </p>
                   <div className="flex justify-between items-center py-2 text-[10px] font-bold uppercase tracking-widest">
                      <span className="text-gray-500">Stability Penalty</span>
                      <span className="text-red-500">-98 REP</span>
                   </div>
                   <div className="flex justify-between items-center pt-3 border-t border-white/5 text-[10px] font-black uppercase tracking-widest">
                      <span className="text-white">Preserved Standing</span>
                      <span className="text-green-500">884 REP</span>
                   </div>
                </div>

                <button 
                  onClick={nextStep}
                  disabled={isProcessing}
                  className="w-full py-4 bg-indigo-500 text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-400 transition-all flex items-center justify-center gap-3 shadow-[0_0_30px_rgba(99,102,241,0.2)]"
                >
                  {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
                  Confirm & Bind Identity
                </button>
              </div>
            )}

            {/* STEP 4: SUCCESS */}
            {step === 4 && (
              <div className="text-center py-10 animate-in zoom-in-95 duration-500 space-y-10">
                <div className="w-24 h-24 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_60px_rgba(34,197,94,0.1)]">
                   <ShieldCheck className="w-12 h-12 text-green-500 animate-bounce" />
                </div>
                <div>
                   <h2 className="text-3xl font-black text-white uppercase tracking-tighter mb-3">Migration Finalized</h2>
                   <p className="text-xs text-gray-500 mb-10 max-w-sm mx-auto leading-relaxed uppercase tracking-widest font-bold">
                      Your standing is now anchored to <span className="text-white">{newUnit?.id}</span>. Old keys have been revoked from the oracle registry.
                   </p>
                </div>
                
                <div className="p-4 bg-black border border-white/5 rounded-xl flex items-center gap-4">
                   <Binary className="w-6 h-6 text-indigo-400" />
                   <div className="text-left flex-1">
                      <span className="text-[9px] text-gray-700 uppercase font-black block">Migration Hash</span>
                      <code className="text-[10px] text-gray-500 font-mono truncate block">0x8A2E...F91C3B...D2A1</code>
                   </div>
                </div>

                <button 
                  onClick={() => window.location.reload()}
                  className="px-12 py-4 bg-white text-black font-black text-[10px] uppercase tracking-widest hover:bg-green-500 transition-all rounded shadow-2xl"
                >
                  Return to Dashboard
                </button>
              </div>
            )}

          </div>

          {/* Footer Security Details */}
          <div className="p-4 bg-black border-t border-white/5 flex items-center justify-between px-10 text-[9px] font-black text-gray-700 uppercase tracking-widest">
             <div className="flex items-center gap-3">
                <Shield className="w-3.5 h-3.5 text-gray-700" />
                <span>SSI: did:proxy:v1</span>
             </div>
             <div className="flex gap-6">
                <span>E2EE: ACTIVE</span>
                <span>HW_LOCKED: TRUE</span>
             </div>
          </div>
        </div>

        {/* Support Context */}
        <div className="mt-8 flex justify-between items-center px-4 opacity-50 hover:opacity-100 transition-opacity">
           <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-gray-600" />
              <span className="text-[10px] text-gray-600 font-bold uppercase tracking-widest leading-none mt-0.5">Need help migrating?</span>
           </div>
           <button className="text-[10px] font-black text-gray-600 hover:text-white uppercase tracking-tighter flex items-center gap-1.5 transition-all">
             Onboarding Guide <ChevronRight className="w-3 h-3" />
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
      `}} />

    </div>
  );
};

export default App;
