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
  AlertOctagon,
  Wifi,
  Binary,
  ShieldEllipsis
} from 'lucide-react';

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [isVoting, setIsVoting] = useState(false);
  
  // Hardware States
  const [isRotating, setIsRotating] = useState(false);
  const [keyRotationStep, setKeyRotationStep] = useState(0); 
  const [nodeId, setNodeId] = useState("NODE_ELITE_X29");

  // Stake Management State
  const [withdrawalState, setWithdrawalState] = useState('IDLE'); 
  const [cooldownDaysRemaining, setCooldownDaysRemaining] = useState(14);
  const [isProcessingStake, setIsProcessingStake] = useState(false);

  // Brownout State
  const [brownoutLevel, setBrownoutLevel] = useState('GREEN'); 
  const [mempoolDepth, setMempoolDepth] = useState(6402);
  const [isManualOverride, setIsManualOverride] = useState(false);

  // Treasury Audit State (v2.9 Update)
  const [treasuryStats] = useState({
    total_inflow: 84290100,
    total_outflow: 12500000,
    slashing_revenue: 34000000,
    tax_revenue: 50290100,
    net_reserves: 71790100,
    locked_insurance_pool: 10450200
  });

  const [ledger] = useState([
    { id: "TX-99812", type: "SLASH", amount: 250000, timestamp: "2026-02-11 11:02:00", node: "NODE_MALICIOUS_X8", status: "CONFIRMED" },
    { id: "TX-99811", type: "TAX", amount: 4200, timestamp: "2026-02-11 10:58:12", node: "NODE_ELITE_X29", status: "CONFIRMED" },
    { id: "TX-99810", type: "PAYOUT", amount: 10000, timestamp: "2026-02-11 10:45:00", node: "CLAIM-X01", status: "SETTLED" },
    { id: "TX-99809", type: "SLASH", amount: 1200000, timestamp: "2026-02-11 09:12:44", node: "SYBIL_CLUSTER_A", status: "CONFIRMED" }
  ]);

  // Network Context
  const [stats] = useState({
    reputation: 982,
    staked_bond: 2000000,
    earned_fees: 45200,
    successful_verdicts: 124,
    accuracy_rate: "98.2%",
    tier: "SUPER-ELITE"
  });

  // Action Handlers
  const handleVote = (verdict) => {
    setIsVoting(true);
    setTimeout(() => {
      setIsVoting(false);
      setSelectedCase(null);
      setSelectedClaim(null);
      setSelectedTemplate(null);
    }, 1200);
  };

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
    link.setAttribute("download", `PROXY_TAX_REPORT_2026.csv`);
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
            <h1 className="text-sm font-bold tracking-tighter text-white uppercase tracking-widest">Jury Tribunal v2.9</h1>
            <p className="text-[10px] text-amber-500/70 uppercase tracking-widest">Treasury Integrity Engine</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6 text-[11px]">
          <div className="flex flex-col items-end">
            <span className="text-gray-500 uppercase font-bold tracking-tighter">Status</span>
            <span className="text-green-500 flex items-center gap-1 font-bold">
              <ShieldCheck className="w-3 h-3" /> HIGH COURT ACTIVE
            </span>
          </div>
          <div className="h-8 w-px bg-white/10" />
          <div className="flex flex-col items-end">
            <span className="text-gray-500 uppercase font-bold tracking-tighter">Treasury Reserves</span>
            <span className="text-white font-bold">{(treasuryStats.net_reserves / 100000000).toFixed(2)} BTC</span>
          </div>
          <div className="flex items-center gap-2 bg-white/5 px-3 py-2 rounded border border-white/10">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-white font-bold text-xs">{nodeId}</span>
          </div>
        </div>
      </header>

      <div className="max-w-[1400px] mx-auto p-6 grid grid-cols-12 gap-6">
        {/* Sidebar */}
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
              onClick={() => { setActiveTab('cases'); setSelectedCase(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'cases' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Activity className="w-4 h-4" /> Open Disputes
            </button>
            <button 
              onClick={() => { setActiveTab('treasury'); setSelectedCase(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'treasury' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <PiggyBank className="w-4 h-4" /> Treasury Audit
            </button>
            <button 
              onClick={() => { setActiveTab('staking'); setSelectedCase(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'staking' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Wallet className="w-4 h-4" /> Stake Management
            </button>
            <button 
              onClick={() => { setActiveTab('brownout'); setSelectedCase(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'brownout' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Waves className="w-4 h-4" /> Brownout Control
            </button>
            <button 
              onClick={() => { setActiveTab('jitter'); setSelectedCase(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'jitter' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Binary className="w-4 h-4" /> Jitter Proof
            </button>
            <button 
              onClick={() => { setActiveTab('sybil'); setSelectedCase(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'sybil' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Globe className="w-4 h-4" /> Sybil Defense
            </button>
            <button 
              onClick={() => { setActiveTab('security'); setSelectedCase(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === 'security' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
            >
              <Cpu className="w-4 h-4" /> Hardware Security
            </button>
          </nav>

          <div className="p-4 bg-green-500/5 border border-green-500/10 rounded-lg">
            <p className="text-[10px] text-green-400/60 font-bold leading-relaxed uppercase tracking-tighter italic">
              "Treasury audits ensure that the insurance pool funded by the 0.1% protocol tax remains mathematically solvent."
            </p>
          </div>
        </aside>

        {/* Main Interface */}
        <main className="col-span-12 lg:col-span-9">
          
          {/* 1. DISPUTE CASES VIEW */}
          {activeTab === 'cases' && !selectedCase && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden animate-in fade-in duration-300">
              <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/[0.02]">
                <h2 className="text-xs uppercase font-bold tracking-widest flex items-center gap-2 text-amber-500">
                  <Activity className="w-4 h-4" /> Pending Case Docket
                </h2>
              </div>
              <div className="p-20 text-center">
                <ShieldCheck className="w-12 h-12 text-gray-800 mx-auto mb-4" />
                <p className="text-xs text-gray-500 uppercase tracking-widest font-bold">No active disputes require your attention</p>
              </div>
            </div>
          )}

          {/* 2. TREASURY AUDIT VIEW (v2.9 FEATURE) */}
          {activeTab === 'treasury' && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
                {/* Protocol Liquidity Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                   <div className="bg-green-500/5 border border-green-500/20 p-5 rounded-lg">
                      <span className="text-[9px] text-green-400 uppercase font-black block mb-2 tracking-widest">Net Reserves</span>
                      <p className="text-2xl font-black text-white">{(treasuryStats.net_reserves / 1000000).toFixed(1)}M <span className="text-xs text-gray-500 font-normal">SATS</span></p>
                   </div>
                   <div className="bg-blue-500/5 border border-blue-500/20 p-5 rounded-lg">
                      <span className="text-[9px] text-blue-400 uppercase font-black block mb-2 tracking-widest">Insurance Depth</span>
                      <p className="text-2xl font-black text-white">{(treasuryStats.locked_insurance_pool / 1000000).toFixed(1)}M <span className="text-xs text-gray-500 font-normal">SATS</span></p>
                   </div>
                   <div className="bg-amber-500/5 border border-amber-500/20 p-5 rounded-lg">
                      <span className="text-[9px] text-amber-400 uppercase font-black block mb-2 tracking-widest">Slash Rev.</span>
                      <p className="text-2xl font-black text-white">{(treasuryStats.slashing_revenue / 1000000).toFixed(1)}M</p>
                   </div>
                   <div className="bg-red-500/5 border border-red-500/20 p-5 rounded-lg">
                      <span className="text-[9px] text-red-400 uppercase font-black block mb-2 tracking-widest">Total Outflow</span>
                      <p className="text-2xl font-black text-white">{(treasuryStats.total_outflow / 1000000).toFixed(1)}M</p>
                   </div>
                </div>

                {/* Economic Health Analysis */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                   <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between">
                      <div>
                         <h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3">
                            <TrendingUp className="w-5 h-5 text-green-500" /> Solvency Trajectory
                         </h3>
                         <p className="text-xs text-gray-500 leading-relaxed mb-6">
                            The Treasury maintains a <span className="text-white font-bold">5.7x Reserve Ratio</span> relative to pending insurance claims. All slashing events are cryptographically verified by the High Court before funds are moved to the burn address.
                         </p>
                      </div>
                      <div className="p-4 bg-white/5 rounded border border-white/10 space-y-3">
                         <div className="flex justify-between items-center text-[10px] font-black uppercase">
                            <span className="text-gray-500">Weekly Tax Inflow</span>
                            <span className="text-green-500">+1.2M SATS</span>
                         </div>
                         <div className="flex justify-between items-center text-[10px] font-black uppercase">
                            <span className="text-gray-500">Average Payout Value</span>
                            <span className="text-red-400">12.5K SATS</span>
                         </div>
                      </div>
                   </div>

                   <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                      <h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3">
                         <History className="w-5 h-5 text-blue-400" /> Protocol Ledger
                      </h3>
                      <div className="space-y-4">
                         {ledger.map((tx) => (
                           <div key={tx.id} className="flex items-center justify-between group">
                              <div className="flex items-center gap-4">
                                 <div className={`p-2 rounded bg-white/5 border border-white/10 ${tx.type === 'PAYOUT' ? 'text-red-400' : 'text-green-400'}`}>
                                    {tx.type === 'PAYOUT' ? <ArrowDownRight className="w-4 h-4" /> : <ArrowUpRight className="w-4 h-4" />}
                                 </div>
                                 <div>
                                    <span className="text-[10px] font-black text-white block mb-0.5">{tx.id}</span>
                                    <span className="text-[8px] text-gray-600 uppercase font-bold">{tx.type} • {tx.timestamp}</span>
                                 </div>
                              </div>
                              <span className={`text-xs font-black ${tx.type === 'PAYOUT' ? 'text-red-400' : 'text-green-500'}`}>
                                 {tx.type === 'PAYOUT' ? '-' : '+'}{tx.amount.toLocaleString()}
                              </span>
                           </div>
                         ))}
                      </div>
                   </div>
                </div>
             </div>
          )}

          {/* 3. BROWNOUT CONTROL VIEW (Syntax Fixed) */}
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
                          brownoutLevel === 'ORANGE' ? 'bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.3)]' : 
                          'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.3)]'
                        }`} />
                        <span className="text-2xl font-black text-white uppercase">{brownoutLevel}</span>
                     </div>
                  </div>
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between">
                     <span className="text-[10px] text-gray-600 uppercase font-black block mb-2">Manual Override</span>
                     <button onClick={() => setIsManualOverride(!isManualOverride)} className={`w-full py-2 rounded text-[10px] font-black uppercase tracking-widest transition-all ${isManualOverride ? 'bg-orange-500 text-black' : 'bg-white/5 border border-white/10 text-gray-400'}`}>{isManualOverride ? 'ENABLED' : 'DISABLED'}</button>
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
                           <p className="text-[10px] text-gray-400 leading-tight font-bold">
                             {level === 'GREEN' ? 'Normal Operations ( > 300 REP)' : 
                              level === 'YELLOW' ? 'Shed Probationary ( > 500 REP)' : 
                              level === 'ORANGE' ? 'Shed Non-Elite ( > 700 REP)' : 
                              'Whale Only ( > 900 REP)'}
                           </p>
                        </button>
                     ))}
                  </div>
               </div>

               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-black text-gray-500 tracking-widest mb-6">Congestion Audit Log</h3>
                  <div className="space-y-3 font-mono text-[9px]">
                     <div className="flex justify-between text-gray-600">
                        <span>[10:42:12] AUTO_SCALING: PROMOTED TO ORANGE (MEMPOOL {'>'} 5000)</span>
                        <span className="text-green-500 font-black">VERIFIED</span>
                     </div>
                     <div className="flex justify-between text-gray-600">
                        <span>[10:45:00] SHEDDING_EXEC: DROPPED 422 TASKS FROM {'<'} 500 REP NODES</span>
                        <span className="text-green-500 font-black">VERIFIED</span>
                     </div>
                  </div>
               </div>
            </div>
          )}

          {/* 4. STAKE MANAGEMENT VIEW */}
          {activeTab === 'staking' && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8">
                      <div className="flex items-center justify-between mb-8">
                         <h3 className="text-xs uppercase font-black tracking-widest text-white flex items-center gap-3 text-glow"><Lock className="w-5 h-5 text-green-500" /> Locked Collateral</h3>
                         <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded bg-green-500/10 text-green-500 border border-green-500/20">STAKED</span>
                      </div>
                      <div className="space-y-6">
                         <div>
                            <span className="text-[10px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Active Bond Balance</span>
                            <div className="flex items-baseline gap-2"><span className="text-4xl font-black text-white">{(stats.staked_bond / 1000000).toFixed(2)}</span><span className="text-sm font-bold text-gray-500 uppercase tracking-widest">M SATS</span></div>
                         </div>
                         {withdrawalState === 'IDLE' ? (
                            <button onClick={initiateWithdrawal} disabled={isProcessingStake} className="w-full py-4 bg-red-500/5 hover:bg-red-500/10 border border-red-500/20 hover:border-red-500/50 rounded-lg flex items-center justify-center gap-3 transition-all group">
                               <Unlock className="w-4 h-4 text-red-500" /><span className="text-xs font-black uppercase text-red-500 tracking-widest">{isProcessingStake ? 'COMMUNICATING WITH MULTISIG...' : 'Request Release of Stake'}</span>
                            </button>
                         ) : (
                            <div className="w-full py-4 bg-orange-500/10 border border-orange-500/30 rounded-lg flex flex-col items-center text-center px-4">
                               <div className="flex items-center gap-2 text-orange-400 mb-1"><Clock className="w-4 h-4 animate-spin-slow" /><span className="text-[10px] font-black uppercase">Cooling-off Period Active</span></div>
                               <p className="text-[9px] text-orange-400/60 leading-tight">Identity suspended. Final release in {cooldownDaysRemaining} days.</p>
                            </div>
                         )}
                      </div>
                   </div>
                   <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                      <h3 className="text-xs uppercase font-black text-gray-400 mb-6 flex items-center gap-3"><AlertOctagon className="w-5 h-5 text-amber-500" /> Staking Policy v1.1</h3>
                      <p className="text-[11px] text-gray-500 leading-relaxed mb-4">Collateral release is subject to a 14-day observation window to prevent exit-scamming of contested epochs.</p>
                   </div>
                </div>
             </div>
          )}

          {/* 5. JITTER PROOF VIEW */}
          {activeTab === 'jitter' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-black tracking-widest text-cyan-400 flex items-center gap-3 mb-6">
                    <Wifi className="w-5 h-5" /> Network Entropy Analysis
                  </h3>
                  <div className="bg-black/40 h-48 rounded border border-white/5 p-8 flex items-end gap-1 overflow-hidden">
                    {[...Array(60)].map((_, i) => (
                      <div key={i} className="flex-1 bg-cyan-500/20 border-t border-cyan-400/40" style={{ height: `${15 + Math.random() * 70}%` }} />
                    ))}
                  </div>
                  <div className="mt-4 flex justify-between text-[9px] text-gray-600 uppercase font-black tracking-widest">
                    <span>Target Jitter: Organic</span>
                    <span>Status: Monitoring</span>
                  </div>
               </div>
            </div>
          )}

          {/* 6. SYBIL DEFENSE VIEW */}
          {activeTab === 'sybil' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-1">
                  <div className="bg-black/60 rounded-lg h-64 flex flex-col items-center justify-center relative overflow-hidden text-center">
                     <Globe className="w-12 h-12 text-red-500/40 mb-4" />
                     <h3 className="text-xs uppercase font-black text-gray-500 tracking-[0.4em]">Global Node Entropy Map</h3>
                  </div>
               </div>
            </div>
          )}

          {/* 7. HARDWARE SECURITY VIEW */}
          {activeTab === 'security' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8">
                     <div className="flex items-center justify-between mb-8">
                        <h3 className="text-xs uppercase font-black tracking-widest text-white flex items-center gap-3"><Key className="w-5 h-5 text-blue-400" /> TPM 2.0 Identity Management</h3>
                        <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded ${isRotating ? 'bg-yellow-500/10 text-yellow-500 animate-pulse' : 'bg-green-500/10 text-green-500'}`}>{isRotating ? 'ROTATING' : 'LOCKED'}</span>
                     </div>
                     <div className="space-y-6">
                        <div className="bg-black/60 p-4 border border-white/5 rounded mono text-xs text-blue-300 break-all select-all">{nodeId === "NODE_ELITE_X29" ? "0x81010001:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd" : "0x81010002:fresh_" + nodeId}</div>
                        <button disabled={isRotating} onClick={startKeyRotation} className="w-full py-4 bg-blue-500/10 border border-blue-500/30 rounded-lg flex items-center justify-center gap-3 transition-all"><RefreshCw className={`w-4 h-4 text-blue-400 ${isRotating ? 'animate-spin' : ''}`} /><span className="text-xs font-black uppercase text-blue-400 tracking-widest">Rotate Hardware Identity</span></button>
                     </div>
                  </div>
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg flex flex-col">
                     <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center"><h3 className="text-xs uppercase font-black tracking-widest flex items-center gap-2"><Fingerprint className="w-4 h-4 text-gray-500" /> Binding Console</h3></div>
                     <div className="flex-1 p-6 font-mono text-[10px] leading-relaxed overflow-y-auto bg-black/40">
                        <p className="text-gray-600">[*] Hardware Root: OPTIGA TPM 2.0 Detected</p>
                        {keyRotationStep >= 1 && <p className="text-yellow-500 mt-2">[*] Wiping handle 0x81010001... SUCCESS</p>}
                        {keyRotationStep >= 2 && <p className="text-green-500 mt-1">[*] Primary Seed Generated (Silicon Entropy)</p>}
                        {keyRotationStep >= 3 && <p className="text-white font-black mt-2">✅ BINDING CEREMONY COMPLETE.</p>}
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
