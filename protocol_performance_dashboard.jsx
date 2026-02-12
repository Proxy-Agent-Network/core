import React, { useState, useEffect, useMemo } from 'react';
import { 
  Zap, 
  Activity, 
  Clock, 
  TrendingUp, 
  BarChart3, 
  Globe, 
  Cpu, 
  RefreshCw, 
  Info, 
  ChevronRight, 
  LayoutGrid, 
  Percent, 
  Search,
  ArrowUpRight,
  ShieldCheck,
  Binary,
  Target,
  Gauge,
  AlertTriangle
} from 'lucide-react';

/**
 * PROXY PROTOCOL - PERFORMANCE DASHBOARD (v1.0)
 * "Visualizing systemic throughput and latency-driven economics."
 * ----------------------------------------------------
 */

const App = () => {
  const [lastTick, setLastTick] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [view, setView] = useState('SYSTEMIC'); // SYSTEMIC, REGIONAL

  // Mock Real-time Vitals (Reflecting core/ops/performance_profiler.py output)
  const [vitals] = useState({
    tps: 8.42,
    p50_ms: 412,
    p90_ms: 890,
    p99_ms: 1840,
    congestion_multiplier: 1.14,
    samples_last_hour: 4205
  });

  const [regionalPerformance] = useState([
    { id: 'US-EAST', name: 'US East (VA)', p50: 18, load: 'LOW', status: 'OPTIMAL' },
    { id: 'US-WEST', name: 'US West (OR)', p50: 84, load: 'NORMAL', status: 'STABLE' },
    { id: 'EU-LONDON', name: 'Europe (UK)', p50: 142, load: 'NORMAL', status: 'STABLE' },
    { id: 'ASIA-SG', name: 'Asia (SG)', p50: 1240, load: 'CRITICAL', status: 'SURGE_ACTIVE' }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30">
      
      {/* Background Decorative Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
              <Gauge className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Performance Profiler</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Systemic Throughput // Sync Tick: <span className="text-indigo-400">{lastTick.toLocaleTimeString()}</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Active Multiplier</span>
                   <span className="text-xl font-black text-amber-500 tracking-tighter">{vitals.congestion_multiplier}x</span>
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

        {/* Primary Latency Percentiles */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
           {[
             { label: 'System TPS', val: vitals.tps, sub: 'TRANS/SEC', icon: Zap, color: 'indigo' },
             { label: 'P50 Latency', val: `${vitals.p50_ms}ms`, sub: 'MEDIAN', icon: Clock, color: 'green' },
             { label: 'P90 Latency', val: `${vitals.p90_ms}ms`, sub: 'HIGH', icon: Activity, color: 'yellow' },
             { label: 'P99 Latency', val: `${vitals.p99_ms}ms`, sub: 'CRITICAL', icon: AlertTriangle, color: 'red' }
           ].map((metric, i) => (
             <div key={i} className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform">
                  <metric.icon className={`w-20 h-20 text-${metric.color}-500`} />
                </div>
                <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">{metric.label}</span>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-black text-white tracking-tighter">{metric.val}</span>
                  <span className="text-[10px] font-bold text-gray-700 uppercase">{metric.sub}</span>
                </div>
                <div className="mt-4 w-full bg-white/5 h-0.5 rounded-full overflow-hidden">
                   <div className={`h-full bg-${metric.color}-500 opacity-60`} style={{ width: i === 0 ? '70%' : i === 1 ? '40%' : i === 2 ? '75%' : '92%' }} />
                </div>
             </div>
           ))}
        </div>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Main Chart: Throughput vs Latency Correlation */}
          <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative overflow-hidden h-[450px]">
             <div className="flex justify-between items-center mb-10">
                <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                  <TrendingUp className="w-4 h-4 text-indigo-500" /> Throughput Sensitivity (TPS)
                </h3>
                <div className="flex items-center gap-6">
                   <span className="flex items-center gap-2 text-[9px] text-indigo-400 font-bold uppercase tracking-tighter">
                      <div className="w-2 h-2 rounded-full bg-indigo-500" /> System Velocity
                   </span>
                   <div className="h-4 w-px bg-white/10" />
                   <span className="text-[10px] text-gray-600 font-bold">Samples: {vitals.samples_last_hour}</span>
                </div>
             </div>

             {/* Bar Graph Simulation */}
             <div className="h-56 flex items-end gap-1.5 px-4 relative">
                <div className="absolute top-0 w-full h-px border-t border-dashed border-white/5" />
                {[...Array(50)].map((_, i) => {
                  const h = 20 + Math.random() * 60;
                  return (
                    <div 
                      key={i} 
                      className={`flex-1 ${h > 70 ? 'bg-red-500/20' : 'bg-indigo-500/20'} rounded-t-sm group relative`} 
                      style={{ height: `${h}%` }}
                    >
                       <div className="absolute inset-x-0 -top-6 text-[8px] font-black text-white opacity-0 group-hover:opacity-100 transition-opacity text-center uppercase tracking-tighter">
                         {Math.floor(h/10)} TPS
                       </div>
                    </div>
                  );
                })}
             </div>
             
             <div className="flex justify-between mt-6 text-[9px] font-black uppercase text-gray-700 tracking-widest border-t border-white/5 pt-4">
                <span>Start Epoch</span>
                <span>Active Mempool Saturation</span>
                <span>Current Real-time Tick</span>
             </div>
          </div>

          {/* Regional Latency Heatmap Sidebar */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl flex flex-col">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3">
                     <Globe className="w-4 h-4 text-blue-500" /> Regional Latency
                   </h3>
                   <span className="text-[9px] text-gray-600 font-black uppercase tracking-widest">v1.0.8</span>
                </div>
                
                <div className="divide-y divide-white/5">
                   {regionalPerformance.map((region) => (
                      <div key={region.id} className="p-6 hover:bg-white/[0.01] transition-all group">
                         <div className="flex justify-between items-center mb-3">
                            <div>
                               <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-blue-400 transition-colors">{region.name}</span>
                               <span className={`text-[9px] font-black block mt-0.5 ${region.status === 'SURGE_ACTIVE' ? 'text-red-500' : 'text-gray-700'}`}>
                                 {region.status}
                               </span>
                            </div>
                            <div className="text-right">
                               <span className={`text-sm font-black ${region.p50 > 1000 ? 'text-red-400' : 'text-green-500'}`}>{region.p50}ms</span>
                               <span className="text-[8px] text-gray-700 font-bold block uppercase">RTT P50</span>
                            </div>
                         </div>
                         <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                            <div className={`h-full ${region.p50 > 1000 ? 'bg-red-500' : 'bg-indigo-500'} opacity-60`} style={{ width: region.p50 > 1000 ? '90%' : '30%' }} />
                         </div>
                      </div>
                   ))}
                </div>
                
                <button className="w-full py-4 text-[9px] font-black text-gray-600 hover:text-white uppercase tracking-[0.3em] border-t border-white/5 bg-white/[0.01] transition-all">
                   View Advanced Routing Map &rarr;
                </button>
             </div>

             <div className="p-8 border border-white/10 bg-[#0a0a0a] rounded-xl shadow-2xl relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-[0.02] group-hover:scale-110 transition-transform">
                   <Target className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5 text-indigo-500" /> Pricing Feedback
                </h4>
                <p className="text-xs text-gray-500 leading-relaxed mb-6 italic">
                   "The market ticker congestion multiplier is currently driven by the P50 latency drift. Systemic drift beyond 500ms activates progressive surge scaling."
                </p>
                <div className="flex justify-between items-center text-[9px] font-black uppercase text-gray-600 border-t border-white/5 pt-4">
                   <span>Drift Index</span>
                   <span className="text-indigo-400">NOMINAL</span>
                </div>
             </div>
          </div>

        </div>

        {/* Diagnostic Footer Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
           <div className="p-6 border border-white/5 bg-indigo-500/5 rounded-xl flex items-center gap-6">
              <div className="p-3 bg-indigo-500/10 rounded-lg"><Cpu className="w-6 h-6 text-indigo-500" /></div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Compute Load</p>
                 <p className="text-xl font-black text-white tracking-tighter">14% <span className="text-[10px] text-indigo-400 font-bold">AVG_IDLE</span></p>
              </div>
           </div>
           <div className="p-6 border border-white/5 bg-emerald-500/5 rounded-xl flex items-center gap-6">
              <div className="p-3 bg-emerald-500/10 rounded-lg"><ShieldCheck className="w-6 h-6 text-emerald-500" /></div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Execution Integrity</p>
                 <p className="text-xl font-black text-white tracking-tighter">100% <span className="text-[10px] text-emerald-400 font-bold">VALIDATED</span></p>
              </div>
           </div>
           <div className="p-6 border border-white/5 bg-blue-500/5 rounded-xl flex items-center gap-6">
              <div className="p-3 bg-blue-500/10 rounded-lg"><Binary className="w-6 h-6 text-blue-500" /></div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Network Backbone</p>
                 <p className="text-xl font-black text-white tracking-tighter">LNV2 <span className="text-[10px] text-blue-400 font-bold">ACTIVE</span></p>
              </div>
           </div>
        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Telemetry Orchestrator v1.0 Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Monitoring 1,248 Node Heartbeats</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] TPS_CAPACITY: 10k</span>
            <span>[*] LATENCY_OPTIMIZED: TRUE</span>
            <span>[*] VERSION: v2.9.4</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
