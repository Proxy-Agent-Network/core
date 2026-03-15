import React, { useState } from 'react';
import { 
  Search, 
  ZoomIn, 
  ZoomOut, 
  Maximize2, 
  FileText, 
  Image as ImageIcon, 
  ShieldCheck, 
  Binary, 
  Cpu, 
  AlertCircle, 
  Info, 
  Lock, 
  Fingerprint,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Split,
  Eye,
  Terminal,
  Activity
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HIGH COURT EVIDENCE VIEWER (v1.0)
 * "Forensic inspection for decentralized justice."
 * ----------------------------------------------------
 */

const App = () => {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [activeShard, setActiveShard] = useState('LOGS'); // LOGS, IMAGE, METADATA
  const [isVerifying, setIsVerifying] = useState(false);

  // Mock Evidence Shard Data
  const evidence = {
    case_id: "CASE-8829-APP",
    shards: {
      logs: [
        { line: 1, text: "2026-02-11T20:45:01Z [LND] HTLC Accept: task_9901", status: "NORMAL" },
        { line: 2, text: "2026-02-11T20:45:05Z [TPM] Signing Request PCR 7...", status: "NORMAL" },
        { line: 3, text: "2026-02-11T20:45:06Z [TPM] ERROR: PCR_VALUE_MISMATCH (0x8A2E...)", status: "CONFLICT" },
        { line: 4, text: "2026-02-11T20:45:06Z [CORE] Slashing Engine Triggered", status: "NORMAL" }
      ],
      metadata: {
        node_id: "NODE_ELITE_X29",
        hardware_id: "INFINEON_OPTIGA_2.0_v42",
        ip_egress: "192.168.1.101",
        latency: "42ms",
        tpm_quote: "8a2e1c...f91c3b"
      }
    }
  };

  const toggleVerify = () => {
    setIsVerifying(true);
    setTimeout(() => setIsVerifying(false), 1500);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col selection:bg-amber-500/30">
      
      {/* Forensic Header */}
      <header className="max-w-7xl mx-auto w-full flex flex-col md:flex-row justify-between items-start md:items-center mb-8 border-b border-white/10 pb-6 gap-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg shadow-[0_0_20px_rgba(245,158,11,0.1)]">
            <Eye className="w-6 h-6 text-amber-500" />
          </div>
          <div>
            <h1 className="text-xl font-black text-white tracking-tighter uppercase">Evidence Viewer</h1>
            <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold">Forensic Station // <span className="text-amber-500">{evidence.case_id}</span></p>
          </div>
        </div>

        <div className="flex gap-3">
           <button 
             onClick={toggleVerify}
             className="px-6 py-2 bg-white/5 border border-white/10 rounded text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-white transition-all flex items-center gap-2"
           >
             {isVerifying ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
             Verify HW Signature
           </button>
           <div className="h-10 w-px bg-white/10 mx-2" />
           <div className="flex flex-col items-end">
              <span className="text-[9px] text-gray-700 uppercase font-black">Retention Clock</span>
              <span className="text-sm font-black text-red-500 tracking-tighter">18h 42m LEFT</span>
           </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto w-full grid grid-cols-12 gap-8 flex-1">
        
        {/* Shard Navigation (Left Sidebar) */}
        <div className="col-span-12 lg:col-span-1 space-y-4">
           {[
             { id: 'LOGS', icon: Terminal },
             { id: 'IMAGE', icon: ImageIcon },
             { id: 'METADATA', icon: Binary }
           ].map((tab) => (
             <button 
               key={tab.id}
               onClick={() => setActiveShard(tab.id)}
               className={`w-full aspect-square flex items-center justify-center rounded-xl border transition-all ${
                 activeShard === tab.id 
                   ? 'bg-amber-500 border-amber-400 text-black shadow-[0_0_20px_rgba(245,158,11,0.2)]' 
                   : 'bg-[#0a0a0a] border-white/5 text-gray-600 hover:border-white/10 hover:text-gray-400'
               }`}
             >
               <tab.icon className="w-6 h-6" />
             </button>
           ))}
        </div>

        {/* Content Viewer (Center) */}
        <div className="col-span-12 lg:col-span-8 space-y-6">
           <div className="bg-[#0a0a0a] border border-white/10 rounded-xl overflow-hidden shadow-2xl flex flex-col min-h-[600px]">
              
              {/* Viewer Tools */}
              <div className="p-4 border-b border-white/5 bg-white/[0.02] flex justify-between items-center px-6">
                 <div className="flex items-center gap-4">
                    <span className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em]">{activeShard} ENGINE</span>
                    <div className="h-4 w-px bg-white/10" />
                    <div className="flex items-center gap-2">
                       <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                       <span className="text-[9px] text-green-500 font-bold uppercase">Decrypted Status: OK</span>
                    </div>
                 </div>
                 {activeShard === 'IMAGE' && (
                    <div className="flex items-center gap-4">
                       <div className="flex bg-black/60 rounded p-1 border border-white/10 gap-2">
                          <button onClick={() => setZoomLevel(prev => Math.max(0.5, prev - 0.25))} className="p-1 hover:text-amber-500"><ZoomOut className="w-4 h-4" /></button>
                          <span className="text-[10px] font-black w-10 text-center flex items-center justify-center">{Math.round(zoomLevel * 100)}%</span>
                          <button onClick={() => setZoomLevel(prev => Math.min(3, prev + 0.25))} className="p-1 hover:text-amber-500"><ZoomIn className="w-4 h-4" /></button>
                       </div>
                       <button className="p-2 bg-white/5 border border-white/10 rounded hover:text-white transition-all"><Maximize2 className="w-4 h-4" /></button>
                    </div>
                 )}
              </div>

              {/* View Rendering */}
              <div className="flex-1 relative overflow-hidden bg-black/40">
                 {activeShard === 'LOGS' && (
                    <div className="p-8 space-y-2 animate-in fade-in duration-500">
                       {evidence.shards.logs.map((log, idx) => (
                         <div key={idx} className="flex gap-6 group">
                            <span className="text-gray-800 text-[10px] w-6 select-none">{log.line}</span>
                            <span className={`text-[11px] font-medium leading-relaxed ${log.status === 'CONFLICT' ? 'text-red-500 bg-red-500/10 px-1 rounded' : 'text-gray-400 group-hover:text-gray-200'} transition-colors`}>
                              {log.text}
                            </span>
                         </div>
                       ))}
                    </div>
                 )}

                 {activeShard === 'IMAGE' && (
                    <div className="absolute inset-0 flex items-center justify-center p-12">
                       <div 
                         className="w-full h-full border border-white/5 rounded-lg flex flex-col items-center justify-center relative transition-transform duration-300"
                         style={{ transform: `scale(${zoomLevel})` }}
                       >
                          {/* Stylized Mock Proof Image */}
                          <div className="w-[300px] h-[400px] bg-[#111] border border-white/10 rounded shadow-2xl flex flex-col p-6 animate-in zoom-in-95 duration-700">
                             <div className="w-full h-12 border-b border-white/5 mb-8 flex items-center justify-center opacity-20">
                                <ImageIcon className="w-8 h-8" />
                             </div>
                             <div className="space-y-4">
                                <div className="h-2 w-full bg-white/5 rounded-full" />
                                <div className="h-2 w-3/4 bg-white/5 rounded-full" />
                                <div className="h-2 w-5/6 bg-white/5 rounded-full" />
                                <div className="pt-20">
                                   <div className="h-10 w-24 border border-red-500/50 flex items-center justify-center text-[8px] text-red-500 font-bold rotate-12 mx-auto uppercase">
                                     Invalid Proof
                                   </div>
                                </div>
                             </div>
                          </div>
                          <div className="absolute top-4 right-4 bg-black/80 p-2 rounded border border-amber-500/50 text-[8px] text-amber-500 font-black uppercase">
                            Forensic Overlay Active
                          </div>
                       </div>
                    </div>
                 )}

                 {activeShard === 'METADATA' && (
                    <div className="p-12 animate-in fade-in duration-500">
                       <div className="grid grid-cols-2 gap-8">
                          {Object.entries(evidence.shards.metadata).map(([key, val]) => (
                            <div key={key} className="border-b border-white/5 pb-4">
                               <span className="text-[10px] text-gray-600 font-black uppercase tracking-widest block mb-2">{key.replace('_', ' ')}</span>
                               <code className="text-xs text-indigo-400">{val}</code>
                            </div>
                          ))}
                       </div>
                       <div className="mt-12 p-6 bg-amber-500/5 border border-amber-500/10 rounded-xl flex items-center gap-6">
                          <Fingerprint className="w-10 h-10 text-amber-500" />
                          <div>
                             <p className="text-xs text-white font-bold mb-1 uppercase tracking-tighter">Cryptographic Attestation</p>
                             <p className="text-[10px] text-gray-500 leading-relaxed">
                                This shard was unsealed at {new Date().toLocaleTimeString()} using the AK_HANDLE context. Any unauthorized screenshot attempts will be logged by the chassis tamper service.
                             </p>
                          </div>
                       </div>
                    </div>
                 )}
              </div>
           </div>
        </div>

        {/* Forensic Insights (Right Sidebar) */}
        <div className="col-span-12 lg:col-span-3 space-y-6">
           <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-8 shadow-2xl">
              <h3 className="text-xs font-black text-white uppercase tracking-[0.2em] mb-8 flex items-center gap-2">
                 <AlertCircle className="w-4 h-4 text-amber-500" /> Auditor's Brief
              </h3>
              <div className="space-y-6">
                 <div>
                    <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Dispute Summary</span>
                    <p className="text-[11px] text-gray-400 leading-relaxed italic">
                      "Agent claims the node submitted a photograph of a blank sheet instead of the signed deed. PCR history confirms firmware stability during the event."
                    </p>
                 </div>
                 <div className="pt-6 border-t border-white/5">
                    <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-4">Anomaly Detection</span>
                    <div className="flex justify-between items-center text-[10px] font-bold text-red-500 uppercase tracking-tighter">
                       <span className="flex items-center gap-2"><Split className="w-3 h-3" /> PCR_DRIFT</span>
                       <span>DETECTION_LEVEL: HIGH</span>
                    </div>
                 </div>
              </div>
           </div>

           <div className="p-8 border border-white/10 bg-[#0a0a0a] rounded-xl flex flex-col justify-between shadow-2xl relative overflow-hidden group">
              <div className="absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform">
                 <Binary className="w-24 h-24 text-white" />
              </div>
              <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                 <Lock className="w-3.5 h-3.5 text-amber-500" /> Evidence Integrity
              </h4>
              <div className="space-y-3">
                 <div className="flex justify-between items-center text-[9px] font-bold">
                    <span className="text-gray-600">Manifest Hash</span>
                    <span className="text-white">e3b0c44...</span>
                 </div>
                 <div className="flex justify-between items-center text-[9px] font-bold">
                    <span className="text-gray-600">E2EE Tunnel</span>
                    <span className="text-green-500">ENCRYPTED</span>
                 </div>
              </div>
           </div>

           <button className="w-full py-4 bg-indigo-500 text-black font-black text-xs uppercase tracking-[0.2em] rounded-lg hover:bg-indigo-400 transition-all flex items-center justify-center gap-3 shadow-xl">
              <ShieldCheck className="w-4 h-4" /> Finalize Audit
           </button>
        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-7xl mx-auto w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Secure Forensic Hub Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Case: CASE-8829-APP</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] HARDWARE_ATTESTATION: OK</span>
            <span>[*] E2EE_TUNNEL: LOCKED</span>
            <span>[*] AUDITOR: NODE_ELITE_X29</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
