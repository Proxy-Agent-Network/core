import React, { useState, useEffect, useMemo } from 'react';
import { 
  ShieldCheck, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Activity, 
  DollarSign, 
  Clock, 
  RefreshCw, 
  BarChart3, 
  Zap, 
  Info,
  ChevronRight,
  ArrowRight,
  Calculator,
  Percent,
  History,
  ShieldAlert,
  Coins
} from 'lucide-react';

/**
 * PROXY PROTOCOL - SOLVENCY DASHBOARD (v1.0)
 * "Visualizing systemic liquidity and default probability."
 * ----------------------------------------------------
 */

const App = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [stressScenario, setStressScenario] = useState('NORMAL'); // NORMAL, VOLATILE, SYBIL_ATTACK

  // Mock Actuarial Data
  const [actuary] = useState({
    pool_balance: 10450200,
    solvency_target: 100000000,
    base_levy: 0.001,
    current_levy: 0.0014,
    default_probability: 0.124,
    time_to_insolvency: "> 365 Days",
    flow_velocity: 850 // Sats/sec
  });

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1200);
  };

  const getRiskColor = (prob) => {
    if (prob < 0.1) return 'text-green-500';
    if (prob < 0.3) return 'text-blue-400';
    if (prob < 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-blue-500/30">
      
      {/* Background Grid Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div>
            <div className="flex items-center gap-4 mb-3">
              <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl shadow-2xl">
                <ShieldCheck className="w-8 h-8 text-blue-500 animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Solvency Monitor</h1>
                <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold font-mono">Actuarial Analytics // Protocol v2.8.6</p>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Active Levy</span>
                   <span className="text-xl font-black text-white tracking-tighter">{(actuary.current_levy * 100).toFixed(4)}%</span>
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

        {/* Primary Actuarial Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl group">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Default Probability</span>
              <div className="flex items-baseline gap-2">
                 <span className={`text-3xl font-black tracking-tighter ${getRiskColor(actuary.default_probability)}`}>
                   {(actuary.default_probability * 100).toFixed(2)}%
                 </span>
                 <Activity className="w-4 h-4 opacity-30" />
              </div>
              <div className="mt-4 w-full bg-white/5 h-1 rounded-full overflow-hidden">
                 <div className={`h-full ${getRiskColor(actuary.default_probability).replace('text', 'bg')}`} style={{ width: `${actuary.default_probability * 100}%` }} />
              </div>
           </div>

           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Solvency Clock</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-3xl font-black text-white tracking-tighter">{actuary.time_to_insolvency}</span>
                 <Clock className="w-4 h-4 text-gray-700" />
              </div>
              <p className="text-[9px] text-gray-700 mt-2 font-black uppercase tracking-tighter">Est. under {stressScenario} flow</p>
           </div>

           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Flow Velocity</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-3xl font-black text-indigo-400 tracking-tighter">{actuary.flow_velocity}</span>
                 <span className="text-[10px] text-gray-500 font-bold uppercase tracking-tighter">Sats/Sec</span>
              </div>
              <p className="text-[9px] text-green-500 mt-2 font-black uppercase tracking-tighter flex items-center gap-1">
                 <TrendingUp className="w-3 h-3" /> +14.2% Peak Shift
              </p>
           </div>

           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Pool Depth</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-3xl font-black text-white tracking-tighter">{(actuary.pool_balance / 1000000).toFixed(2)}M</span>
                 <span className="text-[10px] text-gray-500 font-bold uppercase tracking-tighter">SATS</span>
              </div>
              <div className="mt-4 flex justify-between items-center text-[9px] font-black uppercase text-gray-700">
                 <span>Solvency Target</span>
                 <span className="text-blue-500">1.0 BTC</span>
              </div>
           </div>
        </div>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Main Visual: Risk Sensitivity Curve */}
          <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl overflow-hidden relative">
             <div className="flex justify-between items-center mb-10">
                <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                  <Calculator className="w-4 h-4 text-blue-500" /> Default Sensitivity Projection
                </h3>
                <div className="flex gap-4">
                   <div className="flex bg-white/5 p-1 rounded border border-white/10">
                      {['NORMAL', 'VOLATILE', 'SYBIL_ATTACK'].map(s => (
                        <button 
                          key={s}
                          onClick={() => setStressScenario(s)}
                          className={`px-3 py-1 text-[9px] font-black rounded transition-all ${stressScenario === s ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/20' : 'text-gray-500 hover:text-white'}`}
                        >
                          {s}
                        </button>
                      ))}
                   </div>
                </div>
             </div>

             <div className="h-72 flex items-end gap-1 px-4 relative">
                <div className="absolute top-0 left-0 text-[8px] font-black text-red-500/40 uppercase tracking-widest">Insolvency Threshold</div>
                <div className="absolute top-0 w-full h-px bg-red-500/10 border-t border-dashed border-red-500/30" />
                
                {/* Mock Curve Bars */}
                {[...Array(50)].map((_, i) => {
                  const x = i / 50;
                  // Simulated exponential risk curve based on stress scenario
                  const multiplier = stressScenario === 'SYBIL_ATTACK' ? 2.5 : stressScenario === 'VOLATILE' ? 1.5 : 1.0;
                  const h = Math.min(100, (Math.pow(x, 2) * 100) * multiplier + (Math.random() * 5));
                  
                  return (
                    <div 
                      key={i} 
                      className={`flex-1 ${h > 80 ? 'bg-red-500/30' : h > 40 ? 'bg-blue-500/20' : 'bg-green-500/10'} rounded-t-sm group relative`} 
                      style={{ height: `${h}%` }}
                    >
                       <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  );
                })}
             </div>
             
             <div className="flex justify-between mt-6 text-[9px] font-black uppercase text-gray-700 tracking-widest border-t border-white/5 pt-4">
                <span>Baseline Flow</span>
                <span>Peak Mempool Saturation</span>
                <span>Max Capacity (Theoretical)</span>
             </div>
          </div>

          {/* Sidebar: Dynamic Adjustment Logic */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
                <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                  <Percent className="w-4 h-4 text-blue-500" /> Active Tax Controller
                </h3>
                <div className="space-y-6">
                   <div className="p-4 bg-white/5 border border-white/5 rounded-lg flex justify-between items-center">
                      <div>
                         <span className="text-[9px] text-gray-500 uppercase font-black block mb-1">Standard Levy</span>
                         <span className="text-lg font-black text-white">0.1000%</span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-700" />
                   </div>
                   <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg flex justify-between items-center">
                      <div>
                         <span className="text-[9px] text-blue-400 uppercase font-black block mb-1">Dynamic Surcharge</span>
                         <span className="text-lg font-black text-white">+0.0422%</span>
                      </div>
                      <Zap className="w-5 h-5 text-blue-500" />
                   </div>
                   
                   <p className="text-[10px] text-gray-600 leading-relaxed italic border-t border-white/5 pt-6">
                     "The Actuary Engine has increased the levy to 0.14% due to a 12% spike in Asia-SE failure rates. This secures an additional 42k SATS/hour for the pool."
                   </p>
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-black/40 rounded-xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:scale-110 transition-transform">
                   <ShieldAlert className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5 text-blue-500" /> Solvency Logic
                </h4>
                <p className="text-xs text-gray-500 leading-relaxed mb-6">
                   The target pool depth is 1.0 BTC. If the balance falls below 5M SATS, the levy automatically hits the 0.5% cap to prevent structural insolvency.
                </p>
                <div className="flex justify-between items-center text-[9px] font-black uppercase text-gray-600 border-t border-white/5 pt-4">
                   <span>Auto-Equilibrium</span>
                   <span className="text-green-500">OPTIMIZED</span>
                </div>
             </div>

             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden flex flex-col">
                <div className="p-4 bg-white/[0.02] border-b border-white/5">
                   <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Recent Claim Events</h3>
                </div>
                <div className="p-4 space-y-3 font-mono text-[9px]">
                   <div className="flex gap-3 text-gray-600">
                      <span className="text-blue-500">21:04</span> 
                      <span className="text-white font-bold uppercase">Tax_Collection</span> 
                      <span className="ml-auto">+842 S</span>
                   </div>
                   <div className="flex gap-3 text-gray-600">
                      <span className="text-blue-500">20:12</span> 
                      <span className="text-red-500 font-bold uppercase">Insurance_Payout</span> 
                      <span className="ml-auto">-12.5k S</span>
                   </div>
                   <div className="flex gap-3 text-gray-600">
                      <span className="text-blue-500">18:45</span> 
                      <span className="text-white font-bold uppercase">Tax_Collection</span> 
                      <span className="ml-auto">+412 S</span>
                   </div>
                </div>
             </div>
          </div>

        </div>

      </main>

      {/* Global Treasury Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <Coins className="w-3 h-3 text-amber-500 animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Treasury Guard Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Pool Health: {(actuary.pool_balance / actuary.solvency_target * 100).toFixed(1)}% Capacity</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] LIQUIDITY_VAL: 71.8M SATS</span>
            <span>[*] RISK_INDEX: LOW</span>
            <span>[*] VERSION: v2.8.6</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
