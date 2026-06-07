import React, { useState } from 'react';
import { Settings, Save, Sliders, Database, Eye, Globe } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export const SettingsPage = () => {
  const [dataInterval, setDataInterval] = useState('Hourly');
  const [modelWeight, setModelWeight] = useState(60);

  const intervals = ['Real-time', 'Hourly', 'Daily', 'Weekly'];

  return (
    <div className="space-y-8">
      {/* Settings Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div>
          <h2 className="text-xl font-bold font-display text-white">System Settings</h2>
          <p className="text-xs text-slate-400 mt-1">Configure parameters for background scrapers, API endpoints, and econometric models.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model variables tuning */}
        <Card className="lg:col-span-2 space-y-6">
          <h3 className="text-base font-bold font-display text-white mb-2">Global Pipeline Controls</h3>
          
          <div className="space-y-5">
            {/* Model Weight */}
            <div>
              <div className="flex justify-between items-center text-xs font-semibold mb-2">
                <span className="text-slate-300">Model weight (FRED vs agricultural sentiment)</span>
                <span className="text-cyan-400 font-bold">{modelWeight}% FRED</span>
              </div>
              <input 
                type="range" 
                min="20" 
                max="80" 
                value={modelWeight}
                onChange={(e) => setModelWeight(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-500" 
              />
              <span className="text-[10px] text-slate-500 leading-relaxed block mt-1">
                Specifies how heavily predictions should lean on interest rates (FRED) versus news analysis sentiment index updates.
              </span>
            </div>

            {/* Ingestion Intervals */}
            <div className="pt-4 border-t border-slate-900">
              <span className="text-xs font-bold text-slate-300 block mb-2.5">API Ingest Frequency</span>
              <div className="flex gap-2 bg-slate-950 p-1 rounded-xl border border-slate-900 w-fit">
                {intervals.map((item) => (
                  <button
                    key={item}
                    onClick={() => setDataInterval(item)}
                    className={`px-4 py-1.5 rounded-lg text-2xs font-semibold transition-all ${
                      dataInterval === item ? 'bg-cyan-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>

            {/* API Endpoints mock */}
            <div className="pt-4 border-t border-slate-900 space-y-3">
              <span className="text-xs font-bold text-slate-300 block">Third-Party Data Connections</span>
              <div className="space-y-3 text-2xs">
                <div className="flex justify-between items-center p-3 rounded-xl bg-slate-950/45 border border-slate-900">
                  <span className="text-slate-400 font-semibold">FRED Macroeconomic Database</span>
                  <span className="text-emerald-400 font-bold">Connected</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded-xl bg-slate-950/45 border border-slate-900">
                  <span className="text-slate-400 font-semibold">Bureau of Labor Statistics Feed</span>
                  <span className="text-emerald-400 font-bold">Connected</span>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Global actions card */}
        <Card className="h-fit space-y-6">
          <h3 className="text-base font-bold font-display text-white">Save Configurations</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Changes to model weights will take effect immediately. Recalculation triggers will execute in the background.
          </p>

          <Button className="w-full flex justify-center items-center gap-2">
            <Save size={16} /> Save settings
          </Button>
        </Card>
      </div>
    </div>
  );
};
