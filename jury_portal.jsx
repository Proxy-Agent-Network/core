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

// --- MODULAR UI COMPONENTS ---

const ProtocolHeader = ({ nodeId, reserves, brownoutLevel }) => (
  <header className="border-b border-white/10 bg-[#0d0d0e] px-6 py-4 flex justify-between items-center sticky top-0 z-50">
    <div className="flex items-center gap-3">
      <div className="bg-amber-500/10 p-2 rounded border border-amber-500/20">
        <Gavel className="w-5 h-5 text-amber-500" />
      </div>
      <div>
        <h1 className="text-sm font-bold tracking-tighter text-white uppercase tracking-widest leading-none">Jury Tribunal v2.20</h1>
        <p className="text-[9px] text-amber-500/70 uppercase tracking-widest mt-1 text-glow">Proposal Forge Active</p>
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

// --- v2.20 NEW: Proposal Forge Dashboard ---
const ProposalForgeTab = ({ nodeId, onDraftSubmit, isBroadcasting }) => {
  const [draft, setDraft] = useState({
    title: "",
    category: "CORE",
    content: "# PIP ABSTRACT\n\nProvide a summary of the proposed protocol change...\n\n# MOTIVATION\n\nWhy is this change necessary?"
  });

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Editor Side */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden flex flex-col shadow-2xl">
            <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center">
              <h2 className="text-xs uppercase font-black tracking-widest flex items-center gap-2 text-white">
                <PenTool className="w-4 h-4 text-amber-500" /> Draft Proxy Improvement Proposal
              </h2>
              <span className="text-[9px] text-gray-600 uppercase font-bold tracking-tighter">Standard: RFC-PIP-V1</span>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <label className="text-[10px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Proposal Title</label>
                <input 
                  type="text" 
                  value={draft.title}
                  onChange={(e) => setDraft({...draft, title: e.target.value})}
                  placeholder="e.g., Increase Tier 3 Collateral to 2.5M SATS"
                  className="w-full bg-black border border-white/10 rounded p-3 text-sm text-white focus:outline-none focus:border-amber-500/50 transition-colors"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Category</label>
                  <select 
                    value={draft.category}
                    onChange={(e) => setDraft({...draft, category: e.target.value})}
                    className="w-full bg-black border border-white/10 rounded p-2 text-xs text-gray-300 focus:outline-none"
                  >
                    <option value="CORE">CORE PROTOCOL</option>
                    <option value="FEES">ECONOMIC FEES</option>
                    <option value="LEGAL">LEGAL HUB</option>
                    <option value="META">META GOVERNANCE</option>
                  </select>
                </div>
                <div>
                  <label className="text-[10px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Author ID</label>
                  <div className="bg-white/5 border border-white/10 rounded p-2 text-xs text-gray-500 mono truncate">
                    {nodeId}
                  </div>
                </div>
              </div>

              <div>
                <label className="text-[10px] text-gray-600 uppercase font-black block mb-2 tracking-widest">Specification (Markdown)</label>
                <textarea 
                  value={draft.content}
                  onChange={(e) => setDraft({...draft, content: e.target.value})}
                  className="w-full h-64 bg-black border border-white/10 rounded p-4 text-[11px] mono text-gray-400 focus:outline-none focus:border-amber-500/50 transition-colors resize-none leading-relaxed"
                />
              </div>
            </div>

            <div className="p-4 border-t border-white/10 bg-white/[0.01] flex justify-between items-center">
              <p className="text-[9px] text-gray-600 leading-tight italic max-w-sm">
                "Submitting a PIP consumes 5,000 SATS as an anti-spam levy. Proposals require a 66% majority to activate."
              </p>
              <button 
                onClick={() => onDraftSubmit(draft)}
                disabled={isBroadcasting || !draft.title}
                className="flex items-center gap-3 px-8 py-3 bg-amber-500/10 border border-amber-500/30 text-amber-500 text-[10px] font-black uppercase tracking-widest rounded-lg hover:bg-amber-500 hover:text-black transition-all disabled:opacity-30"
              >
                {isBroadcasting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                {isBroadcasting ? 'Broadcasting...' : 'Sign & Propose'}
              </button>
            </div>
          </div>
        </div>

        {/* History / Archive Side */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 flex flex-col shadow-xl">
            <h3 className="text-xs font-black uppercase text-white mb-6 flex items-center gap-3">
              <Archive className="w-4 h-4 text-gray-500" /> Active Proposals
            </h3>
            <div className="space-y-4">
              <div className="p-4 bg-white/5 border border-white/10 rounded-lg group cursor-pointer hover:border-amber-500/30 transition-all">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-[9px] text-amber-500 font-black tracking-widest uppercase">PIP-882</span>
                  <span className="text-[8px] bg-green-500/10 text-green-500 px-1.5 rounded uppercase font-bold">Voting</span>
                </div>
                <p className="text-[11px] font-bold text-white mb-1">Standardize Singapore Notary Seals</p>
                <div className="w-full bg-white/5 h-1 rounded-full mt-3 overflow-hidden">
                  <div className="bg-green-500 h-full" style={{ width: '74%' }} />
                </div>
              </div>
              
              <div className="p-4 bg-white/5 border border-white/10 rounded-lg opacity-50">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-[9px] text-gray-500 font-black tracking-widest uppercase">PIP-881</span>
                  <span className="text-[8px] bg-white/10 text-gray-400 px-1.5 rounded uppercase font-bold">Passed</span>
                </div>
                <p className="text-[11px] font-bold text-gray-300 mb-1 tracking-tighter">Implement Latency Jitter Proof v1.4</p>
              </div>
            </div>
          </div>

          <div className="p-6 bg-amber-500/5 border border-amber-500/10 rounded-lg flex items-start gap-4">
             <ShieldAlert className="w-5 h-5 text-amber-500 flex-shrink-0" />
             <p className="text-[10px] text-amber-200/40 leading-relaxed italic">
                "Proposing radical changes without community rough consensus in the Governance forum often leads to reputation decay."
             </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const RegionalDensityTab = ({ densityData }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8 flex flex-col items-center justify-center relative overflow-hidden shadow-2xl min-h-[300px]">
       <div className="absolute inset-0 opacity-[0.05]" style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '20px 20px' }} />
       <LayoutGrid className="w-16 h-16 text-amber-500/20 mb-4" />
       <h2 className="text-xl font-black text-white uppercase tracking-tighter mb-2">Physical Proximity Forensics</h2>
       <p className="text-xs text-gray-500 max-w-md text-center leading-relaxed">
          Nodes within the same /24 IP subnet or GPS radius (100m) are flagged for industrial bias. High density indicates data-center farm activity.
       </p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
       {densityData.map((region) => (
          <div key={region.name} className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 hover:bg-white/[0.01] transition-all">
             <div className="flex justify-between items-start mb-6">
                <div>
                   <span className="text-[10px] text-gray-600 font-black uppercase tracking-widest block mb-1">Jurisdiction Cluster</span>
                   <h3 className="text-lg font-black text-white uppercase tracking-tighter">{region.name}</h3>
                </div>
                <div className={`px-3 py-1 rounded text-[10px] font-black uppercase ${region.risk === 'HIGH' ? 'bg-red-500/10 text-red-500' : 'bg-green-500/10 text-green-500'}`}>
                   {region.risk} RISK
                </div>
             </div>
             
             <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-white/5 p-3 rounded border border-white/5">
                   <span className="text-[8px] text-gray-500 uppercase block mb-1">Total Nodes</span>
                   <span className="text-sm font-black text-white">{region.total_nodes}</span>
                </div>
                <div className="bg-white/5 p-3 rounded border border-white/5">
                   <span className="text-[8px] text-gray-500 uppercase block mb-1">DC Bias</span>
                   <span className={`text-sm font-black ${region.bias > 20 ? 'text-red-400' : 'text-green-400'}`}>{region.bias}%</span>
                </div>
                <div className="bg-white/5 p-3 rounded border border-white/5">
                   <span className="text-[8px] text-gray-500 uppercase block mb-1">Entropy</span>
                   <span className="text-sm font-black text-white">{region.entropy}</span>
                </div>
             </div>

             <div className="p-4 bg-black/40 border border-white/5 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-3">
                   <Focus className="w-4 h-4 text-gray-600" />
                   <p className="text-[10px] text-gray-400 italic">"{region.audit_summary}"</p>
                </div>
                <button className="text-[9px] font-black text-amber-500 uppercase hover:text-white">Audit IPs &rarr;</button>
             </div>
          </div>
       ))}
    </div>
  </div>
);

const MessageTunnel = ({ messages, onSendMessage, newMessage, setNewMessage }) => (
  <div className="bg-[#0d0d0e] border border-white/10 rounded-lg flex flex-col h-full shadow-2xl">
    <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center">
      <h3 className="text-xs font-black uppercase tracking-widest text-white flex items-center gap-2">
        <MessageSquare className="w-4 h-4 text-blue-400" /> Secure Message Tunnel
      </h3>
      <div className="flex items-center gap-2">
         <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
         <span className="text-[9px] text-green-500 mono uppercase font-black">E2EE Active</span>
      </div>
    </div>
    
    <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-black/40 min-h-[300px]">
      {messages.map((msg, i) => (
        <div key={i} className={`flex flex-col ${msg.sender === 'JUDGE' ? 'items-end' : 'items-start'}`}>
          <div className="flex items-center gap-2 mb-1">
             <span className="text-[8px] text-gray-600 mono">{msg.timestamp}</span>
             <span className={`text-[9px] font-black uppercase tracking-tighter ${msg.sender === 'JUDGE' ? 'text-amber-500' : 'text-blue-400'}`}>
                {msg.sender === 'JUDGE' ? 'SUPER-ELITE JUDGE' : 'AGENT_X_UPLINK'}
             </span>
          </div>
          <div className={`px-4 py-2 rounded-lg text-xs leading-relaxed max-w-[85%] ${
            msg.sender === 'JUDGE' 
              ? 'bg-amber-500/10 border border-amber-500/20 text-amber-200' 
              : 'bg-blue-500/10 border border-blue-500/20 text-blue-200'
          }`}>
            {msg.content}
          </div>
        </div>
      ))}
    </div>

    <div className="p-4 border-t border-white/10 bg-white/[0.01]">
       <div className="flex gap-2">
          <input 
            type="text" 
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onSendMessage()}
            placeholder="Send directive to Agent..."
            className="flex-1 bg-black border border-white/10 rounded p-2 text-xs text-white focus:outline-none focus:border-blue-500/50 transition-colors"
          />
          <button 
            onClick={onSendMessage}
            disabled={!newMessage.trim()}
            className="p-2 bg-blue-500/10 border border-blue-500/30 text-blue-400 rounded hover:bg-blue-500 hover:text-black transition-all disabled:opacity-20 shadow-lg"
          >
            <Send className="w-4 h-4" />
          </button>
       </div>
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
  const [isBroadcastingPIP, setIsBroadcastingPIP] = useState(false);
  
  const [nodeId, setNodeId] = useState("NODE_ELITE_X29");

  // Protocol State
  const [brownoutLevel] = useState('GREEN');

  // Density Data State
  const [densityData] = useState([
     { name: "Silicon Valley, CA", total_nodes: 142, bias: 8, entropy: "High", risk: "LOW", audit_summary: "Organic residential and office distribution." },
     { name: "Mumbai, India", total_nodes: 89, bias: 62, entropy: "Critical", risk: "HIGH", audit_summary: "Cluster sharing a single data center backbone." }
  ]);

  // Messaging State
  const [newMessage, setNewMessage] = useState("");
  const [messages, setMessages] = useState([
    { sender: "AGENT", content: "Tunnel established for CASE-885-4.", timestamp: "12:12:05" }
  ]);

  // Treasury State
  const [treasuryStats] = useState({
    total_inflow: 84290100,
    total_outflow: 12500000,
    slashing_revenue: 34000000,
    tax_revenue: 50290100,
    net_reserves: 71790100,
    locked_insurance_pool: 10450200
  });

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
        decrypted_data: { raw_payload: "Your Proxy code is: 882190", human_input: "882190", tpm_id: "OPTIGA_7721" }
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
    setTimeout(() => { setIsVoting(false); setSelectedCase(null); setIsEvidenceUnlocked(false); }, 1200);
  };

  const handleUnlockEvidence = () => {
    setIsDecrypting(true);
    setTimeout(() => { setIsDecrypting(false); setIsEvidenceUnlocked(true); }, 2000);
  };

  const handleSendMessage = () => {
    if (!newMessage.trim()) return;
    const msg = {
      sender: "JUDGE",
      content: newMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    };
    setMessages([...messages, msg]);
    setNewMessage("");
  };
