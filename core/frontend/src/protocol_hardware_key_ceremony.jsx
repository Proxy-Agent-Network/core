import React, { useState, useEffect, useRef } from 'react';
import { 
  Cpu, 
  ShieldCheck, 
  Fingerprint, 
  Lock, 
  RefreshCw, 
  Binary, 
  Terminal, 
  Activity, 
  Shield, 
  ChevronRight, 
  ArrowRight, 
  CheckCircle2, 
  Zap, 
  Info,
  AlertTriangle,
  Database,
  Unplug,
  Key,
  HardDrive
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HARDWARE KEY CEREMONY UX (v1.0)
 * "Sealing identity in silicon. The creation of the AK_HANDLE."
 * -----------------------------------------------------------
 */

const App = () => {
  const [step, setStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState([]);
  const [progress, setProgress] = useState(0);
  const scrollRef = useRef(null);

  const addLog = (msg, type = 'INFO') => {
    const ts = new Date().toLocaleTimeString([], { hour12: false });
    setLogs(prev => [...prev, { ts, msg, type }]);
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const simulateStep = (targetStep, duration, startLog, endLog, progressPoints) => {
    setIsProcessing(true);
    addLog(startLog, 'CMD');
    
    let p = 0;
    const interval = setInterval(() => {
      p += 5;
      if (p <= 100) setProgress(p);
    }, duration / 20);

    setTimeout(() => {
      clearInterval(interval);
      addLog(endLog, 'SUCCESS');
      setIsProcessing(false);
      setProgress(0);
      setStep(targetStep);
    }, duration);
  };

  const startCeremony = () => {
    simulateStep(2, 2500, 
      "[*] INIT: Requesting TPM 2.0 Ownership Hierarchy...", 
      "[✓] ACCESS: Primary Hierarchy Accessible (Infineon SLB9670).", 
      100
    );
  };

  const generateSeed = () => {
    simulateStep(3, 4000, 
      "[*] KEYGEN: Executing TPM2_CreatePrimary (RSA-2048)...", 
      "[✓] SEED: Hardware-bound Primary Seed finalized.", 
      100
    );
  };

  const createAK = () => {
    simulateStep(4, 5000, 
      "[*] BIND: Generating Attestation Key [AK_HANDLE: 0x81010002]...", 
      "[✓] IDENTITY: Non-exportable signing identity sealed in silicon.", 
      100
    );
  };

  const finalize = () => {
    simulateStep(5, 2000, 
      "[*] BROADCAST: Registering HW_ID with Reputation Oracle...", 
      "[✓] NETWORK: Node identity verified and globally reachable.", 
      100
    );
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-indigo-500/30">
      
      {/* Background Grid Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-2xl w-full relative z-10">
        
        {/* Progress Stepper */}
        <div className="flex justify-between mb-12 px-10 relative">
           <div className="absolute top-1/2 left-0 w-full h-px bg-white/5 -z-10" />
           {[1, 2, 3, 4].map((s) => (
             <div key={s} className={`w-10 h-10 rounded-full flex items-center justify-center border-2 text-xs font-black transition-all duration-700 ${
               step >= s ? 'bg-indigo-500 border-indigo-400 text-black shadow-[0_0_20px_rgba(99,102,241,0.4)]' : 'bg-black border-white/10 text-gray-700'
             }`}>
               0{s}
             </div>
           ))}
        </div>

        <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
          
          {/* Header Bar */}
          <div className="p-8 border-b border-white/5 bg-white/[0.02] flex justify-between items-center px-10">
             <div className="flex items-center gap-4">
                <div className="p-2 bg-indigo-500/10 rounded border border-indigo-500/20">
                   <Fingerprint className={`w-6 h-6 text-indigo-500 ${isProcessing ? 'animate-pulse' : ''}`} />
                </div>
                <div>
                   <h1 className="text-xl font-black text-white uppercase tracking-tighter leading-none">Key Ceremony</h1>
                   <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-1">Hardware Root of Trust v1.0</p>
                </div>
             </div>
             <div className={`px-4 py-1.5 rounded font-black text-[10px] uppercase tracking-widest ${isProcessing ? 'bg-indigo-500/20 text-indigo-400 animate-pulse' : 'bg-white/5 text-gray-600'}`}>
                {isProcessing ? 'Processing' : 'Awaiting Input'}
             </div>
          </div>

          <div className="p-10 min-h-[450px] flex flex-col justify-between">
            
            {/* Phase 1: Hardware Handshake */}
            {step === 1 && (
              <div className="space-y-8 animate-in fade-in duration-500 text-center max-w-sm mx-auto">
                 <div className="p-5 bg-indigo-500/5 border border-indigo-500/10 rounded-full inline-block mb-4">
                    <Cpu className="w-16 h-16 text-indigo-500" />
                 </div>
                 <h2 className="text-2xl font-black text-white uppercase tracking-tight">Detect Hardware</h2>
                 <p className="text-xs text-gray-500 leading-relaxed italic">
                   "Establishing a secure session with the physical TPM 2.0 module. Ensure your Proxy Sentry is connected and the chassis is closed."
                 </p>
                 <button 
                   onClick={startCeremony}
                   disabled={isProcessing}
                   className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-indigo-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-xl"
                 >
                   {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <HardDrive className="w-4 h-4" />}
                   Initialize Handshake
                 </button>
              </div>
            )}

            {/* Phase 2: Seed Generation */}
            {step === 2 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                <div className="flex items-start gap-6 p-8 bg-indigo-500/5 border border-indigo-500/20 rounded-2xl">
                   <div className="p-3 bg-indigo-500/10 rounded-lg"><Zap className="w-8 h-8 text-indigo-500" /></div>
                   <div>
                      <h3 className="text-white font-black text-xs uppercase mb-2">Generate Primary Seed</h3>
                      <p className="text-[11px] text-gray-500 leading-relaxed font-medium">
                        The seed is the mathematical root of your node identity. It is generated using true hardware randomness (TRNG) inside the Infineon secure element.
                      </p>
                   </div>
                </div>
                
                <div className="p-6 bg-black/40 border border-white/5 rounded-xl">
                   <div className="flex justify-between items-center mb-4">
                      <span className="text-[9px] text-gray-600 font-black uppercase tracking-widest">Entropy Strength</span>
                      <span className="text-[10px] text-green-500 font-bold tracking-tighter">256-BIT HIGH</span>
                   </div>
                   <div className="flex gap-1 h-1">
                      {[...Array(20)].map((_, i) => (
                        <div key={i} className="flex-1 bg-green-500/40 rounded-full" />
                      ))}
                   </div>
                </div>

                <button 
                  onClick={generateSeed}
                  disabled={isProcessing}
                  className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-indigo-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-xl"
                >
                  {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
                  Execute TPM2_CreatePrimary
                </button>
              </div>
            )}

            {/* Phase 3: Identity Sealing */}
            {step === 3 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                <div className="p-8 border border-white/5 bg-black/40 rounded-2xl relative overflow-hidden group">
                   <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:scale-110 transition-transform">
                      <Lock className="w-32 h-32 text-white" />
                   </div>
                   <h3 className="text-xl font-black text-white uppercase tracking-tighter mb-4 relative z-10">Seal Identity</h3>
                   <p className="text-xs text-gray-500 leading-relaxed mb-8 italic relative z-10">
                      "Finalizing the creation of the AK_HANDLE. This key is non-exportable; it will live and die within this specific piece of silicon."
                   </p>
                   <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-lg flex items-center gap-4 relative z-10">
                      <Binary className="w-6 h-6 text-indigo-400" />
                      <span className="text-[9px] text-gray-400 font-bold uppercase tracking-widest">Generating AK_HANDLE Context...</span>
                   </div>
                </div>

                <button 
                  onClick={createAK}
                  disabled={isProcessing}
                  className="w-full py-5 bg-indigo-500 text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-400 transition-all flex items-center justify-center gap-3 shadow-[0_0_40px_rgba(99,102,241,0.2)]"
                >
                  {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
                  Finalize Identity Binding
                </button>
              </div>
            )}

            {/* Phase 4: Final Verification */}
            {step === 4 && (
              <div className="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
                 <div className="text-center">
                    <div className="w-20 h-20 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                       <CheckCircle2 className="w-10 h-10 text-green-500" />
                    </div>
                    <h2 className="text-2xl font-black text-white uppercase tracking-tight">Ceremony Verified</h2>
                    <p className="text-xs text-gray-500">Node Standing: 100% HARDWARE_ATTUNED</p>
                 </div>

                 <div className="bg-black/60 border border-white/5 rounded-xl p-6 space-y-4">
                    <div className="flex justify-between items-center text-[10px]">
                       <span className="text-gray-600 font-black uppercase tracking-widest">Public Identity (HW_ID)</span>
                       <span className="text-white font-mono">0x8A2E...F91C</span>
                    </div>
                    <div className="flex justify-between items-center text-[10px]">
                       <span className="text-gray-600 font-black uppercase tracking-widest">Attestation Standard</span>
                       <span className="text-indigo-400 font-black tracking-tighter">RSA-OAEP / PSS</span>
                    </div>
                 </div>

                 <button 
                   onClick={finalize}
                   disabled={isProcessing}
                   className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-green-500 transition-all flex items-center justify-center gap-3"
                 >
                   {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
                   Broadcast Standing & Activate Node
                 </button>
              </div>
            )}

            {/* Success State */}
            {step === 5 && (
               <div className="text-center py-10 animate-in zoom-in-95 duration-700 space-y-8">
                  <div className="relative inline-block">
                     <ShieldCheck className="w-24 h-24 text-green-500 drop-shadow-[0_0_30px_rgba(34,197,94,0.4)]" />
                  </div>
                  <div>
                     <h2 className="text-4xl font-black text-white uppercase tracking-tighter mb-4">Node Active</h2>
                     <p className="text-sm text-gray-500 uppercase tracking-[0.2em] font-bold">Protocol v3.2.6 // Sentry Online</p>
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

          {/* Terminal / Log Footer */}
          <div className="bg-[#050505] border-t border-white/5 p-6 h-48 flex flex-col">
             <div className="flex justify-between items-center mb-4 text-[9px] font-black text-gray-600 uppercase tracking-[0.2em]">
                <div className="flex items-center gap-2">
                   <Terminal className="w-3 h-3" /> System_Daemon_Logs
                </div>
                <div className="flex items-center gap-2">
                   <div className={`w-1.5 h-1.5 rounded-full ${isProcessing ? 'bg-indigo-500 animate-pulse' : 'bg-gray-800'}`} />
                   <span>{isProcessing ? 'IO_BUSY' : 'READY'}</span>
                </div>
             </div>
             
             <div 
               ref={scrollRef}
               className="flex-1 overflow-y-auto space-y-2 font-mono text-[10px] scroll-smooth pr-4 scrollbar-hide"
             >
                {logs.length === 0 && (
                  <div className="text-gray-800 italic">[*] Awaiting ceremony initialization...</div>
                )}
                {logs.map((log, i) => (
                  <div key={i} className="flex gap-4">
                     <span className="text-gray-800 select-none">{log.ts}</span>
                     <span className={`
                       ${log.type === 'CMD' ? 'text-indigo-400 font-bold' : ''}
                       ${log.type === 'SUCCESS' ? 'text-green-500 font-black' : ''}
                       ${log.type === 'INFO' ? 'text-gray-500' : ''}
                     `}>{log.msg}</span>
                  </div>
                ))}
                {isProcessing && (
                  <div className="flex items-center gap-4">
                    <span className="text-gray-800">--:--:--</span>
                    <div className="flex-1 bg-white/5 h-0.5 rounded-full overflow-hidden">
                       <div className="bg-indigo-500 h-full animate-progress-glow" style={{ width: `${progress}%` }} />
                    </div>
                  </div>
                )}
             </div>
          </div>
        </div>

        {/* Global Security Disclaimer */}
        <div className="mt-8 flex justify-between items-center px-4 opacity-50 hover:opacity-100 transition-opacity">
           <div className="flex items-center gap-2 text-gray-600">
              <Shield className="w-4 h-4" />
              <span className="text-[10px] font-black uppercase tracking-widest leading-none">Standard: FIPS 140-2 Level 3</span>
           </div>
           <button className="text-[9px] font-black text-gray-600 hover:text-white uppercase tracking-tighter flex items-center gap-1.5 transition-all">
             View Security Docs <ChevronRight className="w-3 h-3" />
           </button>
        </div>

      </main>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes progress-glow {
          0% { box-shadow: 0 0 0px rgba(99, 102, 241, 0); }
          50% { box-shadow: 0 0 10px rgba(99, 102, 241, 0.4); }
          100% { box-shadow: 0 0 0px rgba(99, 102, 241, 0); }
        }
        .animate-progress-glow {
          animation: progress-glow 2s infinite;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
      `}} />

    </div>
  );
};

export default App;
