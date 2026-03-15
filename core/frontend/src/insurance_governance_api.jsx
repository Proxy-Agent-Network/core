import React, { useState } from 'react';
import { 
  Gavel, 
  Lock, 
  Fingerprint, 
  Scale, 
  RefreshCw, 
  Binary, 
  Info, 
  XCircle, 
  AlertTriangle,
  Globe,
  Users,
  ShieldCheck,
  Target,
  Zap
} from 'lucide-react';

/**
 * PROXY PROTOCOL - GOVERNANCE MULTI-SIG PORTAL (v1.0)
 * "Judicial oversight for the autonomous Satoshi economy."
 * ----------------------------------------------------
 */

const App = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isVoting, setIsVoting] = useState(false);
  const [hasVoted, setHasVoted] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState(null);

  const [proposals] = useState([
    {
      id: "OVR-8829-PX",
      type: "FEE_OVERRIDE",
      title: "Cap Surge Fees in ASIA_SE Hub",
      reason: "Localized ISP outage causing artificial actuary drift. Manual cap at 0.12% requested.",
      target_levy: "0.1200%",
      region: "ASIA_SE",
      votes_signed: 4,
      votes_required: 5,
      severity: "MEDIUM",
      deadline: "18h 42m"
    },
    {
      id: "FRZ-7714-PX",
      type: "LIQUIDITY_FREEZE",
      title: "Global Reserve Halt",
      reason: "Confirmed systemic PCR drift in 8 nodes. Emergency freeze of all keysend payouts.",
      target_levy: "N/A",
      region: "GLOBAL",
      votes_signed: 2,
      votes_required: 5,
      severity: "CRITICAL",
      deadline: "22h 15m"
    }
  ]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1200);
  };

  const executeVote = () => {
    setIsVoting(true);
    setTimeout(() => {
      setIsVoting(false);
      setHasVoted(true);
    }, 2500);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-indigo-500/30">
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-7xl mx-auto relative z-10 space-y-8">
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl shadow-2xl">
              <Scale className="w-8 h-8 text-indigo-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none text-glow">Governance Bench</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Economic Adjudication // Juror: <span className="text-indigo-400">NODE_ELITE_X29</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Active Proposals</span>
                   <span className="text-xl font-black text-white tracking-tighter">{proposals.length} <span className="text-[10px] text-indigo-500">PENDING</span></span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <button onClick={handleRefresh} className={`p-2 border border-white/10 rounded hover:bg-white/10 transition-all ${isRefreshing ? 'animate-spin' : ''}`}>
                  <RefreshCw className="w-4 h-4 text-gray-500" />
                </button>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-8 items-stretch">
          <div className="col-span-12 lg:col-span-5 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl flex flex-col min-h-[500px]">
                <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center px-6">
                   <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-3 tracking-widest">
                     <Gavel className="w-4 h-4 text-indigo-500" /> Active Docket
                   </h3>
                   <div className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                      <span className="text-[9px] text-green-500 font-bold uppercase">Quorum Link Active</span>
                   </div>
                </div>

                <div className="divide-y divide-white/5 overflow-y-auto max-h-[600px]">
                   {proposals.map((prop) => (
                      <div key={prop.id} onClick={() => { setSelectedProposal(prop); setHasVoted(false); }}
                        className={`p-6 hover:bg-indigo-500/[0.02] transition-all cursor-pointer group ${selectedProposal?.id === prop.id ? 'bg-indigo-500/[0.04]' : ''}`}>
                         <div className="flex justify-between items-start mb-4">
                            <div>
                               <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-indigo-400 transition-colors">{prop.id}</span>
                               <h4 className="text-sm font-bold text-gray-400 uppercase mt-1 leading-tight">{prop.title}</h4>
                            </div>
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${prop.severity === 'CRITICAL' ? 'bg-red-500/10 border-red-500/20 text-red-500' : 'bg-amber-500/10 border-amber-500/20 text-amber-500'}`}>
                               {prop.severity}
                            </span>
                         </div>
                         <div className="space-y-3">
                            <div className="flex justify-between items-center text-[8px] font-black text-gray-700 uppercase">
                               <span>Quorum: {prop.votes_signed}/{prop.votes_required}</span>
                               <span>Expires: {prop.deadline}</span>
                            </div>
                            <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                               <div className={`h-full ${prop.severity === 'CRITICAL' ? 'bg-red-500 animate-pulse' : 'bg-indigo-500'}`} style={{ width: `${(prop.votes_signed/prop.votes_required)*100}%` }} />
                            </div>
                         </div>
                      </div>
                   ))}
                </div>
             </div>

             <div className="p-8 border border-white/10 bg-indigo-500/5 rounded-xl shadow-inner">
                <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Info className="w-3.5 h-3.5" /> High Court Rule 8.4
                </h4>
                <p className="text-[11px] text-gray-500 leading-relaxed italic">
                   "Economic manual overrides must achieve a 5/7 super-majority consensus. Every vote is cryptographically bound to the juror's TPM identity key."
                </p>
             </div>
          </div>

          <div className="col-span-12 lg:col-span-7 flex flex-col">
             {selectedProposal ? (
                <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-10 shadow-2xl animate-in slide-in-from-right-4 duration-300 flex-1 flex flex-col gap-10">
                   <div className="flex justify-between items-start border-b border-white/5 pb-8">
                      <div>
                          <span className="text-[10px] text-indigo-500 font-black uppercase tracking-[0.2em] block mb-1">Intervention Manifest</span>
                          <h2 className="text-3xl font-black text-white tracking-tighter uppercase leading-none">{selectedProposal.title}</h2>
                      </div>
                      <button onClick={() => setSelectedProposal(null)} className="p-3 text-gray-700 hover:text-white transition-colors">
                          <XCircle className="w-6 h-6" />
                      </button>
                   </div>

                   <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                      <div className="space-y-8">
                         <div>
                            <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                               <Binary className="w-3.5 h-3.5 text-indigo-500" /> Executive Brief
                            </h4>
                            <div className="p-6 bg-black border border-white/5 rounded-xl">
                               <p className="text-sm text-gray-400 leading-relaxed font-medium italic">"{selectedProposal.reason}"</p>
                            </div>
                         </div>
                         <div className="grid grid-cols-2 gap-4">
                            <div className="p-5 bg-white/[0.02] border border-white/5 rounded-xl">
                               <span className="text-[9px] text-gray-700 font-black uppercase block mb-1">Target Hub</span>
                               <span className="text-xs font-black text-white flex items-center gap-2"><Globe className="w-3 h-3 text-blue-500" /> {selectedProposal.region}</span>
                            </div>
                            <div className="p-5 bg-white/[0.02] border border-white/5 rounded-xl">
                               <span className="text-[9px] text-gray-700 font-black uppercase block mb-1">Action Type</span>
                               <span className="text-xs font-black text-indigo-400 uppercase tracking-tighter">{selectedProposal.type}</span>
                            </div>
                         </div>
                      </div>

                      <div className="space-y-8">
                         <div>
                            <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                               <Target className="w-3.5 h-3.5 text-amber-500" /> Proposed Parameters
                            </h4>
                            <div className="p-6 bg-indigo-500/5 border border-indigo-500/10 rounded-xl flex items-center justify-between">
                               <div>
                                  <span className="text-[9px] text-gray-600 font-black uppercase block">Levy Adjustment</span>
                                  <span className="text-2xl font-black text-white tracking-tighter">{selectedProposal.target_levy}</span>
                               </div>
                               <Zap className="w-8 h-8 text-amber-500 animate-pulse" />
                            </div>
                         </div>
                         <div className="p-6 bg-red-500/5 border border-red-500/10 rounded-xl">
                            <div className="flex items-center gap-3 text-red-500 mb-3">
                               <AlertTriangle className="w-5 h-5" />
                               <span className="text-[10px] font-black uppercase tracking-widest">Protocol Impact</span>
                            </div>
                            <p className="text-[11px] text-gray-500 leading-relaxed font-bold">Approving this override manually bypasses Actuary calculations for <span className="text-white">24 hours</span>.</p>
                         </div>
                      </div>
                   </div>

                   <div className="mt-auto pt-10 border-t border-white/5 flex flex-col md:flex-row gap-8 items-center">
                      {!hasVoted ? (
                        <>
                          <div className="flex items-center gap-6 flex-1 bg-white/[0.02] border border-white/5 p-6 rounded-xl shadow-inner">
                             <Users className="w-10 h-10 text-indigo-500 shrink-0" />
                             <div>
                                <p className="text-[11px] text-white font-black uppercase tracking-widest mb-1">Juror Confirmation</p>
                                <p className="text-[10px] text-gray-600 leading-relaxed font-medium">Awaiting signature for <span className="text-white">NODE_ELITE_X29</span>.</p>
                             </div>
                          </div>
                          <div className="flex gap-4 w-full md:w-auto">
                             <button onClick={executeVote} disabled={isVoting} className="px-10 py-5 bg-white text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-indigo-500 hover:text-white transition-all rounded flex items-center justify-center gap-3 shadow-2xl">
                                {isVoting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Fingerprint className="w-4 h-4" />} Sign & Broadcast
                             </button>
                             <button className="px-10 py-5 bg-white/5 border border-white/10 text-gray-500 font-black text-xs uppercase tracking-widest hover:text-red-500 transition-all rounded">Reject</button>
                          </div>
                        </>
                      ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-center animate-in zoom-in-95 duration-500">
                           <div className="w-20 h-20 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mb-6 shadow-[0_0_40px_rgba(34,197,94,0.1)]">
                              <ShieldCheck className="w-10 h-10 text-green-500 animate-pulse" />
                           </div>
                           <h3 className="text-2xl font-black text-white uppercase tracking-tighter mb-2">Vote Hardware-Signed</h3>
                           <p className="text-xs text-gray-500 max-w-sm mx-auto leading-relaxed">Your adjudication signature has been anchored to the High Court registry.</p>
                           <div className="mt-8 p-4 bg-black border border-white/5 rounded-xl mono text-[10px] text-gray-700">SIG_RECEIPT: 0x8A2E...{Math.random().toString(16).slice(2, 10).toUpperCase()}</div>
                        </div>
                      )}
                   </div>
                </div>
             ) : (
                <div className="h-full border-2 border-white/5 border-dashed rounded-2xl flex flex-col items-center justify-center p-20 text-center opacity-40 grayscale">
                   <Scale className="w-24 h-24 text-gray-800 mb-10 animate-pulse" />
                   <h3 className="text-xl font-black text-gray-700 uppercase tracking-[0.3em] mb-4">Adjudication Point Ready</h3>
                   <p className="text-sm text-gray-800 font-bold uppercase tracking-widest max-w-md">Select an economic proposal from the docket to cast your hardware-bound judicial vote.</p>
                </div>
             )}
          </div>
        </div>
      </main>

      <footer className="max-w-7xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-5 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
               <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(99,102,241,0.5)]" />
               <span className="text-[10px] text-white font-black uppercase tracking-widest">High Court Registry: SYNCHRONIZED</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[10px] text-gray-600 font-bold uppercase tracking-tighter italic">"Justice is calculated; equity is human."</span>
         </div>
         <div className="flex gap-8 text-[10px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] QUORUM_ACTIVE: TRUE</span>
            <span>[*] SIGNATURE_SCHEME: RSA-PSS</span>
            <span>[*] VERSION: v3.4.8</span>
         </div>
      </footer>
    </div>
  );
};

export default App;
