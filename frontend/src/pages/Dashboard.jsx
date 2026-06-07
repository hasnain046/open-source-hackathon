import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { 
  TrendingDown, Newspaper, Coins, Calendar, ArrowRight, 
  BarChart3, Zap, ShieldCheck, HelpCircle 
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, Legend 
} from 'recharts';
import { MetricCard } from '../components/ui/MetricCard';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { fetchDashboardMetrics } from '../store/slices/dashboardSlice';

export const Dashboard = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { metrics, loading, error } = useSelector((state) => state.dashboard);

  useEffect(() => {
    dispatch(fetchDashboardMetrics());
  }, [dispatch]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-cyan-500/20 border-t-cyan-500 animate-spin" />
        <p className="text-sm text-slate-400 font-semibold uppercase tracking-wider animate-pulse">Loading dashboard telemetry...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 max-w-2xl mx-auto text-center space-y-4">
        <h3 className="text-lg font-bold text-rose-400 font-display">Data Ingestion Failed</h3>
        <p className="text-xs text-slate-400">{typeof error === 'string' ? error : 'Could not synchronize metrics with live backend services.'}</p>
        <Button onClick={() => dispatch(fetchDashboardMetrics())} size="sm">Retry Connection</Button>
      </div>
    );
  }

  // Use fallback dummy data if backend is operating on fresh state
  const data = metrics || {};
  const inflationRate = data.inflation_rate !== undefined ? data.inflation_rate : 5.82;
  const changePrevMonth = data.change_prev_month !== undefined ? data.change_prev_month : 0.12;
  const lstmNextMonth = data.lstm_next_month !== undefined ? data.lstm_next_month : 5.75;
  const usdInr = data.usd_inr !== undefined ? data.usd_inr : 82.52;
  const crudeBrent = data.crude_brent !== undefined ? data.crude_brent : 77.80;

  // Process historical charts
  const chartData = (data.chart_data || [
    { month: 'Jan', historical: 5.7, lstm: 5.7, prophet: 5.7 },
    { month: 'Feb', historical: 5.6, lstm: 5.61, prophet: 5.58 },
    { month: 'Mar', historical: 5.8, lstm: 5.79, prophet: 5.82 },
    { month: 'Apr', historical: 5.9, lstm: 5.88, prophet: 5.91 },
    { month: 'May', historical: 5.85, lstm: 5.82, prophet: 5.86 },
    { month: 'Jun', historical: 5.82, lstm: 5.78, prophet: 5.80 },
    { month: 'Jul', historical: null, lstm: 5.75, prophet: 5.72 }
  ]).map(item => ({
    name: item.month,
    "Headline CPI": item.historical || item.lstm,
    "LSTM Projection": item.lstm,
    "Prophet Projection": item.prophet
  }));

  const quickStats = data.quick_stats || {
    food_inflation: '5.42%',
    energy_inflation: '3.10%',
    wpi_inflation: '2.15%',
    rag_docs: '4,250 docs',
    active_alarms: 2
  };

  const sentimentFeed = data.sentiment_feed || [
    { id: 1, sentiment: 'Bullish', headline: 'RBI keeps interest rates unchanged in bid to support GDP recovery paths.', source: 'Economic Times', time: '1 hour ago', impactScore: 84 },
    { id: 2, sentiment: 'Bearish', headline: 'Global logistics container rates climb amidst renewed Red Sea transport delays.', source: 'Bloomberg', time: '3 hours ago', impactScore: 68 },
    { id: 3, sentiment: 'Neutral', headline: 'Monsoon forecast shows standard rainfall dispersion configurations across Central India.', source: 'Reuters', time: '5 hours ago', impactScore: 45 }
  ];

  const commoditiesForex = data.commodities_forex || [
    { month: 'Jun 2026', usdInr: '82.52', eurUsd: '1.09', crude: '77.80' },
    { month: 'May 2026', usdInr: '82.65', eurUsd: '1.08', crude: '81.20' },
    { month: 'Apr 2026', usdInr: '82.80', eurUsd: '1.08', crude: '84.60' },
    { month: 'Mar 2026', usdInr: '82.40', eurUsd: '1.09', crude: '79.10' }
  ];

  return (
    <div className="space-y-8">
      {/* Welcome & status bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div>
          <h2 className="text-2xl font-bold font-display text-white">System Console</h2>
          <p className="text-xs text-slate-400 mt-1">Live data ingest is operating. All predictive models are fully synchronized.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Live Ingest Active
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-semibold">
            <Calendar size={14} /> June 2026
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Inflation CPI Rate"
          value={inflationRate}
          change={changePrevMonth}
          trend={changePrevMonth > 0 ? 'up' : 'down'}
          subtitle="Change from last month"
          icon={TrendingDown}
          status={changePrevMonth < 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          title="LSTM Projection (Jul)"
          value={lstmNextMonth}
          change={-0.07}
          trend="down"
          subtitle="Confidence Score: 94.5%"
          icon={Zap}
          status="positive"
        />
        <MetricCard
          title="USD / INR Index"
          value={usdInr.toString()}
          change={-0.13}
          trend="down"
          subtitle="Rupee strengthens vs USD"
          icon={Coins}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="Crude Oil (Brent)"
          value={`$${crudeBrent}`}
          change={-3.40}
          trend="down"
          subtitle="Price per barrel (bbl)"
          icon={BarChart3}
          isPercentage={false}
          status="positive"
        />
      </div>

      {/* Main Chart Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Inflation trend chart */}
        <Card className="lg:col-span-2">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-lg font-bold font-display text-white">Headline CPI Trend & Forecast</h3>
              <p className="text-xs text-slate-500 mt-0.5">Comparing historical monthly index with short-term machine learning models.</p>
            </div>
            <Button 
              onClick={() => navigate('/forecasting')}
              variant="glass" 
              size="sm"
              className="flex items-center gap-1.5"
            >
              Analyze Forecasts <ArrowRight size={14} />
            </Button>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCpi" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorLstm" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
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
                <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
                <Area type="monotone" dataKey="Headline CPI" stroke="#06b6d4" strokeWidth={2.5} fillOpacity={1} fill="url(#colorCpi)" />
                <Area type="monotone" dataKey="LSTM Projection" stroke="#6366f1" strokeWidth={1.5} strokeDasharray="5 5" fillOpacity={1} fill="url(#colorLstm)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Quick stats and action cards */}
        <Card className="flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold font-display text-white">Platform Quick Statistics</h3>
            <p className="text-xs text-slate-500 mt-0.5">Key aggregate metrics extracted from the current pipeline run.</p>
            
            <div className="space-y-4.5 mt-6">
              <div className="flex justify-between items-center border-b border-slate-800/40 pb-3">
                <span className="text-xs text-slate-400 font-semibold">Food Inflation CPI</span>
                <span className="text-xs font-bold text-white bg-slate-900 px-2.5 py-1 rounded-lg">{quickStats.food_inflation}</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-800/40 pb-3">
                <span className="text-xs text-slate-400 font-semibold">Energy Inflation CPI</span>
                <span className="text-xs font-bold text-white bg-slate-900 px-2.5 py-1 rounded-lg">{quickStats.energy_inflation}</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-800/40 pb-3">
                <span className="text-xs text-slate-400 font-semibold">Wholesale Inflation (WPI)</span>
                <span className="text-xs font-bold text-white bg-slate-900 px-2.5 py-1 rounded-lg">{quickStats.wpi_inflation}</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-800/40 pb-3">
                <span className="text-xs text-slate-400 font-semibold">RAG Knowledge Documents</span>
                <span className="text-xs font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/20">{quickStats.rag_docs}</span>
              </div>
              <div className="flex justify-between items-center pb-1">
                <span className="text-xs text-slate-400 font-semibold">Active Alarm Triggers</span>
                <span className="text-xs font-bold text-rose-400 bg-rose-500/10 px-2.5 py-1 rounded-lg border border-rose-500/20">{quickStats.active_alarms} active</span>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-slate-800/40 mt-6 space-y-3">
            <Button 
              onClick={() => navigate('/ai-copilot')}
              className="w-full flex justify-center items-center gap-1.5"
            >
              Ask AI Economist Copilot
            </Button>
            <Button 
              onClick={() => navigate('/simulator')}
              variant="glass" 
              className="w-full flex justify-center items-center gap-1.5"
            >
              Run Policy Simulator
            </Button>
          </div>
        </Card>
      </div>

      {/* News Digest & Market Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* News sentiment overview */}
        <Card>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-lg font-bold font-display text-white">Sentiment Feed</h3>
              <p className="text-xs text-slate-500 mt-0.5">Recent financial reports classified by our NLP sentiment parser.</p>
            </div>
            <Button 
              onClick={() => navigate('/news-intelligence')}
              variant="glass" 
              size="sm"
            >
              Browse News
            </Button>
          </div>

          <div className="space-y-4">
            {sentimentFeed.slice(0, 3).map((item) => (
              <div 
                key={item.id} 
                className="p-4 rounded-xl bg-slate-950/40 border border-slate-900 hover:border-slate-800 transition-colors flex justify-between gap-4 items-start"
              >
                <div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    item.sentiment === 'Bullish' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
                    item.sentiment === 'Bearish' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                    'bg-slate-500/10 text-slate-400 border border-slate-800'
                  }`}>
                    {item.sentiment}
                  </span>
                  <h4 className="text-xs font-bold text-slate-200 mt-2 leading-relaxed">{item.headline}</h4>
                  <span className="text-[10px] text-slate-500 mt-1.5 block">{item.source} &bull; {item.time}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Impact</span>
                  <span className="text-sm font-extrabold text-cyan-400 mt-0.5 block">{item.impactScore}%</span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Currency snapshot */}
        <Card>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-lg font-bold font-display text-white">Commodities & Forex Correlation</h3>
              <p className="text-xs text-slate-500 mt-0.5">Historical overlay tracking raw commodities vs exchange values.</p>
            </div>
            <Button 
              onClick={() => navigate('/currency-impact')}
              variant="glass" 
              size="sm"
            >
              Examine Currency
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="pb-3">Reporting Month</th>
                  <th className="pb-3">USD / INR</th>
                  <th className="pb-3">EUR / USD</th>
                  <th className="pb-3 text-right">Crude Brent</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/40 text-xs">
                {commoditiesForex.map((data, index) => (
                  <tr key={index} className="hover:bg-slate-900/10 transition-colors">
                    <td className="py-3 font-semibold text-slate-300">{data.month}</td>
                    <td className="py-3 font-bold text-white">{data.usdInr}</td>
                    <td className="py-3 text-slate-400">{data.eurUsd}</td>
                    <td className="py-3 text-right text-cyan-400 font-bold">${data.crude}</td>
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

