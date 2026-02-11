import React, { useState, useEffect } from 'react';
import { 
  Gavel, 
  ShieldAlert, 
  Eye, 
  CheckCircle2, 
  XCircle, 
  ShieldCheck, 
  Clock, 
  ArrowRight,
  Lock,
  Zap,
  Activity,
  UserCheck,
  HeartPulse,
  Banknote,
  AlertTriangle
} from 'lucide-react';

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [isVoting, setIsVoting] = useState(false);

  // Mock Data for the Tribunal (v1.7)
  const [stats] = useState({
    reputation: 982,
    staked_bond: 2000000,
    earned_fees: 45200,
    successful_verdicts: 124,
    insurance_pool_depth: 10450200
  });

  const [cases] = useState([
    {
      id: "CASE-882-9",
      type: "SMS_VERIFICATION",
      status: "PENDING",
      timestamp: "2026-02-11 08:12:00",
      dispute_reason: "Agent claims code relay was incorrect.",
      evidence: {
        instructions: "Relay the 6-digit code sent to +1 555-0199.",
        proof: "Input: 882190 | Screenshot provided: YES",
        audit_log: "Node location matched. TPM sign-off valid."
      },
      value: 50000,
      reward: 500
    },
    {
      id: "CASE-901-2",
      type: "PHYSICAL_GEOFENCE",
      status: "PENDING",
      timestamp: "2026-02-11 09:45:12",
      dispute_reason: "Node was outside of 500m stationary drift.",
      evidence: {
        instructions: "Notarize document at 44 Market St.",
        proof: "Coordinates: 37.789, -122.401 (Distance: 0.62km)",
        audit_log: "Stationary threshold violation detected."
      },
      value: 250000,
      reward: 2500
    }
  ]);

  const [claims] = useState([
    {
      id: "CLAIM-X01",
      node_id: "node_unlucky_operator",
      amount_sats: 10000,
      reason: "SYSTEMIC_LND_FAILURE",
      timestamp: "2026-02-11 10:15:00",
      proof_log: "Max Retries (5/5) exceeded. Preimage: 30450221... HTLC accepted by node but preimage revelation failed to broadcast.",
      severity: "SEV-2"
    }
  ]);

  const handleVote = (verdict) => {
    setIsVoting(true);
    setTimeout(() => {
      setIsVoting(false);
      setSelectedCase(null);
      setSelectedClaim(null);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-gray-200 font-mono selection:bg-amber-500/30">
      {/* Top Protocol Bar */}
      <header className="border-b border-white/10 bg-[#0d0d0e] px-6 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="bg-amber-500/10 p-2 rounded border border-amber-500/20">
            <Gavel className="w-5 h-5 text-amber-500" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tighter text-white uppercase">Jury Tribunal v1.7</h1>
            <p className="text-[10px] text-amber-500/70 uppercase">Appellate Selection: BTC BLOCK 831201</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6 text-[11px]">
          <div className="flex flex-col items-end">
            <span className="text-gray-500 uppercase">Hardware Attestation</span>
            <span className="text-green-500 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" /> TPM 2.0 ACTIVE
            </span>
          </div>
          <div className="h-8 w-px bg-white/10" />
          <div className="flex flex-col items-end">
            <span className="text-gray-500 uppercase">Staked Bond</span>
            <span className="text-white">{(stats.staked_bond / 1000000).toFixed(1)}M SATS</span>
          </div>
          <div className="flex items-center gap-2 bg-white/5 px-3 py-2 rounded border border-white/10">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-white">NODE_ELITE_X29</span>
          </div>
        </div>
      </header>

      <div className="max-w-[1400px] mx-auto p-6 grid grid-cols-12 gap-6">
        {/* Sidebar / Stats */}
        <aside className="col-span-12 lg:col-span-3 space-y-4">
          <div className="bg-[#0d0d0e] border border-white/10 p-5 rounded-lg">
            <h3 className="text-[10px] uppercase text-gray-500 mb-4 font-bold tracking-widest">Judicial Standing</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm">Reputation Score</span>
                <span className="text-amber-500 font-bold">{stats.reputation}/1000</span>
              </div>
              <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                <div 
                  className="bg-amber-500 h-full" 
                  style={{ width: `${(stats.reputation / 1000) * 100}%` }} 
                />
              </div>
              <div className="grid grid-cols-2 gap-2 pt-2">
                <div className="bg-white/5 p-3 rounded border border-white/5">
                  <p className="text-[10px] text-gray-500 uppercase mb-1">Verdicts</p>
                  <p className="text-lg font-bold">{stats.successful_verdicts}</p>
                </div>
                <div className="bg-white/5 p-3 rounded border border-white/5">
                  <p className="text-[10px] text-gray-500 uppercase mb-1">Fee Share</p>
                  <p className="text-lg font-bold text-green-500">+{stats.earned_fees}</p>
                </div>
              </div>
            </div>
          </div>

          <nav className="space-y-1">
            <button 
              onClick={() => { setActiveTab('cases'); setSelectedCase(null); setSelectedClaim(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm transition-all ${activeTab === 'cases' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Activity className="w-4 h-4" /> Open Disputes
            </button>
            <button 
              onClick={() => { setActiveTab('insurance'); setSelectedCase(null); setSelectedClaim(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm transition-all ${activeTab === 'insurance' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <HeartPulse className="w-4 h-4" /> Insurance Claims
            </button>
            <button 
              onClick={() => setActiveTab('history')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm transition-all ${activeTab === 'history' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Clock className="w-4 h-4" /> Verdict History
            </button>
          </nav>

          {activeTab === 'insurance' && (
            <div className="bg-blue-500/5 border border-blue-500/10 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Banknote className="w-4 h-4 text-blue-400" />
                <span className="text-[10px] uppercase font-bold text-blue-400">Pool Liquidity</span>
              </div>
              <p className="text-lg font-black text-white">{(stats.insurance_pool_depth / 100000000).toFixed(4)} BTC</p>
              <p className="text-[10px] text-blue-300/40 mt-1 uppercase tracking-tighter">0.1% tax accumulation active</p>
            </div>
          )}

          <div className="bg-amber-500/5 border border-amber-500/10 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <ShieldAlert className="w-4 h-4 text-amber-500" />
              <span className="text-[10px] uppercase font-bold text-amber-500">Notice</span>
            </div>
            <p className="text-[11px] text-amber-200/60 leading-relaxed">
              Voting against the majority (Schelling Point) results in a 30% bond slash. Audit evidence carefully.
            </p>
          </div>
        </aside>

        {/* Main Interface */}
        <main className="col-span-12 lg:col-span-9">
          
          {/* 1. DISPUTE CASES TAB */}
          {activeTab === 'cases' && !selectedCase && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden">
              <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/[0.02]">
                <h2 className="text-xs uppercase font-bold tracking-widest flex items-center gap-2">
                  <Activity className="w-4 h-4 text-amber-500" /> Pending Case Docket
                </h2>
                <span className="text-[10px] text-gray-500">{cases.length} cases require review</span>
              </div>
              <div className="divide-y divide-white/5">
                {cases.map((c) => (
                  <div key={c.id} className="p-5 hover:bg-white/[0.02] transition-colors flex items-center justify-between group">
                    <div className="flex items-center gap-6">
                      <div className="w-10 h-10 bg-white/5 rounded flex items-center justify-center border border-white/10">
                        {c.type === 'SMS_VERIFICATION' ? <Zap className="w-5 h-5 text-blue-400" /> : <ShieldAlert className="w-5 h-5 text-red-400" />}
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-white font-bold text-sm">{c.id}</span>
                          <span className="text-[10px] bg-white/5 px-2 py-0.5 rounded text-gray-400 uppercase tracking-tighter">{c.type}</span>
                        </div>
                        <p className="text-xs text-gray-500">{c.dispute_reason}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-8">
                      <div className="text-right">
                        <p className="text-[10px] text-gray-500 uppercase">Adjudication Reward</p>
                        <p className="text-sm font-bold text-green-500">+{c.reward} SATS</p>
                      </div>
                      <button 
                        onClick={() => setSelectedCase(c)}
                        className="bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-2 rounded text-xs transition-all flex items-center gap-2 group-hover:border-amber-500/30"
                      >
                        Enter Locker <ArrowRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 2. INSURANCE CLAIMS TAB */}
          {activeTab === 'insurance' && !selectedClaim && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-300">
               <div className="p-4 border-b border-blue-500/20 flex justify-between items-center bg-blue-500/[0.02]">
                <h2 className="text-xs uppercase font-bold tracking-widest flex items-center gap-2">
                  <HeartPulse className="w-4 h-4 text-blue-400" /> Automated Insurance Claims
                </h2>
                <span className="text-[10px] text-blue-400/50">High Court oversight required</span>
              </div>
              <div className="divide-y divide-white/5">
                {claims.map((claim) => (
                  <div key={claim.id} className="p-6 hover:bg-white/[0.02] transition-colors flex items-center justify-between group">
                    <div className="flex items-center gap-6">
                      <div className="w-12 h-12 bg-blue-500/10 rounded flex flex-col items-center justify-center border border-blue-500/20">
                        <AlertTriangle className="w-5 h-5 text-blue-400" />
                        <span className="text-[8px] font-bold text-blue-500 mt-1">{claim.severity}</span>
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-white font-bold text-sm">{claim.id}</span>
                          <span className="text-[10px] bg-red-500/10 px-2 py-0.5 rounded text-red-400 uppercase tracking-tighter font-bold">Failed Settlement</span>
                        </div>
                        <p className="text-xs text-gray-500">Node: <span className="text-gray-300">{claim.node_id}</span></p>
                        <p className="text-[10px] text-gray-600 mt-1">{claim.timestamp}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-8">
                       <div className="text-right">
                        <p className="text-[10px] text-gray-500 uppercase tracking-tighter">Claim Amount</p>
                        <p className="text-sm font-bold text-white">{claim.amount_sats.toLocaleString()} SATS</p>
                      </div>
                      <button 
                        onClick={() => setSelectedClaim(claim)}
                        className="bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 px-4 py-2 rounded text-xs transition-all flex items-center gap-2 text-blue-400 font-bold"
                      >
                        Audit Incident <ArrowRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              {claims.length === 0 && (
                <div className="p-20 text-center text-gray-600">
                  <ShieldCheck className="w-12 h-12 mx-auto mb-4 opacity-10" />
                  <p className="text-sm">No active insurance claims detected.</p>
                </div>
              )}
            </div>
          )}

          {/* 3. CASE DETAIL VIEW */}
          {selectedCase && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <button 
                onClick={() => setSelectedCase(null)}
                className="text-xs text-gray-500 hover:text-white mb-4 flex items-center gap-2"
              >
                <ArrowRight className="w-3 h-3 rotate-180" /> Back to Docket
              </button>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-6">
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                    <h3 className="text-xs uppercase font-bold mb-4 flex items-center gap-2">
                      <Lock className="w-4 h-4 text-amber-500" /> Task Context
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="text-[10px] uppercase text-gray-500 block mb-2">Original Instructions</label>
                        <div className="bg-black/40 p-4 rounded border border-white/5 text-sm italic leading-relaxed text-gray-300">
                          "{selectedCase.evidence.instructions}"
                        </div>
                      </div>
                      <div>
                        <label className="text-[10px] uppercase text-gray-500 block mb-2">Node Proof Submission</label>
                        <div className="bg-black/40 p-4 rounded border border-white/5 text-sm font-mono text-amber-500/80">
                          {selectedCase.evidence.proof}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                    <h3 className="text-xs uppercase font-bold mb-4 flex items-center gap-2">
                      <Gavel className="w-4 h-4 text-amber-500" /> Adjudication Terminal
                    </h3>
                    <div className="space-y-4">
                       <button onClick={() => handleVote('VALID')} disabled={isVoting} className="w-full py-4 bg-green-500/10 hover:bg-green-500/20 border border-green-500/20 rounded-lg text-green-500 font-bold text-sm uppercase">Valid Execution</button>
                       <button onClick={() => handleVote('FRAUD')} disabled={isVoting} className="w-full py-4 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 rounded-lg text-red-500 font-bold text-sm uppercase">Fraudulent Claim</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 4. CLAIM DETAIL VIEW */}
          {selectedClaim && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <button 
                onClick={() => setSelectedClaim(null)}
                className="text-xs text-gray-500 hover:text-white mb-4 flex items-center gap-2 font-bold"
              >
                <ArrowRight className="w-3 h-3 rotate-180" /> Back to Claims
              </button>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-6">
                  <div className="bg-[#0d0d0e] border border-blue-500/20 rounded-lg p-8">
                    <div className="flex items-center gap-3 mb-6">
                      <Activity className="w-5 h-5 text-blue-400" />
                      <h3 className="text-xs uppercase font-black tracking-widest text-blue-400">Incident Forensic Log</h3>
                    </div>
                    <div className="space-y-6">
                      <div>
                        <label className="text-[10px] uppercase text-gray-600 block mb-2 font-bold">Failure Signature</label>
                        <div className="bg-black/60 p-4 rounded border border-white/5 text-xs font-mono text-red-400/80 leading-relaxed">
                          {selectedClaim.proof_log}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-white/[0.02] p-4 rounded border border-white/5">
                          <p className="text-[9px] text-gray-500 uppercase mb-1">Claimant Node</p>
                          <p className="text-[10px] text-blue-300 font-bold">{selectedClaim.node_id}</p>
                        </div>
                        <div className="bg-white/[0.02] p-4 rounded border border-white/5">
                          <p className="text-[9px] text-gray-500 uppercase mb-1">Loss Value</p>
                          <p className="text-[10px] text-white font-bold">{selectedClaim.amount_sats} SATS</p>
                        </div>
                      </div>
                      <div className="p-4 bg-blue-500/5 border border-blue-500/10 rounded">
                        <p className="text-[10px] text-blue-200/60 leading-relaxed italic">
                          "Systemic LND failures occur when the HTLC is accepted at the gossip layer but the preimage revelation fails the local validation check. This is a protocol-level fault."
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="bg-[#0d0d0e] border border-blue-500/20 rounded-lg p-8">
                    <h3 className="text-xs uppercase font-black tracking-widest text-blue-400 mb-6 flex items-center gap-2">
                      <Banknote className="w-4 h-4" /> Compensation Terminal
                    </h3>
                    <div className="space-y-6">
                       <p className="text-[11px] text-gray-400 leading-relaxed">
                        Verify if the forensic log matches a known systemic bug. Approved claims will be paid instantly from the 0.1% insurance tax pool via <span className="text-white underline underline-offset-4">Keysend</span>.
                      </p>

                      <div className="space-y-3">
                        <button 
                          disabled={isVoting}
                          onClick={() => handleVote('APPROVE')}
                          className="w-full py-5 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 rounded-lg flex items-center justify-between px-6 transition-all group"
                        >
                          <div className="flex items-center gap-4">
                            <CheckCircle2 className="w-6 h-6 text-blue-400" />
                            <div className="text-left">
                              <p className="text-sm font-black text-blue-400 uppercase tracking-tighter">Authorize Payout</p>
                              <p className="text-[9px] text-gray-500 uppercase">Funds released from Pool</p>
                            </div>
                          </div>
                        </button>

                        <button 
                          disabled={isVoting}
                          onClick={() => handleVote('DENY')}
                          className="w-full py-5 border border-white/5 hover:bg-white/5 rounded-lg flex items-center justify-between px-6 transition-all group"
                        >
                          <div className="flex items-center gap-4 opacity-40">
                            <XCircle className="w-6 h-6 text-gray-500" />
                            <div className="text-left">
                              <p className="text-sm font-black text-gray-400 uppercase tracking-tighter">Reject Claim</p>
                              <p className="text-[9px] text-gray-600 uppercase">Suspected False Proof</p>
                            </div>
                          </div>
                        </button>
                      </div>

                      {isVoting && (
                         <div className="text-center py-4 animate-pulse">
                            <p className="text-[10px] text-blue-400 uppercase font-black">Releasing Satoshis from Pool Wallet...</p>
                         </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

        </main>
      </div>

      {/* Background Grid Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-[-1]" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '30px 30px' }} 
      />
    </div>
  );
};

export default App;
