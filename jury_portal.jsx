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
  FileText,
  Shield,
  Fingerprint,
  Cpu,
  RefreshCw,
  Key,
  ShieldQuestion,
  Globe,
  Map,
  ZapOff,
  Waves,
  ShieldX,
  PiggyBank,
  ArrowUpRight,
  ArrowDownRight,
  History,
  FileSignature,
  Stamp,
  Wallet,
  Unlock,
  AlertOctagon
} from 'lucide-react';

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [isVoting, setIsVoting] = useState(false);
  
  // v2.2 Hardware States
  const [isRotating, setIsRotating] = useState(false);
  const [keyRotationStep, setKeyRotationStep] = useState(0); 
  const [nodeId, setNodeId] = useState("NODE_ELITE_X29");

  // v2.7 Stake Management State
  const [withdrawalState, setWithdrawalState] = useState('IDLE'); // IDLE, REQUESTED, COOLING_OFF
  const [cooldownDaysRemaining, setCooldownDaysRemaining] = useState(14);
  const [isProcessingStake, setIsProcessingStake] = useState(false);

  // v2.3 Sybil Defense State
  const [sybilClusters] = useState([
    {
      id: "CLUSTER-ALPHA-9",
      risk_score: 88,
      nodes: 12,
      ip_range: "192.168.1.0/24",
      deviation: "+14.2%",
      status: "FLAGGED",
      logic: "Identical TPM firmware signatures & simultaneous heartbeats detected."
    }
  ]);

  // v2.4 Brownout State
  const [brownoutLevel, setBrownoutLevel] = useState('GREEN'); // GREEN, YELLOW, ORANGE, RED
  const [mempoolDepth, setMempoolDepth] = useState(6402);
  const [isManualOverride, setIsManualOverride] = useState(false);

  // v2.5 Treasury Audit State
  const [treasuryStats] = useState({
    total_inflow: 84290100,
    total_outflow: 12500000,
    slashing_revenue: 34000000,
    tax_revenue: 50290100,
    net_reserves: 71790100
  });

  const [transactions] = useState([
    { id: "TX-99812", type: "SLASH", amount: 250000, timestamp: "2026-02-11 11:02:00", node: "NODE_MALICIOUS_X8", status: "CONFIRMED" },
    { id: "TX-99811", type: "TAX", amount: 4200, timestamp: "2026-02-11 10:58:12", node: "NODE_ELITE_X29", status: "CONFIRMED" },
    { id: "TX-99810", type: "PAYOUT", amount: 10000, timestamp: "2026-02-11 10:45:00", node: "CLAIM-X01", status: "SETTLED" }
  ]);

  // v2.6 Notary Templates State
  const [notaryTemplates] = useState([
    {
      id: "POA-US-DE-V1",
      jurisdiction: "US_DE",
      title: "Delaware Statutory PoA",
      legislation: "Delaware Code Title 12, Chapter 40",
      last_audit: "2026-01-15",
      status: "VERIFIED",
      body: "# LIMITED POWER OF ATTORNEY (US - DELAWARE)\n\nI, [PRINCIPAL NAME], identify by the cryptographic signature attached, hereby appoint the Human Proxy Node [PROXY NODE ID] as my attorney-in-fact.\n\nSCOPE: Corporate Filings, Identity Verification, Contractual Execution..."
    },
    {
      id: "POA-UK-ENG-V1.2",
      jurisdiction: "UK",
      title: "England & Wales PoA",
      legislation: "Powers of Attorney Act 1971",
      last_audit: "2026-02-01",
      status: "AUDIT_REQUIRED",
      body: "# LIMITED POWER OF ATTORNEY (UK JURISDICTION)\n\nTHIS INSTRUMENT is made on the date of the cryptographic timestamp by the Principal... Attorney is authorized to act on behalf of the Principal for the purpose of executing instructions..."
    }
  ]);

  // Stats & Environment
  const [stats] = useState({
    reputation: 982,
    staked_bond: 2000000,
    earned_fees: 45200,
    successful_verdicts: 124,
    insurance_pool_depth: 10450200,
    network_consensus_avg: "91.4%",
    accuracy_rate: "98.2%",
    tier: "SUPER-ELITE",
    is_appellate_eligible: true
  });

  // Appellate VRF State
  const [appellateContext] = useState({
    incident_id: "SEV1-2026-02-11-JURY-COLLUSION",
    btc_block_hash: "00000000000000000001859c25f483c613098555e71415411707572706c6521",
    vrf_score: "8a2f...c91e",
    is_selected: true,
    roster: [
      { id: "NODE_ELITE_X29", score: "8a2f...", status: "YOU" },
      { id: "NODE_ALPHA_001", score: "9b1e...", status: "ACTIVE" }
    ]
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
    }
  ]);

  const handleVote = (verdict) => {
    setIsVoting(true);
    setTimeout(() => {
      setIsVoting(false);
      setSelectedCase(null);
      setSelectedClaim(null);
      setSelectedTemplate(null);
    }, 1200);
  };

  /**
   * Requesting a Stake Withdrawal (v2.7)
   */
  const initiateWithdrawal = () => {
    setIsProcessingStake(true);
    setTimeout(() => {
      setWithdrawalState('COOLING_OFF');
      setIsProcessingStake(false);
    }, 1500);
  };

  const startKeyRotation = () => {
    setIsRotating(true);
    setKeyRotationStep(1);
    setTimeout(() => {
      setKeyRotationStep(2);
      setTimeout(() => {
        setKeyRotationStep(3);
        setTimeout(() => {
          const newSuffix = Math.random().toString(36).substring(7).toUpperCase();
          setNodeId(`NODE_ELITE_${newSuffix}`);
          setIsRotating(false);
          setKeyRotationStep(0);
        }, 2000);
      }, 2500);
    }, 1500);
  };

  const handleTaxExport = () => {
    const csvRows = [
      ["DATE", "TX_ID", "AMOUNT_SATS", "TYPE", "NOTES"],
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
            <h1 className="text-sm font-bold tracking-tighter text-white uppercase tracking-widest">Jury Tribunal v2.7</h1>
            <p className="text-[10px] text-amber-500/70 uppercase tracking-widest">Stake Custody Active</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6 text-[11px]">
          <div className="flex flex-col items-end">
            <span className="text-gray-500 uppercase font-bold tracking-tighter">Identity Tier</span>
            <span className="text-green-500 flex items-center gap-1 font-bold">
              <Award className="w-3 h-3" /> {stats.tier}
            </span>
          </div>
          <div className="h-8 w-px bg-white/10" />
          <div className="flex flex-col items-end">
            <span className="text-gray-500 uppercase font-bold tracking-tighter">Network Reserves</span>
            <span className="text-white font-bold">{(treasuryStats.net_reserves / 100000000).toFixed(2)} BTC</span>
          </div>
          <div className="flex items-center gap-2 bg-white/5 px-3 py-2 rounded border border-white/10">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-white font-bold text-xs">{nodeId}</span>
          </div>
        </div>
      </header>

      <div className="max-w-[1400px] mx-auto p-6 grid grid-cols-12 gap-6">
        {/* Sidebar / Stats */}
        <aside className="col-span-12 lg:col-span-3 space-y-4">
          <div className="bg-[#0d0d0e] border border-white/10 p-5 rounded-lg">
            <h3 className="text-[10px] uppercase text-gray-500 mb-4 font-bold tracking-widest text-glow">Judicial Standing</h3>
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
                  <p className="text-[9px] text-gray-500 uppercase mb-1 font-bold">Accuracy</p>
                  <p className="text-sm font-bold text-white">{stats.accuracy_rate}</p>
                </div>
                <div className="bg-white/5 p-3 rounded border border-white/5 text-center">
                  <p className="text-[9px] text-gray-500 uppercase mb-1 font-bold">Yield</p>
                  <p className="text-sm font-bold text-green-500">+{stats.earned_fees}</p>
                </div>
              </div>
            </div>
          </div>

          <nav className="space-y-1">
            <button 
              onClick={() => { setActiveTab('cases'); setSelectedCase(null); setSelectedClaim(null); setSelectedTemplate(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'cases' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Activity className="w-4 h-4" /> Open Disputes
            </button>
            <button 
              onClick={() => { setActiveTab('staking'); setSelectedCase(null); setSelectedClaim(null); setSelectedTemplate(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'staking' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Wallet className="w-4 h-4" /> Stake Management
            </button>
            <button 
              onClick={() => { setActiveTab('notary'); setSelectedCase(null); setSelectedClaim(null); setSelectedTemplate(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'notary' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Stamp className="w-4 h-4" /> Notary Templates
            </button>
            <button 
              onClick={() => { setActiveTab('treasury'); setSelectedCase(null); setSelectedClaim(null); setSelectedTemplate(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'treasury' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <PiggyBank className="w-4 h-4" /> Treasury Audit
            </button>
            <button 
              onClick={() => { setActiveTab('brownout'); setSelectedCase(null); setSelectedClaim(null); setSelectedTemplate(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'brownout' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Waves className="w-4 h-4" /> Brownout Control
            </button>
            <button 
              onClick={() => { setActiveTab('sybil'); setSelectedCase(null); setSelectedClaim(null); setSelectedTemplate(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'sybil' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Globe className="w-4 h-4" /> Sybil Defense
            </button>
            <button 
              onClick={() => { setActiveTab('appellate'); setSelectedCase(null); setSelectedClaim(null); setSelectedTemplate(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'appellate' ? 'bg-red-500/10 text-red-500 border border-red-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Shield className="w-4 h-4" /> Appellate Court
            </button>
          </nav>

          <div className="p-4 bg-green-500/5 border border-green-500/10 rounded-lg">
            <p className="text-[10px] text-green-400/60 font-bold leading-relaxed uppercase tracking-tighter italic">
              "Collateral release is subject to a 14-day observation window to prevent exit-scamming of contested epochs."
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

          {/* 2. STAKE MANAGEMENT VIEW (v2.7 FEATURE) */}
          {activeTab === 'staking' && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   
                   {/* Current Stake Card */}
                   <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8">
                      <div className="flex items-center justify-between mb-8">
                         <h3 className="text-xs uppercase font-black tracking-widest text-white flex items-center gap-3 text-glow">
                            <Lock className="w-5 h-5 text-green-500" /> Locked Collateral
                         </h3>
                         <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded bg-green-500/10 text-green-500 border border-green-500/20">
                            STAKED
                         </span>
                      </div>
                      <div className="space-y-6">
                         <div>
                            <span className="text-[10px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Active Bond Balance</span>
                            <div className="flex items-baseline gap-2">
                               <span className="text-4xl font-black text-white">{(stats.staked_bond / 1000000).toFixed(2)}</span>
                               <span className="text-sm font-bold text-gray-500 uppercase tracking-widest">M SATS</span>
                            </div>
                         </div>

                         <div className="p-4 bg-white/5 rounded border border-white/10 space-y-3">
                            <div className="flex justify-between items-center text-[10px] uppercase font-black">
                               <span className="text-gray-500">Tier Requirements</span>
                               <span className="text-green-500 font-bold">MET (SUPER-ELITE)</span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] uppercase font-black">
                               <span className="text-gray-500">Slashing Exposure</span>
                               <span className="text-red-400 font-bold">30% PER DISPUTE</span>
                            </div>
                         </div>

                         {withdrawalState === 'IDLE' ? (
                            <button 
                               onClick={initiateWithdrawal}
                               disabled={isProcessingStake}
                               className="w-full py-4 bg-red-500/5 hover:bg-red-500/10 border border-red-500/20 hover:border-red-500/50 rounded-lg flex items-center justify-center gap-3 transition-all group"
                            >
                               <Unlock className="w-4 h-4 text-red-500" />
                               <span className="text-xs font-black uppercase text-red-500 tracking-widest">
                                  {isProcessingStake ? 'COMMUNICATING WITH MULTISIG...' : 'Request Release of Stake'}
                               </span>
                            </button>
                         ) : (
                            <div className="w-full py-4 bg-orange-500/10 border border-orange-500/30 rounded-lg flex flex-col items-center text-center px-4">
                               <div className="flex items-center gap-2 text-orange-400 mb-1">
                                  <Clock className="w-4 h-4 animate-spin-slow" />
                                  <span className="text-[10px] font-black uppercase">Cooling-off Period Active</span>
                               </div>
                               <p className="text-[9px] text-orange-400/60 leading-tight">Identity suspended. Final release in {cooldownDaysRemaining} days.</p>
                            </div>
                         )}
                      </div>
                   </div>

                   {/* Policy and Warnings */}
                   <div className="space-y-6">
                      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                         <h3 className="text-xs uppercase font-black text-gray-400 mb-6 flex items-center gap-3">
                            <AlertOctagon className="w-5 h-5 text-amber-500" /> Staking Policy v1.1
                         </h3>
                         <div className="space-y-4">
                            <div className="flex gap-4">
                               <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-1.5 flex-shrink-0" />
                               <p className="text-[11px] text-gray-500 leading-relaxed">
                                  Withdrawing your bond will <span className="text-white font-bold">immediately terminate</span> your Super-Elite adjudication status and stop all fee-sharing.
                               </p>
                            </div>
                            <div className="flex gap-4">
                               <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-1.5 flex-shrink-0" />
                               <p className="text-[11px] text-gray-500 leading-relaxed">
                                  The 14-day cooldown is mandatory. If you are selected for a jury during this window and fail to participate, your remaining bond may be slashed.
                               </p>
                            </div>
                            <div className="flex gap-4">
                               <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-1.5 flex-shrink-0" />
                               <p className="text-[11px] text-gray-500 leading-relaxed">
                                  Funds are released via <span className="text-white font-bold">Lightning Keysend</span> to the identity key associated with your hardware TPM.
                                </p>
                            </div>
                         </div>
                      </div>

                      {/* Yield Projections */}
                      <div className="bg-green-500/5 border border-green-500/20 rounded-lg p-6 flex items-center justify-between">
                         <div>
                            <span className="text-[9px] text-green-500 uppercase font-black block mb-1">Opportunity Cost</span>
                            <p className="text-xs text-gray-300">Staying staked earns ~12% APY in slash bonuses.</p>
                         </div>
                         <TrendingUp className="w-8 h-8 text-green-500/20" />
                      </div>
                   </div>
                </div>

                {/* Staking History */}
                <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden">
                   <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center text-xs uppercase font-black tracking-widest text-gray-500">
                      Stake Transaction Ledger
                   </div>
                   <div className="divide-y divide-white/5">
                      <div className="p-4 flex justify-between items-center hover:bg-white/[0.01]">
                         <div className="flex items-center gap-4">
                            <span className="text-[9px] text-gray-700 font-black">2026-01-01</span>
                            <span className="text-[10px] text-white font-bold">Initial Bond Deposit</span>
                         </div>
                         <span className="text-sm font-black text-green-500">+2,000,000 SATS</span>
                      </div>
                   </div>
                </div>
             </div>
          )}

          {/* 3. NOTARY TEMPLATES VIEW (v2.6) */}
          {activeTab === 'notary' && !selectedTemplate && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
                <div className="bg-[#0d0d0e] border border-blue-500/20 rounded-lg overflow-hidden">
                   <div className="p-4 border-b border-blue-500/20 bg-blue-500/[0.02] flex justify-between items-center">
                      <h2 className="text-xs uppercase font-black tracking-[0.2em] text-blue-400 flex items-center gap-2">
                        <Stamp className="w-4 h-4" /> Global Legal Registry
                      </h2>
                      <span className="text-[9px] text-gray-500 uppercase font-bold">Standardized POA Formats</span>
                   </div>
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-1 p-1 bg-white/5">
                      {notaryTemplates.map((template) => (
                         <div key={template.id} className="bg-[#0d0d0e] p-6 hover:bg-white/[0.01] transition-all flex flex-col justify-between group">
                            <div>
                               <div className="flex justify-between items-start mb-4">
                                  <div className="w-10 h-10 bg-blue-500/10 rounded flex items-center justify-center border border-blue-500/20 text-blue-400 text-glow">
                                     <FileText className="w-5 h-5" />
                                  </div>
                                  <span className={`text-[8px] font-black uppercase px-2 py-1 rounded ${template.status === 'VERIFIED' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500 animate-pulse'}`}>
                                     {template.status.replace('_', ' ')}
                                  </span>
                               </div>
                               <h3 className="text-sm font-black text-white uppercase mb-1 tracking-tight">{template.title}</h3>
                               <p className="text-[10px] text-gray-500 mb-4">{template.id}</p>
                            </div>
                            <button 
                               onClick={() => setSelectedTemplate(template)}
                               className="w-full py-2 bg-white/5 border border-white/10 text-gray-400 text-[10px] font-black uppercase rounded hover:bg-blue-500/10 hover:text-blue-400 transition-all"
                            >
                               Audit Instrument
                            </button>
                         </div>
                      ))}
                   </div>
                </div>
             </div>
          )}

          {/* 4. TREASURY AUDIT VIEW (v2.5) */}
          {activeTab === 'treasury' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-green-500/5 border border-green-500/20 p-5 rounded-lg">
                    <span className="text-[9px] text-green-400 uppercase font-black block mb-2 tracking-widest">Net Reserves</span>
                    <p className="text-2xl font-black text-white">{(treasuryStats.net_reserves / 1000000).toFixed(1)}M <span className="text-xs text-gray-500 font-normal">SATS</span></p>
                  </div>
                  <div className="bg-emerald-500/5 border border-emerald-500/20 p-5 rounded-lg">
                    <span className="text-[9px] text-emerald-400 uppercase font-black block mb-2 tracking-widest">Insurance Depth</span>
                    <p className="text-2xl font-black text-white">{(stats.insurance_pool_depth / 1000000).toFixed(1)}M</p>
                  </div>
               </div>
               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden">
                  <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center text-xs uppercase font-black text-gray-500">Recent Protocol Transactions</div>
                  <div className="divide-y divide-white/5">
                    {transactions.map((tx) => (
                      <div key={tx.id} className="p-5 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className={`p-2 rounded bg-white/5 ${tx.type === 'PAYOUT' ? 'text-red-400' : 'text-green-400'}`}>{tx.type === 'PAYOUT' ? <ArrowDownRight className="w-4 h-4" /> : <ArrowUpRight className="w-4 h-4" />}</div>
                          <div><span className="text-sm font-bold text-white block mb-0.5">{tx.id} <span className="text-[8px] bg-white/5 px-1.5 py-0.5 rounded text-gray-500 uppercase">{tx.type}</span></span><p className="text-[9px] text-gray-600">{tx.timestamp}</p></div>
                        </div>
                        <p className={`text-sm font-black ${tx.type === 'PAYOUT' ? 'text-red-400' : 'text-green-500'}`}>{tx.type === 'PAYOUT' ? '-' : '+'}{tx.amount.toLocaleString()} SATS</p>
                      </div>
                    ))}
                  </div>
               </div>
            </div>
          )}

          {/* 5. BROWNOUT CONTROL VIEW (v2.4) */}
          {activeTab === 'brownout' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                     <span className="text-[10px] text-gray-600 uppercase font-black block mb-4 tracking-widest">Mempool Depth</span>
                     <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black text-white">{mempoolDepth.toLocaleString()}</span>
                        <span className="text-xs text-gray-500 uppercase tracking-widest">Tasks</span>
                     </div>
                  </div>
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                     <span className="text-[10px] text-gray-600 uppercase font-black block mb-4 tracking-widest text-glow">Congestion Level</span>
                     <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full animate-pulse ${
                          brownoutLevel === 'GREEN' ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.3)]' : 
                          brownoutLevel === 'YELLOW' ? 'bg-yellow-500' : 
                          brownoutLevel === 'ORANGE' ? 'bg-orange-500' : 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.3)]'
                        }`} />
                        <span className="text-2xl font-black text-white uppercase">{brownoutLevel}</span>
                     </div>
                  </div>
               </div>

               <div className="bg-[#0d0d0e] border border-orange-500/20 rounded-lg p-8">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                     {['GREEN', 'YELLOW', 'ORANGE', 'RED'].map((level) => (
                        <button 
                           key={level} 
                           disabled={!isManualOverride} 
                           onClick={() => setBrownoutLevel(level)} 
                           className={`p-6 border rounded-lg transition-all flex flex-col items-center text-center ${brownoutLevel === level ? 'bg-white/5 border-orange-500 ring-1 ring-orange-500/20' : 'bg-black/40 border-white/5 opacity-40'} ${!isManualOverride && 'cursor-not-allowed opacity-20'}`}
                        >
                           <span className={`text-[9px] font-black uppercase mb-3 ${level === 'GREEN' ? 'text-green-500' : level === 'YELLOW' ? 'text-yellow-500' : level === 'ORANGE' ? 'text-orange-500' : 'text-red-500'}`}>{level}</span>
                           <p className="text-[10px] text-gray-400 leading-tight">
                             {level === 'GREEN' ? 'Normal Operations (&gt; 300 REP)' : 
                              level === 'YELLOW' ? 'Shed Probationary (&gt; 500 REP)' : 
                              level === 'ORANGE' ? 'Shed Non-Elite (&gt; 700 REP)' : 
                              'Whale Only (&gt; 900 REP)'}
                           </p>
                        </button>
                     ))}
                  </div>
               </div>
            </div>
          )}

          {/* 6. SYBIL DEFENSE VIEW (v2.3) */}
          {activeTab === 'sybil' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-1">
                  <div className="bg-black/60 rounded-lg h-64 flex flex-col items-center justify-center relative overflow-hidden text-center">
                     <Globe className="w-12 h-12 text-red-500/40 mb-4" />
                     <h3 className="text-xs uppercase font-black text-gray-500 tracking-[0.4em]">Global Node Entropy Map</h3>
                  </div>
               </div>
               <div className="bg-[#0d0d0e] border border-red-500/20 rounded-lg overflow-hidden">
                  <div className="p-4 border-b border-red-500/20 bg-red-500/[0.02] flex justify-between items-center text-xs uppercase font-black text-red-400 tracking-widest">
                    Suspicious Node Clusters
                  </div>
                  <div className="divide-y divide-white/5">
                     {sybilClusters.map((cluster) => (
                        <div key={cluster.id} className="p-6 flex flex-col md:flex-row justify-between gap-6 hover:bg-white/[0.01] transition-colors">
                           <div className="flex gap-6">
                              <div className="w-14 h-14 bg-red-500/10 rounded border border-red-500/30 flex flex-col items-center justify-center"><span className="text-[8px] text-red-500 uppercase font-black">Risk</span><span className="text-lg font-black text-white leading-none">{cluster.risk_score}</span></div>
                              <div className="space-y-1"><span className="text-sm font-bold text-white uppercase block">{cluster.id}</span><p className="text-xs text-gray-500 max-w-md">{cluster.logic}</p></div>
                           </div>
                           <button className="px-6 py-2 bg-red-500/10 border border-red-500 text-red-500 text-[10px] font-black uppercase tracking-widest hover:bg-red-500 hover:text-black transition-all">Mass Slash</button>
                        </div>
                     ))}
                  </div>
               </div>
            </div>
          )}

          {/* DETAIL VIEWS (TEMPLATE / CASE / CLAIM) */}
          
          {selectedTemplate && (
             <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                <button onClick={() => setSelectedTemplate(null)} className="text-xs text-gray-500 hover:text-white mb-4 flex items-center gap-2 font-bold uppercase tracking-widest">
                   <ArrowRight className="w-3 h-3 rotate-180" /> Back to Registry
                </button>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                   <div className="bg-[#0d0d0e] border border-blue-500/20 rounded-lg flex flex-col h-[500px]">
                      <div className="p-4 border-b border-blue-500/20 bg-blue-500/[0.02] flex justify-between items-center">
                         <span className="text-[10px] text-blue-400 font-black uppercase text-glow">Instrument Preview</span>
                         <span className="text-[9px] text-gray-600 mono">{selectedTemplate.jurisdiction}</span>
                      </div>
                      <div className="flex-1 p-8 overflow-y-auto bg-black/40 font-mono text-xs leading-relaxed text-gray-400 whitespace-pre-wrap">
                         {selectedTemplate.body}
                      </div>
                   </div>

                   <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between">
                      <div>
                         <h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3">
                            <ShieldCheck className="w-5 h-5 text-green-500" /> Compliance Sign-off
                         </h3>
                         <p className="text-xs text-gray-500 leading-relaxed mb-6">
                            Signature confirms that this instrument is a valid delegation of authority under <span className="text-blue-400 underline">{selectedTemplate.legislation}</span>.
                         </p>
                      </div>
                      <div className="space-y-3">
                         <button 
                            onClick={() => handleVote('SIGN')}
                            disabled={isVoting}
                            className="w-full py-4 bg-green-500/10 hover:bg-green-500/20 border border-green-500/30 rounded flex items-center justify-center gap-3 text-green-500 font-black text-xs uppercase tracking-widest transition-all"
                         >
                            <FileSignature className="w-4 h-4" /> Notarize Template
                         </button>
                         {isVoting && <p className="text-[9px] text-blue-400 text-center mt-4 animate-pulse uppercase font-black tracking-widest">Broadcasting Judicial Acknowledgment...</p>}
                      </div>
                   </div>
                </div>
             </div>
          )}

          {selectedCase && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <button onClick={() => setSelectedCase(null)} className="text-xs text-gray-500 hover:text-white mb-4 flex items-center gap-2 font-bold uppercase tracking-widest"><ArrowRight className="w-3 h-3 rotate-180" /> Back to Docket</button>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 text-xs leading-relaxed italic text-gray-400">"{selectedCase.evidence.instructions}"</div>
                <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-black text-white mb-6 tracking-widest">Cast Verified Verdict</h3>
                  <div className="space-y-3">
                    <button onClick={() => handleVote('VALID')} disabled={isVoting} className="w-full py-4 bg-green-500/10 border border-green-500/20 rounded text-green-500 font-black text-xs uppercase tracking-widest">Valid Work</button>
                    <button onClick={() => handleVote('FRAUD')} disabled={isVoting} className="w-full py-4 bg-red-500/10 border border-red-500/20 rounded text-red-500 font-black text-xs uppercase tracking-widest">Fraudulent Proof</button>
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
