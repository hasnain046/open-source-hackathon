import React from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, BrainCircuit, LineChart, Globe, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 relative overflow-hidden mesh-bg">
      {/* Navbar overlay */}
      <header className="absolute top-0 inset-x-0 py-6 px-6 md:px-12 flex justify-between items-center z-50">
        <div className="flex items-center gap-2.5">
          <TrendingUp size={24} className="text-cyan-400" />
          <span className="font-display font-black text-xl text-white">InflationIQ</span>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate('/login')}
            className="text-slate-400 hover:text-white text-sm font-semibold transition-colors"
          >
            Sign In
          </button>
          <Button 
            onClick={() => navigate('/register')}
            variant="glass"
            size="sm"
          >
            Launch Console
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 md:px-12 text-center max-w-5xl mx-auto flex flex-col items-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold mb-6 animate-bounce">
          <Sparkles size={14} /> Next-Generation Economic Forecasting
        </div>
        
        <h1 className="font-display font-extrabold text-5xl md:text-7xl text-white leading-tight tracking-tight max-w-4xl">
          Real-time Inflation <br className="hidden md:inline" />
          <span className="bg-gradient-to-r from-cyan-400 via-indigo-400 to-rose-400 bg-clip-text text-transparent">
            AI Economic Intelligence
          </span>
        </h1>
        
        <p className="mt-6 text-slate-400 text-base md:text-lg max-w-2xl leading-relaxed">
          Predict Consumer Price Index shifts, analyze local inflation variations, query the AI Economist Copilot, and simulate market shocks with enterprise-grade explainability.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center w-full max-w-md">
          <Button 
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 group justify-center"
            size="lg"
          >
            Explore Dashboard <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
          </Button>
          <Button 
            onClick={() => navigate('/login')}
            variant="secondary"
            size="lg"
            className="justify-center"
          >
            Request Sandbox Access
          </Button>
        </div>

        {/* Live Status Indicators */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6 w-full max-w-4xl border-t border-slate-900 pt-10">
          <div className="text-center">
            <span className="block text-3xl font-bold text-white font-display">4.82%</span>
            <span className="text-xs text-slate-500 font-semibold tracking-wide uppercase mt-1 block">Current CPI Rate</span>
          </div>
          <div className="text-center">
            <span className="block text-3xl font-bold text-cyan-400 font-display">94.5%</span>
            <span className="text-xs text-slate-500 font-semibold tracking-wide uppercase mt-1 block">Forecast Accuracy</span>
          </div>
          <div className="text-center">
            <span className="block text-3xl font-bold text-indigo-400 font-display">FRED & BLS</span>
            <span className="text-xs text-slate-500 font-semibold tracking-wide uppercase mt-1 block">Ingested Sources</span>
          </div>
          <div className="text-center">
            <span className="block text-3xl font-bold text-emerald-400 font-display">&lt; 100ms</span>
            <span className="text-xs text-slate-500 font-semibold tracking-wide uppercase mt-1 block">Simulation Latency</span>
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="py-20 px-6 md:px-12 max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="font-display font-extrabold text-3xl md:text-4xl text-white">Engineered for Macro Analysts</h2>
          <p className="text-slate-400 text-sm mt-3">All critical inflation analytics, modeling tools, and forecasting vectors in a unified platform.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="glass-panel p-8 rounded-2xl border border-slate-800/40 relative">
            <div className="p-3.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 w-fit mb-6">
              <LineChart size={24} />
            </div>
            <h3 className="font-display font-bold text-lg text-white">LSTM Inflation Forecasting</h3>
            <p className="text-slate-400 text-xs mt-3 leading-relaxed">
              Leverage deep learning models to project headline CPI metrics for the next 12 months, complete with high and low confidence boundaries.
            </p>
          </div>

          <div className="glass-panel p-8 rounded-2xl border border-slate-800/40 relative">
            <div className="p-3.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 w-fit mb-6">
              <BrainCircuit size={24} />
            </div>
            <h3 className="font-display font-bold text-lg text-white">AI Economist Copilot</h3>
            <p className="text-slate-400 text-xs mt-3 leading-relaxed">
              Interact with a custom RAG-grounded economic assistant fed with policy documents, market reviews, and historical data points.
            </p>
          </div>

          <div className="glass-panel p-8 rounded-2xl border border-slate-800/40 relative">
            <div className="p-3.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20 w-fit mb-6">
              <Globe size={24} />
            </div>
            <h3 className="font-display font-bold text-lg text-white">Scenario Shock Simulator</h3>
            <p className="text-slate-400 text-xs mt-3 leading-relaxed">
              Tune sliders for interest rates, crude oil costs, and exchange rate variations to immediately compute projected impacts on general prices.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-slate-900 text-center text-xs text-slate-600">
        <p>&copy; {new Date().getFullYear()} InflationIQ. Built for research purposes. All market projections are mock parameters.</p>
      </footer>
    </div>
  );
};
