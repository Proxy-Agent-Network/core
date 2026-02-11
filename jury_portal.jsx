import React, { useState, useEffect } from 'react';
import { 
  Gavel, ShieldAlert, Eye, CheckCircle2, XCircle, ShieldCheck, 
  Clock, ArrowRight, Lock, Zap, Activity, UserCheck, HeartPulse, 
  Banknote, AlertTriangle, BarChart3, TrendingUp, Scale, UserCircle, 
  Award, Trophy, Download, FileText, Shield, Fingerprint, Cpu, 
  RefreshCw, Key, ShieldQuestion, Globe, Map, ZapOff, Waves, ShieldX, 
  PiggyBank, ArrowUpRight, ArrowDownRight, History, FileSignature, 
  Stamp, Wallet, Unlock, AlertOctagon, Wifi, Binary, ShieldEllipsis, 
  Database, FileCode, CheckSquare, Layers, MapPin, Navigation
} from 'lucide-react';

// --- MODULAR COMPONENTS ---

const ProtocolHeader = ({ nodeId, reserves, tier }) => (
  <header className="border-b border-white/10 bg-[#0d0d0e] px-6 py-4 flex justify-between items-center sticky top-0 z-50">
    <div className="flex items-center gap-3">
      <div className="bg-amber-500/10 p-2 rounded border border-amber-500/20">
        <Gavel className="w-5 h-5 text-amber-500" />
      </div>
      <div>
        <h1 className="text-sm font-bold tracking-tighter text-white uppercase tracking-widest leading-none">Jury Tribunal v2.12</h1>
        <p className="text-[9px] text-amber-500/70 uppercase tracking-widest mt-1">Geospatial Integrity Mapping Active</p>
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
        <span className="text-white font-bold">{(reserves / 100000000).toFixed(2)} BTC</span>
      </div>
      <div className="flex items-center gap-2 bg-white/5 px-3 py-2 rounded border border-white/10">
        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
        <span className="text-white font-bold text-xs tracking-tighter">{nodeId}</span>
      </div>
    </div>
  </header>
);

const JudicialStanding = ({ stats }) => (
  <div className="bg-[#0d0d0e] border border-white/10 p-5 rounded-lg text-glow">
    <h3 className="text-[10px] uppercase text-gray-500 mb-4 font-bold tracking-widest">Judicial Standing</h3>
    <div className="space-y-4">
      <div className="flex justify-between items-center text-sm font-bold">
        <span>Reputation</span>
        <span className="text-amber-500">{stats.reputation}/1000</span>
      </div>
      <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
        <div className="bg-amber-500 h-full" style={{ width: `${(stats.reputation / 1000) * 100}%` }} />
      </div>
      <div className="grid grid-cols-2 gap-2 pt-2">
        <div className="bg-white/5 p-3 rounded border border-white/5 text-center">
          <p className="text-[9px] text-gray-500 uppercase mb-1 font-bold tracking-tighter">Accuracy</p>
          <p className="text-sm font-bold text-white">{stats.accuracy_rate}</p>
        </div>
        <div className="bg-white/5 p-3 rounded border border-white/5 text-center">
          <p className="text-[9px] text-gray-500 uppercase mb-1 font-bold tracking-tighter">Yield</p>
          <p className="text-sm font-bold text-green-500">+{stats.earned_fees}</p>
        </div>
      </div>
    </div>
  </div>
);

// --- v2.12 NEW: Reputation Heatmap Dashboard ---
const ReputationHeatmapTab = ({ regions }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-1">
      <div className="bg-black/60 rounded-lg h-[400px] relative overflow-hidden flex flex-col items-center justify-center border border-white/5">
        <div className="absolute inset-0 opacity-[0.07] pointer-events-none" 
             style={{ backgroundImage: 'radial-gradient(#00FF41 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
        
        {/* Animated Map Markers */}
        <div className="absolute top-1/4 left-1/4 group cursor-help">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-ping opacity-20 absolute" />
          <div className="w-3 h-3 bg-green-500 rounded-full relative" />
          <div className="hidden group-hover:block absolute top-6 left-0 bg-black/90 border border-green-500/30 p-2 rounded text-[8px] mono whitespace-nowrap z-20">
            REGION: US-EAST<br/>HONESTY: 98.2%
          </div>
        </div>

        <div className="absolute bottom-1/3 right-1/3 group cursor-help">
          <div className="w-3 h-3 bg-red-500 rounded-full animate-ping absolute" />
          <div className="w-3 h-3 bg-red-500 rounded-full relative" />
          <div className="hidden group-hover:block absolute top-6 left-0 bg-black/90 border border-red-500/30 p-2 rounded text-[8px] mono whitespace-nowrap z-20">
            REGION: ASIA-SOUTH<br/>HONESTY: 64.1% [ANOMALY]
          </div>
        </div>

        <Globe className="w-16 h-16 text-gray-800 mb-4" />
        <h3 className="text-xs uppercase font-black text-gray-500 tracking-[0.5em]">Geospatial Reputation Grid</h3>
        <p className="text-[9px] text-gray-700 mt-2 uppercase font-bold">Telemetry sourced from Hardware-Heartbeat v1.4</p>
      </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {regions.map((region) => (
        <div key={region.name} className={`bg-[#0d0d0e] border rounded-lg p-5 transition-all hover:bg-white/[0.01] ${region.status === 'CRITICAL' ? 'border-red-500/20' : 'border-white/10'}`}>
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-2">
              <MapPin className={`w-4 h-4 ${region.status === 'CRITICAL' ? 'text-red-500' : 'text-green-500'}`} />
              <span className="text-xs font-black text-white uppercase tracking-tighter">{region.name}</span>
            </div>
            <span className={`text-[8px] font-black px-1.5 py-0.5 rounded uppercase tracking-tighter ${region.status === 'HEALTHY' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
              {region.status}
            </span>
          </div>
          <div className="flex items-baseline gap-2 mb-4">
            <span className="text-2xl font-black text-white">{region.score}%</span>
            <span className="text-[9px] text-gray-600 uppercase font-bold tracking-tighter">Honesty Index</span>
          </div>
          <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden mb-4">
            <div className={`h-full ${region.score > 90 ? 'bg-green-500' : region.score > 80 ? 'bg-amber-500' : 'bg-red-500'}`} 
                 style={{ width: `${region.score}%` }} />
          </div>
          <p className="text-[10px] text-gray-500 leading-tight italic">
            "{region.insight}"
          </p>
        </div>
      ))}
    </div>
  </div>
);

const MultiSigTab = ({ pendingTx, onSign, isSigning }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden">
      <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center text-glow">
        <h2 className="text-xs uppercase font-black tracking-widest flex items-center gap-2 text-white">
          <Layers className="w-4 h-4 text-blue-400" /> Pending Consensus Transactions
        </h2>
        <span className="text-[9px] text-gray-500 uppercase font-bold tracking-tighter">Threshold: 2-of-3 Required</span>
      </div>
      <div className="divide-y divide-white/5">
        {pendingTx.map((tx) => (
          <div key={tx.id} className="p-6 flex flex-col lg:flex-row justify-between gap-6 hover:bg-white/[0.01] transition-all">
            <div className="flex gap-6">
              <div className="w-14 h-14 bg-blue-500/10 rounded border border-blue-500/20 flex flex-col items-center justify-center">
                <Banknote className="w-6 h-6 text-blue-400" />
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-black text-white uppercase">{tx.id}</span>
                  <span className="text-[9px] bg-white/5 px-2 py-0.5 rounded text-gray-400 uppercase font-bold tracking-tighter">{tx.type}</span>
                </div>
                <p className="text-xs text-gray-500 max-w-md leading-relaxed">{tx.description}</p>
                <div className="flex items-center gap-4 pt-1">
                  <span className="text-[9px] text-gray-600 mono truncate max-w-[200px]">TO: {tx.destination}</span>
                  <span className="text-[9px] text-blue-400 font-black uppercase">AMOUNT: {tx.amount.toLocaleString()} SATS</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-6">
               <div className="flex flex-col items-end gap-2">
                  <div className="flex gap-1">
                    {[...Array(3)].map((_, i) => (
                      <div key={i} className={`w-3 h-3 rounded-full border ${i < tx.sigs ? 'bg-green-500 border-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]' : 'border-gray-800'}`} />
                    ))}
                  </div>
                  <span className="text-[9px] text-gray-600 uppercase font-black">{tx.sigs}/3 Signatures</span>
               </div>
               <button 
                  onClick={() => onSign(tx.id)}
                  disabled={isSigning || tx.signed_by_me}
                  className={`px-6 py-3 rounded text-[10px] font-black uppercase tracking-widest transition-all ${
                    tx.signed_by_me 
                      ? 'bg-green-500/10 text-green-500 border border-green-500/20 cursor-default' 
                      : 'bg-blue-500/10 border border-blue-500/30 text-blue-400 hover:bg-blue-500 hover:text-black'
                  }`}
               >
                  {isSigning ? 'Signing...' : tx.signed_by_me ? 'Verified' : 'Affix Signature'}
               </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const TreasuryTab = ({ treasuryStats, ledger }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="bg-green-500/5 border border-green-500/20 p-5 rounded-lg">
        <span className="text-[9px] text-green-400 uppercase font-black block mb-2 tracking-widest">Net Reserves</span>
        <p className="text-2xl font-black text-white">{(treasuryStats.net_reserves / 1000000).toFixed(1)}M <span className="text-xs text-gray-500 font-normal">SATS</span></p>
      </div>
      <div className="bg-blue-500/5 border border-blue-500/20 p-5 rounded-lg">
        <span className="text-[9px] text-blue-400 uppercase font-black block mb-2 tracking-widest">Insurance Pool</span>
        <p className="text-2xl font-black text-white">{(treasuryStats.locked_insurance_pool / 1000000).toFixed(1)}M</p>
      </div>
      <div className="bg-amber-500/5 border border-amber-500/20 p-5 rounded-lg">
        <span className="text-[9px] text-amber-400 uppercase font-black block mb-2 tracking-widest">Slash Revenue</span>
        <p className="text-2xl font-black text-white">{(treasuryStats.slashing_revenue / 1000000).toFixed(1)}M</p>
      </div>
      <div className="bg-red-500/5 border border-red-500/20 p-5 rounded-lg">
        <span className="text-[9px] text-red-400 uppercase font-black block mb-2 tracking-widest">Insurance Drain</span>
        <p className="text-2xl font-black text-white">{(treasuryStats.total_outflow / 1000000).toFixed(1)}M</p>
      </div>
    </div>
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
      <h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3">
        <History className="w-5 h-5 text-blue-400" /> Transaction Ledger
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
              {tx.type === 'PAYOUT' ? '-' : '+'}{tx.amount.toLocaleString()} SATS
            </span>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  const [isVoting, setIsVoting] = useState(false);
  const [isSigningTx, setIsSigningTx] = useState(false);
  
  // v2.10 Evidence Locker State
  const [isDecrypting, setIsDecrypting] = useState(false);
  const [isEvidenceUnlocked, setIsEvidenceUnlocked] = useState(false);

  // Hardware States
  const [nodeId, setNodeId] = useState("NODE_ELITE_X29");

  // Treasury State
  const [treasuryStats] = useState({
    total_inflow: 84290100,
    total_outflow: 12500000,
    slashing_revenue: 34000000,
    tax_revenue: 50290100,
    net_reserves: 71790100,
    locked_insurance_pool: 10450200
  });

  // v2.11 Multi-Sig State
  const [pendingTx, setPendingTx] = useState([
    {
      id: "MSIG-4421",
      type: "BOND_RELEASE",
      description: "Return of collateral for Node_Alpha (Exit-cooling period complete).",
      destination: "bc1q...x921",
      amount: 2000000,
      sigs: 1,
      signed_by_me: false
    },
    {
      id: "MSIG-4422",
      type: "INSURANCE_PAYOUT",
      description: "Compensating Node_Gamma for SEV-2 LND Desync Event.",
      destination: "bc1p...v012",
      amount: 10000,
      sigs: 1,
      signed_by_me: false
    }
  ]);

  // v2.12 Heatmap State
  const [regionStats] = useState([
    { name: "North America", score: 98.4, status: "HEALTHY", insight: "Minimal jitter deviation detected. High PoA compliance." },
    { name: "Europe-West", score: 94.1, status: "HEALTHY", insight: "Organic node distribution aligned with major urban hubs." },
    { name: "Asia-South", score: 64.2, status: "CRITICAL", insight: "Cluster of identical TPM versions in residential subnets. Sybil risk high." }
  ]);

  const [ledger] = useState([
    { id: "TX-99812", type: "SLASH", amount: 250000, timestamp: "2026-02-11 11:02:00", node: "NODE_MALICIOUS_X8", status: "CONFIRMED" },
    { id: "TX-99811", type: "TAX", amount: 4200, timestamp: "2026-02-11 10:58:12", node: "NODE_ELITE_X29", status: "CONFIRMED" },
    { id: "TX-99810", type: "PAYOUT", amount: 10000, timestamp: "2026-02-11 10:45:00", node: "CLAIM-X01", status: "SETTLED" }
  ]);

  const [cases] = useState([
    {
      id: "CASE-885-4",
      type: "SMS_VERIFICATION",
      status: "PENDING",
      timestamp: "2026-02-11 12:12:00",
      dispute_reason: "Agent claims code relay was incorrect.",
      reward: 500,
      evidence: {
        instructions: "Relay the 6-digit code sent to +1 555-0199.",
        locked_blob_hash: "0x7a2e...f91c",
        decrypted_data: {
          raw_payload: "Your Proxy code is: 882190",
          human_input: "882190",
          tpm_id: "OPTIGA_7721_RPI5",
          carrier: "Verizon Wireless",
          timestamp_ms: 1739268720000
        }
      }
    }
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
      setIsEvidenceUnlocked(false);
    }, 1200);
  };

  const handleSignTx = (txId) => {
    setIsSigningTx(true);
    setTimeout(() => {
      setPendingTx(prev => prev.map(tx => 
        tx.id === txId ? { ...tx, sigs: tx.sigs + 1, signed_by_me: true } : tx
      ));
      setIsSigningTx(false);
    }, 2000);
  };

  const handleUnlockEvidence = () => {
    setIsDecrypting(true);
    setTimeout(() => {
      setIsDecrypting(false);
      setIsEvidenceUnlocked(true);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-gray-200 font-mono selection:bg-amber-500/30">
      <ProtocolHeader nodeId={nodeId} reserves={treasuryStats.net_reserves} tier={stats.tier} />

      <div className="max-w-[1400px] mx-auto p-6 grid grid-cols-12 gap-6">
        {/* Sidebar */}
        <aside className="col-span-12 lg:col-span-3 space-y-4">
          <JudicialStanding stats={stats} />

          <nav className="space-y-1">
            {[
              { id: 'cases', label: 'Open Disputes', icon: Activity, color: 'amber' },
              { id: 'multisig', label: 'Multi-Sig Sign', icon: CheckSquare, color: 'blue' },
              { id: 'heatmap', label: 'Reputation Map', icon: Globe, color: 'green' },
              { id: 'treasury', label: 'Treasury Audit', icon: PiggyBank, color: 'emerald' },
              { id: 'staking', label: 'Stake Manager', icon: Wallet, color: 'cyan' },
              { id: 'brownout', label: 'Traffic Control', icon: Waves, color: 'orange' },
              { id: 'security', label: 'Hardware Sec', icon: Cpu, color: 'blue' }
            ].map((tab) => (
              <button 
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setSelectedCase(null); }}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${
                  activeTab === tab.id 
                    ? `bg-${tab.color}-500/10 text-${tab.color}-500 border border-${tab.color}-500/20 shadow-[0_0_15px_rgba(0,0,0,0.4)]` 
                    : 'text-gray-500 hover:text-white hover:bg-white/5'
                }`}
              >
                <tab.icon className="w-4 h-4" /> {tab.label}
              </button>
            ))}
          </nav>

          <div className="p-4 bg-green-500/5 border border-green-500/10 rounded-lg">
            <p className="text-[10px] text-green-400/60 font-bold leading-relaxed uppercase tracking-tighter italic">
              "Mapping regional honesty prevents territorial collusion and allows the protocol to dynamic-weight jury selection."
            </p>
          </div>
        </aside>

        {/* Main Interface */}
        <main className="col-span-12 lg:col-span-9">
          
          {/* CASES TAB */}
          {activeTab === 'cases' && !selectedCase && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden animate-in fade-in duration-300">
              <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center">
                <h2 className="text-xs uppercase font-black tracking-widest flex items-center gap-2 text-amber-500">
                  <Activity className="w-4 h-4" /> Active Dispute Docket
                </h2>
                <span className="text-[9px] text-gray-600 uppercase font-black tracking-tighter">Verified Super-Elite Oversight</span>
              </div>
              <div className="divide-y divide-white/5">
                 {cases.map((c) => (
                    <div key={c.id} className="p-6 flex items-center justify-between hover:bg-white/[0.01] group transition-colors">
                       <div className="flex items-center gap-6">
                          <div className="w-12 h-12 bg-amber-500/10 rounded border border-amber-500/20 flex items-center justify-center text-amber-500">
                             <Database className="w-6 h-6" />
                          </div>
                          <div>
                             <div className="flex items-center gap-3 mb-1">
                                <span className="text-white font-bold uppercase">{c.id}</span>
                                <span className="text-[9px] bg-white/5 px-2 py-0.5 rounded text-gray-400 font-black tracking-widest">{c.type}</span>
                             </div>
                             <p className="text-xs text-gray-500 leading-relaxed max-w-lg">{c.dispute_reason}</p>
                          </div>
                       </div>
                       <button onClick={() => setSelectedCase(c)} className="px-6 py-2 bg-white/5 border border-white/10 rounded text-[10px] font-black uppercase tracking-widest hover:border-amber-500 hover:text-white transition-all">Audit Evidence</button>
                    </div>
                 ))}
              </div>
            </div>
          )}

          {/* REPUTATION HEATMAP (v2.12 FEATURE) */}
          {activeTab === 'heatmap' && <ReputationHeatmapTab regions={regionStats} />}

          {/* MULTI-SIG TAB */}
          {activeTab === 'multisig' && (
             <MultiSigTab 
                pendingTx={pendingTx} 
                onSign={handleSignTx} 
                isSigning={isSigningTx} 
             />
          )}

          {/* TREASURY TAB */}
          {activeTab === 'treasury' && <TreasuryTab treasuryStats={treasuryStats} ledger={ledger} />}

          {/* CASE DETAIL VIEW */}
          {selectedCase && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
                <button onClick={() => { setSelectedCase(null); setIsEvidenceUnlocked(false); }} className="text-xs text-gray-500 hover:text-white mb-2 flex items-center gap-2 font-black uppercase tracking-widest"><ArrowRight className="w-3 h-3 rotate-180" /> Back to Docket</button>
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                   <div className="lg:col-span-4 space-y-6">
                      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                         <h3 className="text-xs font-black uppercase text-white mb-6 flex items-center gap-2"><Activity className="w-4 h-4 text-amber-500" /> Case Context</h3>
                         <div className="space-y-4 text-[10px]">
                            <div><span className="text-gray-600 block uppercase font-bold mb-1">Instruction Log</span><p className="text-gray-400 leading-relaxed italic border-l-2 border-amber-500/20 pl-3">"{selectedCase.evidence.instructions}"</p></div>
                            <div className="pt-4 border-t border-white/5 flex justify-between font-black text-green-500 uppercase tracking-tighter"><span>Adjudication Reward</span><span>+{selectedCase.reward} SATS</span></div>
                         </div>
                      </div>
                   </div>
                   <div className="lg:col-span-8 bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden min-h-[400px] flex flex-col relative shadow-2xl">
                      <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center"><h3 className="text-xs font-black tracking-widest text-white flex items-center gap-2"><ShieldEllipsis className="w-5 h-5 text-amber-500" /> Secure Evidence Locker</h3><span className="text-[9px] text-gray-600 mono uppercase tracking-tighter">CID: {selectedCase.evidence.locked_blob_hash}</span></div>
                      <div className="flex-1 p-8 flex flex-col items-center justify-center bg-black/40 relative z-10">
                         {!isEvidenceUnlocked ? (
                            <div className="text-center max-w-sm">
                               <div className="w-16 h-16 bg-amber-500/10 rounded-full flex items-center justify-center border border-amber-500/20 mx-auto mb-6"><Fingerprint className={`w-8 h-8 text-amber-500 ${isDecrypting ? 'animate-pulse' : ''}`} /></div>
                               <h4 className="text-white font-bold uppercase mb-2 tracking-widest">Evidence Sealed</h4>
                               <p className="text-xs text-gray-500 mb-8 leading-relaxed">High Court hardware signature required to zero-knowledge decrypt the biological proof blob.</p>
                               <button onClick={handleUnlockEvidence} disabled={isDecrypting} className="px-8 py-3 bg-amber-500/10 border border-amber-500/30 text-amber-500 text-[10px] font-black uppercase tracking-[0.2em] rounded-lg hover:bg-amber-500 hover:text-black transition-all shadow-[0_0_20px_rgba(245,158,11,0.1)]">{isDecrypting ? 'Wrangling Silicon...' : 'Unlock via TPM Signature'}</button>
                            </div>
                         ) : (
                            <div className="w-full h-full animate-in zoom-in-95 duration-500 grid grid-cols-1 md:grid-cols-2 gap-4">
                               <div className="p-6 bg-white/[0.02] border border-white/5 rounded-lg overflow-y-auto"><div className="flex items-center gap-2 mb-4 text-green-500"><FileCode className="w-4 h-4" /><span className="text-[9px] font-black uppercase tracking-widest">Decrypted Payload</span></div><pre className="text-[10px] text-gray-400 mono leading-relaxed">{JSON.stringify(selectedCase.evidence.decrypted_data, null, 2)}</pre></div>
                               <div className="space-y-4 flex flex-col">
                                  <div className="p-4 bg-green-500/5 border border-green-500/20 rounded"><span className="text-[9px] text-green-400 font-black uppercase block mb-1">Hardware Attestation</span><p className="text-xs text-white">Silicon binding verified. Response generated within TEE environment.</p></div>
                                  <div className="p-4 bg-black/40 border border-white/5 rounded flex-1 flex flex-col"><span className="text-[9px] text-gray-600 font-black uppercase block mb-4 tracking-widest text-center">Cast Final Verdict</span><button onClick={() => handleVote('VALID')} disabled={isVoting} className="w-full py-3 mb-2 bg-green-500/10 border border-green-500/30 text-green-500 font-black text-[10px] uppercase tracking-widest hover:bg-green-500 hover:text-black transition-all">Verify Valid</button><button onClick={() => handleVote('FRAUD')} disabled={isVoting} className="w-full py-3 bg-red-500/10 border border-red-500/30 text-red-500 font-black text-[10px] uppercase tracking-widest hover:bg-red-500 hover:text-black transition-all">Verify Fraud</button></div>
                               </div>
                            </div>
                         )}
                      </div>
                   </div>
                </div>
             </div>
          )}

          {/* STAKING TAB */}
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
                            <span className="text-[10px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Active Bond</span>
                            <div className="flex items-baseline gap-2 font-black text-white"><span className="text-4xl">{(stats.staked_bond / 1000000).toFixed(2)}</span><span className="text-sm font-bold text-gray-500 uppercase tracking-widest">M SATS</span></div>
                         </div>
                         <button onClick={initiateWithdrawal} disabled={isProcessingStake} className="w-full py-4 bg-red-500/5 hover:bg-red-500/10 border border-red-500/20 rounded-lg flex items-center justify-center gap-3 transition-all">
                            <Unlock className="w-4 h-4 text-red-500" /><span className="text-xs font-black uppercase text-red-500 tracking-widest">{isProcessingStake ? 'Awaiting Multisig...' : 'Request Release'}</span>
                         </button>
                      </div>
                   </div>
                </div>
             </div>
          )}

          {/* BROWNOUT TAB */}
          {activeTab === 'brownout' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 text-glow">
                     <span className="text-[10px] text-gray-600 uppercase font-black block mb-4 tracking-widest">Mempool Depth</span>
                     <div className="flex items-baseline gap-2"><span className="text-3xl font-black text-white">{mempoolDepth.toLocaleString()}</span><span className="text-xs text-gray-500 uppercase tracking-widest">Tasks</span></div>
                  </div>
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                     <span className="text-[10px] text-gray-600 uppercase font-black block mb-4 tracking-widest">Congestion</span>
                     <div className="flex items-center gap-3"><div className={`w-3 h-3 rounded-full animate-pulse ${brownoutLevel === 'GREEN' ? 'bg-green-500' : 'bg-red-500'}`} /><span className="text-2xl font-black text-white uppercase">{brownoutLevel}</span></div>
                  </div>
               </div>
               <div className="bg-[#0d0d0e] border border-orange-500/20 rounded-lg p-8 grid grid-cols-1 md:grid-cols-4 gap-6">
                  {['GREEN', 'YELLOW', 'ORANGE', 'RED'].map((level) => (
                    <button key={level} disabled className={`p-6 border rounded-lg transition-all flex flex-col items-center text-center ${brownoutLevel === level ? 'bg-white/5 border-orange-500 shadow-[0_0_15px_rgba(249,115,22,0.1)]' : 'bg-black/40 border-white/5 opacity-40'}`}>
                      <span className={`text-[9px] font-black uppercase mb-3 ${level === 'GREEN' ? 'text-green-500' : 'text-red-500'}`}>{level}</span>
                      <p className="text-[10px] text-gray-400 font-bold tracking-tighter leading-tight font-black uppercase">REP {'>'} {level === 'GREEN' ? '300' : '900'}</p>
                    </button>
                  ))}
               </div>
            </div>
          )}

          {/* JITTER TAB */}
          {activeTab === 'jitter' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-black tracking-widest text-cyan-400 flex items-center gap-3 mb-6"><Wifi className="w-5 h-5" /> Network Entropy Stream</h3>
                  <div className="bg-black/40 h-48 rounded border border-white/5 p-8 flex items-end gap-1 overflow-hidden relative">
                    {[...Array(60)].map((_, i) => (<div key={i} className="flex-1 bg-cyan-500/20 border-t border-cyan-400/40" style={{ height: `${15 + Math.random() * 70}%` }} />))}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent pointer-events-none" />
                  </div>
               </div>
            </div>
          )}

          {/* SECURITY TAB */}
          {activeTab === 'security' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8 shadow-xl">
                     <div className="flex items-center justify-between mb-8">
                       <h3 className="text-xs uppercase font-black tracking-widest text-white flex items-center gap-3"><Key className="w-5 h-5 text-blue-400" /> Hardware Root Identity</h3>
                     </div>
                     <div className="space-y-6">
                        <div className="bg-black/60 p-4 border border-white/5 rounded mono text-xs text-blue-300 break-all select-all shadow-inner">0x81010001:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd</div>
                        <button disabled className="w-full py-4 bg-blue-500/5 border border-blue-500/10 rounded-lg flex items-center justify-center gap-3 transition-all"><RefreshCw className="w-4 h-4 text-blue-400" /><span className="text-xs font-black uppercase text-blue-400 tracking-widest">Rotate Identity Handle</span></button>
                     </div>
                  </div>
               </div>
            </div>
          )}

        </main>
      </div>

      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-[-1]" style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '30px 30px' }} />
    </div>
  );
};

export default App;
