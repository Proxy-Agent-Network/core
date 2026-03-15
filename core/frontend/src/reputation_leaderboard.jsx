import React, { useState, useMemo } from 'react';
import { 
  Trophy, 
  Search, 
  Filter, 
  ArrowUpRight, 
  ShieldCheck, 
  Zap, 
  Activity, 
  Clock, 
  Globe, 
  Star,
  ChevronDown,
  ArrowRight,
  TrendingUp,
  Award,
  Hash,
  RefreshCw,
  MoreHorizontal
} from 'lucide-react';

/**
 * PROXY PROTOCOL - REPUTATION LEADERBOARD (v1.0)
 * "Showcasing the world's most reliable biological nodes."
 * ----------------------------------------------------
 */

const App = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTier, setFilterTier] = useState('ALL');
  const [sortBy, setSortBy] = useState('REP'); // REP, TASKS, UPTIME
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Mock Global Node Data
  const [nodes] = useState([
    { id: "NODE_ELITE_X29", rep: 998, tasks: 1420, uptime: "42d", region: "US_EAST", status: "SUPER-ELITE" },
    { id: "NODE_WHALE_04", rep: 992, tasks: 890, uptime: "156d", region: "US_WEST", status: "SUPER-ELITE" },
    { id: "NODE_ALPHA_001", rep: 965, tasks: 2104, uptime: "12d", region: "EU_WEST", status: "SUPER-ELITE" },
    { id: "NODE_GAMMA_99", rep: 952, tasks: 540, uptime: "8d", region: "ASIA_SE", status: "SUPER-ELITE" },
    { id: "NODE_BETA_821", rep: 845, tasks: 120, uptime: "4d", region: "LATAM", status: "ELITE" },
    { id: "NODE_SIGMA_02", rep: 812, tasks: 95, uptime: "2d", region: "EU_NORTH", status: "ELITE" },
    { id: "NODE_PROB_77", rep: 410, tasks: 12, uptime: "1d", region: "US_SOUTH", status: "PROBATION" }
  ]);

  const sortedNodes = useMemo(() => {
    let filtered = nodes.filter(n => 
      n.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
      n.region.toLowerCase().includes(searchQuery.toLowerCase())
    );

    if (filterTier !== 'ALL') {
      filtered = filtered.filter(n => n.status === filterTier);
    }

    return filtered.sort((a, b) => {
      if (sortBy === 'REP') return b.rep - a.rep;
      if (sortBy === 'TASKS') return b.tasks - a.tasks;
      return parseInt(b.uptime) - parseInt(a.uptime);
    });
  }, [nodes, searchQuery, filterTier, sortBy]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8">
      
      {/* Background Decorative Element */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl mx-auto relative z-10">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 gap-6">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
                <Trophy className="w-6 h-6 text-indigo-500" />
              </div>
              <h1 className="text-3xl font-black text-white tracking-tighter uppercase">Node Leaderboard</h1>
            </div>
            <p className="text-xs text-gray-500 uppercase tracking-widest leading-relaxed">
              Global Performance Rankings // Protocol <span className="text-indigo-400 font-bold">v2.5.5</span>
            </p>
          </div>

          <div className="flex gap-4">
             <div className="bg-[#0a0a0a] border border-white/5 p-4 rounded flex items-center gap-4">
                <div className="flex flex-col">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Active Fleet</span>
                   <span className="text-lg font-black text-white">1,248</span>
                </div>
                <div className="h-6 w-px bg-white/10" />
                <div className="flex flex-col">
                   <span className="text-[9px] text-gray-600 uppercase font-black">Avg Rep</span>
                   <span className="text-lg font-black text-green-500">942.5</span>
                </div>
             </div>
             <button 
               onClick={handleRefresh}
               className={`p-4 bg-white/5 border border-white/10 rounded hover:bg-white/10 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
             >
               <RefreshCw className="w-4 h-4 text-gray-400" />
             </button>
          </div>
        </header>

        {/* Filters & Search */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-8">
           <div className="md:col-span-6 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
              <input 
                type="text" 
                placeholder="SEARCH NODE_ID OR REGION..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#0a0a0a] border border-white/5 rounded-lg py-3 pl-12 pr-4 text-xs text-white focus:outline-none focus:border-indigo-500/50 uppercase tracking-widest placeholder:text-gray-800"
              />
           </div>
           <div className="md:col-span-3 flex bg-[#0a0a0a] border border-white/5 p-1 rounded-lg">
              {['ALL', 'SUPER-ELITE', 'ELITE'].map(t => (
                <button 
                  key={t}
                  onClick={() => setFilterTier(t)}
                  className={`flex-1 py-2 text-[9px] font-black rounded transition-all ${filterTier === t ? 'bg-white/5 text-white' : 'text-gray-600 hover:text-gray-400'}`}
                >
                  {t.replace('-', ' ')}
                </button>
              ))}
           </div>
           <div className="md:col-span-3 relative group">
              <select 
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full bg-[#0a0a0a] border border-white/5 rounded-lg py-3 px-4 text-xs text-gray-400 appearance-none focus:outline-none uppercase tracking-widest font-bold"
              >
                <option value="REP">SORT BY REPUTATION</option>
                <option value="TASKS">SORT BY VOLUME</option>
                <option value="UPTIME">SORT BY STREAK</option>
              </select>
              <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-700 pointer-events-none" />
           </div>
        </div>

        {/* Leaderboard Table */}
        <div className="bg-[#0a0a0a] border border-white/5 rounded-xl overflow-hidden shadow-2xl">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/[0.02] border-b border-white/5">
                <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest w-16">Rank</th>
                <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest">Node Identity</th>
                <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest">Reputation</th>
                <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest text-center">Tasks</th>
                <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest text-right">Uptime</th>
                <th className="p-6 text-[10px] font-black text-gray-600 uppercase tracking-widest text-right">Region</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {sortedNodes.map((node, index) => (
                <tr key={node.id} className="group hover:bg-white/[0.01] transition-all">
                  <td className="p-6">
                    <span className={`text-xs font-black ${index < 3 ? 'text-amber-500' : 'text-gray-700'}`}>
                      {index + 1 < 10 ? `0${index + 1}` : index + 1}
                    </span>
                  </td>
                  <td className="p-6">
                    <div className="flex items-center gap-4">
                      <div className="w-8 h-8 rounded bg-indigo-500/5 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
                        <Hash className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="text-xs font-black text-white block mb-0.5 group-hover:text-indigo-400 transition-colors uppercase tracking-tight">{node.id}</span>
                        <div className="flex items-center gap-2">
                           <span className={`text-[8px] font-black uppercase tracking-widest ${node.status === 'SUPER-ELITE' ? 'text-amber-500' : 'text-indigo-400'}`}>
                             {node.status}
                           </span>
                           {node.status === 'SUPER-ELITE' && <ShieldCheck className="w-2.5 h-2.5 text-amber-500" />}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="p-6">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-black text-white mono tracking-tighter">{node.rep}</span>
                      <div className="w-16 h-1 bg-white/5 rounded-full overflow-hidden hidden sm:block">
                         <div className={`h-full ${node.rep > 950 ? 'bg-amber-500' : 'bg-indigo-500'} opacity-60`} style={{ width: `${(node.rep/1000)*100}%` }} />
                      </div>
                    </div>
                  </td>
                  <td className="p-6 text-center">
                    <span className="text-xs font-bold text-gray-400">{node.tasks.toLocaleString()}</span>
                  </td>
                  <td className="p-6 text-right">
                    <div className="flex flex-col items-end">
                       <span className="text-xs font-bold text-white tracking-tighter">{node.uptime}</span>
                       <span className="text-[8px] text-gray-700 uppercase font-black">CURRENT STREAK</span>
                    </div>
                  </td>
                  <td className="p-6 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Globe className="w-3 h-3 text-gray-700" />
                      <span className="text-[10px] font-black text-gray-500 uppercase">{node.region}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {sortedNodes.length === 0 && (
            <div className="p-20 text-center flex flex-col items-center">
              <Activity className="w-12 h-12 text-gray-800 mb-4 animate-pulse" />
              <h3 className="text-xs font-black text-gray-600 uppercase tracking-widest">No matching nodes detected</h3>
              <p className="text-[10px] text-gray-800 mt-2">Try adjusting your filtration parameters.</p>
            </div>
          )}
        </div>

        {/* Global Performance Insights (Grid) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl group">
              <div className="flex items-center justify-between mb-6">
                <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Stability Index</h4>
                <TrendingUp className="w-4 h-4 text-green-500" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-black text-white">99.2%</span>
                <span className="text-[9px] text-green-500 font-bold uppercase">+0.4%</span>
              </div>
              <p className="text-[9px] text-gray-700 mt-4 leading-relaxed italic">
                *Aggregated consensus accuracy across all Tier 1/2 tasks over the last 24h.
              </p>
           </div>

           <div className="bg-[#0a0a0a] border border-white/5 p-6 rounded-xl shadow-xl group">
              <div className="flex items-center justify-between mb-6">
                <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Network Growth</h4>
                <Zap className="w-4 h-4 text-indigo-500" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-black text-white">+14</span>
                <span className="text-[9px] text-indigo-500 font-bold uppercase">NODES</span>
              </div>
              <p className="text-[9px] text-gray-700 mt-4 leading-relaxed italic">
                *Net hardware expansion since the previous protocol epoch (2026.02.10).
              </p>
           </div>

           <div className="p-6 bg-gradient-to-br from-amber-500/5 to-transparent border border-amber-500/10 rounded-xl shadow-xl">
              <div className="flex items-center justify-between mb-6">
                <h4 className="text-[10px] font-black text-amber-500/60 uppercase tracking-widest">High Court Status</h4>
                <Award className="w-5 h-5 text-amber-500" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-black text-white">58</span>
                <span className="text-[9px] text-amber-500 font-bold uppercase">JURORS</span>
              </div>
              <p className="text-[9px] text-gray-700 mt-4 leading-relaxed italic">
                *Nodes verifiably exceeding the 950 REP threshold for appellate court VRF selection.
              </p>
           </div>
        </div>

      </main>

      {/* Global Status Footer */}
      <footer className="max-w-6xl mx-auto mt-12 py-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6 opacity-50 grayscale hover:grayscale-0 transition-all duration-700">
         <div className="flex items-center gap-2">
           <ShieldCheck className="w-4 h-4 text-gray-500" />
           <span className="text-[9px] font-black uppercase tracking-widest">Verified Hardware Ledger</span>
         </div>
         <div className="flex gap-8 text-[9px] font-bold uppercase tracking-widest text-gray-700">
           <span>Uptime: 99.98%</span>
           <span>Latency: 42ms</span>
           <span>Block: 882931</span>
         </div>
         <span className="text-[9px] font-black uppercase tracking-widest">© 2026 Proxy Protocol Foundation</span>
      </footer>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes text-glow {
          0% { text-shadow: 0 0 10px rgba(99, 102, 241, 0); }
          50% { text-shadow: 0 0 15px rgba(99, 102, 241, 0.4); }
          100% { text-shadow: 0 0 10px rgba(99, 102, 241, 0); }
        }
        .text-glow-hover:hover {
          animation: text-glow 2s infinite;
        }
      `}} />
    </div>
  );
};

export default App;
