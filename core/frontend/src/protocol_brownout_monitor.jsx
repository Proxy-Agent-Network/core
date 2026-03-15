import React, { useState, useEffect, useMemo } from 'react';
import { 
  Waves, 
  Activity, 
  ShieldAlert, 
  Zap, 
  ZapOff, 
  BarChart3, 
  Clock, 
  Lock, 
  ArrowUpRight, 
  LayoutGrid, 
  Info,
  RefreshCw,
  MoreHorizontal,
  ChevronRight,
  Database,
  Cpu,
  Unplug
} from 'lucide-react';

/**
 * PROXY PROTOCOL - BROWNOUT MONITOR (v1.0)
 * "Visualizing traffic shedding and network saturation."
 * ----------------------------------------------------
 */

const App = () => {
  const [mempoolDepth, setMempoolDepth] = useState(6402);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Congestion Tiers from specs/v1/brownout_logic.md
  const tiers = [
    { id: 'GREEN', label: 'OPTIMAL', range: '0 - 1k', minRep: 300, color: 'bg-green-500', text: 'text-green-500' },
    { id: 'YELLOW', label: 'ELEVATED', range: '1k - 5k', minRep: 500, color: 'bg-yellow-500', text: 'text-yellow-500' },
    { id: 'ORANGE', label: 'CONGESTED', range: '5k - 10k', minRep: 700, color: 'bg-orange-500', text: 'text-orange-500' },
    { id: 'RED', label: 'CRITICAL', range: '10k+', minRep: 900, color: 'bg-red-500', text: 'text-red-500' }
  ];

  const currentTier = useMemo(() => {
    if (mempoolDepth < 1000) return tiers[0];
    if (mempoolDepth < 5000) return tiers[1];
    if (mempoolDepth < 10000) return tiers[2];
    return tiers[3];
  }, [mempoolDepth]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setMempoolDepth(Math.floor(Math.random() * 12000));
      setIsRefreshing(false);
    }, 1000);
  };

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
                <Waves className={`w-8 h-8 text-indigo-500 ${currentTier.id === 'RED' ? 'animate-bounce' : 'animate-pulse'}`} />
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Brownout Monitor</h1>
                <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold">Network Satosity // Traffic Shaper v1.0</p>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Mempool Depth</span>
                   <span className="text-xl font-black text-white tracking-tighter">{mempoolDepth.toLocaleString()} <span className="text-[10px] text-gray-600 uppercase">Tasks</span></span>
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
          
          {/* Main Visualizer: The Congestion Wave */}
          <div className="col-span-12 lg:col-span-8 space-y-8">
            <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl relative overflow-hidden">
               {/* Tier Progress Bar */}
               <div className="flex justify-between items-end mb-4">
                  <h2 className="text-xl font-black text-white uppercase tracking-tight">Active Traffic Level</h2>
                  <span className={`text-lg font-black tracking-widest ${currentTier.text}`}>{currentTier.id} // {currentTier.label}</span>
               </div>
               
               <div className="w-full bg-white/5 h-4 rounded-full flex gap-1 overflow-hidden p-1">
                  {tiers.map(t => (
                    <div 
                      key={t.id} 
                      className={`flex-1 rounded-full transition-all duration-700 ${currentTier.id === t.id ? t.color : 'bg-white/5 opacity-20'}`} 
                    />
                  ))}
               </div>

               {/* Waveform Simulation */}
               <div className="h-48 flex items-end gap-1 mt-12 opacity-50">
                  {[...Array(60)].map((_, i) => (
                    <div 
                      key={i} 
                      className={`flex-1 ${currentTier.color} rounded-t-sm`} 
                      style={{ 
                        height: `${Math.random() * (mempoolDepth / 12000) * 100}%`,
                        opacity: 0.1 + (i / 60) * 0.4
                      }} 
                    />
                  ))}
               </div>

               <div className="absolute inset-0 pointer-events-none border-b-2 border-indigo-500/10" />
            </div>

            {/* Threshold Table */}
            <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-white/[0.02] border-b border-white/5">
                    <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest">Congestion Stage</th>
                    <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest">Task Threshold</th>
                    <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest">Min REP Required</th>
                    <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 font-mono">
                  {tiers.map((t) => {
                    const isActive = currentTier.id === t.id;
                    const isShed = mempoolDepth >= parseInt(t.range.split(' - ')[0].replace('k', '000'));
                    
                    return (
                      <tr key={t.id} className={`${isActive ? 'bg-white/[0.02]' : 'opacity-40'} transition-all`}>
                        <td className="p-6">
                           <div className="flex items-center gap-3">
                              <div className={`w-2 h-2 rounded-full ${t.color} ${isActive ? 'animate-ping' : ''}`} />
                              <span className="text-xs font-black text-white">{t.id}</span>
                           </div>
                        </td>
                        <td className="p-6 text-xs text-gray-400">{t.range}</td>
                        <td className="p-6">
                           <span className={`text-xs font-bold ${isActive ? 'text-indigo-400' : 'text-gray-600'}`}>{t.minRep} REP</span>
                        </td>
                        <td className="p-6 text-right">
                           <span className={`text-[9px] font-black uppercase px-2 py-1 rounded border ${isActive ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400' : 'border-white/5 text-gray-800'}`}>
                             {isActive ? 'ACTIVE_STAGE' : isShed ? 'STABLE' : 'PENDING'}
                           </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Sidebar Insights */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            
             {/* Live Shedding Metrics */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
                <h3 className="text-xs font-black text-white uppercase tracking-widest mb-8 flex items-center gap-2">
                  <ZapOff className="w-4 h-4 text-indigo-500" /> Shedding Analytics
                </h3>
                <div className="space-y-6">
                   <div className="p-4 bg-white/5 border border-white/5 rounded-lg flex justify-between items-center">
                      <div>
                         <span className="text-[9px] text-gray-600 uppercase font-black">Filtered Nodes</span>
                         <p className="text-xl font-black text-white">482 <span className="text-[9px] text-gray-600">OFFLINE</span></p>
                      </div>
                      <Unplug className="w-8 h-8 text-gray-700" />
                   </div>
                   <div className="p-4 bg-white/5 border border-white/5 rounded-lg flex justify-between items-center">
                      <div>
                         <span className="text-[9px] text-gray-600 uppercase font-black">Whale Priority</span>
                         <p className="text-xl font-black text-green-500">ACTIVE</p>
                      </div>
                      <ShieldAlert className="w-8 h-8 text-green-900/50" />
                   </div>
                   <p className="text-[10px] text-gray-600 leading-relaxed italic">
                     *Brownout Stage {currentTier.id} is currently shedding nodes with REP &lt; {currentTier.minRep}. All Whale-Pass agents bypass this filter.
                   </p>
                </div>
             </div>

             {/* Network Action Policy */}
             <div className="p-8 border border-white/10 bg-indigo-500/5 rounded-xl">
                <div className="flex items-center gap-3 mb-4">
                   <Info className="w-5 h-5 text-indigo-400" />
                   <h4 className="text-xs font-black text-white uppercase tracking-widest">Congestion Policy</h4>
                </div>
                <p className="text-[11px] text-gray-500 leading-relaxed mb-6">
                   "During Stage RED, only Super-Elite nodes (REP 900+) are permitted to accept task broadcasts. This maintains a 99% accuracy floor under stress."
                </p>
                <div className="flex justify-between items-center text-[9px] font-black uppercase text-gray-600 border-t border-white/10 pt-4">
                   <span>Auto-Recovery</span>
                   <span className="text-indigo-400">ENABLED</span>
                </div>
             </div>

             {/* Recent Shedding Log */}
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/5 bg-white/[0.02]">
                   <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest">Protocol Heartbeat</h3>
                </div>
                <div className="p-4 space-y-3 font-mono text-[9px]">
                   <div className="flex gap-3 text-gray-600"><span className="text-indigo-500">12:04:02</span> [*] Mempool Depth {'>'} 6,000</div>
                   <div className="flex gap-3 text-gray-400 font-bold"><span className="text-amber-500">12:04:02</span> [!] SHIFT_BROWNOUT_LEVEL {'->'} ORANGE</div>
                   <div className="flex gap-3 text-gray-600"><span className="text-indigo-500">12:04:05</span> [*] Shedding 142 probationary nodes...</div>
                   <div className="flex gap-3 text-gray-600"><span className="text-indigo-500">12:05:00</span> [*] Whale-Pass Agent T-882 routed via High Court.</div>
                </div>
             </div>
          </div>

        </div>

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-6xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className={`w-1.5 h-1.5 ${currentTier.color} rounded-full animate-pulse`} />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Stage {currentTier.id} active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Avg Completion: 14m (Tier 1)</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] LATENCY: 42MS</span>
            <span>[*] NODES: 1,248</span>
            <span>[*] VERSION: v2.6.3</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
