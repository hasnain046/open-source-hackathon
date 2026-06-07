import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Home } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-6 mesh-bg">
      <div className="glass-panel max-w-md w-full p-8 rounded-3xl text-center border border-slate-900 shadow-2xl">
        <div className="w-16 h-16 rounded-2xl bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center justify-center mx-auto mb-6">
          <AlertTriangle size={32} />
        </div>
        
        <h1 className="font-display font-black text-3xl text-white">404 Error</h1>
        <h2 className="text-sm font-semibold text-slate-400 mt-2">Macroeconomic Indicator Not Found</h2>
        
        <p className="text-xs text-slate-500 mt-4 leading-relaxed">
          The reporting pipeline could not resolve this specific route. The database registry may have shifted during model optimization syncs.
        </p>

        <div className="mt-8 flex gap-3 justify-center">
          <Button 
            onClick={() => navigate('/')}
            variant="secondary"
            className="flex items-center gap-1.5 text-xs"
          >
            <Home size={14} /> Home
          </Button>
          <Button 
            onClick={() => navigate('/dashboard')}
            className="text-xs"
          >
            Back to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
};
