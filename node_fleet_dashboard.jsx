import React, { useState, useEffect } from 'react';
import { 
  Server, Activity, MapPin, Wifi, AlertTriangle, 
  Terminal, ShieldCheck, Cpu, Power, RefreshCw, 
  Settings, Search, Filter, ArrowUpRight, 
  MoreHorizontal, Battery, Signal, Lock, Plus, Download, X
} from 'lucide-react';

const FleetDashboard = () => {
  const [selectedNode, setSelectedNode] = useState(null);
  const [filter, setFilter] = useState('ALL');
  const [isProvisioning, setIsProvisioning] = useState(false);
  const [time, setTime] = useState(new Date());

  // Provisioning State
  const [newConfig, setNewConfig] = useState({
    tier: 'TIER_1_DIGITAL',
    network: 'MAINNET',
    lnd_host: '127.0.0.1:10009',
    node_name: 'proxy-node-01'
  });

  // Fleet State
  const [fleetStats, setFleetStats] = useState({
    total_nodes: 42,
    online_count: 38,
    total_earnings_24h: 125000,
    avg_uptime: 99.9,
    global_health: 96
  });

  const [nodes, setNodes] = useState([
    { id: "NODE-US-AZ-001", status: "ONLINE", region: "US_WEST", ip: "192.168.1.101", uptime: "14d 2h", earnings: 4200, temp: 45, cpu: 12, task: "IDLE", tpm: "LOCKED" },
    { id: "NODE-US-AZ-002", status: "ONLINE", region: "US_WEST", ip: "192.168.1.102", uptime: "14d 2h", earnings: 3100, temp: 48, cpu: 34, task: "SMS_VERIFY", tpm: "LOCKED" },
    { id: "NODE-US-AZ-003", status: "WARNING", region: "US_WEST", ip: "192.168.1.103", uptime: "2d 4h", earnings: 800, temp: 82, cpu: 90, task: "COOLDOWN", tpm: "LOCKED" },
    { id: "NODE-EU-LDN-001", status: "ONLINE", region: "EU_WEST", ip: "10.0.4.50", uptime: "45d 12h", earnings: 12500, temp: 51, cpu: 22, task: "LEGAL_SIGN", tpm: "LOCKED" },
    { id: "NODE-EU-LDN-002", status: "OFFLINE", region: "EU_WEST", ip: "10.0.4.51", uptime: "0m", earnings: 0, temp: 0, cpu: 0, task: "NONE", tpm: "UNKNOWN" },
    { id: "NODE-SG-SIN-001", status: "ONLINE", region: "ASIA_SE", ip: "172.16.0.5", uptime: "5d 1h", earnings: 8900, temp: 55, cpu: 45, task: "KYC_VIDEO", tpm: "LOCKED" },
  ]);

  // Live Heartbeat Simulation
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    
    const heartbeat = setInterval(() => {
      setNodes(currentNodes => currentNodes.map(node => {
        if (node.status === 'OFFLINE') return node;
        
        // Fluctuate metrics to simulate live hardware telemetry
        const newTemp = Math.max(30, Math.min(90, node.temp + Math.floor(Math.random() * 5) - 2));
        const newCpu = Math.max(5, Math.min(100, node.cpu + Math.floor(Math.random() * 10) - 5));
        const newEarnings = node.earnings + (Math.random() > 0.8 ? 50 : 0); // Occasional payout
        
        // Auto-flag overheating
        let newStatus = node.status;
        if (newTemp > 80) newStatus = 'WARNING';
        else if (newTemp < 75 && node.status === 'WARNING') newStatus = 'ONLINE';

        return { ...node, temp: newTemp, cpu: newCpu, earnings: newEarnings, status: newStatus };
      }));
      
      // Update fleet totals
      setFleetStats(prev => ({
        ...prev,
        total_earnings_24h: prev.total_earnings_24h + Math.floor(Math.random() * 100)
      }));

    }, 3000);

    return () => {
      clearInterval(timer);
      clearInterval(heartbeat);
    };
  }, []);

  const filteredNodes = nodes.filter(n => {
    if (filter === 'ALL') return true;
    return n.status === filter;
  });

  const getStatusColor = (status) => {
    switch(status) {
      case 'ONLINE': return 'text-green-500 bg-green-500/10 border-green-500/20';
      case 'WARNING': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      case 'OFFLINE': return 'text-red-500 bg-red-500/10 border-red-500/20';
      default: return 'text-gray-500 bg-gray-500/10 border-gray-500/20';
    }
  };

  const handleDownloadConfig = () => {
    const yamlContent = `
version: "3.8"
services:
  ${newConfig.node_name}:
    image: proxy-protocol/node:v1.0
    restart: unless-stopped
    environment:
      - PROXY_ENV=production
      - NODE_TIER=${newConfig.tier}
      - LND_HOST=${newConfig.lnd_host}
      - NETWORK=${newConfig.network}
    ${newConfig.tier !== 'TIER_1_DIGITAL' ? `devices:
      - "/dev/tpm0:/dev/tpm0"
      - "/dev/video0:/dev/video0"` : ''}
    network_mode: "host"
    `;
    
    const blob = new Blob([yamlContent], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'docker-compose.yml';
    link.click();
    setIsProvisioning(false);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-6 selection:bg-green-500/30">
      
      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-white/10 pb-6">
        <div className="flex items-center gap-4">
          <div className="p-2 bg-green-500/10 border border-green-500/20 rounded">
            <Server className="w-6 h-6 text-green-500" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">PROXY FLEET COMMAND</h1>
            <p className="text-[10px] uppercase tracking-widest text-gray-500 flex items-center gap-2">
              v1.2 // UPLINK_ACTIVE // {time.toLocaleTimeString()}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-6">
            <button 
                onClick={() => setIsProvisioning(true)}
                className="flex items-center gap-2 px-4 py-2 bg-green-500 text-black font-bold text-xs uppercase tracking-widest rounded hover:bg-green-400 transition-all shadow-[0_0_15px_rgba(34,197,94,0.3)]"
            >
                <Plus className="w-4 h-4" /> Provision Node
            </button>
          <div className="h-8 w-px bg-white/10"></div>
          <div className="text-right">
            <span className="text-[9px] uppercase tracking-widest text-gray-500 block">Fleet Revenue</span>
            <span className="text-lg font-bold text-white">{fleetStats.total_earnings_24h.toLocaleString()} <span className="text-xs text-green-500">SATS</span></span>
          </div>
        </div>
      </header>

      {/* Provisioning Modal */}
      {isProvisioning && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
            <div className="bg-[#0a0a0a] border border-white/20 rounded-lg w-full max-w-lg shadow-2xl relative">
                <button onClick={() => setIsProvisioning(false)} className="absolute top-4 right-4 text-gray-500 hover:text-white"><X className="w-5 h-5" /></button>
                
                <div className="p-6 border-b border-white/10">
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                        <Cpu className="w-5 h-5 text-green-500" /> Configure New Node
                    </h2>
                    <p className="text-xs text-gray-500 mt-1">Generate a Docker Compose file for instant deployment.</p>
                </div>

                <div className="p-6 space-y-4">
                    <div>
                        <label className="block text-[10px] uppercase font-bold text-gray-500 mb-1">Node Name</label>
                        <input 
                            type="text" 
                            value={newConfig.node_name}
                            onChange={(e) => setNewConfig({...newConfig, node_name: e.target.value})}
                            className="w-full bg-black border border-white/10 rounded p-2 text-sm text-white focus:border-green-500/50 outline-none transition-colors"
                        />
                    </div>
                    <div>
                        <label className="block text-[10px] uppercase font-bold text-gray-500 mb-1">Operational Tier</label>
                        <select 
                            value={newConfig.tier}
                            onChange={(e) => setNewConfig({...newConfig, tier: e.target.value})}
                            className="w-full bg-black border border-white/10 rounded p-2 text-sm text-white focus:border-green-500/50 outline-none transition-colors"
                        >
                            <option value="TIER_1_DIGITAL">Tier 1: Digital Only (No Hardware)</option>
                            <option value="TIER_2_PHYSICAL">Tier 2: Physical (TPM + Camera)</option>
                            <option value="TIER_3_LEGAL">Tier 3: Legal (TPM + Notary)</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-[10px] uppercase font-bold text-gray-500 mb-1">LND Host</label>
                        <input 
                            type="text" 
                            value={newConfig.lnd_host}
                            onChange={(e) => setNewConfig({...newConfig, lnd_host: e.target.value})}
                            className="w-full bg-black border border-white/10 rounded p-2 text-sm text-white focus:border-green-500/50 outline-none transition-colors"
                        />
                    </div>
                </div>

                <div className="p-6 border-t border-white/10 bg-white/[0.02] flex justify-end gap-3">
                    <button onClick={() => setIsProvisioning(false)} className="px-4 py-2 text-xs font-bold text-gray-400 hover:text-white transition-colors">Cancel</button>
                    <button onClick={handleDownloadConfig} className="flex items-center gap-2 px-4 py-2 bg-green-500 text-black text-xs font-bold uppercase rounded hover:bg-green-400 transition-all">
                        <Download className="w-4 h-4" /> Download Config
                    </button>
                </div>
            </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left Column: Fleet Grid */}
        <div className={`col-span-12 ${selectedNode ? 'lg:col-span-8' : 'lg:col-span-12'} transition-all duration-300`}>
          <div className="flex justify-between items-center mb-6">
            <div className="flex gap-2">
              {['ALL', 'ONLINE', 'WARNING', 'OFFLINE'].map(f => (
                <button 
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1.5 rounded text-[10px] font-bold uppercase tracking-wider border ${
                    filter === f ? 'bg-white/10 text-white border-white/20' : 'bg-transparent text-gray-600 border-transparent hover:text-gray-400'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-2 bg-[#0a0a0a] border border-white/10 rounded px-3 py-1.5">
              <Search className="w-3 h-3 text-gray-500" />
              <input type="text" placeholder="Search Node ID..." className="bg-transparent border-none focus:outline-none text-xs text-white w-48" />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filteredNodes.map(node => (
              <div 
                key={node.id}
                onClick={() => setSelectedNode(node)}
                className={`p-4 rounded-lg border cursor-pointer transition-all hover:bg-white/[0.02] relative overflow-hidden group ${
                  selectedNode?.id === node.id ? 'border-green-500/50 bg-green-500/[0.02]' : 'bg-[#0a0a0a] border-white/5 hover:border-white/20'
                }`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${node.status === 'ONLINE' ? 'bg-green-500 animate-pulse' : node.status === 'WARNING' ? 'bg-yellow-500' : 'bg-red-500'}`} />
                    <span className="text-xs font-bold text-gray-200">{node.id}</span>
                  </div>
                  <MoreHorizontal className="w-4 h-4 text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <div className="grid grid-cols-2 gap-y-3 gap-x-2 text-[10px]">
                  <div><span className="text-gray-600 block mb-0.5">REGION</span><span className="text-gray-400 font-bold">{node.region}</span></div>
                  <div className="text-right"><span className="text-gray-600 block mb-0.5">TEMP</span><span className={`${node.temp > 80 ? 'text-red-500' : 'text-green-500'}`}>{node.temp}°C</span></div>
                  <div><span className="text-gray-600 block mb-0.5">TASK</span><span className="text-white bg-white/5 px-1.5 py-0.5 rounded">{node.task}</span></div>
                  <div className="text-right"><span className="text-gray-600 block mb-0.5">EARNINGS</span><span className="text-white">{node.earnings}</span></div>
                </div>
                {/* Live Activity Bar */}
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-white/5">
                  <div className={`h-full ${node.status === 'ONLINE' ? 'bg-green-500' : 'bg-gray-700'}`} style={{ width: `${node.cpu}%`, transition: 'width 1s ease-in-out' }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Node Detail View */}
        {selectedNode && (
          <aside className="col-span-12 lg:col-span-4 animate-in slide-in-from-right duration-300">
            <div className="bg-[#0a0a0a] border border-white/10 rounded-lg h-full flex flex-col sticky top-6">
              
              <div className="p-6 border-b border-white/10 flex justify-between items-start bg-white/[0.01]">
                <div>
                  <h2 className="text-lg font-bold text-white mb-1">{selectedNode.id}</h2>
                  <div className="flex gap-2">
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold border ${getStatusColor(selectedNode.status)}`}>{selectedNode.status}</span>
                    <span className="text-[9px] px-1.5 py-0.5 rounded font-bold border border-blue-500/20 text-blue-400 bg-blue-500/10">{selectedNode.tpm}</span>
                  </div>
                </div>
                <button onClick={() => setSelectedNode(null)} className="text-gray-600 hover:text-white transition-colors"><XCircle className="w-5 h-5" /></button>
              </div>

              <div className="p-6 space-y-6 flex-1 overflow-y-auto">
                <div className="space-y-3">
                  <h3 className="text-[10px] text-gray-500 uppercase font-bold tracking-widest flex items-center gap-2"><Activity className="w-3 h-3" /> Live Telemetry</h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-black p-3 rounded border border-white/5"><span className="text-gray-500 text-[10px] block mb-1">CPU Load</span><div className="w-full bg-gray-800 h-1 rounded mb-1"><div className="bg-green-500 h-full transition-all duration-500" style={{ width: `${selectedNode.cpu}%` }}></div></div><span className="text-white text-xs">{selectedNode.cpu}%</span></div>
                    <div className="bg-black p-3 rounded border border-white/5"><span className="text-gray-500 text-[10px] block mb-1">Memory</span><div className="w-full bg-gray-800 h-1 rounded mb-1"><div className="bg-blue-500 h-full" style={{ width: '68%' }}></div></div><span className="text-white text-xs">68%</span></div>
                    <div className="bg-black p-3 rounded border border-white/5"><span className="text-gray-500 text-[10px] block mb-1">Network</span><span className="text-white text-xs flex items-center gap-1"><Signal className="w-3 h-3 text-green-500" /> Stable</span></div>
                    <div className="bg-black p-3 rounded border border-white/5"><span className="text-gray-500 text-[10px] block mb-1">Voltage</span><span className="text-white text-xs flex items-center gap-1"><Battery className="w-3 h-3 text-green-500" /> 5.1V</span></div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="text-[10px] text-gray-500 uppercase font-bold tracking-widest flex items-center gap-2"><Globe className="w-3 h-3" /> Network Identity</h3>
                  <div className="bg-black p-4 rounded border border-white/5 space-y-2 text-[11px] mono">
                    <div className="flex justify-between"><span className="text-gray-500">IP Address</span><span className="text-gray-300">{selectedNode.ip}</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">Jurisdiction</span><span className="text-gray-300">{selectedNode.region}</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">Uptime</span><span className="text-green-500">{selectedNode.uptime}</span></div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-white flex items-center gap-2"><Lock className="w-3 h-3 text-blue-500" /> Security Module</h3>
                  <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded text-[10px] text-blue-300"><p className="mb-2">TPM 2.0 Integrity Verified.</p><p>PCR 0-7 hashes match Golden State whitelist.</p></div>
                </div>
              </div>

              <div className="p-6 border-t border-white/10 bg-white/[0.02]">
                <div className="grid grid-cols-2 gap-3">
                  <button className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 py-2 rounded text-[10px] font-bold uppercase transition-all"><RefreshCw className="w-3 h-3" /> Reboot</button>
                  <button className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 py-2 rounded text-[10px] font-bold uppercase transition-all"><Terminal className="w-3 h-3" /> SSH Console</button>
                  <button className="col-span-2 flex items-center justify-center gap-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-500 py-3 rounded text-[10px] font-black uppercase transition-all"><Power className="w-3 h-3" /> Emergency Shutdown</button>
                </div>
              </div>
            </div>
          </aside>
        )}
      </div>
    </div>
  );
};

export default FleetDashboard;
