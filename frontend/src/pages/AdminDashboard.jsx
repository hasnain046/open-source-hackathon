import React from 'react';
import { ShieldAlert, Server, Database, Activity, RefreshCw } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { adminLogs } from '../mockData/inflationData';

export const AdminDashboard = () => {
  return (
    <div className="space-y-8">
      {/* Admin Title bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <ShieldAlert size={20} />
          </div>
          <div>
            <h2 className="text-xl font-bold font-display text-white">System Admin Console</h2>
            <p className="text-xs text-slate-400 mt-1">Audit background tasks, evaluate ML accuracy coefficients, and verify storage allocations.</p>
          </div>
        </div>
      </div>

      {/* KPI stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active System Users"
          value={adminLogs.activeUsers}
          change={12}
          trend="up"
          subtitle="Users logged in today"
          icon={Server}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="Requests Handled"
          value={adminLogs.requestsHandled}
          change={210}
          trend="up"
          subtitle="HTTP calls in 24 hours"
          icon={Activity}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="Local Database Size"
          value={adminLogs.dbSize}
          change={0.4}
          trend="up"
          subtitle="Sqlite storage file"
          icon={Database}
          isPercentage={false}
          status="neutral"
        />
        <MetricCard
          title="Pipeline Scheduler"
          value={adminLogs.cronStatus}
          change={0}
          trend="stable"
          subtitle="Cron operations check"
          icon={RefreshCw}
          isPercentage={false}
          status="positive"
        />
      </div>

      {/* Detailed specs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Backtesting stats */}
        <Card className="space-y-4">
          <h3 className="text-base font-bold font-display text-white mb-2">ML Engine Diagnostics</h3>
          
          <div className="space-y-3.5">
            <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900 flex justify-between items-center text-xs">
              <span className="text-slate-400 font-semibold">Last Retrained Cycle</span>
              <span className="text-slate-200 font-bold">{adminLogs.modelTraining.lastTrained}</span>
            </div>
            
            <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900 flex justify-between items-center text-xs">
              <span className="text-slate-400 font-semibold">Model Backtest R2 Accuracy</span>
              <span className="text-cyan-400 font-bold">{adminLogs.modelTraining.accuracyR2}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900 flex justify-between items-center text-xs">
              <span className="text-slate-400 font-semibold">Diagnostic Exception Count</span>
              <span className="text-emerald-400 font-bold">{adminLogs.modelTraining.errorsLogged} errors logged</span>
            </div>
          </div>
        </Card>

        {/* API connection statuses */}
        <Card className="space-y-4">
          <h3 className="text-base font-bold font-display text-white mb-2">Real-time Connection Health</h3>

          <div className="space-y-3.5">
            <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900 flex justify-between items-center text-xs">
              <span className="text-slate-400 font-semibold">FRED API Ingest Gateway</span>
              <span className="text-emerald-400 font-bold">{adminLogs.pipelineStats.fredConnection}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900 flex justify-between items-center text-xs">
              <span className="text-slate-400 font-semibold">Bureau of Labor Statistics Ingest</span>
              <span className="text-emerald-400 font-bold">{adminLogs.pipelineStats.blsConnection}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/45 border border-slate-900 flex justify-between items-center text-xs">
              <span className="text-slate-400 font-semibold">News NLP Scraping Daemons</span>
              <span className="text-emerald-400 font-bold">{adminLogs.pipelineStats.scrapingStatus}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
