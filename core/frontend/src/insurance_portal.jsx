import React, { useState } from 'react';
import { 
  ShieldCheck, AlertCircle, Banknote, History, 
  Search, Filter, CheckCircle2, XCircle, 
  Info, ExternalLink, ArrowUpRight, ShieldAlert,
  Download, Clock, RefreshCw, FileText
} from 'lucide-react';

const App = () => {
  const [activeTab, setActiveTab] = useState('pending');
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Mock Insurance State
  const [poolStats] = useState({
    balance_sats: 10450200,
    total_paid_out: 2450000,
    loss_ratio: 14.8,
    active_claims: 2
  });

  const [claims] = useState([
    {
      id: "CLAIM-882-1",
      node_id: "NODE_ELITE_X29",
      amount: 50000,
      type: "LND_FORCE_CLOSE_ERROR",
      status: "PENDING",
      time: "2h ago",
      description: "Node suffered involuntary channel closure during high-value task settlement. Proof logs indicate LND v0.17.4-beta bug.",
      rep_score: 982
    },
    {
      id: "CLAIM-774-9",
      node_id: "NODE_ALPHA_001",
      amount: 12500,
      type: "TPM_ATTESTATION_FAIL",
      status: "PENDING",
      time: "5h ago",
      description: "Hardware attestation failed due to kernel update desync. Operator requesting refund of accidental bond slash.",
      rep_score: 965
    }
  ]);

  const handleAdjudicate = (verdict) => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setSelectedClaim(null);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-6 selection:bg-blue-500/30">
      
      {/* Header */}
      <header className="flex justify-between items-end mb-8 border-b border-white/10 pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-500/10 border border-blue-500/20 rounded">
              <ShieldCheck className="w-6 h-6 text-blue-500" />
            </div>
            <h1 className="text-xl font-black text-white tracking-tighter uppercase">Insurance Auditor</h1>
          </div>
          <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500">Internal Protocol Desk // Pool Liquidity v1.0</p>
        </div>

        <div className="flex gap-4">
           <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl">
              <div className="flex flex-col items-end">
                 <span className="text-[9px] text-gray-600 uppercase font-black">Pool Depth</span>
                 <span className="text-xl font-black text-blue-400 tracking-tighter">{(poolStats.balance_sats / 1000000).toFixed(2)}M <span className="text-[10px] text-gray-600">SATS</span></span>
              </div>
              <div className="h-8 w-px bg-white/10" />
              <div className="flex flex-col items-end">
                 <span className="text-[9px] text-gray-600 uppercase font-black">Loss Ratio</span>
                 <span className="text-xl font-black text-green-500 tracking-tighter">{poolStats.loss_ratio}%</span>
              </div>
           </div>
        </div>
      </header>

      <div className="grid grid-cols-12 gap-8">
        
        {/* Claims List */}
        <div className="col-span-12 lg:col-span-7 space-y-6">
          <div className="bg-[#0a0a0a] border border-white/5 rounded-lg overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center">
              <h3 className="text-xs font-black text-white uppercase tracking-widest flex items-center gap-2">
                <History className="w-4 h-4 text-blue-500" /> Claims Queue
              </h3>
              <div className="flex gap-2">
                <button onClick={() => setActiveTab('pending')} className={`px-3 py-1 text-[9px] font-black rounded ${activeTab === 'pending' ? 'bg-blue-500 text-white' : 'text-gray-500'}`}>PENDING</button>
                <button onClick={() => setActiveTab('history')} className={`px-3 py-1 text-[9px] font-black rounded ${activeTab === 'history' ? 'bg-blue-500 text-white' : 'text-gray-500'}`}>HISTORY</button>
              </div>
            </div>
            
            <div className="divide-y divide-white/5">
              {claims.map((claim) => (
                <div 
                  key={claim.id} 
                  onClick={() => setSelectedClaim(claim)}
                  className={`p-6 hover:bg-white/[0.01] transition-all cursor-pointer group ${selectedClaim?.id === claim.id ? 'bg-blue-500/[0.03]' : ''}`}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <span className="text-[11px] font-black text-white group-hover:text-blue-400 transition-colors">{claim.id}</span>
                        <span className="text-[9px] bg-white/5 px-1.5 py-0.5 rounded text-gray-500 font-bold tracking-tighter uppercase">{claim.type}</span>
                      </div>
                      <p className="text-[10px] text-gray-500">Node: {claim.node_id} // Rep: {claim.rep_score}</p>
                    </div>
                    <div className="text-right">
                       <span className="text-[11px] font-black text-white">{claim.amount.toLocaleString()} SATS</span>
                       <span className="text-[9px] text-gray-600 block uppercase font-bold">{claim.time}</span>
                    </div>
                  </div>
                  <div className="w-full bg-white/5 h-0.5 rounded-full overflow-hidden mt-2">
                     <div className="bg-blue-500/30 h-full" style={{ width: '40%' }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Claim Audit Detail */}
        <div className="col-span-12 lg:col-span-5">
           {selectedClaim ? (
             <div className="bg-[#0a0a0a] border border-white/10 rounded-lg p-8 shadow-2xl animate-in fade-in slide-in-from-right-4 duration-300 flex flex-col gap-6">
                <div>
                   <span className="text-[10px] text-blue-500 font-black uppercase tracking-widest block mb-1">Audit Mode</span>
                   <h2 className="text-2xl font-black text-white tracking-tighter uppercase">{selectedClaim.id}</h2>
                </div>

                <div className="bg-black/40 border border-white/5 p-4 rounded text-sm text-gray-400 leading-relaxed italic">
                   "{selectedClaim.description}"
                </div>

                <div className="space-y-4">
                   <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest border-b border-white/5 pb-2">
                      <span className="text-gray-600">Verification Integrity</span>
                      <span className="text-green-500">99.2% Match</span>
                   </div>
                   <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest border-b border-white/5 pb-2">
                      <span className="text-gray-600">Hardware Status</span>
                      <span className="text-blue-400">TPM_SEALED_OK</span>
                   </div>
                   <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest border-b border-white/5 pb-2">
                      <span className="text-gray-600">Incident Provenance</span>
                      <span className="text-white font-mono">HASH_E3B0...C442</span>
                   </div>
                </div>

                <div className="pt-6 grid grid-cols-2 gap-4">
                   <button 
                     onClick={() => handleAdjudicate('APPROVED')}
                     disabled={isProcessing}
                     className="py-4 bg-green-500 text-black font-black text-xs uppercase tracking-widest hover:bg-green-400 transition-all flex items-center justify-center gap-3"
                   >
                     {isProcessing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Banknote className="w-3.5 h-3.5" />}
                     Authorize Payout
                   </button>
                   <button 
                     onClick={() => handleAdjudicate('REJECTED')}
                     disabled={isProcessing}
                     className="py-4 border border-red-500/20 bg-red-500/5 text-red-500 font-black text-xs uppercase tracking-widest hover:bg-red-500/10 transition-all"
                   >
                     Reject Claim
                   </button>
                </div>
                <p className="text-[9px] text-gray-600 text-center uppercase tracking-widest font-bold">
                   *All payouts are executed via spontaneous Lightning Keysend.
                </p>
             </div>
           ) : (
             <div className="h-full border border-white/5 border-dashed rounded-lg flex flex-col items-center justify-center p-12 text-center">
                <Info className="w-12 h-12 text-gray-800 mb-4" />
                <h3 className="text-gray-600 font-black uppercase text-xs tracking-widest">Select a claim to audit</h3>
                <p className="text-[10px] text-gray-700 mt-2">Historical forensics will load here.</p>
             </div>
           )}
        </div>

      </div>

      {/* Footer System Feed */}
      <footer className="mt-8 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 font-mono text-[9px] text-gray-600">
        <div className="flex gap-4 items-center">
          <span className="text-blue-500 font-bold uppercase">[INSURANCE_MONITOR]</span>
          <span className="animate-pulse">[*] LISTENING FOR SEV-2 INCIDENTS ON LND_GATEWAY_B...</span>
          <div className="ml-auto flex items-center gap-3">
             <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> AVG AUDIT: 14m</span>
             <span className="text-gray-800 tracking-tighter">LIQUIDITY_SAFE_71.8M</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
