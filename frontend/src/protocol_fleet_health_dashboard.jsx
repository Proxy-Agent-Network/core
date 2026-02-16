import React, { useState, useEffect } from 'react';
import { 
  HeartPulse, 
  RotateCcw, 
  ShieldAlert, 
  TrendingUp, 
  BarChart3, 
  Clock, 
  Cpu, 
  RefreshCw, 
  Activity, 
  Lock, 
  Zap, 
  Info,
  ChevronRight,
  HardDrive,
  History,
  AlertTriangle,
  ArrowUpRight,
  ShieldCheck,
  XCircle,
  Binary,
  Layers,
  Thermometer
} from 'lucide-react';

/**
 * PROXY PROTOCOL - FLEET HEALTH DASHBOARD (v1.0)
 * "Visualizing cryptographic aging and hardware rotation."
 * ----------------------------------------------------
 */

const App = () => {
  const [lastSync, setLastSync] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [filter, setFilter] = useState('ALL');

  // Mock Fleet Lifecycle State
  const [fleetStats] = useState({
    avg_seed_age: 142, // Days
    rotation_required: 12,
    hardware_velocity: "4.2 units/epoch",
    fleet_integrity: 98.4
  });

  // Mock Node Distribution by Age (Histogram Data)
  const ageDistribution = [
    { label: '0-30d', count: 142, color: 'bg-emerald-500' },
    { label: '31-90d', count: 310, color: 'bg-green-500' },
    { label: '91-180d', count: 450, color: 'bg-yellow-500' },
    { label: '181-365d', count: 280, color: 'bg-orange-500' },
    { label: '365d+', count: 66, color: 'bg-red-500' }
  ];

  // Critical Alerts for Rotation
  const [alerts] = useState([
    { id: "SENTRY-VA-042", task_count: 9840, limit: 10000, age: "180d", status: "CRITICAL" },
    { id: "SENTRY-JP-001", task_count: 9200, limit: 10000, age: "165d", status: "WARNING" },
    { id: "SENTRY-EU-991", task_count: 8900, limit: 10000, age: "190d", status: "WARNING" }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setLastSync(new Date());
      setIsRefreshing(false);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header: Tech-Ops Command */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
              <HeartPulse className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Fleet Health</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2 font-mono">
                Hardware Lifecycle Management // Protocol <span className="text-indigo-400">v3.3.0</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Rotation Queue</span>
                   <span className="text-xl font-black text-white tracking-tighter">{fleetStats.rotation_required} <span className="text-[10px] text-red-500 font-bold">UNITS</span></span>
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

        {/* Primary Health KPI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
           {[
             { label: 'Avg Seed Age', val: `${fleetStats.avg_seed_age}d`, sub: 'EPOCH_MEAN', icon: Clock, color: 'indigo' },
             { label: 'Fleet Integrity', val: `${fleetStats.fleet_integrity}%`, sub: 'STABLE_PCR', icon: ShieldCheck, color: 'green' },
             { label: 'Hardware Velocity', val: '4.2', sub: 'NEW_UNITS/EPOCH', icon: TrendingUp, color: 'blue' },
             { label: 'Silicon Entropy', val: '92.1%', sub: 'NOMINAL', icon: Binary, color: 'emerald' }
           ].map((kpi, i) => (
             <div key={i} className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform">
                  <kpi.icon className="w-20 h-20 text-white" />
                </div>
                <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">{kpi.label}</span>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-black text-white tracking-tighter">{kpi.val}</span>
                  <span className={`text-[9px] font-black uppercase text-${kpi.color}-500 ml-2 tracking-tighter`}>{kpi.sub}</span>
                </div>
             </div>
           ))}
        </div>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Age Distribution Histogram */}
          <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl overflow-hidden relative h-[450px]">
             <div className="flex justify-between items-center mb-12">
                <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                  <BarChart3 className="w-4 h-4 text-indigo-500" /> Fleet Seed-Age Distribution
                </h3>
                <span className="text-[10px] text-gray-600 font-bold uppercase">Target Rotation: 180 Days</span>
             </div>

             <div className="h-56 flex items-end gap-12 justify-center px-12 relative">
                <div className="absolute top-1/2 w-full h-px border-t border-dashed border-white/5" />
                {ageDistribution.map((tier, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center gap-6">
                     <div className="w-full relative flex flex-col justify-end h-40">
                        <div 
                          className={`w-full ${tier.color} opacity-20 rounded-t-lg transition-all duration-1000 group cursor-default relative`} 
                          style={{ height: `${(tier.count / 450) * 100}%` }}
                        >
                           <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                           <div className="absolute -top-8 left-1/2 -translate-x-1/2 text-white font-black text-xs opacity-0 group-hover:opacity-100 transition-opacity">{tier.count}</div>
                        </div>
                        <div className={`absolute bottom-0 w-full ${tier.color} h-1 rounded-full`} />
                     </div>
                     <span className="text-[10px] font-black text-gray-600 uppercase tracking-widest">{tier.label}</span>
                  </div>
                ))}
             </div>

             <div className="mt-12 flex justify-center gap-12">
                <div className="flex items-center gap-3">
                   <div className="w-2 h-2 bg-emerald-500 rounded-full" />
                   <span className="text-[9px] text-gray-700 font-black uppercase tracking-widest">Fresh Seeds</span>
                </div>
                <div className="flex items-center gap-3">
                   <div className="w-2 h-2 bg-orange-500 rounded-full" />
                   <span className="text-[9px] text-gray-700 font-black uppercase tracking-widest">Aged Hardware</span>
                </div>
                <div className="flex items-center gap-3">
                   <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                   <span className="text-[9px] text-gray-700 font-black uppercase tracking-widest">Depleted Entropy</span>
                </div>
             </div>
          </div>

          {/* Critical Rotation Feed */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl flex-1 flex flex-col">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <RotateCcw className="w-4 h-4 text-red-500" /> Pending Rotations
                   </h3>
                   <span className="text-[9px] text-gray-700 font-bold uppercase tracking-widest">Strict 10k Limit</span>
                </div>

                <div className="divide-y divide-white/5">
                   {alerts.map((node) => (
                      <div key={node.id} className="p-6 hover:bg-red-500/[0.02] transition-all group cursor-pointer">
                         <div className="flex justify-between items-start mb-3">
                            <div>
                               <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-red-400 transition-colors">{node.id}</span>
                               <p className="text-[9px] text-gray-600 font-bold uppercase mt-1">Age: {node.age}</p>
                            </div>
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${node.status === 'CRITICAL' ? 'bg-red-500/10 border-red-500/20 text-red-500' : 'bg-amber-500/10 border-amber-500/20 text-amber-500'}`}>
                               {node.status}
                            </span>
                         </div>
                         <div className="space-y-2">
                            <div className="flex justify-between text-[8px] font-black uppercase text-gray-700">
                               <span>Task Utilization</span>
                               <span className="text-white">{node.task_count.toLocaleString()} / {node.limit.toLocaleString()}</span>
                            </div>
                            <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                               <div className={`h-full ${node.status === 'CRITICAL' ? 'bg-red-500 animate-pulse' : 'bg-amber-500'}`} style={{ width: `${(node.task_count / node.limit) * 100}%` }} />
                            </div>
                         </div>
                         <button className="w-full mt-4 py-2 border border-white/5 text-[9px] font-black text-gray-700 group-hover:text-white group-hover:border-white/10 transition-all uppercase tracking-widest">
                            Authorize Seed Rotation &rarr;
                         </button>
                      </div>
                   ))}
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-[#0a0a0a] rounded-xl shadow-inner relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-[0.02] group-hover:scale-110 transition-transform duration-1000">
                   <Lock className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5 text-indigo-500" /> Security Rationale
                </h4>
                <p className="text-xs text-gray-500 leading-relaxed italic">
                   "Cryptographic wear occurs when a single hardware seed generates an excessive number of signatures. We mandate rotation every 10k tasks to prevent potential differential attacks on the silicon substrate."
                </p>
             </div>
          </div>

        </div>

        {/* Lower Vitals Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
           <div className="p-6 border border-white/5 bg-indigo-500/5 rounded-xl flex items-center gap-6 group hover:border-indigo-500/30 transition-all">
              <div className="p-3 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500 group-hover:text-black transition-all">
                <Cpu className="w-6 h-6" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Firmware Standard</p>
                 <p className="text-xl font-black text-white tracking-tighter">v2.8.1 <span className="text-[9px] text-indigo-400 font-bold tracking-widest ml-2">COMPLIANT</span></p>
              </div>
           </div>
           <div className="p-6 border border-white/5 bg-red-500/5 rounded-xl flex items-center gap-6 group hover:border-red-500/30 transition-all">
              <div className="p-3 bg-red-500/10 rounded-lg group-hover:bg-red-500 group-hover:text-black transition-all">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">EOL Hardware</p>
                 <p className="text-xl font-black text-white tracking-tighter">03 <span className="text-[9px] text-red-500 font-bold tracking-widest ml-2">RECOUP_REQ</span></p>
              </div>
           </div>
           <div className="p-6 border border-white/5 bg-emerald-500/5 rounded-xl flex items-center gap-6 group hover:border-emerald-500/30 transition-all">
              <div className="p-3 bg-emerald-500/10 rounded-lg group-hover:bg-emerald-500 group-hover:text-black transition-all">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                 <p className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Rotation Velocity</p>
                 <p className="text-xl font-black text-white tracking-tighter">1.2d <span className="text-[9px] text-emerald-400 font-bold tracking-widest ml-2">AVG_TT_ROT</span></p>
              </div>
           </div>
        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Lifecycle Watch Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Hardware is a lease on reputation; silicon is eventually exhausted."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] SEED_MAX_TASK: 10,000</span>
            <span>[*] RECOVERY_PROTOCOL: v1.2</span>
            <span>[*] VERSION: v3.3.0</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
