import React, { useState, useEffect } from 'react';
import { 
  Gavel, ShieldAlert, Eye, CheckCircle2, XCircle, ShieldCheck, 
  Clock, ArrowRight, Lock, Zap, Activity, UserCheck, HeartPulse, 
  Banknote, AlertTriangle, BarChart3, TrendingUp, Scale, UserCircle, 
  Award, Trophy, Download, FileText, Shield, Fingerprint, Cpu, 
  RefreshCw, Key, ShieldQuestion, Globe, Map, ZapOff, Waves, ShieldX, 
  PiggyBank, ArrowUpRight, ArrowDownRight, History, FileSignature, 
  Stamp, Wallet, Unlock, AlertOctagon, Wifi, Binary, ShieldEllipsis, 
  Database, FileCode, CheckSquare, Layers, MapPin, Navigation,
  PenTool, FilePlus, Send, Archive, PieChart, Target, Calculator
} from 'lucide-react';

// --- MODULAR UI COMPONENTS ---

const ProtocolHeader = ({ nodeId, reserves, tier, brownoutLevel }) => (
  <header className="border-b border-white/10 bg-[#0d0d0e] px-6 py-4 flex justify-between items-center sticky top-0 z-50">
    <div className="flex items-center gap-3">
      <div className="bg-amber-500/10 p-2 rounded border border-amber-500/20">
        <Gavel className="w-5 h-5 text-amber-500" />
      </div>
      <div>
        <h1 className="text-sm font-bold tracking-tighter text-white uppercase tracking-widest leading-none">Jury Tribunal v2.17</h1>
        <p className="text-[9px] text-amber-500/70 uppercase tracking-widest mt-1 text-glow">Secure Adjudication Node</p>
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
        <div className={`w-2 h-2 rounded-full animate-pulse ${brownoutLevel === 'RED' ? 'bg-red-500' : 'bg-green-500'}`} />
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

const LivenessHeatmapTab = ({ heartbeats }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-1">
      <div className="bg-black/60 rounded-lg h-[350px] relative overflow-hidden flex flex-col items-center justify-center border border-white/5">
        <div className="absolute inset-0 opacity-[0.1]" 
             style={{ backgroundImage: 'linear-gradient(#f43f5e 1px, transparent 1px), linear-gradient(90deg, #f43f5e 1px, transparent 1px)', backgroundSize: '25px 25px' }} />
        <HeartPulse className="w-16 h-16 text-rose-500/20 mb-4 animate-pulse" />
        <h3 className="text-xs uppercase font-black text-gray-500 tracking-[0.6em] text-glow-red">Biological Pulse Grid</h3>
        <p className="text-[9px] text-gray-700 mt-2 uppercase font-black tracking-widest">Global Aggregate: 1.2Hz</p>
      </div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {heartbeats.map((hb) => (
        <div key={hb.region} className="bg-[#0d0d0e] border border-white/10 rounded-lg p-5 group hover:border-rose-500/30 transition-all">
          <div className="flex justify-between items-center mb-4">
            <span className="text-[10px] text-gray-500 font-black uppercase">{hb.region}</span>
            <div className={`w-2 h-2 rounded-full ${hb.status === 'ACTIVE' ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.4)]' : 'bg-amber-500'}`} />
          </div>
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-2xl font-black text-white">{hb.count}</span>
            <span className="text-[9px] text-gray-600 uppercase font-bold">Nodes</span>
          </div>
          <div className="flex items-center gap-4">
             <div className="flex-1 bg-white/5 h-1 rounded-full overflow-hidden">
                <div className="bg-rose-500 h-full animate-pulse" style={{ width: `${hb.intensity}%` }} />
             </div>
             <span className="text-[9px] text-rose-400 font-bold">{hb.intensity}%</span>
          </div>
        </div>
      ))}
    </div>
  </div>
);

const InsuranceActuaryTab = ({ actuaryData, onAdjustRate, isAdjusting }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between">
        <div>
          <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest block mb-4">Loss Ratio (90d)</span>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-black text-white">{actuaryData.loss_ratio}%</span>
            <span className={`text-[10px] font-bold ${actuaryData.loss_ratio < 20 ? 'text-green-500' : 'text-red-400'}`}>OPTIMAL</span>
          </div>
        </div>
        <div className="mt-6 space-y-2">
          <div className="flex justify-between text-[10px] uppercase font-bold text-gray-500">
            <span>Premium Revenue</span>
            <span className="text-green-500">+{actuaryData.total_premiums.toLocaleString()} SATS</span>
          </div>
          <div className="flex justify-between text-[10px] uppercase font-bold text-gray-500">
            <span>Claims Paid</span>
            <span className="text-red-400">-{actuaryData.total_payouts.toLocaleString()} SATS</span>
          </div>
        </div>
      </div>

      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
        <h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3"><Calculator className="w-5 h-5 text-blue-400" /> Risk Sectors</h3>
        <div className="space-y-4">
          {actuaryData.risk_sectors.map((s) => (
            <div key={s.name}>
              <div className="flex justify-between items-center text-[10px] mb-2 uppercase font-black text-gray-400">
                <span>{s.name}</span>
                <span className="text-white">{s.prob}%</span>
              </div>
              <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden"><div className="bg-blue-500 h-full" style={{ width: `${s.prob * 10}%` }} /></div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between">
        <h3 className="text-xs uppercase font-black text-white mb-4">Tax Governance</h3>
        <p className="text-[10px] text-gray-500 leading-relaxed mb-6">Current 0.1% tax rate covers all SEV-2 liabilities with a healthy treasury surplus.</p>
        <button onClick={() => onAdjustRate(0.0008)} disabled={isAdjusting} className="w-full py-3 bg-blue-500/10 border border-blue-500/30 text-blue-400 text-[10px] font-black uppercase tracking-widest rounded hover:bg-blue-400 hover:text-black transition-all">
          {isAdjusting ? 'Broadcasting...' : 'Adjust Rate'}
        </button>
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
        <span className="text-[9px] text-blue-400 uppercase font-black block mb-2 tracking-widest">Insurance Depth</span>
        <p className="text-2xl font-black text-white">{(treasuryStats.locked_insurance_pool / 1000000).toFixed(1)}M</p>
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
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
      <h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3"><History className="w-5 h-5 text-blue-400" /> Transaction Ledger</h3>
      <div className="space-y-4">
        {ledger.map((tx) => (
          <div key={tx.id} className="flex items-center justify-between group transition-colors">
            <div className="flex items-center gap-4">
              <div className={`p-2 rounded bg-white/5 border border-white/10 ${tx.type === 'PAYOUT' ? 'text-red-400' : 'text-green-400'}`}>
                {tx.type === 'PAYOUT' ? <ArrowDownRight className="w-4 h-4" /> : <ArrowUpRight className="w-4 h-4" />}
              </div>
              <div><span className="text-[10px] font-black text-white block mb-0.5">{tx.id}</span><span className="text-[8px] text-gray-600 uppercase font-bold">{tx.type} • {tx.timestamp}</span></div>
            </div>
            <span className={`text-xs font-black ${tx.type === 'PAYOUT' ? 'text-red-400' : 'text-green-500'}`}>{tx.type === 'PAYOUT' ? '-' : '+'}{tx.amount.toLocaleString()} SATS</span>
          </div>
        ))}
      </div>
    </div>
  </div>
);

// --- MAIN APP COMPONENT ---

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  const [isVoting, setIsVoting] = useState(false);
  
  // v2.17 State Stabilization
  const [mempoolDepth] = useState(6402);
  const [brownoutLevel] = useState('GREEN');
  const [isManualOverride, setIsManualOverride] = useState(false);
  const [isDecrypting, setIsDecrypting] = useState(false);
  const [isEvidenceUnlocked, setIsEvidenceUnlocked] = useState(false);
  const [isAdjustingActuary, setIsAdjustingActuary] = useState(false);
  const [isRotating, setIsRotating] = useState(false);
  const [withdrawalState] = useState('IDLE');
  const [cooldownDaysRemaining] = useState(14);
  const [nodeId, setNodeId] = useState("NODE_ELITE_X29");

  // Multi-Sig State (Missing from previous turn)
  const [pendingTx, setPendingTx] = useState([
    { id: "MSIG-4421", type: "BOND_RELEASE", description: "Node exit release.", sigs: 1, amount: 2000000, destination: "bc1q...", signed_by_me: false }
  ]);

  // Mock Data
  const [livenessHeartbeats] = useState([
    { region: "US_EAST", count: 442, intensity: 98, status: "ACTIVE" },
    { region: "EU_WEST", count: 310, intensity: 94, status: "ACTIVE" },
    { region: "ASIA_S", count: 128, intensity: 42, status: "DEGRADED" }
  ]);

  const [actuaryData] = useState({
    loss_ratio: 14.8,
    total_premiums: 50290100,
    total_payouts: 12500000,
    risk_sectors: [
      { name: "LND Desync", prob: 0.12 },
      { name: "Physical Theft", prob: 0.82 }
    ]
  });

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
    { id: "TX-99811", type: "TAX", amount: 4200, timestamp: "2026-02-11 10:58:12", node: "NODE_ELITE_X29", status: "CONFIRMED" }
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
        decrypted_data: { raw_payload: "Your Proxy code is: 882190", human_input: "882190", tpm_id: "OPTIGA_7721_RPI5" }
      }
    }
  ]);

  const [stats] = useState({
    reputation: 982,
    staked_bond: 2000000,
    earned_fees: 45200,
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

  const handleAdjustRate = () => {
    setIsAdjustingActuary(true);
    setTimeout(() => setIsAdjustingActuary(false), 2000);
  };

  const handleUnlockEvidence = () => {
    setIsDecrypting(true);
    setTimeout(() => {
      setIsDecrypting(false);
      setIsEvidenceUnlocked(true);
    }, 2000);
  };

  const handleRotateKey = () => {
    setIsRotating(true);
    setTimeout(() => setIsRotating(false), 3000);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-gray-200 font-mono selection:bg-amber-500/30">
      <ProtocolHeader nodeId={nodeId} reserves={treasuryStats.net_reserves} tier={stats.tier} brownoutLevel={brownoutLevel} />

      <div className="max-w-[1400px] mx-auto p-6 grid grid-cols-12 gap-6">
        <aside className="col-span-12 lg:col-span-3 space-y-4">
          <JudicialStanding stats={stats} />
          <nav className="space-y-1">
            {[
              { id: 'cases', label: 'Open Disputes', icon: Activity, color: 'amber' },
              { id: 'liveness', label: 'Liveness Map', icon: HeartPulse, color: 'rose' },
              { id: 'actuary', label: 'Insurance Actuary', icon: Calculator, color: 'blue' },
              { id: 'treasury', label: 'Treasury Audit', icon: PiggyBank, color: 'green' },
              { id: 'staking', label: 'Stake Manager', icon: Wallet, color: 'emerald' },
              { id: 'security', label: 'Hardware Sec', icon: Cpu, color: 'blue' }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button 
                  key={tab.id}
                  onClick={() => { setActiveTab(tab.id); setSelectedCase(null); }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${
                    activeTab === tab.id 
                      ? `bg-${tab.color}-500/10 text-${tab.color}-500 border border-${tab.color}-500/20 shadow-[0_0_15px_rgba(0,0,0,0.5)]` 
                      : 'text-gray-500 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-4 h-4" /> {tab.label}
                </button>
              );
            })}
          </nav>
        </aside>

        <main className="col-span-12 lg:col-span-9">
          {activeTab === 'cases' && !selectedCase && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden animate-in fade-in duration-300">
              <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center text-glow">
                <h2 className="text-xs uppercase font-black tracking-widest flex items-center gap-2 text-amber-500"><Activity className="w-4 h-4" /> Pending Case Docket</h2>
              </div>
              <div className="divide-y divide-white/5">
                 {cases.map((c) => (
                    <div key={c.id} className="p-6 flex items-center justify-between hover:bg-white/[0.01] transition-colors">
                       <div className="flex items-center gap-6"><div className="w-12 h-12 bg-amber-500/10 rounded border border-amber-500/20 flex items-center justify-center text-amber-500"><Database className="w-6 h-6" /></div><div><span className="text-white font-bold uppercase">{c.id}</span><p className="text-xs text-gray-500">{c.dispute_reason}</p></div></div>
                       <button onClick={() => setSelectedCase(c)} className="px-6 py-2 bg-white/5 border border-white/10 rounded text-[10px] font-black uppercase tracking-widest hover:border-amber-500 hover:text-white transition-all">Enter Locker</button>
                    </div>
                 ))}
              </div>
            </div>
          )}

          {activeTab === 'liveness' && <LivenessHeatmapTab heartbeats={livenessHeartbeats} />}
          {activeTab === 'actuary' && <InsuranceActuaryTab actuaryData={actuaryData} onAdjustRate={handleAdjustRate} isAdjusting={isAdjustingActuary} />}
          {activeTab === 'treasury' && <TreasuryTab treasuryStats={treasuryStats} ledger={ledger} />}

          {activeTab === 'staking' && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8">
              <h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3"><Lock className="w-5 h-5 text-green-500" /> Locked Collateral</h3>
              <div className="flex items-baseline gap-2 font-black text-white"><span className="text-4xl">{(stats.staked_bond / 1000000).toFixed(2)}</span><span className="text-sm font-bold text-gray-500 uppercase tracking-widest">M SATS</span></div>
              <button disabled className="mt-8 w-full py-4 bg-red-500/5 border border-red-500/20 rounded-lg text-xs font-black uppercase tracking-widest opacity-40">Request Release</button>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8 shadow-xl">
               <h3 className="text-xs uppercase font-black tracking-widest text-white flex items-center gap-3 mb-8"><Key className="w-5 h-5 text-blue-400" /> TPM 2.0 Identity</h3>
               <div className="bg-black/60 p-4 border border-white/5 rounded mono text-[11px] text-blue-300 break-all mb-6">0x81010001:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd</div>
               <button onClick={handleRotateKey} className="w-full py-4 bg-blue-500/5 border border-blue-500/10 rounded-lg flex items-center justify-center gap-3 hover:bg-blue-500/10 transition-all"><RefreshCw className={`w-4 h-4 text-blue-400 ${isRotating ? 'animate-spin' : ''}`} /><span className="text-xs font-black uppercase text-blue-400 tracking-widest">{isRotating ? 'Rotating...' : 'Rotate Handle'}</span></button>
            </div>
          )}

          {selectedCase && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
                <button onClick={() => { setSelectedCase(null); setIsEvidenceUnlocked(false); }} className="text-xs text-gray-500 hover:text-white mb-2 flex items-center gap-2 font-black uppercase tracking-widest"><ArrowRight className="w-3 h-3 rotate-180" /> Back to Docket</button>
                <div className="lg:col-span-8 bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden min-h-[400px] flex flex-col relative shadow-2xl">
                   <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center"><h3 className="text-xs font-black tracking-widest text-white flex items-center gap-2"><ShieldEllipsis className="w-5 h-5 text-amber-500" /> Secure Evidence Locker</h3></div>
                   <div className="flex-1 p-8 flex flex-col items-center justify-center bg-black/40 relative z-10">
                      {!isEvidenceUnlocked ? (
                         <div className="text-center max-w-sm">
                            <Fingerprint className={`w-16 h-16 text-amber-500 mx-auto mb-6 ${isDecrypting ? 'animate-pulse' : ''}`} />
                            <h4 className="text-white font-bold uppercase mb-2 tracking-widest">Evidence Sealed</h4>
                            <p className="text-xs text-gray-500 mb-8 leading-relaxed">High Court hardware signature required to zero-knowledge decrypt the biological proof blob.</p>
                            <button onClick={handleUnlockEvidence} disabled={isDecrypting} className="px-8 py-3 bg-amber-500/10 border border-amber-500/30 text-amber-500 text-[10px] font-black uppercase tracking-[0.2em] rounded-lg hover:bg-amber-500 hover:text-black transition-all shadow-[0_0_20px_rgba(245,158,11,0.2)]">{isDecrypting ? 'RSA-OAEP Handshake...' : 'Unlock via TPM Signature'}</button>
                         </div>
                      ) : (
                         <div className="w-full h-full animate-in zoom-in-95 duration-500 grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-6 bg-white/[0.02] border border-white/5 rounded-lg overflow-y-auto"><FileCode className="w-4 h-4 text-green-500 mb-4" /><pre className="text-[10px] text-gray-400 mono leading-relaxed">{JSON.stringify(selectedCase.evidence.decrypted_data, null, 2)}</pre></div>
                            <div className="space-y-4 flex flex-col"><div className="p-4 bg-green-500/5 border border-green-500/20 rounded text-xs text-white">Hardware Attestation Valid. Response generated in TEE.</div><div className="p-4 bg-black/40 border border-white/5 rounded flex-1 flex flex-col gap-2"><button onClick={() => handleVote('VALID')} disabled={isVoting} className="w-full py-3 bg-green-500/10 border border-green-500/30 text-green-500 font-black text-[10px] uppercase tracking-widest hover:bg-green-500 hover:text-black transition-all">Verify Valid</button><button onClick={() => handleVote('FRAUD')} disabled={isVoting} className="w-full py-3 bg-red-500/10 border border-red-500/30 text-red-500 font-black text-[10px] uppercase tracking-widest hover:bg-red-500 hover:text-black transition-all">Verify Fraud</button></div></div>
                         </div>
                      )}
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
