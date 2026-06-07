import React from 'react';

export const Footer = () => {
  return (
    <footer className="py-6 px-8 border-t border-slate-900 bg-slate-950/20 text-slate-500 text-xs flex flex-col md:flex-row justify-between items-center gap-4">
      <div>
        <p>&copy; {new Date().getFullYear()} InflationIQ. All rights reserved. Econometric predictions are based on mock model configurations.</p>
      </div>
      <div className="flex gap-6 font-semibold">
        <a href="#privacy" className="hover:text-cyan-400 transition-colors">Privacy Charter</a>
        <a href="#terms" className="hover:text-cyan-400 transition-colors">Data Licensing</a>
        <a href="#api" className="hover:text-cyan-400 transition-colors">Developer Sandbox</a>
        <span className="text-slate-600">v1.2.4 (Beta)</span>
      </div>
    </footer>
  );
};
