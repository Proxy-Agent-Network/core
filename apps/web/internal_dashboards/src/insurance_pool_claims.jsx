import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Wallet, 
  Banknote, 
  ArrowDownCircle, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Info, 
  Zap, 
  Lock, 
  ExternalLink,
  ChevronRight,
  Database,
  History,
  AlertTriangle,
  Fingerprint
} from 'lucide-react';

/**
 * PROXY PROTOCOL - INSURANCE POOL CLAIMS UI (v1.0)
 * "The final mile of Satoshi remediation."
 * ----------------------------------------------------
 */

const App = () => {
  const [isWithdrawing, setIsWithdrawing] = useState(false);
  const [withdrawComplete, setWithdrawComplete] = useState(false);
  const [nodeId] = useState("NODE_ELITE_X29");

  // Mock Claims Data for the current Node
  const [claims] = useState([
    { 
      id: "CLAIM-882-1", 
      type: "LND_FORCE_CLOSE", 
      amount: 50000, 
      status: "APPROVED_PENDING_WITHDRAWAL", 
      approved_at: "2026-02-11T20:15:00Z",
      verdict_ref: "VERDICT-8829-APP"
    },
    { 
      id: "CLAIM-774-4", 
      type: "TPM_CERT_DESYNC", 
      amount: 12500, 
      status: "SETTLED", 
      approved_at: "2026-02-08T09:12:00Z",
      verdict_ref: "FORENSIC-AUTO-CLEAR"
    }
  ]);

  const pendingAmount = claims
    .filter(c => c.status === 'APPROVED_PENDING_WITHDRAWAL')
    .reduce((acc, curr) => acc + curr.amount, 0);

  const handleWithdraw = () => {
    setIsWithdrawing(true);
    // Simulate LND Keysend / Invoice Settlement
    setTimeout(() => {
      setIsWithdrawing(false);
      setWithdrawComplete(true);
    }, 2500);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-blue-500/30">
      
      {/* Background Grid Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-4xl w-full relative z-10 space-y-8">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl shadow-2xl">
              <ShieldCheck className="w-8 h-8 text-blue-500" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Approved Payouts</h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Node Recovery Portal // {nodeId}</p>
            </div>
          </div>

          <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
             <div className="flex flex-col items-end">
                <span className="text-[9px] text-gray-600 uppercase font-black">Settled to Date</span>
                <span className="text-xl font-black text-white tracking-tighter">1,242,500 <span className="text-[10px] text-gray-600">SATS</span></span>
             </div>
          </div>
        </header>

        {/* Withdrawal Section */}
        <section className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-10 shadow-2xl relative overflow-hidden group">
           <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:scale-110 transition-transform pointer-events-none">
              <Wallet className="w-32 h-32 text-white" />
           </div>

           <div className="relative z-10">
              {withdrawComplete ? (
                <div className="text-center py-6 animate-in zoom-in-95 duration-500">
                   <div className="w-20 h-20 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_40px_rgba(34,197,94,0.1)]">
                      <CheckCircle2 className="w-10 h-10 text-green-500" />
                   </div>
                   <h2 className="text-2xl font-black text-white uppercase tracking-tighter mb-2">Sats Dispatched</h2>
                   <p className="text-xs text-gray-500 mb-8 max-w-xs mx-auto leading-relaxed">
                     Funds have been pushed to your Node's Lightning address via spontaneous keysend. Check your local LND logs for confirmation.
                   </p>
                   <button 
                     onClick={() => setWithdrawComplete(false)}
                     className="px-8 py-2 border border-white/10 text-gray-500 text-[10px] font-black uppercase tracking-widest hover:text-white transition-all rounded"
                   >
                     Acknowledge
                   </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-12 gap-12 items-center">
                   <div className="md:col-span-7">
                      <span className="text-[10px] text-blue-500 font-black uppercase tracking-[0.2em] block mb-2">Available for Withdrawal</span>
                      <div className="flex items-baseline gap-3 mb-6">
                         <span className="text-5xl font-black text-white tracking-tighter">{pendingAmount.toLocaleString()}</span>
                         <span className="text-sm font-bold text-gray-600 uppercase">Satoshis</span>
                      </div>
                      <p className="text-xs text-gray-500 leading-relaxed mb-4 italic font-medium">
                        "Your insurance claims have been reviewed by the High Court and approved for immediate payout. These funds originate from the 0.1% protocol-wide liquidity reserve."
                      </p>
                   </div>
                   <div className="md:col-span-5">
                      <button 
                        onClick={handleWithdraw}
                        disabled={pendingAmount === 0 || isWithdrawing}
                        className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-blue-500 hover:text-white transition-all flex items-center justify-center gap-3 shadow-[0_0_30px_rgba(255,255,255,0.1)] disabled:opacity-20"
                      >
                        {isWithdrawing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                        {isWithdrawing ? 'Settling HTLC...' : 'Withdraw to Node'}
                      </button>
                      <div className="mt-6 p-4 bg-indigo-500/5 border border-indigo-500/20 rounded-lg flex items-center gap-3">
                         <Lock className="w-4 h-4 text-indigo-400" />
                         <span className="text-[9px] text-gray-500 font-bold uppercase leading-tight">
                           Authenticated via TPM_IDENTITY_X29<br/>
                           Address: 03a2...821f@node.proxy
                         </span>
                      </div>
                   </div>
                </div>
              )}
           </div>
        </section>

        {/* Breakdown Table */}
        <section className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
          <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-8">
            <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-3">
              <History className="w-4 h-4 text-gray-600" /> Claim Resolution Ledger
            </h3>
            <span className="text-[9px] text-gray-600 font-black uppercase">Historical Remediation</span>
          </div>

          <div className="divide-y divide-white/5">
             {claims.map((claim) => (
               <div key={claim.id} className="p-6 flex items-center justify-between group hover:bg-white/[0.01] transition-all">
                  <div className="flex items-center gap-6">
                     <div className={`w-10 h-10 rounded border flex items-center justify-center ${claim.status.includes('PENDING') ? 'bg-amber-500/10 border-amber-500/20 text-amber-500 animate-pulse' : 'bg-green-500/10 border-green-500/20 text-green-500'}`}>
                        {claim.status.includes('PENDING') ? <Clock className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}
                     </div>
                     <div>
                        <div className="flex items-center gap-3 mb-0.5">
                           <span className="text-[11px] font-black text-white uppercase tracking-tight group-hover:text-blue-400 transition-colors">{claim.id}</span>
                           <span className="text-[8px] bg-white/5 px-1.5 py-0.5 rounded text-gray-600 font-bold uppercase tracking-widest">{claim.type}</span>
                        </div>
                        <div className="flex items-center gap-4 text-[9px] text-gray-700 font-bold uppercase tracking-widest">
                           <span className="flex items-center gap-1"><Database className="w-2.5 h-2.5" /> Verdict: {claim.verdict_ref}</span>
                           <span>|</span>
                           <span>Approved {new Date(claim.approved_at).toLocaleDateString()}</span>
                        </div>
                     </div>
                  </div>

                  <div className="text-right flex items-center gap-8">
                     <div>
                        <span className="text-sm font-black text-white block mb-0.5">{claim.amount.toLocaleString()} SATS</span>
                        <span className={`text-[9px] font-black uppercase ${claim.status === 'SETTLED' ? 'text-gray-700' : 'text-amber-500'}`}>
                          {claim.status.replace(/_/g, ' ')}
                        </span>
                     </div>
                     <ChevronRight className="w-4 h-4 text-gray-900 group-hover:text-white transition-colors" />
                  </div>
               </div>
             ))}
          </div>

          <div className="p-6 bg-white/[0.01] border-t border-white/5">
             <div className="flex items-start gap-4">
                <Info className="w-5 h-5 text-gray-600 shrink-0" />
                <p className="text-[10px] text-gray-600 leading-relaxed italic">
                  Note: Payouts are generated by the Protocol Reserve Treasury. In rare cases of pool insolvency (Actuary Alert zones), withdrawals may be queued until the next epoch collection sweep.
                </p>
             </div>
          </div>
        </section>

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-4xl mx-auto w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">LND Gateway Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Settlement Block: 882932</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] CHANNEL_STATE: OPTIMAL</span>
            <span>[*] VERSION: v2.9.0</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
