import React, { useState } from 'react';
import { 
  ShieldCheck, 
  FileWarning, 
  History, 
  ArrowRight, 
  Upload, 
  Lock, 
  Info, 
  AlertCircle,
  Clock,
  ExternalLink,
  ChevronRight,
  Database,
  Search,
  CheckCircle2,
  XCircle,
  FileText,
  Activity,
  Plus
} from 'lucide-react';

/**
 * PROXY PROTOCOL - INSURANCE CLAIM PORTAL (v1.0)
 * "The due process layer for biological nodes."
 * ----------------------------------------------------
 */

const App = () => {
  const [view, setView] = useState('DASHBOARD'); // DASHBOARD, NEW_CLAIM
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [claimSubmitted, setClaimSubmitted] = useState(false);

  // Mock Node Identity
  const [nodeId] = useState("NODE_ELITE_X29");

  // Mock Pool Stats
  const [poolStats] = useState({
    total_liquidity: 10450200,
    active_claims: 3,
    avg_resolution_time: "48h",
    payout_ratio: "82%"
  });

  // Mock History
  const [myClaims] = useState([
    { id: "CLAIM-8821", type: "LND_CHANNEL_FORCE_CLOSE", amount: 50000, status: "APPROVED", time: "2026-01-14" },
    { id: "CLAIM-7740", type: "TPM_CERT_DESYNC", amount: 12500, status: "REJECTED", time: "2025-12-05" }
  ]);

  const handleFileClaim = (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    // Simulate TPM-signed evidence binding
    setTimeout(() => {
      setIsSubmitting(false);
      setClaimSubmitted(true);
      setTimeout(() => {
        setClaimSubmitted(false);
        setView('DASHBOARD');
      }, 3000);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30">
      
      {/* Background Decorative Element */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-5xl mx-auto relative z-10">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 border-b border-white/10 pb-8 gap-6">
          <div>
            <div className="flex items-center gap-4 mb-3">
              <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
                <ShieldCheck className="w-8 h-8 text-indigo-500" />
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Insurance Center</h1>
                <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold">Node Identity: <span className="text-indigo-400">{nodeId}</span></p>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Pool Reserves</span>
                   <span className="text-xl font-black text-white tracking-tighter">{(poolStats.total_liquidity / 1000000).toFixed(2)}M <span className="text-[10px] text-gray-600">SATS</span></span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Resolution</span>
                   <span className="text-xl font-black text-green-500 tracking-tighter">{poolStats.avg_resolution_time}</span>
                </div>
             </div>
          </div>
        </header>

        {view === 'DASHBOARD' ? (
          <div className="space-y-8 animate-in fade-in duration-500">
            
            {/* Action Card */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
               <div className="p-8 border border-white/10 bg-indigo-500/5 rounded-xl flex flex-col justify-between group hover:border-indigo-500/30 transition-all">
                  <div>
                    <FileWarning className="w-12 h-12 text-indigo-500 mb-6 group-hover:scale-110 transition-transform" />
                    <h2 className="text-xl font-black text-white uppercase tracking-tight mb-4">Contest a Slash</h2>
                    <p className="text-xs text-gray-500 leading-relaxed mb-8">
                      Was your bond slashed by a protocol error? File a claim to have your logs reviewed by the Foundation and recover lost Satoshis.
                    </p>
                  </div>
                  <button 
                    onClick={() => setView('NEW_CLAIM')}
                    className="w-full py-4 bg-indigo-500 text-black font-black text-xs uppercase tracking-widest hover:bg-indigo-400 transition-all"
                  >
                    File New Claim
                  </button>
               </div>

               <div className="p-8 border border-white/10 bg-[#0a0a0a] rounded-xl flex flex-col justify-between shadow-2xl">
                  <div>
                    <Activity className="w-12 h-12 text-gray-700 mb-6" />
                    <h2 className="text-xl font-black text-white uppercase tracking-tight mb-4">Pool Governance</h2>
                    <p className="text-xs text-gray-500 leading-relaxed mb-8 italic">
                      "The insurance pool is funded by a 0.1% protocol tax on all tasks. It exists solely to compensate operators for SEV-1 and SEV-2 failures."
                    </p>
                  </div>
                  <div className="flex justify-between items-center text-[10px] font-black uppercase text-gray-600">
                     <span>Payout Probability</span>
                     <span className="text-green-500">{poolStats.payout_ratio}</span>
                  </div>
               </div>
            </div>

            {/* Claims History Table */}
            <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
              <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center">
                <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
                  <History className="w-4 h-4 text-gray-500" /> Recent Claims History
                </h3>
                <span className="text-[9px] text-gray-600 font-bold uppercase">{myClaims.length} Records Found</span>
              </div>
              <div className="divide-y divide-white/5">
                {myClaims.map((claim) => (
                  <div key={claim.id} className="p-6 flex items-center justify-between hover:bg-white/[0.01] transition-colors group">
                    <div className="flex items-center gap-6">
                      <div className={`w-10 h-10 rounded border flex items-center justify-center ${claim.status === 'APPROVED' ? 'bg-green-500/10 border-green-500/20 text-green-500' : 'bg-red-500/10 border-red-500/20 text-red-500'}`}>
                         {claim.status === 'APPROVED' ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                      </div>
                      <div>
                        <span className="text-[11px] font-black text-white uppercase tracking-tighter block mb-0.5 group-hover:text-indigo-400 transition-colors">{claim.id}</span>
                        <span className="text-[9px] text-gray-600 uppercase font-bold tracking-widest">{claim.type}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-8">
                       <div className="text-right">
                          <span className="text-xs font-black text-white block mb-0.5">{claim.amount.toLocaleString()} SATS</span>
                          <span className="text-[9px] text-gray-700 uppercase font-black">{claim.time}</span>
                       </div>
                       <ChevronRight className="w-4 h-4 text-gray-800" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="animate-in slide-in-from-right-4 duration-500">
             <button 
               onClick={() => setView('DASHBOARD')}
               className="text-[10px] text-gray-500 hover:text-white font-black uppercase mb-6 flex items-center gap-2 transition-colors"
             >
               &larr; Cancel Request
             </button>

             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-10 shadow-2xl max-w-2xl mx-auto">
                {claimSubmitted ? (
                  <div className="text-center py-12 animate-in zoom-in-95 duration-500">
                    <div className="w-20 h-20 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_30px_rgba(34,197,94,0.1)]">
                       <CheckCircle2 className="w-10 h-10 text-green-500" />
                    </div>
                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-2">Claim Filed</h2>
                    <p className="text-xs text-gray-500 mb-8 max-w-xs mx-auto leading-relaxed">
                      Your forensic evidence has been hardware-signed and uploaded. A technical auditor will review the logs within 48 hours.
                    </p>
                    <div className="p-3 bg-black border border-white/5 rounded mono text-[9px] text-gray-600">
                      TICKET_ID: CLM-882-99-ALPHA
                    </div>
                  </div>
                ) : (
                  <form onSubmit={handleFileClaim} className="space-y-8">
                    <div className="border-b border-white/5 pb-6">
                       <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-2">New Insurance Claim</h2>
                       <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold">Proof of Technical Error Required</p>
                    </div>

                    <div className="space-y-6">
                       <div>
                          <label className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-3 block">Incident Classification</label>
                          <select className="w-full bg-black border border-white/10 p-4 rounded text-xs text-gray-400 focus:outline-none focus:border-indigo-500 uppercase tracking-widest font-bold">
                             <option>LND_CHANNEL_FORCE_CLOSE</option>
                             <option>TPM_ATTESTATION_FAIL_PX_400</option>
                             <option>HTLC_TIMEOUT_BUG</option>
                             <option>OTHER_PROTOCOL_FAILURE</option>
                          </select>
                       </div>

                       <div className="grid grid-cols-2 gap-6">
                          <div>
                             <label className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-3 block">Loss Amount (Sats)</label>
                             <input type="number" placeholder="50000" className="w-full bg-black border border-white/10 p-4 rounded text-xs text-white focus:outline-none focus:border-indigo-500" required />
                          </div>
                          <div>
                             <label className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-3 block">Related Task ID</label>
                             <input type="text" placeholder="T-9901" className="w-full bg-black border border-white/10 p-4 rounded text-xs text-white focus:outline-none focus:border-indigo-500 uppercase" required />
                          </div>
                       </div>

                       <div>
                          <label className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-3 block">Forensic Log Upload</label>
                          <div className="border-2 border-dashed border-white/5 rounded-xl p-8 text-center hover:border-indigo-500/30 transition-all cursor-pointer group">
                             <Upload className="w-8 h-8 text-gray-700 mx-auto mb-3 group-hover:text-indigo-500 transition-colors" />
                             <span className="text-[10px] text-gray-600 font-black uppercase tracking-widest">Attach Node Daemon Logs (.json/.txt)</span>
                          </div>
                       </div>
                    </div>

                    <div className="pt-4">
                       <div className="p-4 bg-yellow-500/5 border border-yellow-500/10 rounded-lg flex items-start gap-4 mb-8">
                          <AlertCircle className="w-5 h-5 text-yellow-500 shrink-0" />
                          <p className="text-[9px] text-gray-500 leading-relaxed italic">
                            "Filing a fraudulent insurance claim is a SEV-2 security incident. If logs are found to be forged, your entire bond will be slashed and your node will be permanently banned."
                          </p>
                       </div>
                       
                       <button 
                         type="submit"
                         disabled={isSubmitting}
                         className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-500 transition-all flex items-center justify-center gap-3"
                       >
                         {isSubmitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
                         {isSubmitting ? 'Signing Claim...' : 'Hardware Sign & Submit'}
                       </button>
                    </div>
                  </form>
                )}
             </div>
          </div>
        )}

      </main>

      {/* Footer System Status */}
      <footer className="max-w-5xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded p-4 font-mono text-[9px] text-gray-600 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-gray-600" />
            <span className="uppercase tracking-widest font-black">Insurance Protocol Active</span>
         </div>
         <div className="flex gap-6 uppercase font-bold tracking-tighter">
            <span>Pool Liquidity: OK</span>
            <span>Auditors Online: 12</span>
            <span>Epoch: 2026.02.11</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
