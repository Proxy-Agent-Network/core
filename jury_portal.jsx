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
  AlertTriangle,
  BarChart3,
  TrendingUp,
  Scale,
  UserCircle,
  Award,
  Trophy,
  Download,
  FileText
} from 'lucide-react';

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [isVoting, setIsVoting] = useState(false);

  // Stats & Environment
  const [stats] = useState({
    reputation: 982,
    staked_bond: 2000000,
    earned_fees: 45200,
    successful_verdicts: 124,
    insurance_pool_depth: 10450200,
    network_consensus_avg: "91.4%",
    accuracy_rate: "98.2%",
    tier: "SUPER-ELITE"
  });

  // Personal Progress History
  const [performanceHistory] = useState({
    reputation_trend: [940, 945, 952, 960, 975, 982],
    earnings_trend: [5000, 12000, 25000, 31000, 41000, 45200],
    task_breakdown: [
      { type: "SMS", accuracy: 100, count: 50 },
      { type: "KYC", accuracy: 96, count: 42 },
      { type: "LEGAL", accuracy: 98, count: 32 }
    ]
  });

  // 1. Pending Cases Docket
  const [cases] = useState([
    {
      id: "CASE-885-4",
      type: "SMS_VERIFICATION",
      status: "PENDING",
      timestamp: "2026-02-11 12:12:00",
      dispute_reason: "Agent claims code relay was incorrect.",
      evidence: {
        instructions: "Relay the 6-digit code sent to +1 555-0199.",
        proof: "Input: 882190 | Screenshot provided: YES",
      },
      value: 50000,
      reward: 500
    }
  ]);

  // 2. Automated Insurance Claims
  const [claims] = useState([
    {
      id: "CLAIM-X01",
      node_id: "node_unlucky_operator",
      amount_sats: 10000,
      reason: "SYSTEMIC_LND_FAILURE",
      timestamp: "2026-02-11 10:15:00",
      proof_log: "Max Retries (5/5) exceeded. Preimage: 30450221... HTLC accepted but revelation failed.",
      severity: "SEV-2"
    }
  ]);

  // 3. Recent Verdicts
  const [verdicts] = useState([
    {
      id: "CASE-882-9",
      type: "SMS_VERIFICATION",
      outcome: "VALID",
      consensus: "94.2%",
      jurors: 7,
      date: "2026-02-10",
      summary: "Node provided clear OCR-verifiable screenshot."
    },
    {
      id: "CASE-901-2",
      type: "PHYSICAL_GEOFENCE",
      outcome: "FRAUDULENT",
      consensus: "88.1%",
      jurors: 7,
      date: "2026-02-11",
      summary: "Node heartbeat was 0.62km outside target radius."
    }
  ]);

  const handleVote = (verdict) => {
    setIsVoting(true);
    setTimeout(() => {
      setIsVoting(false);
      setSelectedCase(null);
      setSelectedClaim(null);
    }, 1200);
  };

  /**
   * Generates a compliant CSV export based on core/economics/tax_engine.py
   */
  const handleTaxExport = () => {
    const csvRows = [
      ["DATE", "TX_ID", "AMOUNT_SATS", "TYPE", "NOTES"],
      ["2026-02-10", "TX-882-9", "500", "ADJUDICATION_FEE", "Case 882-9 Verdict"],
      ["2026-02-11", "TX-SLASH-BONUS", "15000", "REWARD", "Consensus Slash Share"],
      ["2026-02-11", "TX-LIFETIME-TOTAL", stats.earned_fees.toString(), "SUMMARY", "Total Epoch Earnings"]
    ];
    
    const csvContent = "data:text/csv;charset=utf-8," + csvRows.map(e => e.join(",")).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `PROXY_TAX_REPORT_${stats.tier}_2026.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
            <h1 className="text-sm font-bold tracking-tighter text-white uppercase">Jury Tribunal v2.0</h1>
            <p className="text-[10px] text-amber-500/70 uppercase">Tax Compliance Integrated</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6 text-[11px]">
          <div className="flex flex-col items-end">
            <span className="text-gray-500 uppercase">Identity Tier</span>
            <span className="text-green-500 flex items-center gap-1 font-bold">
              <Award className="w-3 h-3" /> {stats.tier}
            </span>
          </div>
          <div className="h-8 w-px bg-white/10" />
          <div className="flex flex-col items-end">
            <span className="text-gray-500 uppercase">Your Bond</span>
            <span className="text-white">{(stats.staked_bond / 1000000).toFixed(1)}M SATS</span>
          </div>
          <div className="flex items-center gap-2 bg-white/5 px-3 py-2 rounded border border-white/10">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-white font-bold text-xs">NODE_ELITE_X29</span>
          </div>
        </div>
      </header>

      <div className="max-w-[1400px] mx-auto p-6 grid grid-cols-12 gap-6">
        {/* Sidebar / Stats */}
        <aside className="col-span-12 lg:col-span-3 space-y-4">
          <div className="bg-[#0d0d0e] border border-white/10 p-5 rounded-lg">
            <h3 className="text-[10px] uppercase text-gray-500 mb-4 font-bold tracking-widest">Judicial Standing</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center text-sm font-bold">
                <span>Reputation</span>
                <span className="text-amber-500">{stats.reputation}/1000</span>
              </div>
              <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                <div 
                  className="bg-amber-500 h-full" 
                  style={{ width: `${(stats.reputation / 1000) * 100}%` }} 
                />
              </div>
              <div className="grid grid-cols-2 gap-2 pt-2">
                <div className="bg-white/5 p-3 rounded border border-white/5 text-center">
                  <p className="text-[9px] text-gray-500 uppercase mb-1">Accuracy</p>
                  <p className="text-sm font-bold text-white">{stats.accuracy_rate}</p>
                </div>
                <div className="bg-white/5 p-3 rounded border border-white/5 text-center">
                  <p className="text-[9px] text-gray-500 uppercase mb-1">Yield</p>
                  <p className="text-sm font-bold text-green-500">+{stats.earned_fees}</p>
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
              onClick={() => { setActiveTab('history'); setSelectedCase(null); setSelectedClaim(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm transition-all ${activeTab === 'history' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Scale className="w-4 h-4" /> Recent Verdicts
            </button>
            <button 
              onClick={() => { setActiveTab('stats'); setSelectedCase(null); setSelectedClaim(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm transition-all ${activeTab === 'stats' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <TrendingUp className="w-4 h-4" /> Personal Standing
            </button>
            <button 
              onClick={() => { setActiveTab('insurance'); setSelectedCase(null); setSelectedClaim(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm transition-all ${activeTab === 'insurance' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <HeartPulse className="w-4 h-4" /> Insurance Claims
            </button>
          </nav>

          <div className="p-4 bg-amber-500/5 border border-amber-500/10 rounded-lg">
            <p className="text-[10px] text-amber-500/50 leading-relaxed italic">
              "Judicial activity is immutable. Export your history for compliant jurisdictional reporting."
            </p>
          </div>
        </aside>

        {/* Main Interface */}
        <main className="col-span-12 lg:col-span-9">
          
          {/* 1. DISPUTE CASES VIEW */}
          {activeTab === 'cases' && !selectedCase && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden animate-in fade-in duration-300">
              <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/[0.02]">
                <h2 className="text-xs uppercase font-bold tracking-widest flex items-center gap-2">
                  <Activity className="w-4 h-4 text-amber-500" /> Pending Case Docket
                </h2>
              </div>
              <div className="divide-y divide-white/5">
                {cases.map((c) => (
                  <div key={c.id} className="p-5 hover:bg-white/[0.02] transition-colors flex items-center justify-between group">
                    <div className="flex items-center gap-6">
                      <div className="w-10 h-10 bg-white/5 rounded flex items-center justify-center border border-white/10 text-blue-400">
                        <Zap className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-white font-bold text-sm">{c.id}</span>
                          <span className="text-[10px] bg-white/5 px-2 py-0.5 rounded text-gray-400 uppercase font-bold tracking-tighter">{c.type}</span>
                        </div>
                        <p className="text-xs text-gray-500">{c.dispute_reason}</p>
                      </div>
                    </div>
                    <button 
                      onClick={() => setSelectedCase(c)}
                      className="bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-2 rounded text-xs transition-all flex items-center gap-2 group-hover:border-amber-500/30"
                    >
                      Enter Locker <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 2. RECENT VERDICTS FEED */}
          {activeTab === 'history' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-black/40 border border-white/5 p-4 rounded-lg">
                  <span className="text-[9px] text-gray-600 uppercase block mb-1">Total Adjudications</span>
                  <p className="text-xl font-bold text-white">4,821</p>
                </div>
                <div className="bg-black/40 border border-white/5 p-4 rounded-lg">
                  <span className="text-[9px] text-gray-600 uppercase block mb-1">Outcome Skew</span>
                  <p className="text-xl font-bold text-green-500">82% Valid</p>
                </div>
                <div className="bg-black/40 border border-white/5 p-4 rounded-lg">
                  <span className="text-[9px] text-gray-600 uppercase block mb-1">Slashing Yield</span>
                  <p className="text-xl font-bold text-amber-500">12.4M Sats</p>
                </div>
              </div>

              <div className="bg-[#0d0d0e] border border-green-500/20 rounded-lg overflow-hidden">
                <div className="p-4 border-b border-green-500/20 flex justify-between items-center bg-green-500/[0.02]">
                  <h2 className="text-xs uppercase font-bold tracking-widest flex items-center gap-2 text-green-400">
                    <Scale className="w-4 h-4" /> Completed Epochs
                  </h2>
                </div>
                <div className="divide-y divide-white/5">
                  {verdicts.map((v) => (
                    <div key={v.id} className="p-6 hover:bg-white/[0.01] transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-bold text-white">{v.id}</span>
                          <span className="text-[9px] text-gray-600 mono uppercase tracking-widest">{v.date}</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <span className="text-[9px] text-gray-600 uppercase block">Consensus</span>
                            <span className="text-sm font-black text-green-500">{v.consensus}</span>
                          </div>
                          <div className={`px-3 py-1 rounded text-[10px] font-black uppercase tracking-widest ${v.outcome === 'VALID' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                            {v.outcome}
                          </div>
                        </div>
                      </div>
                      <p className="text-xs text-gray-400 leading-relaxed max-w-2xl mb-3">{v.summary}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 3. PERSONAL STATS DASHBOARD (v2.0 UPDATE) */}
          {activeTab === 'stats' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
              
              {/* Performance Cards & Compliance Trigger */}
              <div className="flex flex-col md:flex-row gap-4">
                 <div className="flex-1 bg-purple-500/5 border border-purple-500/20 p-5 rounded-lg">
                    <span className="text-[9px] text-purple-400 uppercase font-black block mb-2 tracking-widest">Growth Factor</span>
                    <p className="text-2xl font-black text-white">+42 <span className="text-xs text-gray-500 font-normal">REP / Mo</span></p>
                 </div>
                 <div className="flex-1 bg-green-500/5 border border-green-500/20 p-5 rounded-lg relative group overflow-hidden">
                    <span className="text-[9px] text-green-400 uppercase font-black block mb-2 tracking-widest">Lifetime Sats</span>
                    <p className="text-2xl font-black text-white">{stats.earned_fees.toLocaleString()}</p>
                    {/* TAX EXPORT BUTTON */}
                    <button 
                      onClick={handleTaxExport}
                      className="absolute top-4 right-4 p-2 bg-green-500/10 hover:bg-green-500/20 rounded border border-green-500/30 transition-all text-green-500 group-hover:scale-110"
                      title="Download Tax Report"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                 </div>
                 <div className="flex-1 bg-amber-500/5 border border-amber-500/20 p-5 rounded-lg">
                    <span className="text-[9px] text-amber-400 uppercase font-black block mb-2 tracking-widest">Consensus Streak</span>
                    <p className="text-2xl font-black text-white">18 <span className="text-xs text-gray-500 font-normal">Epochs</span></p>
                 </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-bold mb-6 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-purple-400" /> Reputation Momentum
                  </h3>
                  <div className="flex items-end gap-2 h-40 mb-4 px-2">
                    {performanceHistory.reputation_trend.map((val, i) => (
                      <div key={i} className="flex-1 flex flex-col items-center group">
                        <div 
                          className="w-full bg-purple-500/20 border-t-2 border-purple-500/50 rounded-t-sm transition-all group-hover:bg-purple-500/40"
                          style={{ height: `${(val / 1000) * 100}%` }}
                        ></div>
                        <span className="text-[8px] text-gray-600 mt-2 uppercase">W{i+1}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-bold mb-6 flex items-center gap-2">
                    <Scale className="w-4 h-4 text-green-400" /> Adjudication Accuracy
                  </h3>
                  <div className="space-y-4">
                    {performanceHistory.task_breakdown.map((task) => (
                      <div key={task.type}>
                        <div className="flex justify-between text-[10px] mb-1.5 uppercase">
                          <span className="text-gray-400 font-bold">{task.type} Protocols</span>
                          <span className="text-white">{task.accuracy}% ({task.count} cases)</span>
                        </div>
                        <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${task.accuracy >= 98 ? 'bg-green-500' : 'bg-amber-500'}`} 
                            style={{ width: `${task.accuracy}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Judicial Compliance Footer */}
              <div className="bg-white/[0.02] border border-white/5 rounded-lg p-5 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-white/5 rounded">
                      <FileText className="w-5 h-5 text-gray-400" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-white uppercase tracking-tighter">Jurisdictional Tax Ledger</p>
                      <p className="text-[10px] text-gray-500">Reportable threshold (US 1099-NEC): $600.00 / ~600k Sats</p>
                    </div>
                  </div>
                  <button 
                    onClick={handleTaxExport}
                    className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded text-[10px] font-black uppercase tracking-widest transition-all"
                  >
                    Generate 2026 CSV <Download className="w-3 h-3" />
                  </button>
              </div>
            </div>
          )}

          {/* 4. INSURANCE CLAIMS VIEW */}
          {activeTab === 'insurance' && !selectedClaim && (
            <div className="bg-[#0d0d0e] border border-blue-500/20 rounded-lg overflow-hidden animate-in fade-in duration-300">
               <div className="p-4 border-b border-blue-500/20 flex justify-between items-center bg-blue-500/[0.02]">
                <h2 className="text-xs uppercase font-bold tracking-widest flex items-center gap-2">
                  <HeartPulse className="w-4 h-4 text-blue-400" /> Automated Insurance Claims
                </h2>
              </div>
              <div className="divide-y divide-white/5">
                {claims.map((claim) => (
                  <div key={claim.id} className="p-6 hover:bg-white/[0.02] transition-colors flex items-center justify-between group">
                    <div className="flex items-center gap-6">
                      <div className="w-12 h-12 bg-blue-500/10 rounded flex flex-col items-center justify-center border border-blue-500/20 text-blue-400">
                        <AlertTriangle className="w-5 h-5" />
                        <span className="text-[8px] font-bold mt-1">{claim.severity}</span>
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-white font-bold text-sm">{claim.id}</span>
                          <span className="text-[9px] bg-red-500/10 px-2 py-0.5 rounded text-red-400 uppercase font-bold tracking-tighter">Settlement Failure</span>
                        </div>
                        <p className="text-xs text-gray-500">Node: {claim.node_id}</p>
                      </div>
                    </div>
                    <button 
                      onClick={() => setSelectedClaim(claim)}
                      className="bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 px-4 py-2 rounded text-xs transition-all flex items-center gap-2 text-blue-400 font-bold"
                    >
                      Audit Incident <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* DETAIL VIEWS */}
          {selectedCase && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <button onClick={() => setSelectedCase(null)} className="text-xs text-gray-500 hover:text-white mb-4 flex items-center gap-2 font-bold">
                <ArrowRight className="w-3 h-3 rotate-180" /> Back to Docket
              </button>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-bold mb-4 flex items-center gap-2 text-amber-500">
                    <Lock className="w-4 h-4" /> Adjudication Locker
                  </h3>
                  <div className="space-y-4">
                    <div className="bg-black/60 p-4 border border-white/5 rounded text-xs text-gray-400 leading-relaxed italic">
                      "{selectedCase.evidence.instructions}"
                    </div>
                  </div>
                </div>
                <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-bold mb-6 text-white">Cast Verified Verdict</h3>
                  <div className="space-y-3">
                    <button onClick={() => handleVote('VALID')} disabled={isVoting} className="w-full py-4 bg-green-500/10 hover:bg-green-500/20 border border-green-500/20 rounded text-green-500 font-black text-xs uppercase tracking-widest">Valid Work</button>
                    <button onClick={() => handleVote('FRAUD')} disabled={isVoting} className="w-full py-4 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 rounded text-red-500 font-black text-xs uppercase tracking-widest">Fraudulent Proof</button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedClaim && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <button onClick={() => setSelectedClaim(null)} className="text-xs text-gray-500 hover:text-white mb-4 flex items-center gap-2 font-bold">
                <ArrowRight className="w-3 h-3 rotate-180" /> Back to Claims
              </button>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0d0d0e] border border-blue-500/20 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-black text-blue-400 mb-6">Incident Forensics</h3>
                  <div className="bg-black/60 p-4 border border-white/5 rounded text-[10px] mono text-red-400/80 leading-relaxed">
                    {selectedClaim.proof_log}
                  </div>
                </div>
                <div className="bg-[#0d0d0e] border border-blue-500/20 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-black text-blue-400 mb-6">Pool Payout Terminal</h3>
                  <button onClick={() => handleVote('APPROVE')} disabled={isVoting} className="w-full py-5 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 rounded flex items-center justify-center gap-3 text-blue-400 font-black text-xs uppercase tracking-widest">
                    <CheckCircle2 className="w-4 h-4" /> Authorize Keysend
                  </button>
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
