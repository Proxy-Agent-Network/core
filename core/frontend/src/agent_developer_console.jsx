import React, { useState, useEffect } from 'react';
import { 
  Code2, Terminal, Key, Wallet, Activity, 
  Zap, ZapOff, LayoutDashboard, Settings, 
  CreditCard, ExternalLink, Plus, Copy,
  CheckCircle2, AlertTriangle, ArrowUpRight,
  Database, RefreshCw, Cpu, Layers, Bot,
  ShieldCheck, Lock, Globe, Share2
} from 'lucide-react';

const App = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [copySuccess, setCopySuccess] = useState('');

  // Mock Developer Data
  const [developer] = useState({
    id: "DEV_8829_X",
    org: "AGI_SYNTHETICS_LAB",
    active_agents: 14,
    balance_sats: 8420500,
    api_key: "proxy_live_8293...k921"
  });

  const [subscriptions] = useState([
    { id: "PASS-01", name: "Premium Tier", status: "ACTIVE", renewal: "2026-03-01", cost: 500000 },
    { id: "PASS-02", name: "API Rate Boost", status: "PENDING", renewal: "2026-02-28", cost: 150000 }
  ]);

  const [recentTasks] = useState([
    { id: "T-9901", agent: "Crawler_Bot_1", cost: 420, status: "SETTLED", type: "DATA_VERIFICATION" },
    { id: "T-9892", agent: "Adjudicator_X", cost: 1200, status: "IN_FLIGHT", type: "LEGAL_SIGNATURE" },
    { id: "T-9884", agent: "Crawler_Bot_2", cost: 420, status: "SETTLED", type: "DATA_VERIFICATION" }
  ]);

  const handleCopy = (text) => {
    // Standard clipboard copy for environment
    const textArea = document.createElement("textarea");
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      setCopySuccess('Copied!');
    } catch (err) {
      setCopySuccess('Failed');
    }
    document.body.removeChild(textArea);
    setTimeout(() => setCopySuccess(''), 2000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8">
      
      {/* Sidebar Navigation */}
      <aside className="fixed left-0 top-0 h-full w-20 md:w-64 bg-[#0a0a0a] border-r border-white/5 flex flex-col items-center md:items-start py-8 z-20">
        <div className="px-6 mb-12 flex items-center gap-3">
          <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
            <Bot className="w-6 h-6 text-indigo-500" />
          </div>
          <span className="hidden md:block font-black text-white text-lg tracking-tighter uppercase">Proxy Dev</span>
        </div>

        <nav className="w-full space-y-2 px-3">
          {[
            { id: 'overview', label: 'Dashboard', icon: LayoutDashboard },
            { id: 'agents', label: 'Active Agents', icon: Cpu },
            { id: 'keys', label: 'API & Security', icon: Key },
            { id: 'billing', label: 'Proxy-Pass', icon: Wallet },
            { id: 'docs', label: 'Documentation', icon: Code2 }
          ].map((item) => (
            <button 
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-4 px-4 py-3 rounded-lg transition-all ${
                activeTab === item.id 
                  ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' 
                  : 'text-gray-500 hover:text-white hover:bg-white/5'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="hidden md:block text-xs font-bold uppercase tracking-widest">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="mt-auto px-6 w-full">
           <div className="p-4 bg-white/5 rounded-xl border border-white/5 hidden md:block">
              <div className="flex items-center gap-2 mb-2">
                 <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                 <span className="text-[9px] text-gray-500 uppercase font-black">Mainnet Uplink</span>
              </div>
              <p className="text-[10px] text-gray-400 font-bold uppercase truncate">{developer.org}</p>
           </div>
        </div>
      </aside>

      <main className="ml-20 md:ml-64 max-w-6xl mx-auto space-y-8">
        
        {/* Top Stats Bar */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-2xl group hover:border-indigo-500/30 transition-all">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Principal Balance</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-2xl font-black text-white tracking-tighter">{(developer.balance_sats / 1000000).toFixed(2)}M</span>
                 <span className="text-[10px] text-indigo-500 font-bold">SATS</span>
              </div>
           </div>
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-2xl group hover:border-green-500/30 transition-all">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Running Agents</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-2xl font-black text-white tracking-tighter">{developer.active_agents}</span>
                 <span className="text-[10px] text-green-500 font-bold">ONLINE</span>
              </div>
           </div>
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-2xl group hover:border-amber-500/30 transition-all">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Proxy-Pass Tier</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-2xl font-black text-white tracking-tighter">ELITE</span>
                 <span className="text-[10px] text-amber-500 font-bold">ACTIVE</span>
              </div>
           </div>
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-2xl">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Uptime Reliability</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-2xl font-black text-white tracking-tighter">99.98%</span>
              </div>
           </div>
        </div>

        {activeTab === 'overview' && (
          <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Real-time Spending Chart (Simulated) */}
            <div className="col-span-12 lg:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
              <div className="flex justify-between items-center mb-8">
                <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                  <Activity className="w-4 h-4 text-indigo-500" /> Satoshi Burn Rate (24h)
                </h3>
                <div className="flex gap-4">
                  <span className="flex items-center gap-2 text-[9px] text-gray-600 font-bold uppercase"><div className="w-2 h-2 bg-indigo-500 rounded-full" /> Total Inflow</span>
                  <span className="flex items-center gap-2 text-[9px] text-gray-600 font-bold uppercase"><div className="w-2 h-2 bg-red-500 rounded-full" /> Task Payouts</span>
                </div>
              </div>
              
              <div className="h-48 flex items-end gap-2 px-2 relative">
                 {[...Array(24)].map((_, i) => (
                   <div key={i} className="flex-1 bg-white/5 rounded-t-sm relative group" style={{ height: `${20 + Math.random() * 60}%` }}>
                      <div className="absolute inset-0 bg-indigo-500/20 opacity-0 group-hover:opacity-100 transition-opacity rounded-t-sm" />
                   </div>
                 ))}
              </div>
              <div className="flex justify-between mt-4 text-[9px] text-gray-700 font-bold uppercase">
                <span>24h Ago</span>
                <span>Current Epoch</span>
              </div>
            </div>

            {/* Recent Activity List */}
            <div className="col-span-12 lg:col-span-4 space-y-6">
               <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                  <div className="p-4 bg-white/[0.02] border-b border-white/5 flex justify-between items-center">
                    <h3 className="text-xs font-black text-white uppercase tracking-widest">Recent Tasks</h3>
                    <Settings className="w-3.5 h-3.5 text-gray-600" />
                  </div>
                  <div className="divide-y divide-white/5">
                    {recentTasks.map((task) => (
                      <div key={task.id} className="p-4 hover:bg-white/[0.01] transition-colors flex justify-between items-center group">
                        <div>
                          <span className="text-[10px] font-black text-white block mb-0.5">{task.id}</span>
                          <span className="text-[8px] text-gray-600 uppercase font-bold">{task.type}</span>
                        </div>
                        <div className="text-right">
                          <span className="text-[10px] font-black text-indigo-400 block">{task.cost} SATS</span>
                          <span className={`text-[8px] font-black uppercase ${task.status === 'SETTLED' ? 'text-green-500' : 'text-amber-500'}`}>
                            {task.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <button className="w-full py-3 bg-white/5 text-[9px] font-black text-gray-500 uppercase tracking-widest hover:text-white transition-colors border-t border-white/5">
                    View All Activity
                  </button>
               </div>

               <div className="p-6 border border-indigo-500/20 bg-indigo-500/5 rounded-xl">
                  <div className="flex items-center gap-3 mb-4">
                     <AlertTriangle className="w-4 h-4 text-amber-500" />
                     <h4 className="text-[10px] font-black text-white uppercase tracking-widest">Liquidity Alert</h4>
                  </div>
                  <p className="text-[11px] text-gray-500 leading-relaxed italic mb-4">
                    "Available balance is below the recommended threshold for scheduled Tier 1 tasks. Consider topping up your Proxy-Pass."
                  </p>
                  <button className="w-full py-2 bg-indigo-500 text-black font-black text-[9px] uppercase tracking-widest rounded hover:bg-indigo-400 transition-all">
                    Recharge Escrow
                  </button>
               </div>
            </div>
          </div>
        )}

        {activeTab === 'keys' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
                <h3 className="text-sm font-black text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                  <Key className="w-5 h-5 text-indigo-500" /> API Access Keys
                </h3>
                <div className="space-y-6">
                   <div className="p-6 bg-black/40 border border-white/5 rounded-lg flex items-center justify-between group">
                      <div>
                        <span className="text-[9px] text-gray-600 uppercase font-black block mb-2">Secret Key</span>
                        <div className="flex items-center gap-4">
                           <code className="text-xs text-indigo-400 font-mono tracking-tighter">{developer.api_key}</code>
                           <button onClick={() => handleCopy(developer.api_key)} className="p-1 hover:text-white transition-colors relative">
                              <Copy className="w-4 h-4" />
                              {copySuccess && <span className="absolute -top-8 left-1/2 -translate-x-1/2 bg-white text-black text-[8px] px-2 py-1 rounded font-black">{copySuccess}</span>}
                           </button>
                        </div>
                      </div>
                      <div className="text-right">
                         <span className="text-[9px] text-green-500 uppercase font-black block mb-1">Status</span>
                         <span className="text-[10px] text-gray-500 font-bold uppercase">ACTIVE</span>
                      </div>
                   </div>

                   <div className="flex gap-4">
                      <button className="flex-1 py-4 bg-white/5 border border-white/10 rounded-lg text-xs font-black text-white uppercase tracking-widest hover:bg-white/10 transition-all flex items-center justify-center gap-2">
                         <RefreshCw className="w-4 h-4" /> Rotate Keys
                      </button>
                      <button className="flex-1 py-4 bg-red-500/10 border border-red-500/20 rounded-lg text-xs font-black text-red-500 uppercase tracking-widest hover:bg-red-500/20 transition-all flex items-center justify-center gap-2">
                         <ZapOff className="w-4 h-4" /> Revoke All
                      </button>
                   </div>
                </div>
             </div>

             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
                <h3 className="text-sm font-black text-white uppercase tracking-widest mb-2 flex items-center gap-3">
                  <ShieldCheck className="w-5 h-5 text-indigo-500" /> E2EE Task Tunnels
                </h3>
                <p className="text-xs text-gray-500 mb-8 max-w-2xl leading-relaxed">
                  Generate RSA-2048 identity keys to establish encrypted tunnels with human nodes. This ensures task metadata is never visible to the protocol maintainers or the network gateway.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   <div className="p-6 border border-white/5 bg-black/40 rounded-xl">
                      <div className="flex justify-between items-center mb-4">
                         <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest">Public Identity</span>
                         <CheckCircle2 className="w-4 h-4 text-green-500" />
                      </div>
                      <div className="bg-black border border-white/5 p-4 rounded h-32 flex items-center justify-center text-center">
                         <p className="text-[10px] text-gray-700 font-mono italic">
                           -----BEGIN PUBLIC KEY-----<br/>
                           MIIBIjANBgkqhkiG9w0BAQEFAA...<br/>
                           IDAQAB<br/>
                           -----END PUBLIC KEY-----
                         </p>
                      </div>
                   </div>
                   <div className="p-6 border border-white/5 bg-black/40 rounded-xl relative overflow-hidden group">
                      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm z-10 flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                         <Lock className="w-8 h-8 text-indigo-500 mb-2" />
                         <span className="text-[10px] text-white font-black uppercase tracking-widest">View Secret</span>
                      </div>
                      <div className="flex justify-between items-center mb-4">
                         <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest">Private Key</span>
                         <ShieldCheck className="w-4 h-4 text-gray-700" />
                      </div>
                      <div className="bg-black border border-white/5 p-4 rounded h-32 flex items-center justify-center text-center">
                         <div className="space-y-1 opacity-20">
                            <div className="w-48 h-2 bg-white/10 rounded-full mx-auto" />
                            <div className="w-40 h-2 bg-white/10 rounded-full mx-auto" />
                            <div className="w-44 h-2 bg-white/10 rounded-full mx-auto" />
                         </div>
                      </div>
                   </div>
                </div>
             </div>
          </div>
        )}

        {activeTab === 'billing' && (
           <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8">
                   <Share2 className="w-32 h-32 text-indigo-500/5 -rotate-12" />
                </div>
                <h3 className="text-sm font-black text-white uppercase tracking-widest mb-8 flex items-center gap-3">
                  <CreditCard className="w-5 h-5 text-indigo-500" /> Proxy-Pass Subscriptions
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                   {subscriptions.map(sub => (
                      <div key={sub.id} className="p-6 border border-white/10 bg-white/[0.02] rounded-xl flex justify-between items-center hover:border-indigo-500/30 transition-all">
                         <div>
                            <span className="text-[9px] text-gray-500 uppercase font-black block mb-1">{sub.id}</span>
                            <h4 className="text-lg font-black text-white uppercase mb-1">{sub.name}</h4>
                            <span className="text-[10px] text-indigo-400 font-bold tracking-widest">{sub.status}</span>
                         </div>
                         <div className="text-right">
                            <span className="text-xl font-black text-white block mb-1">{sub.cost.toLocaleString()} <span className="text-xs text-gray-600">SATS</span></span>
                            <span className="text-[9px] text-gray-600 uppercase font-black">Renews {sub.renewal}</span>
                         </div>
                      </div>
                   ))}
                   <button className="border-2 border-dashed border-white/5 rounded-xl flex flex-col items-center justify-center p-8 hover:bg-white/5 hover:border-indigo-500/20 transition-all group">
                      <Plus className="w-8 h-8 text-gray-700 group-hover:text-indigo-500 mb-2 transition-colors" />
                      <span className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Provision New Pass</span>
                   </button>
                </div>
              </div>

              <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-8 flex flex-col md:flex-row items-center gap-8 shadow-2xl">
                 <div className="p-6 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl">
                    <Zap className="w-12 h-12 text-indigo-500 animate-pulse" />
                 </div>
                 <div className="flex-1 text-center md:text-left">
                    <h3 className="text-xl font-black text-white uppercase tracking-tighter mb-2">Protocol Scaling Escrow</h3>
                    <p className="text-xs text-gray-500 leading-relaxed max-xl">
                       Proxy-Passes allow you to lock significant Satoshi liquidity into the network to guarantee priority routing and higher rate limits for your AGI agents. Locked funds accrue 0.5% Reputation Yield per epoch.
                    </p>
                 </div>
                 <button className="px-8 py-4 bg-indigo-500 text-black font-black text-xs uppercase tracking-[0.2em] rounded-lg hover:bg-indigo-400 transition-all shadow-[0_0_30px_rgba(99,102,241,0.3)]">
                    Add Liquidity
                 </button>
              </div>
           </div>
        )}

      </main>

      {/* Global Status Marquee */}
      <footer className="ml-20 md:ml-64 mt-12 bg-[#0a0a0a] border-t border-white/5 p-4 overflow-hidden">
         <div className="flex gap-12 text-[9px] text-gray-700 font-black uppercase tracking-widest animate-marquee whitespace-nowrap">
            <span>[*] LATENCY_US_WEST: 42MS</span>
            <span>[*] ACTIVE_TASK_POOLS: 182</span>
            <span>[*] ESCROW_LOCKED_TOTAL: 71.8M SATS</span>
            <span>[*] REPUTATION_YIELD: +0.5% / EPOCH</span>
            <span>[*] CONGESTION_MULTIPLIER: 1.0X</span>
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
