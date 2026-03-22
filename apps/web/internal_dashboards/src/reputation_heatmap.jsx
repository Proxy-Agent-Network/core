import React, { useState, useEffect } from 'react';
import { 
  Globe, 
  Activity, 
  Shield, 
  Zap, 
  MapPin, 
  Maximize2, 
  Navigation,
  Info,
  RefreshCw,
  TrendingUp,
  Cpu,
  Layers
} from 'lucide-react';

/**
 * PROXY PROTOCOL - GLOBAL REPUTATION HEATMAP (v1.0)
 * "Visualizing the geographical distribution of biological trust."
 * ----------------------------------------------------
 */

const App = () => {
  const [activeRegion, setActiveRegion] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock Geographical Data
  const [regions] = useState([
    { id: 'NA', name: "North America", nodes: 450, avgRep: 962, stability: "99.2%", status: "OPTIMAL", x: "25%", y: "35%" },
    { id: 'EU', name: "Europe", nodes: 380, avgRep: 945, stability: "98.8%", status: "STABLE", x: "50%", y: "30%" },
    { id: 'ASIA', name: "Asia Pacific", nodes: 310, avgRep: 912, stability: "94.5%", status: "ELEVATED", x: "75%", y: "45%" },
    { id: 'LATAM', name: "Latin America", nodes: 65, avgRep: 880, stability: "92.1%", status: "STABLE", x: "32%", y: "65%" },
    { id: 'MENA', name: "Middle East / Africa", nodes: 43, avgRep: 842, stability: "89.4%", status: "WARNING", x: "55%", y: "55%" }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1200);
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'OPTIMAL': return 'text-green-400';
      case 'STABLE': return 'text-blue-400';
      case 'ELEVATED': return 'text-yellow-500';
      case 'WARNING': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8">
      
      {/* Header */}
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-6 border-b border-white/10 pb-8 relative z-10">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
            <Globe className="w-8 h-8 text-indigo-500 animate-pulse" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Network Heatmap</h1>
            <div className="flex items-center gap-3 mt-1">
               <span className="text-[10px] text-gray-600 uppercase tracking-widest">Protocol v2.5.7</span>
               <div className="h-2 w-px bg-white/10" />
               <span className="text-[10px] text-green-500 font-bold uppercase tracking-widest flex items-center gap-1">
                 <Shield className="w-3 h-3" /> Global Integrity: 99.2%
               </span>
            </div>
          </div>
        </div>

        <div className="flex gap-4">
          <button 
            onClick={handleRefresh}
            className={`p-3 bg-white/5 border border-white/10 rounded hover:bg-white/10 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
          >
            <RefreshCw className="w-4 h-4 text-gray-500" />
          </button>
          <div className="bg-indigo-500/10 px-4 py-2 border border-indigo-500/20 rounded flex flex-col items-end">
             <span className="text-[9px] text-indigo-400 uppercase font-black">Active Regions</span>
             <span className="text-sm font-black text-white tracking-tighter">05_ACTIVE_HUBS</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-12 gap-8 relative z-10">
        
        {/* World Map Container */}
        <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl relative overflow-hidden h-[500px]">
          {/* Stylized Abstract World Map Grid */}
          <div className="absolute inset-0 opacity-10 pointer-events-none" 
               style={{ backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
          
          <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-4 flex items-center gap-2">
            <Navigation className="w-3.5 h-3.5" /> Live Node Clusters
          </h3>

          <div className="relative w-full h-full mt-8">
             {/* Map Region Points */}
             {regions.map((region) => (
               <div 
                 key={region.id}
                 className="absolute group transition-transform hover:scale-110 cursor-pointer"
                 style={{ left: region.x, top: region.y }}
                 onMouseEnter={() => setActiveRegion(region)}
                 onMouseLeave={() => setActiveRegion(null)}
               >
                 <div className={`w-4 h-4 rounded-full ${region.avgRep > 950 ? 'bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.6)]' : 'bg-green-500'} animate-pulse`} />
                 <div className="absolute -top-12 left-1/2 -translate-x-1/2 bg-black border border-white/10 p-2 rounded text-[10px] font-black whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-20">
                   {region.name} // {region.avgRep} REP
                 </div>
               </div>
             ))}

             {/* Map Background Illustration (SVG path for continents simplified) */}
             <svg viewBox="0 0 800 400" className="w-full h-full opacity-[0.05] absolute inset-0 pointer-events-none fill-white">
                <path d="M100,100 Q150,50 200,100 T300,150 T400,100 T500,200 T600,150 T700,100 T800,200 L800,400 L0,400 Z" />
             </svg>
          </div>
          
          <div className="absolute bottom-8 left-8 flex items-center gap-6">
             <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-indigo-500 rounded-full" />
                <span className="text-[9px] text-gray-500 font-bold uppercase tracking-widest">Super-Elite Hub</span>
             </div>
             <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="text-[9px] text-gray-500 font-bold uppercase tracking-widest">Standard Fleet</span>
             </div>
          </div>
        </div>

        {/* Side Panel: Regional Metrics */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
           <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl min-h-[500px] flex flex-col">
              <h3 className="text-xs font-black text-white uppercase tracking-widest mb-8 border-b border-white/10 pb-4">
                Hub Inspection
              </h3>

              {activeRegion ? (
                <div className="space-y-8 animate-in fade-in zoom-in-95 duration-200">
                   <div>
                      <span className="text-[9px] text-indigo-500 font-black uppercase tracking-widest block mb-1">Active Cluster</span>
                      <h2 className="text-3xl font-black text-white tracking-tighter uppercase">{activeRegion.name}</h2>
                   </div>

                   <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-white/5 rounded border border-white/5 text-center">
                         <p className="text-[9px] text-gray-600 uppercase font-black mb-1">Avg Reputation</p>
                         <p className="text-xl font-black text-white">{activeRegion.avgRep}</p>
                      </div>
                      <div className="p-4 bg-white/5 rounded border border-white/5 text-center">
                         <p className="text-[9px] text-gray-600 uppercase font-black mb-1">Integrity</p>
                         <p className="text-xl font-black text-green-500">{activeRegion.stability}</p>
                      </div>
                   </div>

                   <div className="space-y-4">
                      <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest">
                         <span className="text-gray-500">Fleet Density</span>
                         <span className="text-white">{activeRegion.nodes} Verified Nodes</span>
                      </div>
                      <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                         <div className="bg-indigo-500 h-full" style={{ width: `${(activeRegion.nodes/500)*100}%` }} />
                      </div>
                   </div>

                   <div className="pt-4 mt-auto">
                      <div className="p-4 border border-indigo-500/20 bg-indigo-500/5 rounded-lg flex items-center gap-4">
                         <div className="p-2 bg-indigo-500/10 rounded">
                            <Activity className="w-4 h-4 text-indigo-400" />
                         </div>
                         <div>
                            <p className="text-[9px] text-indigo-400 font-black uppercase tracking-widest">Network Status</p>
                            <p className={`text-[11px] font-bold uppercase ${getStatusColor(activeRegion.status)}`}>{activeRegion.status}</p>
                         </div>
                      </div>
                   </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center">
                   <Info className="w-12 h-12 text-gray-800 mb-4 animate-pulse" />
                   <h4 className="text-xs font-black text-gray-600 uppercase tracking-[0.2em]">Select a region on map</h4>
                   <p className="text-[10px] text-gray-800 mt-2 max-w-[200px]">Historical regional forensics will display here upon interaction.</p>
                </div>
              )}
           </div>
        </div>

        {/* Global Aggregate Cards */}
        <div className="col-span-12 grid grid-cols-1 md:grid-cols-3 gap-6">
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-lg shadow-xl group hover:border-indigo-500/30 transition-all">
              <div className="flex justify-between items-center mb-6">
                <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest">Hardware Standard</span>
                <Cpu className="w-4 h-4 text-indigo-500" />
              </div>
              <p className="text-3xl font-black text-white tracking-tighter">TPM 2.0</p>
              <p className="text-[9px] text-gray-700 mt-2 leading-relaxed">Mandatory Infineon OPTIGA™ attestation active for all regional clusters.</p>
           </div>
           
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-lg shadow-xl group hover:border-green-500/30 transition-all">
              <div className="flex justify-between items-center mb-6">
                <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest">Trust Growth</span>
                <TrendingUp className="w-4 h-4 text-green-500" />
              </div>
              <p className="text-3xl font-black text-white tracking-tighter">+0.4%</p>
              <p className="text-[9px] text-gray-700 mt-2 leading-relaxed">Reputation stability drift relative to previous protocol epoch.</p>
           </div>

           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-lg shadow-xl group hover:border-blue-500/30 transition-all">
              <div className="flex justify-between items-center mb-6">
                <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest">Data Layer</span>
                <Layers className="w-4 h-4 text-blue-500" />
              </div>
              <p className="text-3xl font-black text-white tracking-tighter">HYBRID</p>
              <p className="text-[9px] text-gray-700 mt-2 leading-relaxed">Cryptographic proof availability synchronized across all 5 global hubs.</p>
           </div>
        </div>
      </main>

      {/* Footer Marquee */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded p-4 flex items-center gap-6 overflow-hidden grayscale opacity-50 hover:grayscale-0 hover:opacity-100 transition-all duration-700">
         <div className="flex items-center gap-2 whitespace-nowrap">
           <div className="w-1.5 h-1.5 bg-green-500 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.4)]" />
           <span className="text-[9px] text-white font-black uppercase tracking-[0.2em]">Telemetry Synchronized</span>
         </div>
         <div className="h-4 w-px bg-white/10" />
         <div className="flex-1 flex gap-12 text-[9px] text-gray-600 font-bold uppercase tracking-widest animate-marquee whitespace-nowrap">
            <span>[*] LATENCY_US_WEST: 42ms</span>
            <span>[*] HUB_EU_LONDON: STABLE</span>
            <span>[*] HUB_ASIA_SG: OPTIMAL</span>
            <span>[*] REPUTATION_STABILITY: 99.2%</span>
            <span>[*] GLOBAL_NODE_COUNT: 1,248</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes marquee {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }
        .animate-marquee {
          animation: marquee 30s linear infinite;
        }
      `}} />
    </div>
  );
};

export default App;
