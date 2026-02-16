import React, { useState } from 'react';
import { 
  Gavel, 
  CheckCircle2, 
  XCircle, 
  ShieldCheck, 
  Binary, 
  ArrowRight, 
  Download, 
  Lock, 
  Users, 
  Coins, 
  TrendingUp, 
  FileText, 
  ExternalLink,
  Info,
  ChevronRight,
  Fingerprint,
  Zap,
  Scale
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HIGH COURT VERDICT SUMMARY (v1.0)
 * "The final judgment of the biological network."
 * ----------------------------------------------------
 */

const App = () => {
  // Mock Finalized Case Data
  const [verdict] = useState({
    id: "CASE-8829-APP",
    task_id: "T-9901",
    node_id: "NODE_ELITE_X29",
    result: "APPROVED",
    consensus: "6/7",
    action: "RELEASE_TO_NODE",
    dispute_value: 500000,
    published_at: "2026-02-11T21:42:00Z",
    manifest_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    jurors: [
      { id: "Juror 1", vote: "APPROVE", sig: "0x8a2e..." },
      { id: "Juror 2", vote: "APPROVE", sig: "0xf91c..." },
      { id: "Juror 3", vote: "APPROVE", sig: "0xd2a1..." },
      { id: "Juror 4", vote: "APPROVE", sig: "0xe772..." },
      { id: "Juror 5", vote: "APPROVE", sig: "0xb31c..." },
      { id: "Juror 6", vote: "APPROVE", sig: "0x442f..." },
      { id: "Juror 7", vote: "REJECT", sig: "0x9928..." }
    ]
  });

  const isApproved = verdict.result === 'APPROVED';

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-amber-500/30">
      
      {/* Background Decorative Grid */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-4xl w-full relative z-10 animate-in fade-in zoom-in-95 duration-700">
        
        {/* Main Verdict Card */}
        <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)]">
          
          {/* Header Banner */}
          <div className={`p-8 flex justify-between items-center ${isApproved ? 'bg-green-500/10 border-b border-green-500/20' : 'bg-red-500/10 border-b border-red-500/20'}`}>
             <div className="flex items-center gap-6">
                <div className={`p-4 rounded-xl border ${isApproved ? 'bg-green-500/20 border-green-500/40 text-green-500' : 'bg-red-500/20 border-red-500/40 text-red-500'}`}>
                   {isApproved ? <CheckCircle2 className="w-10 h-10" /> : <XCircle className="w-10 h-10" />}
                </div>
                <div>
                   <h1 className="text-3xl font-black text-white tracking-tighter uppercase">Judgment Finalized</h1>
                   <p className={`text-[10px] font-black uppercase tracking-[0.2em] ${isApproved ? 'text-green-500' : 'text-red-500'}`}>
                     Verdict: {verdict.result} // Consensus: {verdict.consensus}
                   </p>
                </div>
             </div>
             <div className="text-right hidden sm:block">
                <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-1">Published At</span>
                <span className="text-xs text-gray-400 font-bold">{new Date(verdict.published_at).toLocaleString()}</span>
             </div>
          </div>

          <div className="p-8 md:p-12 grid grid-cols-12 gap-12">
             
             {/* Left Section: Economic Action */}
             <div className="col-span-12 lg:col-span-7 space-y-10">
                <div>
                   <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-[0.3em] mb-6 flex items-center gap-2">
                     <Coins className="w-4 h-4 text-amber-500" /> Economic Settlement
                   </h3>
                   <div className="bg-black/40 border border-white/5 rounded-2xl p-8 relative overflow-hidden group">
                      <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:scale-110 transition-transform">
                         <Zap className="w-24 h-24 text-white" />
                      </div>
                      <div className="space-y-6 relative z-10">
                         <div>
                            <span className="text-[9px] text-gray-500 uppercase font-black block mb-1">Settlement Action</span>
                            <span className="text-xl font-black text-white tracking-tight uppercase">{verdict.action.replace(/_/g, ' ')}</span>
                         </div>
                         <div className="flex justify-between items-end border-t border-white/5 pt-6">
                            <div>
                               <span className="text-[9px] text-gray-500 uppercase font-black block mb-1">Value Dispatched</span>
                               <span className="text-3xl font-black text-green-500 tracking-tighter">{verdict.dispute_value.toLocaleString()} <span className="text-sm font-bold text-gray-700">SATS</span></span>
                            </div>
                            <div className="text-right">
                               <span className="text-[9px] text-gray-500 uppercase font-black block mb-1">LND Status</span>
                               <span className="text-xs font-black text-white bg-indigo-500 px-2 py-1 rounded uppercase tracking-widest">SETTLED</span>
                            </div>
                         </div>
                      </div>
                   </div>
                </div>

                <div>
                   <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-[0.3em] mb-6">Cryptographic Audit</h3>
                   <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
                         <div className="flex items-center gap-4">
                            <Binary className="w-5 h-5 text-indigo-400" />
                            <div>
                               <span className="text-[9px] text-gray-500 uppercase font-black block">Manifest Hash</span>
                               <code className="text-[10px] text-gray-400 truncate w-48 block">{verdict.manifest_hash}</code>
                            </div>
                         </div>
                         <button className="p-2 hover:bg-white/10 rounded transition-colors"><Download className="w-4 h-4 text-gray-600" /></button>
                      </div>
                      <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
                         <div className="flex items-center gap-4">
                            <ShieldCheck className="w-5 h-5 text-green-500" />
                            <div>
                               <span className="text-[9px] text-gray-500 uppercase font-black block">Hardware Proof</span>
                               <span className="text-[10px] text-gray-400 uppercase font-black">7/7 TPM Signatures Validated</span>
                            </div>
                         </div>
                         <ChevronRight className="w-4 h-4 text-gray-800" />
                      </div>
                   </div>
                </div>
             </div>

             {/* Right Section: Juror Breakdown */}
             <div className="col-span-12 lg:col-span-5 space-y-8">
                <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-6 shadow-xl">
                   <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                     <Users className="w-4 h-4 text-indigo-500" /> Juror Quorum
                   </h3>
                   <div className="space-y-3">
                      {verdict.jurors.map((juror, i) => (
                        <div key={i} className="flex items-center justify-between group">
                           <div className="flex items-center gap-3">
                              <div className={`w-1.5 h-1.5 rounded-full ${juror.vote === 'APPROVE' ? 'bg-green-500' : 'bg-red-500'}`} />
                              <span className="text-[11px] font-bold text-gray-400 uppercase">{juror.id}</span>
                           </div>
                           <div className="flex items-center gap-3">
                              <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${juror.vote === 'APPROVE' ? 'text-green-500 border-green-500/20' : 'text-red-500 border-red-500/20'}`}>
                                {juror.vote}
                              </span>
                              <Fingerprint className="w-3.5 h-3.5 text-gray-800 group-hover:text-indigo-400 transition-colors" />
                           </div>
                        </div>
                      ))}
                   </div>
                   <div className="mt-8 pt-6 border-t border-white/5">
                      <div className="flex justify-between items-end mb-2">
                         <span className="text-[9px] text-gray-600 uppercase font-black">Majority Alignment</span>
                         <span className="text-xs font-black text-white">85.7%</span>
                      </div>
                      <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                         <div className="bg-indigo-500 h-full" style={{ width: '85.7%' }} />
                      </div>
                   </div>
                </div>

                <div className="p-6 bg-amber-500/5 border border-amber-500/20 rounded-xl relative overflow-hidden">
                   <div className="flex items-center gap-3 mb-3">
                      <Scale className="w-4 h-4 text-amber-500" />
                      <h4 className="text-[10px] font-black text-white uppercase tracking-widest">Legal Precedent</h4>
                   </div>
                   <p className="text-[10px] text-gray-500 leading-relaxed italic">
                      "This verdict has been recorded in the Protocol Case Law Registry. Future disputes of category HARDWARE_ATTESTATION_FAIL will reference this settlement logic."
                   </p>
                </div>
             </div>

          </div>

          {/* Action Footer */}
          <div className="p-8 bg-white/[0.02] border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6">
             <div className="flex items-center gap-6">
                <button className="flex items-center gap-2 text-[10px] font-black text-gray-500 hover:text-white transition-colors uppercase tracking-widest">
                   <FileText className="w-4 h-4" /> Export Judgment (PDF/A)
                </button>
                <div className="h-4 w-px bg-white/10 hidden md:block" />
                <button className="flex items-center gap-2 text-[10px] font-black text-gray-500 hover:text-white transition-colors uppercase tracking-widest">
                   <TrendingUp className="w-4 h-4" /> View Reputation Impact
                </button>
             </div>
             <button className="px-8 py-3 bg-white text-black font-black text-[10px] uppercase tracking-widest hover:bg-amber-500 transition-all rounded shadow-xl flex items-center gap-3">
                Finalize & Close Case <ArrowRight className="w-4 h-4" />
             </button>
          </div>
        </div>

        {/* Global Protocol Status */}
        <div className="mt-8 flex justify-between items-center px-4">
           <div className="flex items-center gap-3">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              <span className="text-[9px] font-black uppercase text-gray-600 tracking-widest">Consensus State: SYNCHRONIZED</span>
           </div>
           <div className="flex gap-6 text-[9px] font-black uppercase text-gray-800 tracking-widest">
              <span>[*] QUORUM_7_OF_7</span>
              <span>[*] SETTLEMENT_BLOCK_HEIGHT: 882932</span>
           </div>
        </div>

      </main>

    </div>
  );
};

export default App;
