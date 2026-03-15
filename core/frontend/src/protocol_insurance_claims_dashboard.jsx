import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Scale, 
  FileSearch, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Zap, 
  History, 
  Fingerprint, 
  Binary, 
  Activity, 
  RefreshCw, 
  ChevronRight, 
  Info, 
  Layers, 
  LayoutGrid, 
  Banknote,
  Search,
  Maximize2,
  Trash2,
  User,
  Clock,
  Cpu,
  FileText,
  ShieldAlert
} from 'lucide-react';

/**
 * PROXY PROTOCOL - INSURANCE CLAIMS DASHBOARD (v1.0)
 * "Final adjudication: Synchronizing evidence and capital."
 * ----------------------------------------------------
 */

const App = () => {
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [filter, setFilter] = useState('ALL');

  // Mock Insurance Claims Queue (Reflecting data from Exporter and Incident APIs)
  const [claims] = useState([
    {
      id: "CLM-8821-PX",
      type: "LND_FORCE_CLOSE",
      node_id: "NODE_ELITE_X29",
      amount: 50000,
      rep_score: 982,
      risk_rating: "LOW",
      status: "PENDING_AUDIT",
      timestamp: "2h ago",
      evidence_stack: {
        lnd_logs: "CHANNEL_FORCE_CLOSE_ERROR_v0.17",
        pcr_state: "NOMINAL",
        hardware_attestation: "0x8A2E...F91C (VERIFIED)"
      }
    },
    {
      id: "CLM-7714-PX",
      type: "TPM_CERT_DESYNC",
      node_id: "NODE_ALPHA_004",
      amount: 12500,
      rep_score: 845,
      risk_rating: "ELEVATED",
      status: "UNDER_REVIEW",
      timestamp: "5h ago",
      evidence_stack: {
        lnd_logs: "STABLE",
        pcr_state: "DRIFT_DETECTED (PCR 7)",
        hardware_attestation: "0x3B7C...D2A1 (MISMATCH)"
      }
    }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1200);
  };

  const handleAdjudicate = (verdict) => {
    setIsProcessing(true);
    // In production, this calls the InsuranceEngine API to trigger Keysend
    setTimeout(() => {
      setIsProcessing(false);
      setSelectedClaim(null);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-blue-500/30">
      
      {/* Background Grid Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header: Claims Desk */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl shadow-2xl">
              <Scale className="w-8 h-8 text-blue-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Claims Desk</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Satoshi Remediation // Protocol <span className="text-blue-400">v3.4.4</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Pool Liquidity</span>
                   <span className="text-xl font-black text-white tracking-tighter">10.45M <span className="text-[10px] text-blue-500">SATS</span></span>
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
          
          {/* Claims Queue (Left Column) */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <History className="w-4 h-4 text-blue-500" /> Resolution Feed
                   </h3>
                   <span className="text-[9px] text-gray-700 font-bold uppercase tracking-widest">v1.0 Queue</span>
                </div>

                <div className="divide-y divide-white/5">
                   {claims.map((claim) => (
                      <div 
                        key={claim.id} 
                        onClick={() => setSelectedClaim(claim)}
                        className={`p-6 hover:bg-blue-500/[0.02] transition-all cursor-pointer group ${selectedClaim?.id === claim.id ? 'bg-blue-500/[0.04]' : ''}`}
                      >
                         <div className="flex justify-between items-start mb-4">
                            <div>
                               <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-blue-400 transition-colors">{claim.id}</span>
                               <p className="text-[9px] text-gray-600 font-bold uppercase mt-1">{claim.type}</p>
                            </div>
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${
                              claim.risk_rating === 'LOW' ? 'bg-green-500/10 border-green-500/20 text-green-500' : 'bg-red-500/10 border-red-500/20 text-red-500'
                            }`}>
                               {claim.risk_rating} RISK
                            </span>
                         </div>
                         <div className="flex justify-between items-center mt-4 text-[9px] font-black text-gray-700 uppercase tracking-widest">
                            <span className="flex items-center gap-1.5"><Banknote className="w-3 h-3" /> {claim.amount.toLocaleString()} S</span>
                            <span>{claim.timestamp}</span>
                         </div>
                      </div>
                   ))}
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-blue-500/5 rounded-xl shadow-inner relative overflow-hidden group">
                <div className="absolute -bottom-6 -right-6 opacity-5 group-hover:scale-110 transition-transform">
                   <ShieldCheck className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-blue-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5" /> Adjudication Policy
                </h4>
                <p className="text-[11px] text-gray-500 leading-relaxed italic">
                   "Claim remediation is authorized ONLY for confirmed protocol desyncs or LND gateway failures. Physical tamper events or chassis intrusion alerts result in automatic claim rejection (Rule 8.4)."
                </p>
             </div>
          </div>

          {/* Forensic Adjudicator (Right Column) */}
          <div className="col-span-12 lg:col-span-8 flex flex-col h-full">
             {selectedClaim ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 shadow-2xl animate-in slide-in-from-right-4 duration-300 flex-1 flex flex-col gap-10">
                   <div className="flex justify-between items-start border-b border-white/5 pb-6">
                      <div>
                         <span className="text-[10px] text-blue-500 font-black uppercase tracking-[0.2em] block mb-1">Evidence Auditor</span>
                         <h2 className="text-3xl font-black text-white tracking-tighter uppercase">{selectedClaim.id}</h2>
                      </div>
                      <div className="flex items-center gap-4">
                         <button className="p-3 bg-white/5 border border-white/10 rounded hover:bg-white/10 transition-all text-gray-400"><Maximize2 className="w-4 h-4" /></button>
                         <button onClick={() => setSelectedClaim(null)} className="p-3 text-gray-600 hover:text-white transition-colors"><XCircle className="w-6 h-6" /></button>
                      </div>
                   </div>

                   {/* The Evidence Stack */}
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                      <div className="space-y-8">
                         <div>
                            <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                               <Cpu className="w-3.5 h-3.5 text-blue-500" /> Node Vitals
                            </h4>
                            <div className="space-y-4">
                               {[
                                 { label: 'Identity', val: selectedClaim.node_id, status: 'VERIFIED' },
                                 { label: 'Reputation', val: `${selectedClaim.rep_score} / 1000`, status: 'STABLE' },
                                 { label: 'Hardware ID', val: 'INFINEON_OPTIGA_V1.1', status: 'LOCKED' }
                               ].map((item, i) => (
                                 <div key={i} className="flex justify-between items-center p-4 bg-black border border-white/5 rounded-lg group hover:border-blue-500/30 transition-all">
                                    <div>
                                       <span className="text-[9px] text-gray-700 font-black uppercase block">{item.label}</span>
                                       <span className="text-xs font-bold text-gray-400">{item.val}</span>
                                    </div>
                                    <ShieldCheck className={`w-4 h-4 ${item.status === 'VERIFIED' ? 'text-green-500' : 'text-gray-800'}`} />
                                 </div>
                               ))}
                            </div>
                         </div>
                      </div>

                      <div className="space-y-8">
                         <div>
                            <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                               <Binary className="w-3.5 h-3.5 text-indigo-500" /> Forensic Logs
                            </h4>
                            <div className="bg-black border border-white/5 rounded-xl p-6 font-mono text-[10px] space-y-4 shadow-inner">
                               <div className="flex justify-between items-center">
                                  <span className="text-gray-600 uppercase">LND STATUS</span>
                                  <span className="text-blue-500 font-black uppercase">{selectedClaim.evidence_stack.lnd_logs}</span>
                               </div>
                               <div className="flex justify-between items-center">
                                  <span className="text-gray-600 uppercase">PCR INTEGRITY</span>
                                  <span className={selectedClaim.evidence_stack.pcr_state.includes('DRIFT') ? 'text-red-500 font-bold' : 'text-green-500'}>
                                    {selectedClaim.evidence_stack.pcr_state}
                                  </span>
                               </div>
                               <div className="pt-4 border-t border-white/5">
                                  <span className="text-[9px] text-gray-600 uppercase block mb-1">Attestation Quote</span>
                                  <code className="text-gray-500 break-all">{selectedClaim.evidence_stack.hardware_attestation}</code>
                               </div>
                            </div>
                         </div>
                      </div>
                   </div>

                   {/* Decision Controls */}
                   <div className="mt-auto pt-8 border-t border-white/5 flex flex-col md:flex-row gap-6 items-center">
                      <div className="flex items-center gap-4 flex-1 bg-white/[0.02] border border-white/5 p-4 rounded-xl shadow-inner">
                         <AlertTriangle className="w-10 h-10 text-blue-500 shrink-0" />
                         <p className="text-[11px] text-gray-500 leading-relaxed font-medium">
                           Adjuster review of <span className="text-white">{selectedClaim.id}</span> confirms {selectedClaim.risk_rating === 'LOW' ? 'no physical intrusion detected' : 'systemic drift recorded'}. Payout requires Foundation Master Key sign-off.
                         </p>
                      </div>
                      <div className="flex gap-4 w-full md:w-auto">
                         <button 
                           onClick={() => handleAdjudicate('APPROVED')}
                           disabled={isProcessing}
                           className="px-8 py-5 bg-blue-600 text-white font-black text-xs uppercase tracking-[0.2em] hover:bg-blue-500 transition-all rounded shadow-2xl flex items-center justify-center gap-3 whitespace-nowrap"
                         >
                            {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Banknote className="w-4 h-4" />}
                            Authorize Payout
                         </button>
                         <button 
                           onClick={() => handleAdjudicate('REJECTED')}
                           disabled={isProcessing}
                           className="px-8 py-5 bg-white/5 border border-white/10 text-gray-500 font-black text-xs uppercase tracking-widest hover:text-red-500 hover:border-red-500/50 transition-all rounded"
                         >
                            Reject Claim
                         </button>
                      </div>
                   </div>
                </div>
             ) : (
                <div className="h-full border-2 border-white/5 border-dashed rounded-2xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale transition-all">
                   <ShieldAlert className="w-20 h-20 text-gray-800 mb-8 animate-pulse" />
                   <h3 className="text-lg font-black text-gray-600 uppercase tracking-[0.3em] mb-3">Claims Desk Ready</h3>
                   <p className="text-xs text-gray-800 font-bold uppercase tracking-widest max-w-sm">Select a remediation ticket from the feed to initiate evidence stack auditing and Satoshi settlement.</p>
                </div>
             )}
          </div>

        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity relative z-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-ping shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Remediation Engine Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Due process for the biological edge."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] POOL_STATE: SOLVENT</span>
            <span>[*] AUDIT_QUORUM: OK</span>
            <span>[*] VERSION: v3.4.4</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
