import React, { useState, useEffect } from 'react';
import { 
  QrCode, 
  ShieldCheck, 
  Cpu, 
  Zap, 
  RefreshCw, 
  ChevronRight, 
  ArrowRight, 
  CheckCircle2, 
  Lock, 
  Fingerprint, 
  Box, 
  Wifi, 
  Terminal, 
  Info, 
  Package,
  Activity,
  AlertTriangle,
  XCircle,
  Camera
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HARDWARE ACTIVATION UX (v1.0)
 * "Activating the Sentry: Physical receipt to network deployment."
 * ----------------------------------------------------
 */

const App = () => {
  const [step, setStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [unitId, setUnitId] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);

  // Mock Receipt Data
  const [receipt] = useState({
    serial: "SENTRY-JP-882-01",
    region: "JP_EAST",
    shipped_via: "DHL_EXPRESS",
    status: "IN_TRANSIT"
  });

  const handleScan = () => {
    setIsProcessing(true);
    // Simulate QR Camera focus and decode
    setTimeout(() => {
      setUnitId(receipt.serial);
      setIsProcessing(false);
      setStep(2);
    }, 2000);
  };

  const handleActivation = () => {
    setIsProcessing(true);
    // Simulate sequence:
    // 1. Establish E2EE Tunnel with Foundation
    // 2. Perform local TPM PCR Audit
    // 3. Hardware-sign 'DEPLOYED' attestation
    // 4. Update Registry API
    setTimeout(() => {
      setIsProcessing(false);
      setIsSuccess(true);
      setStep(4);
    }, 4000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-indigo-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-2xl w-full relative z-10">
        
        {/* Progress Stepper */}
        <div className="flex justify-between mb-12 px-10 relative">
           <div className="absolute top-1/2 left-0 w-full h-px bg-white/5 -z-10" />
           {[1, 2, 3, 4].map((s) => (
             <div key={s} className={`w-8 h-8 rounded-full flex items-center justify-center border-2 text-[10px] font-black transition-all duration-500 ${
               step >= s ? 'bg-indigo-500 border-indigo-400 text-black shadow-[0_0_15px_rgba(99,102,241,0.4)]' : 'bg-black border-white/10 text-gray-700'
             }`}>
               0{s}
             </div>
           ))}
        </div>

        <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
          
          {/* Header */}
          <div className="p-8 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
             <div className="flex items-center gap-4">
                <div className="p-2 bg-indigo-500/10 rounded border border-indigo-500/20">
                   <Package className="w-5 h-5 text-indigo-500" />
                </div>
                <div>
                   <h1 className="text-lg font-black text-white uppercase tracking-tight leading-none">Unit Activation</h1>
                   <p className="text-[9px] text-gray-600 uppercase tracking-widest font-bold mt-1">Sentry Deployment Protocol</p>
                </div>
             </div>
             <div className="text-right">
                <span className="text-[9px] text-gray-700 uppercase font-black block">Block Ref</span>
                <span className="text-xs text-gray-400 font-bold">882932</span>
             </div>
          </div>

          <div className="p-10 min-h-[400px] flex flex-col justify-between">
            
            {/* STEP 1: Scan QR */}
            {step === 1 && (
              <div className="space-y-10 animate-in fade-in duration-500 text-center">
                 <div className="max-w-xs mx-auto">
                    <div className="aspect-square bg-black border-2 border-dashed border-white/10 rounded-3xl flex items-center justify-center relative group overflow-hidden">
                       {isProcessing ? (
                         <div className="absolute inset-0 bg-indigo-500/5 flex flex-col items-center justify-center">
                            <div className="w-full h-0.5 bg-indigo-500 animate-scan shadow-[0_0_15px_rgba(99,102,241,0.8)]" />
                            <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin mt-4" />
                         </div>
                       ) : (
                         <Camera className="w-12 h-12 text-gray-800 group-hover:text-indigo-500 transition-colors" />
                       )}
                    </div>
                 </div>
                 
                 <div>
                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-3">Scan Unit Chassis</h2>
                    <p className="text-xs text-gray-500 leading-relaxed italic max-w-sm mx-auto">
                      "Point your camera at the QR code on the base of your Proxy Sentry unit to bind the physical serial ID to your operator standing."
                    </p>
                 </div>

                 <button 
                   onClick={handleScan}
                   disabled={isProcessing}
                   className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-indigo-500 hover:text-white transition-all rounded shadow-xl flex items-center justify-center gap-3"
                 >
                   <QrCode className="w-4 h-4" /> Initialize Scanner
                 </button>
              </div>
            )}

            {/* STEP 2: Authenticate Identity */}
            {step === 2 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                <div className="p-6 bg-indigo-500/5 border border-indigo-500/20 rounded-xl flex items-center gap-6">
                   <div className="p-3 bg-indigo-500/10 rounded-lg"><Box className="w-8 h-8 text-indigo-500" /></div>
                   <div>
                      <span className="text-[9px] text-indigo-400 font-black uppercase tracking-widest">Serial Identified</span>
                      <h3 className="text-lg font-black text-white uppercase">{unitId}</h3>
                      <span className="text-[10px] text-gray-600 font-bold uppercase">Jurisdiction: {receipt.region}</span>
                   </div>
                </div>

                <div className="bg-black/40 border border-white/5 rounded-xl p-6">
                   <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-4 flex items-center gap-2">
                      <Lock className="w-3.5 h-3.5" /> Operator Attestation
                   </h4>
                   <p className="text-xs text-gray-400 leading-relaxed mb-6 italic">
                     Confirm that you have received the unit in a tamper-free state and are authorized to activate it at your current physical coordinates.
                   </p>
                   <div className="flex items-center gap-3 p-4 bg-white/5 border border-white/5 rounded-lg">
                      <Wifi className="w-4 h-4 text-green-500" />
                      <span className="text-[10px] text-gray-400 font-bold uppercase">Proximity Verified via Local SSID Mesh</span>
                   </div>
                </div>

                <button 
                  onClick={() => setStep(3)}
                  className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-indigo-500 hover:text-white transition-all rounded shadow-xl flex items-center justify-center gap-3"
                >
                  Authorize Activation <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* STEP 3: The Deployment Ceremony */}
            {step === 3 && (
              <div className="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
                 <div className="text-center">
                    <div className="w-20 h-20 bg-indigo-500/10 border border-indigo-500/20 rounded-full flex items-center justify-center mx-auto mb-6 relative">
                       <Cpu className={`w-10 h-10 text-indigo-500 ${isProcessing ? 'animate-pulse' : ''}`} />
                       {isProcessing && <div className="absolute inset-0 bg-indigo-500/20 rounded-full animate-ping" />}
                    </div>
                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-2">Hardware Bootstrapping</h2>
                    <p className="text-xs text-gray-500">Generating un-exportable deployment keys...</p>
                 </div>

                 <div className="bg-[#050505] border border-white/5 rounded-xl p-6 h-40 flex flex-col font-mono text-[10px] shadow-inner">
                    <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
                       <span className="text-gray-700 font-black uppercase tracking-widest flex items-center gap-2"><Terminal className="w-3 h-3" /> Bootstrap_Log</span>
                       <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                    </div>
                    <div className="space-y-2 text-gray-500 overflow-y-auto flex-1 scrollbar-hide">
                       <p>[*] INVOKING TPM2_CREATEPRIMARY...</p>
                       <p>[*] GENERATING RSA-2048 IDENTITY KEY [AK]...</p>
                       {isProcessing && <p className="text-indigo-400 font-bold">[*] BROADCASTING DEPLOYMENT SIG TO REGISTRY...</p>}
                       {isProcessing && <p className="text-indigo-400 font-bold">[*] UPDATING SPATIAL HOTSPOT MAP...</p>}
                       <p className="animate-pulse">[*] WAITING_ATTESTATION...</p>
                    </div>
                 </div>

                 <button 
                  onClick={handleActivation}
                  disabled={isProcessing}
                  className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-xl"
                >
                  {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                  {isProcessing ? 'Deploying to Network...' : 'Confirm Delivery & Activate'}
                </button>
              </div>
            )}

            {/* STEP 4: Success */}
            {step === 4 && (
              <div className="text-center py-10 animate-in zoom-in-95 duration-500 space-y-10">
                <div className="w-24 h-24 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mx-auto mb-8 shadow-[0_0_60px_rgba(34,197,94,0.1)]">
                   <ShieldCheck className="w-12 h-12 text-green-500 animate-bounce" />
                </div>
                <div>
                   <h2 className="text-3xl font-black text-white uppercase tracking-tighter mb-3">Sentry Operational</h2>
                   <p className="text-xs text-gray-500 mb-10 max-w-sm mx-auto leading-relaxed italic uppercase tracking-widest">
                      Standing Updated: <span className="text-white">DEPLOYED</span><br/>
                      Region: <span className="text-indigo-400">{receipt.region}</span>
                   </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                   <div className="p-4 bg-black border border-white/5 rounded-xl flex items-center gap-4">
                      <Lock className="w-5 h-5 text-indigo-500" />
                      <div className="text-left">
                         <span className="text-[9px] text-gray-600 uppercase font-black block">Registry</span>
                         <span className="text-xs font-bold text-white uppercase tracking-tighter">SYNCHRONIZED</span>
                      </div>
                   </div>
                   <div className="p-4 bg-black border border-white/5 rounded-xl flex items-center gap-4">
                      <Activity className="w-5 h-5 text-green-500" />
                      <div className="text-left">
                         <span className="text-[9px] text-gray-600 uppercase font-black block">Health</span>
                         <span className="text-xs font-bold text-white uppercase tracking-tighter">OPTIMAL</span>
                      </div>
                   </div>
                </div>

                <button 
                  onClick={() => window.location.reload()}
                  className="px-12 py-4 bg-white text-black font-black text-xs uppercase tracking-widest hover:bg-green-500 transition-all rounded shadow-2xl"
                >
                  Enter Command Center
                </button>
              </div>
            )}

          </div>

          {/* Footer Security Note */}
          <div className="p-4 bg-black border-t border-white/5 flex items-center justify-between px-10 text-[9px] font-black text-gray-700 uppercase tracking-widest">
             <div className="flex items-center gap-3">
                <Fingerprint className="w-3.5 h-3.5" />
                <span>TPM Bound Identity</span>
             </div>
             <div className="flex gap-6">
                <span>AES-256-GCM</span>
                <span>HW_LOCKED: TRUE</span>
             </div>
          </div>
        </div>

        {/* Global Help Footer */}
        <div className="mt-8 flex justify-between items-center px-4">
           <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-gray-600" />
              <span className="text-[10px] text-gray-600 font-bold uppercase tracking-widest leading-none mt-0.5">Need help with your Sentry?</span>
           </div>
           <button className="text-[10px] font-black text-gray-600 hover:text-white uppercase tracking-tighter flex items-center gap-1.5 transition-all">
             Deployment Docs <ChevronRight className="w-3 h-3" />
           </button>
        </div>

      </main>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scan {
          0% { transform: translateY(-100px); }
          50% { transform: translateY(100px); }
          100% { transform: translateY(-100px); }
        }
        .animate-scan {
          animation: scan 3s ease-in-out infinite;
        }
      `}} />

    </div>
  );
};

export default App;
