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
  Stamp
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
    },
    {
      id: "POA-SG-ETA-V1",
      jurisdiction: "SG",
      title: "Singapore Electronic PoA",
      legislation: "Electronic Transactions Act 2010",
      last_audit: "2025-12-20",
      status: "VERIFIED",
      body: "# LIMITED POWER OF ATTORNEY (SINGAPORE JURISDICTION)\n\nPursuant to the Powers of Attorney Act (Cap. 243), the Principal grants the Attorney the limited power to perform specific physical and legal acts..."
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
            <h1 className="text-sm font-bold tracking-tighter text-white uppercase">Jury Tribunal v2.6</h1>
            <p className="text-[10px] text-amber-500/70 uppercase tracking-widest">Legal Instrument Notarization</p>
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
              onClick={() => { setActiveTab('notary'); setSelectedCase(null); setSelectedClaim(null); setSelectedTemplate(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'notary' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Stamp className="w-4 h-4" /> Notary Templates
            </button>
            <button 
              onClick={() => { setActiveTab('treasury'); setSelectedCase(null); setSelectedClaim(null); setSelectedTemplate(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'treasury' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
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

          <div className="p-4 bg-blue-500/5 border border-blue-500/10 rounded-lg">
            <p className="text-[10px] text-blue-400/60 font-bold leading-relaxed uppercase tracking-tighter italic">
              "Legal instrument notarization ensures all Power of Attorney templates comply with local statutes before being served to Agents."
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

          {/* 2. NOTARY TEMPLATES VIEW (v2.6 FEATURE) */}
          {activeTab === 'notary' && !selectedTemplate && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
                <div className="bg-[#0d0d0e] border border-blue-500/20 rounded-lg overflow-hidden">
                   <div className="p-4 border-b border-blue-500/20 bg-blue-500/[0.02] flex justify-between items-center">
                      <h2 className="text-xs uppercase font-black tracking-[0.2em] text-blue-400 flex items-center gap-2">
                        <Stamp className="w-4 h-4" /> Global Legal Registry
                      </h2>
                      <span className="text-[9px] text-gray-500 uppercase font-bold">Standardized POA Formats</span>
                   </div>
                   <div className="grid grid-cols-1 md:grid-cols-3 gap-1 p-1 bg-white/5">
                      {notaryTemplates.map((template) => (
                         <div key={template.id} className="bg-[#0d0d0e] p-6 hover:bg-white/[0.01] transition-all flex flex-col justify-between group">
                            <div>
                               <div className="flex justify-between items-start mb-4">
                                  <div className="w-10 h-10 bg-blue-500/10 rounded flex items-center justify-center border border-blue-500/20 text-blue-400">
                                     <FileText className="w-5 h-5" />
                                  </div>
                                  <span className={`text-[8px] font-black uppercase px-2 py-1 rounded ${template.status === 'VERIFIED' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500 animate-pulse'}`}>
                                     {template.status.replace('_', ' ')}
                                  </span>
                               </div>
                               <h3 className="text-sm font-black text-white uppercase mb-1 tracking-tight">{template.title}</h3>
                               <p className="text-[10px] text-gray-500 mb-4">{template.id}</p>
                               <div className="space-y-2 mb-6">
                                  <div className="flex items-center gap-2 text-[9px] text-gray-400">
                                     <Shield className="w-3 h-3 text-blue-400/60" />
                                     <span>{template.legislation}</span>
                                  </div>
                                  <div className="flex items-center gap-2 text-[9px] text-gray-400">
                                     <Clock className="w-3 h-3 text-gray-600" />
                                     <span>Last Audit: {template.last_audit}</span>
                                  </div>
                               </div>
                            </div>
                            <button 
                               onClick={() => setSelectedTemplate(template)}
                               className="w-full py-2 bg-white/5 border border-white/10 text-gray-400 text-[10px] font-black uppercase rounded group-hover:bg-blue-500/10 group-hover:border-blue-500/30 group-hover:text-blue-400 transition-all"
                            >
                               Audit Instrument
                            </button>
                         </div>
                      ))}
                   </div>
                </div>

                {/* Statutory Warning */}
                <div className="p-6 bg-blue-500/5 border border-blue-500/10 rounded-lg flex items-start gap-4">
                   <AlertTriangle className="w-5 h-5 text-blue-400 flex-shrink-0" />
                   <p className="text-xs text-blue-300/60 leading-relaxed italic">
                      "High Court Judges are responsible for ensuring that the legal bridge remains un-compromised. Modifying template logic without a formal PIP (Proxy Improvement Proposal) constitutes judicial misconduct."
                   </p>
                </div>
             </div>
          )}

          {/* 3. TREASURY AUDIT VIEW (v2.5) */}
          {activeTab === 'treasury' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-green-500/5 border border-green-500/20 p-5 rounded-lg">
                    <span className="text-[9px] text-green-400 uppercase font-black block mb-2 tracking-widest">Net Reserves</span>
                    <p className="text-2xl font-black text-white">{(treasuryStats.net_reserves / 1000000).toFixed(1)}M <span className="text-xs text-gray-500 font-normal">SATS</span></p>
                  </div>
                  <div className="bg-blue-500/5 border border-blue-500/20 p-5 rounded-lg">
                    <span className="text-[9px] text-blue-400 uppercase font-black block mb-2 tracking-widest">Insurance Depth</span>
                    <p className="text-2xl font-black text-white">{(stats.insurance_pool_depth / 1000000).toFixed(1)}M <span className="text-xs text-gray-500 font-normal">SATS</span></p>
                  </div>
                  <div className="bg-amber-500/5 border border-amber-500/20 p-5 rounded-lg">
                    <span className="text-[9px] text-amber-400 uppercase font-black block mb-2 tracking-widest">Slash Revenue</span>
                    <p className="text-2xl font-black text-white">{(treasuryStats.slashing_revenue / 1000000).toFixed(1)}M</p>
                  </div>
                  <div className="bg-red-500/5 border border-red-500/20 p-5 rounded-lg">
                    <span className="text-[9px] text-red-400 uppercase font-black block mb-2 tracking-widest">Total Outflow</span>
                    <p className="text-2xl font-black text-white">{(treasuryStats.total_outflow / 1000000).toFixed(1)}M</p>
                  </div>
               </div>
               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden">
                  <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center"><h3 className="text-xs uppercase font-bold tracking-widest flex items-center gap-2"><History className="w-4 h-4 text-green-500" /> Recent Protocol Transactions</h3></div>
                  <div className="divide-y divide-white/5">
                    {transactions.map((tx) => (
                      <div key={tx.id} className="p-5 flex items-center justify-between hover:bg-white/[0.01]">
                        <div className="flex items-center gap-4">
                          <div className={`p-2 rounded bg-white/5 border border-white/10 ${tx.type === 'PAYOUT' ? 'text-red-400' : 'text-green-400'}`}>{tx.type === 'PAYOUT' ? <ArrowDownRight className="w-4 h-4" /> : <ArrowUpRight className="w-4 h-4" />}</div>
                          <div><span className="text-sm font-bold text-white block mb-0.5">{tx.id} <span className="text-[8px] bg-white/5 px-1.5 py-0.5 rounded text-gray-500 uppercase">{tx.type}</span></span><p className="text-[9px] text-gray-600">{tx.node} • {tx.timestamp}</p></div>
                        </div>
                        <p className={`text-sm font-black ${tx.type === 'PAYOUT' ? 'text-red-400' : 'text-green-500'}`}>{tx.type === 'PAYOUT' ? '-' : '+'}{tx.amount.toLocaleString()} SATS</p>
                      </div>
                    ))}
                  </div>
               </div>
            </div>
          )}

          {/* 4. BROWNOUT CONTROL VIEW (v2.4) */}
          {activeTab === 'brownout' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                     <span className="text-[10px] text-gray-600 uppercase font-black block mb-4">Mempool Depth</span>
                     <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black text-white">{mempoolDepth.toLocaleString()}</span>
                        <span className="text-xs text-gray-500 uppercase tracking-widest">Tasks</span>
                     </div>
                  </div>
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                     <span className="text-[10px] text-gray-600 uppercase font-black block mb-4">Congestion Level</span>
                     <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full animate-pulse ${
                          brownoutLevel === 'GREEN' ? 'bg-green-500' : 
                          brownoutLevel === 'YELLOW' ? 'bg-yellow-500' : 
                          brownoutLevel === 'ORANGE' ? 'bg-orange-500' : 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.3)]'
                        }`} />
                        <span className="text-2xl font-black text-white uppercase">{brownoutLevel}</span>
                     </div>
                  </div>
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between">
                     <span className="text-[10px] text-gray-600 uppercase font-black block mb-2">Manual Override</span>
                     <button onClick={() => setIsManualOverride(!isManualOverride)} className={`w-full py-2 rounded text-[10px] font-black uppercase tracking-widest ${isManualOverride ? 'bg-orange-500 text-black' : 'bg-white/5 border border-white/10 text-gray-400'}`}>{isManualOverride ? 'ENABLED' : 'DISABLED'}</button>
                  </div>
               </div>

               <div className="bg-[#0d0d0e] border border-orange-500/20 rounded-lg overflow-hidden">
                  <div className="p-4 border-b border-orange-500/20 bg-orange-500/[0.02] flex justify-between items-center"><h3 className="text-xs uppercase font-black tracking-widest text-orange-400 flex items-center gap-2"><ShieldAlert className="w-4 h-4" /> Traffic Shedding Parameters</h3></div>
                  <div className="p-8">
                     <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        {['GREEN', 'YELLOW', 'ORANGE', 'RED'].map((level) => (
                           <button 
                              key={level} 
                              disabled={!isManualOverride} 
                              onClick={() => setBrownoutLevel(level)} 
                              className={`p-6 border rounded-lg transition-all flex flex-col items-center text-center ${brownoutLevel === level ? 'bg-white/5 border-orange-500' : 'bg-black/40 border-white/5 opacity-40'} ${!isManualOverride && 'cursor-not-allowed opacity-20'}`}
                           >
                              <span className={`text-[9px] font-black uppercase mb-3 ${level === 'GREEN' ? 'text-green-500' : level === 'YELLOW' ? 'text-yellow-500' : level === 'ORANGE' ? 'text-orange-500' : 'text-red-500'}`}>{level}</span>
                              <p className="text-[10px] text-gray-400 leading-tight">
                                {level === 'GREEN' ? 'Normal Operations ( > 300 REP)' : 
                                 level === 'YELLOW' ? 'Shed Probationary ( > 500 REP)' : 
                                 level === 'ORANGE' ? 'Shed Non-Elite ( > 700 REP)' : 
                                 'Whale Only ( > 900 REP)'}
                              </p>
                           </button>
                        ))}
                     </div>
                  </div>
               </div>

               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-black text-gray-500 tracking-widest mb-6">Congestion Audit Log</h3>
                  <div className="space-y-3 font-mono text-[9px]">
                     <div className="flex justify-between text-gray-600"><span>[10:42:12] AUTO_SCALING: PROMOTED TO ORANGE (MEMPOOL {'>'} 5000)</span><span className="text-green-500 uppercase font-black">Verified</span></div>
                     <div className="flex justify-between text-gray-600"><span>[10:45:00] SHEDDING_EXEC: DROPPED 422 TASKS FROM {'<'} 500 REP NODES</span><span className="text-green-500 uppercase font-black">Verified</span></div>
                  </div>
               </div>
            </div>
          )}

          {/* 5. SYBIL DEFENSE VIEW (v2.3) */}
          {activeTab === 'sybil' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-1">
                  <div className="bg-black/60 rounded-lg h-64 flex flex-col items-center justify-center relative overflow-hidden">
                     <Globe className="w-12 h-12 text-red-500/40 mb-4" />
                     <h3 className="text-xs uppercase font-black text-gray-500 tracking-[0.4em]">Global Node Entropy Map</h3>
                  </div>
               </div>
               <div className="bg-[#0d0d0e] border border-red-500/20 rounded-lg overflow-hidden">
                  <div className="p-4 border-b border-red-500/20 bg-red-500/[0.02] flex justify-between items-center"><h3 className="text-xs uppercase font-black tracking-widest text-red-400 flex items-center gap-2"><ZapOff className="w-4 h-4" /> Suspicious Node Clusters</h3></div>
                  <div className="divide-y divide-white/5">
                     {sybilClusters.map((cluster) => (
                        <div key={cluster.id} className="p-6 flex flex-col md:flex-row justify-between gap-6 hover:bg-white/[0.01] transition-colors">
                           <div className="flex gap-6">
                              <div className="w-14 h-14 bg-red-500/10 rounded border border-red-500/30 flex flex-col items-center justify-center"><span className="text-[8px] text-red-500 uppercase font-black">Risk</span><span className="text-lg font-black text-white leading-none">{cluster.risk_score}</span></div>
                              <div className="space-y-1"><span className="text-sm font-bold text-white uppercase block">{cluster.id}</span><p className="text-xs text-gray-500 max-w-md">{cluster.logic}</p></div>
                           </div>
                           <button className="px-4 py-2 bg-red-500/10 border border-red-500 text-red-500 text-[10px] font-black uppercase tracking-widest hover:bg-red-500 hover:text-black transition-all">Mass Slash</button>
                        </div>
                     ))}
                  </div>
               </div>
            </div>
          )}

          {/* DETAIL VIEWS (CASE / CLAIM / TEMPLATE) */}
          
          {/* v2.6 TEMPLATE AUDIT VIEW */}
          {selectedTemplate && (
             <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                <button onClick={() => setSelectedTemplate(null)} className="text-xs text-gray-500 hover:text-white mb-4 flex items-center gap-2 font-bold uppercase tracking-widest">
                   <ArrowRight className="w-3 h-3 rotate-180" /> Back to Registry
                </button>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                   <div className="bg-[#0d0d0e] border border-blue-500/20 rounded-lg flex flex-col h-[500px]">
                      <div className="p-4 border-b border-blue-500/20 bg-blue-500/[0.02] flex justify-between items-center">
                         <span className="text-[10px] text-blue-400 font-black uppercase">Instrument Preview (Markdown)</span>
                         <span className="text-[9px] text-gray-600 mono">{selectedTemplate.jurisdiction}</span>
                      </div>
                      <div className="flex-1 p-8 overflow-y-auto bg-black/40 font-mono text-xs leading-relaxed text-gray-400 whitespace-pre-wrap">
                         {selectedTemplate.body}
                      </div>
                   </div>

                   <div className="space-y-6">
                      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                         <h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3">
                            <ShieldCheck className="w-5 h-5 text-green-500" /> Compliance Sign-off
                         </h3>
                         <div className="space-y-4 mb-8">
                            <p className="text-xs text-gray-500 leading-relaxed">
                               Review the instrument body against the cited legislation: <span className="text-blue-400 underline">{selectedTemplate.legislation}</span>. 
                               Affixing your signature confirms that this template is a valid delegation of authority under local law.
                            </p>
                            <div className="p-4 bg-white/5 rounded border border-white/10">
                               <div className="flex justify-between items-center text-[10px] mb-2 uppercase font-black">
                                  <span className="text-gray-600">Juror Standing</span>
                                  <span className="text-green-500">Super-Elite</span>
                               </div>
                               <div className="flex justify-between items-center text-[10px] uppercase font-black">
                                  <span className="text-gray-600">Signing Power</span>
                                  <span className="text-white">Active</span>
                               </div>
                            </div>
                         </div>
                         
                         <div className="space-y-3">
                            <button 
                               onClick={() => handleVote('SIGN')}
                               disabled={isVoting}
                               className="w-full py-4 bg-green-500/10 hover:bg-green-500/20 border border-green-500/30 rounded flex items-center justify-center gap-3 text-green-500 font-black text-xs uppercase tracking-widest transition-all"
                            >
                               <FileSignature className="w-4 h-4" /> Notarize Template
                            </button>
                            <button 
                               onClick={() => handleVote('REJECT')}
                               disabled={isVoting}
                               className="w-full py-2 text-gray-600 hover:text-red-500 text-[9px] uppercase font-bold transition-all"
                            >
                               Flag for Re-drafting
                            </button>
                         </div>
                         {isVoting && <p className="text-[9px] text-blue-400 text-center mt-4 animate-pulse uppercase font-black">Broadcasting Judicial Acknowledgment...</p>}
                      </div>

                      {/* Version Control History */}
                      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col">
                         <span className="text-[9px] text-gray-600 uppercase font-black mb-4 tracking-widest">Audit Trail</span>
                         <div className="space-y-3">
                            <div className="flex justify-between items-center text-[9px] mono">
                               <span className="text-green-500">v1.1 APPROVED</span>
                               <span className="text-gray-700">2026-01-15</span>
                            </div>
                            <div className="flex justify-between items-center text-[9px] mono">
                               <span className="text-yellow-500">v1.2 PROPOSED</span>
                               <span className="text-gray-700">2026-02-11</span>
                            </div>
                         </div>
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
                  <button onClick={() => handleVote('VALID')} disabled={isVoting} className="w-full py-4 mb-3 bg-green-500/10 border border-green-500/20 rounded text-green-500 font-black text-xs uppercase tracking-widest">Valid Work</button>
                  <button onClick={() => handleVote('FRAUD')} disabled={isVoting} className="w-full py-4 bg-red-500/10 border border-red-500/20 rounded text-red-500 font-black text-xs uppercase tracking-widest">Fraudulent Proof</button>
                </div>
              </div>
            </div>
          )}

          {selectedClaim && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <button onClick={() => setSelectedClaim(null)} className="text-xs text-gray-500 hover:text-white mb-4 flex items-center gap-2 font-bold uppercase tracking-widest"><ArrowRight className="w-3 h-3 rotate-180" /> Back to Claims</button>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0d0d0e] border border-cyan-500/20 rounded-lg p-6 mono text-[10px] text-red-400/80 leading-relaxed">{selectedClaim.proof_log}</div>
                <button onClick={() => handleVote('APPROVE')} disabled={isVoting} className="w-full py-5 bg-cyan-500/10 border border-cyan-500/30 rounded text-cyan-400 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2"><CheckCircle2 className="w-4 h-4" /> Authorize Keysend</button>
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
