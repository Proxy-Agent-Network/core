import React, { useState, useEffect } from 'react';
import { 
  Globe, 
  Target, 
  Zap, 
  Activity, 
  Box, 
  ShieldCheck, 
  ArrowRight, 
  RefreshCw, 
  Info, 
  Lock, 
  AlertTriangle, 
  Navigation,
  Map as MapIcon,
  ChevronRight,
  TrendingUp,
  Radio,
  Signal,
  MapPin,
  XCircle,
  Truck,
  Plane,
  Package
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HOTSPOT VISUALIZER UI (v1.1)
 * "Logistical Reinforcements: Mapping the supply chain of trust."
 * ----------------------------------------------------
 */

const App = () => {
  const [lastSync, setLastSync] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedHotspot, setSelectedHotspot] = useState(null);

  // Mock Geographical Hotspots (Demand)
  const hotspots = [
    { id: 'JP_TOKYO', name: 'Tokyo (JP-EAST)', x: 82, y: 38, intents: 4205, supply: 12, rating: 'CRITICAL', trend: '+142%' },
    { id: 'US_VA', name: 'Ashburn (US-EAST)', x: 28, y: 35, intents: 1840, supply: 85, rating: 'STABLE', trend: '+4%' },
    { id: 'EU_LDN', name: 'London (EU-WEST)', x: 48, y: 28, intents: 2100, supply: 42, rating: 'ELEVATED', trend: '+18%' },
    { id: 'SG_SIN', name: 'Singapore (ASIA-SE)', x: 78, y: 62, intents: 950, supply: 5, rating: 'CRITICAL', trend: '+88%' }
  ];

  // Mock Logistics Data (Supply Chain Reinforcements)
  const reinforcements = [
    { id: 'SENTRY-JP-001', type: 'AIR', start: {x: 10, y: 15}, end: {x: 82, y: 38}, progress: 65, status: 'IN_TRANSIT' },
    { id: 'SENTRY-SG-005', type: 'ROAD', start: {x: 50, y: 30}, end: {x: 78, y: 62}, progress: 30, status: 'IN_TRANSIT' },
    { id: 'SENTRY-LDN-012', type: 'ROAD', start: {x: 55, y: 15}, end: {x: 48, y: 28}, progress: 85, status: 'IN_TRANSIT' }
  ];

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setLastSync(new Date());
      setIsRefreshing(false);
    }, 1200);
  };

  const getRatingColor = (rating) => {
    switch(rating) {
      case 'CRITICAL': return 'text-red-500';
      case 'ELEVATED': return 'text-yellow-500';
      case 'STABLE': return 'text-green-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30 overflow-hidden">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header: Logistics Command */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
              <Target className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Logistics Command</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Reinforcement Tracking // Sync: <span className="text-indigo-400">{lastSync.toLocaleTimeString()}</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">In-Transit</span>
                   <span className="text-xl font-black text-amber-500 tracking-tighter">{reinforcements.length} UNITS</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <button 
                  onClick={handleRefresh}
                  className={`p-2 border border-white/10 rounded hover:bg-white/10 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
                >
                  <RefreshCw className="w-4 h-4 text-gray-500" />
                </button>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Main Visualizer: The Heat Map + Logistics Overlay */}
          <div className="col-span-12 lg:col-span-9 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative h-[650px] overflow-hidden">
             
             {/* Map Decoration */}
             <div className="absolute inset-0 opacity-10 pointer-events-none" 
                  style={{ backgroundImage: 'linear-gradient(to right, #333 1px, transparent 1px), linear-gradient(to bottom, #333 1px, transparent 1px)', backgroundSize: '60px 60px' }} />

             <div className="absolute top-8 left-8 flex flex-col gap-4">
                <div className="flex items-center gap-2">
                   <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping" />
                   <span className="text-[10px] text-red-500 font-black uppercase tracking-widest">Critical Shortage Area</span>
                </div>
                <div className="flex items-center gap-2">
                   <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse" />
                   <span className="text-[10px] text-amber-500 font-black uppercase tracking-widest">Reinforcement Inbound</span>
                </div>
             </div>

             {/* World Map SVG Layer */}
             <div className="relative w-full h-full mt-10">
                <svg className="absolute inset-0 w-full h-full opacity-[0.05] pointer-events-none fill-white" viewBox="0 0 100 100" preserveAspectRatio="none">
                   <path d="M10,20 Q15,10 20,20 T30,30 T40,20 T50,40 T60,30 T70,20 T80,40 T90,30 L90,80 L10,80 Z" />
                </svg>

                {/* Logistics Paths & Reinforcements */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                  {reinforcements.map((r) => (
                    <g key={r.id}>
                      <line 
                        x1={r.start.x} y1={r.start.y} 
                        x2={r.end.x} y2={r.end.y} 
                        stroke="#f59e0b" 
                        strokeWidth="0.1" 
                        strokeDasharray="1,1" 
                        opacity="0.3"
                      />
                      {/* Animated Delivery Icon */}
                      <circle r="0.8" fill="#f59e0b">
                        <animateMotion 
                          dur="10s" 
                          repeatCount="indefinite" 
                          path={`M ${r.start.x} ${r.start.y} L ${r.end.x} ${r.end.y}`} 
                        />
                      </circle>
                    </g>
                  ))}
                </svg>

                {/* Hotspots */}
                {hotspots.map((spot) => (
                  <div 
                    key={spot.id}
                    onClick={() => setSelectedHotspot(spot)}
                    className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-500 hover:scale-125 z-20 group"
                    style={{ left: `${spot.x}%`, top: `${spot.y}%` }}
                  >
                     <div className={`absolute inset-0 rounded-full animate-ping ${spot.rating === 'CRITICAL' ? 'bg-red-500/40' : 'bg-indigo-500/20'}`} style={{ animationDuration: '3s' }} />
                     
                     <div className={`p-2.5 rounded-full border-2 shadow-2xl bg-black relative z-10 ${
                       spot.rating === 'CRITICAL' ? 'border-red-500 shadow-red-500/40' : 
                       spot.rating === 'ELEVATED' ? 'border-yellow-500' : 
                       'border-green-500/40'
                     }`}>
                        <Radio className={`w-4 h-4 ${spot.rating === 'CRITICAL' ? 'text-red-500 animate-pulse' : 'text-indigo-400'}`} />
                     </div>

                     <div className="absolute top-full left-1/2 -translate-x-1/2 mt-4 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="bg-black/90 border border-white/10 p-2 rounded shadow-2xl flex flex-col items-center">
                           <span className="text-[9px] font-black text-white uppercase">{spot.name}</span>
                           <span className="text-[8px] text-gray-500 font-bold uppercase">{spot.intents} Intents</span>
                        </div>
                     </div>
                  </div>
                ))}
             </div>

             <div className="absolute bottom-8 right-8 text-right">
                <span className="text-[9px] text-gray-700 font-bold uppercase tracking-widest block mb-1">Reinforcement Engine v1.1</span>
                <span className="text-[10px] text-amber-500 font-black uppercase flex items-center gap-2 justify-end">
                   <Package className="w-3.5 h-3.5" /> Logistical Parity: 84%
                </span>
             </div>
          </div>

          {/* Right Sidebar: Hotspot Analysis & Recommendations */}
          <div className="col-span-12 lg:col-span-3 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl min-h-[400px] flex flex-col">
                <h3 className="text-xs font-black text-white uppercase tracking-widest mb-10 flex items-center gap-2 border-b border-white/5 pb-4">
                   <Activity className="w-4 h-4 text-indigo-500" /> Regional Brief
                </h3>

                {selectedHotspot ? (
                  <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
                     <div>
                        <span className="text-[9px] text-indigo-400 font-black uppercase tracking-widest block mb-1">Target Hub</span>
                        <h2 className="text-2xl font-black text-white tracking-tighter uppercase">{selectedHotspot.id}</h2>
                     </div>

                     <div className="space-y-3">
                        <div className="p-4 bg-white/5 border border-white/5 rounded-lg flex justify-between items-center">
                           <span className="text-[9px] text-gray-600 uppercase font-black">Demand/Supply</span>
                           <span className="text-sm font-black text-white">{selectedHotspot.intents} / {selectedHotspot.supply}</span>
                        </div>
                        
                        {/* Status for Inbound Units */}
                        <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg flex justify-between items-center">
                           <span className="text-[9px] text-amber-500 uppercase font-black">Reinforcements</span>
                           <span className="text-sm font-black text-amber-400">+2 Units</span>
                        </div>
                     </div>

                     <div className="p-5 bg-indigo-500/5 border border-indigo-500/20 rounded-xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-2 opacity-5">
                           <Box className="w-16 h-16 text-white" />
                        </div>
                        <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                           <ShieldCheck className="w-3 h-3" /> Hardware Registry
                        </h4>
                        <p className="text-[10px] text-gray-500 leading-relaxed italic mb-4">
                           "SENTRY-JP-001 is currently 65% through the trans-pacific shipping lane. Estimated activation in 48h."
                        </p>
                        <button className="w-full py-2 bg-indigo-500 text-black font-black text-[9px] uppercase tracking-widest rounded hover:bg-indigo-400 transition-all">
                           Track Shipment
                        </button>
                     </div>
                  </div>
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center text-center opacity-40 grayscale">
                     <MapPin className="w-16 h-16 text-gray-800 mb-6 animate-bounce" />
                     <h4 className="text-xs font-black text-gray-600 uppercase tracking-widest mb-2">Selection Required</h4>
                     <p className="text-[10px] text-gray-800 uppercase font-bold tracking-tighter max-w-[180px]">
                        Select a ripple to view hardware arrival estimates
                     </p>
                  </div>
                )}
             </div>

             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden flex flex-col">
                <div className="p-4 bg-white/[0.02] border-b border-white/5">
                   <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest">In-Transit Manifest</h3>
                </div>
                <div className="p-4 space-y-3">
                   {reinforcements.map(r => (
                      <div key={r.id} className="flex items-center justify-between">
                         <div className="flex items-center gap-2">
                            {r.type === 'AIR' ? <Plane className="w-3 h-3 text-amber-500" /> : <Truck className="w-3 h-3 text-amber-500" />}
                            <span className="text-[10px] text-gray-400 font-bold">{r.id}</span>
                         </div>
                         <div className="flex items-center gap-2">
                            <span className="text-[9px] text-gray-600 uppercase font-black">{r.progress}%</span>
                            <div className="w-8 bg-white/5 h-1 rounded-full overflow-hidden">
                               <div className="bg-amber-500 h-full" style={{ width: `${r.progress}%` }} />
                            </div>
                         </div>
                      </div>
                   ))}
                </div>
             </div>
          </div>

        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Supply Chain Watch Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Fleet Capacity: 1,248 (+12 Pending)</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] LATENCY_RECOVERY: ACTIVE</span>
            <span>[*] SHIPMENT_PRIORITY: HIGH</span>
            <span>[*] VERSION: v3.0.2</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
