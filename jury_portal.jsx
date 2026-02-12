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
  MessageSquare, User, LayoutGrid, Focus, Percent, ChevronRight,
  ShieldHalf, Terminal, EyeOff
} from 'lucide-react';

// --- MODULAR UI COMPONENTS ---

const ProtocolHeader = ({ nodeId, reserves, brownoutLevel }) => (
  <header className="border-b border-white/10 bg-[#0d0d0e] px-6 py-4 flex justify-between items-center sticky top-0 z-50">
    <div className="flex items-center gap-3">
      <div className="bg-amber-500/10 p-2 rounded border border-amber-500/20">
        <Gavel className="w-5 h-5 text-amber-500" />
      </div>
      <div>
        <h1 className="text-sm font-bold tracking-tighter text-white uppercase tracking-widest leading-none">Jury Tribunal v3.1</h1>
        <p className="text-[9px] text-amber-500/70 uppercase tracking-widest mt-1 text-glow">High Court Protocol v2.2.2</p>
      </div>
    </div>
    
    <div className="flex items-center gap-6 text-[11px]">
      <div className="flex flex-col items-end">
        <span className="text-gray-500 uppercase font-bold tracking-tighter text-[9px]">Status</span>
        <span className="text-green-500 flex items-center gap-1 font-bold">
          <ShieldCheck className="w-3 h-3" /> HIGH COURT ACTIVE
        </span>
      </div>
      <div className="h-8 w-px bg-white/10" />
      <div className="flex flex-col items-end">
        <span className="text-gray-500 uppercase font-bold tracking-tighter text-[9px]">Treasury</span>
        <span className="text-white font-bold">{(reserves / 100000000).toFixed(2)} BTC</span>
      </div>
      <div className="flex items-center gap-2 bg-white/5 px-3 py-2 rounded border border-white/10">
        <div className={`w-2 h-2 rounded-full animate-pulse ${brownoutLevel === 'RED' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' : 'bg-green-500'}`} />
        <span className="text-white font-bold text-xs tracking-tighter">{nodeId}</span>
      </div>
    </div>
  </header>
);

const JudicialStanding = ({ stats }) => (
  <div className="bg-[#0d0d0e] border border-white/10 p-5 rounded-lg text-glow shadow-xl">
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

// --- STAGE: DISPUTE EVIDENCE LOCKER ---

const EvidenceLockerView = ({ selectedCase, onVote }) => {
  const [isDecrypting, setIsDecrypting] = useState(false);
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [voteValue, setVoteValue] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleDecryption = () => {
    setIsDecrypting(true);
    // Simulate TPM 2.0 Unseal Command
    setTimeout(() => {
      setIsDecrypting(false);
      setIsUnlocked(true);
    }, 2500);
  };

  const handleSubmit = () => {
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      onVote();
    }, 1500);
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
      {/* Case Header */}
      <div className="bg-[#0d0d0e] border border-white/10 p-8 rounded-lg shadow-2xl flex flex-col md:flex-row justify-between items-start gap-6">
        <div>
          <div className="flex items-center gap-3 mb-4">
             <span className="px-2 py-1 bg-amber-500/10 text-amber-500 text-[9px] font-black uppercase rounded border border-amber-500/20 tracking-widest">
               {selectedCase.type}
             </span>
             <span className="text-[10px] text-gray-600 font-bold uppercase tracking-tighter">DISPUTE_ID: {selectedCase.id}</span>
          </div>
          <h2 className="text-3xl font-black text-white tracking-tight uppercase mb-2">High Court Adjudication</h2>
          <p className="text-sm text-gray-500 flex items-center gap-2">
            <Clock className="w-3.5 h-3.5" /> Convocation Expires: 03h 42m
          </p>
        </div>
        <div className="bg-black/40 border border-white/5 p-4 rounded text-right">
           <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Potential Yield</span>
           <span className="text-xl font-black text-green-500">+{selectedCase.reward} SATS</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: The Evidence Frame */}
        <div className="lg:col-span-2 bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden flex flex-col min-h-[500px] shadow-2xl">
          <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/[0.02]">
            <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-2">
              <Database className="w-3.5 h-3.5 text-amber-500" /> Evidence Shard
            </h3>
            <span className="text-[9px] text-gray-600 font-bold uppercase">RSA-OAEP // SHA-256</span>
          </div>
          
          <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
            {!isUnlocked ? (
              <div className="max-w-md">
                <div className="w-16 h-16 bg-white/5 border border-white/10 rounded-full flex items-center justify-center mx-auto mb-6 shadow-inner">
                  <Lock className={`w-6 h-6 ${isDecrypting ? 'text-amber-500 animate-pulse' : 'text-gray-500'}`} />
                </div>
                <h3 className="text-lg font-black text-white mb-2 uppercase tracking-tighter">Ciphertext Encrypted</h3>
                <p className="text-xs text-gray-500 mb-8 leading-relaxed">
                  The evidence shard for {selectedCase.id} is encrypted for your hardware key. Invoke your local TPM to reveal the task metadata.
                </p>
                <button 
                  onClick={handleDecryption}
                  disabled={isDecrypting}
                  className="w-full py-3 bg-amber-500 text-black font-black text-xs uppercase tracking-widest hover:bg-amber-400 transition-all flex items-center justify-center gap-3 disabled:opacity-50"
                >
                  {isDecrypting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Fingerprint className="w-3.5 h-3.5" />}
                  {isDecrypting ? 'Decryption in Progress...' : 'Invoke Hardware Decrypt'}
                </button>
              </div>
            ) : (
              <div className="w-full h-full text-left space-y-8 animate-in fade-in zoom-in-95">
                <div>
                  <h4 className="text-[10px] font-black text-gray-600 uppercase mb-3 flex items-center gap-2">
                    <ShieldAlert className="w-3.5 h-3.5 text-amber-500" /> Agent Instructions
                  </h4>
                  <div className="bg-black/40 border border-white/5 p-4 rounded text-sm text-gray-300 italic font-medium">
                    "{selectedCase.evidence.instructions}"
                  </div>
                </div>

                <div>
                  <h4 className="text-[10px] font-black text-gray-600 uppercase mb-3 flex items-center gap-2">
                    <Eye className="w-3.5 h-3.5 text-green-500" /> Human Node Submission
                  </h4>
                  <div className="bg-black/40 border border-white/5 p-4 rounded mono text-xs text-green-500/80 break-all leading-relaxed">
                    {JSON.stringify(selectedCase.evidence.decrypted_data, null, 2)}
                  </div>
                </div>

                <div className="p-4 border border-blue-500/20 bg-blue-500/5 rounded flex items-center gap-4">
                   <ShieldCheck className="w-6 h-6 text-blue-400" />
                   <div>
                     <p className="text-[10px] text-blue-400 font-black uppercase tracking-widest">Hardware Attestation</p>
                     <p className="text-[9px] text-gray-500">TPM Proof {selectedCase.evidence.locked_blob_hash.substring(0, 16)} verified locally.</p>
                   </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right: The Voting Console */}
        <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8 shadow-2xl flex flex-col justify-between">
           <div>
              <h3 className="text-xs uppercase font-black text-white mb-6 border-b border-white/10 pb-4 flex items-center gap-2 tracking-widest">
                <Gavel className="w-4 h-4 text-amber-500" /> Final Verdict
              </h3>
              <p className="text-[10px] text-gray-500 leading-relaxed mb-8 font-bold italic">
                "As an Elite Juror, your vote is a commitment to the Schelling Point. Voting against consensus will result in a 600,000 SAT bond slash."
              </p>
              
              <div className="space-y-4">
                 <button 
                   onClick={() => setVoteValue('APPROVE')}
                   disabled={!isUnlocked || isSubmitting}
                   className={`w-full py-4 border rounded-lg flex items-center justify-center gap-3 transition-all ${
                     voteValue === 'APPROVE' 
                       ? 'bg-green-500 border-green-400 text-black font-black' 
                       : 'bg-white/5 border-white/10 text-gray-500 hover:border-green-500/50 hover:text-green-500'
                   } disabled:opacity-20`}
                 >
                   <CheckCircle2 className="w-4 h-4" /> 
                   <span className="text-xs uppercase tracking-widest">Approve Task</span>
                 </button>

                 <button 
                   onClick={() => setVoteValue('REJECT')}
                   disabled={!isUnlocked || isSubmitting}
                   className={`w-full py-4 border rounded-lg flex items-center justify-center gap-3 transition-all ${
                     voteValue === 'REJECT' 
                       ? 'bg-red-500 border-red-400 text-black font-black' 
                       : 'bg-white/5 border-white/10 text-gray-500 hover:border-red-500/50 hover:text-red-500'
                   } disabled:opacity-20`}
                 >
                   <XCircle className="w-4 h-4" /> 
                   <span className="text-xs uppercase tracking-widest">Reject Proof</span>
                 </button>
              </div>
           </div>

           <div className="pt-8">
              <button 
                onClick={handleSubmit}
                disabled={!voteValue || isSubmitting}
                className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.2em] hover:bg-amber-500 transition-all disabled:opacity-20 disabled:bg-gray-800 shadow-[0_0_20px_rgba(255,255,255,0.1)]"
              >
                {isSubmitting ? 'Signing...' : 'Broadcast Signature'}
              </button>
              <div className="mt-4 flex items-center justify-center gap-2 text-[8px] text-gray-700 font-bold uppercase tracking-widest">
                <Lock className="w-2.5 h-2.5" /> Multi-Sig Protection Active
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};

// --- v2.21: Dynamic Fee Calculator ---
const DynamicFeeCalculator = () => {
  const [baseFee, setBaseFee] = useState(5000);
  const [intuitionScore, setIntuitionScore] = useState(0); 
  
  const PROTOCOL_RATE = 0.20;
  const INSURANCE_RATE = 0.001;
  const INTUITION_MULTIPLIER = 0.05; 

  const protocolCut = Math.floor(baseFee * PROTOCOL_RATE);
  const insuranceLevy = Math.floor(baseFee * INSURANCE_RATE);
  const humanBase = baseFee - protocolCut - insuranceLevy;
  const tipAmount = Math.floor(humanBase * (intuitionScore * INTUITION_MULTIPLIER));
  const totalPayout = humanBase + tipAmount;

  return (
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col gap-6 shadow-2xl">
      <div className="flex justify-between items-center border-b border-white/10 pb-4">
        <h3 className="text-xs uppercase font-black text-white flex items-center gap-2 tracking-widest text-glow">
           <Percent className="w-4 h-4 text-green-500" /> Dynamic Settlement Engine
        </h3>
        <span className="text-[9px] bg-green-500/10 text-green-500 px-2 py-0.5 rounded font-black tracking-tighter">LIVE CALC</span>
      </div>

      <div className="grid grid-cols-2 gap-4">
         <div>
            <label className="text-[9px] text-gray-500 uppercase font-bold block mb-1">Task Base Fee (Sats)</label>
            <input 
              type="number" 
              value={baseFee}
              onChange={(e) => setBaseFee(Number(e.target.value))}
              className="w-full bg-black/40 border border-white/10 rounded p-2 text-xs text-white font-mono focus:border-green-500/50 outline-none"
            />
         </div>
         <div>
            <label className="text-[9px] text-gray-500 uppercase font-bold block mb-1">Intuition Score (0-10)</label>
            <input 
              type="range" 
              min="0" max="10" 
              value={intuitionScore}
              onChange={(e) => setIntuitionScore(Number(e.target.value))}
              className="w-full h-8 accent-green-500 cursor-pointer"
            />
            <div className="text-right text-[9px] text-green-500 font-bold">{intuitionScore > 0 ? `+${intuitionScore * 5}% BONUS` : 'STANDARD'}</div>
         </div>
      </div>

      <div className="space-y-3 pt-2">
         <div className="flex justify-between text-[10px] uppercase font-bold text-gray-400">
            <span>Human Net Earnings</span>
            <span className="text-white">{humanBase.toLocaleString()} Sats</span>
         </div>
         <div className="flex justify-between text-[10px] uppercase font-bold text-gray-400">
            <span>Protocol Treasury (20%)</span>
            <span className="text-amber-500">+{protocolCut.toLocaleString()} Sats</span>
         </div>
         <div className="flex justify-between text-[10px] uppercase font-bold text-gray-400">
            <span>Insurance Pool (0.1%)</span>
            <span className="text-blue-400">+{insuranceLevy.toLocaleString()} Sats</span>
         </div>
         <div className="flex justify-between text-[10px] uppercase font-bold text-gray-400 pt-2 border-t border-white/5">
            <span className="flex items-center gap-2"><Zap className="w-3 h-3 text-yellow-400" /> Keysend Tip (Intuition)</span>
            <span className="text-yellow-400">+{tipAmount.toLocaleString()} Sats</span>
         </div>
      </div>

      <div className="bg-green-500/10 border border-green-500/20 p-4 rounded text-center">
         <span className="text-[9px] text-green-600 uppercase font-black block mb-1 tracking-widest">Total Payout to Node</span>
         <span className="text-2xl font-black text-green-400 tracking-tight">{totalPayout.toLocaleString()} SATS</span>
      </div>
    </div>
  );
};

const InsuranceActuaryTab = ({ actuaryData, onAdjustRate, isAdjusting }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      {/* Loss Ratio Card */}
      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between shadow-xl">
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
          <div className="flex justify-between text-[10px] uppercase font-black font-bold">
            <span className="text-gray-500">Premium Revenue</span>
            <span className="text-green-500">+{actuaryData.total_premiums.toLocaleString()} SATS</span>
          </div>
          <div className="flex justify-between text-[10px] uppercase font-black font-bold">
            <span className="text-gray-500">Claims Paid</span>
            <span className="text-red-400">-{actuaryData.total_payouts.toLocaleString()} SATS</span>
          </div>
        </div>
      </div>

      {/* Dynamic Fee Calculator */}
      <DynamicFeeCalculator />

      {/* Tax Adjustment Controller */}
      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between shadow-xl">
        <div>
          <h3 className="text-xs uppercase font-black text-white mb-4">Tax Governance</h3>
          <p className="text-[10px] text-gray-500 leading-relaxed mb-6 font-bold tracking-tighter">
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
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8 shadow-2xl">
       <div className="flex justify-between items-center mb-8">
          <h3 className="text-xs uppercase font-black text-white flex items-center gap-3">
             <BarChart3 className="w-5 h-5 text-green-500" /> Reserve Growth vs Claims Volatility
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

const TreasuryTab = ({ treasuryStats, ledger }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="bg-green-500/5 border border-green-500/20 p-5 rounded-lg"><span className="text-[9px] text-green-400 uppercase font-black block mb-2 tracking-widest">Net Reserves</span><p className="text-2xl font-black text-white">{(treasuryStats.net_reserves / 1000000).toFixed(1)}M <span className="text-xs text-gray-500 font-normal">SATS</span></p></div>
      <div className="bg-blue-500/5 border border-blue-500/20 p-5 rounded-lg"><span className="text-[9px] text-blue-400 uppercase font-black block mb-2 tracking-widest">Insurance Pool</span><p className="text-2xl font-black text-white">{(treasuryStats.locked_insurance_pool / 1000000).toFixed(1)}M</p></div>
      <div className="bg-amber-500/5 border border-amber-500/20 p-5 rounded-lg"><span className="text-[9px] text-amber-400 uppercase font-black block mb-2 tracking-widest">Slash Revenue</span><p className="text-2xl font-black text-white">{(treasuryStats.slashing_revenue / 1000000).toFixed(1)}M</p></div>
      <div className="bg-red-500/5 border border-red-500/20 p-5 rounded-lg"><span className="text-[9px] text-red-400 uppercase font-black block mb-2 tracking-widest">Total Outflow</span><p className="text-2xl font-black text-white">{(treasuryStats.total_outflow / 1000000).toFixed(1)}M</p></div>
    </div>
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6">
      <h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3"><History className="w-5 h-5 text-blue-400" /> Transaction Ledger</h3>
      <div className="space-y-4">{ledger.map((tx) => (<div key={tx.id} className="flex items-center justify-between group transition-colors"><div className="flex items-center gap-4"><div className={`p-2 rounded bg-white/5 border border-white/10 ${tx.type === 'PAYOUT' ? 'text-red-400' : 'text-green-400'}`}>{tx.type === 'PAYOUT' ? <ArrowDownRight className="w-4 h-4" /> : <ArrowUpRight className="w-4 h-4" />}</div><div><span className="text-[10px] font-black text-white block mb-0.5">{tx.id}</span><span className="text-[8px] text-gray-600 uppercase font-bold">{tx.type} • {tx.timestamp}</span></div></div><span className={`text-xs font-black ${tx.type === 'PAYOUT' ? 'text-red-400' : 'text-green-500'}`}>{tx.type === 'PAYOUT' ? '-' : '+'}{tx.amount.toLocaleString()} SATS</span></div>))}</div>
    </div>
  </div>
);

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  const [isAdjustingActuary, setIsAdjustingActuary] = useState(false);
  
  const [nodeId, setNodeId] = useState("NODE_ELITE_X29");
  const [brownoutLevel, setBrownoutLevel] = useState('GREEN');

  // Data Buffers
  const [stats] = useState({ reputation: 982, staked_bond: 2000000, earned_fees: 45200, accuracy_rate: "98.2%", tier: "SUPER-ELITE" });
  const [actuaryData] = useState({ loss_ratio: 14.8, total_premiums: 50290100, total_payouts: 12500000, risk_sectors: [{ name: "LND Desync", prob: 0.12 }, { name: "Physical Theft", prob: 0.82 }] });
  const [treasuryStats] = useState({ total_inflow: 84290100, total_outflow: 12500000, slashing_revenue: 34000000, tax_revenue: 50290100, net_reserves: 71790100, locked_insurance_pool: 10450200 });
  const [ledger] = useState([ { id: "TX-99812", type: "SLASH", amount: 250000, timestamp: "2026-02-11 11:02", node: "NODE_MALICIOUS_X8", status: "CONFIRMED" }, { id: "TX-99811", type: "TAX", amount: 4200, timestamp: "2026-02-11 10:58", node: "NODE_ELITE_X29", status: "CONFIRMED" } ]);
  const [cases] = useState([ { id: "CASE-885-4", type: "SMS_VERIFICATION", status: "PENDING", timestamp: "2026-02-11 12:12:00", dispute_reason: "Agent claims code relay was incorrect.", reward: 500, evidence: { instructions: "Relay 6-digit code.", locked_blob_hash: "0x7a2e...f91c", decrypted_data: { raw_payload: "Proxy code: 882190" } } } ]);

  // Handlers
  const handleAdjustRate = () => { setIsAdjustingActuary(true); setTimeout(() => setIsAdjustingActuary(false), 2000); };
  const handleVoteSubmit = () => { setSelectedCase(null); };

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-gray-200 font-mono selection:bg-amber-500/30">
      <ProtocolHeader nodeId={nodeId} reserves={treasuryStats.net_reserves} brownoutLevel={brownoutLevel} />
      <div className="max-w-[1400px] mx-auto p-6 grid grid-cols-12 gap-6">
        <aside className="col-span-12 lg:col-span-3 space-y-4">
          <JudicialStanding stats={stats} />
          <nav className="space-y-1">
            {[{ id: 'cases', label: 'Open Disputes', icon: Activity, color: 'amber' }, { id: 'actuary', label: 'Insurance Actuary', icon: Calculator, color: 'blue' }, { id: 'treasury', label: 'Treasury Audit', icon: PiggyBank, color: 'green' }].map((tab) => (
              <button key={tab.id} onClick={() => { setActiveTab(tab.id); setSelectedCase(null); }} className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${activeTab === tab.id ? `bg-${tab.color}-500/10 text-${tab.color}-500 border border-${tab.color}-500/20 shadow-xl` : 'text-gray-500 hover:text-white hover:bg-white/5'}`}>
                <tab.icon className="w-4 h-4" /> {tab.label}
              </button>
            ))}
          </nav>
        </aside>
        <main className="col-span-12 lg:col-span-9">
          {activeTab === 'actuary' && <InsuranceActuaryTab actuaryData={actuaryData} onAdjustRate={handleAdjustRate} isAdjusting={isAdjustingActuary} />}
          {activeTab === 'treasury' && <TreasuryTab treasuryStats={treasuryStats} ledger={ledger} />}
          
          {activeTab === 'cases' && !selectedCase && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden animate-in fade-in duration-300 shadow-2xl">
              <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center text-glow">
                <h2 className="text-xs uppercase font-black tracking-widest flex items-center gap-2 text-amber-500">
                  <Activity className="w-4 h-4" /> Pending Case Docket
                </h2>
                <span className="text-[9px] text-gray-600 font-bold uppercase">Showing 1 Active Case</span>
              </div>
              <div className="divide-y divide-white/5">
                {cases.map((c) => (
                  <div key={c.id} className="p-6 flex items-center justify-between hover:bg-white/[0.01] transition-colors group">
                    <div className="flex items-center gap-6">
                      <div className="w-12 h-12 bg-amber-500/10 rounded border border-amber-500/20 flex items-center justify-center text-amber-500 group-hover:scale-105 transition-transform">
                        <Database className="w-6 h-6" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-white font-bold uppercase tracking-tighter">{c.id}</span>
                          <span className="text-[8px] bg-white/5 px-1.5 py-0.5 rounded text-gray-500 font-black uppercase">v2.2.2 Ready</span>
                        </div>
                        <p className="text-xs text-gray-500">{c.dispute_reason}</p>
                      </div>
                    </div>
                    <button 
                      onClick={() => setSelectedCase(c)} 
                      className="px-6 py-2 bg-amber-500/10 border border-amber-500/20 rounded text-[10px] font-black text-amber-500 uppercase tracking-widest hover:bg-amber-500 hover:text-black transition-all shadow-xl"
                    >
                      Enter Locker
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'cases' && selectedCase && (
            <div className="space-y-4">
               <button 
                 onClick={() => setSelectedCase(null)} 
                 className="text-[10px] text-gray-500 uppercase font-black hover:text-white flex items-center gap-2 transition-colors mb-2"
               >
                 &larr; Exit Evidence Locker
               </button>
               <EvidenceLockerView selectedCase={selectedCase} onVote={handleVoteSubmit} />
            </div>
          )}
        </main>
      </div>
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-[-1]" style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '30px 30px' }} />
    </div>
  );
};

export default App;
