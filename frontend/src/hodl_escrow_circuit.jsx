import React, { useState, useEffect } from 'react';
import { 
  Lock, 
  Unlock, 
  ShieldCheck, 
  Cpu, 
  Zap, 
  ArrowRight, 
  Timer, 
  AlertCircle,
  CheckCircle2,
  Database
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HODL ESCROW CIRCUIT (v1.0.0)
 * "Visualizing the non-custodial settlement of human labor."
 */

const HODLEscrowVisualizer = () => {
  const [step, setStep] = useState(0); // 0: Idle, 1: Locked, 2: Proof Pending, 3: Settled
  const [isAnimating, setIsAnimating] = useState(false);

  const steps = [
    { label: "Create Invoice", icon: <Zap /> },
    { label: "Lock Funds", icon: <Lock /> },
    { label: "Hardware Proof", icon: <Cpu /> },
    { label: "Settle Payment", icon: <CheckCircle2 /> }
  ];

  const advanceSimulation = () => {
    if (step < 3) {
      setIsAnimating(true);
      setTimeout(() => {
        setStep(prev => prev + 1);
        setIsAnimating(false);
      }, 1500);
    } else {
      setStep(0);
    }
  };

  return (
    <div className="w-full max-w-4xl bg-[#080808] border border-white/5 rounded-2xl p-8 shadow-2xl font-mono text-gray-300">
      <div className="flex justify-between items-start mb-12">
        <div>
          <h2 className="text-xl font-black text-white uppercase tracking-tighter flex items-center gap-3">
            <Zap className="w-5 h-5 text-amber-500 animate-pulse" />
            HODL Escrow Circuit
          </h2>
          <p className="text-[10px] text-gray-500 uppercase font-bold mt-1">Non-Custodial Settlement Layer // v1.0.0</p>
        </div>
        <div className="flex gap-2">
          {steps.map((s, i) => (
            <div key={i} className={`w-2 h-2 rounded-full ${i <= step ? 'bg-amber-500' : 'bg-white/10'}`} />
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center relative py-12">
        {/* Agent Side */}
        <div className={`p-6 rounded-xl border-2 transition-all duration-500 flex flex-col items-center gap-4 ${step >= 1 ? 'border-amber-500 bg-amber-500/5' : 'border-white/5 opacity-40'}`}>
          <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center">
            <Database className="w-6 h-6 text-gray-400" />
          </div>
          <span className="text-xs font-black uppercase">AI Principal</span>
          <div className="text-[10px] text-gray-600 uppercase font-bold">Funds: <span className="text-white">50k SATS</span></div>
        </div>

        {/* The Circuit / Escrow */}
        <div className="flex flex-col items-center justify-center relative">
          <div className={`w-24 h-24 rounded-full border-4 flex items-center justify-center transition-all duration-1000 ${
            step === 1 || step === 2 ? 'border-amber-500 animate-pulse' : 
            step === 3 ? 'border-green-500 shadow-[0_0_30px_#22c55e]' : 'border-white/5'
          }`}>
            {step < 3 ? <Lock className={`w-10 h-10 ${step >= 1 ? 'text-amber-500' : 'text-gray-800'}`} /> : <Unlock className="w-10 h-10 text-green-500" />}
          </div>
          <div className="absolute -bottom-8 whitespace-nowrap">
             <span className="text-[9px] font-black uppercase tracking-widest text-gray-500">
               {step === 0 && "Ready"}
               {step === 1 && "HTLC Accepted"}
               {step === 2 && "Awaiting TPM Proof"}
               {step === 3 && "Preimage Released"}
             </span>
          </div>
        </div>

        {/* Human Node Side */}
        <div className={`p-6 rounded-xl border-2 transition-all duration-500 flex flex-col items-center gap-4 ${step === 2 ? 'border-indigo-500 bg-indigo-500/5' : step === 3 ? 'border-green-500 bg-green-500/5' : 'border-white/5 opacity-40'}`}>
          <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center">
            <Cpu className={`w-6 h-6 ${step >= 2 ? 'text-indigo-400' : 'text-gray-400'}`} />
          </div>
          <span className="text-xs font-black uppercase">Human Node</span>
          <div className="text-[10px] text-gray-600 uppercase font-bold">Rep: <span className="text-white">920</span></div>
        </div>
      </div>

      <div className="mt-16 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-8">
        <div className="flex-1">
          <p className="text-[11px] text-gray-400 leading-relaxed italic max-w-sm">
            {step === 0 && "The circuit is open. No funds are committed."}
            {step === 1 && "Funds are locked in the Lightning Network. Human node can see the escrow but cannot claim it without the secret preimage."}
            {step === 2 && "The task is complete. The node is generating a TPM 2.0 hardware signature to prove execution."}
            {step === 3 && "Mathematical finality. The proof was valid, the preimage was revealed, and the Sats have moved instantly."}
          </p>
        </div>
        <button 
          onClick={advanceSimulation}
          disabled={isAnimating}
          className={`px-8 py-4 rounded-lg font-black text-xs uppercase tracking-widest transition-all ${
            step === 3 ? 'bg-green-600 text-white shadow-xl' : 'bg-white text-black hover:bg-amber-500'
          }`}
        >
          {isAnimating ? "Processing..." : step === 3 ? "Restart Simulation" : "Next Step"}
        </button>
      </div>
    </div>
  );
};

export default HODLEscrowVisualizer;
