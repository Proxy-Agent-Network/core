import React, { useState, useEffect } from 'react';
import { 
  History, 
  ArrowUpRight, 
  ArrowDownRight, 
  Gavel, 
  Zap, 
  Clock, 
  ExternalLink, 
  Search, 
  Filter, 
  ShieldCheck, 
  AlertTriangle,
  Info,
  Link as LinkIcon,
  ChevronRight,
  Target,
  UserCheck,
  TrendingUp
} from 'lucide-react';

// PROXY PROTOCOL - REPUTATION AUDIT LOG (v1.0)
// "Forensic transparency for the biological node standing."
// ----------------------------------------------------

const App = () => {
  const [filter, setFilter] = useState('ALL');
  const [nodeId] = useState("NODE_ELITE_X29");
  
  // Mock Audit Events
  const [events] = useState([
    { 
      id: "EVT-88291", 
      type: "TASK_SUCCESS", 
      delta: 2, 
      score: 982, 
      timestamp: "2026-02-11T18:42:00Z", 
      ref_id: "T-9901", 
      desc: "Verified SMS Relay (US_DE)" 
    },
    { 
      id: "EVT-88274", 
      type: "JURY_CONSENSUS", 
      delta: 5, 
      score: 980, 
      timestamp: "2026-02-10T11:15:00Z", 
      ref_id: "CASE-992", 
      desc: "Majority vote in High Court adjudication" 
    },
    { 
      id: "EVT-88102", 
      type: "REPUTATION_DECAY", 
      delta: -1, 
      score: 975, 
      timestamp: "2026-02-04T00:00:00Z", 
      ref_id: "CRON-DECAY", 
      desc: "Weekly inactivity adjustment" 
    },
    { 
      id: "EVT-87993", 
      type: "BOND_SLASH", 
      delta: -50, 
      score: 976, 
      timestamp: "2026-01-28T09:12:00Z", 
      ref_id: "CASE-771", 
      desc: "Dissenting vote in Tier 2 dispute" 
    }
  ]);

  const filteredEvents = events.filter(e => {
    if (filter === 'ALL') return true;
    if (filter === 'GAINS') return e.delta > 0;
    if (filter === 'LOSSES') return e.delta < 0;
    return true;
  });

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8">
      
      {/* Background Grid Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '30px 30px' }} />

      <main className="max-w-4xl mx-auto relative z-10 space-y-8">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
                <History className="w-6 h-6 text-indigo-500" />
              </div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase">Reputation Audit Log</h1>
            </div>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest leading-relaxed">
              Forensic Ledger for <span className="text-indigo-400 font-bold">{nodeId}</span>
            </p>
          </div>

          <div className="flex gap-2">
            {['ALL', 'GAINS', 'LOSSES'].map((f) => (
              <button 
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-1.5 rounded text-[10px] font-black uppercase tracking-widest border transition-all ${
                  filter === f 
                    ? 'bg-white text-black border-white' 
                    : 'bg-white/5 border-white/10 text-gray-500 hover:text-white'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Audit Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-2xl">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Stability Index</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-2xl font-black text-white tracking-tighter">98.2%</span>
                 <TrendingUp className="w-4 h-4 text-green-500" />
              </div>
           </div>
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-2xl">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Total Points Gained</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-2xl font-black text-green-500 tracking-tighter">+1,242</span>
                 <Zap className="w-4 h-4 text-green-500/50" />
              </div>
           </div>
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-2xl">
              <span className="text-[9px] text-gray-600 uppercase font-black tracking-widest block mb-2">Slashing Incidents</span>
              <div className="flex items-baseline gap-2">
                 <span className="text-2xl font-black text-red-500 tracking-tighter">1</span>
                 <Gavel className="w-4 h-4 text-red-500/50" />
              </div>
           </div>
        </div>

        {/* Ledger List */}
        <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
          <div className="p-4 bg-white/[0.02] border-b border-white/5 flex justify-between items-center px-8">
            <h3 className="text-[10px] uppercase font-black text-gray-400 tracking-widest flex items-center gap-2">
              <Clock className="w-3.5 h-3.5" /> Immutable Event Stream
            </h3>
            <span className="text-[9px] text-gray-600 font-bold uppercase">{filteredEvents.length} Records Found</span>
          </div>

          <div className="divide-y divide-white/5">
            {filteredEvents.map((event) => (
              <div key={event.id} className="p-8 hover:bg-white/[0.01] transition-all group flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div className="flex items-center gap-6 flex-1">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center border ${
                    event.delta > 0 
                      ? 'bg-green-500/5 border-green-500/20 text-green-500' 
                      : 'bg-red-500/5 border-red-500/20 text-red-500'
                  }`}>
                    {event.delta > 0 ? <ArrowUpRight className="w-6 h-6" /> : <ArrowDownRight className="w-6 h-6" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-[11px] font-black text-white uppercase tracking-tighter group-hover:text-indigo-400 transition-colors">
                        {event.type}
                      </span>
                      <span className="text-[9px] text-gray-600 font-bold uppercase tracking-widest">{event.id}</span>
                    </div>
                    <p className="text-sm text-gray-400 font-medium mb-1">{event.desc}</p>
                    <div className="flex items-center gap-4 text-[9px] text-gray-600 font-bold uppercase tracking-tighter">
                       <span className="flex items-center gap-1"><LinkIcon className="w-2.5 h-2.5" /> Ref: {event.ref_id}</span>
                       <span>{new Date(event.timestamp).toLocaleDateString()} // {new Date(event.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-8 w-full md:w-auto border-t md:border-t-0 border-white/5 pt-4 md:pt-0">
                  <div className="flex flex-col items-end">
                    <span className="text-[9px] text-gray-600 font-black uppercase mb-1">Change</span>
                    <span className={`text-lg font-black tracking-tighter ${event.delta > 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {event.delta > 0 ? '+' : ''}{event.delta}
                    </span>
                  </div>
                  <div className="h-8 w-px bg-white/5" />
                  <div className="flex flex-col items-end min-w-[80px]">
                    <span className="text-[9px] text-gray-600 font-black uppercase mb-1">Balance</span>
                    <span className="text-lg font-black text-white tracking-tighter">{event.score}</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-800 group-hover:text-white transition-colors" />
                </div>
              </div>
            ))}
          </div>

          <button className="w-full py-4 bg-white/[0.02] hover:bg-white/[0.05] text-[10px] font-black uppercase tracking-[0.3em] text-gray-500 hover:text-white transition-all border-t border-white/5">
            Load Historical Archive (2025)
          </button>
        </div>

        {/* Security Verification Panel */}
        <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-8 shadow-2xl flex flex-col md:flex-row items-center gap-8">
           <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl">
              <ShieldCheck className="w-10 h-10 text-indigo-500" />
           </div>
           <div className="flex-1 text-center md:text-left">
              <h3 className="text-lg font-black text-white uppercase tracking-tighter mb-2">Cryptographic Continuity</h3>
              <p className="text-xs text-gray-500 leading-relaxed max-w-xl">
                 This audit log is derived from the **Oracle Heartbeat Hash-Chain**. Every reputation event is cryptographically linked to the preceding state, ensuring that scores cannot be modified without invalidating the entire network's trust root.
              </p>
           </div>
           <button className="px-6 py-3 border border-indigo-500/40 text-indigo-400 font-black text-[10px] uppercase tracking-widest rounded hover:bg-indigo-500 hover:text-black transition-all">
              Verify Chain
           </button>
        </div>

      </main>

      {/* Footer System Status */}
      <footer className="max-w-4xl mx-auto mt-12 flex items-center justify-between px-4 opacity-50">
        <div className="flex items-center gap-2">
           <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
           <span className="text-[9px] font-black uppercase tracking-widest">Oracle Sync: 100%</span>
        </div>
        <span className="text-[9px] font-black uppercase tracking-widest">Proxy Protocol Reputation v2.5.3</span>
      </footer>

    </div>
  );
};

export default App;
