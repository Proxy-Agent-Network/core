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
  ShieldAlert
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HIGH COURT JURY CHAT (v1.0)
 * "Anonymized, hardware-signed deliberation."
 * ----------------------------------------------------
 */

const App = () => {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'Juror 2', content: 'Has everyone reviewed the PCR 7 drift logs for T-9901?', timestamp: '14:20', isHardwareVerified: true },
    { id: 2, sender: 'Juror 5', content: 'Yes. The drift occurs exactly at the moment of the SMS relay attempt. Looks like a genuine kernel desync.', timestamp: '14:22', isHardwareVerified: true },
    { id: 3, sender: 'Juror 1', content: 'I am seeing a mismatch in the location fingerprint as well. Checking the WiFi entropy now.', timestamp: '14:25', isHardwareVerified: true }
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [isSigning, setIsSigning] = useState(false);
  const scrollRef = useRef(null);

  // Mock Case/Juror Identity
  const caseId = "CASE-8829-APP";
  const myJurorId = "Juror 3 (You)";

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    setIsSigning(true);
    // Simulate TPM 2.0 RSA-PSS Signing
    setTimeout(() => {
      const msg = {
        id: messages.length + 1,
        sender: myJurorId,
        content: newMessage,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isHardwareVerified: true
      };
      setMessages([...messages, msg]);
      setNewMessage('');
      setIsSigning(false);
    }, 800000); // Simulate some delay for "signing"
    
    // Immediate optimistic update for the demo feel
    setIsSigning(false); 
    const msg = {
      id: messages.length + 1,
      sender: myJurorId,
      content: newMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isHardwareVerified: true
    };
    setMessages([...messages, msg]);
    setNewMessage('');
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 flex flex-col selection:bg-indigo-500/30">
      
      {/* Background Decorative Grid */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl mx-auto w-full flex flex-col flex-1 relative z-10 gap-6">
        
        {/* Header: Secure Chamber Info */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-white/10 pb-6 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg shadow-[0_0_20px_rgba(99,102,241,0.1)]">
              <MessageSquare className="w-6 h-6 text-indigo-500" />
            </div>
            <div>
              <h1 className="text-xl font-black text-white tracking-tighter uppercase">Deliberation Chamber</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold">
                Case: <span className="text-indigo-400">{caseId}</span> // Status: <span className="text-green-500">ENCRYPTED</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-3 rounded flex items-center gap-4 shadow-xl">
                <div className="flex flex-col items-end">
                   <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest">Active Quorum</span>
                   <span className="text-sm font-black text-white tracking-tighter">7 / 7 JURORS</span>
                </div>
                <div className="h-6 w-px bg-white/10" />
                <div className="flex items-center gap-2">
                   <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                   <span className="text-[10px] text-green-500 font-black uppercase tracking-widest">Secure Line</span>
                </div>
             </div>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-8 flex-1 min-h-0">
          
          {/* Main Chat Interface */}
          <div className="col-span-12 lg:col-span-8 flex flex-col bg-[#0a0a0a] border border-white/10 rounded-xl overflow-hidden shadow-2xl">
             
             {/* Chat History */}
             <div 
               ref={scrollRef}
               className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth"
             >
                <div className="flex flex-col items-center mb-8">
                   <div className="px-4 py-1.5 bg-white/5 border border-white/10 rounded-full text-[9px] font-black text-gray-500 uppercase tracking-widest mb-4">
                      Protocol Log: Discussion Window Opened
                   </div>
                   <p className="text-[10px] text-gray-700 max-w-sm text-center leading-relaxed">
                     This is a decentralized signal line. Identities are masked to prevent collusion. Messages are permanently shredded 24h after case closure.
                   </p>
                </div>

                {messages.map((msg) => (
                  <div key={msg.id} className={`flex flex-col ${msg.sender.includes('You') ? 'items-end' : 'items-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                     <div className="flex items-center gap-2 mb-2 px-1">
                        <span className={`text-[10px] font-black uppercase tracking-widest ${msg.sender.includes('You') ? 'text-indigo-400' : 'text-gray-500'}`}>
                           {msg.sender}
                        </span>
                        <span className="text-[9px] text-gray-700 font-bold">{msg.timestamp}</span>
                        {msg.isHardwareVerified && (
                          <div className="flex items-center gap-1 text-[8px] text-green-600 font-black uppercase tracking-tighter bg-green-500/5 px-1.5 py-0.5 rounded border border-green-500/10">
                             <ShieldCheck className="w-2.5 h-2.5" /> TPM_SIGNED
                          </div>
                        )}
                     </div>
                     <div className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed ${
                       msg.sender.includes('You') 
                         ? 'bg-indigo-600 text-white rounded-tr-none shadow-[0_4px_15px_rgba(79,70,229,0.2)]' 
                         : 'bg-white/5 border border-white/10 text-gray-300 rounded-tl-none'
                     }`}>
                        {msg.content}
                     </div>
                  </div>
                ))}
             </div>

             {/* Message Input */}
             <form onSubmit={handleSendMessage} className="p-6 border-t border-white/10 bg-white/[0.01]">
                <div className="relative">
                   <input 
                     type="text" 
                     value={newMessage}
                     onChange={(e) => setNewMessage(e.target.value)}
                     placeholder="Type message to the Jury..."
                     className="w-full bg-black border border-white/10 rounded-xl py-4 pl-6 pr-32 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                   />
                   <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
                      <button 
                        type="submit"
                        disabled={isSigning || !newMessage.trim()}
                        className="bg-indigo-500 text-black px-4 py-2 rounded-lg font-black text-[10px] uppercase tracking-widest hover:bg-indigo-400 transition-all flex items-center gap-2 disabled:opacity-20"
                      >
                        {isSigning ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                        Broadcast
                      </button>
                   </div>
                </div>
                <div className="mt-3 flex items-center justify-between px-2">
                   <div className="flex items-center gap-2 text-[9px] text-gray-600 font-black uppercase">
                      <Fingerprint className="w-3 h-3" /> AK_HANDLE: 0x8A2E...{Math.random().toString(16).slice(2, 6).toUpperCase()}
                   </div>
                   <div className="text-[9px] text-gray-700 italic">
                      Hardware-encrypted end-to-end
                   </div>
                </div>
             </form>
          </div>

          {/* Sidebar: Case Context & Rules */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
             
             {/* Rules of Adjudication */}
             <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-8 shadow-2xl">
                <h3 className="text-xs font-black text-white uppercase tracking-[0.2em] mb-8 flex items-center gap-2">
                   <Gavel className="w-4 h-4 text-amber-500" /> Deliberation Rules
                </h3>
                <ul className="space-y-6">
                   <li className="flex items-start gap-4">
                      <div className="p-2 bg-white/5 rounded text-gray-500"><EyeOff className="w-4 h-4" /></div>
                      <div>
                         <p className="text-[10px] text-white font-black uppercase mb-1">Strict Anonymity</p>
                         <p className="text-xs text-gray-500 leading-relaxed">Revealing your Node ID or physical location is a SEV-1 offense and results in bond forfeiture.</p>
                      </div>
                   </li>
                   <li className="flex items-start gap-4">
                      <div className="p-2 bg-white/5 rounded text-gray-500"><Binary className="w-4 h-4" /></div>
                      <div>
                         <p className="text-[10px] text-white font-black uppercase mb-1">Forensic Focus</p>
                         <p className="text-xs text-gray-500 leading-relaxed">Limit discussion to the hardware telemetry and task proof provided in the Evidence Viewer.</p>
                      </div>
                   </li>
                </ul>
             </div>

             {/* Case Summary Card */}
             <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-8 shadow-2xl relative overflow-hidden group">
                <div className="absolute -top-4 -right-4 opacity-5 group-hover:scale-110 transition-transform">
                   <Lock className="w-24 h-24 text-indigo-500" />
                </div>
                <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                   <Clock className="w-3.5 h-3.5" /> Adjudication Clock
                </h4>
                <div className="space-y-4">
                   <div className="flex justify-between items-end">
                      <span className="text-[9px] text-gray-500 uppercase font-black tracking-widest">Time Remaining</span>
                      <span className="text-xl font-black text-white">03:42:15</span>
                   </div>
                   <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                      <div className="bg-indigo-500 h-full" style={{ width: '78%' }} />
                   </div>
                   <button className="w-full py-3 bg-white/5 border border-white/10 rounded-lg text-[10px] font-black text-gray-400 hover:text-white transition-all uppercase tracking-[0.2em]">
                      Open Evidence Viewer
                   </button>
                </div>
             </div>

             {/* Quick Actions */}
             <div className="p-6 border border-white/10 bg-[#0a0a0a] rounded-xl flex flex-col gap-4">
                <div className="flex items-center gap-3">
                   <ShieldAlert className="w-5 h-5 text-red-500" />
                   <h4 className="text-xs font-black text-white uppercase tracking-widest">Report Juror</h4>
                </div>
                <p className="text-[11px] text-gray-500 leading-relaxed italic">
                   "If a juror is proposing collusion or off-protocol settlement, report them immediately for manual High Court audit."
                </p>
                <button className="w-full py-2 bg-red-500/10 border border-red-500/20 text-red-500 font-black text-[9px] uppercase tracking-widest rounded hover:bg-red-500/20 transition-all">
                   Flag Ethics Violation
                </button>
             </div>
          </div>

        </div>

      </main>

      {/* Global Status Bar */}
      <footer className="max-w-6xl mx-auto w-full mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Deliberation Protocol v1.0 Active</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter">Secure Link ID: 0xDEAD...{Math.random().toString(16).slice(2, 6).toUpperCase()}</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] PRIVACY_LEVEL: ZERO_KNOWLEDGE</span>
            <span>[*] HARDWARE_LOCK: ARMED</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
