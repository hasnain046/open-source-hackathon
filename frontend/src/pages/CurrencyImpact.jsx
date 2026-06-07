import React from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, Legend, YAxis as RechartsYAxis 
} from 'recharts';
import { Coins, Flame, Gem, Percent, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { currencyAndCommodities } from '../mockData/inflationData';

export const CurrencyImpact = () => {
  return (
    <div className="space-y-8">
      {/* Page header controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div>
          <h2 className="text-xl font-bold font-display text-white">Currency & Commodity Pass-Through Overlay</h2>
          <p className="text-xs text-slate-400 mt-1">Track correlation factors between local currency values and landed import prices (Crude Oil & Gold).</p>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="USD / INR Exchange Rate"
          value="82.52"
          change={-0.13}
          trend="down"
          subtitle="Rupee strengthens vs USD"
          icon={Coins}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="EUR / USD Exchange Rate"
          value="1.13"
          change={0.02}
          trend="up"
          subtitle="Euro rises against Dollar"
          icon={Percent}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="Brent Crude Spot"
          value="$77.80"
          change={-3.40}
          trend="down"
          subtitle="Brent crude oil index / bbl"
          icon={Flame}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="Gold Price Index (10g)"
          value="₹67,200"
          change={400}
          trend="up"
          subtitle="Standard gold bullion price"
          icon={Gem}
          isPercentage={false}
          status="negative"
        />
      </div>

      {/* Main comparative correlation chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart */}
        <Card className="lg:col-span-2">
          <h3 className="text-lg font-bold font-display text-white mb-2">Exchange Rates vs Brent Crude Spot</h3>
          <p className="text-xs text-slate-500 mb-6">Evaluating if a stronger Rupee coincides with decreasing energy imports (dual axis index).</p>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={currencyAndCommodities} margin={{ top: 10, right: -5, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} tickLine={false} />
                {/* Left Y-Axis for USD/INR */}
                <YAxis yAxisId="left" stroke="#06b6d4" fontSize={11} tickLine={false} domain={[82, 84]} />
                {/* Right Y-Axis for Crude */}
                <YAxis yAxisId="right" orientation="right" stroke="#f59e0b" fontSize={11} tickLine={false} domain={[70, 90]} />
                
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
                
                <Line yAxisId="left" type="monotone" dataKey="usdInr" name="USD/INR Exchange" stroke="#06b6d4" strokeWidth={2.5} dot={{ r: 3 }} />
                <Line yAxisId="right" type="monotone" dataKey="crude" name="Brent Crude ($/bbl)" stroke="#f59e0b" strokeWidth={2.5} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Pass-through statistics */}
        <Card className="lg:col-span-1">
          <h3 className="text-base font-bold font-display text-white mb-4">CPI Impact Coefficients</h3>
          <p className="text-xs text-slate-500 mb-6">Determining raw correlation values mapping directly onto inflation projections.</p>

          <div className="space-y-4">
            <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900 flex justify-between items-center">
              <div>
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Crude Oil Correlation</span>
                <span className="text-xs font-bold text-white mt-1 block">Brent Crude & CPI index</span>
              </div>
              <div className="text-right">
                <span className="text-xs font-black text-emerald-400 block flex items-center gap-0.5"><ArrowUpRight size={14} /> +0.76</span>
                <span className="text-[9px] text-slate-500">Strong positive</span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900 flex justify-between items-center">
              <div>
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">USD/INR Exchange</span>
                <span className="text-xs font-bold text-white mt-1 block">Exchange rate & Landing cost</span>
              </div>
              <div className="text-right">
                <span className="text-xs font-black text-emerald-400 block flex items-center gap-0.5"><ArrowUpRight size={14} /> +0.64</span>
                <span className="text-[9px] text-slate-500">Moderate positive</span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900 flex justify-between items-center">
              <div>
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Gold Bullion rate</span>
                <span className="text-xs font-bold text-white mt-1 block">Gold index & retail CPI</span>
              </div>
              <div className="text-right">
                <span className="text-xs font-black text-slate-400 block flex items-center gap-0.5"><ArrowDownRight size={14} /> -0.15</span>
                <span className="text-[9px] text-slate-500">Weak negative</span>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
