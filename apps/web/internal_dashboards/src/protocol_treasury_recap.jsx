import React, { useState } from 'react';
import { 
  History, 
  ShieldCheck, 
  Zap, 
  Hash, 
  Users, 
  CheckCircle2, 
  Clock, 
  ExternalLink, 
  ArrowRight, 
  Gavel, 
  Fingerprint, 
  Database,
  Search,
  Filter,
  RefreshCw,
  Info,
  Layers,
  Activity,
  FileText,
  ChevronRight,
  XCircle
} from 'lucide-react';

/**
 * PROXY PROTOCOL - TREASURY RECAP UI (v1.0)
 * "The forensic audit trail of decentralized payouts."
 * ----------------------------------------------------
 */

const App = () => {
  const [selectedAudit, setSelectedAudit] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock Payout Audit Data
  const [payouts] = useState([
    {
      id: "PAYOUT-882-X29",
      claim_id: "CLAIM-882-1",
      verdict_id: "VERDICT-8829-APP",
      node_id: "NODE_ELITE_X29",
      amount: 50000,
      timestamp: "2026-02-11T21:45:00Z",
      txid: "3045022100...deadbeef_tx",
      status: "FINALIZED",
      signatures: 7,
      attestation_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    {
      id: "PAYOUT-771-A01",
      claim_id: "CLAIM-771-4",
      verdict_id: "FORENSIC-AUTO-CLEAR",
      node_id: "NODE_ALPHA_001",
      amount: 12500,
      timestamp: "2026-02-10T10:12:00Z",
      txid: "f91c3b2e...c442_tx",
      status: "FINALIZED",
      signatures: 1, // Auto-audit only requires Oracle sig
      attestation_hash: "3b7c89f...9a21"
    }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1200);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30">
      
      {/* Background Decorative Element */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl mx-auto relative z-10 space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-[0_0_20px_rgba(99,102,241,0.1)]">
              <History className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Treasury Recap</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Payout Audit Trail // Protocol <span className="text-indigo-400">v2.9.2</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Total Settle (24h)</span>
                   <span className="text-xl font-black text-white tracking-tighter">62,500 <span className="text-[10px] text-gray-600">SATS</span></span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <button 
                  onClick={handleRefresh}
                  className={`p-2 border border-white/10 rounded hover:bg-white/5 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
                >
                  <RefreshCw className="w-4 h-4 text-gray-500" />
                </button>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Audit Timeline */}
          <div className="col-span-12 lg:col-span-7 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-8">
                   <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                     <Layers className="w-4 h-4 text-indigo-500" /> Settlement Sequence
                   </h3>
                   <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Epoch 88294 Active</span>
                </div>

                <div className="divide-y divide-white/5">
                   {payouts.map((audit) => (
                      <div 
                        key={audit.id} 
                        onClick={() => setSelectedAudit(audit)}
                        className={`p-8 hover:bg-white/[0.01] transition-all cursor-pointer group flex flex-col md:flex-row justify-between items-start md:items-center gap-6 ${selectedAudit?.id === audit.id ? 'bg-indigo-500/[0.03]' : ''}`}
                      >
                         <div className="flex items-center gap-6 flex-1">
                            <div className="w-12 h-12 rounded-lg bg-green-500/5 border border-green-500/20 flex items-center justify-center text-green-500 group-hover:scale-110 transition-transform">
                               <Zap className="w-6 h-6" />
                            </div>
                            <div>
                               <div className="flex items-center gap-3 mb-1">
                                  <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-indigo-400 transition-colors">
                                     {audit.id}
                                  </span>
                                  <span className="text-[9px] bg-white/5 px-1.5 py-0.5 rounded text-gray-600 font-black uppercase tracking-widest">
                                    {audit.signatures === 7 ? 'HIGH_COURT' : 'AUTO_AUDIT'}
                                  </span>
                               </div>
                               <p className="text-sm text-gray-500 font-bold uppercase tracking-tight mb-2">Claim: {audit.claim_id} &rarr; {audit.node_id}</p>
                               <div className="flex items-center gap-4 text-[9px] text-gray-700 font-black uppercase tracking-widest">
                                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {new Date(audit.timestamp).toLocaleString()}</span>
                                  <span>|</span>
                                  <span className="flex items-center gap-1"><Hash className="w-3 h-3" /> TX: {audit.txid.substring(0, 12)}...</span>
                               </div>
                            </div>
                         </div>
                         <div className="flex items-center gap-4">
                            <div className="text-right flex flex-col items-end">
                               <span className="text-[9px] text-gray-700 uppercase font-black mb-1">Released</span>
                               <span className="text-lg font-black text-white tracking-tighter">{audit.amount.toLocaleString()} <span className="text-[10px] text-gray-800 font-bold">S</span></span>
                            </div>
                            <ChevronRight className={`w-5 h-5 transition-transform ${selectedAudit?.id === audit.id ? 'rotate-90 text-indigo-500' : 'text-gray-800'}`} />
                         </div>
                      </div>
                   ))}
                </div>
                
                <button className="w-full py-4 bg-white/[0.02] hover:bg-white/[0.05] text-[10px] font-black uppercase tracking-[0.3em] text-gray-600 hover:text-white transition-all border-t border-white/5">
                   Sync Ledger with LND Wallet
                </button>
             </div>

             <div className="p-8 border border-white/10 bg-[#0a0a0a] rounded-xl shadow-inner relative overflow-hidden group">
                <div className="absolute -bottom-6 -right-6 opacity-[0.02] group-hover:scale-110 transition-transform">
                   <ShieldCheck className="w-32 h-32 text-white" />
                </div>
                <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5 text-indigo-500" /> Audit Compliance
                </h4>
                <p className="text-xs text-gray-500 leading-relaxed italic">
                   "All insurance payouts are cross-verified against finalized verdict manifests stored in the persistent registry. This prevents double-spending and unauthorized pool depletion."
                </p>
             </div>
          </div>

          {/* Forensic Drilldown */}
          <div className="col-span-12 lg:col-span-5">
             {selectedAudit ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-8 shadow-2xl animate-in slide-in-from-right-4 duration-300 space-y-8 h-full flex flex-col">
                   <div className="flex justify-between items-start border-b border-white/5 pb-6">
                      <div>
                         <span className="text-[10px] text-indigo-400 font-black uppercase tracking-widest block mb-1">Audit Breakdown</span>
                         <h2 className="text-2xl font-black text-white tracking-tighter uppercase">{selectedAudit.id}</h2>
                      </div>
                      <CheckCircle2 className="w-6 h-6 text-green-500" />
                   </div>

                   <div className="space-y-6">
                      <div>
                         <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Gavel className="w-3.5 h-3.5" /> Verdict Finality
                         </h4>
                         <div className="p-4 bg-black border border-white/5 rounded-lg space-y-3">
                            <div className="flex justify-between items-center text-xs">
                               <span className="text-gray-500 font-bold uppercase tracking-tighter">Manifest ID</span>
                               <span className="text-white font-mono">{selectedAudit.verdict_id}</span>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                               <span className="text-gray-500 font-bold uppercase tracking-tighter">Consensus Reach</span>
                               <span className="text-green-500 font-black">{selectedAudit.signatures}/7 Signed</span>
                            </div>
                            <div className="pt-2 border-t border-white/5">
                               <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Attestation Hash</span>
                               <code className="text-[10px] text-gray-400 break-all leading-tight">{selectedAudit.attestation_hash}</code>
                            </div>
                         </div>
                      </div>

                      <div>
                         <h4 className="text-[10px] font-black text-gray-600 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Database className="w-3.5 h-3.5" /> Economic Proof
                         </h4>
                         <div className="space-y-4">
                            <div className="p-4 bg-white/5 rounded-lg border border-white/5 flex justify-between items-center group hover:border-indigo-500/30 transition-all">
                               <div className="flex items-center gap-4">
                                  <Zap className="w-4 h-4 text-green-500" />
                                  <div>
                                     <span className="text-[9px] text-gray-500 uppercase font-black block">Lightning TXID</span>
                                     <span className="text-[10px] text-white font-mono">{selectedAudit.txid.substring(0, 24)}...</span>
                                  </div>
                               </div>
                               <ExternalLink className="w-3 h-3 text-gray-700 group-hover:text-white" />
                            </div>
                            <div className="p-4 bg-white/5 rounded-lg border border-white/5 flex justify-between items-center group hover:border-indigo-500/30 transition-all">
                               <div className="flex items-center gap-4">
                                  <Fingerprint className="w-4 h-4 text-indigo-500" />
                                  <div>
                                     <span className="text-[9px] text-gray-500 uppercase font-black block">Hardware Receiver</span>
                                     <span className="text-[10px] text-white font-mono">{selectedAudit.node_id}</span>
                                  </div>
                               </div>
                               <ChevronRight className="w-3 h-3 text-gray-700" />
                            </div>
                         </div>
                      </div>
                   </div>

                   <div className="mt-auto pt-8 border-t border-white/5 space-y-3">
                      <button className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-widest hover:bg-indigo-500 hover:text-white transition-all flex items-center justify-center gap-3">
                         <FileText className="w-4 h-4" /> Export Audit Receipt (PDF/A)
                      </button>
                      <button className="w-full py-3 text-[9px] font-black text-gray-600 hover:text-white uppercase tracking-[0.2em] transition-all">
                         View Governance Discussion &rarr;
                      </button>
                   </div>
                </div>
             ) : (
                <div className="h-full border border-white/5 border-dashed rounded-xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale">
                   <Activity className="w-16 h-16 text-gray-800 mb-6 animate-pulse" />
                   <h3 className="text-xs font-black text-gray-600 uppercase tracking-widest mb-2">Audit Drilldown Required</h3>
                   <p className="text-[10px] text-gray-800 uppercase font-bold tracking-tighter max-w-xs">Select a finalized payout from the timeline to view cryptographic proof and hardware signatures.</p>
                </div>
             )}
          </div>

        </div>

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-6xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Payout Auditor Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Settlement Block: 882932</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] TOTAL_CLAIMS: 18,422</span>
            <span>[*] RECOVERY_RATE: 82%</span>
            <span>[*] VERSION: v2.9.2</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
