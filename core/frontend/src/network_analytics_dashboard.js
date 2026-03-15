import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, TrendingDown, Activity, DollarSign, 
  Users, BarChart3, PieChart, ArrowUpRight, 
  ArrowDownRight, Globe, Shield, Zap, RefreshCw, 
  Download, Filter, Calendar, Search
} from 'lucide-react';

const App = () => {
  const [timeframe, setTimeframe] = useState('24H');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock Global Economic Data
  const [metrics] = useState({
    total_volume_sats: 124508900,
    active_escrows_sats: 4200500,
    insurance_pool_sats: 10450200,
    avg_reputation: 942.5,
    successful_payouts: 18422,
    slashed_bonds: 142
  });

  const [topNodes] = useState([
    { id: "NODE_ELITE_X29", region: "US_EAST", earnings: 450200, rep: 982, status: "STABLE" },
    { id: "NODE_ALPHA_001", region: "EU_WEST", earnings: 380150, rep: 965, status: "STABLE" },
    { id: "NODE_GAMMA_992", region: "ASIA_SE", earnings: 310800, rep: 958, status: "STABLE" },
    { id: "NODE_WHALE_04", region: "US_WEST", earnings: 290400, rep: 991, status: "STABLE" }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1500);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-6 selection:bg-indigo-500/30">
      
      {/* Header */}
      <header className="flex justify-between items-end mb-8 border-b border-white/10 pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-1.5 bg-indigo-500/10 border border-indigo-500/20 rounded">
              <BarChart3 className="w-5 h-5 text-indigo-500" />
            </div>
            <h1 className="text-xl font-black text-white tracking-tighter uppercase">Protocol Analytics</h1>
          </div>
          <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500">Internal Observability // High-Fidelity Data Stream</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex bg-white/5 p-1 rounded border border-white/10">
            {['24H', '7D', '30D', 'ALL'].map((t) => (
              <button 
                key={t}
                onClick={() => setTimeframe(t)}
                className={`px-3 py-1 text-[9px] font-black rounded transition-all ${timeframe === t ? 'bg-indigo-500 text-white' : 'text-gray-500 hover:text-gray-300'}`}
              >
                {t}
              </button>
            ))}
          </div>
          <button 
            onClick={handleRefresh}
            className={`p-2 border border-white/10 rounded hover:bg-white/5 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
          >
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </header>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[
          { label: 'Total Task Volume', val: `${(metrics.total_volume_sats / 1000000).toFixed(1)}M`, sub: 'SATS', icon: Zap, color: 'indigo' },
          { label: 'Network Liquidity', val: `${(metrics.active_escrows_sats / 1000000).toFixed(2)}M`, sub: 'LOCKED', icon: Shield, color: 'green' },
          { label: 'Global Health', val: metrics.avg_reputation, sub: 'AVG REP', icon: Activity, color: 'blue' },
          { label: 'Settlement Ratio', val: '99.2%', sub: 'SUCCESS', icon: Globe, color: 'emerald' }
        ].map((kpi, i) => (
          <div key={i} className="bg-[#0a0a0a] border border-white/5 p-6 rounded-lg shadow-xl relative overflow-hidden group">
            <div className={`absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity`}>
              <kpi.icon className={`w-12 h-12 text-${kpi.color}-500`} />
            </div>
            <span className="text-[10px] text-gray-500 uppercase font-black tracking-widest block mb-2">{kpi.label}</span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black text-white tracking-tighter">{kpi.val}</span>
              <span className="text-[10px] font-bold text-gray-600">{kpi.sub}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-12 gap-6">
        
        {/* Satoshi Flow Visualizer */}
        <div className="col-span-12 lg:col-span-8 space-y-6">
          <div className="bg-[#0a0a0a] border border-white/5 rounded-lg p-8 shadow-2xl">
            <div className="flex justify-between items-center mb-10">
              <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                <TrendingUp className="w-4 h-4 text-indigo-500" /> Satoshi Flow Velocity
              </h3>
              <div className="flex gap-4 text-[9px] font-bold">
                <span className="flex items-center gap-2 text-indigo-400"><div className="w-2 h-2 rounded-full bg-indigo-500" /> INFLOW</span>
                <span className="flex items-center gap-2 text-emerald-400"><div className="w-2 h-2 rounded-full bg-emerald-500" /> PAYOUTS</span>
              </div>
            </div>
            
            {/* Mock Chart Area */}
            <div className="h-64 flex items-end gap-1 px-2 relative">
              {[...Array(40)].map((_, i) => {
                const h1 = 20 + Math.random() * 60;
                const h2 = h1 * (0.7 + Math.random() * 0.2);
                return (
                  <div key={i} className="flex-1 flex flex-col justify-end gap-0.5 group cursor-crosshair">
                    <div className="w-full bg-emerald-500/20 border-t border-emerald-500/40" style={{ height: `${h2}%` }} />
                    <div className="w-full bg-indigo-500/20 border-t border-indigo-500/40" style={{ height: `${h1}%` }} />
                    <div className="hidden group-hover:block absolute -top-12 left-1/2 -translate-x-1/2 bg-black border border-white/10 p-2 rounded text-[8px] z-10 whitespace-nowrap shadow-2xl">
                      EPOCH {8820 + i}<br/>IN: +4.2M SATS<br/>OUT: -3.8M SATS
                    </div>
                  </div>
                );
              })}
              <div className="absolute inset-x-0 bottom-0 h-px bg-white/10" />
            </div>
            <div className="flex justify-between mt-4 text-[9px] text-gray-600 uppercase font-black">
              <span>{timeframe === '24H' ? '00:00' : '01 FEB'}</span>
              <span>{timeframe === '24H' ? '12:00' : '15 FEB'}</span>
              <span>{timeframe === '24H' ? '23:59' : 'NOW'}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Reputation Drift Analytics */}
            <div className="bg-[#0a0a0a] border border-white/5 rounded-lg p-6">
              <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6">Reputation Stability</h3>
              <div className="space-y-4">
                {[
                  { label: 'Tier 1 (Digital)', stability: 98.2, drift: '+0.4%' },
                  { label: 'Tier 2 (Physical)', stability: 94.5, drift: '-1.2%' },
                  { label: 'Tier 3 (Legal)', stability: 99.8, drift: '+0.1%' }
                ].map((tier, i) => (
                  <div key={i} className="flex flex-col gap-2">
                    <div className="flex justify-between text-[10px] font-bold">
                      <span className="text-gray-500 uppercase">{tier.label}</span>
                      <span className={tier.drift.startsWith('+') ? 'text-green-500' : 'text-red-500'}>{tier.drift}</span>
                    </div>
                    <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                      <div className="bg-indigo-500 h-full" style={{ width: `${tier.stability}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Network Liquidity Health */}
            <div className="bg-[#0a0a0a] border border-white/5 rounded-lg p-6 flex flex-col justify-between">
              <h3 className="text-xs font-black text-white uppercase tracking-widest mb-4">Liquidity Distribution</h3>
              <div className="flex-1 flex items-center justify-center">
                <PieChart className="w-24 h-24 text-indigo-500/20" />
              </div>
              <div className="space-y-2 mt-4">
                <div className="flex justify-between text-[10px] font-bold">
                  <span className="text-gray-500 uppercase">HODL Escrows</span>
                  <span className="text-white">62%</span>
                </div>
                <div className="flex justify-between text-[10px] font-bold">
                  <span className="text-gray-500 uppercase">Insurance Reserve</span>
                  <span className="text-white">28%</span>
                </div>
                <div className="flex justify-between text-[10px] font-bold">
                  <span className="text-gray-500 uppercase">Treasury Surplus</span>
                  <span className="text-white">10%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar: Top Performing Human Nodes */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
          <div className="bg-[#0a0a0a] border border-white/5 rounded-lg overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-white/10 bg-white/[0.02]">
              <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-2">
                <Users className="w-4 h-4 text-indigo-500" /> Elite Node Leaderboard
              </h3>
            </div>
            <div className="divide-y divide-white/5">
              {topNodes.map((node) => (
                <div key={node.id} className="p-4 hover:bg-white/[0.01] transition-colors group">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex flex-col">
                      <span className="text-[11px] font-black text-white group-hover:text-indigo-400 transition-colors">{node.id}</span>
                      <span className="text-[9px] text-gray-600 uppercase font-bold">{node.region}</span>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className="text-[11px] font-black text-indigo-500">{node.earnings.toLocaleString()} SATS</span>
                      <span className="text-[9px] text-gray-600 font-bold">LIFETIME</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-3">
                    <div className="flex-1 bg-white/5 h-1 rounded-full overflow-hidden">
                      <div className="bg-indigo-500 h-full opacity-60" style={{ width: `${(node.rep / 1000) * 100}%` }} />
                    </div>
                    <span className="text-[9px] font-bold text-gray-500">{node.rep}/1k</span>
                  </div>
                </div>
              ))}
            </div>
            <button className="w-full py-3 text-[10px] font-black text-gray-500 hover:text-white uppercase tracking-widest transition-all">
              View All 1,248 Nodes &rarr;
            </button>
          </div>

          <div className="p-6 bg-indigo-500/5 border border-indigo-500/10 rounded-lg shadow-inner">
            <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-3 flex items-center gap-2">
              <Shield className="w-3.5 h-3.5" /> Security Advisory
            </h4>
            <p className="text-[11px] text-gray-500 leading-relaxed italic">
              "Node slashing events in the ASIA_SE region have spiked by 14% over the last 48h. Investigating potential Sybil cluster targeting Tier 1 SMS tasks."
            </p>
          </div>

          <div className="bg-void border border-white/5 p-4 rounded-lg flex items-center justify-between shadow-xl">
             <div className="flex flex-col">
                <span className="text-[9px] text-gray-600 uppercase font-black">Export Dataset</span>
                <span className="text-[10px] text-gray-400">EPOCH_DATA_2026_02.CSV</span>
             </div>
             <button className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded hover:bg-indigo-500/20 transition-all">
                <Download className="w-4 h-4 text-indigo-400" />
             </button>
          </div>
        </div>

      </div>

      {/* Global Event Feed (Footer) */}
      <div className="mt-8 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 font-mono text-[9px] text-gray-600">
        <div className="flex gap-4">
          <span className="text-indigo-500 font-bold uppercase">[SYSTEM_MONITOR]</span>
          <span className="animate-pulse">[*] BROADCAST: PI_PROPOSAL_882 MOVED TO PHASE 03 VOTING...</span>
          <span className="ml-auto text-gray-800">Uptime: 142d 12h 04m</span>
        </div>
      </div>

    </div>
  );
};

export default App;
