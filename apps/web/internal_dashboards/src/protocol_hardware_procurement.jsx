import React, { useState, useMemo } from 'react';
import { 
  ShoppingCart, 
  Package, 
  Truck, 
  ShieldCheck, 
  Zap, 
  Globe, 
  Cpu, 
  RefreshCw, 
  ChevronRight, 
  ArrowRight, 
  Info, 
  CreditCard, 
  MapPin, 
  Activity, 
  Lock, 
  Binary, 
  Layers, 
  CheckCircle2, 
  Plane,
  Box,
  HardDrive,
  BadgeCheck,
  Smartphone,
  Coins
} from 'lucide-react';

/**
 * PROXY PROTOCOL - HARDWARE PROCUREMENT PORTAL (v1.0)
 * "Provisioning the physical edge of the autonomous economy."
 * ----------------------------------------------------
 */

const App = () => {
  const [cart, setCart] = useState([]);
  const [view, setView] = useState('CATALOG'); // CATALOG, TRACKING, CHECKOUT
  const [isProcessing, setIsProcessing] = useState(false);

  // Mock Sentry Catalog
  const products = [
    {
      id: 'SENTRY-V1',
      name: 'Proxy Sentry v1 (Stationary)',
      tier: 'TIER 2',
      price: 2500000,
      specs: ['Infineon SLB9670 TPM', 'RPi 5 (8GB)', 'Tamper-Evident Chassis'],
      description: 'Ideal for Mailroom and Notary nodes requiring high-fidelity proof of location.',
      icon: HardDrive
    },
    {
      id: 'SENTRY-MOBILE',
      name: 'Mobile Sentry (Portable)',
      tier: 'TIER 2',
      price: 1800000,
      specs: ['Mobile TPM Module', 'GPS-L5 Assisted', '12h Battery Life'],
      description: 'Optimized for Courier nodes with city-wide hardware-verified geofencing.',
      icon: Smartphone
    },
    {
      id: 'SENTRY-PRO',
      name: 'Professional Notary Unit',
      tier: 'TIER 3',
      price: 4500000,
      specs: ['HSM-Grade Security', 'Dual Biometric Auth', 'E2EE Document Scanner'],
      description: 'The standard for Legal Proxies handling sensitive jurisdictional deeds.',
      icon: Cpu
    }
  ];

  // Mock Active Orders (Integrated with Logistics Relay)
  const [orders] = useState([
    {
      id: 'ORD-8829-JP',
      unit: 'SENTRY-V1',
      status: 'IN_TRANSIT',
      carrier: 'DHL_EXPRESS',
      tracking: '8829310',
      progress: 65,
      eta: '48h',
      region: 'Tokyo, JP'
    }
  ]);

  const addToCart = (product) => {
    setCart([...cart, product]);
    // Small UI feedback would go here
  };

  const totalSats = cart.reduce((acc, curr) => acc + curr.price, 0);

  return (
    <div className="min-h-screen bg-[#050505] text-gray-300 font-mono p-4 md:p-8 selection:bg-amber-500/30">
      
      {/* Background Grid Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02] z-0" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      <main className="max-w-6xl mx-auto relative z-10 space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-8 gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl shadow-2xl">
              <Package className="w-8 h-8 text-amber-500 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tighter uppercase leading-none">Procurement Hub</h1>
              <p className="text-[10px] text-gray-600 uppercase tracking-widest font-bold mt-2">
                Certified Hardware // Satoshi Standard // Protocol <span className="text-amber-500">v3.3.1</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4">
             <button 
               onClick={() => setView('CATALOG')}
               className={`px-6 py-2 text-[10px] font-black uppercase tracking-widest rounded-lg transition-all ${view === 'CATALOG' ? 'bg-amber-500 text-black shadow-lg shadow-amber-500/20' : 'text-gray-500 hover:text-white'}`}
             >
                Catalog
             </button>
             <button 
               onClick={() => setView('TRACKING')}
               className={`px-6 py-2 text-[10px] font-black uppercase tracking-widest rounded-lg transition-all ${view === 'TRACKING' ? 'bg-amber-500 text-black shadow-lg shadow-amber-500/20' : 'text-gray-500 hover:text-white'}`}
             >
                Active Orders
             </button>
             <div className="h-10 w-px bg-white/10 mx-2" />
             <div className="bg-[#0a0a0a] border border-white/5 p-3 rounded-lg flex items-center gap-4 shadow-xl">
                <ShoppingCart className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-black text-white">{cart.length} <span className="text-[10px] text-gray-700">ITEMS</span></span>
             </div>
          </div>
        </header>

        {view === 'CATALOG' && (
          <div className="space-y-8 animate-in fade-in duration-500">
             {/* Product Grid */}
             <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {products.map((p) => (
                  <div key={p.id} className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-8 flex flex-col group hover:border-amber-500/30 transition-all shadow-2xl relative overflow-hidden">
                     <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:scale-110 transition-transform">
                        <p.icon className="w-32 h-32 text-white" />
                     </div>
                     <div className="mb-6">
                        <span className="text-[9px] text-amber-500 font-black uppercase tracking-widest bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20">{p.tier}</span>
                        <h3 className="text-xl font-black text-white uppercase tracking-tighter mt-4">{p.name}</h3>
                        <p className="text-xs text-gray-500 mt-2 leading-relaxed italic">{p.description}</p>
                     </div>

                     <div className="space-y-3 mb-8">
                        {p.specs.map((spec, i) => (
                           <div key={i} className="flex items-center gap-3 text-[10px] text-gray-400 font-bold uppercase tracking-tight">
                              <ShieldCheck className="w-3 h-3 text-indigo-500" /> {spec}
                           </div>
                        ))}
                     </div>

                     <div className="mt-auto pt-6 border-t border-white/5 flex items-center justify-between">
                        <div>
                           <span className="text-[9px] text-gray-700 uppercase font-black block mb-1">Unit Cost</span>
                           <span className="text-xl font-black text-white">{(p.price / 1000000).toFixed(1)}M <span className="text-xs text-gray-600">SATS</span></span>
                        </div>
                        <button 
                          onClick={() => addToCart(p)}
                          className="p-3 bg-white text-black rounded-xl hover:bg-amber-500 hover:text-white transition-all shadow-xl"
                        >
                           <ArrowRight className="w-5 h-5" />
                        </button>
                     </div>
                  </div>
                ))}
             </div>

             {/* Total & Checkout */}
             {cart.length > 0 && (
               <div className="bg-amber-500/5 border border-amber-500/20 rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-8 shadow-[0_0_50px_rgba(245,158,11,0.05)] animate-in slide-in-from-bottom-4">
                  <div className="flex items-center gap-6">
                     <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl">
                        <Coins className="w-10 h-10 text-amber-500" />
                     </div>
                     <div>
                        <h3 className="text-xl font-black text-white uppercase tracking-tighter">Order Summary</h3>
                        <p className="text-xs text-gray-500 uppercase tracking-widest font-black">Total: <span className="text-white">{totalSats.toLocaleString()} Satoshis</span></p>
                     </div>
                  </div>
                  <div className="flex gap-4 w-full md:w-auto">
                     <button 
                       onClick={() => setCart([])}
                       className="px-8 py-4 border border-white/10 text-gray-500 font-black text-xs uppercase tracking-widest hover:text-white transition-all"
                     >
                        Clear Cart
                     </button>
                     <button className="flex-1 md:flex-none px-12 py-4 bg-white text-black font-black text-xs uppercase tracking-[0.2em] rounded shadow-2xl hover:bg-amber-500 hover:text-white transition-all">
                        Initialize Lightning Payment
                     </button>
                  </div>
               </div>
             )}
          </div>
        )}

        {view === 'TRACKING' && (
          <div className="space-y-8 animate-in fade-in duration-500">
             {orders.map((order) => (
                <div key={order.id} className="bg-[#0a0a0a] border border-white/5 rounded-2xl overflow-hidden shadow-2xl">
                   <div className="p-6 border-b border-white/5 bg-white/[0.02] flex justify-between items-center px-10">
                      <div>
                         <span className="text-[10px] text-amber-500 font-black uppercase tracking-[0.2em] block mb-1">Global Logistics</span>
                         <h2 className="text-2xl font-black text-white tracking-tighter uppercase">{order.id}</h2>
                      </div>
                      <div className="text-right">
                         <span className="text-[9px] text-gray-700 uppercase font-black block mb-1">Estimated Arrival</span>
                         <span className="text-sm font-black text-white uppercase">{order.eta}</span>
                      </div>
                   </div>

                   <div className="p-10 grid grid-cols-1 md:grid-cols-12 gap-12">
                      {/* Visual Path */}
                      <div className="md:col-span-8 space-y-12">
                         <div className="relative">
                            <div className="absolute top-1/2 left-0 w-full h-px bg-white/5 -translate-y-1/2" />
                            <div className="flex justify-between relative z-10">
                               {[
                                 { label: 'Factory', icon: Box, complete: true },
                                 { label: 'Carrier', icon: Plane, complete: true },
                                 { label: 'Regional Hub', icon: Globe, complete: false },
                                 { label: 'Deployed', icon: MapPin, complete: false }
                               ].map((step, i) => (
                                 <div key={i} className="flex flex-col items-center gap-4">
                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-700 ${step.complete ? 'bg-amber-500 border-amber-400 text-black shadow-[0_0_15px_rgba(245,158,11,0.4)]' : 'bg-black border-white/10 text-gray-700'}`}>
                                       <step.icon className="w-5 h-5" />
                                    </div>
                                    <span className={`text-[9px] font-black uppercase tracking-widest ${step.complete ? 'text-white' : 'text-gray-700'}`}>{step.label}</span>
                                 </div>
                               ))}
                            </div>
                         </div>

                         <div className="p-6 bg-black border border-white/5 rounded-xl space-y-4">
                            <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                               <span className="text-gray-600">Transit Progress</span>
                               <span className="text-amber-500">{order.progress}%</span>
                            </div>
                            <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                               <div className="bg-amber-500 h-full animate-pulse shadow-[0_0_10px_rgba(245,158,11,0.5)]" style={{ width: `${order.progress}%` }} />
                            </div>
                         </div>
                      </div>

                      {/* Manifest Detail */}
                      <div className="md:col-span-4 space-y-6">
                         <div className="p-6 border border-white/5 rounded-xl bg-white/[0.01]">
                            <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                               <Info className="w-3.5 h-3.5" /> Shipment Manifest
                            </h4>
                            <div className="space-y-4 font-mono text-[11px]">
                               <div className="flex justify-between">
                                  <span className="text-gray-700">UNIT:</span>
                                  <span className="text-white">{order.unit}</span>
                               </div>
                               <div className="flex justify-between">
                                  <span className="text-gray-700">CARRIER:</span>
                                  <span className="text-white">{order.carrier}</span>
                               </div>
                               <div className="flex justify-between">
                                  <span className="text-gray-700">TRACKING:</span>
                                  <span className="text-indigo-400">{order.tracking}</span>
                               </div>
                               <div className="flex justify-between border-t border-white/5 pt-3">
                                  <span className="text-gray-700">DEST:</span>
                                  <span className="text-white">{order.region}</span>
                               </div>
                            </div>
                         </div>
                         <button className="w-full py-3 bg-white/5 border border-white/10 rounded text-[9px] font-black text-gray-500 hover:text-white uppercase tracking-widest transition-all">
                            View Logistics Proof &rarr;
                         </button>
                      </div>
                   </div>
                </div>
             ))}
          </div>
        )}

        {/* Global Hardware Assurance */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
           <div className="p-8 bg-indigo-500/5 border border-indigo-500/20 rounded-2xl flex flex-col gap-4 group hover:border-indigo-500/40 transition-all">
              <ShieldCheck className="w-8 h-8 text-indigo-500" />
              <h4 className="text-xs font-black text-white uppercase tracking-widest">Hardware Root of Trust</h4>
              <p className="text-[11px] text-gray-500 leading-relaxed italic">
                 "All sentry units are provisioned with Infineon OPTIGA™ TPM 2.0 modules. Keys are sealed at the factory and never enter RAM."
              </p>
           </div>
           <div className="p-8 bg-emerald-500/5 border border-emerald-500/20 rounded-2xl flex flex-col gap-4 group hover:border-emerald-500/40 transition-all">
              <BadgeCheck className="w-8 h-8 text-emerald-500" />
              <h4 className="text-xs font-black text-white uppercase tracking-widest">Certified Deployment</h4>
              <p className="text-[11px] text-gray-500 leading-relaxed italic">
                 "Units undergo a 48h stress-test and PCR audit before shipment to ensure no software-level tampered states exist."
              </p>
           </div>
           <div className="p-8 bg-blue-500/5 border border-blue-500/20 rounded-2xl flex flex-col gap-4 group hover:border-blue-500/40 transition-all">
              <Layers className="w-8 h-8 text-blue-500" />
              <h4 className="text-xs font-black text-white uppercase tracking-widest">Global Interoperability</h4>
              <p className="text-[11px] text-gray-500 leading-relaxed italic">
                 "Designed for the Proxy SDK, units support sub-second HODL invoice resolution via standard LND REST interfaces."
              </p>
           </div>
        </div>

      </main>

      {/* Global Procurement Footer */}
      <footer className="max-w-6xl mx-auto mt-12 bg-[#0a0a0a] border border-white/5 rounded-lg p-4 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
         <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse" />
               <span className="text-[9px] text-white font-black uppercase tracking-widest">Inventory Ledger Synchronized</span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[9px] text-gray-600 font-bold uppercase tracking-tighter italic">"Scaling the network brick by brick, silicon by silicon."</span>
         </div>
         <div className="flex gap-8 text-[9px] font-black uppercase text-gray-700 tracking-widest">
            <span>[*] FACTORY_UP: TRUE</span>
            <span>[*] REINFORCEMENT_ETA: 48H</span>
            <span>[*] VERSION: v3.3.1</span>
         </div>
      </footer>

    </div>
  );
};

export default App;
