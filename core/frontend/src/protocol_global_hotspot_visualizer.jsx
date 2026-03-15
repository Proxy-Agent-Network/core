import React, { useState, useEffect, useMemo } from 'react';
import { 
  Globe, 
  Zap, 
  Activity, 
  ShieldCheck, 
  MapPin, 
  RefreshCw, 
  ChevronRight, 
  Info, 
  Lock, 
  Terminal, 
  Cpu, 
  LayoutGrid, 
  Database,
  Radio,
  Target,
  Waves,
  Maximize2
} from 'lucide-react';

/**
 * PROXY PROTOCOL - GLOBAL HOTSPOT VISUALIZER (v3.0.2)
 * "The Star Wars Map: Visualizing the biological edge."
 * ----------------------------------------------------
 */

const App = () => {
  const [lastTick, setLastTick] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [ripples, setRipples] = useState([]);
  
  // Canonical Node Clusters (Industrial Terminal Green)
  const clusters = [
    { id: 'VA', name: 'VA_HUB', x: 25, y: 35, nodes: 450, status: 'STABLE' },
    { id: 'LDN', name: 'UK_HUB', x: 48, y: 28, nodes: 380, status: 'STABLE' },
    { id: 'SG', name: 'SG_HUB', x: 78, y: 62, nodes: 310, status: 'STABLE' },
    { id: 'AZ', name: 'AZ_HUB', x: 18, y: 38, nodes: 142, status: 'STABLE' },
    { id: 'TKY', name: 'JP_HUB', x: 84, y: 36, nodes: 240, status: 'STABLE' },
    { id: 'BR', name: 'BR_HUB', x: 34, y: 72, nodes: 65, status: 'OPTIMIZING' }
  ];

  // Logic to spawn demand ripples (Task Intents)
  useEffect(() => {
    const interval = setInterval(() => {
      setLastTick(new Date());
      
      const source = clusters[Math.floor(Math.random() * clusters.length)];
      const newRipple = {
        id: Math.random().toString(36).substr(2, 9),
        x: source.x,
        y: source.y,
        timestamp: Date.now()
      };

      setRipples(prev => [...prev.slice(-10), newRipple]);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-[#00FF41] font-mono p-4 md:p-8 selection:bg-green-500/30 overflow-hidden flex flex-col">
      
      {/* Heavy Scanline Overlay */}
      <div className="fixed inset-0 pointer-events-none z-50 opacity-[0.03]" 
           style={{ backgroundImage: 'linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06))', backgroundSize: '100% 4px, 3px 100%' }} />

      <main className="max-w-7xl mx-auto w-full relative z-10 flex-1 flex flex-col gap-8">
        
        {/* Header: Visualizer Branding */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-[#00FF41]/20 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-xl shadow-[0_0_20px_rgba(0,255,65,0.1)]">
              <Globe className="w-8 h-8 text-green-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Global Hotspots</h1>
              <p className="text-[10px] text-green-500/60 uppercase tracking-widest font-bold mt-2">
                Biological Node Density // Sync_Block: <span className="text-white">882931</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-black/60 border border-green-500/10 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-green-900 uppercase font-black tracking-widest">Active Fleet</span>
                   <span className="text-xl font-black text-white tracking-tighter">1,248_UNITS</span>
                </div>
                <div className="h-8 w-px bg-green-500/10" />
                <button 
                  onClick={handleRefresh}
                  className={`p-2 border border-green-500/20 rounded hover:bg-green-500/10 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
                >
                  <RefreshCw className="w-4 h-4 text-green-900" />
                </button>
             </div>
          </div>
        </header>

        {/* The "Star Wars" Map Container */}
        <div className="relative flex-1 bg-black border border-green-500/10 rounded-2xl shadow-[inset_0_0_50px_rgba(0,255,65,0.05)] overflow-hidden">
           
           {/* Abstract Map Grid */}
           <div className="absolute inset-0 opacity-[0.05]" 
                style={{ backgroundImage: 'linear-gradient(to right, #00FF41 1px, transparent 1px), linear-gradient(to bottom, #00FF41 1px, transparent 1px)', backgroundSize: '60px 60px' }} />

           {/* World Map SVG Path (Simplified Projection) */}
           <svg className="absolute inset-0 w-full h-full opacity-[0.03] pointer-events-none fill-[#00FF41]" viewBox="0 0 100 100" preserveAspectRatio="none">
              <path d="M10,25 Q15,15 25,25 T40,35 T55,25 T70,35 T85,25 T95,35 L95,75 Q85,85 70,75 T55,85 T40,75 T25,85 T10,75 Z" />
           </svg>

           {/* Animated Ripples (Task Demand) */}
           <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
              {ripples.map((r) => (
                <g key={r.id}>
                  <circle cx={r.x} cy={r.y} r="0" fill="none" stroke="#6366f1" strokeWidth="0.2">
                    <animate attributeName="r" from="0" to="15" dur="3s" repeatCount="1" />
                    <animate attributeName="opacity" from="0.6" to="0" dur="3s" repeatCount="1" />
                  </circle>
                </g>
              ))}
           </svg>

           {/* Pulsing Node Clusters */}
           {clusters.map((hub) => (
             <div 
               key={hub.id}
               className="absolute transform -translate-x-1/2 -translate-y-1/2 group cursor-pointer"
               style={{ left: `${hub.x}%`, top: `${hub.y}%` }}
             >
                {/* Layered Pulsing Rings */}
                <div className="absolute inset-0 rounded-full bg-green-500/20 animate-ping" style={{ animationDuration: '3s' }} />
                <div className="absolute inset-0 rounded-full bg-green-500/10 animate-ping" style={{ animationDuration: '4s' }} />
                
                {/* Core Dot */}
                <div className="w-2.5 h-2.5 bg-green-500 rounded-full shadow-[0_0_15px_#00FF41] relative z-10 border border-white/20" />
                
                {/* Label Overlay */}
                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-4 opacity-0 group-hover:opacity-100 transition-opacity z-20">
                   <div className="bg-black/90 border border-green-500/30 p-3 rounded-lg shadow-2xl min-w-[120px]">
                      <span className="text-[10px] font-black text-white block mb-1 uppercase tracking-tighter">{hub.name}</span>
                      <div className="flex justify-between items-center text-[8px] font-bold text-green-500 uppercase tracking-widest">
                         <span>Nodes: {hub.nodes}</span>
                         <span className="animate-pulse">{hub.status}</span>
                      </div>
                   </div>
                </div>
             </div>
           ))}

           {/* Legend & Telemetry */}
           <div className="absolute bottom-8 left-8 flex flex-col gap-4">
              <div className="flex items-center gap-3">
                 <div className="w-2 h-2 bg-green-500 rounded-full shadow-[0_0_10px_#00FF41]" />
                 <span className="text-[10px] text-white font-black uppercase tracking-widest">Verified Hardware Cluster</span>
              </div>
              <div className="flex items-center gap-3">
                 <div className="w-2 h-2 border border-indigo-500 rounded-full shadow-[0_0_10px_#6366f1]" />
                 <span className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Real-time Task Intent</span>
              </div>
           </div>

           <div className="absolute top-8 right-8 text-right bg-black/40 p-4 rounded border border-white/5">
              <div className="flex items-center gap-2 justify-end mb-1">
                 <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                 <span className="text-[10px] text-green-500 font-black uppercase tracking-widest">Broadcasting Map v3.0.2</span>
              </div>
              <span className="text-[9px] text-gray-700 font-bold uppercase tracking-tighter font-mono">Telemetry Source: REGISTRY_SINK_B</span>
           </div>
        </div>

        {/* Tactical Overview Footer Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
           <div className="p-6 bg-black border border-green-500/10 rounded-xl flex items-center gap-6 group hover:border-green-500/30 transition-all">
              <div className="p-3 bg-green-500/5 rounded-lg group-hover:bg-green-500/10 transition-all">
                <Target className="w-6 h-6 text-green-500" />
              </div>
              <div>
                 <p className="text-[10px] text-green-900 font-black uppercase tracking-widest">Focus Hub</p>
                 <p className="text-lg font-black text-white uppercase tracking-tighter">JP_EAST (Tokyo)</p>
              </div>
           </div>
           <div className="p-6 bg-black border border-green-500/10 rounded-xl flex items-center gap-6 group hover:border-green-500/30 transition-all">
              <div className="p-3 bg-green-500/5 rounded-lg group-hover:bg-green-500/10 transition-all">
                <Activity className="w-6 h-6 text-green-500" />
              </div>
              <div>
                 <p className="text-[10px] text-green-900 font-black uppercase tracking-widest">Task Intensity</p>
                 <p className="text-lg font-black text-white uppercase tracking-tighter">High Surge</p>
              </div>
           </div>
           <div className="p-6 bg-black border border-green-500/10 rounded-xl flex items-center gap-6 group hover:border-green-500/30 transition-all">
              <div className="p-3 bg-green-500/5 rounded-lg group-hover:bg-green-500/10 transition-all">
                <Radio className="w-6 h-6 text-green-500" />
              </div>
              <div>
                 <p className="text-[10px] text-green-900 font-black uppercase tracking-widest">Signal Mode</p>
                 <p className="text-lg font-black text-white uppercase tracking-tighter">HODL_ESCROW_V2</p>
              </div>
           </div>
        </div>

      </main>

      {/* Industrial Footer */}
      <footer className="max-w-7xl mx-auto w-full mt-8 border-t border-white/5 pt-6 flex justify-between items-center opacity-40 hover:opacity-100 transition-opacity">
         <div className="flex gap-12 text-[10px] font-black uppercase tracking-widest text-green-900">
            <span>[*] HUD_STATE: NOMINAL</span>
            <span>[*] CLUSTER_SYNC: OK</span>
            <span>[*] LATENCY_MEAN: 42MS</span>
         </div>
         <div className="flex items-center gap-2">
            <span className="text-[9px] font-black text-gray-700 uppercase tracking-tighter">Proxy Protocol Foundation // 2026</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scan {
          0% { transform: translateY(-300px); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateY(300px); opacity: 0; }
        }
        .animate-scan {
          animation: scan 4s linear infinite;
        }
      `}} />

    </div>
  );
};

export default App;
