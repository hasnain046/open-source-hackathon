import React from 'react';
import { TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const AuthLayout = ({ children }) => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden mesh-bg">
      {/* Decorative backdrop blobs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />
      
      <div className="sm:mx-auto sm:w-full sm:max-w-md z-10 flex flex-col items-center">
        <div 
          onClick={() => navigate('/')}
          className="flex items-center gap-3 cursor-pointer group hover:opacity-90 transition-opacity"
        >
          <div className="p-3 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-lg group-hover:scale-105 transition-transform duration-300">
            <TrendingUp size={28} className="animate-pulse" />
          </div>
          <div>
            <span className="font-display font-extrabold text-2xl bg-gradient-to-r from-cyan-400 via-indigo-400 to-rose-400 bg-clip-text text-transparent">
              InflationIQ
            </span>
            <p className="text-xs text-slate-500 font-bold tracking-widest uppercase">AI Economic intelligence</p>
          </div>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md z-10 px-4">
        <div className="glass-panel py-8 px-6 sm:px-10 rounded-3xl shadow-2xl border border-slate-800/40 relative">
          {children}
        </div>
      </div>
    </div>
  );
};
