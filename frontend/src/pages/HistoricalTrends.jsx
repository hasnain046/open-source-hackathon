import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, Legend 
} from 'recharts';
import { History, Calendar, Award, Flame } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import api from '../services/api';

export const HistoricalTrends = () => {
  const [timeframe, setTimeframe] = useState('5Y'); // '1Y' | '3Y' | '5Y' | 'MAX'
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchTrends = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/trends/timeline');
      setTrends(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch historical trends.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-cyan-500/20 border-t-cyan-500 animate-spin" />
        <p className="text-sm text-slate-400 font-semibold uppercase tracking-wider animate-pulse">Analyzing historical macro timelines...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 max-w-2xl mx-auto text-center space-y-4">
        <h3 className="text-lg font-bold text-rose-400 font-display">Ingestion Failed</h3>
        <p className="text-xs text-slate-400">{error}</p>
        <Button onClick={fetchTrends} size="sm">Retry Sync</Button>
      </div>
    );
  }

  const data = trends || {};

  const timelinePoints = data.timeline || [
    { date: '2022 Q1', inflation: 6.2, food: 5.8, fuel: 8.5, core: 5.9 },
    { date: '2022 Q2', inflation: 7.01, food: 6.5, fuel: 12.1, core: 6.2 },
    { date: '2022 Q3', inflation: 6.8, food: 6.2, fuel: 10.5, core: 6.0 },
    { date: '2022 Q4', inflation: 6.5, food: 5.9, fuel: 9.8, core: 5.8 },
    { date: '2023 Q1', inflation: 6.1, food: 5.5, fuel: 8.0, core: 5.6 },
    { date: '2023 Q2', inflation: 5.8, food: 5.2, fuel: 7.2, core: 5.4 },
    { date: '2023 Q3', inflation: 5.5, food: 5.0, fuel: 6.5, core: 5.3 },
    { date: '2023 Q4', inflation: 5.4, food: 4.9, fuel: 5.8, core: 5.2 },
    { date: '2024 Q1', inflation: 5.2, food: 4.8, fuel: 4.2, core: 5.1 },
    { date: '2024 Q2', inflation: 5.1, food: 4.7, fuel: 3.8, core: 5.1 }
  ];

  const summary = data.summary || {
    maxInflation: '7.01%',
    minInflation: '3.33%',
    annualGrowth: '7.30%',
    avgInflation: '5.12%'
  };

  const decadalGrowth = data.decadal_growth || [
    { year: '2025', rate: 5.12, growth: 7.30 },
    { year: '2024', rate: 5.20, growth: 7.00 },
    { year: '2023', rate: 5.70, growth: 6.80 },
    { year: '2022', rate: 6.70, growth: 7.20 },
    { year: '2021', rate: 5.10, growth: 8.90 },
    { year: '2020', rate: 6.60, growth: -5.80 }
  ];

  // Filter timeframe
  const getFilteredData = () => {
    if (timeframe === '1Y') return timelinePoints.slice(-4);
    if (timeframe === '3Y') return timelinePoints.slice(-8);
    return timelinePoints;
  };

  return (
    <div className="space-y-8">
      {/* Page Header and timeline filters */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div>
          <h2 className="text-xl font-bold font-display text-white">Historical Trends & Macro Cycles</h2>
          <p className="text-xs text-slate-400 mt-1">Examine cyclical macroeconomic waves over quarterly, yearly, and multi-decade regimes.</p>
        </div>

        {/* Timeline Selector */}
        <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-900">
          {['1Y', '3Y', '5Y', 'MAX'].map((t) => (
            <button
              key={t}
              onClick={() => setTimeframe(t)}
              className={`px-4.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                timeframe === t ? 'bg-cyan-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Metric summaries of cycles */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Historical Max Inflation"
          value={summary.maxInflation}
          change={2.19}
          trend="up"
          subtitle="Peak reached in June 2022"
          icon={Flame}
          isPercentage={false}
          status="negative"
        />
        <MetricCard
          title="Historical Min Inflation"
          value={summary.minInflation}
          change={-1.49}
          trend="down"
          subtitle="Trough reached in 2017"
          icon={Award}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="Annual Growth Rate"
          value={summary.annualGrowth}
          change={0.20}
          trend="up"
          subtitle="Average real GDP growth rate"
          icon={Calendar}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="Average Inflation Rate"
          value={summary.avgInflation}
          change={0.30}
          trend="up"
          subtitle="Aggregate average across 5 years"
          icon={History}
          isPercentage={false}
          status="neutral"
        />
      </div>

      {/* Main comparative trend chart */}
      <Card>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h3 className="text-lg font-bold font-display text-white">Comparative CPI Timelines</h3>
            <p className="text-xs text-slate-500 mt-0.5">Plotting aggregate Headline CPI alongside core, agricultural, and energy sub-indices.</p>
          </div>
        </div>

        <div className="h-96 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={getFilteredData()} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} domain={['auto', 'auto']} />
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
              
              <Line type="monotone" dataKey="inflation" name="Headline CPI" stroke="#06b6d4" strokeWidth={3} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="food" name="Food Sub-Index" stroke="#10b981" strokeWidth={1.5} dot={{ r: 2 }} />
              <Line type="monotone" dataKey="fuel" name="Fuel & Light Index" stroke="#f59e0b" strokeWidth={1.5} dot={{ r: 2 }} />
              <Line type="monotone" dataKey="core" name="Core Index (Excl. Food/Fuel)" stroke="#6366f1" strokeWidth={1.5} dot={{ r: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Decadal Growth Cycles list */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Economic Cycles Info Card */}
        <Card className="lg:col-span-1">
          <h3 className="text-base font-bold font-display text-white mb-4">Macro Regime Identifications</h3>
          <p className="text-xs text-slate-500 mb-6">Cycles identified by our trend parsing pipeline filters.</p>
          
          <div className="space-y-4">
            <div className="p-3.5 rounded-xl bg-slate-950/40 border border-slate-900">
              <span className="text-[10px] font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-md">2022 Peak Shock</span>
              <p className="text-xs font-bold text-slate-200 mt-2">Post-pandemic reopening + energy shock.</p>
              <p className="text-2xs text-slate-400 mt-0.5">Headline inflation spiked to 7.01% as fuel indices surged over 12%.</p>
            </div>
            
            <div className="p-3.5 rounded-xl bg-slate-950/40 border border-slate-900">
              <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md">2024 Stable Plateau</span>
              <p className="text-xs font-bold text-slate-200 mt-2">Monetary tightening stability.</p>
              <p className="text-2xs text-slate-400 mt-0.5">Inflation consolidated around 5.10% as global crude oil imports eased back.</p>
            </div>
          </div>
        </Card>

        {/* Historical rates over the years */}
        <Card className="lg:col-span-2">
          <h3 className="text-base font-bold font-display text-white mb-4">Decadal Inflation & Real GDP Metrics</h3>
          <p className="text-xs text-slate-500 mb-6">Historical year-on-year averages showing growth correlations.</p>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="pb-3">Economic Year</th>
                  <th className="pb-3">Average Inflation (CPI)</th>
                  <th className="pb-3 text-right">Real GDP Growth Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/40 text-xs">
                {decadalGrowth.map((trend, index) => (
                  <tr key={index} className="hover:bg-slate-900/10 transition-colors">
                    <td className="py-2.5 font-bold text-slate-300">{trend.year}</td>
                    <td className="py-2.5 text-cyan-400 font-bold">{trend.rate}%</td>
                    <td className={`py-2.5 text-right font-bold ${trend.growth > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {trend.growth}%
                    </td>
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

