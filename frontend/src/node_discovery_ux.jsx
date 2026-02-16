import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  Globe, 
  Search, 
  Activity, 
  ShieldCheck, 
  Cpu, 
  RefreshCw, 
  ChevronRight, 
  ArrowRight, 
  CheckCircle2, 
  Lock, 
  Fingerprint, 
  MapPin, 
  Wifi, 
  Signal,
  Box,
  Terminal,
  Info,
  XCircle,
  AlertTriangle
} from 'lucide-react';

/**
 * PROXY PROTOCOL - NODE DISCOVERY UX (v1.0)
 * "The entry point for biological fleet onboarding."
 * ----------------------------------------------------
 */

const App = () => {
  const [step, setStep] = useState(1);
  const [isProbing, setIsProbing] = useState(false);
  const [selectedHub, setSelectedHub] = useState(null);
  const [isBinding, setIsBinding] = useState(false);

  // Mock Discovery API Data (Reflects output from core/api/hub_discovery_api.py)
  const [hubs, setHubs] = useState([
    { id: 'US-EAST', name: 'US East (Virginia)', url: 'va.proxyagent.network', latency: '--', status: 'OPTIMAL', priority: 1 },
    { id: 'US-WEST', name: 'US West (Oregon)', url: 'or.proxyagent.network', latency: '--', status: 'STABLE', priority: 2 },
    { id: 'EU-LONDON', name: 'Europe (London)', url: 'ldn.proxyagent.network', latency: '--', status: 'STABLE', priority: 3 },
    { id: 'ASIA-SG', name: 'Asia (Singapore)', url: 'sg.proxyagent.network', latency: '--', status: 'DEGRADED', priority: 4 }
  ]);

  const runDiscoveryProbes = () => {
    setIsProbing(true);
    let iterations = 0;
    const interval = setInterval(() => {
      setHubs(prev => prev.map(h => ({
        ...h,
        latency: Math.floor(Math.random() * (h.id === 'ASIA-SG' ? 400 : 150) + 20)
      })));
      iterations++;
      if (iterations >= 10) {
        clearInterval(interval);
        setIsProbing(false);
      }
    }, 200);
  };

  const handleBind = () => {
    setIsBinding(true);
    // Simulate TPM 2.0 Key Generation & Identity Binding
    setTimeout(() => {
      setIsBinding(false);
      setStep(4);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-indigo-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-3xl w-full relative z-10">
        
        {/* Progress Stepper */}
        <div className="flex justify-between mb-12 px-6 relative">
           <div className="absolute top-1/2 left-0 w-full h-px bg-white/5 -z-10" />
           {[1, 2, 3, 4].map((s) => (
             <div key={s} className={`w-10 h-10 rounded-full flex items-center justify-center border-2 text-xs font-black transition-all duration-500 ${
               step >= s ? 'bg-indigo-500 border-indigo-400 text-black shadow-[0_0_20px_rgba(99,102,241,0.5)]' : 'bg-black border-white/10 text-gray-700'
             }`}>
               0{s}
             </div>
           ))}
        </div>

        <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
          
          {/* Dashboard Header */}
          <div className="p-8 border-b border-white/5 bg-white/[0.02] flex justify-between items-center px-10">
             <div>
                <h1 className="text-xl font-black text-white uppercase tracking-tight">Hub Discovery</h1>
                <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold">Node Onboarding // Protocol v2.9.8</p>
             </div>
             <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                <span className="text-[10px] text-green-500 font-black uppercase">Local Daemon Active</span>
             </div>
          </div>

          <div className="p-10 min-h-[450px] flex flex-col justify-between">
            
            {/* STEP 1: Locate */}
            {step === 1 && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="text-center max-w-md mx-auto">
                   <div className="p-4 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 inline-block mb-6">
                      <Globe className="w-12 h-12 text-indigo-500" />
                   </div>
                   <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-4">Geolocation Audit</h2>
                   <p className="text-xs text-gray-500 leading-relaxed italic mb-8">
                     "Your egress IP has been mapped to the North America (US-WEST) jurisdiction. Discovering optimized regional backbones..."
                   </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                   <div className="p-5 bg-black border border-white/5 rounded-xl text-center">
                      <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Detected IP</span>
                      <span className="text-xs text-indigo-400 font-bold">192.168.1.101</span>
                   </div>
                   <div className="p-5 bg-black border border-white/5 rounded-xl text-center">
                      <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Regional Code</span>
                      <span className="text-xs text-green-500 font-bold">US_WEST_PHX</span>
                   </div>
                </div>

                <button 
                  onClick={() => { setStep(2); runDiscoveryProbes(); }}
                  className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-indigo-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-xl"
                >
                  Discover Optimized Hubs <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* STEP 2: Probe & Select */}
            {step === 2 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                <div className="flex justify-between items-end">
                   <div>
                      <h3 className="text-xs font-black text-gray-500 uppercase tracking-widest mb-1">Network Vitality</h3>
                      <p className="text-lg font-black text-white uppercase tracking-tight">SLA Performance Probes</p>
                   </div>
                   <button 
                     onClick={runDiscoveryProbes}
                     disabled={isProbing}
                     className={`p-2 rounded border border-white/10 hover:bg-white/5 transition-all ${isProbing ? 'animate-spin' : ''}`}
                   >
                     <RefreshCw className="w-4 h-4 text-gray-600" />
                   </button>
                </div>

                <div className="bg-black/40 rounded-xl border border-white/5 overflow-hidden">
                   <div className="divide-y divide-white/5 font-mono">
                      {hubs.map((hub) => (
                        <div 
                          key={hub.id} 
                          onClick={() => !isProbing && setSelectedHub(hub)}
                          className={`p-5 flex items-center justify-between cursor-pointer transition-all ${
                            selectedHub?.id === hub.id ? 'bg-indigo-500/10' : 'hover:bg-white/[0.01]'
                          } ${isProbing ? 'opacity-50 pointer-events-none' : ''}`}
                        >
                           <div className="flex items-center gap-6">
                              <div className={`w-2 h-2 rounded-full ${selectedHub?.id === hub.id ? 'bg-indigo-500' : hub.status === 'OPTIMAL' ? 'bg-green-500' : 'bg-gray-700'}`} />
                              <div>
                                 <span className="text-xs font-black text-white block uppercase mb-0.5">{hub.name}</span>
                                 <span className="text-[9px] text-gray-600 font-bold">{hub.url}</span>
                              </div>
                           </div>
                           <div className="text-right">
                              <span className={`text-sm font-black ${hub.latency === '--' ? 'text-gray-800' : parseInt(hub.latency) < 100 ? 'text-green-500' : 'text-yellow-500'}`}>
                                {hub.latency}{hub.latency !== '--' && 'ms'}
                              </span>
                              <span className="text-[8px] text-gray-700 block font-black uppercase">RTT</span>
                           </div>
                        </div>
                      ))}
                   </div>
                </div>

                <button 
                  onClick={() => setStep(3)}
                  disabled={!selectedHub || isProbing}
                  className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-indigo-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-xl disabled:opacity-20"
                >
                  Establish Peer Link <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* STEP 3: Bind (Ceremony) */}
            {step === 3 && (
              <div className="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
                 <div className="p-8 border border-indigo-500/20 bg-indigo-500/5 rounded-2xl flex items-center gap-8 shadow-inner">
                    <div className="p-5 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl relative">
                       <Cpu className={`w-12 h-12 text-indigo-500 ${isBinding ? 'animate-pulse' : ''}`} />
                       {isBinding && <div className="absolute inset-0 bg-indigo-500/20 rounded-2xl animate-ping" />}
                    </div>
                    <div>
                       <h3 className="text-xl font-black text-white uppercase tracking-tighter mb-2">Binding Ceremony</h3>
                       <p className="text-xs text-gray-500 leading-relaxed max-w-sm">
                         Establishing hardware root of trust with <span className="text-white font-bold">{selectedHub.name}</span>. This binds your TPM private key to the jurisdictional hub.
                       </p>
                    </div>
                 </div>

                 <div className="bg-[#050505] border border-white/5 rounded-xl p-6 h-40 flex flex-col font-mono text-[10px]">
                    <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
                       <span className="text-gray-700 font-black uppercase tracking-widest flex items-center gap-2"><Terminal className="w-3 h-3" /> Daemon_Log</span>
                       <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                    </div>
                    <div className="space-y-2 text-gray-500 overflow-y-auto flex-1 scrollbar-hide">
                       <p>[*] INVOKING TPM2_CREATEPRIMARY...</p>
                       <p>[*] GENERATING RSA-2048 IDENTITY KEY [AK]...</p>
                       {isBinding && <p className="text-indigo-400 font-bold">[*] BROADCASTING ATTESTATION QUOTE TO HUB...</p>}
                       {isBinding && <p className="text-indigo-400 font-bold">[*] AWAITING HUB_CONFIRMATION_HASH...</p>}
                       <p className="animate-pulse">[*] WAITING_INPUT...</p>
                    </div>
                 </div>

                 <button 
                  onClick={handleBind}
                  disabled={isBinding}
                  className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-[0_0_40px_rgba(255,255,255,0.1)]"
                >
                  {isBinding ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Fingerprint className="w-5 h-5" />}
                  {isBinding ? 'Sealing Identity...' : 'Initiate Hardware Binding'}
                </button>
              </div>
            )}

            {/* STEP 4: Success */}
            {step === 4 && (
              <div className="text-center py-8 animate-in zoom-in-95 duration-500 space-y-10">
                <div className="w-24 h-24 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_60px_rgba(34,197,94,0.1)]">
                   <ShieldCheck className="w-12 h-12 text-green-500" />
                </div>
                <div>
                   <h2 className="text-3xl font-black text-white uppercase tracking-tighter mb-3">Node Online</h2>
                   <p className="text-xs text-gray-500 mb-10 max-w-sm mx-auto leading-relaxed">
                     Your hardware identity has been successfully registered in the Global Reputation Oracle. You are now reachable via the <span className="text-indigo-400 font-bold">{selectedHub.id}</span> backbone.
                   </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                   <div className="p-4 bg-black border border-white/5 rounded-xl flex items-center gap-4">
                      <Lock className="w-5 h-5 text-indigo-500" />
                      <div className="text-left">
                         <span className="text-[9px] text-gray-600 uppercase font-black block">Status</span>
                         <span className="text-xs font-bold text-white uppercase">TPM_LOCKED</span>
                      </div>
                   </div>
                   <div className="p-4 bg-black border border-white/5 rounded-xl flex items-center gap-4">
                      <Signal className="w-5 h-5 text-green-500" />
                      <div className="text-left">
                         <span className="text-[9px] text-gray-600 uppercase font-black block">Peer Path</span>
                         <span className="text-xs font-bold text-white uppercase">{selectedHub.id}</span>
                      </div>
                   </div>
                </div>

                <button 
                  onClick={() => window.location.reload()}
                  className="px-12 py-4 bg-white text-black font-black text-xs uppercase tracking-widest hover:bg-green-500 transition-all rounded shadow-xl"
                >
                  Enter Command Center
                </button>
              </div>
            )}

          </div>

          {/* Footer Security Note */}
          <div className="p-4 bg-black border-t border-white/5 flex items-center justify-between px-10 text-[9px] font-black text-gray-700 uppercase tracking-widest">
             <div className="flex items-center gap-3">
                <Box className="w-3.5 h-3.5" />
                <span>Protocol: LNV2 Mainnet</span>
             </div>
             <div className="flex gap-6">
                <span>TPM_AUTH: ENABLED</span>
                <span>HW_ID: 0x8A2E...F91C</span>
             </div>
          </div>
        </div>

        {/* Global Help Link */}
        <div className="mt-8 flex justify-between items-center px-4">
           <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-gray-600" />
              <span className="text-[10px] text-gray-600 font-bold uppercase tracking-widest leading-none mt-0.5">Need assistance?</span>
           </div>
           <button className="text-[10px] font-black text-gray-600 hover:text-white uppercase tracking-tighter flex items-center gap-1.5 transition-all">
             View Onboarding Docs <ChevronRight className="w-3 h-3" />
           </button>
        </div>

      </main>

    </div>
  );
};

export default App;
