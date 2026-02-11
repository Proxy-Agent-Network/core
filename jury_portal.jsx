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
  ShieldQuestion
} from 'lucide-react';

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [isVoting, setIsVoting] = useState(false);
  
  // v2.2 Hardware States
  const [isRotating, setIsRotating] = useState(false);
  const [keyRotationStep, setKeyRotationStep] = useState(0); // 0: Idle, 1: Wiping, 2: Generating, 3: Verifying
  const [nodeId, setNodeId] = useState("NODE_ELITE_X29");

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
      { id: "NODE_ALPHA_001", score: "9b1e...", status: "ACTIVE" },
      { id: "NODE_GAMMA_442", score: "a3f0...", status: "ACTIVE" },
      { id: "NODE_BETA_991", score: "b2d1...", status: "ACTIVE" },
      { id: "NODE_OMEGA_772", score: "c5e9...", status: "ACTIVE" },
      { id: "NODE_ZETA_083", score: "d4a2...", status: "ACTIVE" },
      { id: "NODE_SIGMA_115", score: "e9f2...", status: "ACTIVE" }
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
    }, 1200);
  };

  /**
   * Simulation of the hardware-bound Key Rotation Ceremony (v2.2)
   */
  const startKeyRotation = () => {
    setIsRotating(true);
    setKeyRotationStep(1);
    
    // Step 1: Wipe Old Handle
    setTimeout(() => {
      setKeyRotationStep(2);
      // Step 2: Generate Primary Seed in TPM
      setTimeout(() => {
        setKeyRotationStep(3);
        // Step 3: Verify and Re-bind Reputation
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
            <h1 className="text-sm font-bold tracking-tighter text-white uppercase">Jury Tribunal v2.2</h1>
            <p className="text-[10px] text-amber-500/70 uppercase tracking-widest">Identity Rotation Integrated</p>
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
            <span className="text-gray-500 uppercase font-bold tracking-tighter">Your Bond</span>
            <span className="text-white">{(stats.staked_bond / 1000000).toFixed(1)}M SATS</span>
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
              onClick={() => { setActiveTab('cases'); setSelectedCase(null); setSelectedClaim(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'cases' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Activity className="w-4 h-4" /> Open Disputes
            </button>
            <button 
              onClick={() => { setActiveTab('appellate'); setSelectedCase(null); setSelectedClaim(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'appellate' ? 'bg-red-500/10 text-red-500 border border-red-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Shield className="w-4 h-4" /> Appellate Court
            </button>
            <button 
              onClick={() => { setActiveTab('history'); setSelectedCase(null); setSelectedClaim(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'history' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Scale className="w-4 h-4" /> Recent Verdicts
            </button>
            <button 
              onClick={() => { setActiveTab('stats'); setSelectedCase(null); setSelectedClaim(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'stats' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <TrendingUp className="w-4 h-4" /> Personal Standing
            </button>
            <button 
              onClick={() => { setActiveTab('security'); setSelectedCase(null); setSelectedClaim(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'security' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Cpu className="w-4 h-4" /> Hardware Security
            </button>
            <button 
              onClick={() => { setActiveTab('insurance'); setSelectedCase(null); setSelectedClaim(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'insurance' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <HeartPulse className="w-4 h-4" /> Insurance Claims
            </button>
          </nav>

          <div className="p-4 bg-blue-500/5 border border-blue-500/10 rounded-lg">
            <p className="text-[10px] text-blue-400/60 font-bold leading-relaxed uppercase tracking-tighter italic">
              "Silently verify hardware PCRs every epoch to ensure zero-day protection remains active."
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

          {/* 2. HARDWARE SECURITY VIEW (v2.2 FEATURE) */}
          {activeTab === 'security' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  {/* Key Management Card */}
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8">
                     <div className="flex items-center justify-between mb-8">
                        <h3 className="text-xs uppercase font-black tracking-widest text-white flex items-center gap-3">
                           <Key className="w-5 h-5 text-blue-400" /> TPM 2.0 Identity Management
                        </h3>
                        <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded ${isRotating ? 'bg-yellow-500/10 text-yellow-500 animate-pulse' : 'bg-green-500/10 text-green-500'}`}>
                           {isRotating ? 'ROTATING' : 'LOCKED'}
                        </span>
                     </div>

                     <div className="space-y-6">
                        <div>
                           <label className="text-[10px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Active Identity Hash</label>
                           <div className="bg-black/60 p-4 border border-white/5 rounded mono text-xs text-blue-300 break-all select-all">
                              {nodeId === "NODE_ELITE_X29" ? "0x81010001:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd" : "0x81010002:fresh_" + nodeId}
                           </div>
                        </div>

                        <div className="bg-blue-500/5 border border-blue-500/10 p-4 rounded text-[10px] text-blue-300 leading-relaxed italic">
                           "Identity keys are sealed within the OPTIGA™ TPM 2.0. Rotating your key will invalidate all pending signatures but maintain your reputation bridge."
                        </div>

                        <button 
                           disabled={isRotating}
                           onClick={startKeyRotation}
                           className="w-full py-4 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 rounded-lg flex items-center justify-center gap-3 transition-all group"
                        >
                           <RefreshCw className={`w-4 h-4 text-blue-400 ${isRotating ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
                           <span className="text-xs font-black uppercase text-blue-400 tracking-widest">
                              Rotate Hardware Identity
                           </span>
                        </button>
                     </div>
                  </div>

                  {/* Ceremony Console */}
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg flex flex-col">
                     <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center">
                        <h3 className="text-xs uppercase font-black tracking-widest flex items-center gap-2">
                           <Fingerprint className="w-4 h-4 text-gray-500" /> Binding Console
                        </h3>
                     </div>
                     <div className="flex-1 p-6 font-mono text-[10px] leading-relaxed overflow-y-auto bg-black/40">
                        <p className="text-gray-600">[*] System initialized at T-0ms</p>
                        <p className="text-gray-600">[*] Kernel: Linux 6.6.1-proxy-node</p>
                        <p className="text-green-500">[*] Hardware Root: OPTIGA TPM 2.0 Detected</p>
                        
                        {keyRotationStep >= 1 && (
                           <div className="mt-4 animate-in fade-in slide-in-from-left duration-300">
                              <p className="text-red-500 font-bold">[!] REQUESTING ROTATION...</p>
                              <p className="text-white">[*] Command: tpm2_clear --hierarchy platform</p>
                              <p className="text-yellow-500">[*] Wiping handle 0x81010001... SUCCESS</p>
                           </div>
                        )}
                        
                        {keyRotationStep >= 2 && (
                           <div className="mt-4 animate-in fade-in slide-in-from-left duration-300">
                              <p className="text-white">[*] Command: tpm2_createprimary -C e -G ecc</p>
                              <p className="text-green-500">[*] Primary Seed Generated (Silicon Entropy)</p>
                              <p className="text-white">[*] Creating AK Handle at 0x81010002...</p>
                              <p className="text-green-500">[*] Object Persistence Locked.</p>
                           </div>
                        )}

                        {keyRotationStep >= 3 && (
                           <div className="mt-4 animate-in fade-in slide-in-from-left duration-300">
                              <p className="text-white">[*] Synchronizing Reputation Bridge...</p>
                              <p className="text-green-500">[*] PGP Revocation Certificate Published.</p>
                              <p className="text-green-500">[*] New Attestation Key Public Key Exported.</p>
                              <p className="text-white font-black mt-2">✅ BINDING CEREMONY COMPLETE.</p>
                           </div>
                        )}
                        
                        {isRotating && (
                           <div className="mt-4 animate-pulse flex items-center gap-2 text-blue-400">
                              <div className="w-1 h-3 bg-blue-400"></div>
                              <p>PROCESSING HARDWARE REQUEST...</p>
                           </div>
                        )}
                     </div>
                  </div>
               </div>

               {/* Forensics Section */}
               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-6">
                     <h3 className="text-xs uppercase font-black tracking-widest text-gray-400 flex items-center gap-2">
                        <ShieldQuestion className="w-4 h-4" /> Integrity Forensics
                     </h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                     <div className="bg-black/40 p-4 border border-white/5 rounded">
                        <span className="text-[9px] text-gray-600 uppercase block mb-1">Chassis Intrusion</span>
                        <span className="text-xs font-bold text-green-500">CIRCUIT CLOSED</span>
                     </div>
                     <div className="bg-black/40 p-4 border border-white/5 rounded">
                        <span className="text-[9px] text-gray-600 uppercase block mb-1">PCR Banks</span>
                        <span className="text-xs font-bold text-white uppercase">UNMODIFIED (GOLDEN)</span>
                     </div>
                     <div className="bg-black/40 p-4 border border-white/5 rounded">
                        <span className="text-[9px] text-gray-600 uppercase block mb-1">Node Temperature</span>
                        <span className="text-xs font-bold text-amber-500 uppercase tracking-tighter">44°C STABLE</span>
                     </div>
                  </div>
               </div>
            </div>
          )}

          {/* 3. APPELLATE COURT VIEW (v2.1) */}
          {activeTab === 'appellate' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
              <div className="bg-red-500/10 border border-red-500/40 rounded-lg p-8 flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="flex items-center gap-6">
                   <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center border border-red-500/30 text-red-500">
                      <ShieldAlert className="w-8 h-8 animate-pulse" />
                   </div>
                   <div>
                      <h2 className="text-xl font-black text-red-500 uppercase tracking-tighter">SEV-1 Convocation Active</h2>
                      <p className="text-sm text-gray-400 mt-1 max-w-md">Systemic jury collusion detected. High Court convened to restore Schelling Point integrity.</p>
                   </div>
                </div>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1 bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                   <h3 className="text-xs uppercase font-bold mb-6 flex items-center gap-2 text-white">
                     <Cpu className="w-4 h-4 text-red-500" /> VRF Selection Proof
                   </h3>
                   <div className="space-y-4 text-[10px]">
                      <div className="bg-black/40 p-2 rounded mono text-red-400 truncate">{appellateContext.incident_id}</div>
                      <div className="bg-black/40 p-2 rounded mono text-gray-400 break-all">{appellateContext.btc_block_hash}</div>
                   </div>
                </div>
                <div className="lg:col-span-2">
                   <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden h-full">
                      <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center">
                         <h3 className="text-xs uppercase font-bold tracking-widest flex items-center gap-2">
                           <Fingerprint className="w-4 h-4 text-red-500" /> Verified High Court Roster
                         </h3>
                      </div>
                      <div className="divide-y divide-white/5">
                         {appellateContext.roster.map((juror) => (
                           <div key={juror.id} className={`p-4 flex items-center justify-between ${juror.status === 'YOU' ? 'bg-red-500/5' : ''}`}>
                              <span className={`text-xs font-bold ${juror.status === 'YOU' ? 'text-white' : 'text-gray-400'}`}>{juror.id}</span>
                              <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded ${juror.status === 'YOU' ? 'bg-red-500 text-black' : 'text-green-500 border border-green-500/20'}`}>
                                 {juror.status}
                              </span>
                           </div>
                         ))}
                      </div>
                   </div>
                </div>
              </div>
            </div>
          )}

          {/* 4. RECENT VERDICTS FEED */}
          {activeTab === 'history' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-black/40 border border-white/5 p-4 rounded-lg">
                  <span className="text-[9px] text-gray-600 uppercase block mb-1 font-bold">Total Adjudications</span>
                  <p className="text-xl font-bold text-white">4,821</p>
                </div>
                <div className="bg-black/40 border border-white/5 p-4 rounded-lg text-green-500">
                  <span className="text-[9px] text-gray-600 uppercase block mb-1 font-bold">Outcome Skew</span>
                  <p className="text-xl font-bold">82% Valid</p>
                </div>
                <div className="bg-black/40 border border-white/5 p-4 rounded-lg text-amber-500">
                  <span className="text-[9px] text-gray-600 uppercase block mb-1 font-bold">Slashing Yield</span>
                  <p className="text-xl font-bold">12.4M Sats</p>
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
                    <div key={v.id} className="p-6">
                      <div className="flex justify-between items-start">
                        <span className="text-sm font-bold text-white">{v.id}</span>
                        <div className={`px-3 py-1 rounded text-[10px] font-black uppercase tracking-widest ${v.outcome === 'VALID' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                          {v.outcome}
                        </div>
                      </div>
                      <p className="text-xs text-gray-400 mt-2">{v.summary}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 5. PERSONAL STATS DASHBOARD */}
          {activeTab === 'stats' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="flex flex-col md:flex-row gap-4">
                 <div className="flex-1 bg-purple-500/5 border border-purple-500/20 p-5 rounded-lg">
                    <span className="text-[9px] text-purple-400 uppercase font-black block mb-2 tracking-widest">Growth Factor</span>
                    <p className="text-2xl font-black text-white">+42 <span className="text-xs text-gray-500 font-normal">REP / Mo</span></p>
                 </div>
                 <div className="flex-1 bg-green-500/5 border border-green-500/20 p-5 rounded-lg relative group overflow-hidden">
                    <span className="text-[9px] text-green-400 uppercase font-black block mb-2 tracking-widest">Lifetime Sats</span>
                    <p className="text-2xl font-black text-white">{stats.earned_fees.toLocaleString()}</p>
                    <button onClick={handleTaxExport} className="absolute top-4 right-4 p-2 bg-green-500/10 hover:bg-green-500/20 rounded border border-green-500/30 transition-all text-green-500"><Download className="w-4 h-4" /></button>
                 </div>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-bold mb-6 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-purple-400" /> Reputation Momentum
                  </h3>
                  <div className="flex items-end gap-2 h-40">
                    {performanceHistory.reputation_trend.map((val, i) => (
                      <div key={i} className="flex-1 bg-purple-500/20 border-t-2 border-purple-500/50 rounded-t-sm" style={{ height: `${(val / 1000) * 100}%` }}></div>
                    ))}
                  </div>
                </div>
                <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-bold mb-6 flex items-center gap-2">
                    <Scale className="w-4 h-4 text-green-400" /> Adjudication Accuracy
                  </h3>
                  <div className="space-y-4 text-[10px]">
                    {performanceHistory.task_breakdown.map((task) => (
                      <div key={task.type}>
                        <div className="flex justify-between mb-1.5 uppercase font-bold"><span>{task.type} Protocols</span><span className="text-white">{task.accuracy}%</span></div>
                        <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden"><div className={`h-full ${task.accuracy >= 98 ? 'bg-green-500' : 'bg-amber-500'}`} style={{ width: `${task.accuracy}%` }} /></div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 6. INSURANCE CLAIMS VIEW */}
          {activeTab === 'insurance' && !selectedClaim && (
            <div className="bg-[#0d0d0e] border border-cyan-500/20 rounded-lg overflow-hidden animate-in fade-in duration-300">
               <div className="p-4 border-b border-cyan-500/20 flex justify-between items-center bg-cyan-500/[0.02]">
                <h2 className="text-xs uppercase font-bold tracking-widest flex items-center gap-2 text-cyan-400">
                  <HeartPulse className="w-4 h-4" /> Automated Insurance Claims
                </h2>
              </div>
              <div className="divide-y divide-white/5">
                {claims.map((claim) => (
                  <div key={claim.id} className="p-6 flex items-center justify-between group">
                    <div className="flex items-center gap-6">
                      <div className="w-12 h-12 bg-cyan-500/10 rounded flex flex-col items-center justify-center border border-cyan-500/20 text-cyan-400">
                        <AlertTriangle className="w-5 h-5" />
                        <span className="text-[8px] font-black mt-1">{claim.severity}</span>
                      </div>
                      <div>
                        <span className="text-white font-bold text-sm block">{claim.id}</span>
                        <p className="text-xs text-gray-500 uppercase">Settlement Failure: {claim.node_id}</p>
                      </div>
                    </div>
                    <button onClick={() => setSelectedClaim(claim)} className="bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 px-4 py-2 rounded text-xs transition-all text-cyan-400 font-bold">
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
              <button onClick={() => setSelectedCase(null)} className="text-xs text-gray-500 hover:text-white mb-4 flex items-center gap-2 font-bold"><ArrowRight className="w-3 h-3 rotate-180" /> Back to Docket</button>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 text-xs leading-relaxed italic text-gray-400">"{selectedCase.evidence.instructions}"</div>
                <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <button onClick={() => handleVote('VALID')} disabled={isVoting} className="w-full py-4 mb-3 bg-green-500/10 hover:bg-green-500/20 border border-green-500/20 rounded text-green-500 font-black text-xs uppercase tracking-widest">Valid Work</button>
                  <button onClick={() => handleVote('FRAUD')} disabled={isVoting} className="w-full py-4 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 rounded text-red-500 font-black text-xs uppercase tracking-widest">Fraudulent Proof</button>
                </div>
              </div>
            </div>
          )}

          {selectedClaim && (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <button onClick={() => setSelectedClaim(null)} className="text-xs text-gray-500 hover:text-white mb-4 flex items-center gap-2 font-bold"><ArrowRight className="w-3 h-3 rotate-180" /> Back to Claims</button>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0d0d0e] border border-cyan-500/20 rounded-lg p-6 mono text-[10px] text-red-400/80 leading-relaxed">{selectedClaim.proof_log}</div>
                <div className="bg-[#0d0d0e] border border-cyan-500/20 rounded-lg p-6">
                  <button onClick={() => handleVote('APPROVE')} disabled={isVoting} className="w-full py-5 bg-cyan-500/10 border border-cyan-500/30 rounded flex items-center justify-center gap-3 text-cyan-400 font-black text-xs uppercase tracking-widest"><CheckCircle2 className="w-4 h-4" /> Authorize Keysend</button>
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
