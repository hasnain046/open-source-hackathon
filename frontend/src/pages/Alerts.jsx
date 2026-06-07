import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Bell, Mail, Send, BellRing, Trash2, ShieldAlert } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { 
  fetchAlertRules, 
  createAlertRule, 
  deleteAlertRule, 
  updatePreferences 
} from '../store/slices/alertsSlice';

export const Alerts = () => {
  const dispatch = useDispatch();
  const { rules, preferences, loading } = useSelector((state) => state.alerts);
  
  const [newTitle, setNewTitle] = useState('');
  const [newCondition, setNewCondition] = useState('');

  useEffect(() => {
    dispatch(fetchAlertRules());
  }, [dispatch]);

  const handleDeleteRule = (id) => {
    dispatch(deleteAlertRule(id));
  };

  const handleCreateRule = (e) => {
    e.preventDefault();
    if (!newTitle.trim() || !newCondition.trim()) return;

    dispatch(createAlertRule({
      title: newTitle,
      message: `Trigger alert when threshold reached: ${newCondition}`,
      severity: 'Medium',
      channel: 'Console',
      date: new Date().toISOString().split('T')[0],
      read: false
    }));

    setNewTitle('');
    setNewCondition('');
  };

  const handleTogglePreference = (key, value) => {
    dispatch(updatePreferences({
      ...preferences,
      [key]: value
    }));
  };

  const activeAlarmsCount = rules.filter(a => a.severity === 'High').length;

  return (
    <div className="space-y-8">
      {/* Alerts Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div>
          <h2 className="text-xl font-bold font-display text-white">Alerts & Trigger Center</h2>
          <p className="text-xs text-slate-400 mt-1">Configure automated notifications linking macro index changes to specific alert endpoints.</p>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Logged Alarms"
          value={rules.length}
          change={rules.length > 0 ? 1 : 0}
          trend="up"
          subtitle="Alarm counts this cycle"
          icon={BellRing}
          isPercentage={false}
          status="neutral"
        />
        <MetricCard
          title="High Severity Alarms"
          value={activeAlarmsCount}
          change={0}
          trend="stable"
          subtitle="Urgent critical actions"
          icon={ShieldAlert}
          isPercentage={false}
          status="negative"
        />
        <MetricCard
          title="Email Integration"
          value={preferences.email ? 'Active' : 'Disabled'}
          change={0}
          trend="stable"
          subtitle="Digest deliveries"
          icon={Mail}
          isPercentage={false}
          status={preferences.email ? 'positive' : 'neutral'}
        />
        <MetricCard
          title="Telegram Webhook"
          value={preferences.telegram ? 'Active' : 'Disabled'}
          change={0}
          trend="stable"
          subtitle="Real-time push channel"
          icon={Send}
          isPercentage={false}
          status={preferences.telegram ? 'positive' : 'neutral'}
        />
      </div>

      {/* Configurations split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configurations toggles */}
        <Card className="lg:col-span-1 space-y-6 h-fit">
          <h3 className="text-base font-bold font-display text-white mb-4">Notification Routings</h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 rounded-xl bg-slate-950/45 border border-slate-900">
              <div className="flex items-center gap-2.5">
                <Mail size={16} className="text-slate-400" />
                <span className="text-xs font-semibold text-slate-300">Email Digests</span>
              </div>
              <input 
                type="checkbox" 
                checked={preferences.email}
                onChange={(e) => handleTogglePreference('email', e.target.checked)}
                className="w-4 h-4 rounded text-cyan-500 bg-slate-900 border-slate-800 focus:ring-0 cursor-pointer"
              />
            </div>

            <div className="flex justify-between items-center p-3 rounded-xl bg-slate-950/45 border border-slate-900">
              <div className="flex items-center gap-2.5">
                <Send size={16} className="text-slate-400" />
                <span className="text-xs font-semibold text-slate-300">Telegram Channel</span>
              </div>
              <input 
                type="checkbox" 
                checked={preferences.telegram}
                onChange={(e) => handleTogglePreference('telegram', e.target.checked)}
                className="w-4 h-4 rounded text-cyan-500 bg-slate-900 border-slate-800 focus:ring-0 cursor-pointer"
              />
            </div>

            <div className="flex justify-between items-center p-3 rounded-xl bg-slate-950/45 border border-slate-900">
              <div className="flex items-center gap-2.5">
                <Bell size={16} className="text-slate-400" />
                <span className="text-xs font-semibold text-slate-300">Console Alarms</span>
              </div>
              <input 
                type="checkbox" 
                checked={preferences.system}
                onChange={(e) => handleTogglePreference('system', e.target.checked)}
                className="w-4 h-4 rounded text-cyan-500 bg-slate-900 border-slate-800 focus:ring-0 cursor-pointer"
              />
            </div>
          </div>

          <div className="pt-4 border-t border-slate-900">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">Add Custom Ingest rule</h4>
            <form onSubmit={handleCreateRule} className="space-y-3">
              <input 
                type="text" 
                placeholder="Indicator name (e.g. Brent Crude)" 
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="w-full bg-slate-950/60 border border-slate-900 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none" 
              />
              <input 
                type="text" 
                placeholder="Trigger condition (e.g. > $85.00)" 
                value={newCondition}
                onChange={(e) => setNewCondition(e.target.value)}
                className="w-full bg-slate-950/60 border border-slate-900 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none" 
              />
              <Button type="submit" className="w-full text-xs py-2" disabled={loading}>
                Create Active Trigger
              </Button>
            </form>
          </div>
        </Card>

        {/* Alarm Log table list */}
        <Card className="lg:col-span-2 space-y-4">
          <h3 className="text-base font-bold font-display text-white mb-2">Platform Alarm Logs</h3>
          
          <div className="space-y-3.5">
            {rules.length > 0 ? (
              rules.map((alert) => (
                <div 
                  key={alert.id}
                  className={`p-4 rounded-xl border flex justify-between items-start gap-4 transition-colors ${
                    alert.read ? 'bg-slate-950/30 border-slate-900 opacity-60' : 'bg-slate-900/20 border-slate-800/80 hover:bg-slate-900/40'
                  }`}
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full ${
                        alert.severity === 'High' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                        alert.severity === 'Medium' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' :
                        'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}>
                        {alert.severity}
                      </span>
                      <span className="text-[10px] text-slate-500 font-semibold">{alert.date}</span>
                    </div>

                    <h4 className="text-xs font-bold text-white leading-relaxed">{alert.title}</h4>
                    <p className="text-[11px] text-slate-400 leading-normal">{alert.message}</p>
                    <span className="text-[10px] text-slate-500 block">Ingested via {alert.channel}</span>
                  </div>

                  <button 
                    onClick={() => handleDeleteRule(alert.id)}
                    className="p-1.5 text-slate-500 hover:text-rose-400 rounded-lg hover:bg-slate-900/40 transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))
            ) : (
              <div className="text-center py-12 text-slate-500 text-xs">
                No active alarms in index history log.
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

