import React, { useState, useEffect } from 'react';
import { Map, MapPin, Compass, Sparkles } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import api from '../services/api';

export const Heatmap = () => {
  const [filterRegion, setFilterRegion] = useState('All');
  const [heatmapData, setHeatmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchHeatmap = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/heatmap/matrix');
      setHeatmapData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch regional heatmap metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHeatmap();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-cyan-500/20 border-t-cyan-500 animate-spin" />
        <p className="text-sm text-slate-400 font-semibold uppercase tracking-wider animate-pulse">Ingesting regional geographic coordinates...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 max-w-2xl mx-auto text-center space-y-4">
        <h3 className="text-lg font-bold text-rose-400 font-display">Ingest Failed</h3>
        <p className="text-xs text-slate-400">{error}</p>
        <Button onClick={fetchHeatmap} size="sm">Retry Sync</Button>
      </div>
    );
  }

  const regionalInflation = heatmapData?.regions || [
    { state: 'Delhi', region: 'North', currentRate: 5.10, yearAgoRate: 5.40, status: 'High' },
    { state: 'Tamil Nadu', region: 'South', currentRate: 5.25, yearAgoRate: 5.10, status: 'High' },
    { state: 'Maharashtra', region: 'West', currentRate: 4.10, yearAgoRate: 4.50, status: 'Low' },
    { state: 'West Bengal', region: 'East', currentRate: 5.42, yearAgoRate: 5.20, status: 'High' },
    { state: 'Madhya Pradesh', region: 'Central', currentRate: 4.52, yearAgoRate: 4.70, status: 'Medium' }
  ];

  const summary = heatmapData?.summary || {
    highestState: 'West Bengal',
    highestRegion: 'East',
    highestRate: 5.42,
    lowestState: 'Maharashtra',
    lowestRegion: 'West',
    lowestRate: 4.10,
    deviation: '1.38%',
    monitoredCount: regionalInflation.length
  };

  // Filter states
  const filteredStates = regionalInflation.filter(item => {
    return filterRegion === 'All' || item.region === filterRegion;
  });

  // Sort states by rate descending
  const sortedStates = [...filteredStates].sort((a, b) => b.currentRate - a.currentRate);

  return (
    <div className="space-y-8">
      {/* Top filter bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div>
          <h2 className="text-xl font-bold font-display text-white">Regional Inflation Heatmap</h2>
          <p className="text-xs text-slate-400 mt-1">Monitor inflation discrepancies across Indian geographical territories and identify supply-chain bottlenecks.</p>
        </div>

        {/* Region selector */}
        <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-900">
          {['All', 'North', 'South', 'West', 'East', 'Central'].map((region) => (
            <button
              key={region}
              onClick={() => setFilterRegion(region)}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                filterRegion === region ? 'bg-cyan-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              {region}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Highest Regional Inflation"
          value={`${summary.highestRate}%`}
          change={0.12}
          trend="up"
          subtitle={`${summary.highestState} (${summary.highestRegion})`}
          icon={MapPin}
          isPercentage={false}
          status="negative"
        />
        <MetricCard
          title="Lowest Regional Inflation"
          value={`${summary.lowestRate}%`}
          change={-0.34}
          trend="down"
          subtitle={`${summary.lowestState} (${summary.lowestRegion})`}
          icon={Compass}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="National Deviation"
          value={summary.deviation}
          change={0.05}
          trend="up"
          subtitle="Variance between states"
          icon={Sparkles}
          isPercentage={false}
          status="neutral"
        />
        <MetricCard
          title="Monitored Territories"
          value={summary.monitoredCount}
          change={0}
          trend="stable"
          subtitle="Ingesting state-level CPI indices"
          icon={Map}
          isPercentage={false}
          status="neutral"
        />
      </div>

      {/* Layout Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interactive SVG Choropleth Map representation */}
        <Card className="lg:col-span-2 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold font-display text-white mb-2">Regional Geographical Distribution</h3>
            <p className="text-xs text-slate-500 mb-6">Visual model detailing consumer pressure zones across five major sectors.</p>
          </div>

          {/* Choropleth SVG Mock layout */}
          <div className="h-80 w-full flex items-center justify-center bg-slate-950/40 rounded-2xl border border-slate-900 relative p-6">
            <svg viewBox="0 0 400 400" className="w-full h-full max-h-72 opacity-85">
              {/* North Region */}
              <path 
                d="M 120,40 L 220,40 L 220,120 L 120,120 Z" 
                fill={filterRegion === 'North' || filterRegion === 'All' ? '#f43f5e' : '#1e293b'} 
                stroke="#0f172a" 
                strokeWidth={2.5}
                opacity={0.3}
              />
              <text x="170" y="85" fill="#f8fafc" fontSize="10" fontWeight="bold" textAnchor="middle">NORTH (5.10%)</text>

              {/* South Region */}
              <path 
                d="M 120,240 L 220,240 L 220,360 L 120,360 Z" 
                fill={filterRegion === 'South' || filterRegion === 'All' ? '#f43f5e' : '#1e293b'} 
                stroke="#0f172a" 
                strokeWidth={2.5}
                opacity={0.4}
              />
              <text x="170" y="305" fill="#f8fafc" fontSize="10" fontWeight="bold" textAnchor="middle">SOUTH (5.25%)</text>

              {/* West Region */}
              <path 
                d="M 20,120 L 120,120 L 120,240 L 20,240 Z" 
                fill={filterRegion === 'West' || filterRegion === 'All' ? '#10b981' : '#1e293b'} 
                stroke="#0f172a" 
                strokeWidth={2.5}
                opacity={0.3}
              />
              <text x="70" y="185" fill="#f8fafc" fontSize="10" fontWeight="bold" textAnchor="middle">WEST (4.10%)</text>

              {/* East Region */}
              <path 
                d="M 220,120 L 380,120 L 380,240 L 220,240 Z" 
                fill={filterRegion === 'East' || filterRegion === 'All' ? '#f43f5e' : '#1e293b'} 
                stroke="#0f172a" 
                strokeWidth={2.5}
                opacity={0.35}
              />
              <text x="300" y="185" fill="#f8fafc" fontSize="10" fontWeight="bold" textAnchor="middle">EAST (5.42%)</text>

              {/* Central Region */}
              <path 
                d="M 120,120 L 220,120 L 220,240 L 120,240 Z" 
                fill={filterRegion === 'Central' || filterRegion === 'All' ? '#eab308' : '#1e293b'} 
                stroke="#0f172a" 
                strokeWidth={2.5}
                opacity={0.3}
              />
              <text x="170" y="185" fill="#f8fafc" fontSize="10" fontWeight="bold" textAnchor="middle">CENTRAL (4.52%)</text>
            </svg>

            {/* Map Legend */}
            <div className="absolute bottom-4 right-4 flex items-center gap-4 bg-slate-900/90 border border-slate-800 p-2.5 rounded-xl text-2xs font-semibold">
              <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 bg-rose-500/35 border border-rose-500 rounded-sm" /> High (&gt;5.0%)</span>
              <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 bg-yellow-500/35 border border-yellow-500 rounded-sm" /> Med (4.5-5.0%)</span>
              <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 bg-emerald-500/35 border border-emerald-500 rounded-sm" /> Low (&lt;4.5%)</span>
            </div>
          </div>
        </Card>

        {/* State Rankings Card List */}
        <Card className="lg:col-span-1 flex flex-col h-[480px]">
          <div className="mb-4">
            <h3 className="text-base font-bold font-display text-white">State Inflation Rankings</h3>
            <p className="text-xs text-slate-500 mt-0.5">Rates sorted highest to lowest.</p>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1.5">
            {sortedStates.map((item, idx) => (
              <div 
                key={idx}
                className="p-3 rounded-xl bg-slate-950/45 border border-slate-900 flex justify-between items-center transition-all hover:border-slate-800"
              >
                <div className="flex items-center gap-2.5">
                  <span className="text-2xs font-bold text-slate-500 w-4">#{idx + 1}</span>
                  <div>
                    <span className="text-xs font-bold text-slate-200 block">{item.state}</span>
                    <span className="text-[10px] text-slate-500 block">Region: {item.region} &bull; Prev: {item.yearAgoRate}%</span>
                  </div>
                </div>

                <div className="text-right">
                  <span className={`text-xs font-extrabold px-2 py-0.5 rounded-lg ${
                    item.status === 'High' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                    item.status === 'Medium' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' :
                    'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  }`}>
                    {item.currentRate}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

