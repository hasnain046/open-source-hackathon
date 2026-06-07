import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

export const MetricCard = ({ 
  title, 
  value, 
  change, 
  subtitle, 
  icon: Icon,
  trend = 'up', // 'up' | 'down' | 'stable'
  isPercentage = true,
  decimals = 2,
  status = 'neutral' // 'positive' | 'negative' | 'neutral'
}) => {
  const isNeutral = status === 'neutral';
  const isUp = trend === 'up';
  
  // Choose colors. For inflation, "down" is generally positive/good (green), "up" is negative/bad (red).
  let trendColor = 'text-slate-400';
  let trendBg = 'bg-slate-500/10';
  
  if (status === 'positive') {
    trendColor = 'text-emerald-400';
    trendBg = 'bg-emerald-500/10';
  } else if (status === 'negative') {
    trendColor = 'text-rose-400';
    trendBg = 'bg-rose-500/10';
  } else {
    // Rely on trend orientation if status not explicitly positive/negative
    trendColor = isUp ? 'text-rose-400' : 'text-emerald-400';
    trendBg = isUp ? 'bg-rose-500/10' : 'bg-emerald-500/10';
  }

  return (
    <div className="rounded-2xl p-6 glass-panel transition-all duration-300 hover:-translate-y-1 hover:border-cyan-500/20">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider font-display">{title}</p>
          <h3 className="text-3xl font-bold font-display mt-2 text-white">
            {value}{isPercentage ? '%' : ''}
          </h3>
        </div>
        {Icon && (
          <div className="p-2.5 rounded-xl bg-slate-900/50 border border-slate-800/40 text-cyan-400">
            <Icon size={20} />
          </div>
        )}
      </div>

      <div className="flex items-center gap-2 mt-4">
        <span className={`flex items-center gap-0.5 text-xs font-semibold px-2 py-0.5 rounded-full ${trendBg} ${trendColor}`}>
          {isUp ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          {change > 0 ? '+' : ''}{change}{isPercentage ? '%' : ''}
        </span>
        <span className="text-xs text-slate-500">{subtitle}</span>
      </div>
    </div>
  );
};
