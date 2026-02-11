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
        <h1 className="text-sm font-bold tracking-tighter text-white uppercase tracking-widest leading-none">Jury Tribunal v2.19</h1>
        <p className="text-[9px] text-amber-500/70 uppercase tracking-widest mt-1 text-glow">Node Density Audit Active</p>
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

// --- v2.19 NEW: Regional Node Density Tab ---
const RegionalDensityTab = ({ densityData }) => (
  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
    <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-8 flex flex-col items-center justify-center relative overflow-hidden shadow-2xl min-h-[300px]">
       <div className="absolute inset-0 opacity-[0.05]" style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '20px 20px' }} />
       <LayoutGrid className="w-16 h-16 text-amber-500/20 mb-4" />
       <h2 className="text-xl font-black text-white uppercase tracking-tighter mb-2">Physical Proximity Forensics</h2>
       <p className="text-xs text-gray-500 max-w-md text-center leading-relaxed">
          Nodes within the same /24 IP subnet or GPS radius (100m) are flagged for industrial bias. High density in non-urban areas indicates data-center farm activity.
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
              ? 'bg-amber-500/10 border border-amber-500/20 text-amber-200 shadow-[0_0_15px_rgba(245,158,11,0.05)]' 
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
            className="flex-1 bg-black border border-white/10 rounded p-2 text-xs text-white focus:outline-none focus:border-blue-500/50 transition-colors shadow-inner"
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
  const [isAdjustingActuary, setIsAdjustingActuary] = useState(false);
  const [isRotating, setIsRotating] = useState(false);
  const [isSigningTx, setIsSigningTx] = useState(false);
  const [isBroadcastingPIP, setIsBroadcastingPIP] = useState(false);
  
  const [nodeId, setNodeId] = useState("NODE_ELITE_X29");

  // Protocol State
  const [mempoolDepth] = useState(6402);
  const [brownoutLevel] = useState('GREEN');

  // v2.19 NEW: Density Data State
  const [densityData] = useState([
     { name: "Silicon Valley, CA", total_nodes: 142, bias: 8, entropy: "High", risk: "LOW", audit_summary: "Organic residential and office distribution." },
     { name: "Mumbai, India", total_nodes: 89, bias: 62, entropy: "Critical", risk: "HIGH", audit_summary: "Cluster of 42 nodes sharing a single tier-1 data center backbone." }
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

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-gray-200 font-mono selection:bg-amber-500/30">
      <ProtocolHeader nodeId={nodeId} reserves={treasuryStats.net_reserves} brownoutLevel={brownoutLevel} />

      <div className="max-w-[1400px] mx-auto p-6 grid grid-cols-12 gap-6">
        <aside className="col-span-12 lg:col-span-3 space-y-4">
          <JudicialStanding stats={stats} />
          <nav className="space-y-1">
            {[
              { id: 'cases', label: 'Open Disputes', icon: Activity, color: 'amber' },
              { id: 'density', label: 'Node Density', icon: LayoutGrid, color: 'orange' },
              { id: 'heatmap', label: 'Reputation Map', icon: Globe, color: 'green' },
              { id: 'liveness', label: 'Liveness Map', icon: HeartPulse, color: 'rose' },
              { id: 'treasury', label: 'Treasury Audit', icon: PiggyBank, color: 'emerald' },
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
              <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center text-glow">
                <h2 className="text-xs uppercase font-black tracking-widest flex items-center gap-2 text-amber-500"><Activity className="w-4 h-4" /> Pending Case Docket</h2>
              </div>
              <div className="divide-y divide-white/5">
                 {cases.map((c) => (
                    <div key={c.id} className="p-6 flex items-center justify-between hover:bg-white/[0.01] transition-colors group">
                       <div className="flex items-center gap-6"><div className="w-12 h-12 bg-amber-500/10 rounded border border-amber-500/20 flex items-center justify-center text-amber-500"><Database className="w-6 h-6" /></div><div><span className="text-white font-bold uppercase tracking-tighter">{c.id}</span><p className="text-xs text-gray-500">{c.dispute_reason}</p></div></div>
                       <button onClick={() => setSelectedCase(c)} className="px-6 py-2 bg-white/5 border border-white/10 rounded text-[10px] font-black uppercase tracking-widest hover:border-amber-500 hover:text-white transition-all shadow-xl">Enter Locker</button>
                    </div>
                 ))}
              </div>
            </div>
          )}

          {activeTab === 'density' && <RegionalDensityTab densityData={densityData} />}

          {selectedCase && (
             <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
                <button onClick={() => { setSelectedCase(null); setIsEvidenceUnlocked(false); }} className="text-xs text-gray-500 hover:text-white mb-2 flex items-center gap-2 font-black uppercase tracking-widest transition-colors"><ArrowRight className="w-3 h-3 rotate-180" /> Back to Docket</button>
                
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                   <div className="lg:col-span-4 space-y-6">
                      <div className="bg-[#0d0d0e] border border-white/10 rounded-lg p-6 shadow-xl">
                         <h3 className="text-xs font-black uppercase text-white mb-6 flex items-center gap-2"><Activity className="w-4 h-4 text-amber-500" /> Case Context</h3>
                         <div className="space-y-4 text-[10px]">
                            <div><span className="text-gray-600 block uppercase font-bold mb-1 text-glow">Instruction Log</span><p className="text-gray-400 leading-relaxed italic border-l-2 border-amber-500/20 pl-3">"{selectedCase.evidence.instructions}"</p></div>
                            <div className="pt-4 border-t border-white/5 flex justify-between font-black text-green-500 uppercase tracking-tighter"><span>Adjudication Reward</span><span>+{selectedCase.reward} SATS</span></div>
                         </div>
                      </div>
                      <MessageTunnel messages={messages} onSendMessage={handleSendMessage} newMessage={newMessage} setNewMessage={setNewMessage} />
                   </div>

                   <div className="lg:col-span-8 bg-[#0d0d0e] border border-white/10 rounded-lg overflow-hidden min-h-[500px] flex flex-col relative shadow-2xl">
                      <div className="p-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center"><h3 className="text-xs font-black tracking-widest text-white flex items-center gap-2 text-glow"><ShieldEllipsis className="w-5 h-5 text-amber-500" /> Secure Evidence Locker</h3><span className="text-[9px] text-gray-600 mono uppercase tracking-tighter">CID: {selectedCase.evidence.locked_blob_hash}</span></div>
                      <div className="flex-1 p-8 flex flex-col items-center justify-center bg-black/40 relative z-10">
                         {!isEvidenceUnlocked ? (
                            <div className="text-center max-w-sm">
                               <div className="w-16 h-16 bg-amber-500/10 rounded-full flex items-center justify-center border border-amber-500/20 mx-auto mb-6"><Fingerprint className={`w-8 h-8 text-amber-500 ${isDecrypting ? 'animate-pulse' : ''}`} /></div>
                               <h4 className="text-white font-bold uppercase mb-2 tracking-widest">Evidence Sealed</h4>
                               <p className="text-xs text-gray-500 mb-8 leading-relaxed font-bold tracking-tighter uppercase">High Court hardware signature required to zero-knowledge decrypt the biological proof blob.</p>
                               <button onClick={handleUnlockEvidence} disabled={isDecrypting} className="px-8 py-3 bg-amber-500/10 border border-amber-500/30 text-amber-500 text-[10px] font-black uppercase tracking-[0.2em] rounded-lg hover:bg-amber-500 hover:text-black transition-all shadow-2xl">{isDecrypting ? 'RSA-OAEP Handshake...' : 'Unlock Evidence'}</button>
                            </div>
                         ) : (
                            <div className="w-full h-full animate-in zoom-in-95 duration-500 grid grid-cols-1 md:grid-cols-2 gap-4">
                               <div className="p-6 bg-white/[0.02] border border-white/5 rounded-lg overflow-y-auto"><div className="flex items-center gap-2 mb-4 text-green-500"><FileCode className="w-4 h-4" /><span className="text-[9px] font-black uppercase tracking-widest">Decrypted Payload</span></div><pre className="text-[10px] text-gray-400 mono leading-relaxed">{JSON.stringify(selectedCase.evidence.decrypted_data, null, 2)}</pre></div>
                               <div className="space-y-4 flex flex-col">
                                  <div className="p-4 bg-green-500/5 border border-green-500/20 rounded"><span className="text-[9px] text-green-400 font-black uppercase block mb-1 font-bold">Hardware Attestation</span><p className="text-xs text-white">Silicon binding verified. Response generated within TEE environment.</p></div>
                                  <div className="p-4 bg-black/40 border border-white/5 rounded flex-1 flex flex-col gap-2"><span className="text-[9px] text-gray-600 font-black uppercase block mb-4 tracking-widest text-center">Cast Final Verdict</span><button onClick={() => handleVote('VALID')} disabled={isVoting} className="w-full py-3 mb-2 bg-green-500/10 border border-green-500/30 text-green-500 font-black text-[10px] uppercase tracking-widest hover:bg-green-500 hover:text-black transition-all">Verify Valid</button><button onClick={() => handleVote('FRAUD')} disabled={isVoting} className="w-full py-3 bg-red-500/10 border border-red-500/30 text-red-500 font-black text-[10px] uppercase tracking-widest hover:bg-red-500 hover:text-black transition-all">Verify Fraud</button></div>
                               </div>
                            </div>
                         )}
                      </div>
                   </div>
                </div>
             </div>
          )}

          {/* Fallback rendering for missing tabs (Stability check) */}
          {activeTab === 'treasury' && <div className="p-8 text-center text-gray-600 uppercase font-black text-[10px] tracking-widest">Treasury Audit Tab Refactoring...</div>}
        </main>
      </div>
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-[-1]" style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '30px 30px' }} />
    </div>
  );
};

export default App;
