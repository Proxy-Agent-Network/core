import React, { useState, useEffect, useMemo } from 'react';
import { 
  Zap, 
  Globe, 
  Activity, 
  Signal, 
  Navigation, 
  Clock, 
  RefreshCw, 
  ArrowRight, 
  ShieldCheck, 
  Info,
  BarChart3,
  Wifi,
  ChevronRight,
  Target,
  Layers,
  MapPin
} from 'lucide-react';

/**
 * PROXY PROTOCOL - NETWORK LATENCY PROFILER (v1.0)
 * "Optimizing the human routing layer."
 * ----------------------------------------------------
 */

const App = () => {
  const [isProbing, setIsProbing] = useState(false);
  const [lastAudit, setLastAudit] = useState(null);

  // Mock Hub Data
  const hubs = [
    { id: 'US-EAST', name: 'US East (Virginia)', base: 18, jitter: 2, status: 'OPTIMAL' },
    { id: 'US-WEST', name: 'US West (Oregon)', base: 84, jitter: 12, status: 'STABLE' },
    { id: 'EU-LONDON', name: 'Europe (London)', base: 142, jitter: 8, status: 'STABLE' },
    { id: 'ASIA-SG', name: 'Asia (Singapore)', base: 260, jitter: 45, status: 'DEGRADED' }
  ];

  const [results, setResults] = useState(
    hubs.map(h => ({ ...h, current: '--', sparkline: Array(20).fill(0) }))
  );

  const startProbe = () => {
    setIsProbing(true);
    setLastAudit(new Date().toLocaleTimeString());
    
    let iterations = 0;
    const interval = setInterval(() => {
      setResults(prev => prev.map(h => {
        const noise = Math.floor(Math.random() * h.jitter);
        const newPing = h.base + noise;
        const newSpark = [...h.sparkline.slice(1), newPing];
        return { ...h, current: newPing, sparkline: newSpark };
      }));

      iterations++;
      if (iterations >= 20) {
        clearInterval(interval);
        setIsProbing(false);
      }
    }, 150);
  };

  const optimalHub = useMemo(() => {
    const active = results.filter(r => typeof r.current === 'number');
    if (active.length === 0) return null;
    return active.reduce((prev, curr) => prev.current < curr.current ? prev : curr);
  }, [results]);

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30">
      
      {/* Background Decorative Grid */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '30px 30px' }} />

      <main className="max-w-6xl mx-auto relative z-10">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 gap-6 border-b border-white/10 pb-8">
          <div>
            <div className="flex items-center gap-4 mb-3">
              <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
                <Zap className={`w-8 h-8 text-indigo-500 ${isProbing ? 'animate-pulse' : ''}`} />
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Latency Profiler</h1>
                <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold">Backbone Diagnostics // Hub Prober v1.0</p>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Last Audit</span>
                   <span className="text-sm font-black text-white tracking-widest">{lastAudit || 'NEVER'}</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <button 
                  onClick={startProbe}
                  disabled={isProbing}
                  className={`flex items-center gap-3 px-6 py-2 bg-indigo-500 text-black font-black text-[10px] uppercase tracking-widest rounded hover:bg-indigo-400 transition-all disabled:opacity-50`}
                >
                  {isProbing ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Activity className="w-3 h-3" />}
                  {isProbing ? 'Probing...' : 'Run Benchmark'}
                </button>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Main Table: Regional Benchmarks */}
          <div className="col-span-12 lg:col-span-8 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <table className="w-full text-left border-collapse">
                   <thead>
                      <tr className="bg-white/[0.02] border-b border-white/5 font-black uppercase text-[10px] text-gray-600 tracking-widest">
                         <th className="p-6 w-12">Hub</th>
                         <th className="p-6">Geographical Node</th>
                         <th className="p-6 text-center">Current Latency</th>
                         <th className="p-6 text-right">Trend (20s)</th>
                      </tr>
                   </thead>
                   <tbody className="divide-y divide-white/5">
                      {results.map((hub) => (
                        <tr key={hub.id} className="group hover:bg-white/[0.01] transition-all">
                           <td className="p-6 text-indigo-500 font-black text-xs">{hub.id}</td>
                           <td className="p-6">
                              <span className="text-xs font-bold text-white block mb-0.5">{hub.name}</span>
                              <span className={`text-[9px] font-black uppercase ${hub.status === 'OPTIMAL' ? 'text-green-500' : hub.status === 'DEGRADED' ? 'text-red-500' : 'text-gray-600'}`}>{hub.status}</span>
                           </td>
                           <td className="p-6 text-center font-mono">
                              <span className={`text-xl font-black ${typeof hub.current === 'number' && hub.current < 50 ? 'text-green-500' : typeof hub.current === 'number' && hub.current > 150 ? 'text-red-400' : 'text-white'}`}>
                                 {hub.current}
                              </span>
                              <span className="text-[10px] text-gray-700 ml-1 font-bold uppercase">ms</span>
                           </td>
                           <td className="p-6 text-right">
                              <div className="h-8 flex items-end gap-0.5 justify-end">
                                 {hub.sparkline.map((val, idx) => (
                                   <div 
                                     key={idx} 
                                     className="w-1 bg-indigo-500/20" 
                                     style={{ height: `${(val / 300) * 100}%`, opacity: idx / 20 }} 
                                   />
                                 ))}
                              </div>
                           </td>
                        </tr>
                      ))}
                   </tbody>
                </table>
             </div>

             {/* Recommendation Panel */}
             {optimalHub && (
               <div className="p-8 border border-green-500/20 bg-green-500/5 rounded-xl animate-in slide-in-from-left-4 duration-500 shadow-2xl">
                  <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                     <div className="flex items-center gap-6">
                        <div className="p-4 bg-green-500/10 rounded-2xl border border-green-500/20">
                           <Target className="w-10 h-10 text-green-500 animate-pulse" />
                        </div>
                        <div>
                           <h3 className="text-lg font-black text-white uppercase tracking-tighter mb-1">Routing Recommendation</h3>
                           <p className="text-xs text-gray-500 max-w-sm leading-relaxed">
                              Based on current telemetry, <span className="text-green-500 font-bold">{optimalHub.id}</span> provides the lowest RTT. Reconfiguring daemon peer list for optimal task fulfillment.
                           </p>
                        </div>
                     </div>
                     <button className="px-8 py-3 bg-white text-black font-black text-[10px] uppercase tracking-widest hover:bg-green-500 transition-all rounded shadow-xl">
                        Apply Configuration
                     </button>
                  </div>
               </div>
             )}
          </div>

          {/* Sidebar Metrics */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             
             {/* Overall Health Card */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
                <h3 className="text-xs font-black text-white uppercase tracking-widest mb-8 flex items-center gap-2">
                   <Signal className="w-4 h-4 text-indigo-500" /> Connection Health
                </h3>
                <div className="space-y-6">
                   <div className="flex justify-between items-end mb-1">
                      <span className="text-[9px] text-gray-600 font-black uppercase">Global Egress</span>
                      <span className="text-lg font-black text-white">94.2%</span>
                   </div>
                   <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                      <div className="bg-indigo-500 h-full" style={{ width: '94.2%' }} />
                   </div>
                   <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-white/5 rounded text-center">
                         <p className="text-[9px] text-gray-600 uppercase font-black mb-1">Avg Jitter</p>
                         <p className="text-xl font-black text-white">12ms</p>
                      </div>
                      <div className="p-4 bg-white/5 rounded text-center">
                         <p className="text-[9px] text-gray-600 uppercase font-black mb-1">Packet Loss</p>
                         <p className="text-xl font-black text-green-500">0%</p>
                      </div>
                   </div>
                </div>
             </div>

             {/* Probing Logic Context */}
             <div className="p-6 border border-white/10 bg-[#0a0a0a] rounded-xl flex flex-col gap-4">
                <div className="flex items-center gap-3">
                   <Info className="w-5 h-5 text-gray-500" />
                   <h4 className="text-xs font-black text-white uppercase tracking-widest">Diagnostic Logic</h4>
                </div>
                <p className="text-[11px] text-gray-500 leading-relaxed italic">
                   "We use ICMP Echo Requests and TCP handshake timing to verify the speed of light constraints across jurisdictional boundaries."
                </p>
                <div className="flex justify-between items-center text-[9px] font-bold text-gray-600 border-t border-white/5 pt-4">
                   <span>Method</span>
                   <span className="uppercase tracking-widest">STABLE_RTT_V2</span>
                </div>
             </div>

             {/* World Map Snippet */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl relative overflow-hidden h-[250px] group">
                <div className="absolute inset-0 opacity-[0.03] pointer-events-none group-hover:scale-110 transition-transform duration-[2000ms]" 
                     style={{ backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)', backgroundSize: '20px 20px' }} />
                <h3 className="text-xs font-black text-gray-600 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <MapPin className="w-3.5 h-3.5" /> Logical Geofence
                </h3>
                <div className="flex flex-col items-center justify-center h-full relative z-10">
                   <Globe className="w-16 h-16 text-indigo-500/20 mb-4 animate-spin-slow" />
                   <span className="text-[9px] text-indigo-500 font-black uppercase tracking-[0.4em]">Tracking Packets...</span>
                </div>
                <div className="absolute bottom-4 left-4 flex flex-col gap-1">
                   <span className="text-[8px] font-black text-gray-800 uppercase tracking-widest">Local Egress: 192.168.1.101</span>
                   <span className="text-[8px] font-black text-gray-800 uppercase tracking-widest">ISP: COMCAST_BUSINESS_X1</span>
                </div>
             </div>
          </div>

        </div>

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-6xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Diagnostics: Ready</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Throughput Cap: 100 Mbps</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] HUB_COUNT: 04</span>
            <span>[*] PEERING: ENABLED</span>
            <span>[*] VERSION: v2.6.5</span>
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
      `}} />

    </div>
  );
};

export default App;
