import React, { useState, useMemo } from 'react';
import { 
  Gavel, 
  Target, 
  Users, 
  ShieldCheck, 
  ShieldAlert, 
  Clock, 
  Fingerprint, 
  Award, 
  ChevronRight, 
  RefreshCw, 
  Info, 
  Lock,
  Zap,
  CheckCircle2,
  AlertTriangle,
  LayoutGrid,
  Scale
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HIGH COURT JURY SELECTION (v1.0)
 * "Opt-in for the next epoch of decentralized justice."
 * ----------------------------------------------------
 */

const App = () => {
  const [isEnrolling, setIsEnrolling] = useState(false);
  const [isEnrolled, setIsEnrolled] = useState(false);
  
  // Mock Node Operator State
  const [node] = useState({
    id: "NODE_ELITE_X29",
    rep: 982,
    bond: 2000000,
    status: "SUPER-ELITE"
  });

  // Mock Epoch Data
  const [epoch] = useState({
    id: "EPOCH_88294",
    starts_in: "14h 22m",
    candidate_pool_count: 58,
    required_jurors: 7,
    selection_seed_source: "Next BTC Block Hash"
  });

  const [candidates] = useState([
    { id: "NODE_ELITE_X29", rep: 982, status: "ENROLLED" },
    { id: "NODE_ALPHA_001", rep: 965, status: "ENROLLED" },
    { id: "NODE_GAMMA_992", rep: 958, status: "ENROLLED" },
    { id: "NODE_WHALE_04", rep: 991, status: "PENDING" },
    { id: "NODE_SIGMA_77", rep: 952, status: "ENROLLED" }
  ]);

  const isEligible = node.rep >= 950 && node.bond >= 2000000;

  const handleEnroll = () => {
    setIsEnrolling(true);
    // Simulate TPM Signing for Enrollment
    setTimeout(() => {
      setIsEnrolling(false);
      setIsEnrolled(true);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-amber-500/30">
      
      {/* Background Decorative Element */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl mx-auto relative z-10">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 border-b border-white/10 pb-8 gap-6">
          <div>
            <div className="flex items-center gap-4 mb-3">
              <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl shadow-2xl">
                <Scale className="w-8 h-8 text-amber-500" />
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tighter uppercase">High Court Draft</h1>
                <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold">Epoch {epoch.id} // VRF Selection active</p>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-6 shadow-xl text-right">
                <div className="flex flex-col">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Selection Seed</span>
                   <span className="text-xs font-black text-white tracking-widest uppercase">{epoch.selection_seed_source}</span>
                </div>
                <div className="h-8 w-px bg-white/10" />
                <div className="flex flex-col">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Draw Window</span>
                   <span className="text-sm font-black text-amber-500 tracking-tighter">{epoch.starts_in}</span>
                </div>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-8">
          
          {/* Eligibility & Enrollment Card */}
          <div className="col-span-12 lg:col-span-8 space-y-8">
            <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
              <div className="p-1 bg-gradient-to-r from-amber-500/20 to-transparent" />
              <div className="p-8">
                 <div className="flex justify-between items-start mb-8">
                    <div>
                       <h2 className="text-xl font-black text-white uppercase tracking-tight mb-2">My Candidate Standing</h2>
                       <p className="text-xs text-gray-500">Hardware Identity: <span className="text-amber-500 font-bold">{node.id}</span></p>
                    </div>
                    {isEligible ? (
                       <span className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded text-[10px] font-black text-green-500 uppercase tracking-widest">
                         <ShieldCheck className="w-3 h-3" /> Eligible for High Court
                       </span>
                    ) : (
                       <span className="flex items-center gap-2 px-3 py-1 bg-red-500/10 border border-red-500/20 rounded text-[10px] font-black text-red-500 uppercase tracking-widest">
                         <ShieldAlert className="w-3 h-3" /> Not Eligible
                       </span>
                    )}
                 </div>

                 <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    <div className="p-6 bg-white/[0.02] border border-white/5 rounded-lg">
                       <span className="text-[9px] text-gray-600 uppercase font-black block mb-2">Requirement 1: Reputation</span>
                       <div className="flex items-baseline gap-2">
                          <span className={`text-2xl font-black ${node.rep >= 950 ? 'text-white' : 'text-red-500'}`}>{node.rep}</span>
                          <span className="text-[10px] text-gray-600">/ 950 Threshold</span>
                       </div>
                    </div>
                    <div className="p-6 bg-white/[0.02] border border-white/5 rounded-lg">
                       <span className="text-[9px] text-gray-600 uppercase font-black block mb-2">Requirement 2: Staked Bond</span>
                       <div className="flex items-baseline gap-2">
                          <span className={`text-2xl font-black ${node.bond >= 2000000 ? 'text-white' : 'text-red-500'}`}>{(node.bond / 1000000).toFixed(1)}M</span>
                          <span className="text-[10px] text-gray-600">/ 2.0M Threshold</span>
                       </div>
                    </div>
                 </div>

                 {!isEnrolled ? (
                    <div className="pt-8 border-t border-white/5">
                       <div className="flex items-start gap-4 mb-8">
                          <Info className="w-5 h-5 text-gray-500 shrink-0" />
                          <p className="text-xs text-gray-500 leading-relaxed italic">
                            "By enrolling in the High Court Draft, you agree to respond to SEV-1 adjudications within a 4-hour window. Failure to vote once a case is opened results in a -50 REP penalty."
                          </p>
                       </div>
                       <button 
                         onClick={handleEnroll}
                         disabled={!isEligible || isEnrolling}
                         className="w-full py-4 bg-amber-500 text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-amber-400 transition-all flex items-center justify-center gap-3 disabled:opacity-20 disabled:grayscale shadow-[0_0_30px_rgba(245,158,11,0.2)]"
                       >
                         {isEnrolling ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Fingerprint className="w-4 h-4" />}
                         {isEnrolling ? 'Signing Enrollment...' : 'Sign Opt-In for Epoch'}
                       </button>
                    </div>
                 ) : (
                    <div className="pt-8 border-t border-white/5 animate-in zoom-in-95 duration-500 text-center">
                       <div className="w-16 h-16 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                          <CheckCircle2 className="w-8 h-8 text-green-500" />
                       </div>
                       <h3 className="text-xl font-black text-white uppercase tracking-tight mb-2">Enrolled Successfully</h3>
                       <p className="text-xs text-gray-500 mb-6">Your Node ID has been added to the VRF pool. Awaiting Bitcoin block hash for the random draw.</p>
                       <div className="bg-black border border-white/5 p-3 rounded inline-block mono text-[9px] text-gray-600">
                         ENROLLMENT_HASH: 0x8a2e...{Math.random().toString(16).slice(2, 10)}
                       </div>
                    </div>
                 )}
              </div>
            </div>

            {/* Candidate Pool Visualization */}
            <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
              <h3 className="text-xs font-black text-white uppercase tracking-widest mb-8 flex items-center gap-3">
                <Users className="w-4 h-4 text-indigo-500" /> Global Candidate Pool
              </h3>
              <div className="grid grid-cols-5 md:grid-cols-10 gap-3">
                 {[...Array(60)].map((_, i) => (
                   <div 
                    key={i} 
                    className={`aspect-square rounded border ${i < epoch.candidate_pool_count ? 'bg-indigo-500/20 border-indigo-500/40 animate-pulse' : 'bg-white/5 border-white/10'}`} 
                    title={i < epoch.candidate_pool_count ? "Active Candidate" : "Open Slot"}
                   />
                 ))}
              </div>
              <div className="mt-8 flex justify-between items-center text-[9px] font-black uppercase text-gray-600 tracking-widest">
                 <div className="flex gap-4">
                    <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-indigo-500 rounded-full" /> Verified Enrollee</span>
                    <span className="flex items-center gap-1.5"><div className="w-2 h-2 bg-white/5 rounded-full" /> Unclaimed Spot</span>
                 </div>
                 <span>Draft Cap: 100 Nodes</span>
              </div>
            </div>
          </div>

          {/* Sidebar Metrics */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
                <h3 className="text-xs font-black text-white uppercase tracking-[0.2em] mb-8 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-500" /> Probability Matrix
                </h3>
                <div className="space-y-8">
                   <div>
                      <div className="flex justify-between items-end mb-3">
                         <span className="text-[10px] text-gray-500 uppercase font-black tracking-widest">Selection Odds</span>
                         <span className="text-lg font-black text-white">12.06%</span>
                      </div>
                      <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                         <div className="bg-amber-500 h-full" style={{ width: '12.06%' }} />
                      </div>
                   </div>
                   <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-white/5 rounded text-center">
                         <p className="text-[9px] text-gray-600 uppercase font-black mb-1">Pool Depth</p>
                         <p className="text-xl font-black text-white">{epoch.candidate_pool_count}</p>
                      </div>
                      <div className="p-4 bg-white/5 rounded text-center">
                         <p className="text-[9px] text-gray-600 uppercase font-black mb-1">Court Seats</p>
                         <p className="text-xl font-black text-indigo-500">{epoch.required_jurors}</p>
                      </div>
                   </div>
                   <p className="text-[9px] text-gray-700 italic leading-relaxed text-center">
                     *Probability is inversely proportional to pool depth and adjusted for individual node accuracy.
                   </p>
                </div>
             </div>

             <div className="p-8 border border-amber-500/10 bg-amber-500/5 rounded-xl relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform">
                   <Gavel className="w-24 h-24 text-amber-500" />
                </div>
                <h4 className="text-[10px] font-black text-amber-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                   <Lock className="w-3.5 h-3.5" /> Adjudicator Bonus
                </h4>
                <p className="text-[11px] text-gray-500 leading-relaxed mb-6">
                   Active High Court Jurors earn a 5% pro-rata share of all slashed bonds and transaction priority fees during their 7-day term.
                </p>
                <div className="flex justify-between text-[10px] font-black uppercase text-gray-600 border-t border-white/5 pt-4">
                   <span>Avg Term Yield</span>
                   <span className="text-green-500">~12,400 SATS</span>
                </div>
             </div>

             <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="p-4 bg-white/[0.02] border-b border-white/5">
                   <h3 className="text-[10px] font-black text-white uppercase tracking-widest">Enrolled Elite Roster</h3>
                </div>
                <div className="divide-y divide-white/5">
                   {candidates.map(c => (
                      <div key={c.id} className="p-4 flex items-center justify-between group hover:bg-white/[0.01] transition-all">
                         <div className="flex flex-col">
                            <span className="text-[10px] font-black text-white block mb-0.5 group-hover:text-amber-500 transition-colors">{c.id}</span>
                            <span className="text-[8px] text-gray-600 font-bold uppercase">{c.rep} REP</span>
                         </div>
                         <span className={`text-[8px] font-black px-1.5 py-0.5 rounded border ${c.status === 'ENROLLED' ? 'text-green-500 border-green-500/20' : 'text-gray-500 border-white/10'}`}>
                           {c.status}
                         </span>
                      </div>
                   ))}
                </div>
             </div>
          </div>

        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-6xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">VRF Oracle Operational</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Drafting Epoch: 88294</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] QUORUM: 58/100</span>
            <span>[*] PENDING_PIPS: 3</span>
            <span>[*] PROTOCOL: v2.6.1</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
