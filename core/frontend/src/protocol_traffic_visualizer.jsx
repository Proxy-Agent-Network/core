import React, { useState, useEffect, useMemo } from 'react';
import { 
  Zap, 
  Globe, 
  Activity, 
  ArrowRight, 
  ShieldCheck, 
  MapPin, 
  Cpu, 
  Database, 
  RefreshCw, 
  Lock, 
  Waves,
  LayoutGrid,
  TrendingUp,
  Info,
  ExternalLink,
  ChevronRight,
  Target,
  Box
} from 'lucide-react';

/**
 * PROXY PROTOCOL - TRAFFIC VISUALIZER (v1.0)
 * "Visualizing the movement of labor and capital in real-time."
 * ----------------------------------------------------
 */

const App = () => {
  const [lastTick, setLastTick] = useState(new Date());
  const [pulses, setPulses] = useState([]);
  const [stats, setStats] = useState({
    tasks_in_flight: 142,
    settlements_24h: 8422,
    velocity_sats_sec: 420
  });

  // Hub coordinates (Relative % for SVG)
  const hubs = {
    'US_WEST': { x: 20, y: 35, label: 'Phoenix Hub' },
    'US_EAST': { x: 35, y: 30, label: 'Delaware Hub' },
    'EU_WEST': { x: 50, y: 25, label: 'London Hub' },
    'ASIA_SE': { x: 80, y: 55, label: 'Singapore Hub' },
    'AGENT_CORE': { x: 10, y: 15, label: 'Global API Gateway' }
  };

  // Generate random traffic pulses
  useEffect(() => {
    const interval = setInterval(() => {
      setLastTick(new Date());
      
      // Randomly spawn a task or settlement pulse
      const type = Math.random() > 0.4 ? 'TASK' : 'SETTLEMENT';
      const hubKeys = Object.keys(hubs).filter(k => k !== 'AGENT_CORE');
      const targetHub = hubKeys[Math.floor(Math.random() * hubKeys.length)];
      
      const newPulse = {
        id: Math.random().toString(36).substr(2, 9),
        type,
        start: hubs['AGENT_CORE'],
        end: hubs[targetHub],
        value: Math.floor(Math.random() * 5000),
        timestamp: Date.now()
      };

      setPulses(prev => [...prev.slice(-15), newPulse]);
      
      // Fluctuating metrics
      setStats(prev => ({
        ...prev,
        tasks_in_flight: Math.floor(130 + Math.random() * 40),
        velocity_sats_sec: Math.floor(380 + Math.random() * 100)
      }));
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30 overflow-hidden">
      
      {/* Background Decorative Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 flex flex-col gap-6">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-xl shadow-[0_0_20px_rgba(34,197,94,0.1)]">
              <Activity className="w-8 h-8 text-green-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Traffic Visualizer</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Network Velocity // Synchronized Tick: <span className="text-indigo-400">{lastTick.toLocaleTimeString()}</span>
              </p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex flex-col items-end shadow-xl">
                <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">In-Flight</span>
                <span className="text-xl font-black text-white tracking-tighter">{stats.tasks_in_flight}</span>
             </div>
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex flex-col items-end shadow-xl">
                <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Velocity</span>
                <span className="text-xl font-black text-green-500 tracking-tighter">{stats.velocity_sats_sec} <span className="text-[10px] text-gray-700">S/s</span></span>
             </div>
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex flex-col items-end shadow-xl">
                <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Uptime</span>
                <span className="text-xl font-black text-indigo-400 tracking-tighter">99.98%</span>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Main Map Visualizer */}
          <div className="col-span-12 lg:col-span-9 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative overflow-hidden h-[600px]">
             
             {/* Map Background Grid */}
             <div className="absolute inset-0 opacity-10" 
                  style={{ backgroundImage: 'linear-gradient(to right, #333 1px, transparent 1px), linear-gradient(to bottom, #333 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

             <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                {/* Static Connections */}
                {Object.keys(hubs).filter(k => k !== 'AGENT_CORE').map(hub => (
                  <line 
                    key={hub}
                    x1={hubs['AGENT_CORE'].x} y1={hubs['AGENT_CORE'].y}
                    x2={hubs[hub].x} y2={hubs[hub].y}
                    stroke="rgba(255,255,255,0.03)"
                    strokeWidth="0.2"
                  />
                ))}

                {/* Animated Pulses */}
                {pulses.map((p) => (
                  <circle key={p.id} r="0.6" fill={p.type === 'TASK' ? '#6366f1' : '#22c55e'}>
                    <animateMotion 
                      dur="2s" 
                      repeatCount="1"
                      path={`M ${p.start.x} ${p.start.y} L ${p.end.x} ${p.end.y}`} 
                    />
                    <animate attributeName="opacity" values="1;0" dur="2s" fill="freeze" />
                  </circle>
                ))}
             </svg>

             {/* Node Hub Markers */}
             {Object.entries(hubs).map(([key, hub]) => (
               <div 
                key={key}
                className="absolute transform -translate-x-1/2 -translate-y-1/2 group"
                style={{ left: `${hub.x}%`, top: `${hub.y}%` }}
               >
                  <div className={`p-2 rounded-lg border shadow-2xl transition-all group-hover:scale-110 ${key === 'AGENT_CORE' ? 'bg-white text-black border-white' : 'bg-black border-white/10 group-hover:border-indigo-500/50'}`}>
                    {key === 'AGENT_CORE' ? <Box className="w-5 h-5" /> : <MapPin className="w-4 h-4" />}
                  </div>
                  <div className="absolute top-full left-1/2 -translate-x-1/2 mt-3 whitespace-nowrap">
                     <span className="text-[9px] font-black text-white uppercase tracking-widest bg-black/80 px-2 py-1 rounded border border-white/5 opacity-0 group-hover:opacity-100 transition-opacity">
                        {hub.label}
                     </span>
                  </div>
               </div>
             ))}

             <div className="absolute bottom-8 left-8 flex items-center gap-8">
                <div className="flex items-center gap-3">
                   <div className="w-2 h-2 bg-indigo-500 rounded-full shadow-[0_0_10px_rgba(99,102,241,0.6)]" />
                   <span className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Task Intent Packet</span>
                </div>
                <div className="flex items-center gap-3">
                   <div className="w-2 h-2 bg-green-500 rounded-full shadow-[0_0_10px_rgba(34,197,94,0.6)]" />
                   <span className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Satoshi Settlement</span>
                </div>
             </div>

             <div className="absolute top-8 right-8 text-right">
                <div className="flex items-center gap-2 justify-end mb-1">
                   <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                   <span className="text-[10px] text-green-500 font-black uppercase tracking-widest">Live Feed Synchronized</span>
                </div>
                <span className="text-[9px] text-gray-700 font-bold uppercase">Source: Orchestrator v1.0.8</span>
             </div>
          </div>

          {/* Right Sidebar Metrics */}
          <div className="col-span-12 lg:col-span-3 space-y-6">
             
             {/* Settlement Velocity */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-6 shadow-2xl">
                <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                   <TrendingUp className="w-4 h-4 text-green-500" /> Economic Pager
                </h3>
                <div className="space-y-4">
                   <div className="p-4 bg-white/5 rounded border border-white/5">
                      <span className="text-[9px] text-gray-600 uppercase font-black block mb-1 tracking-tighter">Settled (24h)</span>
                      <p className="text-xl font-black text-white tracking-tighter">8,422 <span className="text-[9px] text-green-500 font-bold tracking-widest">TASKS</span></p>
                   </div>
                   <div className="p-4 bg-white/5 rounded border border-white/5">
                      <span className="text-[9px] text-gray-600 uppercase font-black block mb-1 tracking-tighter">Throughput</span>
                      <p className="text-xl font-black text-white tracking-tighter">1.2 <span className="text-[9px] text-indigo-500 font-bold tracking-widest">PB/sec</span></p>
                   </div>
                </div>
             </div>

             {/* Network Policy */}
             <div className="p-8 border border-white/10 bg-indigo-500/5 rounded-xl flex flex-col justify-between">
                <div>
                   <div className="flex items-center gap-3 mb-4">
                      <Info className="w-5 h-5 text-indigo-400" />
                      <h4 className="text-xs font-black text-white uppercase tracking-widest">Traffic Policy</h4>
                   </div>
                   <p className="text-[11px] text-gray-500 leading-relaxed italic mb-8">
                      "Whale Pass tasks receive immediate priority routing across the US-EAST and ASIA-SE hub backbones."
                   </p>
                </div>
                <button className="w-full py-3 bg-white/5 border border-white/10 rounded-lg text-[9px] font-black uppercase text-indigo-400 hover:text-white transition-all flex items-center justify-center gap-2">
                   QoS Standards <ChevronRight className="w-3 h-3" />
                </button>
             </div>

             {/* Recent Activity Log */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl flex-1">
                <div className="p-4 border-b border-white/10 bg-white/[0.02]">
                   <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest">Packet Log</h3>
                </div>
                <div className="p-4 space-y-3 font-mono text-[9px]">
                   {pulses.slice(-5).reverse().map((p) => (
                      <div key={p.id} className="flex gap-3 animate-in fade-in slide-in-from-top-1">
                         <span className={p.type === 'TASK' ? 'text-indigo-500' : 'text-green-500'}>
                           {p.type === 'TASK' ? '[->]' : '[OK]'}
                         </span>
                         <span className="text-gray-500 uppercase font-bold">{p.type === 'TASK' ? 'Task_Routed' : 'Escrow_Paid'}</span>
                         <span className="text-gray-700 ml-auto">{p.value}s</span>
                      </div>
                   ))}
                </div>
             </div>
          </div>

        </div>

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-7xl mx-auto mt-8 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <Zap className="w-3 h-3 text-green-500 animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Lightning Backbone Operational</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Avg Block Confirmation: 8.2m</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] HUB_VITALITY: 94.2%</span>
            <span>[*] SAT_VELOCITY: NOMINAL</span>
            <span>[*] VERSION: v2.8.2</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
