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
  MessageSquare, User, LayoutGrid, Focus
} from 'lucide-react';

// --- 1. SHARED COMPONENTS ---

const ProtocolHeader = ({ nodeId, reserves, brownoutLevel }) => (
  <header className="border-b border-white/10 bg-[#0d0d0e] px-6 py-4 flex justify-between items-center sticky top-0 z-50">
    <div className="flex items-center gap-3">
      <div className="bg-amber-500/10 p-2 rounded border border-amber-500/20">
        <Gavel className="w-5 h-5 text-amber-500" />
      </div>
      <div>
        <h1 className="text-sm font-bold tracking-tighter text-white uppercase tracking-widest leading-none">Jury Tribunal v3.0</h1>
        <p className="text-[9px] text-amber-500/70 uppercase tracking-widest mt-1 text-glow">Master Governance Node</p>
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
        <div className={`w-2 h-2 rounded-full animate-pulse ${brownoutLevel === 'RED' ? 'bg-red-500' : 'bg-green-500'}`} />
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

// --- 2. TAB DEFINITIONS (MISSING IN PREVIOUS VERSION) ---

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

const InsuranceActuaryTab = ({ actuaryData, onAdjustRate, isAdjusting }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between">
        <div><span className="text-[10px] text-gray-600 uppercase font-black tracking-widest block mb-4">Loss Ratio (90d)</span><div className="flex items-baseline gap-2"><span className="text-4xl font-black text-white">{actuaryData.loss_ratio}%</span><span className={`text-[10px] font-bold ${actuaryData.loss_ratio < 20 ? 'text-green-500' : 'text-red-400'}`}>OPTIMAL</span></div></div>
        <div className="mt-6 space-y-2 text-[10px] uppercase font-bold text-gray-500"><div className="flex justify-between"><span>Revenue</span><span className="text-green-500">+{actuaryData.total_premiums.toLocaleString()} SATS</span></div><div className="flex justify-between"><span>Claims</span><span className="text-red-400">-{actuaryData.total_payouts.toLocaleString()} SATS</span></div></div>
      </div>
      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6"><h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3"><Calculator className="w-5 h-5 text-blue-400" /> Incident Probability</h3><div className="space-y-4">{actuaryData.risk_sectors.map((s) => (<div key={s.name}><div className="flex justify-between text-[10px] mb-2 uppercase font-black text-gray-400"><span>{s.name}</span><span className="text-white">{s.prob}%</span></div><div className="w-full bg-white/5 h-1 rounded-full overflow-hidden"><div className="bg-blue-500 h-full" style={{ width: `${s.prob * 10}%` }} /></div></div>))}</div></div>
      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col justify-between"><h3 className="text-xs uppercase font-black text-white mb-4">Tax Governance</h3><button onClick={() => onAdjustRate(0.0008)} disabled={isAdjusting} className="w-full py-3 bg-blue-500/10 border border-blue-500/30 text-blue-400 text-[10px] font-black uppercase tracking-widest rounded hover:bg-blue-400 hover:text-black transition-all">{isAdjusting ? 'Broadcasting...' : 'Adjust Rate'}</button></div>
    </div>
  </div>
);

const MultiSigSignerTab = ({ pendingTx, onSign, isSigning }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden shadow-2xl">
      <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center text-glow"><h2 className="text-xs uppercase font-black tracking-widest flex items-center gap-2 text-white"><Layers className="w-4 h-4 text-blue-400" /> Multi-Sig Quorum</h2><span className="text-[9px] text-gray-500 uppercase font-black tracking-tighter">Threshold: 2-of-3 Required</span></div>
      <div className="divide-y divide-white/5">{pendingTx.map((tx) => (<div key={tx.id} className="p-6 flex flex-col lg:flex-row justify-between gap-6 hover:bg-white/[0.01]"><div className="flex gap-6"><div className="w-14 h-14 bg-blue-500/10 rounded border border-blue-500/20 flex flex-col items-center justify-center"><Banknote className="w-6 h-6 text-blue-400" /></div><div className="space-y-2"><div className="flex items-center gap-3"><span className="text-sm font-black text-white uppercase">{tx.id}</span><span className="text-[9px] bg-white/5 px-2 py-0.5 rounded text-gray-400 uppercase font-bold tracking-tighter">{tx.type}</span></div><p className="text-xs text-gray-500 max-w-md leading-relaxed">{tx.description}</p><div className="flex items-center gap-4 pt-1"><span className="text-[9px] text-gray-600 mono truncate max-w-[200px]">TO: {tx.destination}</span><span className="text-[9px] text-blue-400 font-black uppercase">AMOUNT: {tx.amount.toLocaleString()} SATS</span></div></div></div><div className="flex items-center gap-6"><div className="flex flex-col items-end gap-2"><div className="flex gap-1">{[...Array(3)].map((_, i) => (<div key={i} className={`w-3 h-3 rounded-full border ${i < tx.sigs ? 'bg-green-500 border-green-500' : 'border-gray-800'}`} />))}</div><span className="text-[9px] text-gray-600 uppercase font-black">{tx.sigs}/3 Signatures</span></div><button onClick={() => onSign(tx.id)} disabled={isSigning || tx.signed_by_me} className={`px-6 py-3 rounded text-[10px] font-black uppercase ${tx.signed_by_me ? 'bg-green-500/10 text-green-500' : 'bg-blue-500/10 text-blue-400 hover:bg-blue-500 hover:text-black transition-all'}`}>{isSigning ? 'Signing...' : tx.signed_by_me ? 'Verified' : 'Affix Signature'}</button></div></div>))}</div>
    </div>
  </div>
);

const ProposalForgeTab = ({ nodeId, onDraftSubmit, isBroadcasting }) => {
  const [draft, setDraft] = useState({ title: "", content: "# Abstract\n\n..." });
  return (
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-400">
      <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center"><h2 className="text-xs uppercase font-black text-white flex items-center gap-2"><PenTool className="w-4 h-4 text-amber-500" /> Draft Proposal</h2></div>
      <div className="p-8 space-y-6"><input type="text" value={draft.title} onChange={(e) => setDraft({...draft, title: e.target.value})} placeholder="Proposal Title..." className="w-full bg-black border border-white/10 rounded p-4 text-sm text-white focus:outline-none focus:border-amber-500/50" /><textarea value={draft.content} onChange={(e) => setDraft({...draft, content: e.target.value})} className="w-full h-48 bg-black border border-white/10 rounded p-4 text-xs mono text-gray-400 focus:outline-none resize-none" /><button onClick={() => onDraftSubmit(draft)} disabled={isBroadcasting || !draft.title} className="w-full py-4 bg-amber-500/10 border border-amber-500/30 text-amber-500 text-[10px] font-black uppercase tracking-widest hover:bg-amber-500 hover:text-black transition-all">{isBroadcasting ? 'Broadcasting...' : 'Sign & Broadcast PIP'}</button></div>
    </div>
  );
};

const RegionalDensityTab = ({ densityData }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8 flex flex-col items-center justify-center relative overflow-hidden shadow-2xl min-h-[300px]">
       <div className="absolute inset-0 opacity-[0.05]" style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '20px 20px' }} />
       <LayoutGrid className="w-16 h-16 text-amber-500/20 mb-4" /><h2 className="text-xl font-black text-white uppercase tracking-tighter mb-2">Physical Proximity Forensics</h2>
       <p className="text-xs text-gray-500 max-w-md text-center leading-relaxed">Nodes within the same /24 IP subnet or GPS radius (100m) are flagged for industrial bias.</p>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
       {densityData.map((region) => (
          <div key={region.name} className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 hover:bg-white/[0.01] transition-all">
             <div className="flex justify-between items-start mb-6">
                <div><span className="text-[10px] text-gray-600 font-black uppercase tracking-widest block mb-1">Jurisdiction Cluster</span><h3 className="text-lg font-black text-white uppercase tracking-tighter">{region.name}</h3></div>
                <div className={`px-3 py-1 rounded text-[10px] font-black uppercase ${region.risk === 'HIGH' ? 'bg-red-500/10 text-red-500' : 'bg-green-500/10 text-green-500'}`}>{region.risk} RISK</div>
             </div>
             <div className="grid grid-cols-3 gap-4 mb-6"><div className="bg-white/5 p-3 rounded border border-white/5"><span className="text-[8px] text-gray-500 uppercase block mb-1">Total Nodes</span><span className="text-sm font-black text-white">{region.total_nodes}</span></div><div className="bg-white/5 p-3 rounded border border-white/5"><span className="text-[8px] text-gray-500 uppercase block mb-1">DC Bias</span><span className={`text-sm font-black ${region.bias > 20 ? 'text-red-400' : 'text-green-400'}`}>{region.bias}%</span></div><div className="bg-white/5 p-3 rounded border border-white/5"><span className="text-[8px] text-gray-500 uppercase block mb-1">Entropy</span><span className="text-sm font-black text-white">{region.entropy}</span></div></div>
             <div className="p-4 bg-black/40 border border-white/5 rounded-lg flex items-center justify-between"><div className="flex items-center gap-3"><Focus className="w-4 h-4 text-gray-600" /><p className="text-[10px] text-gray-400 italic">"{region.audit_summary}"</p></div><button className="text-[9px] font-black text-amber-500 uppercase hover:text-white">Audit IPs &rarr;</button></div>
          </div>
       ))}
    </div>
  </div>
);

const ReputationHeatmapTab = ({ regions }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-1">
      <div className="bg-black/60 rounded-lg h-[300px] relative overflow-hidden flex flex-col items-center justify-center border border-white/5">
        <div className="absolute inset-0 opacity-[0.07]" style={{ backgroundImage: 'radial-gradient(#00FF41 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
        <Globe className="w-16 h-16 text-gray-800 mb-4 opacity-40" />
        <h3 className="text-xs uppercase font-black text-gray-500 tracking-[0.6em] text-glow">Geospatial Integrity Grid</h3>
      </div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">{regions.map((r) => (<div key={r.name} className={`bg-[#0d0d0e] border rounded-lg p-5 group hover:bg-white/[0.01] ${r.status === 'CRITICAL' ? 'border-red-500/20' : 'border-white/10'}`}><div className="flex justify-between items-center mb-4"><span className="text-xs font-black text-white uppercase">{r.name}</span><span className={`text-[8px] font-black px-1.5 py-0.5 rounded ${r.status === 'HEALTHY' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>{r.status}</span></div><div className="text-2xl font-black text-white mb-1">{r.score}%</div><p className="text-[10px] text-gray-500 italic leading-tight">"{r.insight}"</p></div>))}</div>
  </div>
);

const LivenessHeatmapTab = ({ heartbeats }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-1">
      <div className="bg-black/60 rounded-lg h-[300px] relative overflow-hidden flex flex-col items-center justify-center border border-white/5">
        <div className="absolute inset-0 opacity-[0.1]" style={{ backgroundImage: 'linear-gradient(#f43f5e 1px, transparent 1px), linear-gradient(90deg, #f43f5e 1px, transparent 1px)', backgroundSize: '25px 25px' }} />
        <HeartPulse className="w-16 h-16 text-rose-500/20 mb-4 animate-pulse" />
        <h3 className="text-xs uppercase font-black text-gray-500 tracking-[0.6em] text-glow-red">Biological Pulse Grid</h3>
      </div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">{heartbeats.map((hb) => (<div key={hb.region} className="bg-[#0d0d0e] border border-white/10 rounded-lg p-5 group hover:border-rose-500/30 transition-all"><div className="flex justify-between items-center mb-4"><span className="text-[10px] text-gray-500 font-black uppercase">{hb.region}</span><div className={`w-2 h-2 rounded-full ${hb.status === 'ACTIVE' ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.4)]' : 'bg-amber-500'}`} /></div><div className="flex items-baseline gap-2 mb-2"><span className="text-2xl font-black text-white">{hb.count}</span><span className="text-[9px] text-gray-600 uppercase font-bold">Nodes</span></div><div className="flex items-center gap-4"><div className="flex-1 bg-white/5 h-1 rounded-full overflow-hidden"><div className="bg-rose-500 h-full animate-pulse" style={{ width: `${hb.intensity}%` }} /></div><span className="text-[9px] text-rose-400 font-bold">{hb.intensity}%</span></div></div>))}</div>
  </div>
);

const MessageTunnel = ({ messages, onSendMessage, newMessage, setNewMessage }) => (
  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg flex flex-col h-full shadow-2xl">
    <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center"><h3 className="text-xs font-black uppercase tracking-widest text-white flex items-center gap-2"><MessageSquare className="w-4 h-4 text-blue-400" /> Secure Message Tunnel</h3><div className="flex items-center gap-2"><span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" /><span className="text-[9px] text-green-500 mono uppercase font-black">E2EE Active</span></div></div>
    <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-black/40 min-h-[300px]">
      {messages.map((msg, i) => (
        <div key={i} className={`flex flex-col ${msg.sender === 'JUDGE' ? 'items-end' : 'items-start'}`}>
          <div className="flex items-center gap-2 mb-1"><span className="text-[8px] text-gray-600 mono">{msg.timestamp}</span><span className={`text-[9px] font-black uppercase tracking-tighter ${msg.sender === 'JUDGE' ? 'text-amber-500' : 'text-blue-400'}`}>{msg.sender === 'JUDGE' ? 'SUPER-ELITE JUDGE' : 'AGENT_X_UPLINK'}</span></div>
          <div className={`px-4 py-2 rounded-lg text-xs leading-relaxed max-w-[85%] ${msg.sender === 'JUDGE' ? 'bg-amber-500/10 border border-amber-500/20 text-amber-200' : 'bg-blue-500/10 border border-blue-500/20 text-blue-200'}`}>{msg.content}</div>
        </div>
      ))}
    </div>
    <div className="p-4 border-t border-white/10 bg-white/[0.01]">
       <div className="flex gap-2"><input type="text" value={newMessage} onChange={(e) => setNewMessage(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && onSendMessage()} placeholder="Send directive to Agent..." className="flex-1 bg-black border border-white/10 rounded p-2 text-xs text-white focus:outline-none focus:border-blue-500/50 transition-colors shadow-inner" /><button onClick={onSendMessage} disabled={!newMessage.trim()} className="p-2 bg-blue-500/10 border border-blue-500/30 text-blue-400 rounded hover:bg-blue-500 hover:text-black transition-all disabled:opacity-20 shadow-lg"><Send className="w-4 h-4" /></button></div>
    </div>
  </div>
);

// --- MAIN APP COMPONENT ---

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  const [isVoting, setIsVoting] = useState(false);
  const [isDecrypting, setIsDecrypting] = useState(false);
  const [isEvidenceUnlocked, setIsEvidenceUnlocked] = useState(false);
  const [isAdjustingActuary, setIsAdjustingActuary] = useState(false);
  const [isRotating, setIsRotating] = useState(false);
  const [isSigningTx, setIsSigningTx] = useState(false);
  const [isBroadcastingPIP, setIsBroadcastingPIP] = useState(false);
  
  const [nodeId, setNodeId] = useState("NODE_ELITE_X29");
  const [mempoolDepth] = useState(6402);
  const [brownoutLevel, setBrownoutLevel] = useState('GREEN');
  const [isManualOverride, setIsManualOverride] = useState(false);
  const [withdrawalState, setWithdrawalState] = useState('IDLE');
  const [isProcessingStake, setIsProcessingStake] = useState(false);
  const [cooldownDaysRemaining, setCooldownDaysRemaining] = useState(14);
  const [newMessage, setNewMessage] = useState("");
  const [keyRotationStep, setKeyRotationStep] = useState(0);

  // --- DATA BUFFERS ---
  const [stats] = useState({ reputation: 982, staked_bond: 2000000, earned_fees: 45200, accuracy_rate: "98.2%", tier: "SUPER-ELITE" });
  
  const [regionStats] = useState([
    { name: "North America", score: 98.4, status: "HEALTHY", insight: "Minimal jitter deviation detected." },
    { name: "Europe-West", score: 94.1, status: "HEALTHY", insight: "Organic node distribution aligned." },
    { name: "Asia-South", score: 64.2, status: "CRITICAL", insight: "Cluster of identical TPM versions." }
  ]);

  const [densityData] = useState([
     { name: "Silicon Valley, CA", total_nodes: 142, bias: 8, entropy: "High", risk: "LOW", audit_summary: "Organic residential distribution." },
     { name: "Mumbai, India", total_nodes: 89, bias: 62, entropy: "Critical", risk: "HIGH", audit_summary: "Cluster sharing single backbone." }
  ]);

  const [pendingTx, setPendingTx] = useState([
    { id: "MSIG-4421", type: "BOND_RELEASE", description: "Node Alpha 002 exit.", sigs: 1, amount: 2000000, destination: "bc1q...", signed_by_me: false }
  ]);

  const [actuaryData] = useState({
    loss_ratio: 14.8, total_premiums: 50290100, total_payouts: 12500000,
    risk_sectors: [{ name: "LND Desync", prob: 0.12 }, { name: "Physical Theft", prob: 0.82 }]
  });

  const [treasuryStats] = useState({
    total_inflow: 84290100, total_outflow: 12500000, slashing_revenue: 34000000, tax_revenue: 50290100, net_reserves: 71790100, locked_insurance_pool: 10450200
  });

  const [ledger] = useState([
    { id: "TX-99812", type: "SLASH", amount: 250000, timestamp: "2026-02-11 11:02", node: "NODE_MALICIOUS_X8", status: "CONFIRMED" },
    { id: "TX-99811", type: "TAX", amount: 4200, timestamp: "2026-02-11 10:58", node: "NODE_ELITE_X29", status: "CONFIRMED" }
  ]);

  const [cases] = useState([
    { id: "CASE-885-4", type: "SMS_VERIFICATION", status: "PENDING", timestamp: "2026-02-11 12:12:00", dispute_reason: "Agent claims code relay was incorrect.", reward: 500, evidence: { instructions: "Relay 6-digit code.", locked_blob_hash: "0x7a2e...f91c", decrypted_data: { raw_payload: "Proxy code: 882190" } } }
  ]);

  const [messages, setMessages] = useState([
    { sender: "AGENT", content: "Tunnel established for CASE-885-4.", timestamp: "12:12:05" }
  ]);

  const [livenessHeartbeats] = useState([
    { region: "US_EAST", count: 442, intensity: 98, status: "ACTIVE" },
    { region: "ASIA_S", count: 128, intensity: 42, status: "DEGRADED" }
  ]);

  // Handlers
  const handleVote = () => { setIsVoting(true); setTimeout(() => { setIsVoting(false); setSelectedCase(null); setIsEvidenceUnlocked(false); }, 1200); };
  const handleSignTx = (txId) => { setIsSigningTx(true); setTimeout(() => { setPendingTx(prev => prev.map(tx => tx.id === txId ? { ...tx, sigs: tx.sigs + 1, signed_by_me: true } : tx)); setIsSigningTx(false); }, 2000); };
  const handlePIPBroadcast = () => { setIsBroadcastingPIP(true); setTimeout(() => { setIsBroadcastingPIP(false); setActiveTab('cases'); }, 3000); };
  const handleAdjustRate = () => { setIsAdjustingActuary(true); setTimeout(() => setIsAdjustingActuary(false), 2000); };
  const initiateWithdrawal = () => { setIsProcessingStake(true); setTimeout(() => { setWithdrawalState('COOLING_OFF'); setIsProcessingStake(false); }, 1500); };
  const startKeyRotation = () => { setIsRotating(true); setTimeout(() => { setNodeId(`NODE_ELITE_${Math.random().toString(36).substring(7).toUpperCase()}`); setIsRotating(false); }, 3000); };
  
  const handleSendMessage = () => {
    if (!newMessage.trim()) return;
    setMessages([...messages, { sender: "JUDGE", content: newMessage, timestamp: "Now" }]);
    setNewMessage("");
  };

  const handleUnlockEvidence = () => {
    setIsDecrypting(true);
    setTimeout(() => { setIsDecrypting(false); setIsEvidenceUnlocked(true); }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-gray-200 font-mono selection:bg-amber-500/30">
      <ProtocolHeader nodeId={nodeId} reserves={treasuryStats.net_reserves} brownoutLevel={brownoutLevel} />

      <div className="max-w-[1400px] mx-auto p-6 grid grid-cols-12 gap-6">
        <aside className="col-span-12 lg:col-span-3 space-y-4">
          <JudicialStanding stats={stats} />
          <nav className="space-y-1">
            {[
              { id: 'cases', label: 'Open Disputes', icon: Activity, color: 'amber' },
              { id: 'treasury', label: 'Treasury Audit', icon: PiggyBank, color: 'green' },
              { id: 'multisig', label: 'Multi-Sig Sign', icon: CheckSquare, color: 'blue' },
              { id: 'actuary', label: 'Insurance Actuary', icon: Calculator, color: 'blue' },
              { id: 'forge', label: 'Proposal Forge', icon: FilePlus, color: 'purple' },
              { id: 'heatmap', label: 'Reputation Map', icon: Globe, color: 'green' },
              { id: 'density', label: 'Node Density', icon: LayoutGrid, color: 'orange' },
              { id: 'liveness', label: 'Liveness Map', icon: HeartPulse, color: 'rose' },
              { id: 'staking', label: 'Stake Manager', icon: Wallet, color: 'emerald' },
              { id: 'brownout', label: 'Traffic Control', icon: Waves, color: 'orange' },
              { id: 'security', label: 'Hardware Sec', icon: Cpu, color: 'blue' }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button 
                  key={tab.id}
                  onClick={() => { setActiveTab(tab.id); setSelectedCase(null); }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm font-bold transition-all ${
                    activeTab === tab.id 
                      ? `bg-${tab.color}-500/10 text-${tab.color}-500 border border-${tab.color}-500/20 shadow-xl` 
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
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden animate-in fade-in duration-300 shadow-2xl">
              <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center text-glow"><h2 className="text-xs uppercase font-black tracking-widest flex items-center gap-2 text-amber-500"><Activity className="w-4 h-4" /> Pending Case Docket</h2></div>
              <div className="divide-y divide-white/5">{cases.map((c) => (<div key={c.id} className="p-6 flex items-center justify-between hover:bg-white/[0.01] transition-colors group"><div className="flex items-center gap-6"><div className="w-12 h-12 bg-amber-500/10 rounded border border-amber-500/20 flex items-center justify-center text-amber-500 group-hover:scale-105 transition-transform"><Database className="w-6 h-6" /></div><div><span className="text-white font-bold uppercase tracking-tighter">{c.id}</span><p className="text-xs text-gray-500">{c.dispute_reason}</p></div></div><button onClick={() => setSelectedCase(c)} className="px-6 py-2 bg-white/5 border border-white/10 rounded text-[10px] font-black uppercase tracking-widest hover:border-amber-500 hover:text-white transition-all shadow-xl">Enter Locker</button></div>))}</div>
            </div>
          )}

          {activeTab === 'treasury' && <TreasuryTab treasuryStats={treasuryStats} ledger={ledger} />}
          {activeTab === 'actuary' && <InsuranceActuaryTab actuaryData={actuaryData} onAdjustRate={handleAdjustRate} isAdjusting={isAdjustingActuary} />}
          {activeTab === 'multisig' && <MultiSigSignerTab pendingTx={pendingTx} onSign={handleSignTx} isSigning={isSigningTx} />}
          {activeTab === 'heatmap' && <ReputationHeatmapTab regions={regionStats} />}
          {activeTab === 'density' && <RegionalDensityTab densityData={densityData} />}
          {activeTab === 'liveness' && <LivenessHeatmapTab heartbeats={livenessHeartbeats} />}
          {activeTab === 'forge' && <ProposalForgeTab nodeId={nodeId} onDraftSubmit={handlePIPBroadcast} isBroadcasting={isBroadcastingPIP} />}

          {/* Fallback for simple tabs (Brownout, Staking, Security) to ensure no crash */}
          {activeTab === 'brownout' && (
             <div className="bg-[#0d0d0e] border border-orange-500/20 rounded-lg p-6">
                <span className="text-[10px] text-gray-600 uppercase font-black block mb-4 tracking-widest text-glow">Congestion Level</span>
                <div className="flex items-center gap-3"><div className={`w-3 h-3 rounded-full animate-pulse ${brownoutLevel === 'GREEN' ? 'bg-green-500' : 'bg-red-500'}`} /><span className="text-2xl font-black text-white uppercase">{brownoutLevel}</span></div>
             </div>
          )}
          {activeTab === 'staking' && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8 shadow-2xl">
              <h3 className="text-xs uppercase font-black text-white mb-6 flex items-center gap-3"><Lock className="w-5 h-5 text-green-500" /> Locked Collateral</h3>
              <div className="flex items-baseline gap-2 font-black text-white mb-8"><span className="text-4xl">{(stats.staked_bond / 1000000).toFixed(2)}</span><span className="text-sm font-bold text-gray-500 uppercase tracking-widest">M SATS</span></div>
              <button onClick={initiateWithdrawal} disabled={isProcessingStake} className="w-full py-4 bg-red-500/5 border border-red-500/20 rounded-lg text-[10px] font-black uppercase tracking-[0.2em]">{isProcessingStake ? 'Processing...' : 'Request Release'}</button>
            </div>
          )}
          {activeTab === 'security' && (
            <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8 shadow-xl">
               <h3 className="text-xs uppercase font-black tracking-widest text-white flex items-center gap-3 mb-8"><Key className="w-5 h-5 text-blue-400" /> TPM 2.0 Identity</h3>
               <div className="bg-black/60 p-4 border border-white/5 rounded mono text-[11px] text-blue-300 break-all mb-6">0x81010001:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd</div>
               <button onClick={startKeyRotation} disabled={isRotating} className="w-full py-4 bg-blue-500/5 border border-blue-500/10 rounded-lg flex items-center justify-center gap-3"><RefreshCw className={`w-4 h-4 text-blue-400 ${isRotating ? 'animate-spin' : ''}`} /><span className="text-xs font-black uppercase text-blue-400 tracking-widest">{isRotating ? 'Rotating...' : 'Rotate Handle'}</span></button>
            </div>
          )}

          {selectedCase && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
                <button onClick={() => { setSelectedCase(null); setIsEvidenceUnlocked(false); }} className="text-xs text-gray-500 hover:text-white mb-2 flex items-center gap-2 font-black uppercase tracking-widest transition-colors"><ArrowRight className="w-3 h-3 rotate-180" /> Back to Docket</button>
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                   <div className="lg:col-span-4 space-y-6">
                      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 shadow-xl"><h3 className="text-xs font-black uppercase text-white mb-6 flex items-center gap-2"><Activity className="w-4 h-4 text-amber-500" /> Case Context</h3><div className="space-y-4 text-[10px]"><div><span className="text-gray-600 block uppercase font-bold mb-1 text-glow">Instruction Log</span><p className="text-gray-400 leading-relaxed italic border-l-2 border-amber-500/20 pl-3">"{selectedCase.evidence.instructions}"</p></div></div><MessageTunnel messages={messages} onSendMessage={handleSendMessage} newMessage={newMessage} setNewMessage={setNewMessage} /></div>
                   </div>
                   <div className="lg:col-span-8 bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden min-h-[500px] flex flex-col relative shadow-2xl">
                      <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center"><h3 className="text-xs font-black tracking-widest text-white flex items-center gap-2 text-glow"><ShieldEllipsis className="w-5 h-5 text-amber-500" /> Secure Evidence Locker</h3></div>
                      <div className="flex-1 p-8 flex flex-col items-center justify-center bg-black/40 relative z-10">
                         {!isEvidenceUnlocked ? (
                            <div className="text-center max-w-sm"><Fingerprint className={`w-16 h-16 text-amber-500 mx-auto mb-6 ${isDecrypting ? 'animate-pulse' : ''}`} /><h4 className="text-white font-bold uppercase mb-2 tracking-widest">Evidence Sealed</h4><button onClick={handleUnlockEvidence} disabled={isDecrypting} className="px-8 py-3 bg-amber-500/10 border border-amber-500/30 text-amber-500 text-[10px] font-black uppercase tracking-[0.2em] rounded-lg hover:bg-amber-500 hover:text-black transition-all shadow-2xl">{isDecrypting ? 'Decrypting...' : 'Unlock Evidence'}</button></div>
                         ) : (
                            <div className="w-full h-full animate-in zoom-in-95 duration-500 grid grid-cols-1 md:grid-cols-2 gap-4"><div className="p-6 bg-white/[0.02] border border-white/5 rounded-lg overflow-y-auto shadow-inner"><FileCode className="w-4 h-4 text-green-500 mb-4" /><pre className="text-[10px] text-gray-400 mono leading-relaxed">{JSON.stringify(selectedCase.evidence.decrypted_data, null, 2)}</pre></div><div className="space-y-4 flex flex-col"><div className="p-4 bg-green-500/5 border border-green-500/20 rounded text-xs text-white">Hardware Attestation Valid.</div><div className="p-4 bg-black/40 border border-white/5 rounded flex-1 flex flex-col gap-2"><button onClick={handleVote} disabled={isVoting} className="w-full py-3 mb-2 bg-green-500/10 border border-green-500/30 text-green-500 font-black text-[10px] uppercase tracking-widest hover:bg-green-500 hover:text-black transition-all">Verify Valid</button><button onClick={handleVote} disabled={isVoting} className="w-full py-3 bg-red-500/10 border border-red-500/30 text-red-500 font-black text-[10px] uppercase tracking-widest hover:bg-red-500 hover:text-black transition-all">Verify Fraud</button></div></div></div>
                         )}
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
