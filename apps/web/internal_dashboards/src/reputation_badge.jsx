import React, { useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  ShieldX, 
  Info, 
  Fingerprint, 
  Clock, 
  Lock,
  CheckCircle2,
  ExternalLink,
  ChevronRight,
  Binary
} from 'lucide-react';

/**
 * PROXY PROTOCOL - REPUTATION BADGE (v1.0)
 * "Verifiable trust, rendered in real-time."
 * ----------------------------------------------------
 * @param {number} score - 0 to 1000 Reputation Score
 * @param {string} nodeId - The ID of the node being verified
 * @param {object} attestation - The signed attestation object from the Oracle
 */

const ReputationBadge = ({ score = 500, nodeId = "NODE_UNKNOWN", attestation = null }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  // 1. Determine Tier and Color
  let tier = "PROBATION";
  let colorClass = "text-yellow-500 border-yellow-500/20 bg-yellow-500/5";
  let Icon = ShieldAlert;

  if (score >= 951) {
    tier = "SUPER-ELITE";
    colorClass = "text-amber-500 border-amber-500/30 bg-amber-500/10 shadow-[0_0_15px_rgba(245,158,11,0.2)]";
    Icon = ShieldCheck;
  } else if (score >= 801) {
    tier = "ELITE";
    colorClass = "text-indigo-400 border-indigo-400/20 bg-indigo-400/5";
    Icon = ShieldCheck;
  } else if (score >= 501) {
    tier = "VERIFIED";
    colorClass = "text-green-500 border-green-500/20 bg-green-500/5";
    Icon = ShieldCheck;
  } else if (score <= 300) {
    tier = "BANNED";
    colorClass = "text-red-500 border-red-500/30 bg-red-500/10";
    Icon = ShieldX;
  }

  return (
    <div className="relative inline-block font-mono">
      {/* Primary Badge */}
      <div 
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className={`flex items-center gap-2 px-3 py-1.5 border rounded-lg cursor-help transition-all duration-300 hover:scale-[1.02] ${colorClass}`}
      >
        <Icon className="w-4 h-4 animate-pulse" />
        <div className="flex flex-col">
          <span className="text-[10px] font-black uppercase tracking-tighter leading-none mb-0.5">{tier}</span>
          <div className="flex items-center gap-1.5">
            <span className="text-sm font-black tracking-tighter">{score}</span>
            <div className="w-12 h-1 bg-white/10 rounded-full overflow-hidden">
               <div className="h-full bg-current opacity-60" style={{ width: `${(score/1000)*100}%` }} />
            </div>
          </div>
        </div>
      </div>

      {/* Forensic Attestation Tooltip */}
      {showTooltip && (
        <div className="absolute top-full left-0 mt-3 w-80 bg-[#0a0a0a] border border-white/10 rounded-xl shadow-2xl p-5 z-[100] animate-in fade-in zoom-in-95 duration-200 backdrop-blur-md">
          <div className="flex justify-between items-start mb-4 border-b border-white/5 pb-3">
             <div>
                <h4 className="text-[10px] font-black text-white uppercase tracking-widest mb-1">Oracle Attestation</h4>
                <p className="text-[9px] text-gray-500 uppercase tracking-tighter">{nodeId}</p>
             </div>
             <CheckCircle2 className="w-4 h-4 text-green-500" />
          </div>

          <div className="space-y-4">
             <div className="flex items-start gap-3">
                <Clock className="w-3.5 h-3.5 text-gray-600 mt-0.5" />
                <div>
                   <span className="text-[9px] text-gray-600 font-bold uppercase block">Timestamp</span>
                   <span className="text-[10px] text-gray-300">{new Date().toISOString()}</span>
                </div>
             </div>

             <div className="flex items-start gap-3">
                <Fingerprint className="w-3.5 h-3.5 text-indigo-500 mt-0.5" />
                <div>
                   <span className="text-[9px] text-indigo-500 font-bold uppercase block">RSA-PSS Signature</span>
                   <code className="text-[9px] text-gray-500 break-all leading-tight">
                     {attestation?.signature || "0x8a2e1c...f91c3b...d2a1...e772"}
                   </code>
                </div>
             </div>

             <div className="flex items-start gap-3">
                <Binary className="w-3.5 h-3.5 text-amber-500 mt-0.5" />
                <div>
                   <span className="text-[9px] text-amber-500 font-bold uppercase block">Hardware Root</span>
                   <span className="text-[10px] text-gray-300">TPM 2.0 (Infineon OPTIGA)</span>
                </div>
             </div>
          </div>

          <div className="mt-5 pt-4 border-t border-white/5">
             <button className="w-full py-2 bg-white/5 border border-white/10 rounded text-[9px] font-black uppercase text-gray-400 hover:text-white hover:bg-white/10 transition-all flex items-center justify-center gap-2">
                <Lock className="w-3 h-3" /> Verify Oracle Root
             </button>
          </div>
        </div>
      )}
    </div>
  );
};

// --- Demo Wrapper for Preview ---
const App = () => {
  return (
    <div className="min-h-screen bg-[#050505] flex flex-col items-center justify-center gap-12 p-8">
      <div className="text-center space-y-2 mb-8">
        <h2 className="text-white font-black uppercase tracking-tighter text-2xl">Trust Primitives</h2>
        <p className="text-gray-500 text-xs tracking-widest uppercase">Hover badges to audit hardware signatures</p>
      </div>
      
      <div className="flex flex-wrap justify-center gap-8">
        <ReputationBadge score={982} nodeId="NODE_ELITE_X29" />
        <ReputationBadge score={845} nodeId="NODE_ALPHA_001" />
        <ReputationBadge score={542} nodeId="NODE_BETA_99" />
        <ReputationBadge score={210} nodeId="NODE_SUSPECT_01" />
      </div>

      <div className="max-w-md bg-white/5 border border-white/10 rounded-xl p-6 mt-12">
        <h3 className="text-white font-bold text-sm mb-4 flex items-center gap-2 uppercase">
          <Info className="w-4 h-4 text-indigo-400" /> Component Context
        </h3>
        <p className="text-xs text-gray-500 leading-relaxed mb-4">
          This React component is designed for multi-tenant dashboards. It serves as the primary visual link between the 
          <strong> Global Reputation Oracle</strong> and the user interface.
        </p>
        <div className="bg-black/50 p-3 rounded mono text-[10px] text-gray-400 leading-tight">
          &lt;ReputationBadge <br/>
          &nbsp;&nbsp;score={"{982}"} <br/>
          &nbsp;&nbsp;nodeId="NODE_ELITE_X29" <br/>
          /&gt;
        </div>
      </div>
    </div>
  );
};

export default App;
