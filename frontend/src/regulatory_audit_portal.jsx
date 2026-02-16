import React, { useState, useCallback } from 'react';
import { 
  ShieldCheck, 
  UploadCloud, 
  FileSearch, 
  Binary, 
  CheckCircle2, 
  ShieldAlert, 
  Lock, 
  RefreshCw, 
  ChevronRight, 
  Download, 
  ExternalLink, 
  Gavel, 
  Fingerprint, 
  Layers, 
  Clock, 
  Activity, 
  Info,
  XCircle,
  Briefcase,
  FileCheck2,
  Trash2,
  ArrowRight
} from 'lucide-react';

/**
 * PROXY PROTOCOL - REGULATORY AUDIT PORTAL (v1.0)
 * "Mathematical proof of network-wide evidence destruction."
 * ----------------------------------------------------
 */

const App = () => {
  const [manifest, setManifest] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  // Simulation: Standard manifest structure from compliance_export_api.py
  const mockValidManifest = {
    export_id: "EXP-EPOCH_88293-1707684000",
    epoch_id: "EPOCH_88293",
    timestamp: 1707684000,
    certificate_count: 142,
    batch_state_root: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    policy: "24H_SCRUB_ENFORCED",
    foundation_signature: "0x8a2e1c...f91c3b2e...d2a1...e772"
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file) => {
    setIsVerifying(true);
    // Simulate parsing and cryptographic verification of the batch signature
    setTimeout(() => {
      setManifest(mockValidManifest);
      setVerificationResult({
        isValid: true,
        trustLevel: "FOUNDATION_HSM_VERIFIED",
        auditTimestamp: new Date().toISOString()
      });
      setIsVerifying(false);
    }, 2000);
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-emerald-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-5xl w-full relative z-10 space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl shadow-2xl">
              <ShieldCheck className="w-8 h-8 text-emerald-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Regulatory Portal</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                External Audit Desk // Vaporization Verification // Protocol <span className="text-emerald-500">v3.1.9</span>
              </p>
            </div>
          </div>
          <div className="bg-white/5 border border-white/10 px-4 py-2 rounded-lg flex items-center gap-3">
             <Briefcase className="w-4 h-4 text-gray-500" />
             <span className="text-[10px] text-gray-400 font-black uppercase tracking-widest leading-none">Auditor Role: JURISDICTIONAL_AGENT</span>
          </div>
        </header>

        {!manifest ? (
          <div className="space-y-8 animate-in fade-in duration-700">
             {/* Upload Zone */}
             <div 
               onDragOver={onDragOver}
               onDragLeave={onDragLeave}
               onDrop={onDrop}
               className={`border-2 border-dashed rounded-3xl p-20 text-center transition-all duration-300 flex flex-col items-center justify-center gap-6 cursor-pointer ${
                 isDragging ? 'bg-emerald-500/5 border-emerald-500/50 scale-[1.02]' : 'bg-[#0a0a0a] border-white/10 hover:border-white/20'
               }`}
             >
                {isVerifying ? (
                   <>
                      <div className="relative">
                         <RefreshCw className="w-16 h-16 text-emerald-500 animate-spin" />
                         <Lock className="w-6 h-6 text-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                      </div>
                      <h2 className="text-xl font-black text-white uppercase tracking-tighter">Verifying HSM Signatures</h2>
                      <p className="text-xs text-gray-500 max-w-xs leading-relaxed italic">
                        Re-calculating Merkle State Root for 142 destruction certificates...
                      </p>
                   </>
                ) : (
                   <>
                      <div className="p-6 bg-white/5 rounded-full border border-white/10 group-hover:scale-110 transition-transform">
                         <UploadCloud className="w-12 h-12 text-gray-600" />
                      </div>
                      <div>
                         <h2 className="text-xl font-black text-white uppercase tracking-tighter mb-2">Drop Export Manifest</h2>
                         <p className="text-xs text-gray-500 uppercase tracking-widest font-bold">JSON Archive // Minimum 256-bit Entropy</p>
                      </div>
                      <input 
                        type="file" 
                        id="manifest-upload" 
                        className="hidden" 
                        onChange={handleFileUpload} 
                        accept=".json"
                      />
                      <label 
                        htmlFor="manifest-upload"
                        className="px-10 py-3 bg-white text-black font-black text-[10px] uppercase tracking-widest rounded-lg hover:bg-emerald-500 hover:text-white transition-all shadow-xl cursor-pointer"
                      >
                         Select Manifest File
                      </label>
                   </>
                )}
             </div>

             {/* Instructional Grid */}
             <div className="grid grid-cols-1 md:grid-cols-3 gap-6 opacity-60">
                <div className="p-6 bg-[#0a0a0a] border border-white/5 rounded-xl flex items-start gap-4">
                   <Lock className="w-5 h-5 text-indigo-500 shrink-0" />
                   <div>
                      <p className="text-[10px] text-white font-black uppercase mb-1">E2EE Integrity</p>
                      <p className="text-[9px] text-gray-600 leading-relaxed">Manifests are encrypted with the Regulatory Public Key before export from the Foundation Hub.</p>
                   </div>
                </div>
                <div className="p-6 bg-[#0a0a0a] border border-white/5 rounded-xl flex items-start gap-4">
                   <Binary className="w-5 h-5 text-emerald-500 shrink-0" />
                   <div>
                      <p className="text-[10px] text-white font-black uppercase mb-1">State Root Hash</p>
                      <p className="text-[9px] text-gray-600 leading-relaxed">The batch root proves the presence of every Destruction Certificate without revealing individual task metadata.</p>
                   </div>
                </div>
                <div className="p-6 bg-[#0a0a0a] border border-white/5 rounded-xl flex items-start gap-4">
                   <Gavel className="w-5 h-5 text-amber-500 shrink-0" />
                   <div>
                      <p className="text-[10px] text-white font-black uppercase mb-1">Legal Finality</p>
                      <p className="text-[9px] text-gray-600 leading-relaxed">Verified manifests provide programmatic proof of GDPR Compliance for the "Right to be Forgotten" policy.</p>
                   </div>
                </div>
             </div>
          </div>
        ) : (
          <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
             
             {/* Verification Hero */}
             <div className="bg-[#0a0a0a] border-2 border-emerald-500/30 rounded-3xl p-10 shadow-[0_0_50px_rgba(16,185,129,0.05)] relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-[0.03]">
                   <ShieldCheck className="w-64 h-64 text-white" />
                </div>

                <div className="flex flex-col md:flex-row justify-between items-start gap-8 relative z-10">
                   <div className="flex-1 space-y-6">
                      <div className="flex items-center gap-4">
                         <div className="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center border border-emerald-500/40">
                            <FileCheck2 className="w-6 h-6 text-emerald-500" />
                         </div>
                         <div>
                            <span className="text-[10px] text-emerald-500 font-black uppercase tracking-[0.2em] block mb-0.5">HSM Audit Result</span>
                            <h2 className="text-3xl font-black text-white tracking-tighter uppercase">Manifest Authenticated</h2>
                         </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                         <div className="p-4 bg-black border border-white/5 rounded-xl">
                            <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Target Epoch</span>
                            <span className="text-sm font-black text-white uppercase tracking-widest">{manifest.epoch_id}</span>
                         </div>
                         <div className="p-4 bg-black border border-white/5 rounded-xl">
                            <span className="text-[9px] text-gray-600 uppercase font-black block mb-1">Scrub Policy</span>
                            <span className="text-sm font-black text-indigo-400 uppercase tracking-widest">{manifest.policy}</span>
                         </div>
                      </div>

                      <div className="p-5 bg-emerald-500/5 border border-emerald-500/10 rounded-xl">
                         <div className="flex items-center gap-3 mb-2">
                            <Fingerprint className="w-4 h-4 text-emerald-500" />
                            <span className="text-[10px] text-white font-black uppercase">Foundation HSM Signature</span>
                         </div>
                         <code className="text-[10px] text-gray-600 break-all leading-tight block font-mono">
                            {manifest.foundation_signature}
                         </code>
                      </div>
                   </div>

                   <div className="w-full md:w-80 space-y-6">
                      <div className="bg-black/60 border border-white/5 rounded-2xl p-6 text-center">
                         <span className="text-[9px] text-gray-700 font-black uppercase tracking-widest block mb-4">Batch Vaporization</span>
                         <div className="flex items-center justify-center gap-3 mb-4">
                            <Trash2 className="w-8 h-8 text-emerald-500" />
                            <span className="text-4xl font-black text-white tracking-tighter">{manifest.certificate_count}</span>
                         </div>
                         <p className="text-[10px] text-gray-500 font-bold uppercase tracking-tighter">Irreversible Destruction Events</p>
                      </div>
                      <button 
                        onClick={() => setManifest(null)}
                        className="w-full py-3 border border-white/10 rounded-lg text-[9px] font-black text-gray-500 hover:text-white transition-all uppercase tracking-widest flex items-center justify-center gap-2"
                      >
                         <RefreshCw className="w-3 h-3" /> Audit Another Epoch
                      </button>
                   </div>
                </div>
             </div>

             <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
                
                {/* Destruction Chain Graph */}
                <div className="md:col-span-8 bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl">
                   <h3 className="text-xs font-black text-white uppercase tracking-widest mb-10 flex items-center gap-3">
                     <Layers className="w-4 h-4 text-indigo-500" /> Destruction Chain Integrity
                   </h3>
                   
                   <div className="relative space-y-12">
                      <div className="absolute left-[11px] top-2 bottom-2 w-px bg-white/5" />
                      
                      {[
                        { label: 'Network Mempool', status: 'PURGED', icon: Activity, time: 'T-24h' },
                        { label: 'Regional Edge RAM', status: 'WIPED', icon: Cpu, time: 'T-24h 5m' },
                        { label: 'Containment Vault', status: 'VAPORIZED', icon: Database, time: 'T-24h 12m' },
                        { label: 'Compliance Audit', status: 'SIGNED', icon: ShieldCheck, time: 'T-24h 15m' }
                      ].map((step, i) => (
                        <div key={i} className="flex items-start gap-8 relative z-10 group">
                           <div className={`w-6 h-6 rounded-full border border-white/10 flex items-center justify-center transition-colors group-hover:border-emerald-500/50 ${i === 3 ? 'bg-emerald-500 border-emerald-400 text-black shadow-[0_0_15px_rgba(16,185,129,0.5)]' : 'bg-black text-gray-600'}`}>
                              <step.icon className="w-3 h-3" />
                           </div>
                           <div className="flex-1 flex justify-between items-center bg-white/[0.02] border border-white/5 p-4 rounded-xl group-hover:border-white/10 transition-all">
                              <div>
                                 <p className="text-[11px] text-white font-black uppercase tracking-widest mb-1">{step.label}</p>
                                 <span className="text-[9px] text-gray-600 font-bold uppercase">{step.time}</span>
                              </div>
                              <span className={`text-[10px] font-black uppercase tracking-tighter ${i === 3 ? 'text-emerald-500' : 'text-gray-500'}`}>{step.status}</span>
                           </div>
                        </div>
                      ))}
                   </div>
                </div>

                {/* Audit Context Sidebar */}
                <div className="md:col-span-4 space-y-6">
                   <div className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl">
                      <h3 className="text-xs font-black text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                         <Info className="w-4 h-4 text-emerald-500" /> Evidence Proof
                      </h3>
                      <div className="space-y-6">
                         <div>
                            <span className="text-[9px] text-gray-600 uppercase font-black block mb-2">Batch State Root</span>
                            <code className="text-[10px] text-indigo-400 break-all leading-relaxed bg-black p-3 rounded block border border-white/5">
                               {manifest.batch_state_root}
                            </code>
                         </div>
                         <div className="pt-4 border-t border-white/5">
                            <p className="text-[10px] text-gray-500 leading-relaxed italic">
                               "The Batch State Root is a deterministic hash of all 142 Destruction Certificates. Matching this root against the Foundation's public ledger confirms the macro-scale purge."
                            </p>
                         </div>
                      </div>
                   </div>

                   <div className="p-6 bg-emerald-500/5 border border-emerald-500/20 rounded-2xl flex flex-col gap-4">
                      <div className="flex items-center gap-3 text-emerald-500">
                         <ShieldCheck className="w-5 h-5" />
                         <span className="text-[10px] font-black uppercase tracking-widest leading-none">Compliant State</span>
                      </div>
                      <p className="text-[11px] text-gray-500 leading-relaxed font-bold">
                         The local verification of this manifest satisfies the requirements for <span className="text-white">GDPR Recital 65</span> regarding the right to erasure.
                      </p>
                      <button className="w-full py-2 bg-emerald-500 text-black font-black text-[9px] uppercase tracking-widest rounded hover:bg-emerald-400 transition-all flex items-center justify-center gap-2 mt-2">
                         <FileSearch className="w-3.5 h-3.5" /> Full Audit Report
                      </button>
                   </div>
                </div>
             </div>

             {/* Verification Footer */}
             <div className="p-4 bg-emerald-500 text-black rounded-xl flex items-center justify-between px-10 shadow-2xl">
                <div className="flex items-center gap-4">
                   <ShieldCheck className="w-5 h-5" />
                   <span className="text-[10px] font-black uppercase tracking-[0.2em]">Cryptographic Integrity Chain: VERIFIED</span>
                </div>
                <div className="flex items-center gap-2 text-[10px] font-black uppercase">
                   Audit ID: {manifest.export_id.slice(-8)} <ArrowRight className="w-4 h-4" />
                </div>
             </div>
          </div>
        )}

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-5xl mx-auto w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Verification Node Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Mathematical finality is the ultimate audit trail."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] RTBF_AUDIT: ENABLED</span>
            <span>[*] BATCH_MODE: EPOCH_V1</span>
            <span>[*] VERSION: v3.1.9</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
