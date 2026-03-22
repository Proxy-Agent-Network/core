import React, { useState, useMemo } from 'react';
import { 
  Truck, 
  Package, 
  ShieldCheck, 
  FileSearch, 
  Binary, 
  MapPin, 
  Globe, 
  RefreshCw, 
  History, 
  Activity, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  Lock, 
  Cpu, 
  Plane, 
  Layers, 
  ShieldAlert,
  Search,
  XCircle,
  FileText,
  Navigation,
  Box,
  Info
} from 'lucide-react';

/**
 * PROXY PROTOCOL - SHIPMENT AUDIT DASHBOARD (v1.0)
 * "Verifying the physical path of silicon trust."
 * ----------------------------------------------------
 */

const App = () => {
  const [selectedUnit, setSelectedUnit] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Mock Active Shipments (Linked to Hardware Registry)
  const [shipments] = useState([
    {
      id: "SENTRY-JP-001",
      status: "IN_TRANSIT",
      origin: "Foundation Factory (TW)",
      destination: "Tokyo, JP",
      carrier: "DHL",
      progress: 65,
      last_event: "IMPORT_SCAN - Narita",
      timestamp: "2026-02-12T04:12:00Z",
      risk_score: "NOMINAL"
    },
    {
      id: "SENTRY-SG-005",
      status: "IN_TRANSIT",
      origin: "Foundation Factory (TW)",
      destination: "Singapore, SG",
      carrier: "FEDEX",
      progress: 30,
      last_event: "DEPARTED_FACILITY - Taipei",
      timestamp: "2026-02-11T22:15:00Z",
      risk_score: "ELEVATED"
    },
    {
      id: "SENTRY-VA-042",
      status: "DELIVERED",
      origin: "Foundation Factory (TW)",
      destination: "Ashburn, US",
      carrier: "UPS",
      progress: 100,
      last_event: "SIGNED_BY_NODE - Ashburn",
      timestamp: "2026-02-10T14:30:00Z",
      risk_score: "VERIFIED"
    }
  ]);

  // Mock Forensic Chain for a selected unit
  const forensicChain = [
    { step: "FACTORY_SEED", location: "Taipei, TW", time: "2026-02-08 09:00", sig: "HSM_MASTER_ROOT", status: "OK" },
    { step: "EXPORT_CLEARANCE", location: "Taipei, TW", time: "2026-02-09 14:20", sig: "TW_CUSTOMS_API", status: "OK" },
    { step: "CARRIER_PICKUP", location: "Taipei, TW", time: "2026-02-09 18:00", sig: "DHL_WH_SEC", status: "OK" },
    { step: "IMPORT_SCAN", location: "Narita, JP", time: "2026-02-11 23:45", sig: "JP_CUSTOMS_API", status: "OK" },
    { step: "LAST_MILE_OUT", location: "Tokyo, JP", time: "2026-02-12 04:00", sig: "DHL_LOCAL_SIG", status: "OK" }
  ];

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1200);
  };

  const filteredShipments = useMemo(() => {
    return shipments.filter(s => 
      s.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.destination.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm, shipments]);

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-amber-500/30">
      
      {/* Background matrix pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl shadow-2xl">
              <Truck className="w-8 h-8 text-amber-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Shipment Audit</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Logistics Desk // Chain of Custody // Protocol <span className="text-amber-500">v3.3.3</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-700" />
                <input 
                  type="text" 
                  placeholder="SEARCH SERIAL..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="bg-[#0a0a0a] border border-white/5 rounded-lg py-2 pl-10 pr-4 text-xs text-white focus:outline-none focus:border-amber-500/30 w-48 uppercase"
                />
             </div>
             <button 
               onClick={handleRefresh}
               className={`p-2 border border-white/10 rounded hover:bg-white/10 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
             >
               <RefreshCw className="w-4 h-4 text-gray-500" />
             </button>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-8">
          {/* Active Unit List (Left Column) */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <Activity className="w-4 h-4 text-amber-500" /> Live Manifest
                   </h3>
                </div>

                <div className="divide-y divide-white/5">
                   {filteredShipments.map((unit) => (
                      <div 
                        key={unit.id} 
                        onClick={() => setSelectedUnit(unit)}
                        className={`p-6 hover:bg-white/[0.01] transition-all cursor-pointer group ${selectedUnit?.id === unit.id ? 'bg-amber-500/[0.03]' : ''}`}
                      >
                         <div className="flex justify-between items-start mb-4">
                            <div>
                               <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-amber-400 transition-colors">{unit.id}</span>
                               <p className="text-[9px] text-gray-600 font-bold uppercase mt-1">{unit.carrier} // {unit.destination}</p>
                            </div>
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${
                              unit.status === 'DELIVERED' ? 'bg-green-500/10 border-green-500/20 text-green-500' : 'bg-amber-500/10 border-amber-500/20 text-amber-500'
                            }`}>
                               {unit.status}
                            </span>
                         </div>
                         <div className="space-y-2">
                            <div className="flex justify-between items-center text-[8px] font-black text-gray-700 uppercase">
                               <span>Transit: {unit.progress}%</span>
                               <span className={unit.risk_score === 'CRITICAL' ? 'text-red-500' : 'text-gray-500'}>Risk: {unit.risk_score}</span>
                            </div>
                            <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                               <div className={`h-full ${unit.status === 'DELIVERED' ? 'bg-green-500' : 'bg-amber-500 animate-pulse'}`} style={{ width: `${unit.progress}%` }} />
                            </div>
                         </div>
                      </div>
                   ))}
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-indigo-500/5 rounded-xl shadow-inner relative overflow-hidden group">
                <div className="absolute -bottom-6 -right-6 opacity-[0.03] group-hover:scale-110 transition-transform">
                   <Lock className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5" /> Chain of Custody
                </h4>
                <p className="text-[11px] text-gray-500 leading-relaxed italic">
                   "A Proxy Sentry remains UN-ACTIVATED until its physical delivery event is confirmed by an HMAC-signed webhook from the carrier. This prevents pre-binding tokens from being compromised in transit."
                </p>
             </div>
          </div>

          {/* Forensic Audit View (Right Column) */}
          <div className="col-span-12 lg:col-span-8 flex flex-col h-full">
             {selectedUnit ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 shadow-2xl animate-in slide-in-from-right-4 duration-300 flex-1 flex flex-col gap-8">
                   <div className="flex justify-between items-start border-b border-white/5 pb-6">
                      <div>
                         <span className="text-[10px] text-amber-500 font-black uppercase tracking-[0.2em] block mb-1">Custody Manifest</span>
                         <h2 className="text-3xl font-black text-white tracking-tighter uppercase">{selectedUnit.id}</h2>
                      </div>
                      <button onClick={() => setSelectedUnit(null)} className="p-3 text-gray-600 hover:text-white transition-colors">
                         <XCircle className="w-6 h-6" />
                      </button>
                   </div>

                   {/* Geographical Path Visualizer */}
                   <div className="relative h-48 bg-black/40 border border-white/5 rounded-2xl overflow-hidden group">
                      <div className="absolute inset-0 opacity-10" 
                           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '20px 20px' }} />
                      <div className="absolute inset-0 flex items-center justify-center">
                         <Globe className="w-24 h-24 text-white/5 animate-spin-slow" />
                      </div>
                      <div className="absolute inset-0 flex items-center justify-between px-12">
                         <div className="flex flex-col items-center gap-2">
                            <div className="p-3 bg-white text-black rounded-lg shadow-xl"><Box className="w-4 h-4" /></div>
                            <span className="text-[9px] font-black uppercase text-gray-600">{selectedUnit.origin}</span>
                         </div>
                         <div className="flex-1 flex items-center justify-center px-4">
                            <div className="w-full h-px border-t-2 border-dashed border-amber-500/20 relative">
                               <div className="absolute top-1/2 left-0 h-1 bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)] transition-all duration-1000" style={{ width: `${selectedUnit.progress}%` }} />
                               <div className="absolute top-1/2 left-0 -translate-y-1/2 group-hover:translate-x-full transition-all duration-[2000ms]" style={{ left: `${selectedUnit.progress}%` }}>
                                  <Plane className="w-4 h-4 text-amber-500 -rotate-45" />
                               </div>
                            </div>
                         </div>
                         <div className="flex flex-col items-center gap-2">
                            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg"><MapPin className="w-4 h-4 text-amber-500" /></div>
                            <span className="text-[9px] font-black uppercase text-gray-600">{selectedUnit.destination}</span>
                         </div>
                      </div>
                   </div>

                   {/* Attestation Chain */}
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                      <div className="space-y-6">
                         <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest flex items-center gap-2 border-b border-white/5 pb-2">
                            <Layers className="w-3.5 h-3.5 text-indigo-500" /> Signature Chain
                         </h4>
                         <div className="relative space-y-8">
                            <div className="absolute left-[11px] top-2 bottom-2 w-px bg-white/5" />
                            {forensicChain.map((step, i) => (
                               <div key={i} className="flex items-start gap-6 relative z-10">
                                  <div className={`w-6 h-6 rounded-full border border-white/10 flex items-center justify-center transition-all ${
                                    i === forensicChain.length - 1 ? 'bg-amber-500 border-amber-400 text-black shadow-[0_0_15px_rgba(245,158,11,0.5)]' : 'bg-black text-gray-700'
                                  }`}>
                                     <CheckCircle2 className="w-3 h-3" />
                                  </div>
                                  <div>
                                     <p className="text-[11px] text-white font-black uppercase tracking-tighter mb-0.5">{step.step}</p>
                                     <div className="flex items-center gap-2 text-[9px] text-gray-600 font-bold uppercase tracking-widest">
                                        <span>{step.location}</span>
                                        <span>|</span>
                                        <span>{step.time}</span>
                                     </div>
                                  </div>
                               </div>
                            ))}
                         </div>
                      </div>

                      <div className="space-y-6">
                         <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest flex items-center gap-2 border-b border-white/5 pb-2">
                            <FileSearch className="w-3.5 h-3.5 text-amber-500" /> Forensic Manifest
                         </h4>
                         <div className="space-y-4">
                            <div className="p-4 bg-black border border-white/5 rounded-xl space-y-4">
                               <div>
                                  <span className="text-[8px] text-gray-700 font-black uppercase block mb-1">Carrier Signal Proof</span>
                                  <code className="text-[10px] text-indigo-400 break-all font-mono">HMAC_SHA256:0x8A2E...F91C</code>
                               </div>
                               <div className="pt-3 border-t border-white/5">
                                  <span className="text-[8px] text-gray-700 font-black uppercase block mb-1">Expected TPM Fingerprint</span>
                                  <code className="text-[10px] text-gray-500 break-all font-mono">8A2E1C3B...D2A1</code>
                               </div>
                            </div>
                            <div className="p-4 bg-amber-500/5 border border-amber-500/10 rounded-xl">
                               <div className="flex items-center gap-3 text-amber-500 mb-2">
                                  <ShieldAlert className="w-3.5 h-3.5" />
                                  <span className="text-[9px] font-black uppercase">Geofence Policy</span>
                               </div>
                               <p className="text-[10px] text-gray-500 leading-relaxed font-bold">
                                 Unit activation only permitted within <span className="text-white">500m</span> of the verified import coordinate.
                               </p>
                            </div>
                         </div>
                      </div>
                   </div>

                   {/* Audit Action Bar */}
                   <div className="mt-auto pt-8 border-t border-white/5 flex flex-col md:flex-row gap-6 items-center">
                      <div className="flex items-center gap-4 flex-1 bg-white/[0.02] border border-white/5 p-4 rounded-xl">
                         <Binary className="w-8 h-8 text-gray-700" />
                         <p className="text-[11px] text-gray-500 leading-relaxed font-medium">
                           The attestation chain for <span className="text-white">{selectedUnit.id}</span> is complete. Cryptographic residency proof is pending node activation.
                         </p>
                      </div>
                      <div className="flex gap-4 w-full md:w-auto">
                         <button className="px-8 py-4 bg-white text-black font-black text-xs uppercase tracking-widest hover:bg-amber-500 transition-all rounded shadow-xl flex items-center gap-2">
                            <FileText className="w-4 h-4" /> Export Report
                         </button>
                         <button className="px-8 py-4 bg-white/5 border border-white/10 text-gray-600 font-black text-xs uppercase tracking-widest hover:text-red-500 hover:border-red-500/40 transition-all rounded">
                            Flag Discrepancy
                         </button>
                      </div>
                   </div>
                </div>
             ) : (
                <div className="h-full border-2 border-white/5 border-dashed rounded-2xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale">
                   <Package className="w-20 h-20 text-gray-800 mb-8 animate-pulse" />
                   <h3 className="text-lg font-black text-gray-600 uppercase tracking-[0.3em] mb-3">Audit Station Ready</h3>
                   <p className="text-xs text-gray-800 font-bold uppercase tracking-widest max-w-sm">Select a hardware unit from the live manifest to audit its physical chain of custody and signature history.</p>
                </div>
             )}
          </div>

        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Logistics Link Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Attestation Standard: HMAC-SHA256</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] FACTORY_SIG: OK</span>
            <span>[*] BORDER_SYNC: ACTIVE</span>
            <span>[*] VERSION: v3.3.3</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 20s linear infinite;
        }
      `}} />

    </div>
  );
};

export default App;
