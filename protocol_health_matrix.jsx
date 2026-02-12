import React, { useState, useEffect, useMemo } from 'react';
import { 
  Activity, 
  Zap, 
  Database, 
  ShieldCheck, 
  Globe, 
  RefreshCw, 
  AlertTriangle, 
  LayoutGrid, 
  Server, 
  Wifi, 
  Lock, 
  Cpu, 
  Clock,
  Unplug,
  History,
  Terminal,
  Activity as PulseIcon
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HEALTH MATRIX UI (v1.0)
 * "NOC-style observability for internal service dependencies."
 * ----------------------------------------------------
 */

const App = () => {
  const [lastTick, setLastTick] = useState(new Date());
  const [logs, setLogs] = useState([]);
  
  // Mock Real-time Dependency Data
  // In production, this state is updated via the Orchestrator WebSocket
  const [services, setServices] = useState([
    { id: 'LND-MAIN-01', type: 'PAYMENT', status: 'OPERATIONAL', load: '14%', uptime: '142d', ping: '2ms' },
    { id: 'LND-MAIN-02', type: 'PAYMENT', status: 'OPERATIONAL', load: '22%', uptime: '142d', ping: '3ms' },
    { id: 'TPM-ORACLE-V2', type: 'SECURITY', status: 'OPERATIONAL', load: '8%', uptime: '45d', ping: '12ms' },
    { id: 'REGISTRY-DB', type: 'DATA', status: 'OPERATIONAL', load: '45%', uptime: '89d', ping: '1ms' },
    { id: 'GEOFENCE-API-US', type: 'LOCATION', status: 'OPERATIONAL', load: '12%', uptime: '12d', ping: '42ms' },
    { id: 'GEOFENCE-API-EU', type: 'LOCATION', status: 'OPERATIONAL', load: '18%', uptime: '12d', ping: '84ms' },
    { id: 'GEOFENCE-API-ASIA', type: 'LOCATION', status: 'DEGRADED', load: '92%', uptime: '12d', ping: '260ms' },
    { id: 'NOSTR-RELAY-P2P', type: 'FALLBACK', status: 'OPERATIONAL', load: '2%', uptime: '201d', ping: '110ms' },
    { id: 'ESCROW-CONTRACT-V2', type: 'FINANCE', status: 'OPERATIONAL', load: '31%', uptime: '45d', ping: '5ms' },
    { id: 'REPUTATION-CRON', type: 'OPS', status: 'OPERATIONAL', load: '1%', uptime: '8h', ping: '0ms' },
    { id: 'IMAGE-SANITY-API', type: 'VISION', status: 'OPERATIONAL', load: '56%', uptime: '14d', ping: '120ms' },
    { id: 'AUTH-GATEWAY', type: 'SECURITY', status: 'OPERATIONAL', load: '67%', uptime: '142d', ping: '4ms' }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setLastTick(new Date());
      // Randomly fluctuate load for realism
      setServices(prev => prev.map(s => ({
        ...s,
        load: `${Math.min(99, Math.max(1, parseInt(s.load) + (Math.random() > 0.5 ? 1 : -1)))}%`
      })));
      
      if (Math.random() > 0.8) {
        const randomService = services[Math.floor(Math.random() * services.length)];
        addLog(`Service Heartbeat: ${randomService.id} reported health checkpoint.`);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [services]);

  const addLog = (msg) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [`[${timestamp}] ${msg}`, ...prev].slice(0, 10));
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'OPERATIONAL': return 'bg-green-500';
      case 'DEGRADED': return 'bg-yellow-500';
      case 'OFFLINE': return 'bg-red-500';
      default: return 'bg-gray-700';
    }
  };

  const getIcon = (type) => {
    switch(type) {
      case 'PAYMENT': return Zap;
      case 'SECURITY': return Lock;
      case 'DATA': return Database;
      case 'LOCATION': return Globe;
      case 'VISION': return Cpu;
      default: return Server;
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30">
      
      {/* Background Decorative Grid */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 border-b border-white/10 pb-8 gap-6">
          <div>
            <div className="flex items-center gap-4 mb-3">
              <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
                <LayoutGrid className="w-8 h-8 text-indigo-500 animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Protocol Health Matrix</h1>
                <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold font-mono">NOC Ops // Systemic Orchestration v1.0</p>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Sync Tick</span>
                   <span className="text-sm font-black text-white tracking-widest">{lastTick.toLocaleTimeString()}</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Overall Health</span>
                   <span className="text-xl font-black text-green-500 tracking-tighter">98.2%</span>
                </div>
             </div>
          </div>
        </header>

        {/* The Matrix Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {services.map((service) => {
            const Icon = getIcon(service.type);
            return (
              <div key={service.id} className="bg-[#0a0a0a] border border-white/5 rounded-xl p-6 shadow-2xl group hover:border-indigo-500/30 transition-all relative overflow-hidden">
                {/* Background Type Indicator */}
                <div className="absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform">
                  <Icon className="w-20 h-20 text-white" />
                </div>

                <div className="flex justify-between items-start mb-6 relative z-10">
                   <div className={`w-2.5 h-2.5 rounded-full ${getStatusColor(service.status)} ${service.status === 'OPERATIONAL' ? 'shadow-[0_0_10px_rgba(34,197,94,0.4)]' : 'animate-ping shadow-[0_0_10px_rgba(234,179,8,0.4)]'}`} />
                   <div className="text-right">
                      <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">{service.type}</span>
                   </div>
                </div>

                <div className="relative z-10 mb-6">
                   <h3 className="text-[11px] font-black text-white uppercase tracking-tighter truncate group-hover:text-indigo-400 transition-colors">{service.id}</h3>
                   <div className="flex items-center gap-2 text-[9px] text-gray-600 font-bold uppercase mt-1">
                      <Clock className="w-3 h-3" /> Uptime: {service.uptime}
                   </div>
                </div>

                <div className="grid grid-cols-2 gap-4 relative z-10 pt-4 border-t border-white/5">
                   <div>
                      <span className="text-[9px] text-gray-700 uppercase font-black block mb-1">Compute</span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-black text-white">{service.load}</span>
                        <div className="flex-1 bg-white/5 h-1 rounded-full overflow-hidden">
                           <div className="bg-indigo-500 h-full opacity-60" style={{ width: service.load }} />
                        </div>
                      </div>
                   </div>
                   <div className="text-right">
                      <span className="text-[9px] text-gray-700 uppercase font-black block mb-1">Latency</span>
                      <span className={`text-xs font-black ${parseInt(service.ping) > 100 ? 'text-red-400' : 'text-green-500'}`}>{service.ping}</span>
                   </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Lower Analysis Section */}
        <div className="grid grid-cols-12 gap-8">
           
           {/* Live Terminal Logs */}
           <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl flex flex-col h-[350px]">
              <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-8">
                 <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                   <Terminal className="w-4 h-4 text-emerald-500" /> Orchestrator Event Log
                 </h3>
                 <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-[9px] text-green-500 font-black uppercase tracking-widest">Live Stream Active</span>
                 </div>
              </div>
              <div className="p-8 font-mono text-[11px] space-y-3 overflow-y-auto flex-1 scrollbar-hide">
                 {logs.map((log, i) => (
                    <div key={i} className="flex gap-4 animate-in fade-in slide-in-from-left-2 duration-300">
                       <span className="text-gray-800 select-none">00{i+1}</span>
                       <span className={`${log.includes('checkpoint') ? 'text-gray-500' : 'text-indigo-400 font-bold'}`}>{log}</span>
                    </div>
                 ))}
                 <div className="flex gap-4 opacity-50">
                    <span className="text-gray-800 select-none">...</span>
                    <span className="text-gray-600 italic">Listening for PROTOCOL_TICK events from port 8008...</span>
                 </div>
              </div>
           </div>

           {/* Dependency Map / Context */}
           <div className="col-span-12 lg:col-span-4 space-y-6">
              <div className="p-8 border border-white/10 bg-[#0a0a0a] rounded-xl flex flex-col justify-between shadow-2xl relative overflow-hidden group">
                 <div className="absolute top-0 right-0 p-6 opacity-5">
                   <ShieldCheck className="w-24 h-24 text-white" />
                 </div>
                 <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2 relative z-10">
                    <Lock className="w-3.5 h-3.5 text-indigo-500" /> Security Overlay
                 </h4>
                 <p className="text-xs text-gray-500 leading-relaxed mb-8 italic relative z-10">
                    "Internal services communicate via a mesh VPN. Any node showing unauthenticated traffic is automatically quarantined from the Registry DB."
                 </p>
                 <div className="flex justify-between items-center text-[10px] font-black uppercase text-gray-600 border-t border-white/5 pt-4 relative z-10">
                    <span>Mesh Status</span>
                    <span className="text-green-500">ENCRYPTED</span>
                 </div>
              </div>

              <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-8 flex flex-col gap-4">
                 <div className="flex items-center gap-3">
                    <History className="w-5 h-5 text-indigo-400" />
                    <h4 className="text-xs font-black text-white uppercase tracking-widest">Protocol Recovery</h4>
                 </div>
                 <p className="text-[11px] text-gray-500 leading-relaxed font-medium">
                    The health matrix monitors the SEV-1 circuit breaker status. If 3 or more nodes in a cluster report PCR drift, the master orchestrator will trigger a global bridge freeze.
                 </p>
                 <button className="mt-4 w-full py-3 border border-indigo-500/30 text-indigo-400 font-black text-[9px] uppercase tracking-[0.2em] hover:bg-indigo-500 hover:text-black transition-all rounded">
                    Audit Circuit Breakers
                 </button>
              </div>
           </div>

        </div>

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <PulseIcon className="w-3 h-3 text-green-500 animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">NOC Core Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Synchronized with Orchestrator v1.0.8</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] DEP_COUNT: 12</span>
            <span>[*] MESH_ENCRYPTION: AES-GCM</span>
            <span>[*] VERSION: v2.8.1</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
