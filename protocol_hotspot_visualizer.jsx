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
  XCircle
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HOTSPOT VISUALIZER UI (v1.0)
 * "Mapping geographical demand to authorize hardware expansion."
 * ----------------------------------------------------
 */

const App = () => {
  const [lastSync, setLastSync] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedHotspot, setSelectedHotspot] = useState(null);

  // Mock Geographical Hotspots (Reflecting core/ops/traffic_profiler.py output)
  const hotspots = [
    { id: 'JP_TOKYO', name: 'Tokyo (JP-EAST)', x: 82, y: 38, intents: 4205, supply: 12, rating: 'CRITICAL', trend: '+142%' },
    { id: 'US_VA', name: 'Ashburn (US-EAST)', x: 28, y: 35, intents: 1840, supply: 85, rating: 'STABLE', trend: '+4%' },
    { id: 'EU_LDN', name: 'London (EU-WEST)', x: 48, y: 28, intents: 2100, supply: 42, rating: 'ELEVATED', trend: '+18%' },
    { id: 'SG_SIN', name: 'Singapore (ASIA-SE)', x: 78, y: 62, intents: 950, supply: 5, rating: 'CRITICAL', trend: '+88%' }
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
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Hotspot Visualizer</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Infrastructure Scaling // Sync: <span className="text-indigo-400">{lastSync.toLocaleTimeString()}</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Active Intents</span>
                   <span className="text-xl font-black text-white tracking-tighter">9,095 <span className="text-[10px] text-gray-700">TOTAL</span></span>
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
          
          {/* Main Visualizer: The Heat Map */}
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
                   <div className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                   <span className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Nominal Node Density</span>
                </div>
             </div>

             {/* World Map SVG with Hotspots */}
             <div className="relative w-full h-full mt-10">
                <svg className="w-full h-full opacity-20 pointer-events-none fill-white" viewBox="0 0 100 100" preserveAspectRatio="none">
                   <path d="M10,20 Q15,10 20,20 T30,30 T40,20 T50,40 T60,30 T70,20 T80,40 T90,30 L90,80 L10,80 Z" />
                </svg>

                {hotspots.map((spot) => (
                  <div 
                    key={spot.id}
                    onClick={() => setSelectedHotspot(spot)}
                    className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-500 hover:scale-125 z-20 group"
                    style={{ left: `${spot.x}%`, top: `${spot.y}%` }}
                  >
                     {/* Heat Ripples */}
                     <div className={`absolute inset-0 rounded-full animate-ping ${spot.rating === 'CRITICAL' ? 'bg-red-500/40' : 'bg-indigo-500/20'}`} style={{ animationDuration: '3s' }} />
                     <div className={`absolute inset-0 rounded-full animate-ping ${spot.rating === 'CRITICAL' ? 'bg-red-500/20' : 'bg-indigo-500/10'}`} style={{ animationDuration: '4.5s', animationDelay: '1s' }} />
                     
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
                <span className="text-[9px] text-gray-700 font-bold uppercase tracking-widest block mb-1">Spatial Engine v3.0</span>
                <span className="text-[10px] text-indigo-400 font-black uppercase flex items-center gap-2 justify-end">
                   <ShieldCheck className="w-3.5 h-3.5" /> Demand Validated via Hash-Chain
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

                     <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-white/5 border border-white/5 rounded text-center">
                           <span className="text-[8px] text-gray-600 uppercase font-black block mb-1">Intent Spikes</span>
                           <span className="text-lg font-black text-white">{selectedHotspot.intents}</span>
                        </div>
                        <div className="p-4 bg-white/5 border border-white/5 rounded text-center">
                           <span className="text-[8px] text-gray-600 uppercase font-black block mb-1">Supply Node</span>
                           <span className="text-lg font-black text-white">{selectedHotspot.supply}</span>
                        </div>
                     </div>

                     <div className="p-5 bg-indigo-500/5 border border-indigo-500/20 rounded-xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-2 opacity-5">
                           <Box className="w-16 h-16 text-white" />
                        </div>
                        <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                           <ShieldCheck className="w-3 h-3" /> Foundation Action
                        </h4>
                        <p className="text-[10px] text-gray-500 leading-relaxed italic mb-4">
                           "Unmet demand detected. Recommend dispatching 5+ Proxy Sentry Tier 2 units to restore regional SLA."
                        </p>
                        <button className="w-full py-2 bg-indigo-500 text-black font-black text-[9px] uppercase tracking-widest rounded hover:bg-indigo-400 transition-all">
                           Provision Shipment
                        </button>
                     </div>

                     <div className="flex justify-between items-center text-[10px] font-bold uppercase border-t border-white/5 pt-6">
                        <span className="text-gray-600">Saturation Trend</span>
                        <span className="text-red-500 flex items-center gap-1">
                           <TrendingUp className="w-3 h-3" /> {selectedHotspot.trend}
                        </span>
                     </div>
                  </div>
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center text-center opacity-40 grayscale">
                     <MapPin className="w-16 h-16 text-gray-800 mb-6 animate-bounce" />
                     <h4 className="text-xs font-black text-gray-600 uppercase tracking-widest mb-2">Selection Required</h4>
                     <p className="text-[10px] text-gray-800 uppercase font-bold tracking-tighter max-w-[180px]">
                        Select a ripple on the spatial map to view hardware logistics data
                     </p>
                  </div>
                )}
             </div>

             <div className="p-8 border border-white/10 bg-[#0a0a0a] rounded-xl shadow-2xl relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-[0.02] group-hover:scale-110 transition-transform">
                   <Globe className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5 text-indigo-500" /> Policy Context
                </h4>
                <p className="text-xs text-gray-500 leading-relaxed">
                   "Intents represent cryptographically-signed task requests that failed to find a matching node within the 60s gossip window."
                </p>
                <div className="mt-6 flex justify-between items-center text-[9px] font-black uppercase text-gray-700 border-t border-white/5 pt-4">
                   <span>Gossip Window</span>
                   <span className="text-green-500">OPTIMIZED</span>
                </div>
             </div>
          </div>

        </div>

        {/* Diagnostic Footer Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
           <div className="p-6 border border-white/5 bg-indigo-500/5 rounded-xl flex items-center gap-6 group hover:border-indigo-500/30 transition-all cursor-pointer">
              <div className="p-3 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500 group-hover:text-black transition-all">
                <Signal className="w-6 h-6" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Network Pull</p>
                 <p className="text-lg font-black text-white tracking-tighter">942.5 <span className="text-[10px] text-indigo-400">INDEX</span></p>
              </div>
           </div>
           <div className="p-6 border border-white/5 bg-red-500/5 rounded-xl flex items-center gap-6 group hover:border-red-500/30 transition-all cursor-pointer">
              <div className="p-3 bg-red-500/10 rounded-lg group-hover:bg-red-500 group-hover:text-black transition-all">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Demand Gaps</p>
                 <p className="text-lg font-black text-white tracking-tighter">02 <span className="text-[10px] text-red-500 font-bold uppercase">Critical</span></p>
              </div>
           </div>
           <div className="p-6 border border-white/5 bg-emerald-500/5 rounded-xl flex items-center gap-6 group hover:border-emerald-500/30 transition-all cursor-pointer">
              <div className="p-3 bg-emerald-500/10 rounded-lg group-hover:bg-emerald-500 group-hover:text-black transition-all">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Supply Match</p>
                 <p className="text-lg font-black text-white tracking-tighter">82% <span className="text-[10px] text-emerald-400 font-bold uppercase">EFFICIENCY</span></p>
              </div>
           </div>
        </div>

      </main>

      {/* Global Logistics Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Logistics Hub v3.0 Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Pending Shipments: 12 Units</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] LATENCY_OPTIMIZED: TRUE</span>
            <span>[*] SPATIAL_DENSITY: 0.12/km²</span>
            <span>[*] VERSION: v3.0.0</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
