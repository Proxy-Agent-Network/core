import React, { useState, useEffect, useMemo } from 'react';
import { 
  ShieldAlert, 
  AlertTriangle, 
  Activity, 
  Zap, 
  RefreshCw, 
  TrendingUp, 
  Lock, 
  Unlock, 
  ChevronRight, 
  Info, 
  Percent, 
  History, 
  ShieldCheck, 
  Gavel, 
  Scale, 
  Database,
  Binary,
  Target,
  Gauge,
  AlertOctagon,
  ArrowUpRight,
  Flame
} from 'lucide-react';

/**
 * PROXY PROTOCOL - INSURANCE ACTUARY ALERT UI (v1.2)
 * "Visualizing the 0.5 Barrier: Systemic risk at the autonomous edge."
 * -------------------------------------------------------------------
 * v1.2 Fix: Removed rigid height constraints causing box overlap.
 * Integrated auto-flow for better responsive integrity.
 */

const App = () => {
  const [prob, setProb] = useState(0.124); // Starting probability 12.4%
  const [isEscalating, setIsEscalating] = useState(false);
  const [lastTick, setLastTick] = useState(new Date());
  const [logs, setLogs] = useState([
    { ts: '18:42:01', msg: 'ACTUARY: Baseline failure rate (2%) within nominal bounds.', type: 'STABLE' },
    { ts: '18:44:10', msg: 'ORCHESTRATOR: Hub US-EAST reporting 4% RTT drift.', type: 'INFO' }
  ]);

  // Real-time risk fluctuation logic
  useEffect(() => {
    const interval = setInterval(() => {
      setLastTick(new Date());
      setProb(prev => {
        const drift = Math.random() > 0.4 ? 0.005 : -0.003;
        const newVal = Math.max(0.05, Math.min(0.95, prev + drift));
        
        // Trigger escalation logic when crossing the 0.5 barrier
        if (newVal >= 0.5 && !isEscalating) {
          setIsEscalating(true);
          addLog("BARRIER_CROSS: Default probability > 0.5. Engaging fee escalation.", "CRITICAL");
        } else if (newVal < 0.45 && isEscalating) {
          setIsEscalating(false);
          addLog("BARRIER_RECOVER: Risk normalized. Reseting surcharge.", "SUCCESS");
        }
        
        return newVal;
      });
    }, 3000);
    return () => clearInterval(interval);
  }, [isEscalating]);

  const addLog = (msg, type) => {
    const ts = new Date().toLocaleTimeString([], { hour12: false });
    setLogs(prev => [{ ts, msg, type }, ...prev].slice(0, 8));
  };

  const currentLevy = useMemo(() => {
    const base = 0.001; // 0.1%
    const surcharge = isEscalating ? (prob * 0.004) : 0;
    return (base + surcharge).toFixed(4);
  }, [prob, isEscalating]);

  const getRiskColor = (p) => {
    if (p < 0.2) return 'text-green-500';
    if (p < 0.5) return 'text-blue-400';
    if (p < 0.7) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-red-500/30 overflow-x-hidden">
      
      {/* Background Warning Mesh */}
      <div className={`fixed inset-0 pointer-events-none transition-opacity duration-1000 ${prob > 0.5 ? 'opacity-10' : 'opacity-[0.02]'} z-0`} 
           style={{ 
             backgroundImage: `radial-gradient(${prob > 0.5 ? '#ef4444' : '#fff'} 1px, transparent 1px)`, 
             backgroundSize: '40px 40px' 
           }} />

      <main className="max-w-6xl w-full relative z-10 space-y-8 animate-in fade-in duration-700">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl shadow-2xl">
              <AlertOctagon className={`w-8 h-8 ${prob > 0.5 ? 'text-red-500 animate-ping' : 'text-indigo-500'}`} />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Actuary Sentinel</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Systemic Default Watchdog // Protocol <span className="text-red-500">v3.4.6</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Active Levy</span>
                   <span className={`text-xl font-black tracking-tighter ${isEscalating ? 'text-amber-500' : 'text-white'}`}>{currentLevy}%</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Global Status</span>
                   <span className={`text-xs font-black uppercase ${isEscalating ? 'text-red-500' : 'text-green-500'}`}>
                      {isEscalating ? 'Active Containment' : 'Stable'}
                   </span>
                </div>
             </div>
          </div>
        </header>

        {/* Primary Row: visualizer and logic */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          
          {/* Main Visualizer: The 0.5 Barrier */}
          <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative overflow-hidden flex flex-col min-h-[550px]">
             <div className="flex justify-between items-start mb-8 relative z-10">
                <div>
                   <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-2">
                     <Target className="w-4 h-4 text-red-500" /> Default Probability Barrier
                   </h3>
                   <p className="text-[10px] text-gray-600 font-bold uppercase mt-1">Bayesian Analysis Window (5m)</p>
                </div>
                <span className={`text-5xl font-black tracking-tighter tabular-nums ${getRiskColor(prob)}`}>
                  {(prob * 100).toFixed(1)}<span className="text-lg opacity-40">%</span>
                </span>
             </div>

             <div className="flex-1 flex items-center justify-center relative my-4">
                <div className="w-64 h-64 rounded-full border-4 border-white/5 flex items-center justify-center relative">
                   <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-full h-px border-t border-dashed border-white/20 rotate-[180deg]" />
                   </div>
                   
                   <div className="w-48 h-48 rounded-full border-2 border-white/5 relative overflow-hidden">
                      <div 
                        className={`absolute bottom-0 w-full transition-all duration-1000 ${prob > 0.5 ? 'bg-red-600' : 'bg-indigo-600'} opacity-20`} 
                        style={{ height: `${prob * 100}%` }} 
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                         <ShieldAlert className={`w-16 h-16 ${getRiskColor(prob)} drop-shadow-[0_0_15px_rgba(0,0,0,0.5)]`} />
                      </div>
                   </div>

                   <div className="absolute inset-0 animate-spin-slow pointer-events-none">
                      <div className="w-2 h-2 bg-white rounded-full blur-[2px]" style={{ transform: 'translateX(128px)' }} />
                   </div>
                </div>
                
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none w-full flex flex-col items-center">
                   <div className="w-px h-64 bg-red-500/20 border-l border-dashed border-red-500/40 relative">
                      <div className="absolute top-1/2 left-0 -translate-x-1/2 px-2 py-0.5 bg-red-600 text-white text-[8px] font-black uppercase rounded shadow-2xl">
                        Critical_Barrier_0.5
                      </div>
                   </div>
                </div>
             </div>

             <div className="mt-auto grid grid-cols-2 gap-8 relative z-10 border-t border-white/5 pt-8">
                <div>
                   <span className="text-[9px] text-gray-700 font-black uppercase block mb-1">Mempool Velocity</span>
                   <div className="flex items-center gap-3">
                      <Activity className="w-4 h-4 text-indigo-400" />
                      <span className="text-xl font-black text-white tracking-tighter">850 <span className="text-xs text-gray-600">SATS/S</span></span>
                   </div>
                </div>
                <div className="text-right">
                   <span className="text-[9px] text-gray-700 font-black uppercase block mb-1">Failure Drift</span>
                   <div className="flex items-center gap-3 justify-end">
                      <span className="text-xl font-black text-red-500 tracking-tighter">+4.2%</span>
                      <TrendingUp className="w-4 h-4 text-red-500" />
                   </div>
                </div>
             </div>
          </div>

          {/* Sidebar Column: Fixed flow and removed forced height */}
          <div className="col-span-12 lg:col-span-4 flex flex-col gap-8">
             {/* Containment Logic Box */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl flex flex-col flex-1 min-h-[350px]">
                <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-2 border-b border-white/10 pb-4">
                   <Zap className="w-4 h-4 text-amber-500" /> Containment Logic
                </h3>

                <div className="space-y-6">
                   <div className={`p-4 rounded-xl border flex justify-between items-center transition-all ${isEscalating ? 'bg-red-500/10 border-red-500/30' : 'bg-white/5 border-white/10 opacity-50'}`}>
                      <div>
                         <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Escalation Mode</span>
                         <span className={`text-sm font-black uppercase ${isEscalating ? 'text-red-500' : 'text-gray-500'}`}>
                            {isEscalating ? 'Active Surcharge' : 'Passive Monitoring'}
                         </span>
                      </div>
                      {isEscalating ? <Flame className="w-6 h-6 text-red-500 animate-pulse" /> : <Lock className="w-6 h-6 text-gray-800" />}
                   </div>

                   <div className="space-y-2">
                      <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest">
                         <span className="text-gray-500">Pool Solvency</span>
                         <span className="text-white">94.2%</span>
                      </div>
                      <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                         <div className="bg-green-500 h-full opacity-60" style={{ width: '94.2%' }} />
                      </div>
                   </div>
                   
                   <p className="text-[10px] text-gray-500 leading-relaxed italic border-t border-white/5 pt-4">
                      "Once probability crosses the 0.5 barrier, the protocol automatically increases the levy to discourage low-value volume."
                   </p>
                </div>
             </div>

             {/* Probability Log Box */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl flex flex-col h-[200px] shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h4 className="text-[9px] font-black text-gray-500 uppercase tracking-widest flex items-center gap-2">
                      <History className="w-3.5 h-3.5" /> Probability Log
                   </h4>
                   <div className={`w-1.5 h-1.5 rounded-full ${prob > 0.5 ? 'bg-red-500 animate-ping' : 'bg-gray-800'}`} />
                </div>
                <div className="p-6 font-mono text-[10px] space-y-3 overflow-y-auto flex-1 scrollbar-hide">
                   {logs.map((log, i) => (
                      <div key={i} className="flex gap-4">
                         <span className="text-gray-800 shrink-0">{log.ts}</span>
                         <span className={`
                            ${log.type === 'CRITICAL' ? 'text-red-500 font-bold' : ''}
                            ${log.type === 'SUCCESS' ? 'text-green-500' : ''}
                            ${log.type === 'WARN' ? 'text-yellow-500' : ''}
                            ${log.type === 'INFO' ? 'text-gray-500' : ''}
                            ${log.type === 'STABLE' ? 'text-blue-400' : ''}
                         `}>{log.msg}</span>
                      </div>
                   ))}
                </div>
             </div>
          </div>

        </div>

        {/* Global Security Grid: Fixed responsive card layouts to prevent overlap */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 relative z-10">
           <div className="p-6 border border-white/5 bg-indigo-500/5 rounded-xl flex items-center gap-5 group hover:border-indigo-500/30 transition-all overflow-hidden min-h-[100px]">
              <div className="p-3 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500 group-hover:text-black transition-all shrink-0">
                <Database className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">Reserve Audit</p>
                 <p className="text-sm font-bold text-white uppercase tracking-tighter truncate">LIQUIDITY_HEALTH_OK</p>
              </div>
           </div>
           <div className="p-6 border border-white/5 bg-emerald-500/5 rounded-xl flex items-center gap-5 group hover:border-emerald-500/30 transition-all overflow-hidden min-h-[100px]">
              <div className="p-3 bg-emerald-500/10 rounded-lg group-hover:bg-emerald-500 group-hover:text-black transition-all shrink-0">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">Actuarial Proof</p>
                 <p className="text-sm font-bold text-white uppercase tracking-tighter truncate">BAYES_V1_VERIFIED</p>
              </div>
           </div>
           <div className="p-6 border border-white/5 bg-blue-500/5 rounded-xl flex items-center gap-5 group hover:border-blue-500/30 transition-all overflow-hidden min-h-[100px]">
              <div className="p-3 bg-blue-500/10 rounded-lg group-hover:bg-blue-500 group-hover:text-black transition-all shrink-0">
                <Binary className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest truncate">State Logic</p>
                 <p className="text-sm font-bold text-white uppercase tracking-tighter truncate">TICK_SYNC_COMPLETE</p>
              </div>
           </div>
        </div>

      </main>

      {/* Global Status Bar: Removed overlap potential here too */}
      <footer className="max-w-6xl w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-6 flex flex-col md:flex-row items-center justify-between gap-4 opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className={`w-1.5 h-1.5 rounded-full animate-pulse ${prob > 0.5 ? 'bg-red-500' : 'bg-green-500'}`} />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Actuary Engine v1.0.4 Online</span>
            </div>
            <div className="h-4 w-px bg-white/10 hidden md:block" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic text-center md:text-left">"Ensuring protocol survival through algorithmic prudence."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest shrink-0">
            <span>[*] BARRIER: 0.5</span>
            <span>[*] LEVY_CAP: 0.5%</span>
            <span>[*] VERSION: v3.4.6</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 15s linear infinite;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
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
