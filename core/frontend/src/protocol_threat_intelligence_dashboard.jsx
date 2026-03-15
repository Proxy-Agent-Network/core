import React, { useState, useEffect } from 'react';
import { 
  Globe, 
  ShieldAlert, 
  Activity, 
  RefreshCw, 
  Search, 
  Filter, 
  MapPin, 
  Zap, 
  Lock, 
  Binary, 
  LayoutGrid, 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  Info, 
  ChevronRight, 
  ShieldX, 
  EyeOff, 
  Terminal, 
  Radio,
  XCircle,
  AlertTriangle,
  Fingerprint
} from 'lucide-react';

/**
 * PROXY PROTOCOL - THREAT INTELLIGENCE DASHBOARD (v1.0)
 * "Visualizing the noise before it hits the mempool."
 * ----------------------------------------------------
 */

const App = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedThreat, setSelectedThreat] = useState(null);
  const [lastSync, setLastSync] = useState(new Date());

  // Mock Threat Intel Data (Reflecting core/ops/threat_intelligence_api.py)
  const [threats] = useState([
    { id: "THT-8821-PX", ip: "185.220.101.42", type: "TOR_EXIT_NODE", risk: 0.80, status: "BLOCKED", region: "EU-NORTH", confidence: 1.0 },
    { id: "THT-7714-PX", ip: "45.15.22.91", type: "KNOWN_SYBIL_CLUSTER", risk: 0.95, status: "BLOCKED", region: "ASIA-SE", confidence: 0.98 },
    { id: "THT-6602-PX", ip: "103.22.201.12", type: "DATA_CENTER_PROXY", risk: 0.75, status: "FLAGGED", region: "US-EAST", confidence: 0.92 },
    { id: "THT-4411-PX", ip: "HW-8829-PX-04", type: "REVOKED_TPM_CHIP", risk: 1.00, status: "BLACKLISTED", region: "GLOBAL", confidence: 1.0 }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setLastSync(new Date());
      setIsRefreshing(false);
    }, 1200);
  };

  const getRiskColor = (risk) => {
    if (risk >= 0.9) return 'text-red-500';
    if (risk >= 0.7) return 'text-orange-500';
    return 'text-yellow-500';
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-red-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header: Intelligence Desk */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl shadow-[0_0_20px_rgba(239,68,68,0.1)]">
              <Globe className="w-8 h-8 text-red-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Threat Intelligence</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2 font-mono">
                External Risk Aggregator // Protocol <span className="text-red-500">v3.4.0</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Sentinel Blocks</span>
                   <span className="text-xl font-black text-white tracking-tighter">1,842 <span className="text-[10px] text-red-500 font-bold">/ 24H</span></span>
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

        {/* Intelligence Pillar Matrix */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
           {[
             { label: 'Tor Exit Filter', val: '412', sub: 'ACTIVE_BLOCKS', icon: EyeOff, color: 'red' },
             { label: 'VPN Mitigation', val: '842', sub: 'DATA_CENTER_HITS', icon: Radio, color: 'orange' },
             { label: 'Sybil Clusters', val: '12', sub: 'MONITORED_PREFIX', icon: Binary, color: 'yellow' },
             { label: 'Malicious Hardware', val: '04', sub: 'REVOKED_TPM', icon: ShieldX, color: 'red' }
           ].map((kpi, i) => (
             <div key={i} className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
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
          
          {/* Active Ingress Stream (Left Column) */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <Activity className="w-4 h-4 text-red-500" /> Ingress Pulse
                   </h3>
                   <div className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping" />
                      <span className="text-[9px] text-red-500 font-bold uppercase">Live Filter</span>
                   </div>
                </div>

                <div className="divide-y divide-white/5">
                   {threats.map((threat) => (
                      <div 
                        key={threat.id} 
                        onClick={() => setSelectedThreat(threat)}
                        className={`p-6 hover:bg-white/[0.01] transition-all cursor-pointer group ${selectedThreat?.id === threat.id ? 'bg-red-500/[0.03]' : ''}`}
                      >
                         <div className="flex justify-between items-start mb-4">
                            <div>
                               <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-red-400 transition-colors">{threat.ip}</span>
                               <p className="text-[9px] text-gray-600 font-bold uppercase mt-1">{threat.type} // {threat.region}</p>
                            </div>
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border border-red-500/20 bg-red-500/10 text-red-500`}>
                               {Math.round(threat.risk * 100)}% RISK
                            </span>
                         </div>
                         <div className="flex justify-between items-center mt-4 text-[9px] font-black text-gray-700 uppercase tracking-widest">
                            <span className="flex items-center gap-1.5"><MapPin className="w-3 h-3" /> {threat.status}</span>
                            <span>{lastSync.toLocaleTimeString()}</span>
                         </div>
                      </div>
                   ))}
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-[#0a0a0a] rounded-xl shadow-inner relative overflow-hidden group">
                <div className="absolute -bottom-6 -right-6 opacity-[0.02] group-hover:scale-110 transition-transform duration-1000">
                   <Lock className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-red-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5 text-red-500" /> Filtering Logic
                </h4>
                <p className="text-xs text-gray-500 leading-relaxed mb-6 italic">
                   "Incoming heartbeats are pre-filtered against global blacklists. Nodes originating from Tor exit points or data-center VPN subnets are automatically shed to preserve network biological purity."
                </p>
                <div className="flex justify-between items-center text-[9px] font-black uppercase text-gray-600 border-t border-white/5 pt-4">
                   <span>Pre-Filter Mode</span>
                   <span className="text-red-500">STRICT</span>
                </div>
             </div>
          </div>

          {/* Forensic Inspection View (Right Column) */}
          <div className="col-span-12 lg:col-span-8 flex flex-col h-full">
             {selectedThreat ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 shadow-2xl animate-in slide-in-from-right-4 duration-300 flex-1 flex flex-col gap-10">
                   <div className="flex justify-between items-start border-b border-white/5 pb-6">
                      <div>
                         <span className="text-[10px] text-red-500 font-black uppercase tracking-[0.2em] block mb-1">Forensic Analysis</span>
                         <h2 className="text-3xl font-black text-white tracking-tighter uppercase">{selectedThreat.ip}</h2>
                      </div>
                      <button onClick={() => setSelectedThreat(null)} className="p-3 text-gray-600 hover:text-white transition-colors">
                         <XCircle className="w-6 h-6" />
                      </button>
                   </div>

                   {/* Threat Composition Grid */}
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                      <div className="space-y-8">
                         <div>
                            <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                               <ShieldAlert className="w-3.5 h-3.5 text-red-500" /> Risk Classification
                            </h4>
                            <div className="space-y-4">
                               {[
                                 { label: 'Vector Type', val: selectedThreat.type, risk: 'HIGH' },
                                 { label: 'Attribution Confidence', val: `${(selectedThreat.confidence * 100).toFixed(0)}%`, risk: 'SECURE' },
                                 { label: 'Historical Re-occurrence', val: '12 Instances', risk: 'ELEVATED' }
                               ].map((metric, i) => (
                                 <div key={i} className="flex justify-between items-center p-4 bg-black border border-white/5 rounded-lg group hover:border-red-500/30 transition-all">
                                    <div>
                                       <span className="text-[9px] text-gray-700 font-black uppercase block">{metric.label}</span>
                                       <span className="text-xs font-bold text-gray-400">{metric.val}</span>
                                    </div>
                                    <AlertTriangle className={`w-4 h-4 ${metric.risk === 'HIGH' ? 'text-red-500' : 'text-gray-800'}`} />
                                 </div>
                               ))}
                            </div>
                         </div>
                      </div>

                      <div className="space-y-8">
                         <div>
                            <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                               <Binary className="w-3.5 h-3.5 text-indigo-500" /> Intelligence Metadata
                            </h4>
                            <div className="bg-black border border-white/5 rounded-xl p-6 font-mono text-[10px] space-y-4 shadow-inner">
                               <div className="flex justify-between items-center">
                                  <span className="text-gray-600 uppercase">ASN Source</span>
                                  <span className="text-white">AS16276 (OVH SAS)</span>
                               </div>
                               <div className="flex justify-between items-center">
                                  <span className="text-gray-600 uppercase">Blacklist Ref</span>
                                  <span className="text-indigo-400 font-bold uppercase underline cursor-pointer">SPAMHAUS_DROP</span>
                               </div>
                               <div className="flex justify-between items-center pt-4 border-t border-white/5">
                                  <span className="text-gray-600 uppercase">Threat Signature</span>
                                  <span className="text-red-500">BOT_FARM_BEHAVIOR</span>
                               </div>
                            </div>
                         </div>

                         <div className="p-6 bg-red-500/5 border border-red-500/10 rounded-xl">
                            <div className="flex items-center gap-3 text-red-500 mb-3">
                               <AlertTriangle className="w-5 h-5" />
                               <span className="text-[10px] font-black uppercase tracking-widest">Shedding Impact</span>
                            </div>
                            <p className="text-[11px] text-gray-500 leading-relaxed font-bold">
                               This subnet has been effectively blacklisted across all 5 regional gateways. <span className="text-white">42 potential Sybil heartbeats</span> were dropped in the last tick.
                            </p>
                         </div>
                      </div>
                   </div>

                   {/* Forensic Action Bar */}
                   <div className="mt-auto pt-8 border-t border-white/5 flex flex-col md:flex-row gap-6 items-center">
                      <div className="flex items-center gap-4 flex-1 bg-white/[0.02] border border-white/5 p-4 rounded-xl shadow-inner">
                         <Fingerprint className="w-8 h-8 text-gray-700" />
                         <p className="text-[11px] text-gray-500 leading-relaxed font-medium">
                           The automated risk score for <span className="text-white">{selectedThreat.ip}</span> has exceeded the 0.80 critical threshold. Permanent IP-level exclusion is recommended.
                         </p>
                      </div>
                      <div className="flex gap-4 w-full md:w-auto">
                         <button className="px-8 py-4 bg-red-600 text-white font-black text-xs uppercase tracking-widest hover:bg-red-500 transition-all rounded shadow-2xl flex items-center justify-center gap-2">
                            <ShieldX className="w-4 h-4" /> Blacklist Subnet
                         </button>
                         <button className="px-8 py-4 bg-white/5 border border-white/10 text-gray-600 font-black text-xs uppercase tracking-widest hover:text-white transition-all rounded">
                            Allow One-Time
                         </button>
                      </div>
                   </div>
                </div>
             ) : (
                <div className="h-full border-2 border-white/5 border-dashed rounded-2xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale transition-all">
                   <ShieldAlert className="w-20 h-20 text-gray-800 mb-8 animate-pulse" />
                   <h3 className="text-lg font-black text-gray-600 uppercase tracking-[0.3em] mb-3">Intel Station Ready</h3>
                   <p className="text-xs text-gray-800 font-bold uppercase tracking-widest max-w-sm">Select an ingress anomaly from the pulse stream to inspect external threat metadata and IP attribution.</p>
                </div>
             )}
          </div>

        </div>

      </main>

      {/* Global Security Footer */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Threat Ingress Watch Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Filtering the digital static to preserve biological trust."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] BLACKLIST_DEPTH: 84,201</span>
            <span>[*] ATTRIBUTION_ENGINE: v1.1</span>
            <span>[*] VERSION: v3.4.0</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
