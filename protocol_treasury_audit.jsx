import React, { useState, useMemo } from 'react';
import { 
  PieChart, 
  BarChart3, 
  ArrowUpRight, 
  ArrowDownRight, 
  ShieldCheck, 
  Zap, 
  Heart, 
  Hammer, 
  Clock, 
  Lock, 
  Globe, 
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Database,
  Search,
  Wallet,
  Coins,
  History,
  Info
} from 'lucide-react';

/**
 * PROXY PROTOCOL - TREASURY AUDIT DASHBOARD (v1.0)
 * "Economic transparency for the autonomous economy."
 * ----------------------------------------------------
 */

const App = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [filter, setFilter] = useState('ALL');

  // Mock Global Treasury Stats
  const stats = {
    total_reserves: 71790100, // 0.71 BTC
    total_inflow_24h: 425000,
    total_outflow_24h: 112000,
    active_escrows: 4200500,
    insurance_pool: 10450200,
    dev_grants_pool: 5000000,
    burn_count: 8829310
  };

  const allocation = [
    { label: "Insurance Pool", value: 35, color: "bg-blue-500", icon: ShieldCheck },
    { label: "Infrastructure", value: 30, color: "bg-indigo-500", icon: Database },
    { label: "Dev Grants", value: 20, color: "bg-emerald-500", icon: Hammer },
    { label: "Satoshi Burn", value: 15, color: "bg-red-500", icon: Zap }
  ];

  const ledger = [
    { id: "TX-99812", type: "INFLOW", category: "PROTOCOL_FEE", amount: 250000, timestamp: "12m ago", status: "CONFIRMED" },
    { id: "TX-99804", type: "OUTFLOW", category: "NODE_INSURANCE", amount: 50000, timestamp: "2h ago", status: "CONFIRMED" },
    { id: "TX-99791", type: "INFLOW", category: "PROXY_PASS", amount: 1000000, timestamp: "5h ago", status: "CONFIRMED" },
    { id: "TX-99782", type: "OUTFLOW", category: "DEV_GRANT", amount: 250000, timestamp: "8h ago", status: "SETTLED" },
    { id: "TX-99770", type: "INFLOW", category: "TASK_FEE", amount: 4200, timestamp: "10h ago", status: "CONFIRMED" }
  ];

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1200);
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
                <Coins className="w-8 h-8 text-indigo-500 animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Protocol Treasury</h1>
                <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold">Public Audit // Real-Time Satoshi Velocity</p>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Net Reserves</span>
                   <span className="text-xl font-black text-white tracking-tighter">{(stats.total_reserves / 1000000).toFixed(1)}M <span className="text-[10px] text-gray-500">SATS</span></span>
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

        {/* Primary Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">24h Inflow</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-2xl font-black text-green-500">+{stats.total_inflow_24h.toLocaleString()}</span>
                 <ArrowUpRight className="w-3 h-3 text-green-500/50" />
              </div>
           </div>
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">24h Outflow</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-2xl font-black text-red-400">-{stats.total_outflow_24h.toLocaleString()}</span>
                 <ArrowDownRight className="w-3 h-3 text-red-400/50" />
              </div>
           </div>
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Insurance Depth</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-2xl font-black text-blue-400">{(stats.insurance_pool / 1000000).toFixed(2)}M</span>
                 <ShieldCheck className="w-3 h-3 text-blue-400/50" />
              </div>
           </div>
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Network Burn</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-2xl font-black text-white">{(stats.burn_count / 1000000).toFixed(1)}M</span>
                 <Zap className="w-3 h-3 text-white/30" />
              </div>
           </div>
        </div>

        {/* Detailed Insights Section */}
        <div className="grid grid-cols-12 gap-8">
          
          {/* Allocation Breakdown */}
          <div className="col-span-12 lg:col-span-4 bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl flex flex-col justify-between">
             <div>
                <h3 className="text-xs font-black text-white uppercase tracking-widest mb-8 flex items-center gap-3">
                  <PieChart className="w-4 h-4 text-indigo-500" /> Fund Allocation
                </h3>
                <div className="space-y-6">
                  {allocation.map((item, i) => (
                    <div key={i} className="group cursor-default">
                       <div className="flex justify-between items-center mb-2">
                          <div className="flex items-center gap-3">
                             <item.icon className="w-3.5 h-3.5 text-gray-600" />
                             <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">{item.label}</span>
                          </div>
                          <span className="text-xs font-black text-white">{item.value}%</span>
                       </div>
                       <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                          <div className={`${item.color} h-full group-hover:opacity-80 transition-opacity`} style={{ width: `${item.value}%` }} />
                       </div>
                    </div>
                  ))}
                </div>
             </div>
             
             <div className="pt-8 border-t border-white/5 mt-8">
                <div className="p-4 bg-indigo-500/5 border border-indigo-500/10 rounded-lg">
                   <p className="text-[10px] text-gray-500 leading-relaxed italic">
                     "Treasury distribution is finalized every epoch by a 2-of-3 Multi-Sig involving the Foundation and elected High Court Jurors."
                   </p>
                </div>
             </div>
          </div>

          {/* Transaction Ledger */}
          <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
             <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-8">
                <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                  <History className="w-4 h-4 text-emerald-500" /> Transaction Ledger
                </h3>
                <div className="flex gap-2">
                   {['ALL', 'INFLOW', 'OUTFLOW'].map(f => (
                     <button key={f} onClick={() => setFilter(f)} className={`px-3 py-1 text-[8px] font-black rounded border ${filter === f ? 'bg-white text-black border-white' : 'border-white/10 text-gray-500'}`}>{f}</button>
                   ))}
                </div>
             </div>
             
             <div className="divide-y divide-white/5">
                {ledger.filter(tx => filter === 'ALL' || tx.type === filter).map((tx) => (
                  <div key={tx.id} className="p-6 flex items-center justify-between hover:bg-white/[0.01] transition-colors group">
                    <div className="flex items-center gap-6">
                       <div className={`w-10 h-10 rounded-lg flex items-center justify-center border ${tx.type === 'INFLOW' ? 'bg-green-500/10 border-green-500/20 text-green-500' : 'bg-red-500/10 border-red-500/20 text-red-500'}`}>
                          {tx.type === 'INFLOW' ? <ArrowUpRight className="w-5 h-5" /> : <ArrowDownRight className="w-5 h-5" />}
                       </div>
                       <div>
                          <span className="text-[11px] font-black text-white uppercase tracking-tighter block mb-0.5 group-hover:text-indigo-400 transition-colors">{tx.id}</span>
                          <span className="text-[9px] text-gray-600 uppercase font-bold tracking-widest">{tx.category} // {tx.timestamp}</span>
                       </div>
                    </div>
                    <div className="flex items-center gap-8">
                       <div className="text-right">
                          <span className={`text-sm font-black block mb-0.5 ${tx.type === 'INFLOW' ? 'text-green-500' : 'text-red-400'}`}>
                            {tx.type === 'INFLOW' ? '+' : '-'}{tx.amount.toLocaleString()} SATS
                          </span>
                          <span className="text-[9px] text-gray-700 uppercase font-black tracking-widest">{tx.status}</span>
                       </div>
                       <ChevronRight className="w-4 h-4 text-gray-800" />
                    </div>
                  </div>
                ))}
             </div>
             
             <button className="w-full py-4 text-[10px] font-black text-gray-600 hover:text-white uppercase tracking-[0.3em] border-t border-white/5 bg-white/[0.01] transition-all">
                Download Full Ledger (CSV/JSON)
             </button>
          </div>

        </div>

        {/* Transparency Verification Card */}
        <div className="mt-8 bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-8 flex flex-col md:flex-row items-center gap-8 shadow-2xl">
           <div className="p-5 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl">
              <Lock className="w-10 h-10 text-indigo-500" />
           </div>
           <div className="flex-1 text-center md:text-left">
              <h3 className="text-xl font-black text-white uppercase tracking-tighter mb-2">Multi-Sig Accountability</h3>
              <p className="text-xs text-gray-500 leading-relaxed max-w-xl">
                 All protocol funds are held in a 2-of-3 multi-signature vault. Keys are held by the Proxy Protocol Foundation, a rotating Tier 3 High Court Juror, and a third-party institutional security partner.
              </p>
           </div>
           <div className="flex flex-col gap-3 w-full md:w-auto">
              <button className="px-8 py-3 bg-white text-black font-black text-[10px] uppercase tracking-widest hover:bg-indigo-500 hover:text-white transition-all whitespace-nowrap">
                 Verify Wallet Hash
              </button>
              <button className="px-8 py-3 border border-white/10 text-gray-500 font-black text-[10px] uppercase tracking-widest hover:text-white transition-all whitespace-nowrap">
                 View Keyholders
              </button>
           </div>
        </div>
      </main>

      {/* Global Status Marquee (Footer) */}
      <footer className="max-w-6xl mx-auto mt-12 bg-[#0a0a0a] border-t border-white/5 p-4 overflow-hidden grayscale opacity-50 hover:grayscale-0 hover:opacity-100 transition-all duration-700">
         <div className="flex gap-12 text-[9px] text-gray-700 font-black uppercase tracking-widest animate-marquee whitespace-nowrap">
            <span>[*] TREASURY_EPOCH: 88293</span>
            <span>[*] MULTISIG_STATUS: LOCKED</span>
            <span>[*] RESERVES_BTC: 0.717901</span>
            <span>[*] GRANTS_REMAINING: 5.0M SATS</span>
            <span>[*] INSURANCE_LIQUIDITY: OK</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes marquee {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }
        .animate-marquee {
          animation: marquee 40s linear infinite;
        }
      `}} />
    </div>
  );
};

export default App;
