import React, { useState, useEffect, useMemo } from 'react';
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
  ShieldHalf, Terminal, EyeOff, Info, ChevronLeft, XCircle as XClose
} from 'lucide-react';

/**
 * PROXY PROTOCOL - JURY TRIBUNAL PORTAL v3.1
 * "Standard: Monolithic Portal Standard (Zero External Dependencies)"
 * -------------------------------------------------------------------
 * Architecture:
 * - All components integrated into a single file for air-gapped auditability.
 * - Self-contained RSA-OAEP / SHA-256 evidence unsealing flow.
 * - Industrial Terminal aesthetic optimized for Raspberry Pi/Infineon nodes.
 */

// --- 1. CRYPTO PRIMITIVES (Audit-Ready) ---

const ProtocolCrypto = {
  /**
   * Simulates the unsealing of an evidence shard.
   * In production, this invokes the native TPM2_Unseal command via bridge.ts
   */
  async unsealEvidence(blob, nodeId) {
    console.log(`[TPM] Invoking RSA-OAEP unseal for identity ${nodeId}...`);
    // Simulated asymmetric decryption delay
    await new Promise(r => setTimeout(r, 2000));
    
    // In a real environment, this returns the decrypted plaintext object
    return {
      success: true,
      integrity_hash: "e3b0c442...98fc",
      attestation: "HARDWARE_SEALED_OK"
    };
  }
};

// --- 2. INTERNAL COMPONENTS (Monolithic Standard) ---

const ProtocolHeader = ({ nodeId, reserves, brownoutLevel }) => (
  <header className="border-b border-white/10 bg-[#0d0d0e] px-6 py-4 flex justify-between items-center sticky top-0 z-50">
    <div className="flex items-center gap-3">
      <div className="bg-amber-500/10 p-2 rounded border border-amber-500/20">
        <Gavel className="w-5 h-5 text-amber-500" />
      </div>
      <div>
        <h1 className="text-sm font-bold tracking-tighter text-white uppercase tracking-widest leading-none text-glow">Jury Tribunal v3.1</h1>
        <p className="text-[9px] text-amber-500/70 uppercase tracking-widest mt-1">High Court Protocol v3.1.0</p>
      </div>
    </div>
    
    <div className="flex items-center gap-6 text-[11px]">
      <div className="flex flex-col items-end hidden md:flex">
        <span className="text-gray-500 uppercase font-bold tracking-tighter text-[9px]">Status</span>
        <span className="text-green-500 flex items-center gap-1 font-bold">
          <ShieldCheck className="w-3 h-3" /> HIGH COURT ACTIVE
        </span>
      </div>
      <div className="h-8 w-px bg-white/10 hidden md:block" />
      <div className="flex flex-col items-end">
        <span className="text-gray-500 uppercase font-bold tracking-tighter text-[9px]">Treasury</span>
        <span className="text-white font-bold">{(reserves / 100000000).toFixed(4)} BTC</span>
      </div>
      <div className="flex items-center gap-2 bg-white/5 px-3 py-2 rounded border border-white/10">
        <div className={`w-2 h-2 rounded-full animate-pulse ${brownoutLevel === 'RED' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' : 'bg-green-500'}`} />
        <span className="text-white font-bold text-xs tracking-tighter">{nodeId}</span>
      </div>
    </div>
  </header>
);

const JudicialStanding = ({ stats }) => (
  <div className="bg-[#0d0d0e] border border-white/10 p-5 rounded-lg shadow-xl">
    <h3 className="text-[10px] uppercase text-gray-500 mb-4 font-black tracking-widest border-b border-white/5 pb-2">Judicial Standing</h3>
    <div className="space-y-4">
      <div className="flex justify-between items-center text-sm font-black">
        <span className="text-gray-400">Reputation</span>
        <span className="text-amber-500">{stats.reputation}/1000</span>
      </div>
      <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
        <div className="bg-amber-500 h-full" style={{ width: `${(stats.reputation / 1000) * 100}%` }} />
      </div>
      <div className="grid grid-cols-2 gap-2 pt-2">
        <div className="bg-white/5 p-3 rounded border border-white/5 text-center">
          <p className="text-[9px] text-gray-500 uppercase mb-1 font-bold tracking-tighter">Accuracy</p>
          <p className="text-sm font-bold text-white tracking-tighter">{stats.accuracy_rate}</p>
        </div>
        <div className="bg-white/5 p-3 rounded border border-white/5 text-center">
          <p className="text-[9px] text-gray-500 uppercase mb-1 font-bold tracking-tighter">Yield</p>
          <p className="text-sm font-bold text-green-500 tracking-tighter">+{stats.earned_fees} S</p>
        </div>
      </div>
    </div>
  </div>
);

const EvidenceLockerView = ({ selectedCase, onVote, nodeId }) => {
  const [isDecrypting, setIsDecrypting] = useState(false);
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [voteValue, setVoteValue] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleDecryption = async () => {
    setIsDecrypting(true);
    const result = await ProtocolCrypto.unsealEvidence(selectedCase.evidence.locked_blob, nodeId);
    if (result.success) {
      setIsDecrypting(false);
      setIsUnlocked(true);
    }
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
      <div className="bg-[#0d0d0e] border border-white/10 p-8 rounded-lg shadow-2xl flex flex-col md:flex-row justify-between items-start gap-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
          <Database className="w-32 h-32 text-white" />
        </div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-4">
             <span className="px-2 py-1 bg-amber-500/10 text-amber-500 text-[9px] font-black uppercase rounded border border-amber-500/20 tracking-widest">
               {selectedCase.type}
             </span>
             <span className="text-[10px] text-gray-600 font-bold uppercase tracking-tighter">DISPUTE_ID: {selectedCase.id}</span>
          </div>
          <h2 className="text-3xl font-black text-white tracking-tight uppercase mb-2">High Court Adjudication</h2>
          <p className="text-sm text-gray-500 flex items-center gap-2">
            <Clock className="w-3.5 h-3.5 text-amber-500" /> Convocation Window: <span className="text-white font-black">03h 42m LEFT</span>
          </p>
        </div>
        <div className="bg-black/40 border border-white/5 p-4 rounded text-right relative z-10">
           <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Potential Yield</span>
           <span className="text-xl font-black text-green-500 tracking-tighter">+{selectedCase.reward} SATS</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-[#0d0d0e] border border-white/10 rounded-xl overflow-hidden flex flex-col min-h-[500px] shadow-2xl">
          <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/[0.02] px-8">
            <h3 className="text-[10px] uppercase font-black text-white flex items-center gap-2">
              <Database className="w-3.5 h-3.5 text-indigo-500" /> Secure Evidence Shard
            </h3>
            <span className="text-[9px] text-indigo-400 font-black uppercase tracking-widest">SHA-256 // AES-GCM</span>
          </div>
          
          <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
            {!isUnlocked ? (
              <div className="max-w-md">
                <div className="w-20 h-20 bg-white/5 border border-white/10 rounded-full flex items-center justify-center mx-auto mb-8 shadow-inner group">
                  <Lock className={`w-8 h-8 ${isDecrypting ? 'text-amber-500 animate-pulse' : 'text-gray-700 group-hover:text-gray-500 transition-colors'}`} />
                </div>
                <h3 className="text-xl font-black text-white mb-4 uppercase tracking-tighter">Shard Encrypted</h3>
                <p className="text-xs text-gray-500 mb-10 leading-relaxed font-medium italic">
                  The evidence shard for {selectedCase.id} is unreadable until the local TPM performs a hardware unseal. This ensures zero-knowledge delivery to the jury.
                </p>
                <button 
                  onClick={handleDecryption}
                  disabled={isDecrypting}
                  className="w-full py-4 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-amber-500 transition-all flex items-center justify-center gap-3 shadow-xl disabled:opacity-50"
                >
                  {isDecrypting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Fingerprint className="w-4 h-4" />}
                  {isDecrypting ? 'Unsealing Shard...' : 'Invoke Hardware Unseal'}
                </button>
              </div>
            ) : (
              <div className="w-full h-full text-left space-y-10 animate-in fade-in zoom-in-95 duration-500">
                <div>
                  <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                    <ShieldAlert className="w-3.5 h-3.5 text-amber-500" /> Agent Instructions
                  </h4>
                  <div className="bg-black/60 border border-white/5 p-6 rounded-lg text-sm text-gray-300 italic font-medium leading-relaxed">
                    "{selectedCase.evidence.instructions}"
                  </div>
                </div>

                <div>
                  <h4 className="text-[10px] font-black text-gray-600 uppercase mb-4 tracking-widest flex items-center gap-2">
                    <Eye className="w-3.5 h-3.5 text-green-500" /> Forensic Proof Blob
                  </h4>
                  <div className="bg-black border border-white/5 p-6 rounded-lg mono text-xs text-green-500/70 break-all leading-relaxed max-h-60 overflow-y-auto font-mono">
                    {JSON.stringify(selectedCase.evidence.decrypted_data, null, 2)}
                  </div>
                </div>

                <div className="p-5 border border-indigo-500/20 bg-indigo-500/5 rounded-xl flex items-center gap-6 shadow-inner">
                   <ShieldCheck className="w-10 h-10 text-indigo-400" />
                   <div>
                     <p className="text-[11px] text-white font-black uppercase tracking-tighter">Hardware Attestation Verified</p>
                     <p className="text-[10px] text-gray-600 font-bold">SHA256 Manifest: {selectedCase.evidence.locked_blob_hash}</p>
                   </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="bg-[#0d0d0e] border border-white/10 rounded-xl p-8 shadow-2xl flex flex-col justify-between">
           <div>
              <h3 className="text-xs uppercase font-black text-white mb-8 border-b border-white/10 pb-4 flex items-center gap-2 tracking-widest">
                <Gavel className="w-4 h-4 text-amber-500" /> Final Verdict
              </h3>
              <p className="text-[10px] text-gray-500 leading-relaxed mb-10 font-bold italic">
                "By broadcasting this verdict, you commit to the Schelling Point. Dissenting from the majority consensus results in an immediate 600,000 SAT bond slash."
              </p>
              
              <div className="space-y-4">
                 <button 
                   onClick={() => setVoteValue('APPROVE')}
                   disabled={!isUnlocked || isSubmitting}
                   className={`w-full py-5 border rounded-xl flex items-center justify-center gap-4 transition-all ${
                     voteValue === 'APPROVE' 
                       ? 'bg-green-500 border-green-400 text-black font-black' 
                       : 'bg-white/5 border-white/10 text-gray-500 hover:border-green-500/50 hover:text-green-500'
                   } disabled:opacity-20`}
                 >
                   <CheckCircle2 className="w-5 h-5" /> 
                   <span className="text-xs font-black uppercase tracking-[0.2em]">Approve</span>
                 </button>

                 <button 
                   onClick={() => setVoteValue('REJECT')}
                   disabled={!isUnlocked || isSubmitting}
                   className={`w-full py-5 border rounded-xl flex items-center justify-center gap-4 transition-all ${
                     voteValue === 'REJECT' 
                       ? 'bg-red-500 border-red-400 text-black font-black' 
                       : 'bg-white/5 border-white/10 text-gray-500 hover:border-red-500/50 hover:text-red-500'
                   } disabled:opacity-20`}
                 >
                   <XCircle className="w-5 h-5" /> 
                   <span className="text-xs font-black uppercase tracking-[0.2em]">Reject</span>
                 </button>
              </div>
           </div>

           <div className="pt-10">
              <button 
                onClick={handleSubmit}
                disabled={!voteValue || isSubmitting}
                className="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.3em] hover:bg-amber-500 transition-all disabled:opacity-10 disabled:bg-gray-800 shadow-[0_0_30px_rgba(255,255,255,0.1)]"
              >
                {isSubmitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Finalize Decision'}
              </button>
              <div className="mt-6 flex items-center justify-center gap-3 text-[9px] text-gray-700 font-black uppercase tracking-widest">
                <ShieldCheck className="w-3.5 h-3.5 text-green-500" /> Multi-Sig Quorum Active
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};

// --- 3. THE MAIN PORTAL ---

const App = () => {
  const [activeTab, setActiveTab] = useState('cases');
  const [selectedCase, setSelectedCase] = useState(null);
  
  // Protocol State
  const [nodeId] = useState("NODE_ELITE_X29");
  const [reserves] = useState(71790100);
  const [stats] = useState({ reputation: 982, earned_fees: 45200, accuracy_rate: "98.2%" });
  
  // Case Data Buffer
  const [cases] = useState([
    { 
      id: "CASE-885-4", 
      type: "SMS_VERIFICATION", 
      dispute_reason: "Agent claims code relay was incorrect.", 
      reward: 500, 
      evidence: { 
        instructions: "Relay 6-digit code for Genesis Trading Bot.", 
        locked_blob_hash: "0x8A2E1C...F91C", 
        decrypted_data: { raw_payload: "Proxy code: 882190", timestamp: "2026-02-11T12:00:00Z", hub: "US_DE" } 
      } 
    }
  ]);

  return (
    <div className="min-h-screen bg-[#050506] text-gray-200 font-mono selection:bg-amber-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <ProtocolHeader nodeId={nodeId} reserves={reserves} brownoutLevel="GREEN" />

      <div className="max-w-[1400px] mx-auto p-6 md:p-10 grid grid-cols-12 gap-10 relative z-10">
        
        {/* Navigation Sidebar */}
        <aside className="col-span-12 lg:col-span-3 space-y-8">
          <JudicialStanding stats={stats} />
          
          <nav className="space-y-2">
            {[
              { id: 'cases', label: 'Active Docket', icon: Activity, color: 'amber' },
              { id: 'ledger', label: 'Audit Ledger', icon: History, color: 'blue' },
              { id: 'registry', label: 'Case Registry', icon: Archive, color: 'indigo' }
            ].map((tab) => (
              <button 
                key={tab.id} 
                onClick={() => { setActiveTab(tab.id); setSelectedCase(null); }} 
                className={`w-full flex items-center justify-between px-5 py-4 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${
                  activeTab === tab.id 
                    ? `bg-${tab.color}-500/10 text-${tab.color}-500 border border-${tab.color}-500/20 shadow-2xl` 
                    : 'text-gray-600 hover:text-white hover:bg-white/5'
                }`}
              >
                <div className="flex items-center gap-4">
                  <tab.icon className="w-4.5 h-4.5" /> 
                  <span>{tab.label}</span>
                </div>
                <ChevronRight className={`w-4 h-4 transition-transform ${activeTab === tab.id ? 'translate-x-1' : 'opacity-0'}`} />
              </button>
            ))}
          </nav>

          <div className="p-6 bg-indigo-500/5 border border-indigo-500/10 rounded-xl hidden lg:block shadow-inner">
             <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                <Info className="w-3.5 h-3.5" /> High Court Rule 4.2
             </h4>
             <p className="text-[11px] text-gray-500 leading-relaxed italic">
                "Evidence shards must be unsealed on local hardware. Direct cloud transmission of unencrypted evidence is a protocol violation."
             </p>
          </div>
        </aside>

        {/* Main Workspace */}
        <main className="col-span-12 lg:col-span-9">
          {activeTab === 'cases' && !selectedCase && (
            <div className="bg-[#0a0a0b] border border-white/10 rounded-xl overflow-hidden shadow-2xl animate-in fade-in duration-500">
              <div className="p-6 border-b border-white/5 bg-white/[0.02] flex justify-between items-center px-10">
                <h2 className="text-[11px] uppercase font-black tracking-[0.2em] flex items-center gap-3 text-amber-500">
                  <Activity className="w-4 h-4" /> Pending Case Docket
                </h2>
                <span className="text-[10px] text-gray-700 font-bold uppercase tracking-tighter">Showing 1 Record</span>
              </div>
              
              <div className="divide-y divide-white/5">
                {cases.map((c) => (
                  <div key={c.id} className="p-10 flex items-center justify-between hover:bg-white/[0.01] transition-all group">
                    <div className="flex items-center gap-10">
                      <div className="w-14 h-14 bg-amber-500/10 rounded-2xl border border-amber-500/20 flex items-center justify-center text-amber-500 group-hover:scale-105 transition-all shadow-inner">
                        <Database className="w-7 h-7" />
                      </div>
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-lg font-black text-white uppercase tracking-tighter">{c.id}</span>
                          <span className="text-[9px] bg-white/5 px-2 py-0.5 rounded text-gray-600 font-black uppercase tracking-widest border border-white/5">VRF_SUMMONS</span>
                        </div>
                        <p className="text-sm text-gray-500 font-medium">{c.dispute_reason}</p>
                      </div>
                    </div>
                    <button 
                      onClick={() => setSelectedCase(c)} 
                      className="px-8 py-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-[10px] font-black text-amber-500 uppercase tracking-widest hover:bg-amber-500 hover:text-black transition-all shadow-xl"
                    >
                      Enter Locker
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'cases' && selectedCase && (
            <div className="space-y-6">
               <button 
                 onClick={() => setSelectedCase(null)} 
                 className="text-[10px] text-gray-600 uppercase font-black hover:text-white flex items-center gap-2 transition-colors mb-4 group"
               >
                 <ChevronLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" /> Exit Evidence Locker
               </button>
               <EvidenceLockerView selectedCase={selectedCase} onVote={() => setSelectedCase(null)} nodeId={nodeId} />
            </div>
          )}

          {activeTab !== 'cases' && (
            <div className="h-[600px] border border-white/5 border-dashed rounded-2xl flex flex-col items-center justify-center text-center opacity-30 grayscale p-12">
               <Activity className="w-20 h-20 text-gray-800 mb-8 animate-pulse" />
               <h3 className="text-sm font-black text-gray-600 uppercase tracking-[0.3em] mb-3">Module Access Restricted</h3>
               <p className="text-xs text-gray-800 font-bold uppercase tracking-widest max-w-sm">Historical ledger and registry audits require an active High Court Quorum session.</p>
            </div>
          )}
        </main>
      </div>

      {/* Global Status Footer */}
      <footer className="max-w-[1400px] mx-auto mt-12 bg-[#0a0a0b] border border-white/5 rounded-xl p-5 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
               <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.4)]" />
               <span className="text-[10px] text-white font-black uppercase tracking-widest">Oracle Stream: SYNCHRONIZED</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[10px] text-gray-600 font-bold uppercase tracking-tighter">Settlement Block: 882932</span>
         </div>
         <div className="flex gap-10 text-[10px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] CHANNEL_STATE: OPTIMAL</span>
            <span>[*] HSM_STATUS: LOCKED</span>
            <span>[*] VERSION: v3.1.0</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
