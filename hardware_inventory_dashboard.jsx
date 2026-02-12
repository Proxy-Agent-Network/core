import React, { useState, useMemo } from 'react';
import { 
  Package, 
  Truck, 
  PlusCircle, 
  ClipboardList, 
  Settings, 
  ShieldCheck, 
  Box, 
  MapPin, 
  Activity, 
  RefreshCw, 
  Search, 
  Filter, 
  ArrowRight, 
  ChevronRight, 
  Info, 
  X,
  Plane,
  AlertTriangle,
  Fingerprint,
  Layers,
  Archive,
  MoreHorizontal
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HARDWARE INVENTORY DASHBOARD (v1.0)
 * "Foundation Logistics: Authorizing the physical scale of the fleet."
 * ----------------------------------------------------
 */

const App = () => {
  const [isProvisioning, setIsProvisioning] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Mock Hardware State (Reflecting core/ops/hardware_registry.py)
  const [units, setUnits] = useState([
    { id: 'SENTRY-JP-001', type: 'AIR', region: 'JP_EAST', status: 'IN_TRANSIT', carrier: 'DHL', tracking: '8829310', progress: 65, created: '2026-02-10' },
    { id: 'SENTRY-SG-005', type: 'ROAD', region: 'ASIA_SE', status: 'IN_TRANSIT', carrier: 'FEDEX', tracking: '992182', progress: 30, created: '2026-02-11' },
    { id: 'SENTRY-VA-042', type: 'STATIONARY', region: 'US_EAST', status: 'DEPLOYED', carrier: 'LOCAL', tracking: 'SIGN-OFF', progress: 100, created: '2026-01-15' },
    { id: 'SENTRY-LDN-012', type: 'ROAD', region: 'EU_WEST', status: 'IN_TRANSIT', carrier: 'UPS', tracking: '420115', progress: 85, created: '2026-02-09' },
    { id: 'SENTRY-BR-009', type: 'STATIONARY', region: 'LATAM', status: 'MANUFACTURED', carrier: 'PENDING', tracking: 'NONE', progress: 0, created: '2026-02-11' }
  ]);

  const [form, setForm] = useState({
    region: 'JP_EAST',
    carrier: 'DHL',
    tracking: '',
    unit_count: 1
  });

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const handleAuthorize = (e) => {
    e.preventDefault();
    setIsRefreshing(true);
    setTimeout(() => {
      const newUnit = {
        id: `SENTRY-${form.region}-${Math.floor(Math.random() * 900 + 100)}`,
        type: 'AIR',
        region: form.region,
        status: 'IN_TRANSIT',
        carrier: form.carrier,
        tracking: form.tracking || 'GEN-882-X',
        progress: 5,
        created: new Date().toISOString().split('T')[0]
      };
      setUnits([newUnit, ...units]);
      setIsProvisioning(false);
      setIsRefreshing(false);
    }, 1500);
  };

  const filteredUnits = useMemo(() => {
    return units.filter(u => 
      u.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
      u.region.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [units, searchQuery]);

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl shadow-2xl">
              <Archive className="w-8 h-8 text-amber-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Hardware Registry</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Logistics Command // Operational Tier: <span className="text-amber-500">FOUNDATION</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <button 
               onClick={() => setIsProvisioning(true)}
               className="flex items-center gap-3 px-6 py-2 bg-indigo-500 text-black font-black text-[10px] uppercase tracking-widest rounded hover:bg-indigo-400 transition-all shadow-xl"
             >
                <PlusCircle className="w-4 h-4" /> Authorize Shipment
             </button>
             <div className="h-10 w-px bg-white/10" />
             <button 
               onClick={handleRefresh}
               className={`p-3 border border-white/10 rounded hover:bg-white/10 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
             >
               <RefreshCw className="w-4 h-4 text-gray-500" />
             </button>
          </div>
        </header>

        {/* Fleet KPI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
           {[
             { label: 'Total Inventory', val: units.length, sub: 'UNITS', icon: Box, color: 'white' },
             { label: 'In-Transit', val: units.filter(u => u.status === 'IN_TRANSIT').length, sub: 'REINFORCEMENTS', icon: Truck, color: 'amber' },
             { label: 'Active Deployment', val: units.filter(u => u.status === 'DEPLOYED').length, sub: 'ONLINE', icon: ShieldCheck, color: 'green' },
             { label: 'Provision Rate', val: '+4.2%', sub: 'PER EPOCH', icon: Activity, color: 'indigo' }
           ].map((kpi, i) => (
             <div key={i} className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform">
                  <kpi.icon className="w-20 h-20 text-white" />
                </div>
                <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">{kpi.label}</span>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-black text-white tracking-tighter">{kpi.val}</span>
                  <span className={`text-[9px] font-black uppercase text-${kpi.color}-500`}>{kpi.sub}</span>
                </div>
             </div>
           ))}
        </div>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Main Manifest Table */}
          <div className="col-span-12 lg:col-span-9 bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
             <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-8">
                <div className="flex items-center gap-4">
                   <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                     <ClipboardList className="w-4 h-4 text-gray-500" /> Physical Manifest
                   </h3>
                   <div className="h-4 w-px bg-white/10" />
                   <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-700" />
                      <input 
                        type="text" 
                        placeholder="FILTER BY ID/REGION..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="bg-black border border-white/5 rounded py-1 pl-8 pr-4 text-[9px] text-white focus:outline-none focus:border-indigo-500/30 w-48 uppercase"
                      />
                   </div>
                </div>
                <span className="text-[9px] text-gray-600 font-bold uppercase tracking-widest">v1.0.2 STABLE</span>
             </div>

             <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                   <thead>
                      <tr className="bg-white/[0.01] border-b border-white/5">
                         <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest">Serial ID</th>
                         <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest">Target Hub</th>
                         <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest">Logistics</th>
                         <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest">Status</th>
                         <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest text-right">Progress</th>
                      </tr>
                   </thead>
                   <tbody className="divide-y divide-white/5">
                      {filteredUnits.map((u) => (
                        <tr key={u.id} className="group hover:bg-white/[0.01] transition-all">
                           <td className="p-6">
                              <div className="flex items-center gap-3">
                                 <div className="p-2 bg-white/5 border border-white/5 rounded">
                                    {u.type === 'AIR' ? <Plane className="w-3.5 h-3.5 text-indigo-400" /> : <Truck className="w-3.5 h-3.5 text-amber-500" />}
                                 </div>
                                 <span className="text-xs font-black text-white uppercase tracking-tighter group-hover:text-indigo-400 transition-colors">{u.id}</span>
                              </div>
                           </td>
                           <td className="p-6">
                              <div className="flex items-center gap-2">
                                 <MapPin className="w-3 h-3 text-gray-700" />
                                 <span className="text-[10px] font-bold text-gray-400 uppercase">{u.region}</span>
                              </div>
                           </td>
                           <td className="p-6">
                              <div className="flex flex-col">
                                 <span className="text-[9px] text-gray-700 font-black uppercase mb-0.5">{u.carrier}</span>
                                 <span className="text-[10px] text-white font-mono">{u.tracking}</span>
                              </div>
                           </td>
                           <td className="p-6">
                              <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded border ${
                                u.status === 'DEPLOYED' ? 'bg-green-500/10 border-green-500/20 text-green-500' :
                                u.status === 'IN_TRANSIT' ? 'bg-amber-500/10 border-amber-500/20 text-amber-500 animate-pulse' :
                                'bg-white/5 border-white/10 text-gray-500'
                              }`}>
                                 {u.status}
                              </span>
                           </td>
                           <td className="p-6">
                              <div className="flex flex-col items-end gap-2">
                                 <span className="text-[10px] font-black text-white">{u.progress}%</span>
                                 <div className="w-24 bg-white/5 h-1 rounded-full overflow-hidden">
                                    <div className={`${u.progress === 100 ? 'bg-green-500' : 'bg-indigo-500'} h-full opacity-60`} style={{ width: `${u.progress}%` }} />
                                 </div>
                              </div>
                           </td>
                        </tr>
                      ))}
                   </tbody>
                </table>
             </div>
             <button className="w-full py-4 text-[9px] font-black text-gray-700 hover:text-white uppercase tracking-[0.3em] border-t border-white/5 transition-all">
                Export Registry Dataset (CSV/A)
             </button>
          </div>

          {/* Sidebar Tools & Metadata */}
          <div className="col-span-12 lg:col-span-3 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-[0.02] group-hover:scale-110 transition-transform">
                   <Settings className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-6 flex items-center gap-2 relative z-10">
                   <Info className="w-3.5 h-3.5 text-indigo-500" /> Operational Context
                </h4>
                <p className="text-xs text-gray-500 leading-relaxed mb-8 italic relative z-10">
                   "Authorize new hardware deployments to restore regional SLA integrity. Binding a serial ID creates a pre-registered entry in the Reputation Oracle."
                </p>
                <div className="space-y-4 relative z-10">
                   <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-tighter">
                      <span className="text-gray-700">Audit Proof</span>
                      <span className="text-indigo-400 flex items-center gap-1 cursor-pointer hover:underline">
                         <Layers className="w-3 h-3" /> VERIFY_CHAIN
                      </span>
                   </div>
                </div>
             </div>

             <div className="p-6 border border-red-500/10 bg-red-500/5 rounded-xl">
                <div className="flex items-center gap-3 mb-4 text-red-500">
                   <AlertTriangle className="w-5 h-5" />
                   <h4 className="text-[10px] font-black uppercase tracking-widest leading-none">Tamper Watch</h4>
                </div>
                <p className="text-[11px] text-gray-500 leading-relaxed font-bold">
                   If a shipment exceeds 14 days in transit, the protocol automatically flags the unit as <span className="text-red-400">SUSPECT</span> and revokes the pre-binding token.
                </p>
             </div>

             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-6 flex flex-col gap-4">
                <h3 className="text-[10px] font-black text-white uppercase tracking-widest border-b border-white/5 pb-2">Carrier Performance</h3>
                {[
                  { name: 'DHL Express', score: '98.2%' },
                  { name: 'FedEx Global', score: '94.5%' },
                  { name: 'UPS Int.', score: '91.8%' }
                ].map((c, i) => (
                   <div key={i} className="flex justify-between items-center text-[10px] font-bold">
                      <span className="text-gray-500">{c.name}</span>
                      <span className="text-green-500">{c.score}</span>
                   </div>
                ))}
             </div>
          </div>

        </div>

      </main>

      {/* Provisioning Modal Overlay */}
      {isProvisioning && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
           <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl max-w-lg w-full p-10 shadow-[0_0_50px_rgba(0,0,0,1)] relative">
              <button 
                onClick={() => setIsProvisioning(false)} 
                className="absolute top-6 right-6 text-gray-700 hover:text-white transition-colors"
              >
                <X className="w-6 h-6" />
              </button>

              <div className="flex items-center gap-4 mb-10">
                 <div className="p-3 bg-indigo-500/10 rounded-xl border border-indigo-500/20">
                    <PlusCircle className="w-8 h-8 text-indigo-500" />
                 </div>
                 <div>
                    <h2 className="text-2xl font-black text-white uppercase tracking-tight">Authorize Shipment</h2>
                    <p className="text-[9px] text-gray-600 font-black uppercase tracking-widest">Spawn New Registry ID</p>
                 </div>
              </div>

              <form onSubmit={handleAuthorize} className="space-y-6">
                 <div className="grid grid-cols-2 gap-6">
                    <div>
                       <label className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Target Hub</label>
                       <select 
                         value={form.region}
                         onChange={(e) => setForm({...form, region: e.target.value})}
                         className="w-full bg-black border border-white/10 rounded p-3 text-xs text-white uppercase font-bold focus:border-indigo-500 transition-all outline-none"
                       >
                          <option value="JP_EAST">JP East (Tokyo)</option>
                          <option value="ASIA_SE">Asia SE (Singapore)</option>
                          <option value="US_EAST">US East (VA)</option>
                          <option value="EU_WEST">Europe (UK)</option>
                       </select>
                    </div>
                    <div>
                       <label className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Carrier</label>
                       <select 
                         value={form.carrier}
                         onChange={(e) => setForm({...form, carrier: e.target.value})}
                         className="w-full bg-black border border-white/10 rounded p-3 text-xs text-white uppercase font-bold focus:border-indigo-500 transition-all outline-none"
                       >
                          <option value="DHL">DHL Express</option>
                          <option value="FEDEX">FedEx</option>
                          <option value="UPS">UPS</option>
                       </select>
                    </div>
                 </div>

                 <div>
                    <label className="text-[9px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Tracking Number</label>
                    <input 
                      type="text" 
                      placeholder="e.g. 8829310"
                      value={form.tracking}
                      onChange={(e) => setForm({...form, tracking: e.target.value})}
                      className="w-full bg-black border border-white/10 rounded p-3 text-xs text-white font-mono focus:border-indigo-500 transition-all outline-none"
                      required
                    />
                 </div>

                 <div className="p-4 bg-indigo-500/5 border border-indigo-500/20 rounded-xl flex items-center gap-4">
                    <Fingerprint className="w-8 h-8 text-indigo-400" />
                    <p className="text-[10px] text-gray-500 leading-relaxed italic">
                       Signing this authorization with your Foundation Master Key will broadcast the intent to the Hub Discovery API.
                    </p>
                 </div>

                 <button 
                   type="submit"
                   disabled={isRefreshing}
                   className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-indigo-500 hover:text-white transition-all rounded shadow-xl flex items-center justify-center gap-3 disabled:opacity-20"
                 >
                   {isRefreshing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
                   {isRefreshing ? 'Broadcasting...' : 'Authorize Dispatch'}
                 </button>
              </form>
           </div>
        </div>
      )}

      {/* Global Status Footer */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Inventory Orchestrator Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Sync Block: 882932</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] REGISTRY_STATE: LOCKED</span>
            <span>[*] VERSION: v3.0.3</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
