import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  ShieldCheck, 
  Fingerprint, 
  Activity, 
  RefreshCw, 
  Lock, 
  Binary, 
  Layers, 
  Terminal, 
  Info, 
  Globe, 
  Search, 
  Filter, 
  ChevronRight, 
  Zap, 
  AlertTriangle, 
  CheckCircle2, 
  FileCheck2,
  HardDrive,
  Network,
  XCircle,
  Database,
  ArrowRight,
  ShieldAlert
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HARDWARE AUDIT DASHBOARD (v1.0)
 * "Visualizing the Birth of a Node: Silicon Verification at Scale."
 * ---------------------------------------------------------------
 */

const App = () => {
  const [lastSync, setLastSync] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedUnit, setSelectedUnit] = useState(null);

  // Mock Fleet Enrollment Data (Reflecting core/ops/hardware_audit_api.py)
  const [units] = useState([
    { 
      id: "SENTRY-JP-001", 
      status: "VERIFIED", 
      region: "JP_EAST", 
      tpm_model: "Infineon SLB9670", 
      pcr_status: "NOMINAL", 
      timestamp: "2026-02-12T00:15:00Z",
      ak_handle: "0x81010002",
      trust_score: 100
    },
    { 
      id: "SENTRY-VA-099", 
      status: "ENROLLING", 
      region: "US_EAST", 
      tpm_model: "Infineon SLB9670", 
      pcr_status: "AUDITING", 
      timestamp: "2026-02-12T01:04:22Z",
      ak_handle: "PENDING",
      trust_score: 0
    },
    { 
      id: "SENTRY-LDN-012", 
      status: "VERIFIED", 
      region: "EU_WEST", 
      tpm_model: "Infineon SLB9670", 
      pcr_status: "NOMINAL", 
      timestamp: "2026-02-11T22:45:00Z",
      ak_handle: "0x81010002",
      trust_score: 100
    }
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
      
      {/* Background Decorative Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header: Foundation Engineering Desk */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-[0_0_20px_rgba(99,102,241,0.1)]">
              <Cpu className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Hardware Auditor</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Foundation Tech-Ops // Node Enrollment // Protocol <span className="text-indigo-400">v3.2.8</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Fleet Integrity</span>
                   <span className="text-xl font-black text-green-500 tracking-tighter">100% SECURE</span>
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

        <div className="grid grid-cols-12 gap-8">
          
          {/* Active Enrollment Stream (Left Column) */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <Activity className="w-4 h-4 text-indigo-500" /> Birth Events
                   </h3>
                   <span className="text-[9px] text-gray-700 font-bold uppercase tracking-widest">Real-time Hook</span>
                </div>

                <div className="divide-y divide-white/5">
                   {units.map((unit) => (
                      <div 
                        key={unit.id} 
                        onClick={() => setSelectedUnit(unit)}
                        className={`p-6 hover:bg-white/[0.01] transition-all cursor-pointer group ${selectedUnit?.id === unit.id ? 'bg-indigo-500/[0.03]' : ''}`}
                      >
                         <div className="flex justify-between items-start mb-4">
                            <div>
                               <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-indigo-400 transition-colors">{unit.id}</span>
                               <p className="text-[9px] text-gray-600 font-bold uppercase mt-1">Model: {unit.tpm_model}</p>
                            </div>
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${unit.status === 'VERIFIED' ? 'bg-green-500/10 border-green-500/20 text-green-500' : 'bg-amber-500/10 border-amber-500/20 text-amber-500 animate-pulse'}`}>
                               {unit.status}
                            </span>
                         </div>
                         <div className="flex justify-between items-center mt-4 text-[9px] font-black text-gray-700 uppercase tracking-tighter">
                            <span className="flex items-center gap-1.5"><Globe className="w-3 h-3" /> {unit.region}</span>
                            <span>{new Date(unit.timestamp).toLocaleTimeString()}</span>
                         </div>
                      </div>
                   ))}
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-indigo-500/5 rounded-xl shadow-inner relative overflow-hidden group">
                <div className="absolute -bottom-6 -right-6 opacity-[0.03] group-hover:scale-110 transition-transform">
                   <ShieldCheck className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5" /> Residency Policy
                </h4>
                <p className="text-[11px] text-gray-500 leading-relaxed italic">
                   "Identity verification requires a successful ActivateCredential challenge, mathematically proving that the Attestation Key (AK) is resident in the same silicon chip as the Endorsement Key (EK)."
                </p>
             </div>
          </div>

          {/* Forensic Inspection View (Right Column) */}
          <div className="col-span-12 lg:col-span-8 flex flex-col h-full">
             {selectedUnit ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 shadow-2xl animate-in slide-in-from-right-4 duration-300 flex-1 flex flex-col gap-10">
                   <div className="flex justify-between items-start border-b border-white/5 pb-6">
                      <div>
                         <span className="text-[10px] text-indigo-400 font-black uppercase tracking-[0.2em] block mb-1">Silicon Fingerprint</span>
                         <h2 className="text-3xl font-black text-white tracking-tighter uppercase">{selectedUnit.id}</h2>
                      </div>
                      <button onClick={() => setSelectedUnit(null)} className="p-3 text-gray-600 hover:text-white transition-colors">
                         <XCircle className="w-6 h-6" />
                      </button>
                   </div>

                   {/* Hardware Integrity Grid */}
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div className="space-y-6">
                         <div>
                            <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                               <Fingerprint className="w-3.5 h-3.5 text-indigo-500" /> Certificate Chain (EK)
                            </h4>
                            <div className="space-y-3">
                               {[
                                 { label: 'Manufacturer Root', val: 'Infineon Trusted Root CA', status: 'OK' },
                                 { label: 'Device ID', val: 'OPTIGA™ SLB 9670 V1.0', status: 'OK' },
                                 { label: 'AK-to-EK Binding', val: 'HARDWARE_SEALED', status: selectedUnit.status === 'VERIFIED' ? 'OK' : 'PENDING' }
                               ].map((step, i) => (
                                 <div key={i} className="flex justify-between items-center p-4 bg-black border border-white/5 rounded-lg group hover:border-indigo-500/30 transition-all">
                                    <div>
                                       <span className="text-[9px] text-gray-700 font-black uppercase block">{step.label}</span>
                                       <span className="text-xs font-bold text-gray-400">{step.val}</span>
                                    </div>
                                    <ShieldCheck className={`w-4 h-4 ${step.status === 'OK' ? 'text-green-500' : 'text-gray-800'}`} />
                                 </div>
                               ))}
                            </div>
                         </div>
                      </div>

                      <div className="space-y-6">
                         <div>
                            <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                               <Binary className="w-3.5 h-3.5 text-indigo-500" /> PCR Integrity Whitelist
                            </h4>
                            <div className="bg-black border border-white/5 rounded-xl p-6 font-mono text-[10px] space-y-4">
                               <div className="flex justify-between items-center">
                                  <span className="text-gray-600 uppercase">PCR 0 (Firmware)</span>
                                  <span className="text-green-500">e3b0c442...</span>
                               </div>
                               <div className="flex justify-between items-center">
                                  <span className="text-gray-600 uppercase">PCR 1 (Hardware Config)</span>
                                  <span className="text-green-500">8a2e1c3b...</span>
                               </div>
                               <div className="flex justify-between items-center">
                                  <span className="text-gray-600 uppercase">PCR 7 (Secure Boot)</span>
                                  <span className={selectedUnit.pcr_status === 'NOMINAL' ? 'text-green-500' : 'text-amber-500 animate-pulse'}>
                                    {selectedUnit.pcr_status === 'NOMINAL' ? 'f91c3b2e...' : 'AUDITING_IN_RAM'}
                                  </span>
                               </div>
                            </div>
                            <div className="mt-4 p-4 bg-indigo-500/5 border border-indigo-500/10 rounded-lg flex items-center gap-3">
                               <Info className="w-4 h-4 text-indigo-400 shrink-0" />
                               <p className="text-[9px] text-gray-500 leading-relaxed uppercase font-black">
                                 Integrity matched against <span className="text-white">"Golden State"</span> manifest 2026.02.10
                               </p>
                            </div>
                         </div>
                      </div>
                   </div>

                   {/* Audit Action Bar */}
                   <div className="mt-auto pt-8 border-t border-white/5 flex flex-col md:flex-row gap-6 items-center">
                      <div className="flex items-center gap-4 flex-1 bg-indigo-500/5 border border-indigo-500/10 p-4 rounded-xl">
                         <Layers className="w-10 h-10 text-indigo-500 shrink-0" />
                         <p className="text-[11px] text-gray-500 leading-relaxed font-bold">
                           Finalizing enrollment will anchor this hardware ID to the global reputation registry. This unit will then be eligible for <span className="text-white uppercase tracking-widest">Tier 2 Verification</span> tasks.
                         </p>
                      </div>
                      <div className="flex gap-4 w-full md:w-auto">
                         <button 
                           className="px-8 py-5 bg-indigo-600 text-white font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-500 transition-all rounded shadow-2xl flex items-center justify-center gap-3 whitespace-nowrap disabled:opacity-20"
                           disabled={selectedUnit.status === 'VERIFIED'}
                         >
                            <FileCheck2 className="w-4 h-4" />
                            Finalize Enrollment
                         </button>
                         <button 
                           className="px-8 py-5 bg-white/5 border border-white/10 text-gray-500 font-black text-xs uppercase tracking-widest hover:text-red-500 hover:border-red-500/50 transition-all rounded"
                         >
                            Deny Silicon
                         </button>
                      </div>
                   </div>
                </div>
             ) : (
                <div className="h-full border-2 border-white/5 border-dashed rounded-2xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale">
                   <HardDrive className="w-20 h-20 text-gray-800 mb-8 animate-pulse" />
                   <h3 className="text-lg font-black text-gray-600 uppercase tracking-[0.3em] mb-3">Audit Station Ready</h3>
                   <p className="text-xs text-gray-800 font-bold uppercase tracking-widest max-w-sm">Select a pending unit from the birth stream to initiate forensic silicon validation and PCR integrity checks.</p>
                </div>
             )}
          </div>

        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Hardware Auditor v1.0 Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Silicon identity is the anchor of biological trust."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] EK_VALIDATION: ON</span>
            <span>[*] PCR_ENFORCEMENT: STRICT</span>
            <span>[*] VERSION: v3.2.8</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
