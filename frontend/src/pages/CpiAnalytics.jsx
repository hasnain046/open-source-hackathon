import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { ShoppingBag, Fuel, Home, HeartPulse, Sparkles } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import api from '../services/api';

export const CpiAnalytics = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeCategoryIndex, setActiveCategoryIndex] = useState(0);

  const fetchCpiCategories = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/cpi/categories');
      setCategories(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch CPI categories.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCpiCategories();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-cyan-500/20 border-t-cyan-500 animate-spin" />
        <p className="text-sm text-slate-400 font-semibold uppercase tracking-wider animate-pulse">Decomposing CPI Basket Categories...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 max-w-2xl mx-auto text-center space-y-4">
        <h3 className="text-lg font-bold text-rose-400 font-display">Ingest Failed</h3>
        <p className="text-xs text-slate-400">{error}</p>
        <Button onClick={fetchCpiCategories} size="sm">Retry Ingest</Button>
      </div>
    );
  }

  const activeCategory = categories[activeCategoryIndex] || {
    name: 'Food & Beverages',
    weight: 45.86,
    rate: 5.42,
    color: '#06b6d4',
    itemBreakdown: []
  };

  const COLORS = ['#06b6d4', '#6366f1', '#f59e0b', '#ec4899', '#10b981'];

  const pieData = categories.map((cat, idx) => ({
    name: cat.name,
    value: cat.weight,
    rate: cat.rate,
    color: cat.color || COLORS[idx % COLORS.length]
  }));

  const categorySubItems = (activeCategory.itemBreakdown || []).map(item => ({
    name: item.name,
    "CPI Rate": item.rate,
    "Weight": item.weight
  }));

  const activeIcons = [ShoppingBag, Home, Fuel, HeartPulse, Sparkles];
  const ActiveIcon = activeIcons[activeCategoryIndex % activeIcons.length] || ShoppingBag;

  return (
    <div className="space-y-8">
      {/* Category Selection Summary bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div>
          <h2 className="text-xl font-bold font-display text-white">CPI Category Analytics</h2>
          <p className="text-xs text-slate-400 mt-1">Decompose the Consumer Price Index (CPI) basket by category weighting and individual sector rates.</p>
        </div>
      </div>

      {/* Metric Cards focusing on key sectors */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Food Inflation"
          value={categories[0]?.rate || 5.42}
          change={0.24}
          trend="up"
          subtitle={`Weight: ${categories[0]?.weight || 45.86}% of Basket`}
          icon={ShoppingBag}
          status="negative"
        />
        <MetricCard
          title="Housing Rent Index"
          value={categories[1]?.rate || 4.15}
          change={-0.08}
          trend="down"
          subtitle={`Weight: ${categories[1]?.weight || 10.07}% of Basket`}
          icon={Home}
          status="positive"
        />
        <MetricCard
          title="Fuel & Power"
          value={categories[2]?.rate || 3.10}
          change={-1.15}
          trend="down"
          subtitle={`Weight: ${categories[2]?.weight || 6.84}% of Basket`}
          icon={Fuel}
          status="positive"
        />
        <MetricCard
          title="Healthcare index"
          value={categories[3]?.rate || 5.80}
          change={0.12}
          trend="up"
          subtitle={`Weight: ${categories[3]?.weight || 8.0}% of Basket`}
          icon={HeartPulse}
          status="negative"
        />
      </div>

      {/* Visual Analytics Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* CPI Basket Weights PieChart */}
        <Card className="lg:col-span-1">
          <h3 className="text-base font-bold font-display text-white mb-2">CPI Basket Weight Split</h3>
          <p className="text-xs text-slate-500 mb-6">Percentage allocation of individual components in aggregate calculation.</p>
          
          <div className="h-64 w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                  onClick={(data, index) => setActiveCategoryIndex(index)}
                  className="cursor-pointer"
                >
                  {pieData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.color} 
                      stroke={activeCategoryIndex === index ? '#ffffff' : 'transparent'} 
                      strokeWidth={activeCategoryIndex === index ? 2 : 0}
                      style={{ outline: 'none' }}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'Weight']}
                  contentStyle={{ 
                    backgroundColor: '#0f172a', 
                    borderColor: '#334155', 
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '11px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            
            {/* Center label */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-2xs text-slate-500 font-bold uppercase tracking-wider">Active Sector</span>
              <span className="text-sm font-extrabold text-white font-display mt-0.5">{activeCategory.name.split(' ')[0]}</span>
            </div>
          </div>

          {/* Interactive Legend List */}
          <div className="space-y-2.5 mt-4">
            {categories.map((cat, idx) => (
              <button
                key={idx}
                onClick={() => setActiveCategoryIndex(idx)}
                className={`w-full flex justify-between items-center p-2 rounded-xl transition-all border ${
                  activeCategoryIndex === idx 
                    ? 'bg-slate-900/60 border-slate-700/60' 
                    : 'bg-transparent border-transparent hover:bg-slate-900/20'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cat.color || COLORS[idx % COLORS.length] }} />
                  <span className="text-xs text-slate-300 font-semibold">{cat.name}</span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-white block">{cat.weight}%</span>
                  <span className="text-[10px] text-slate-500 block">Rate: {cat.rate}%</span>
                </div>
              </button>
            ))}
          </div>
        </Card>

        {/* Selected Category breakdown */}
        <Card className="lg:col-span-2">
          <div className="flex justify-between items-start mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <ActiveIcon size={20} />
              </div>
              <div>
                <h3 className="text-lg font-bold font-display text-white">{activeCategory.name} Sub-Items</h3>
                <p className="text-xs text-slate-500 mt-0.5">Focus breakdown showing weight and local inflation rating.</p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Aggregate Rate</span>
              <span className="text-lg font-black text-cyan-400 block">{activeCategory.rate}%</span>
            </div>
          </div>

          {/* Chart of subitems */}
          <div className="h-60 w-full mb-6">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categorySubItems} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ 
                    backgroundColor: '#0f172a', 
                    borderColor: '#334155', 
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '11px'
                  }}
                />
                <Bar dataKey="CPI Rate" fill={activeCategory.color || '#06b6d4'} radius={[6, 6, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Detail List */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="pb-3">Sub-Component Name</th>
                  <th className="pb-3">Basket Weight</th>
                  <th className="pb-3 text-right">Current CPI Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/40 text-xs">
                {(activeCategory.itemBreakdown || []).map((item, index) => (
                  <tr key={index} className="hover:bg-slate-900/10 transition-colors">
                    <td className="py-2.5 font-bold text-slate-300">{item.name}</td>
                    <td className="py-2.5 text-slate-500">{item.weight}%</td>
                    <td className="py-2.5 text-right font-black text-cyan-400">{item.rate}%</td>
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

