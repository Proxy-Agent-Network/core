import React, { useState, useMemo } from 'react';
import { 
  ShieldCheck, 
  FileCheck, 
  Search, 
  History, 
  Clock, 
  Database, 
  Trash2, 
  Fingerprint, 
  Binary, 
  ChevronRight, 
  ExternalLink, 
  RefreshCw, 
  CheckCircle2, 
  ShieldAlert, 
  FileText,
  Lock,
  Info,
  Layers,
  Activity,
  XCircle,
  Gavel
} from 'lucide-react';

/**
 * PROXY PROTOCOL - COMPLIANCE AUDIT UI (v1.0)
 * "Verifying the vaporization of toxic data."
 * ----------------------------------------------------
 */

const App = () => {
  const [taskId, setTaskId] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // Mock Certificate Data (Reflecting core/ops/compliance_auditor.py)
  const mockRegistry = {
    'T-9901': {
      id: 'T-9901',
      cert_id: 'CERT-PURGE-1707684000-8A2E',
      node_id: 'NODE_ELITE_X29',
      ingested_at: '2026-02-10T21:00:00Z',
      purged_at: '2026-02-11T21:00:05Z',
      method: 'SHRED_TRIPLE_PASS',
      state_root: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      signature: '0x8a2e1c...f91c3b2e...d2a1...e772'
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setIsSearching(true);
    setError('');
    
    // Simulate API Latency
    setTimeout(() => {
      const found = mockRegistry[taskId.toUpperCase()];
      if (found) {
        setResult(found);
      } else {
        setError('PX_301: Certificate not found for this Task ID.');
        setResult(null);
      }
      setIsSearching(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col items-center selection:bg-emerald-500/30">
      
      {/* Background Matrix Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-4xl w-full relative z-10 space-y-8">
        
        {/* Header: Legal Desk */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl shadow-2xl">
              <FileCheck className="w-8 h-8 text-emerald-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Compliance Audit</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Legal Desk // PII Vaporization Proof // Protocol <span className="text-emerald-500">v3.1.7</span>
              </p>
            </div>
          </div>
          <div className="hidden md:flex flex-col items-end">
             <span className="text-[9px] text-gray-700 uppercase font-black tracking-widest">Attestation Method</span>
             <span className="text-xs font-black text-white">HMAC-SHA256-RSASSA</span>
          </div>
        </header>

        {/* Search Bar */}
        <section className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 shadow-2xl">
           <form onSubmit={handleSearch} className="space-y-4">
              <label className="text-[10px] text-gray-500 font-black uppercase tracking-widest block mb-2">Query Task ID</label>
              <div className="flex gap-4">
                 <div className="relative flex-1">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-700" />
                    <input 
                      type="text" 
                      placeholder="e.g. T-9901"
                      value={taskId}
                      onChange={(e) => setTaskId(e.target.value)}
                      className="w-full bg-black border border-white/10 rounded-xl py-4 pl-12 pr-4 text-sm text-white focus:outline-none focus:border-emerald-500/50 transition-all uppercase tracking-widest"
                      required
                    />
                 </div>
                 <button 
                   type="submit"
                   disabled={isSearching}
                   className="px-8 bg-white text-black font-black text-xs uppercase tracking-widest hover:bg-emerald-500 hover:text-white transition-all rounded-xl shadow-xl flex items-center gap-3 disabled:opacity-20"
                 >
                    {isSearching ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
                    Verify Purge
                 </button>
              </div>
              {error && (
                <div className="flex items-center gap-2 text-red-500 text-[10px] font-bold uppercase mt-2 px-2">
                   <ShieldAlert className="w-3 h-3" /> {error}
                </div>
              )}
           </form>
        </section>

        {/* Result: The Certificate */}
        {result && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
             
             {/* Certificate Hero */}
             <div className="bg-[#0a0a0a] border-2 border-emerald-500/30 rounded-2xl p-10 shadow-[0_0_50px_rgba(16,185,129,0.1)] relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-5">
                   <Gavel className="w-48 h-48 text-white" />
                </div>
                
                <div className="flex justify-between items-start relative z-10 mb-10">
                   <div>
                      <span className="text-[10px] text-emerald-500 font-black uppercase tracking-[0.2em] block mb-1">Destruction Certificate</span>
                      <h2 className="text-3xl font-black text-white tracking-tighter uppercase">{result.cert_id}</h2>
                   </div>
                   <div className="bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 rounded flex items-center gap-3">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      <span className="text-[10px] text-emerald-500 font-black uppercase tracking-widest">VERIFIED_PURGE</span>
                   </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 relative z-10">
                   {/* Data Lifecycle Timeline */}
                   <div className="space-y-6">
                      <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest border-b border-white/5 pb-2">Vaporization Timeline</h3>
                      <div className="space-y-4">
                         <div className="flex gap-4">
                            <div className="w-6 h-6 rounded-full border border-white/10 flex items-center justify-center bg-black shrink-0"><Database className="w-3 h-3 text-gray-600" /></div>
                            <div>
                               <p className="text-[10px] text-white font-black uppercase mb-0.5">Evidence Ingested</p>
                               <p className="text-[9px] text-gray-500 font-bold">{new Date(result.ingested_at).toLocaleString()}</p>
                            </div>
                         </div>
                         <div className="w-px h-6 bg-white/5 ml-3" />
                         <div className="flex gap-4">
                            <div className="w-6 h-6 rounded-full border border-white/10 flex items-center justify-center bg-black shrink-0"><Clock className="w-3 h-3 text-gray-600" /></div>
                            <div>
                               <p className="text-[10px] text-white font-black uppercase mb-0.5">Retention Window Closed</p>
                               <p className="text-[9px] text-gray-500 font-bold">24 Hours Expired</p>
                            </div>
                         </div>
                         <div className="w-px h-6 bg-white/5 ml-3" />
                         <div className="flex gap-4">
                            <div className="w-6 h-6 rounded-full border border-emerald-500/20 flex items-center justify-center bg-emerald-500/10 shrink-0"><Trash2 className="w-3 h-3 text-emerald-500" /></div>
                            <div>
                               <p className="text-[10px] text-emerald-500 font-black uppercase mb-0.5">Irreversible Wipe</p>
                               <p className="text-[9px] text-gray-500 font-bold">{new Date(result.purged_at).toLocaleString()}</p>
                            </div>
                         </div>
                      </div>
                   </div>

                   {/* Cryptographic Manifest */}
                   <div className="space-y-6">
                      <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest border-b border-white/5 pb-2">Audit Manifest</h3>
                      <div className="space-y-4">
                         <div>
                            <span className="text-[9px] text-gray-600 font-black uppercase block mb-1">Scrub Method</span>
                            <span className="text-xs text-white font-bold">{result.method}</span>
                         </div>
                         <div>
                            <span className="text-[9px] text-gray-600 font-black uppercase block mb-1">State Root (Post-Purge)</span>
                            <code className="text-[10px] text-indigo-400 break-all leading-tight block">{result.state_root}</code>
                         </div>
                         <div>
                            <span className="text-[9px] text-gray-600 font-black uppercase block mb-1">Foundation Signature</span>
                            <code className="text-[10px] text-gray-500 break-all leading-tight block">{result.signature}</code>
                         </div>
                      </div>
                   </div>
                </div>

                <div className="mt-12 pt-8 border-t border-white/5 flex flex-col md:flex-row gap-6 items-center">
                   <div className="flex items-center gap-4 flex-1">
                      <Fingerprint className="w-8 h-8 text-indigo-500" />
                      <p className="text-[10px] text-gray-500 leading-relaxed italic">
                        "This certificate provides mathematical proof that the visual evidence associated with {result.id} no longer exists within the Proxy Protocol's containment vaults."
                      </p>
                   </div>
                   <button className="px-8 py-3 bg-white/5 border border-white/10 rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-white/10 transition-all flex items-center gap-2">
                      <FileText className="w-4 h-4 text-gray-400" /> Export Certificate (PDF/A)
                   </button>
                </div>
             </div>

             {/* Regulator Drilldown Grid */}
             <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl flex items-center gap-4 group hover:border-emerald-500/30 transition-all">
                   <div className="p-2 bg-emerald-500/10 rounded-lg group-hover:bg-emerald-500 group-hover:text-black transition-all">
                      <Lock className="w-5 h-5" />
                   </div>
                   <div>
                      <span className="text-[9px] text-gray-600 uppercase font-black block">Privacy Standard</span>
                      <span className="text-xs font-black text-white">GDPR_RTBF</span>
                   </div>
                </div>
                <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl flex items-center gap-4 group hover:border-indigo-500/30 transition-all">
                   <div className="p-2 bg-indigo-500/10 rounded-lg group-hover:bg-indigo-500 group-hover:text-black transition-all">
                      <Layers className="w-5 h-5" />
                   </div>
                   <div>
                      <span className="text-[9px] text-gray-600 uppercase font-black block">Storage Type</span>
                      <span className="text-xs font-black text-white">VOLATILE_RAM</span>
                   </div>
                </div>
                <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl flex items-center gap-4 group hover:border-blue-500/30 transition-all">
                   <div className="p-2 bg-blue-500/10 rounded-lg group-hover:bg-blue-500 group-hover:text-black transition-all">
                      <ShieldCheck className="w-5 h-5" />
                   </div>
                   <div>
                      <span className="text-[9px] text-gray-600 uppercase font-black block">Audit Standing</span>
                      <span className="text-xs font-black text-white uppercase">Compliant</span>
                   </div>
                </div>
             </div>
          </div>
        )}

        {/* Empty State */}
        {!result && !isSearching && (
           <div className="h-64 border-2 border-white/5 border-dashed rounded-2xl flex flex-col items-center justify-center p-12 text-center opacity-40 grayscale">
              <Search className="w-16 h-16 text-gray-800 mb-6" />
              <h3 className="text-xs font-black text-gray-600 uppercase tracking-widest mb-2">Audit Desk Ready</h3>
              <p className="text-[10px] text-gray-800 uppercase font-bold tracking-tighter">Input a finalized Task ID to retrieve its cryptographically-signed destruction receipt.</p>
           </div>
        )}

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-4xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity w-full">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Compliance Registry Online</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Zero-Knowledge means Zero-Trace."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] RTBF_ENABLED: TRUE</span>
            <span>[*] AUDIT_VERSION: v1.0.2</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
