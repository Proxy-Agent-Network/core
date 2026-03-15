import React, { useState, useEffect } from 'react';
import { 
  Gavel, Vote, Users, Shield, Clock, 
  CheckCircle2, XCircle, Info, ArrowRight,
  TrendingUp, Lock, Award, Fingerprint, 
  AlertTriangle, MessageSquare, ExternalLink,
  ChevronRight, Layout
} from 'lucide-react';

const App = () => {
  const [voted, setVoted] = useState(false);
  const [voteType, setVoteType] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Mock Voter Identity (Derived from TPM Identity)
  const [voter] = useState({
    node_id: "NODE_ELITE_X29",
    reputation: 982,
    staked_bond: 2000000,
    voting_power: 142.5 // Calculated as (Bond / 100k) * (Rep / 1000)
  });

  // Mock Active Proposal: PIP-882
  const [proposal] = useState({
    id: "PIP-882",
    title: "Increase Tier 3 Staking Requirement",
    author: "Foundation_Core",
    status: "ACTIVE",
    category: "ECONOMICS",
    expires_at: "2026-02-18T12:00:00Z",
    abstract: "Proposing an increase of the minimum collateral for Tier 3 (Legal) nodes from 2,000,000 to 2,500,000 Satoshis to combat rising Sybil risk in high-stakes jurisdictions.",
    current_stats: {
      total_votes: 842,
      power_for: 124500.5,
      power_against: 42300.2,
      quorum_needed: 250000,
      quorum_reached: 66.7
    }
  });

  const handleVote = (type) => {
    setVoteType(type);
    setIsSubmitting(true);
    // Simulate TPM Signing Ceremony
    setTimeout(() => {
      setIsSubmitting(false);
      setVoted(true);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-terminal-green/30">
      
      {/* Header */}
      <header className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center mb-12 border-b border-white/10 pb-8 gap-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-white/5 border border-white/10 rounded-xl shadow-2xl">
            <Gavel className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Network Governance</h1>
            <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500">Decentralized Consensus Node // {voter.node_id}</p>
          </div>
        </div>

        <div className="flex gap-4">
          <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded-lg flex items-center gap-4">
             <div className="flex flex-col items-end">
                <span className="text-[9px] text-gray-600 uppercase font-black">Voting Power</span>
                <span className="text-xl font-black text-white tracking-tighter">{voter.voting_power} <span className="text-[10px] text-gray-500">VP</span></span>
             </div>
             <div className="h-8 w-px bg-white/10" />
             <div className="flex flex-col items-end">
                <span className="text-[9px] text-gray-600 uppercase font-black">Reputation</span>
                <span className="text-xl font-black text-green-500 tracking-tighter">{voter.reputation}</span>
             </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-12 gap-8">
        
        {/* Proposal Details */}
        <div className="col-span-12 lg:col-span-8 space-y-8">
          <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
            <div className="p-1 bg-gradient-to-r from-blue-500/20 via-indigo-500/20 to-purple-500/20" />
            <div className="p-8">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <span className="px-2 py-1 bg-indigo-500/10 text-indigo-400 text-[9px] font-black uppercase rounded border border-indigo-500/20 tracking-widest mb-3 inline-block">
                    {proposal.category}
                  </span>
                  <h2 className="text-3xl font-black text-white tracking-tight uppercase mb-2">{proposal.id}: {proposal.title}</h2>
                  <div className="flex items-center gap-4 text-[10px] text-gray-500">
                    <span className="flex items-center gap-1"><Users className="w-3 h-3" /> Prop: {proposal.author}</span>
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> Ends: 7 Days</span>
                  </div>
                </div>
                <div className="text-right">
                   <div className="text-[10px] font-black text-gray-600 uppercase mb-1">Status</div>
                   <div className="flex items-center gap-2 text-green-500 font-black text-xs">
                      <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" /> ACTIVE VOTING
                   </div>
                </div>
              </div>

              <div className="space-y-6 py-6 border-y border-white/5">
                <div className="flex items-start gap-4">
                  <div className="p-2 bg-white/5 rounded"><Info className="w-4 h-4 text-gray-400" /></div>
                  <div>
                    <h4 className="text-xs font-black text-gray-300 uppercase mb-2">Abstract</h4>
                    <p className="text-sm text-gray-400 leading-relaxed italic">"{proposal.abstract}"</p>
                  </div>
                </div>
              </div>

              <div className="pt-8">
                {!voted ? (
                  <div className="grid grid-cols-2 gap-4">
                    <button 
                      onClick={() => handleVote('FOR')}
                      disabled={isSubmitting}
                      className="group p-6 border border-green-500/20 bg-green-500/5 rounded-xl hover:bg-green-500/10 hover:border-green-500/50 transition-all text-center"
                    >
                      <CheckCircle2 className="w-8 h-8 text-green-500 mx-auto mb-3 group-hover:scale-110 transition-transform" />
                      <span className="block text-xs font-black text-white uppercase tracking-widest mb-1">Vote For</span>
                      <span className="text-[10px] text-gray-600">Apply +2.5M Sats Cap</span>
                    </button>
                    <button 
                      onClick={() => handleVote('AGAINST')}
                      disabled={isSubmitting}
                      className="group p-6 border border-red-500/20 bg-red-500/5 rounded-xl hover:bg-red-500/10 hover:border-red-500/50 transition-all text-center"
                    >
                      <XCircle className="w-8 h-8 text-red-500 mx-auto mb-3 group-hover:scale-110 transition-transform" />
                      <span className="block text-xs font-black text-white uppercase tracking-widest mb-1">Vote Against</span>
                      <span className="text-[10px] text-gray-600">Maintain 2M Sats Cap</span>
                    </button>
                  </div>
                ) : (
                  <div className="bg-white/5 border border-white/10 p-8 rounded-xl text-center animate-in fade-in zoom-in-95 duration-500">
                    <Fingerprint className="w-12 h-12 text-indigo-500 mx-auto mb-4 animate-pulse" />
                    <h3 className="text-xl font-black text-white uppercase mb-2 tracking-tighter">Vote Signed & Recorded</h3>
                    <p className="text-xs text-gray-500 mb-6">Your hardware signature (AK_HANDLE) has been broadcast to the governance ledger.</p>
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-500/10 border border-indigo-500/20 rounded text-[10px] text-indigo-400 font-bold uppercase tracking-widest">
                       Receipt: 0x8a2...{Math.random().toString(16).slice(2, 8)}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Discussion Snippet */}
          <div className="p-6 bg-white/[0.02] border border-white/5 rounded-xl flex items-center justify-between group cursor-pointer hover:bg-white/5 transition-all">
            <div className="flex items-center gap-4">
              <MessageSquare className="w-5 h-5 text-gray-600" />
              <span className="text-xs text-gray-400 font-bold uppercase tracking-widest">Join the Discussion on GitHub</span>
            </div>
            <ChevronRight className="w-4 h-4 text-gray-700 group-hover:text-white transition-colors" />
          </div>
        </div>

        {/* Sidebar: Real-time Tally */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
          <div className="bg-[#0a0a0a] border border-white/5 rounded-xl p-8 shadow-2xl">
            <h3 className="text-xs font-black text-white uppercase tracking-[0.2em] mb-8 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-500" /> Live Tally
            </h3>
            
            <div className="space-y-8">
              <div>
                <div className="flex justify-between items-end mb-3">
                  <span className="text-[10px] text-gray-500 uppercase font-black">Support</span>
                  <span className="text-lg font-black text-white">74.6%</span>
                </div>
                <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                  <div className="bg-indigo-500 h-full shadow-[0_0_10px_rgba(99,102,241,0.5)]" style={{ width: '74.6%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-end mb-3">
                  <span className="text-[10px] text-gray-500 uppercase font-black">Opposition</span>
                  <span className="text-lg font-black text-white">25.4%</span>
                </div>
                <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                  <div className="bg-red-500/40 h-full" style={{ width: '25.4%' }} />
                </div>
              </div>

              <div className="pt-6 border-t border-white/5 space-y-4">
                 <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                    <span className="text-gray-600">Quorum Status</span>
                    <span className="text-green-500">{proposal.current_stats.quorum_reached}% Reached</span>
                 </div>
                 <div className="flex gap-1 h-1.5">
                    {[...Array(20)].map((_, i) => (
                      <div key={i} className={`flex-1 rounded-full ${i < 13 ? 'bg-green-500/40' : 'bg-white/5'}`} />
                    ))}
                 </div>
                 <p className="text-[9px] text-gray-600 italic leading-relaxed">
                   *Minimum of 250,000 VP required for this proposal to be binding. 66% Super-majority required for activation.
                 </p>
              </div>
            </div>
          </div>

          <div className="p-6 bg-yellow-500/5 border border-yellow-500/20 rounded-xl relative overflow-hidden group">
            <div className="absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform">
              <AlertTriangle className="w-24 h-24 text-yellow-500" />
            </div>
            <h4 className="text-[10px] font-black text-yellow-500 uppercase tracking-widest mb-3 flex items-center gap-2">
              <Lock className="w-3.5 h-3.5" /> Voting Safeguard
            </h4>
            <p className="text-[11px] text-gray-500 leading-relaxed">
              Voting power is snapshot at the beginning of the epoch. Withdrawing your bond before the vote concludes will invalidate your signature.
            </p>
          </div>

          <div className="bg-void border border-white/5 p-4 rounded-lg flex items-center justify-between">
            <div className="flex flex-col">
              <span className="text-[9px] text-gray-600 uppercase font-black">Audit Source</span>
              <span className="text-[10px] text-gray-400 mono italic font-bold tracking-tighter">GOV_EPOCH_882.JSON</span>
            </div>
            <Layout className="w-4 h-4 text-gray-700" />
          </div>
        </div>

      </main>

      {/* Global Status Bar (Footer) */}
      <footer className="max-w-6xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 font-mono text-[9px] text-gray-600 flex items-center gap-6">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
          <span className="text-white font-black uppercase">Consensus Node Active</span>
        </div>
        <div className="h-4 w-px bg-white/10" />
        <div className="animate-marquee whitespace-nowrap overflow-hidden">
           PIP-881 [PASSED] // PIP-882 [ACTIVE] // PIP-883 [DRAFT] ...
        </div>
        <div className="ml-auto flex items-center gap-2 text-gray-800">
          <Shield className="w-3 h-3" /> Hardware Verified Identity
        </div>
      </footer>
    </div>
  );
};

export default App;
