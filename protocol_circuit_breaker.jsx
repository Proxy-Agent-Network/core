import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Lock, 
  Unlock, 
  Key, 
  Zap, 
  ZapOff, 
  Activity, 
  AlertTriangle, 
  RefreshCw, 
  ShieldCheck, 
  Terminal, 
  Radio,
  Cpu,
  Unplug,
  History,
  ChevronRight,
  Info,
  Bomb
} from 'lucide-react';

/**
 * PROXY PROTOCOL - CIRCUIT BREAKER UI (v1.0)
 * "The final defense against systemic protocol failure."
 * ----------------------------------------------------
 */

const App = () => {
  const [key1Active, setKey1Active] = useState(false);
  const [key2Active, setKey2Active] = useState(false);
  const [isTripped, setIsTripped] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState([
    { ts: '20:42:01', msg: 'ORCHESTRATOR: Monitoring node fleet PCR stability...', type: 'INFO' },
    { ts: '20:45:00', msg: 'ANOMALY_ENGINE: Subnet cluster 192.168.42.0/24 reporting 40% failure.', type: 'WARN' },
    { ts: '21:05:12', msg: 'SYSTEM: Waiting for manual security overrides.', type: 'INFO' }
  ]);

  const bridgeStatus = isTripped ? 'FROZEN' : 'OPERATIONAL';

  const handleKey1 = () => setKey1Active(!key1Active);
  const handleKey2 = () => setKey2Active(!key2Active);

  const triggerKillSwitch = () => {
    if (!key1Active || !key2Active) return;
    
    setIsProcessing(true);
    // Simulate SEV-1 Shutdown Sequence
    setTimeout(() => {
      setIsTripped(true);
      setIsProcessing(false);
      addLog("CIRCUIT_BREAKER: MANUALLY TRIPPED. BRIDGE FROZEN.", "CRITICAL");
    }, 2000);
  };

  const handleReset = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsTripped(false);
      setKey1Active(false);
      setKey2Active(false);
      setIsProcessing(false);
      addLog("CIRCUIT_BREAKER: SYSTEM RESET. RAILS RE-ARMED.", "SUCCESS");
    }, 2000);
  };

  const addLog = (msg, type) => {
    const ts = new Date().toLocaleTimeString([], { hour12: false });
    setLogs(prev => [{ ts, msg, type }, ...prev].slice(0, 10));
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-red-500/30">
      
      {/* Heavy Warning Background */}
      <div className={`fixed inset-0 pointer-events-none transition-opacity duration-1000 ${isTripped ? 'opacity-20' : 'opacity-[0.03]'} z-0`} 
           style={{ 
             backgroundImage: `radial-gradient(${isTripped ? '#ff3333' : '#fff'} 1px, transparent 1px)`, 
             backgroundSize: '40px 40px' 
           }} />

      <main className="max-w-4xl w-full relative z-10 animate-in fade-in duration-700">
        
        {/* Main Console */}
        <div className={`bg-[#0a0a0a] border-2 rounded-2xl overflow-hidden shadow-2xl transition-colors duration-1000 ${isTripped ? 'border-red-500 shadow-red-500/20' : 'border-white/10'}`}>
          
          {/* Header Bar */}
          <div className={`p-6 border-b flex justify-between items-center px-10 ${isTripped ? 'bg-red-500 text-black border-red-600' : 'bg-white/[0.02] border-white/5'}`}>
             <div className="flex items-center gap-4">
                <ShieldAlert className={`w-8 h-8 ${isTripped ? 'text-black' : 'text-red-500 animate-pulse'}`} />
                <div>
                   <h1 className="text-xl font-black uppercase tracking-tighter leading-none">Circuit Breaker v1.0</h1>
                   <p className="text-[9px] font-black uppercase tracking-widest mt-1 opacity-60">Master Protocol Control // Core Team Access</p>
                </div>
             </div>
             <div className="flex items-center gap-6">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] uppercase font-black opacity-50">Bridge State</span>
                   <span className="text-lg font-black tracking-tighter">{bridgeStatus}</span>
                </div>
                <div className="h-8 w-px bg-current opacity-20" />
                <div className={`px-4 py-1.5 rounded font-black text-xs uppercase tracking-widest ${isTripped ? 'bg-black text-red-500' : 'bg-red-500/10 text-red-500'}`}>
                   {isTripped ? 'SEV-1 ACTIVE' : 'NOMINAL'}
                </div>
             </div>
          </div>

          <div className="p-10 grid grid-cols-12 gap-12">
             
             {/* Key Interaction Area */}
             <div className="col-span-12 lg:col-span-7 space-y-10">
                <div className="space-y-4">
                   <h3 className="text-xs font-black text-gray-500 uppercase tracking-widest flex items-center gap-2">
                     <Lock className="w-4 h-4" /> Dual-Key Authentication Required
                   </h3>
                   <p className="text-[11px] text-gray-600 leading-relaxed italic">
                     "Manual protocol suspension requires two independent hardware attestations. Do not initiate unless a SEV-1 incident is confirmed by the Anomaly Engine."
                   </p>
                </div>

                <div className="grid grid-cols-2 gap-8">
                   {/* Key Slot 1 */}
                   <div className={`p-8 border-2 rounded-2xl flex flex-col items-center gap-6 transition-all ${key1Active ? 'border-indigo-500 bg-indigo-500/5' : 'border-white/5 bg-black/40'}`}>
                      <div className={`p-4 rounded-full border transition-all ${key1Active ? 'bg-indigo-500 border-indigo-400 text-black shadow-[0_0_20px_rgba(99,102,241,0.4)]' : 'bg-white/5 border-white/10 text-gray-700'}`}>
                         <Key className="w-8 h-8" />
                      </div>
                      <div className="text-center">
                         <span className="text-[9px] text-gray-600 font-black uppercase tracking-widest block mb-1">Key Socket Alpha</span>
                         <span className={`text-[10px] font-black uppercase ${key1Active ? 'text-indigo-400' : 'text-gray-800'}`}>
                           {key1Active ? 'ARMED_LOCKED' : 'WAITING_AUTH'}
                         </span>
                      </div>
                      {!isTripped && (
                        <button 
                          onClick={handleKey1}
                          className={`w-full py-2 rounded text-[10px] font-black uppercase transition-all ${key1Active ? 'bg-indigo-500 text-black' : 'border border-white/10 text-gray-600 hover:text-white'}`}
                        >
                          {key1Active ? 'Revoke' : 'Sign Auth'}
                        </button>
                      )}
                   </div>

                   {/* Key Slot 2 */}
                   <div className={`p-8 border-2 rounded-2xl flex flex-col items-center gap-6 transition-all ${key2Active ? 'border-amber-500 bg-amber-500/5' : 'border-white/5 bg-black/40'}`}>
                      <div className={`p-4 rounded-full border transition-all ${key2Active ? 'bg-amber-500 border-amber-400 text-black shadow-[0_0_20px_rgba(245,158,11,0.4)]' : 'bg-white/5 border-white/10 text-gray-700'}`}>
                         <Key className="w-8 h-8" />
                      </div>
                      <div className="text-center">
                         <span className="text-[9px] text-gray-600 font-black uppercase tracking-widest block mb-1">Key Socket Beta</span>
                         <span className={`text-[10px] font-black uppercase ${key2Active ? 'text-amber-400' : 'text-gray-800'}`}>
                           {key2Active ? 'ARMED_LOCKED' : 'WAITING_AUTH'}
                         </span>
                      </div>
                      {!isTripped && (
                        <button 
                          onClick={handleKey2}
                          className={`w-full py-2 rounded text-[10px] font-black uppercase transition-all ${key2Active ? 'bg-amber-500 text-black' : 'border border-white/10 text-gray-600 hover:text-white'}`}
                        >
                          {key2Active ? 'Revoke' : 'Sign Auth'}
                        </button>
                      )}
                   </div>
                </div>

                <div className="pt-6">
                   {!isTripped ? (
                     <button 
                       onClick={triggerKillSwitch}
                       disabled={!key1Active || !key2Active || isProcessing}
                       className="w-full py-6 bg-red-600 text-white font-black text-sm uppercase tracking-[0.4em] rounded-xl flex items-center justify-center gap-4 hover:bg-red-500 transition-all disabled:opacity-20 shadow-[0_0_40px_rgba(239,68,68,0.2)]"
                     >
                       {isProcessing ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Bomb className="w-6 h-6" />}
                       {isProcessing ? 'COMMUNICATING WITH LND GATEWAY...' : 'TRIGGER BRIDGE FREEZE'}
                     </button>
                   ) : (
                     <button 
                       onClick={handleReset}
                       disabled={isProcessing}
                       className="w-full py-6 bg-green-500 text-black font-black text-sm uppercase tracking-[0.4em] rounded-xl flex items-center justify-center gap-4 hover:bg-green-400 transition-all shadow-[0_0_30px_rgba(34,197,94,0.2)]"
                     >
                       {isProcessing ? <RefreshCw className="w-5 h-5 animate-spin" /> : <ShieldCheck className="w-6 h-6" />}
                       {isProcessing ? 'RE-SYNCING CONSENSUS...' : 'RESTORE NORMAL PROTOCOL'}
                     </button>
                   )}
                </div>
             </div>

             {/* Right Sidebar: Telemetry & Logs */}
             <div className="col-span-12 lg:col-span-5 space-y-6">
                
                {/* Protocol Health Stats */}
                <div className="bg-black/40 border border-white/5 rounded-xl p-6 space-y-6 shadow-inner">
                   <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest flex items-center gap-2">
                     <Activity className="w-3.5 h-3.5 text-indigo-400" /> Vital Telemetry
                   </h3>
                   <div className="space-y-4">
                      <div className="flex justify-between items-center text-[11px] font-bold">
                         <span className="text-gray-500">Mempool Backlog</span>
                         <span className="text-white">6,402 Tasks</span>
                      </div>
                      <div className="flex justify-between items-center text-[11px] font-bold">
                         <span className="text-gray-500">LND Gateway B</span>
                         <span className="text-green-500">NOMINAL</span>
                      </div>
                      <div className="flex justify-between items-center text-[11px] font-bold">
                         <span className="text-gray-500">PCR Drift Threshold</span>
                         <span className="text-red-400">ALERT_READY</span>
                      </div>
                      <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden mt-2">
                         <div className="bg-red-500 h-full animate-pulse" style={{ width: isTripped ? '100%' : '78%' }} />
                      </div>
                   </div>
                </div>

                {/* Secure Event Log */}
                <div className="bg-[#050505] border border-white/10 rounded-xl flex flex-col h-[300px]">
                   <div className="p-3 border-b border-white/5 bg-white/[0.02] flex justify-between items-center px-4">
                      <h4 className="text-[9px] font-black text-gray-500 uppercase tracking-widest flex items-center gap-2">
                         <Terminal className="w-3 h-3" /> Secure Event Log
                      </h4>
                      <div className="flex gap-1">
                         <div className="w-1 h-1 rounded-full bg-red-500 animate-ping" />
                      </div>
                   </div>
                   <div className="p-4 overflow-y-auto font-mono text-[10px] space-y-2 flex-1 scrollbar-hide">
                      {logs.map((log, i) => (
                        <div key={i} className="flex gap-3 leading-relaxed">
                           <span className="text-gray-700 shrink-0">{log.ts}</span>
                           <span className={
                             log.type === 'CRITICAL' ? 'text-red-500 font-bold' : 
                             log.type === 'WARN' ? 'text-amber-500' : 
                             log.type === 'SUCCESS' ? 'text-green-500' : 'text-gray-500'
                           }>
                              {log.msg}
                           </span>
                        </div>
                      ))}
                      <div className="text-[9px] text-gray-800 italic animate-pulse pt-2">
                        [*] Awaiting input...
                      </div>
                   </div>
                </div>
                
                <div className="p-4 bg-indigo-500/5 border border-indigo-500/20 rounded-lg flex items-start gap-4">
                   <Info className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                   <p className="text-[9px] text-gray-500 leading-relaxed font-bold">
                     All circuit breaker interactions are recorded on the hardware-ledger and broadcast to institutional partners via E2EE signal.
                   </p>
                </div>
             </div>

          </div>

          {/* Security Banner Footer */}
          <div className="p-4 bg-black border-t border-white/5 flex items-center justify-between px-10 text-[10px] font-bold text-gray-700 uppercase tracking-widest">
             <div className="flex items-center gap-4">
                <Radio className="w-3.5 h-3.5" />
                <span>Broadcasting to Fleet Orchestrator...</span>
             </div>
             <div className="flex gap-8">
                <span>Protocol: v2.8.4</span>
                <span>Node: CORE_VIRTUAL_X1</span>
             </div>
          </div>
        </div>

        {/* Manual Emergency Bypass Note */}
        <div className="mt-8 flex justify-between items-center px-4">
           <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse" />
              <span className="text-[9px] font-black uppercase text-gray-600 tracking-widest uppercase">Encryption Mode: AES-256-GCM</span>
           </div>
           <button className="text-[9px] font-black uppercase text-gray-600 hover:text-white transition-colors flex items-center gap-1.5 tracking-tighter">
             Full Incident Response Playbook <ChevronRight className="w-3 h-3" />
           </button>
        </div>

      </main>

    </div>
  );
};

export default App;
