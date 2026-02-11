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
  PenTool, FilePlus, Send, Archive, PieChart, Target, Calculator,
  ZapOff as LightningOff, LineChart
} from 'lucide-react';

// --- MODULAR COMPONENTS ---

const ProtocolHeader = ({ nodeId, reserves, tier }) => (
  <header className="border-b border-white/10 bg-[#0d0d0e] px-6 py-4 flex justify-between items-center sticky top-0 z-50">
    <div className="flex items-center gap-3">
      <div className="bg-amber-500/10 p-2 rounded border border-amber-500/20">
        <Gavel className="w-5 h-5 text-amber-500" />
      </div>
      <div>
        <h1 className="text-sm font-bold tracking-tighter text-white uppercase tracking-widest leading-none">Jury Tribunal v2.15</h1>
        <p className="text-[9px] text-amber-500/70 uppercase tracking-widest mt-1 text-glow">Actuarial Risk Engine Active</p>
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
        <span className="text-gray-500 uppercase font-bold tracking-tighter">Network Reserves</span>
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

// --- v2.15 NEW: Insurance Actuary Dashboard ---
const InsuranceActuaryTab = ({ actuaryData, onAdjustRate }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      {/* Loss Ratio Card */}
      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between">
        <div>
          <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest block mb-4">Loss Ratio (90d)</span>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-black text-white">{actuaryData.loss_ratio}%</span>
            <span className={`text-[10px] font-bold uppercase ${actuaryData.loss_ratio < 20 ? 'text-green-500' : 'text-red-400'}`}>
              {actuaryData.loss_ratio < 20 ? 'OPTIMAL' : 'ELEVATED'}
            </span>
          </div>
        </div>
        <div className="mt-6 space-y-2">
          <div className="flex justify-between text-[10px] uppercase font-black">
            <span className="text-gray-500">Premium Revenue</span>
            <span className="text-green-500">+{actuaryData.total_premiums.toLocaleString()} SATS</span>
          </div>
          <div className="flex justify-between text-[10px] uppercase font-black">
            <span className="text-gray-500">Claims Paid</span>
            <span className="text-red-400">-{actuaryData.total_payouts.toLocaleString()} SATS</span>
          </div>
        </div>
      </div>

      {/* Probability Index */}
      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
        <h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3">
          <Calculator className="w-5 h-5 text-blue-400" /> Incident Probability
        </h3>
        <div className="space-y-4">
          {actuaryData.risk_sectors.map((sector) => (
            <div key={sector.name}>
              <div className="flex justify-between items-center text-[10px] mb-2 uppercase font-black tracking-tighter">
                <span className="text-gray-400">{sector.name} Failure Rate</span>
                <span className="text-white">{sector.prob}%</span>
              </div>
              <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                <div className="bg-blue-500 h-full" style={{ width: `${sector.prob * 10}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tax Adjustment Controller */}
      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between">
        <div>
          <h3 className="text-xs uppercase font-black text-white mb-4">Premium Settings</h3>
          <p className="text-[10px] text-gray-500 leading-relaxed mb-6">
            The current 0.1% tax is generating a <span className="text-green-500">12.4M SAT</span> monthly surplus. Recommend reduction or liquidity burn.
          </p>
        </div>
        <div className="space-y-3">
          <div className="flex justify-between items-center text-xs font-black bg-black/40 p-3 rounded border border-white/5">
            <span className="text-gray-600 uppercase tracking-widest">Active Rate</span>
            <span className="text-white">0.10%</span>
          </div>
          <button 
            onClick={() => onAdjustRate(0.0008)}
            className="w-full py-3 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 text-blue-400 text-[10px] font-black uppercase tracking-widest rounded transition-all"
          >
            Propose Rate Decrease (0.08%)
          </button>
        </div>
      </div>
    </div>

    {/* Actuarial Charts */}
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8">
       <div className="flex justify-between items-center mb-8">
          <h3 className="text-xs uppercase font-black text-white flex items-center gap-3">
             <LineChart className="w-5 h-5 text-green-500" /> Reserve Growth vs Claims Volatility
          </h3>
          <div className="flex gap-4">
             <span className="flex items-center gap-2 text-[9px] text-green-500 font-bold uppercase"><div className="w-2 h-2 bg-green-500 rounded-full" /> Premiums</span>
             <span className="flex items-center gap-2 text-[9px] text-red-500 font-bold uppercase"><div className="w-2 h-2 bg-red-500 rounded-full" /> Payouts</span>
          </div>
       </div>
       <div className="h-48 flex items-end gap-2 px-2 relative">
          {[...Array(24)].map((_, i) => {
            const h1 = 30 + Math.random() * 50;
            const h2 = Math.random() * h1 * 0.4;
            return (
              <div key={i} className="flex-1 flex flex-col justify-end gap-1 group relative">
                 <div className="w-full bg-red-500/20 border-t border-red-500/40 rounded-t-sm" style={{ height: `${h2}%` }} />
                 <div className="w-full bg-green-500/10 border-t border-green-500/30 rounded-t-sm" style={{ height: `${h1}%` }} />
                 <div className="hidden group-hover:block absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 p-2 rounded text-[8px] z-10 whitespace-nowrap">
                   EPOCH {8800 + i}: +450K | -12K
                 </div>
              </div>
            )
          })}
       </div>
    </div>
  </div>
);

// --- OTHER TAB COMPONENTS (Truncated for readability, preserved in App) ---

const TreasuryTab = ({ treasuryStats, ledger }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="bg-green-500/5 border border-green-500/20 p-5 rounded-lg"><span className="text-[9px] text-green-400 uppercase font-black block mb-2 tracking-widest">Net Reserves</span><p className="text-2xl font-black text-white">{(treasuryStats.net_reserves / 1000000).toFixed(1)}M <span className="text-xs text-gray-500 font-normal">SATS</span></p></div>
      <div className="bg-blue-500/5 border border-blue-500/20 p-5 rounded-lg"><span className="text-[9px] text-blue-400 uppercase font-black block mb-2 tracking-widest">Insurance Pool</span><p className="text-2xl font-black text-white">{(treasuryStats.locked_insurance_pool / 1000000).toFixed(1)}M</p></div>
      <div className="bg-amber-500/5 border border-amber-500/20 p-5 rounded-lg"><span className="text-[9px] text-amber-400 uppercase font-black block mb-2 tracking-widest">Slash Revenue</span><p className="text-2xl font-black text-white">{(treasuryStats.slashing_revenue / 1000000).toFixed(1)}M</p></div>
      <div className="bg-red-500/5 border border-red-500/20 p-5 rounded-lg"><span className="text-[9px] text-red-400 uppercase font-black block mb-2 tracking-widest">Insurance Drain</span><p className="text-2xl font-black text-white">{(treasuryStats.total_outflow / 1000000).toFixed(1)}M</p></div>
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

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  const [isVoting, setIsVoting] = useState(false);
  const [isDecrypting, setIsDecrypting] = useState(false);
  const [isEvidenceUnlocked, setIsEvidenceUnlocked] = useState(false);
  const [isAdjustingActuary, setIsAdjustingActuary] = useState(false);

  const [nodeId, setNodeId] = useState("NODE_ELITE_X29");

  // v2.15 Actuarial State
  const [actuaryData] = useState({
    loss_ratio: 14.8,
    total_premiums: 50290100,
    total_payouts: 12500000,
    risk_sectors: [
      { name: "LND Desync", prob: 0.12 },
      { name: "Jury Collusion", prob: 0.05 },
      { name: "TPM Firmware Hack", prob: 0.01 },
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

  const handleAdjustRate = (newRate) => {
    setIsAdjustingActuary(true);
    setTimeout(() => {
      setIsAdjustingActuary(false);
    }, 1500);
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
              { id: 'actuary', label: 'Insurance Actuary', icon: Calculator, color: 'blue' },
              { id: 'treasury', label: 'Treasury Audit', icon: PiggyBank, color: 'green' },
              { id: 'staking', label: 'Stake Management', icon: Wallet, color: 'emerald' },
              { id: 'brownout', label: 'Brownout Control', icon: Waves, color: 'orange' },
              { id: 'jitter', label: 'Jitter Proof', icon: Binary, color: 'cyan' },
              { id: 'security', label: 'Hardware Security', icon: Cpu, color: 'blue' }
            ].map((tab) => (
              <button 
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setSelectedCase(null); }}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${
                  activeTab === tab.id 
                    ? `bg-${tab.color}-500/10 text-${tab.color}-500 border border-${tab.color}-500/20 shadow-[0_0_15px_rgba(0,0,0,0.5)]` 
                    : 'text-gray-500 hover:text-white hover:bg-white/5'
                }`}
              >
                <tab.icon className="w-4 h-4" /> {tab.label}
              </button>
            ))}
          </nav>

          <div className="p-4 bg-blue-500/5 border border-blue-500/10 rounded-lg">
            <p className="text-[10px] text-blue-400/60 font-bold leading-relaxed uppercase tracking-tighter italic">
              "The High Court reviews actuarial data every epoch to ensure the 0.1% insurance tax is sufficient to cover protocol liabilities."
            </p>
          </div>
        </aside>

        {/* Main Interface */}
        <main className="col-span-12 lg:col-span-9">
          
          {/* CASES TAB */}
          {activeTab === 'cases' && !selectedCase && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden animate-in fade-in duration-300">
              <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center text-glow">
                <h2 className="text-xs uppercase font-black tracking-widest flex items-center gap-2 text-amber-500">
                  <Activity className="w-4 h-4" /> Pending Case Docket
                </h2>
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
                             <p className="text-xs text-gray-500">{c.dispute_reason}</p>
                          </div>
                       </div>
                       <button onClick={() => setSelectedCase(c)} className="px-6 py-2 bg-white/5 border border-white/10 rounded text-[10px] font-black uppercase tracking-widest hover:border-amber-500 hover:text-white transition-all">Enter Locker</button>
                    </div>
                 ))}
              </div>
            </div>
          )}

          {/* INSURANCE ACTUARY (v2.15 FEATURE) */}
          {activeTab === 'actuary' && (
            <InsuranceActuaryTab 
              actuaryData={actuaryData} 
              onAdjustRate={handleAdjustRate} 
              isAdjusting={isAdjustingActuary}
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
                         <h3 className="text-xs font-black uppercase text-white mb-6 flex items-center gap-2"><Activity className="w-4 h-4 text-amber-500" /> Dispute Metadata</h3>
                         <div className="space-y-4 text-[10px]">
                            <div><span className="text-gray-600 block uppercase font-bold mb-1">Incident Type</span><span className="text-white">{selectedCase.type}</span></div>
                            <div><span className="text-gray-600 block uppercase font-bold mb-1">Instructions</span><p className="text-gray-400 leading-relaxed italic border-l-2 border-amber-500/20 pl-3">"{selectedCase.evidence.instructions}"</p></div>
                            <div className="pt-4 border-t border-white/5 flex justify-between font-black text-green-500 uppercase"><span>Reward</span><span>+{selectedCase.reward} SATS</span></div>
                         </div>
                      </div>
                   </div>
                   <div className="lg:col-span-8 bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden min-h-[400px] flex flex-col relative">
                      <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center"><h3 className="text-xs font-black tracking-widest text-white flex items-center gap-2 text-glow"><ShieldEllipsis className="w-5 h-5 text-amber-500" /> Evidence Locker</h3><span className="text-[9px] text-gray-600 mono uppercase tracking-tighter">Blob: {selectedCase.evidence.locked_blob_hash}</span></div>
                      <div className="flex-1 p-8 flex flex-col items-center justify-center bg-black/40 relative z-10">
                         {!isEvidenceUnlocked ? (
                            <div className="text-center max-w-sm">
                               <div className="w-16 h-16 bg-amber-500/10 rounded-full flex items-center justify-center border border-amber-500/20 mx-auto mb-6"><Fingerprint className={`w-8 h-8 text-amber-500 ${isDecrypting ? 'animate-pulse' : ''}`} /></div>
                               <h4 className="text-white font-bold uppercase mb-2 tracking-widest">Evidence Sealed</h4>
                               <p className="text-xs text-gray-500 mb-8 leading-relaxed">Requires High Court RSA-OAEP decryption via TPM.</p>
                               <button onClick={handleUnlockEvidence} disabled={isDecrypting} className="px-8 py-3 bg-amber-500/10 border border-amber-500/30 text-amber-500 text-[10px] font-black uppercase tracking-[0.2em] rounded-lg hover:bg-amber-500 hover:text-black transition-all">{isDecrypting ? 'Decrypting...' : 'Unlock Evidence'}</button>
                            </div>
                         ) : (
                            <div className="w-full h-full animate-in zoom-in-95 duration-500 grid grid-cols-1 md:grid-cols-2 gap-4">
                               <div className="p-6 bg-white/[0.02] border border-white/5 rounded-lg overflow-y-auto"><div className="flex items-center gap-2 mb-4 text-green-500"><FileCode className="w-4 h-4" /><span className="text-[9px] font-black uppercase">Decrypted Proof</span></div><pre className="text-[10px] text-gray-400 mono leading-relaxed">{JSON.stringify(selectedCase.evidence.decrypted_data, null, 2)}</pre></div>
                               <div className="space-y-4 flex flex-col">
                                  <div className="p-4 bg-green-500/5 border border-green-500/20 rounded"><span className="text-[9px] text-green-400 font-black uppercase block mb-1">Hardware Audit</span><p className="text-xs text-white">TPM Quote Valid. Instruction matched at T+42s.</p></div>
                                  <div className="p-4 bg-black/40 border border-white/5 rounded flex-1 flex flex-col"><span className="text-[9px] text-gray-600 font-black uppercase block mb-4">Cast Verdict</span><button onClick={() => handleVote('VALID')} disabled={isVoting} className="w-full py-3 mb-2 bg-green-500/10 border border-green-500/30 text-green-500 font-black text-[10px] uppercase tracking-widest hover:bg-green-500 hover:text-black transition-all">Valid</button><button onClick={() => handleVote('FRAUD')} disabled={isVoting} className="w-full py-3 bg-red-500/10 border border-red-500/30 text-red-500 font-black text-[10px] uppercase tracking-widest hover:bg-red-500 hover:text-black transition-all">Fraud</button></div>
                               </div>
                            </div>
                         )}
                      </div>
                   </div>
                </div>
             </div>
          )}

          {/* BROWNOUT TAB */}
          {activeTab === 'brownout' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                     <span className="text-[10px] text-gray-600 uppercase font-black block mb-4 tracking-widest">Mempool Depth</span>
                     <div className="flex items-baseline gap-2"><span className="text-3xl font-black text-white">{mempoolDepth.toLocaleString()}</span><span className="text-xs text-gray-500 uppercase tracking-widest">Tasks</span></div>
                  </div>
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                     <span className="text-[10px] text-gray-600 uppercase font-black block mb-4 tracking-widest text-glow">Congestion Level</span>
                     <div className="flex items-center gap-3"><div className={`w-3 h-3 rounded-full animate-pulse ${brownoutLevel === 'GREEN' ? 'bg-green-500' : 'bg-red-500'}`} /><span className="text-2xl font-black text-white uppercase">{brownoutLevel}</span></div>
                  </div>
               </div>
               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 font-mono text-[9px] text-gray-600 space-y-2">
                  <p>[10:42:12] AUTO_SCALING: PROMOTED TO ORANGE (MEMPOOL {'>'} 5000)</p>
                  <p>[10:45:00] SHEDDING_EXEC: DROPPED 422 TASKS FROM {'<' } 500 REP NODES</p>
               </div>
            </div>
          )}

          {/* JITTER TAB */}
          {activeTab === 'jitter' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
                  <h3 className="text-xs uppercase font-black tracking-widest text-cyan-400 flex items-center gap-3 mb-6"><Wifi className="w-5 h-5" /> Network Entropy Analysis</h3>
                  <div className="bg-black/40 h-48 rounded border border-white/5 p-8 flex items-end gap-1 overflow-hidden">
                    {[...Array(60)].map((_, i) => (<div key={i} className="flex-1 bg-cyan-500/20 border-t border-cyan-400/40" style={{ height: `${15 + Math.random() * 70}%` }} />))}
                  </div>
               </div>
            </div>
          )}

          {/* SECURITY TAB */}
          {activeTab === 'security' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
               <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8">
                     <div className="flex items-center justify-between mb-8"><h3 className="text-xs uppercase font-black tracking-widest text-white flex items-center gap-3"><Key className="w-5 h-5 text-blue-400" /> TPM 2.0 Identity</h3></div>
                     <div className="space-y-6 text-glow">
                        <div className="bg-black/60 p-4 border border-white/5 rounded mono text-xs text-blue-300 break-all select-all">0x81010001:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd</div>
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
