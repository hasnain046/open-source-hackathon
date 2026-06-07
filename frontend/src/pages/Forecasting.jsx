import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, Legend, AreaChart, Area 
} from 'recharts';
import { 
  BrainCircuit, TrendingDown, TrendingUp, Cpu, Settings2 
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { fetchPredictions } from '../store/slices/forecastSlice';

export const Forecasting = () => {
  const dispatch = useDispatch();
  const { predictions, loading, error } = useSelector((state) => state.forecast);
  const [selectedModel, setSelectedModel] = useState('lstm'); // 'lstm' | 'prophet' | 'ensemble'

  useEffect(() => {
    dispatch(fetchPredictions());
  }, [dispatch]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-cyan-500/20 border-t-cyan-500 animate-spin" />
        <p className="text-sm text-slate-400 font-semibold uppercase tracking-wider animate-pulse">Running predictive projection systems...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 max-w-2xl mx-auto text-center space-y-4">
        <h3 className="text-lg font-bold text-rose-400 font-display">Forecasting Offline</h3>
        <p className="text-xs text-slate-400">{typeof error === 'string' ? error : 'Failed to query machine learning forecasting predictions.'}</p>
        <Button onClick={() => dispatch(fetchPredictions())} size="sm">Retry Predictions</Button>
      </div>
    );
  }

  const data = predictions || {};
  
  // Parse monthly forecast rows from backend. If empty, fall back to default template.
  const forecastList = data.forecasts || [
    { month: 'Jan 2026', historical: 5.7, lstm: 5.7, prophet: 5.7, upper: 5.9, lower: 5.5 },
    { month: 'Feb 2026', historical: 5.6, lstm: 5.61, prophet: 5.58, upper: 5.8, lower: 5.4 },
    { month: 'Mar 2026', historical: 5.8, lstm: 5.79, prophet: 5.82, upper: 6.0, lower: 5.6 },
    { month: 'Apr 2026', historical: 5.9, lstm: 5.88, prophet: 5.91, upper: 6.1, lower: 5.7 },
    { month: 'May 2026', historical: 5.85, lstm: 5.82, prophet: 5.86, upper: 6.05, lower: 5.65 },
    { month: 'Jun 2026', historical: 5.82, lstm: 5.78, prophet: 5.80, upper: 6.02, lower: 5.58 },
    { month: 'Jul 2026', historical: null, lstm: 5.75, prophet: 5.72, upper: 5.95, lower: 5.51 },
    { month: 'Aug 2026', historical: null, lstm: 5.71, prophet: 5.68, upper: 5.92, lower: 5.45 },
    { month: 'Sep 2026', historical: null, lstm: 5.68, prophet: 5.63, upper: 5.90, lower: 5.40 },
    { month: 'Oct 2026', historical: null, lstm: 5.62, prophet: 5.59, upper: 5.85, lower: 5.35 },
    { month: 'Nov 2026', historical: null, lstm: 5.58, prophet: 5.55, upper: 5.82, lower: 5.30 },
    { month: 'Dec 2026', historical: null, lstm: 5.52, prophet: 5.49, upper: 5.78, lower: 5.22 }
  ];

  const summary = data.summary || {
    lstmForecastNextMonth: 5.75,
    prophetForecastNextMonth: 5.72,
    confidenceScore: 94.5,
    direction: 'Downward',
    trajectoryChange: -0.47,
    mape: '1.85%'
  };

  const chartData = forecastList.map(item => ({
    name: item.month,
    "Historical CPI": item.historical,
    "LSTM Prediction": item.lstm,
    "Prophet Prediction": item.prophet,
    "Confidence Upper": item.upper,
    "Confidence Lower": item.lower,
  }));

  const selectedModelLabel = selectedModel === 'lstm' ? 'LSTM Neural Engine' : selectedModel === 'prophet' ? 'Prophet Additive' : 'Weighted Ensemble';

  return (
    <div className="space-y-8">
      {/* Page header controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div>
          <h2 className="text-xl font-bold font-display text-white">Forecasting Playground</h2>
          <p className="text-xs text-slate-400 mt-1">Simulate short-term predictive modeling using deep learning and additive parameters.</p>
        </div>
        
        {/* Model Select Buttons */}
        <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-900">
          <button
            onClick={() => setSelectedModel('lstm')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${selectedModel === 'lstm' ? 'bg-cyan-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'}`}
          >
            LSTM Neural Network
          </button>
          <button
            onClick={() => setSelectedModel('prophet')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${selectedModel === 'prophet' ? 'bg-cyan-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'}`}
          >
            Prophet Model
          </button>
          <button
            onClick={() => setSelectedModel('ensemble')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${selectedModel === 'ensemble' ? 'bg-cyan-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'}`}
          >
            AI Ensemble (50/50)
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Projection Next Month"
          value={selectedModel === 'lstm' ? summary.lstmForecastNextMonth : summary.prophetForecastNextMonth}
          change={-0.07}
          trend="down"
          subtitle="Jul 2026 Expected Rate"
          icon={BrainCircuit}
          status="positive"
        />
        <MetricCard
          title="Model Confidence Score"
          value={`${summary.confidenceScore}%`}
          change={1.2}
          trend="up"
          subtitle="Model Backtest Validation"
          icon={Cpu}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="Forecast Direction"
          value={summary.direction}
          change={summary.trajectoryChange}
          trend={summary.trajectoryChange > 0 ? 'up' : 'down'}
          subtitle="Next 6-Month Trajectory"
          icon={TrendingDown}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="Aggregate Error (MAPE)"
          value={summary.mape}
          change={-0.12}
          trend="down"
          subtitle="Mean Abs Percentage Error"
          icon={Settings2}
          isPercentage={false}
          status="positive"
        />
      </div>

      {/* Main Prediction Chart */}
      <Card>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h3 className="text-lg font-bold font-display text-white">12-Month Projection Horizon & Uncertainty Bounds</h3>
            <p className="text-xs text-slate-500 mt-0.5">Shaded regions depict the 95% forecast confidence boundaries. Model type: <strong className="text-cyan-400">{selectedModelLabel}</strong>.</p>
          </div>
          
          <div className="flex items-center gap-4 text-xs font-semibold text-slate-400">
            <span className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-cyan-400 inline-block" /> Historical</span>
            <span className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-indigo-400 stroke-dasharray inline-block" /> Projection</span>
            <span className="flex items-center gap-1.5"><span className="w-3.5 h-3 bg-indigo-500/10 inline-block rounded-sm border border-indigo-500/20" /> Confidence Interval</span>
          </div>
        </div>

        <div className="h-96 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.12}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0.01}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} domain={[3.5, 6.5]} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#0f172a', 
                  borderColor: '#334155', 
                  borderRadius: '12px',
                  color: '#f8fafc',
                  fontSize: '12px'
                }} 
              />
              <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
              
              {/* Shaded Area for confidence intervals */}
              <Area 
                type="monotone" 
                dataKey="Confidence Upper" 
                stroke="transparent" 
                fill="url(#colorConfidence)" 
                legendType="none"
              />
              <Area 
                type="monotone" 
                dataKey="Confidence Lower" 
                stroke="transparent" 
                fill="#0f172a" 
                legendType="none"
              />
              
              <Line 
                type="monotone" 
                dataKey="Historical CPI" 
                stroke="#06b6d4" 
                strokeWidth={3} 
                dot={{ r: 4, stroke: '#06b6d4', strokeWidth: 1, fill: '#0f172a' }}
                activeDot={{ r: 6 }}
              />
              
              {(selectedModel === 'lstm' || selectedModel === 'ensemble') && (
                <Line 
                  type="monotone" 
                  dataKey="LSTM Prediction" 
                  stroke="#6366f1" 
                  strokeWidth={2} 
                  strokeDasharray="5 5"
                  dot={{ r: 2 }}
                />
              )}
              
              {(selectedModel === 'prophet' || selectedModel === 'ensemble') && (
                <Line 
                  type="monotone" 
                  dataKey="Prophet Prediction" 
                  stroke="#f59e0b" 
                  strokeWidth={2} 
                  strokeDasharray="4 4"
                  dot={{ r: 2 }}
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Breakdown Tabulations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model configurations */}
        <Card className="lg:col-span-1">
          <h3 className="text-base font-bold font-display text-white mb-4">Neural Architecture Weights</h3>
          <p className="text-xs text-slate-500 mb-6">Modify default model weightings and optimizer hyperparameters (Visual Sandbox).</p>
          
          <div className="space-y-5">
            <div>
              <div className="flex justify-between items-center text-xs font-semibold mb-2">
                <span className="text-slate-400">Sequence Ingestion Window</span>
                <span className="text-cyan-400">12 Months</span>
              </div>
              <input type="range" min="3" max="36" defaultValue="12" className="w-full h-1 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-500" />
            </div>

            <div>
              <div className="flex justify-between items-center text-xs font-semibold mb-2">
                <span className="text-slate-400">Weighting (FRED Ingest vs BLS)</span>
                <span className="text-cyan-400">60% Ingest</span>
              </div>
              <input type="range" min="10" max="90" defaultValue="60" className="w-full h-1 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-500" />
            </div>

            <div>
              <div className="flex justify-between items-center text-xs font-semibold mb-2">
                <span className="text-slate-400">LSTM Learning Rate</span>
                <span className="text-cyan-400">0.001</span>
              </div>
              <input type="range" min="1" max="10" defaultValue="5" className="w-full h-1 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-500" />
            </div>

            <div className="pt-4 border-t border-slate-900">
              <Button className="w-full text-xs py-2">Retrain Hyperparameters</Button>
            </div>
          </div>
        </Card>

        {/* Detailed forecasting data table */}
        <Card className="lg:col-span-2">
          <h3 className="text-base font-bold font-display text-white mb-4">Monthly Value Matrix</h3>
          <p className="text-xs text-slate-500 mb-6">Raw index predictions generated by the active model runtime.</p>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="pb-3">Forecasted Period</th>
                  <th className="pb-3">LSTM Forecast</th>
                  <th className="pb-3">Prophet Forecast</th>
                  <th className="pb-3 text-right">Confidence Bounds</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/40 text-xs">
                {forecastList.slice(5, 12).map((item, index) => (
                  <tr key={index} className="hover:bg-slate-900/10 transition-colors">
                    <td className="py-2.5 font-semibold text-slate-300">{item.month}</td>
                    <td className="py-2.5 text-indigo-400 font-bold">{item.lstm}%</td>
                    <td className="py-2.5 text-amber-500 font-semibold">{item.prophet}%</td>
                    <td className="py-2.5 text-right text-slate-400 font-semibold">{item.lower}% &mdash; {item.upper}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
};

