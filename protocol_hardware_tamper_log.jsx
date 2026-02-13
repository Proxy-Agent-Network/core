import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Bomb, 
  Trash2, 
  Activity, 
  RefreshCw, 
  Lock, 
  Unlock, 
  MapPin, 
  Clock, 
  Binary, 
  ChevronRight, 
  ExternalLink, 
  Info, 
  Terminal, 
  ShieldCheck, 
  AlertTriangle,
  Cpu,
  Unplug,
  History,
  XCircle,
  Skull,
  FileText
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HARDWARE TAMPER LOG (v1.0)
 * "Visualizing the Scorched Earth: Real-time physical threat forensics."
 * ----------------------------------------------------------------------
 */

const App = () => {
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock Tamper Incidents (Reflecting core/node/tamper_listener.py signals)
  const [incidents] = useState([
    {
      id: "INT-8829-PX",
      unit_id: "SENTRY-JP-004",
      type: "CHASSIS_INTRUSION",
      severity: "CRITICAL",
      status: "IDENTITY_WIPED",
      timestamp: "2026-02-12T14:22:05Z",
      region: "Tokyo, JP",
      coordinates: "35.6762° N, 139.6503° E",
      action_taken: "TPM2_CLEAR + SHRED_SECRETS"
    },
    {
      id: "INT-7714-PX",
      unit_id: "SENTRY-VA-092",
      type: "GEOFENCE_VIOLATION",
      severity: "ELEVATED",
      status: "PAUSED_LOCKED",
      timestamp: "2026-02-11T20:15:00Z",
      region: "Ashburn, US",
      coordinates: "39.0438° N, 77.4874° W",
      action_taken: "DAEMON_HALT"
    }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1200);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-red-500/30">
      
      {/* Background Warning Grid */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#ff3333 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl shadow-[0_0_20px_rgba(239,68,68,0.1)]">
              <ShieldAlert className="w-8 h-8 text-red-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Tamper Sentinel</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Physical Security Desk // Protocol <span className="text-red-500">v3.3.5</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Active Breaches</span>
                   <span className="text-xl font-black text-red-500 tracking-tighter">{incidents.filter(i => i.severity === 'CRITICAL').length} SEV-1</span>
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
          
          {/* Incident Stream (Left Column) */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <Activity className="w-4 h-4 text-red-500" /> Tamper Pulse
                   </h3>
                   <span className="text-[9px] text-gray-700 font-bold uppercase tracking-widest">Real-time IO</span>
                </div>

                <div className="divide-y divide-white/5">
                   {incidents.map((item) => (
                      <div 
                        key={item.id} 
                        onClick={() => setSelectedIncident(item)}
                        className={`p-6 hover:bg-red-500/[0.02] transition-all cursor-pointer group ${selectedIncident?.id === item.id ? 'bg-red-500/[0.04]' : ''}`}
                      >
                         <div className="flex justify-between items-start mb-4">
                            <div>
                               <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-red-400 transition-colors">{item.id}</span>
                               <p className="text-[9px] text-gray-600 font-bold uppercase mt-1">Unit: {item.unit_id}</p>
                            </div>
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${item.severity === 'CRITICAL' ? 'bg-red-500/10 border-red-500/20 text-red-500' : 'bg-amber-500/10 border-amber-500/20 text-amber-500'}`}>
                               {item.severity}
                            </span>
                         </div>
                         <div className="flex justify-between items-center mt-4 text-[9px] font-black text-gray-700 uppercase tracking-tighter">
                            <span>{item.type}</span>
                            <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                         </div>
                      </div>
                   ))}
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-red-500/5 rounded-xl shadow-inner relative overflow-hidden group">
                <div className="absolute -bottom-6 -right-6 opacity-[0.05] group-hover:scale-110 transition-transform">
                   <Bomb className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-red-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5" /> Scorched Earth Policy
                </h4>
                <p className="text-[11px] text-gray-500 leading-relaxed italic">
                   "Chassis intrusion triggers an asynchronous kernel interrupt, executing an immediate TPM hierarchy clear and a triple-pass shred of local secret directories. The node is bricked and the identity is unrecoverable."
                </p>
             </div>
          </div>

          {/* Forensic Investigation View (Right Column) */}
          <div className="col-span-12 lg:col-span-8 flex flex-col h-full">
             {selectedIncident ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 shadow-2xl animate-in slide-in-from-right-4 duration-300 flex-1 flex flex-col gap-10">
                   <div className="flex justify-between items-start border-b border-white/5 pb-6">
                      <div>
                         <span className="text-[10px] text-red-500 font-black uppercase tracking-[0.2em] block mb-1">Incident Report</span>
                         <h2 className="text-3xl font-black text-white tracking-tighter uppercase">{selectedIncident.id}</h2>
                      </div>
                      <button onClick={() => setSelectedIncident(null)} className="p-3 text-gray-600 hover:text-white transition-colors">
                         <XCircle className="w-6 h-6" />
                      </button>
                   </div>

                   {/* Geographical & Status Grid */}
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                      <div className="space-y-8">
                         <div>
                            <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                               <MapPin className="w-3.5 h-3.5 text-red-500" /> Event Locality
                            </h4>
                            <div className="p-6 bg-black border border-white/5 rounded-xl relative overflow-hidden group">
                               <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '20px 20px' }} />
                               <div className="relative z-10">
                                  <span className="text-sm font-black text-white uppercase">{selectedIncident.region}</span>
                                  <p className="text-[10px] text-gray-500 font-mono mt-2 tracking-tighter">{selectedIncident.coordinates}</p>
                               </div>
                            </div>
                         </div>

                         <div>
                            <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                               <Terminal className="w-3.5 h-3.5 text-indigo-500" /> Dying Breath Log
                            </h4>
                            <div className="bg-black border border-white/5 rounded-xl p-6 font-mono text-[10px] space-y-2 max-h-48 overflow-y-auto">
                               <p className="text-red-500 font-bold">14:22:01 🚨 GPIO_INT_26 (RISING)</p>
                               <p className="text-gray-500">14:22:01 [*] Triggering Scorched Earth...</p>
                               <p className="text-gray-500">14:22:02 [*] Executing tpm2_clear -c p</p>
                               <p className="text-green-500">14:22:03 [✓] TPM Identity Wiped.</p>
                               <p className="text-gray-500">14:22:03 [*] Shredding /app/secrets/...</p>
                               <p className="text-green-500">14:22:05 [✓] Disk Neutralized.</p>
                               <p className="text-red-500 font-black">14:22:05 [💀] NODE_HALT</p>
                            </div>
                         </div>
                      </div>

                      <div className="space-y-8">
                         <div>
                            <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                               <Skull className="w-3.5 h-3.5 text-red-500" /> Neutralization Proof
                            </h4>
                            <div className="space-y-4">
                               <div className="p-4 bg-white/5 border border-white/5 rounded-lg flex justify-between items-center group hover:border-red-500/30 transition-all">
                                  <div>
                                     <span className="text-[9px] text-gray-700 font-black uppercase block">Binary Wipe Sig</span>
                                     <code className="text-[10px] text-indigo-400 font-mono">0x8101...WIPED</code>
                                  </div>
                                  <ShieldCheck className="w-4 h-4 text-green-500" />
                               </div>
                               <div className="p-4 bg-white/5 border border-white/5 rounded-lg flex justify-between items-center group hover:border-red-500/30 transition-all">
                                  <div>
                                     <span className="text-[9px] text-gray-700 font-black uppercase block">Disk Status</span>
                                     <span className="text-[10px] text-white font-bold uppercase">ZEROED_OUT</span>
                                  </div>
                                  <Trash2 className="w-4 h-4 text-red-500" />
                               </div>
                            </div>
                         </div>

                         <div className="p-6 bg-red-500/5 border border-red-500/10 rounded-xl flex flex-col gap-4">
                            <div className="flex items-center gap-3 text-red-500">
                               <AlertTriangle className="w-5 h-5 animate-pulse" />
                               <span className="text-[10px] font-black uppercase tracking-widest">Protocol Action</span>
                            </div>
                            <p className="text-[11px] text-gray-500 leading-relaxed font-bold">
                               Identity <span className="text-white">{selectedIncident.unit_id}</span> has been permanently revoked. Reputation score frozen at last known valid heartbeat.
                            </p>
                            <button className="w-full py-2 bg-red-600 text-white font-black text-[9px] uppercase tracking-widest rounded hover:bg-red-500 transition-all flex items-center justify-center gap-2">
                               <XCircle className="w-3.5 h-3.5" /> Blacklist Serial ID
                            </button>
                         </div>
                      </div>
                   </div>

                   {/* Audit Action Bar */}
                   <div className="mt-auto pt-8 border-t border-white/5 flex flex-col md:flex-row gap-6 items-center">
                      <div className="flex items-center gap-4 flex-1 bg-white/[0.02] border border-white/5 p-4 rounded-xl">
                         <Binary className="w-8 h-8 text-gray-700" />
                         <p className="text-[11px] text-gray-500 leading-relaxed font-medium">
                           The forensic proof of destruction is valid. This incident satisfies the non-repudiation requirement for insurance claim rejection.
                         </p>
                      </div>
                      <button className="px-8 py-4 bg-white text-black font-black text-xs uppercase tracking-widest hover:bg-red-500 transition-all rounded shadow-xl flex items-center gap-2">
                         <FileText className="w-4 h-4" /> Export Incident Report
                      </button>
                   </div>
                </div>
             ) : (
                <div className="h-full border-2 border-white/5 border-dashed rounded-2xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale transition-all">
                   <ShieldAlert className="w-20 h-20 text-gray-800 mb-8 animate-pulse" />
                   <h3 className="text-lg font-black text-gray-600 uppercase tracking-[0.3em] mb-3">Threat Station Ready</h3>
                   <p className="text-xs text-gray-800 font-bold uppercase tracking-widest max-w-sm">Select a security event from the pulse stream to inspect hardware intrusion forensics and wipe-confirmation logs.</p>
                </div>
             )}
          </div>

        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Tamper Watch Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Silicon identity: Protected by destruction."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] INTRUSION_DETECTION: ON</span>
            <span>[*] WIPE_PROTOCOL: V1.0</span>
            <span>[*] VERSION: v3.3.5</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scan {
          0% { transform: translateY(-80px); }
          50% { transform: translateY(80px); }
          100% { transform: translateY(-80px); }
        }
        .animate-scan {
          animation: scan 3s ease-in-out infinite;
        }
      `}} />

    </div>
  );
};

export default App;
