import React, { useState, useMemo } from 'react';
import { 
  History, 
  Search, 
  Cpu, 
  RotateCcw, 
  ShieldCheck, 
  Trash2, 
  Activity, 
  RefreshCw, 
  Clock, 
  Binary, 
  ChevronRight, 
  ArrowRight, 
  Info, 
  Lock, 
  Database, 
  HardDrive, 
  Fingerprint, 
  XCircle, 
  Zap, 
  CheckCircle2, 
  FileText,
  MapPin,
  Layers,
  Thermometer
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HARDWARE LIFECYCLE LEDGER (v1.0)
 * "Cradle-to-Grave silicon forensics."
 * ----------------------------------------------------
 */

const App = () => {
  const [serialQuery, setSerialQuery] = useState('');
  const [activeUnit, setActiveUnit] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  // Mock Lifecycle History (Aggregated from Lifecycle API & Hardware Registry)
  const mockLifecycleData = {
    'SENTRY-VA-042': {
      id: 'SENTRY-VA-042',
      born: '2025-11-14',
      status: 'ACTIVE',
      current_rep: 982,
      total_tasks: 9840,
      region: 'US_EAST',
      events: [
        { type: 'FACTORY_PROVISION', date: '2025-11-14 09:00', location: 'Taipei, TW', sig: 'HSM_MASTER_01', detail: 'Initial PCR Whitelist Generated' },
        { type: 'INITIAL_CEREMONY', date: '2026-01-15 14:22', location: 'Ashburn, US', sig: 'AK_0x81010001', detail: 'Primary Identity Key Sealed' },
        { type: 'JURISDICTION_LOCK', date: '2026-01-15 15:00', location: 'Ashburn, US', sig: 'GEO_ORACLE', detail: 'Geofence bound to 39.7459, -75.5467' },
        { type: 'KEY_ROTATION', date: '2026-02-01 10:12', location: 'Ashburn, US', sig: 'AK_0x81010002', detail: 'Entropy refresh triggered (Task 5k limit)' },
        { type: 'HEALTH_CHECK', date: '2026-02-12 04:30', location: 'Ashburn, US', sig: 'DAEMON_PULSE', detail: 'PCR 0,1,7 Integrity Verified (NOMINAL)' }
      ]
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setIsSearching(true);
    setTimeout(() => {
      setActiveUnit(mockLifecycleData[serialQuery.toUpperCase()] || null);
      setIsSearching(false);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30">
      
      {/* Background matrix pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl mx-auto relative z-10 space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
              <History className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none text-glow">Lifecycle Ledger</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Silicon Provenance // Hardware Audit // Protocol <span className="text-indigo-400">v3.3.4</span>
              </p>
            </div>
          </div>

          <form onSubmit={handleSearch} className="flex gap-2 w-full md:w-auto">
             <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-700" />
                <input 
                  type="text" 
                  placeholder="INPUT SERIAL (e.g. SENTRY-VA-042)..."
                  value={serialQuery}
                  onChange={(e) => setSerialQuery(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg py-3 pl-10 pr-4 text-xs text-white focus:outline-none focus:border-indigo-500/50 uppercase tracking-widest"
                />
             </div>
             <button 
               type="submit"
               disabled={isSearching}
               className="px-6 bg-white text-black font-black text-[10px] uppercase tracking-widest hover:bg-indigo-500 hover:text-white transition-all rounded-lg shadow-xl flex items-center gap-2"
             >
                {isSearching ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ChevronRight className="w-4 h-4" />}
                Audit
             </button>
          </form>
        </header>

        {activeUnit ? (
          <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
             
             {/* Left Column: Unit Vitals */}
             <div className="col-span-12 lg:col-span-4 space-y-6">
                <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl relative overflow-hidden group">
                   <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:scale-110 transition-transform duration-[2000ms]">
                      <Cpu className="w-48 h-48 text-white" />
                   </div>
                   
                   <div className="relative z-10 mb-8">
                      <span className="text-[10px] text-indigo-500 font-black uppercase tracking-widest block mb-1">Physical Identity</span>
                      <h2 className="text-3xl font-black text-white tracking-tighter uppercase">{activeUnit.id}</h2>
                      <div className="flex items-center gap-2 mt-2">
                         <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                         <span className="text-[10px] text-gray-600 font-bold uppercase tracking-tighter">Status: {activeUnit.status}</span>
                      </div>
                   </div>

                   <div className="grid grid-cols-2 gap-4 relative z-10">
                      <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                         <span className="text-[9px] text-gray-700 font-black uppercase block mb-1">Reputation</span>
                         <span className="text-xl font-black text-white">{activeUnit.current_rep}</span>
                      </div>
                      <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                         <span className="text-[9px] text-gray-700 font-black uppercase block mb-1">Tasks Done</span>
                         <span className="text-xl font-black text-white">{activeUnit.total_tasks.toLocaleString()}</span>
                      </div>
                   </div>

                   <div className="mt-8 pt-8 border-t border-white/5 relative z-10">
                      <div className="flex items-center gap-3 text-indigo-400 mb-4">
                         <ShieldCheck className="w-5 h-5" />
                         <span className="text-[10px] font-black uppercase tracking-[0.2em]">Security Standing</span>
                      </div>
                      <div className="space-y-3">
                         <div className="flex justify-between items-center text-[10px] font-bold uppercase">
                            <span className="text-gray-600">Firmware</span>
                            <span className="text-white">v2.8.1-RELEASE</span>
                         </div>
                         <div className="flex justify-between items-center text-[10px] font-bold uppercase">
                            <span className="text-gray-600">TPM Module</span>
                            <span className="text-white font-mono">SLB 9670 V1.0</span>
                         </div>
                         <div className="flex justify-between items-center text-[10px] font-bold uppercase">
                            <span className="text-gray-600">Seed Age</span>
                            <span className="text-amber-500">142 DAYS</span>
                         </div>
                      </div>
                   </div>
                </div>

                <div className="p-6 bg-red-500/5 border border-red-500/10 rounded-xl">
                   <div className="flex items-center gap-3 text-red-500 mb-4">
                      <AlertTriangle className="w-5 h-5" />
                      <h4 className="text-[10px] font-black uppercase tracking-widest">EOL Maintenance</h4>
                   </div>
                   <p className="text-[11px] text-gray-500 leading-relaxed font-bold">
                      Unit is currently within the <span className="text-white">5% margin</span> of its 10,000 task seed limit. A mandatory hardware rotation (TPM2_CreatePrimary) is required within the next 160 tasks.
                   </p>
                   <button className="w-full py-3 mt-6 bg-red-600 text-white font-black text-[10px] uppercase tracking-widest rounded hover:bg-red-500 transition-all flex items-center justify-center gap-2">
                      <RotateCcw className="w-3.5 h-3.5" /> Authorize Key Rotation
                   </button>
                </div>
             </div>

             {/* Right Column: Timeline & Shards */}
             <div className="col-span-12 lg:col-span-8 space-y-6">
                
                {/* Event Timeline */}
                <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl">
                   <h3 className="text-xs font-black text-white uppercase tracking-widest mb-10 flex items-center gap-3">
                      <Layers className="w-4 h-4 text-indigo-500" /> Physical Audit Trail
                   </h3>

                   <div className="relative space-y-12 pb-4">
                      <div className="absolute left-[11px] top-2 bottom-2 w-px bg-white/5" />
                      
                      {activeUnit.events.map((evt, i) => (
                        <div key={i} className="flex items-start gap-8 relative z-10 group">
                           <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all bg-black ${
                             evt.type === 'KEY_ROTATION' ? 'border-amber-500 text-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.3)]' : 
                             evt.type === 'HEALTH_CHECK' ? 'border-green-500 text-green-500' :
                             'border-white/20 text-gray-700'
                           }`}>
                              <CheckCircle2 className="w-3 h-3" />
                           </div>
                           <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-6 items-center bg-white/[0.01] border border-white/5 p-5 rounded-xl group-hover:bg-white/[0.03] group-hover:border-white/10 transition-all">
                              <div className="md:col-span-1">
                                 <span className="text-[10px] font-black text-white uppercase tracking-tighter block mb-1">{evt.type}</span>
                                 <span className="text-[8px] text-gray-700 font-bold uppercase">{evt.date}</span>
                              </div>
                              <div className="md:col-span-1 flex items-center gap-2">
                                 <MapPin className="w-3 h-3 text-gray-800" />
                                 <span className="text-[9px] text-gray-600 font-bold uppercase">{evt.location}</span>
                              </div>
                              <div className="md:col-span-1">
                                 <span className="text-[8px] text-gray-800 font-black uppercase block mb-1">Attestation Sig</span>
                                 <code className="text-[10px] text-indigo-400 font-mono">{evt.sig}</code>
                              </div>
                              <div className="md:col-span-1 text-right">
                                 <p className="text-[10px] text-gray-500 italic font-medium leading-tight">"{evt.detail}"</p>
                              </div>
                           </div>
                        </div>
                      ))}
                   </div>
                </div>

                {/* Hardware Forensics Card */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
                      <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                         <Binary className="w-4 h-4 text-indigo-500" /> Silicon Fingerprint
                      </h3>
                      <div className="space-y-6">
                         <div>
                            <span className="text-[9px] text-gray-700 uppercase font-black block mb-2 tracking-widest">Active AK Public Handle</span>
                            <div className="p-4 bg-black border border-white/5 rounded-lg">
                               <code className="text-[10px] text-gray-500 break-all leading-relaxed">
                                  028A2E1C3B2E9928310D2A1E772B31C442F9928310A1B2C3D4E5F6
                               </code>
                            </div>
                         </div>
                         <div className="flex justify-between items-center text-[10px] font-bold uppercase border-t border-white/5 pt-4">
                            <span className="text-gray-600">Verification Hash</span>
                            <span className="text-green-500 flex items-center gap-1">
                               <ShieldCheck className="w-3 h-3" /> MATCH_FOUND
                            </span>
                         </div>
                      </div>
                   </div>

                   <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl flex flex-col justify-between">
                      <div>
                         <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                            <Database className="w-4 h-4 text-emerald-500" /> Registry Manifest
                         </h3>
                         <div className="space-y-4 font-mono text-[10px]">
                            <div className="flex justify-between">
                               <span className="text-gray-700 uppercase">Birth Epoch</span>
                               <span className="text-white font-bold">2025.11.14</span>
                            </div>
                            <div className="flex justify-between">
                               <span className="text-gray-700 uppercase">Provisioner</span>
                               <span className="text-white font-bold">FOUNDATION_LABS_01</span>
                            </div>
                            <div className="flex justify-between">
                               <span className="text-gray-700 uppercase">Audit Chain</span>
                               <span className="text-indigo-400 font-bold">PX_LEDGER_SYNC</span>
                            </div>
                         </div>
                      </div>
                      <button className="w-full mt-6 py-2 border border-white/10 rounded text-[9px] font-black text-gray-500 hover:text-white uppercase tracking-widest transition-all">
                         Export Full Lifecycle (JSON) &rarr;
                      </button>
                   </div>
                </div>
             </div>

          </div>
        ) : (
          <div className="h-[600px] border-2 border-white/5 border-dashed rounded-3xl flex flex-col items-center justify-center p-12 text-center opacity-30 grayscale transition-all duration-700">
             <History className="w-24 h-24 text-gray-800 mb-8 animate-pulse" />
             <h2 className="text-2xl font-black text-gray-600 uppercase tracking-[0.3em] mb-4">Audit Registry Ready</h2>
             <p className="text-sm text-gray-800 font-bold uppercase tracking-widest max-w-md mx-auto leading-relaxed">
                Input a hardware serial ID to retrieve the non-repudiable silicon lifecycle ledger and verify the cryptographic root of trust for any Node.
             </p>
          </div>
        )}

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-6xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(99,102,241,0.5)]" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Hardware Ledger Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Silicon is the witness; the ledger is the proof."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] REGISTRY_LOCK: ACTIVE</span>
            <span>[*] PROVENANCE_V1: ENABLED</span>
            <span>[*] VERSION: v3.3.4</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
