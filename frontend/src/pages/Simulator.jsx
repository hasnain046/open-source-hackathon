import React, { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import api from '../services/api';

export const Simulator = () => {
  const [crudeChange, setCrudeChange] = useState(0); // in $/bbl change (-30 to +50)
  const [rateChange, setRateChange] = useState(0); // in bps change (-200 to +300)
  const [currencyChange, setCurrencyChange] = useState(0); // in % strength (-15% to +15%)
  
  const [simulatedRate, setSimulatedRate] = useState(4.82);
  const [rateDifference, setRateDifference] = useState(0.0);
  const [threat, setThreat] = useState({ label: 'Macro Equilibrium', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' });
  const [loading, setLoading] = useState(false);

  // Constants representing baseline parameters
  const BASE_CRUDE = 77.80;
  const BASE_RATE = 6.50;
  const BASE_USD = 82.52;

  const runSimulation = async () => {
    setLoading(true);
    try {
      const response = await api.post('/simulator/shock', {
        crude_change: crudeChange,
        rate_change: rateChange,
        currency_change: currencyChange
      });
      const data = response.data;
      setSimulatedRate(data.simulated_rate);
      setRateDifference(data.rate_difference);
      
      const score = data.simulated_rate;
      if (score > 6.0) {
        setThreat({ label: 'Hyper-Inflation Threat', color: 'text-rose-400 bg-rose-500/10 border-rose-500/20' });
      } else if (score > 5.0) {
        setThreat({ label: 'Elevated Pressure', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' });
      } else if (score < 3.5) {
        setThreat({ label: 'Deflation Risk', color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20' });
      } else {
        setThreat({ label: 'Macro Equilibrium', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' });
      }
    } catch (err) {
      console.error('Failed to run simulation shock modeling:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      runSimulation();
    }, 400);

    return () => clearTimeout(delayDebounceFn);
  }, [crudeChange, rateChange, currencyChange]);

  const resetSliders = () => {
    setCrudeChange(0);
    setRateChange(0);
    setCurrencyChange(0);
  };

  return (
    <div className="space-y-8">
      {/* Simulation Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div>
          <h2 className="text-xl font-bold font-display text-white">Scenario Shock Simulator</h2>
          <p className="text-xs text-slate-400 mt-1">Adjust macro variables to observe their cumulative pass-through effects on the CPI index.</p>
        </div>
        <Button 
          onClick={resetSliders}
          variant="glass" 
          size="sm"
        >
          Reset Baseline
        </Button>
      </div>

      {/* Primary Outputs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Simulated CPI Rate"
          value={simulatedRate}
          change={rateDifference}
          trend={rateDifference >= 0 ? 'up' : 'down'}
          subtitle={loading ? "Computing metrics..." : "Simulated Projected rate"}
          icon={Activity}
          status={rateDifference === 0 ? 'neutral' : rateDifference < 0 ? 'positive' : 'negative'}
        />

        <Card className="md:col-span-2 flex flex-col justify-center">
          <div className="flex justify-between items-start gap-4">
            <div>
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Policy Assessment</span>
              <h3 className="text-lg font-bold font-display text-white mt-1">Impact Commentary</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                {rateDifference > 0 ? (
                  <span>A net increase of <strong className="text-rose-400">+{rateDifference}%</strong> in prices would likely prompt the Central Bank to raise the policy repo rate by at least 50 bps in the subsequent cycle to anchor inflation expectations.</span>
                ) : rateDifference < 0 ? (
                  <span>A price decline of <strong className="text-emerald-400">{rateDifference}%</strong> signals structural cooling. This would open up room for borrowing cuts, spurring private investment and consumer credit expansion.</span>
                ) : (
                  <span>The platform is sitting at the verified econometrics baseline. Adjust the sliders below to run structural shock assessments.</span>
                )}
              </p>
            </div>
            
            <div className={`shrink-0 border px-3 py-1.5 rounded-xl text-xs font-bold ${threat.color}`}>
              {threat.label}
            </div>
          </div>
        </Card>
      </div>

      {/* Input controls split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sliders panel */}
        <Card className="lg:col-span-2 space-y-7">
          <h3 className="text-base font-bold font-display text-white mb-2">Adjust Shock Variables</h3>

          {/* Slider 1: Crude Oil */}
          <div className="space-y-3">
            <div className="flex justify-between items-center text-xs font-semibold">
              <span className="text-slate-300">Brent Crude Price Adjustment</span>
              <span className="text-cyan-400 font-bold">
                {crudeChange >= 0 ? '+' : ''}${crudeChange}/bbl (Total: ${parseFloat((BASE_CRUDE + crudeChange).toFixed(1))})
              </span>
            </div>
            <input 
              type="range" 
              min="-30" 
              max="50" 
              value={crudeChange}
              onChange={(e) => setCrudeChange(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-500" 
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-bold uppercase">
              <span>-$30 (Over-supply)</span>
              <span>Baseline (${BASE_CRUDE})</span>
              <span>+$50 (Supply shock)</span>
            </div>
          </div>

          {/* Slider 2: Interest Rates */}
          <div className="space-y-3">
            <div className="flex justify-between items-center text-xs font-semibold">
              <span className="text-slate-300">Monetary Policy Rate Adjustment</span>
              <span className="text-cyan-400 font-bold">
                {rateChange >= 0 ? '+' : ''}{rateChange} bps (Total: {parseFloat(((BASE_RATE * 100 + rateChange) / 100).toFixed(2))}%)
              </span>
            </div>
            <input 
              type="range" 
              min="-200" 
              max="300" 
              value={rateChange}
              onChange={(e) => setRateChange(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-500" 
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-bold uppercase">
              <span>-200 bps (Easing)</span>
              <span>Baseline ({BASE_RATE}%)</span>
              <span>+300 bps (Tightening)</span>
            </div>
          </div>

          {/* Slider 3: Currency Strength */}
          <div className="space-y-3">
            <div className="flex justify-between items-center text-xs font-semibold">
              <span className="text-slate-300">Local Currency Strength (vs USD)</span>
              <span className="text-cyan-400 font-bold">
                {currencyChange >= 0 ? '+' : ''}{currencyChange}% (USD/INR: {parseFloat((BASE_USD * (1 - currencyChange / 100)).toFixed(2))})
              </span>
            </div>
            <input 
              type="range" 
              min="-15" 
              max="15" 
              value={currencyChange}
              onChange={(e) => setCurrencyChange(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-500" 
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-bold uppercase">
              <span>-15% (Depreciation)</span>
              <span>Baseline ({BASE_USD})</span>
              <span>+15% (Appreciation)</span>
            </div>
          </div>
        </Card>

        {/* Shock Impact Breakdown Cards */}
        <Card className="space-y-4">
          <h3 className="text-base font-bold font-display text-white mb-2">Estimated Sector Spreads</h3>
          
          <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Industrial Output Impact</span>
            <p className="text-xs text-slate-200 font-semibold mt-1">
              {rateChange > 150 ? 'Stunted Growth. Borrowing expenses limit capital expenditure programs.' : 'Operational Baseline. Standard credit conditions persist.'}
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Import Spending Profile</span>
            <p className="text-xs text-slate-200 font-semibold mt-1">
              {currencyChange < -5 || crudeChange > 20 ? 'Deficit Expansion. Weak exchange rate increases landed crude bills.' : 'Balanced. Imports tracking within treasury forecasts.'}
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Consumer Discretionary Demand</span>
            <p className="text-xs text-slate-200 font-semibold mt-1">
              {simulatedRate > 5.5 ? 'Contraction expected as household budgets re-allocate to cover food.' : 'Stable household credit expansions.'}
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

