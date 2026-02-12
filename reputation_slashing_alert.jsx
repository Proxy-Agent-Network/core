import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  Clock, 
  ShieldAlert, 
  Gavel, 
  ArrowRight, 
  ExternalLink, 
  Zap, 
  FileWarning, 
  Fingerprint, 
  Lock,
  ChevronRight,
  Info,
  X,
  History,
  Activity
} from 'lucide-react';

/**
 * PROXY PROTOCOL - REPUTATION SLASHING ALERT (v1.0)
 * "The final warning before automated bond liquidation."
 * ----------------------------------------------------
 */

const App = () => {
  const [timeLeft, setTimeLeft] = useState(7200); // 2 Hours in seconds
  const [isDismissed, setIsDismissed] = useState(false);
  
  // Mock Anomaly Data
  const [anomaly] = useState({
    id: "ANOMALY-88293-PX",
    type: "PCR_DRIFT_DETECTED",
    severity: "CRITICAL",
    bond_at_risk: 600000, // 30% of standard 2M bond
    timestamp: "2026-02-11T20:45:00Z",
    evidence_hash: "e3b0c442...98fc",
    description: "Hardware attestation failed. PCR 7 (Secure Boot) values do not match the authorized Golden State."
  });

  useEffect(() => {
    if (timeLeft <= 0) return;
    const timer = setInterval(() => {
      setTimeLeft(prev => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  if (isDismissed) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center p-8">
        <button 
          onClick={() => setIsDismissed(false)}
          className="px-6 py-3 bg-red-500/10 border border-red-500/20 text-red-500 font-black text-xs uppercase tracking-widest rounded hover:bg-red-500/20 transition-all"
        >
          Re-open Security Alert
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-red-500/30">
      
      {/* Background Warning Grid */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.05] z-0" 
           style={{ backgroundImage: 'radial-gradient(#ff3333 1px, transparent 1px)', backgroundSize: '30px 30px' }} />

      <main className="max-w-2xl w-full relative z-10 animate-in fade-in zoom-in-95 duration-500">
        
        {/* Main Alert Card */}
        <div className="bg-[#0a0a0a] border-2 border-red-500/40 rounded-xl overflow-hidden shadow-[0_0_50px_rgba(239,68,68,0.15)]">
          
          {/* Header Marquee */}
          <div className="bg-red-500 text-black py-2 px-4 flex justify-between items-center overflow-hidden whitespace-nowrap">
             <div className="flex gap-8 animate-marquee">
                {[...Array(10)].map((_, i) => (
                  <span key={i} className="text-[10px] font-black uppercase tracking-[0.3em] flex items-center gap-2">
                    <AlertTriangle className="w-3 h-3" /> SECURITY_BREACH_PROTOCOL_ACTIVE
                  </span>
                ))}
             </div>
          </div>

          <div className="p-8 md:p-12">
            <div className="flex justify-between items-start mb-8">
               <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl shadow-inner">
                  <ShieldAlert className="w-12 h-12 text-red-500 animate-pulse" />
               </div>
               <div className="text-right">
                  <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest block mb-1">Slash Countdown</span>
                  <span className="text-4xl font-black text-white tracking-tighter tabular-nums drop-shadow-lg">
                    {formatTime(timeLeft)}
                  </span>
               </div>
            </div>

            <div className="space-y-6 mb-10">
               <div>
                  <h2 className="text-2xl font-black text-white uppercase tracking-tight mb-2">Reputation Slash Pending</h2>
                  <div className="flex items-center gap-3 text-[10px] font-bold">
                    <span className="text-red-500 uppercase tracking-widest">Severity: {anomaly.severity}</span>
                    <div className="h-2 w-px bg-white/10" />
                    <span className="text-gray-500 uppercase tracking-widest">ID: {anomaly.id}</span>
                  </div>
               </div>

               <div className="bg-black/40 border border-white/5 p-6 rounded-lg">
                  <p className="text-sm text-gray-400 leading-relaxed mb-4 italic">
                    "{anomaly.description}"
                  </p>
                  <div className="flex items-center gap-4 text-[10px] text-gray-600 font-bold uppercase tracking-tighter">
                     <span className="flex items-center gap-1"><Fingerprint className="w-3 h-3" /> Proof Hash: {anomaly.evidence_hash.substring(0, 16)}</span>
                     <span>|</span>
                     <span className="flex items-center gap-1"><Activity className="w-3 h-3" /> Event: 2026.02.11 20:45</span>
                  </div>
               </div>

               <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-white/5 rounded border border-white/5">
                     <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Bond at Risk</span>
                     <span className="text-xl font-black text-red-400">-{anomaly.bond_at_risk.toLocaleString()} <span className="text-xs opacity-50">SATS</span></span>
                  </div>
                  <div className="p-4 bg-white/5 rounded border border-white/5">
                     <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Standing Impact</span>
                     <span className="text-xl font-black text-white">-50 <span className="text-xs opacity-50 text-red-500">REP</span></span>
                  </div>
               </div>
            </div>

            <div className="space-y-3">
               <button 
                 onClick={() => window.open('/insurance', '_blank')}
                 className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-red-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-xl group"
               >
                 <Gavel className="w-4 h-4 group-hover:rotate-12 transition-transform" />
                 Contest Verdict & Submit Logs
               </button>
               <button 
                 onClick={() => setIsDismissed(true)}
                 className="w-full py-3 border border-white/10 text-gray-600 font-black text-[10px] uppercase tracking-widest hover:text-white hover:border-white/20 transition-all"
               >
                 Acknowledge Anomaly
               </button>
            </div>
          </div>

          <div className="p-6 bg-red-500/5 border-t border-white/5 flex items-start gap-4">
             <Info className="w-5 h-5 text-red-500 shrink-0" />
             <p className="text-[10px] text-gray-500 leading-relaxed font-bold">
               LEGAL NOTICE: Failure to dispute within the 2-hour window constitutes an admission of fault. Funds will be burned according to the Slashing Engine v1.2 protocol rules.
             </p>
          </div>
        </div>

        {/* Action Link Footer */}
        <div className="mt-8 flex justify-between items-center px-4">
           <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping" />
              <span className="text-[9px] font-black uppercase text-red-500 tracking-widest">Active Security Event</span>
           </div>
           <a href="/support" className="text-[9px] font-black uppercase text-gray-600 hover:text-white transition-colors flex items-center gap-1.5 tracking-tighter">
             Technical Support Desk <ChevronRight className="w-3 h-3" />
           </a>
        </div>

      </main>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-marquee {
          animation: marquee 20s linear infinite;
        }
      `}} />
    </div>
  );
};

export default App;
