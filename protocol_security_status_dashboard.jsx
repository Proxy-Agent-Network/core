import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Activity, 
  RefreshCw, 
  Lock, 
  Zap, 
  Radio, 
  Bell, 
  Database, 
  Binary, 
  Terminal, 
  Info, 
  ChevronRight, 
  AlertTriangle, 
  Cpu, 
  Unplug, 
  Layers, 
  Eye, 
  Bomb,
  Smartphone,
  Network,
  Fingerprint
} from 'lucide-react';

/**
 * PROXY PROTOCOL - SECURITY STATUS DASHBOARD (v1.1)
 * "The high-fidelity overview of the protocol's defensive posture."
 * ----------------------------------------------------
 * v1.1 Fix: Resolved HSM Identity box overlap and improved grid stability.
 */

const App = () => {
  const [threatLevel, setThreatLevel] = useState(12); // Percentage 0-100
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [logs, setLogs] = useState([
    { ts: '17:42:01', msg: 'ALERT_GATEWAY: Heartbeat stable (PGP_V1_LOCKED)', status: 'OK' },
    { ts: '17:42:05', msg: 'ANOMALY_ENGINE: Scanning /24 subnet clusters...', status: 'OK' },
    { ts: '17:43:10', msg: 'TELEMETRY_SINK: PCR check completed for 1,248 nodes', status: 'OK' }
  ]);

  // Real-time Threat Level fluctuation
  useEffect(() => {
    const interval = setInterval(() => {
      setThreatLevel(prev => {
        const drift = Math.random() > 0.5 ? 1 : -1;
        return Math.min(100, Math.max(5, prev + drift));
      });
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleManualRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      setLogs(prev => [
        { ts: new Date().toLocaleTimeString([], { hour12: false }), msg: 'MANUAL_SYNC: Security state refreshed across all hubs.', status: 'OK' },
        ...prev.slice(0, 9)
      ]);
    }, 1000);
  };

  const getThreatColor = (level) => {
    if (level < 20) return 'text-green-500';
    if (level < 50) return 'text-yellow-500';
    if (level < 80) return 'text-orange-500';
    return 'text-red-500';
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30">
      
      {/* Background Warning Overlay */}
      <div className={`fixed inset-0 pointer-events-none transition-opacity duration-1000 ${threatLevel > 70 ? 'opacity-10' : 'opacity-[0.02]'} z-0`} 
           style={{ backgroundImage: `radial-gradient(${threatLevel > 70 ? '#ff3333' : '#fff'} 1px, transparent 1px)`, backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header: SOC Desk */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
              <ShieldCheck className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none text-glow">Security Sentinel</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Protocol SOC // Fleet Integrity // Version <span className="text-indigo-400">v3.3.8</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Global Status</span>
                   <span className="text-xl font-black text-green-500 tracking-tighter uppercase">Defcon 5</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <button 
                  onClick={handleManualRefresh}
                  className={`p-2 border border-white/10 rounded hover:bg-white/10 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
                >
                  <RefreshCw className="w-4 h-4 text-gray-500" />
                </button>
             </div>
          </div>
        </header>

        {/* Threat Level Meter & Primary KPI Row */}
        <div className="grid grid-cols-12 gap-8">
          
          {/* Threat Level Component */}
          <div className="col-span-12 lg:col-span-4 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative overflow-hidden flex flex-col justify-between h-[450px]">
             <div className="flex justify-between items-start">
                <div>
                   <h3 className="text-xs font-black text-white uppercase tracking-widest mb-1 flex items-center gap-2">
                     <Activity className="w-4 h-4 text-indigo-500" /> Threat Level
                   </h3>
                   <p className="text-[10px] text-gray-600 uppercase font-bold">Real-time Anomaly Index</p>
                </div>
                <span className={`text-4xl font-black tracking-tighter tabular-nums ${getThreatColor(threatLevel)}`}>{threatLevel}%</span>
             </div>

             <div className="flex-1 flex items-center justify-center relative">
                <div className="w-48 h-48 rounded-full border-2 border-white/5 flex items-center justify-center relative">
                   <div className={`absolute inset-0 rounded-full opacity-20 animate-ping ${getThreatColor(threatLevel).replace('text', 'bg')}`} style={{ animationDuration: '3s' }} />
                   <div className={`w-32 h-32 rounded-full border-4 border-dashed border-white/10 animate-spin-slow`} />
                   <ShieldAlert className={`w-16 h-16 ${getThreatColor(threatLevel)} drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]`} />
                </div>
             </div>

             <div className="space-y-4">
                <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                   <div className={`h-full transition-all duration-1000 ${getThreatColor(threatLevel).replace('text', 'bg')}`} style={{ width: `${threatLevel}%` }} />
                </div>
                <div className="flex justify-between items-center text-[9px] font-black uppercase text-gray-700 tracking-widest">
                   <span>Baseline</span>
                   <span className={threatLevel > 50 ? 'text-red-500' : 'text-gray-500'}>Anomaly Threshold (50%)</span>
                </div>
             </div>
          </div>

          {/* Service Pillar Status & Master HSM Bar */}
          <div className="col-span-12 lg:col-span-8 flex flex-col gap-6 h-[450px]">
             <div className="grid grid-cols-1 md:grid-cols-3 gap-6 flex-1">
                {[
                  { name: 'Alert Gateway', status: 'ACTIVE', uptime: '142d 12h', icon: Bell, detail: 'PGP_GPG_v2.2' },
                  { name: 'Anomaly Engine', status: 'SCANNING', uptime: '45d 08h', icon: Radio, detail: 'SUBNET_V1.1_ACTIVE' },
                  { name: 'Telemetry Sink', status: 'SYNCED', uptime: '142d 12h', icon: Database, detail: 'PCR_WH_MATCH: 100%' }
                ].map((pillar, i) => (
                  <div key={i} className="bg-[#0a0a0a] border border-white/5 p-8 rounded-2xl shadow-xl flex flex-col justify-between group hover:border-indigo-500/30 transition-all">
                     <div className="flex justify-between items-start mb-6">
                        <div className="p-3 bg-white/5 rounded-xl border border-white/5 group-hover:border-indigo-500/20 transition-all">
                           <pillar.icon className="w-6 h-6 text-gray-500 group-hover:text-indigo-500" />
                        </div>
                        <div className="flex items-center gap-2">
                           <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                           <span className="text-[10px] text-green-500 font-black uppercase tracking-widest">{pillar.status}</span>
                        </div>
                     </div>
                     <div>
                        <h4 className="text-sm font-black text-white uppercase tracking-tighter mb-1">{pillar.name}</h4>
                        <p className="text-[9px] text-gray-600 font-bold uppercase tracking-widest">Uptime: {pillar.uptime}</p>
                     </div>
                     <div className="mt-6 pt-4 border-t border-white/5">
                        <span className="text-[9px] text-gray-500 font-mono tracking-tighter uppercase">{pillar.detail}</span>
                     </div>
                  </div>
                ))}
             </div>
             
             {/* Master HSM Status Bar - Now naturally follows the grid */}
             <div className="bg-indigo-500/5 border border-indigo-500/20 p-6 rounded-2xl flex items-center justify-between gap-8 shadow-2xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:scale-110 transition-transform">
                  <Fingerprint className="w-24 h-24 text-white" />
                </div>
                <div className="flex items-center gap-6 relative z-10">
                   <div className="p-4 bg-indigo-500/10 rounded-xl border border-indigo-500/20">
                      <Lock className="w-6 h-6 text-indigo-500" />
                   </div>
                   <div>
                      <h3 className="text-lg font-black text-white uppercase tracking-tighter mb-1">Master HSM Identity</h3>
                      <p className="text-[10px] text-gray-500 italic max-w-sm">"Root keys for PGP encryption and signature verification are sealed in the core secure enclave."</p>
                   </div>
                </div>
                <div className="text-right relative z-10 hidden md:block">
                   <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">State Root</span>
                   <code className="text-[10px] text-indigo-400 font-mono">0x8A2E...F91C</code>
                </div>
             </div>
          </div>
        </div>

        {/* Lower Detail Grid */}
        <div className="grid grid-cols-12 gap-8">
           
           {/* Incident Response Timeline */}
           <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[400px]">
              <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-8">
                 <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                   <Terminal className="w-4 h-4 text-emerald-500" /> Operational Event Stream
                 </h3>
                 <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-[9px] text-green-500 font-black uppercase tracking-widest">Security Link Active</span>
                 </div>
              </div>
              <div className="p-8 overflow-y-auto space-y-4 font-mono text-[11px] flex-1 scrollbar-hide">
                 {logs.map((log, i) => (
                    <div key={i} className="flex gap-6 animate-in fade-in slide-in-from-left-2 duration-300">
                       <span className="text-gray-700 shrink-0 select-none">{log.ts}</span>
                       <span className={`
                         ${log.status === 'OK' ? 'text-gray-500' : ''}
                         ${log.status === 'WARN' ? 'text-yellow-500 font-bold' : ''}
                         ${log.status === 'CRITICAL' ? 'text-red-500 font-black' : ''}
                       `}>{log.msg}</span>
                    </div>
                 ))}
                 <div className="flex gap-6 opacity-30">
                    <span className="text-gray-800 shrink-0">--:--:--</span>
                    <span className="italic">Awaiting incoming telemetry pulses from regional hubs...</span>
                 </div>
              </div>
           </div>

           {/* Emergency Action & Protocol Info */}
           <div className="col-span-12 lg:col-span-4 space-y-6">
              <div className="p-8 border border-red-500/10 bg-red-500/5 rounded-2xl shadow-2xl flex flex-col justify-between group overflow-hidden h-full min-h-[400px] relative">
                 <div className="absolute -bottom-4 -right-4 opacity-5 group-hover:scale-110 transition-transform">
                   <Bomb className="w-32 h-32 text-white" />
                 </div>
                 <div className="relative z-10">
                    <h4 className="text-[10px] font-black text-red-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                       <AlertTriangle className="w-4 h-4" /> Defense Protocol
                    </h4>
                    <p className="text-sm text-gray-500 leading-relaxed mb-8 italic font-bold">
                       "In the event of systemic PCR drift, the SOC desk is authorized to trigger the 'Circuit Breaker', instantly freezing all Lightning bridge settlements and PII ingress."
                    </p>
                 </div>
                 <button className="w-full py-4 border-2 border-red-600/50 text-red-500 font-black text-[10px] uppercase tracking-[0.3em] hover:bg-red-600 hover:text-white transition-all rounded-lg relative z-10">
                    Enter Kill Switch Panel
                 </button>
              </div>
           </div>

        </div>

        {/* Global Security Disclaimer Footer Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
           <div className="p-6 bg-white/[0.02] border border-white/5 rounded-xl flex items-center gap-6 group hover:border-indigo-500/30 transition-all">
              <div className="p-3 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500 group-hover:text-black transition-all">
                <Network className="w-5 h-5" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Mesh Link</p>
                 <p className="text-[11px] font-bold text-white uppercase tracking-tighter">SECURE_TUNNEL_ESTABLISHED</p>
              </div>
           </div>
           <div className="p-6 bg-white/[0.02] border border-white/5 rounded-xl flex items-center gap-6 group hover:border-emerald-500/30 transition-all">
              <div className="p-3 bg-emerald-500/10 rounded-lg group-hover:bg-emerald-500 group-hover:text-black transition-all">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Signature Trust</p>
                 <p className="text-[11px] font-bold text-white uppercase tracking-tighter">RSA_PSS_SHA256_VERIFIED</p>
              </div>
           </div>
           <div className="p-6 bg-white/[0.02] border border-white/5 rounded-xl flex items-center gap-6 group hover:border-blue-500/30 transition-all">
              <div className="p-3 bg-blue-500/10 rounded-lg group-hover:bg-blue-500 group-hover:text-black transition-all">
                <Smartphone className="w-5 h-5" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Alert Gateway</p>
                 <p className="text-[11px] font-bold text-white uppercase tracking-tighter">SIGNAL_PGP_READY</p>
              </div>
           </div>
        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">SOC Monitoring Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Ensuring the integrity of the autonomous edge."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] HSM_QUORUM: OK</span>
            <span>[*] NETWORK_INTEGRITY: 99.98%</span>
            <span>[*] VERSION: v3.3.8</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 20s linear infinite;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}} />

    </div>
  );
};

export default App;
