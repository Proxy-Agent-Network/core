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
  UserCheck
} from 'lucide-react';

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  const [isVoting, setIsVoting] = useState(false);

  // Mock Data for the Tribunal
  const [stats] = useState({
    reputation: 982,
    staked_bond: 2000000,
    earned_fees: 45200,
    successful_verdicts: 124
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

  const handleVote = (verdict) => {
    setIsVoting(true);
    setTimeout(() => {
      setIsVoting(false);
      setSelectedCase(null);
      // In prod, this would trigger the jury_bond.py slashing engine
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
            <h1 className="text-sm font-bold tracking-tighter text-white uppercase">Jury Tribunal v1.6</h1>
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
              onClick={() => setActiveTab('cases')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm transition-all ${activeTab === 'cases' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Activity className="w-4 h-4" /> Open Disputes
            </button>
            <button 
              onClick={() => setActiveTab('history')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm transition-all ${activeTab === 'history' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Clock className="w-4 h-4" /> Verdict History
            </button>
            <button 
              onClick={() => setActiveTab('bond')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm transition-all ${activeTab === 'bond' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Lock className="w-4 h-4" /> Bond Management
            </button>
          </nav>

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
          {!selectedCase ? (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden">
              <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/[0.02]">
                <h2 className="text-xs uppercase font-bold tracking-widest flex items-center gap-2">
                  <Activity className="w-4 h-4 text-amber-500" /> Pending Case Docket
                </h2>
                <span className="text-[10px] text-gray-500">2 cases require review</span>
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
          ) : (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <button 
                onClick={() => setSelectedCase(null)}
                className="text-xs text-gray-500 hover:text-white mb-4 flex items-center gap-2"
              >
                <ArrowRight className="w-3 h-3 rotate-180" /> Back to Docket
              </button>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Evidence Column */}
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
                      <div className="bg-amber-500/5 p-4 rounded border border-amber-500/10">
                        <label className="text-[10px] uppercase text-amber-500 block mb-1 font-bold">Protocol Audit Log</label>
                        <p className="text-xs text-amber-200/60 font-mono">
                          {selectedCase.evidence.audit_log}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Verdict Column */}
                <div className="space-y-6">
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                    <h3 className="text-xs uppercase font-bold mb-4 flex items-center gap-2">
                      <Gavel className="w-4 h-4 text-amber-500" /> Adjudication Terminal
                    </h3>
                    <div className="space-y-6">
                      <p className="text-xs text-gray-400 leading-relaxed">
                        Review the hardware logs and distance thresholds. If the Node's proof matches the Agent's instructions within standard error margins, select <span className="text-green-500">VALID</span>. Otherwise, select <span className="text-red-500">FRAUDULENT</span>.
                      </p>
                      
                      <div className="grid grid-cols-1 gap-3">
                        <button 
                          disabled={isVoting}
                          onClick={() => handleVote('VALID')}
                          className="w-full py-4 bg-green-500/10 hover:bg-green-500/20 border border-green-500/20 rounded-lg flex items-center justify-between px-6 group transition-all"
                        >
                          <div className="flex items-center gap-3">
                            <CheckCircle2 className="w-5 h-5 text-green-500" />
                            <div className="text-left">
                              <p className="text-sm font-bold text-green-500">VALID EXECUTION</p>
                              <p className="text-[10px] text-gray-500 uppercase tracking-tighter">Release Escrow + Reward Node</p>
                            </div>
                          </div>
                          <ArrowRight className="w-4 h-4 text-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </button>

                        <button 
                          disabled={isVoting}
                          onClick={() => handleVote('FRAUDULENT')}
                          className="w-full py-4 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 rounded-lg flex items-center justify-between px-6 group transition-all"
                        >
                          <div className="flex items-center gap-3">
                            <XCircle className="w-5 h-5 text-red-500" />
                            <div className="text-left">
                              <p className="text-sm font-bold text-red-500">FRAUDULENT CLAIM</p>
                              <p className="text-[10px] text-gray-500 uppercase tracking-tighter">Slash Node + Refund Agent</p>
                            </div>
                          </div>
                          <ArrowRight className="w-4 h-4 text-red-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </button>
                      </div>

                      {isVoting && (
                        <div className="flex flex-col items-center gap-3 py-4 animate-pulse">
                          <div className="flex gap-1">
                            <div className="w-1 h-1 bg-amber-500 rounded-full" />
                            <div className="w-1 h-1 bg-amber-500 rounded-full" />
                            <div className="w-1 h-1 bg-amber-500 rounded-full" />
                          </div>
                          <p className="text-[10px] text-amber-500 uppercase font-bold">Cryptographically Signing Verdict...</p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                    <h3 className="text-xs uppercase font-bold mb-4 flex items-center gap-2">
                      <UserCheck className="w-4 h-4 text-blue-400" /> Peer Activity
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center text-[11px]">
                        <span className="text-gray-500">Consensus Quorum</span>
                        <span className="text-white font-bold">2/7 Jurors Voted</span>
                      </div>
                      <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-blue-500 h-full w-[28.5%]" />
                      </div>
                      <p className="text-[10px] text-gray-500 italic">
                        Minimum 4/7 votes required for finality.
                      </p>
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
