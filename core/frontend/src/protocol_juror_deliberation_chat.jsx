import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageSquare, 
  ShieldCheck, 
  Lock, 
  Users, 
  Send, 
  Fingerprint, 
  EyeOff, 
  AlertTriangle, 
  Clock, 
  RefreshCw, 
  Info, 
  Terminal,
  Gavel,
  CheckCircle2,
  Binary,
  UserCheck,
  ShieldAlert,
  Smartphone,
  ChevronRight,
  Database
} from 'lucide-react';

/**
 * PROXY PROTOCOL - JUROR DELIBERATION CHAT (v1.1)
 * "Anonymized, E2EE communication for High Court quorums."
 * ----------------------------------------------------
 * v1.1 Fix: Replaced input with auto-expanding textarea to prevent text-button overlap.
 */

const App = () => {
  const caseId = "CASE-8829-APP"; 
  const [messages, setMessages] = useState([
    { id: 1, sender: 'Juror 1', content: 'Checking in. Evidence shard unsealed. Initial look at the PCR logs suggests valid drift.', timestamp: '19:42', isVerified: true },
    { id: 2, sender: 'Juror 4', content: 'Agreed. The delta in US_EAST hub coordinates is outside the 500m policy window.', timestamp: '19:45', isVerified: true },
    { id: 3, sender: 'Juror 7', content: 'Wait—look at the dHash on the original intent. It matches an Asia-SE cluster signature.', timestamp: '19:50', isVerified: true }
  ]);
  const [input, setInput] = useState('');
  const [isSigning, setIsSigning] = useState(false);
  const scrollRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll logic
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Dynamic Textarea Sizing
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSend = (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || isSigning) return;

    setIsSigning(true);
    setTimeout(() => {
      const msg = {
        id: Date.now(),
        sender: 'Juror 3 (You)',
        content: input,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isVerified: true
      };
      setMessages([...messages, msg]);
      setInput('');
      setIsSigning(false);
    }, 1200);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex items-center justify-center selection:bg-indigo-500/30 overflow-hidden">
      
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl w-full h-[85vh] relative z-10 flex flex-col bg-[#0a0a0a] border border-white/10 rounded-3xl shadow-2xl overflow-hidden">
        
        <header className="p-6 border-b border-white/5 bg-white/[0.02] flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
              <MessageSquare className="w-6 h-6 text-indigo-500" />
            </div>
            <div>
              <h1 className="text-xl font-black text-white tracking-tighter uppercase leading-none">Chamber_8829_SEC</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-1">
                E2EE Deliberation // High Court <span className="text-indigo-400">v3.5.6</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-black/40 border border-white/5 px-4 py-2 rounded-lg flex items-center gap-6">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Quorum Status</span>
                   <span className="text-sm font-black text-white tracking-tighter">7 / 7 ONLINE</span>
                </div>
                <div className="h-6 w-px bg-white/10" />
                <div className="flex items-center gap-2">
                   <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                   <span className="text-[10px] text-green-500 font-black uppercase tracking-widest">Secure Line</span>
                </div>
             </div>
          </div>
        </header>

        <div className="flex-1 flex overflow-hidden">
          <section className="flex-1 flex flex-col min-w-0">
             <div ref={scrollRef} className="flex-1 overflow-y-auto p-8 space-y-6 scrollbar-hide">
                <div className="flex flex-col items-center mb-10 opacity-40">
                   <div className="px-4 py-1.5 bg-white/5 border border-white/5 rounded-full text-[9px] font-black uppercase tracking-widest mb-3">
                      Secure Channel Initialization Complete
                   </div>
                   <p className="text-[10px] text-center max-w-sm leading-relaxed italic">
                      "Personal node identities are masked. All communications are hardware-signed."
                   </p>
                </div>

                {messages.map((msg) => (
                  <div key={msg.id} className={`flex flex-col ${msg.sender.includes('You') ? 'items-end' : 'items-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                     <div className="flex items-center gap-3 mb-2 px-1">
                        <span className={`text-[10px] font-black uppercase tracking-widest ${msg.sender.includes('You') ? 'text-indigo-400' : 'text-gray-500'}`}>
                           {msg.sender}
                        </span>
                        {msg.isVerified && (
                          <div className="flex items-center gap-1 text-[8px] text-green-600 font-black uppercase bg-green-500/5 px-1.5 py-0.5 rounded border border-green-500/10 tracking-tighter">
                             <ShieldCheck className="w-2.5 h-2.5" /> TPM_AUTH
                          </div>
                        )}
                        <span className="text-[9px] text-gray-700 font-bold">{msg.timestamp}</span>
                     </div>
                     <div className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed ${
                       msg.sender.includes('You') 
                         ? 'bg-indigo-600 text-white rounded-tr-none shadow-[0_5px_15px_rgba(99,102,241,0.2)]' 
                         : 'bg-white/5 border border-white/10 text-gray-300 rounded-tl-none'
                     }`}>
                        {msg.content}
                     </div>
                  </div>
                ))}
             </div>

             <div className="p-6 border-t border-white/5 bg-black/40">
                <form className="relative flex items-end gap-3 bg-black border border-white/10 rounded-2xl p-2 focus-within:border-indigo-500 transition-all">
                   <textarea 
                     ref={textareaRef}
                     rows="1"
                     value={input}
                     onChange={(e) => setInput(e.target.value)}
                     onKeyDown={handleKeyDown}
                     placeholder="Broadcast signed message to the quorum..."
                     className="flex-1 bg-transparent py-4 pl-6 pr-2 text-sm text-white focus:outline-none placeholder:text-gray-700 resize-none min-h-[54px] max-h-32 scrollbar-hide"
                     disabled={isSigning}
                   />
                   <button 
                     type="button"
                     onClick={handleSend}
                     disabled={!input.trim() || isSigning}
                     className="mb-1.5 mr-1.5 bg-indigo-500 text-black px-6 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-indigo-400 transition-all flex items-center gap-3 shadow-2xl disabled:opacity-20 shrink-0"
                   >
                      {isSigning ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                      {isSigning ? 'Signing' : 'Sign & Send'}
                   </button>
                </form>
                <div className="mt-4 flex justify-between items-center px-2 opacity-50">
                   <div className="flex items-center gap-2 text-[9px] text-gray-600 font-black uppercase">
                      <Fingerprint className="w-3 h-3" /> AK_HANDLE: 0x8A2E...F91C
                   </div>
                   <div className="text-[9px] text-gray-700 italic">Encrypted via RSA-OAEP / 2048-bit</div>
                </div>
             </div>
          </section>

          <aside className="hidden lg:flex w-80 border-l border-white/5 flex-col bg-black/20">
             <div className="p-6 border-b border-white/5">
                <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-6 flex items-center gap-2">
                   <Info className="w-4 h-4 text-indigo-500" /> Case Context
                </h3>
                <div className="space-y-6">
                   <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                      <span className="text-[9px] text-gray-600 uppercase font-black block mb-2">Dispute Target</span>
                      <p className="text-xs text-white font-bold uppercase tracking-tight">Case {caseId}</p>
                   </div>
                   <div className="p-4 bg-red-500/5 border border-red-500/10 rounded-xl">
                      <span className="text-[9px] text-red-500 font-black uppercase block mb-2">Risk Violation</span>
                      <p className="text-xs text-gray-400 font-medium leading-relaxed italic">
                         "Probable metadata forgery on T-9901 proof-of-work."
                      </p>
                   </div>
                </div>
             </div>

             <div className="flex-1 p-6 overflow-y-auto scrollbar-hide space-y-6">
                <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest flex items-center gap-2">
                   <Binary className="w-4 h-4 text-emerald-500" /> Evidence Locks
                </h3>
                <div className="space-y-4">
                   <div className="p-4 bg-black border border-white/5 rounded-xl flex items-center justify-between group hover:border-emerald-500/30 transition-all cursor-pointer">
                      <div className="flex items-center gap-4">
                         <Database className="w-4 h-4 text-gray-600 group-hover:text-emerald-500 transition-colors" />
                         <span className="text-[10px] text-gray-500 font-bold uppercase">PCR_Log.bin</span>
                      </div>
                      <ChevronRight className="w-3 h-3 text-gray-800" />
                   </div>
                   <div className="p-4 bg-black border border-white/5 rounded-xl flex items-center justify-between group hover:border-indigo-500/30 transition-all cursor-pointer">
                      <div className="flex items-center gap-4">
                         <Lock className="w-4 h-4 text-gray-600 group-hover:text-indigo-500 transition-colors" />
                         <span className="text-[10px] text-gray-500 font-bold uppercase">LND_State.json</span>
                      </div>
                      <ChevronRight className="w-3 h-3 text-gray-800" />
                   </div>
                </div>
             </div>

             <div className="p-8 border-t border-white/5 bg-black/60">
                <div className="flex items-start gap-4 mb-6">
                   <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />
                   <p className="text-[10px] text-gray-500 leading-relaxed italic">
                      "Any attempts to reveal personal node identity result in bond liquidation."
                   </p>
                </div>
                <button className="w-full py-4 bg-red-600/10 border border-red-600/30 text-red-500 font-black text-[10px] uppercase tracking-widest rounded hover:bg-red-600 hover:text-white transition-all">
                   Report Violation
                </button>
             </div>
          </aside>
        </div>
      </main>

      <footer className="fixed bottom-0 w-full bg-[#0a0a0a] border-t border-white/5 p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity z-50 px-10">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest font-mono">Quorum Sync: Active</span>
            </div>
            <div className="h-4 w-px bg-white/10 hidden md:block" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter hidden md:block italic">"Collaborative biological audit."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] SESSION: {caseId}</span>
            <span>[*] VERSION: v3.5.6</span>
         </div>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        @keyframes scan { 0% { transform: translateY(-120px); } 50% { transform: translateY(120px); } 100% { transform: translateY(-120px); } }
        .animate-scan { animation: scan 3s ease-in-out infinite; }
      `}} />
    </div>
  );
};

export default App;
