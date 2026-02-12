import React, { useState, useEffect } from 'react';
import { 
  Activity, Globe, Zap, ShieldCheck, 
  Clock, BarChart3, Server, Wifi, 
  CheckCircle2, AlertCircle, RefreshCw, 
  Map as MapIcon, Info, ChevronRight,
  Database, Shield, Binary
} from 'lucide-react';

const App = () => {
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [latency, setLatency] = useState(42);

  // Mock Global Network Status
  const [stats] = useState({
    api_gateway: "OPERATIONAL",
    settlement_layer: "OPERATIONAL",
    active_nodes: 1248,
    global_integrity: 0.9992,
    congestion_multiplier: 1.0,
    total_volume_24h: 4250800,
    active_governance_cases: 2
  });

  const [regions] = useState([
    { name: "North America (US-WEST)", nodes: 450, health: 1.0, load: "12%" },
    { name: "Europe (EU-WEST)", nodes: 380, health: 0.99, load: "18%" },
    { name: "Asia Pacific (ASIA-SE)", nodes: 310, health: 0.98, load: "24%" },
    { name: "Other (LATAM/MENA)", nodes: 108, health: 0.95, load: "9%" }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setLatency(Math.floor(38 + Math.random() * 10));
      setLastUpdate(new Date());
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleManualRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-green-500/30">
      
      {/* Background Grid Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '30px 30px' }} />

      {/* Header */}
      <header className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center mb-12 border-b border-white/10 pb-8 gap-6 relative z-10">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-xl">
            <ShieldCheck className="w-8 h-8 text-green-500 animate-pulse" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Network Status</h1>
            <div className="flex items-center gap-2 mt-1">
               <span className="text-[10px] uppercase tracking-[0.2em] text-gray-500">Proxy Protocol v2.3.3</span>
               <div className="h-2 w-px bg-white/10" />
               <span className="text-[10px] text-green-500 font-bold uppercase tracking-widest flex items-center gap-1">
                 <CheckCircle2 className="w-3 h-3" /> All Systems Nominal
               </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right hidden md:block">
            <span className="text-[9px] uppercase font-black text-gray-600 block">Last Checksum</span>
            <span className="text-xs text-gray-400">{lastUpdate.toLocaleTimeString()} UTC</span>
          </div>
          <button 
            onClick={handleManualRefresh}
            className={`p-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
          >
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-12 gap-6 relative z-10">
        
        {/* Real-time Vitals Grid */}
        <div className="col-span-12 grid grid-cols-1 md:grid-cols-4 gap-6 mb-4">
           {[
             { label: 'Avg Latency', val: `${latency}ms`, sub: 'STABLE', icon: Zap, color: 'green' },
             { label: 'Active Nodes', val: stats.active_nodes.toLocaleString(), sub: 'VERIFIED', icon: Server, color: 'blue' },
             { label: 'Integrity Index', val: `${(stats.global_integrity * 100).toFixed(2)}%`, sub: 'TPM ATTESTED', icon: Binary, color: 'indigo' },
             { label: 'Network Load', val: `${stats.congestion_multiplier}x`, sub: 'BASE PRICE', icon: Activity, color: 'emerald' }
           ].map((vital, i) => (
             <div key={i} className="bg-[#0a0a0a] border border-white/5 p-6 rounded-lg shadow-2xl relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
                  <vital.icon className="w-24 h-24" />
                </div>
                <span className="text-[9px] text-gray-600 uppercase font-black tracking-[0.2em] block mb-2">{vital.label}</span>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-black text-white tracking-tighter">{vital.val}</span>
                  <span className={`text-[9px] font-black text-${vital.color}-500 uppercase tracking-widest`}>{vital.sub}</span>
                </div>
             </div>
           ))}
        </div>

        {/* Uptime and Regional Status */}
        <div className="col-span-12 lg:col-span-8 space-y-6">
          <div className="bg-[#0a0a0a] border border-white/5 rounded-lg p-8 shadow-2xl">
            <h3 className="text-xs font-black text-white uppercase tracking-widest mb-8 flex items-center gap-3">
              <Clock className="w-4 h-4 text-green-500" /> Service Availability (Last 90 Days)
            </h3>
            
            <div className="space-y-10">
               <div>
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-[10px] text-gray-500 uppercase font-black">API Gateway</span>
                    <span className="text-[10px] text-green-500 font-bold">99.99% Uptime</span>
                  </div>
                  <div className="flex gap-1 h-8">
                     {[...Array(50)].map((_, i) => (
                       <div key={i} className={`flex-1 rounded-sm ${i === 42 ? 'bg-yellow-500/40' : 'bg-green-500/20'}`} title="Feb 10: 99.95%" />
                     ))}
                  </div>
               </div>

               <div>
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-[10px] text-gray-500 uppercase font-black">Lightning Settlement Rails</span>
                    <span className="text-[10px] text-green-500 font-bold">99.95% Uptime</span>
                  </div>
                  <div className="flex gap-1 h-8">
                     {[...Array(50)].map((_, i) => (
                       <div key={i} className={`flex-1 rounded-sm ${i === 15 ? 'bg-red-500/40' : 'bg-green-500/20'}`} title="Jan 28: 98.2% (LN Partition)" />
                     ))}
                  </div>
               </div>
            </div>
          </div>

          {/* Regional Health Table */}
          <div className="bg-[#0a0a0a] border border-white/5 rounded-lg overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center">
               <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                 <Globe className="w-4 h-4 text-blue-500" /> Regional Distribution
               </h3>
               <span className="text-[9px] text-gray-600 font-bold uppercase">4 Geographical Hubs</span>
            </div>
            <div className="divide-y divide-white/5">
               {regions.map((region, i) => (
                 <div key={i} className="p-6 flex items-center justify-between group hover:bg-white/[0.01] transition-colors">
                    <div className="flex items-center gap-6">
                       <div className={`w-2 h-2 rounded-full ${region.health === 1.0 ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'}`} />
                       <div>
                          <span className="text-xs font-black text-white uppercase tracking-tight block mb-0.5">{region.name}</span>
                          <span className="text-[9px] text-gray-600 uppercase font-bold">{region.nodes} Online // {region.load} Utilization</span>
                       </div>
                    </div>
                    <div className="flex items-center gap-4">
                       <div className="w-32 bg-white/5 h-1 rounded-full overflow-hidden hidden md:block">
                          <div className="bg-green-500 h-full opacity-60" style={{ width: `${region.health * 100}%` }} />
                       </div>
                       <ChevronRight className="w-4 h-4 text-gray-800 group-hover:text-white transition-colors" />
                    </div>
                 </div>
               ))}
            </div>
          </div>
        </div>

        {/* Side Panel: Active Incident / Gov Status */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
           {/* Governance Activity */}
           <div className="bg-[#0a0a0a] border border-white/5 rounded-lg p-8 shadow-2xl">
              <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                <Shield className="w-4 h-4 text-indigo-500" /> Consensus Watch
              </h3>
              <div className="space-y-6">
                 <div className="p-4 bg-white/5 rounded border border-white/5">
                    <div className="flex justify-between items-center mb-2">
                       <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">PIP-882 Voting</span>
                       <span className="text-[9px] text-green-500 font-bold">PHASE 03</span>
                    </div>
                    <p className="text-[11px] text-gray-500 leading-relaxed mb-4">Community vote to increase Tier 3 collateral requirement.</p>
                    <div className="w-full bg-black h-1.5 rounded-full overflow-hidden">
                       <div className="bg-indigo-500 h-full" style={{ width: '74.6%' }} />
                    </div>
                 </div>

                 <div className="flex items-center gap-4 text-[10px] text-gray-600 font-bold uppercase tracking-widest pt-2">
                    <div className="flex-1 flex flex-col items-center p-3 border border-white/5 rounded">
                       <span className="text-white text-lg font-black">{stats.active_governance_cases}</span>
                       <span>Active Cases</span>
                    </div>
                    <div className="flex-1 flex flex-col items-center p-3 border border-white/5 rounded">
                       <span className="text-white text-lg font-black">2h</span>
                       <span>Avg Resolution</span>
                    </div>
                 </div>
              </div>
           </div>

           {/* Public Info / Help */}
           <div className="p-6 border border-white/10 bg-gradient-to-br from-green-500/5 to-blue-500/5 rounded-xl shadow-inner">
              <div className="flex items-center gap-3 mb-4">
                 <Info className="w-5 h-5 text-gray-400" />
                 <h4 className="text-xs font-black text-white uppercase tracking-widest">Transparency Note</h4>
              </div>
              <p className="text-[11px] text-gray-500 leading-relaxed italic mb-6">
                "All performance data is derived from cryptographically-signed heartbeats. Regional health metrics reflect real-time hardware attestation audits across the node fleet."
              </p>
              <button className="w-full py-3 bg-white/5 border border-white/10 text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 hover:text-white hover:bg-white/10 transition-all">
                Audit Registry
              </button>
           </div>

           <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded flex items-center justify-between group cursor-pointer hover:bg-white/5 transition-all shadow-2xl">
              <div className="flex items-center gap-4">
                <Database className="w-5 h-5 text-gray-600" />
                <div className="flex flex-col">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Uptime Proof</span>
                   <span className="text-[10px] text-gray-400 font-mono">STATUS_LOGS_2026.JSON</span>
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-700" />
           </div>
        </div>

      </main>

      {/* Global Marquee (Footer) */}
      <footer className="max-w-6xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center gap-6 overflow-hidden">
        <div className="flex items-center gap-2 whitespace-nowrap">
          <span className="w-2 h-2 bg-green-500 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
          <span className="text-[9px] text-white font-black uppercase tracking-widest">Mainnet Uplink Active</span>
        </div>
        <div className="h-4 w-px bg-white/10" />
        <div className="flex-1 flex gap-12 text-[9px] text-gray-600 font-bold uppercase tracking-widest animate-marquee whitespace-nowrap">
           <span>[*] 24H_TX_VOLUME: 4.2M SATS</span>
           <span>[*] REPUTATION_AVG: 942.5</span>
           <span>[*] ACTIVE_PIPS: 3</span>
           <span>[*] LAST_BTC_BLOCK: 882931</span>
           <span>[*] NODE_COUNT_GLOBAL: 1,248</span>
           <span>[*] REPUTATION_STABILITY: 99.2%</span>
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
