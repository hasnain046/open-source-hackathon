import React, { useState, useContext } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Menu, Sun, Moon, Bell, Search, User, Check, ExternalLink } from 'lucide-react';
import { alertsHistory } from '../mockData/inflationData';

export const Navbar = ({ toggleSidebar, darkTheme, toggleTheme }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [showNotifications, setShowNotifications] = useState(false);
  const [alerts, setAlerts] = useState(alertsHistory);

  // Derive page title from pathname
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 'Platform Overview';
    if (path === '/forecasting') return 'AI Inflation Forecasting';
    if (path === '/cpi-analytics') return 'CPI Basket Analytics';
    if (path === '/historical-trends') return 'Historical Trends & Cycles';
    if (path === '/news-intelligence') return 'News Sentiment Intelligence';
    if (path === '/currency-impact') return 'Currency & Commodities Overlay';
    if (path === '/ai-copilot') return 'AI Economist Copilot';
    if (path === '/heatmap') return 'Regional Inflation Heatmap';
    if (path === '/simulator') return 'Macro Scenario Simulator';
    if (path === '/alerts') return 'Alerts & Triggers';
    if (path === '/profile') return 'My Profile';
    if (path === '/settings') return 'Platform Settings';
    if (path === '/admin') return 'System Administration';
    return 'InflationIQ';
  };

  const unreadCount = alerts.filter(a => !a.read).length;

  const markAllRead = () => {
    setAlerts(alerts.map(a => ({ ...a, read: true })));
  };

  const toggleAlertRead = (id) => {
    setAlerts(alerts.map(a => a.id === id ? { ...a, read: !a.read } : a));
  };

  return (
    <header className="sticky top-0 z-30 w-full glass-panel border-b border-slate-800/40 p-4 flex items-center justify-between">
      {/* Mobile controls & page title */}
      <div className="flex items-center gap-4">
        <button 
          onClick={toggleSidebar}
          className="p-2 text-slate-400 hover:text-white lg:hidden rounded-xl hover:bg-slate-900/50"
        >
          <Menu size={20} />
        </button>
        <div>
          <h1 className="text-xl font-bold font-display text-white">{getPageTitle()}</h1>
        </div>
      </div>

      {/* Utilities */}
      <div className="flex items-center gap-3">
        {/* Search Input Bar (Mock) */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950/50 border border-slate-800/50 focus-within:border-cyan-500/50 transition-colors w-64">
          <Search size={16} className="text-slate-500" />
          <input 
            type="text" 
            placeholder="Search economic indicators..." 
            className="bg-transparent text-xs text-slate-300 focus:outline-none w-full placeholder:text-slate-600"
          />
        </div>

        {/* Theme Toggle */}
        <button 
          onClick={toggleTheme}
          className="p-2.5 rounded-xl bg-slate-900/50 border border-slate-800/40 text-slate-400 hover:text-cyan-400 transition-colors"
          title="Toggle color theme"
        >
          {darkTheme ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* Notifications Dropdown Container */}
        <div className="relative">
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2.5 rounded-xl bg-slate-900/50 border border-slate-800/40 text-slate-400 hover:text-cyan-400 transition-colors relative"
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 w-5 h-5 flex items-center justify-center text-[10px] font-bold text-slate-950 bg-cyan-400 rounded-full animate-bounce">
                {unreadCount}
              </span>
            )}
          </button>

          {showNotifications && (
            <>
              {/* Click outside target */}
              <div className="fixed inset-0 z-40" onClick={() => setShowNotifications(false)} />
              
              <div className="absolute right-0 mt-3.5 w-80 max-w-sm rounded-2xl glass-panel border border-slate-800/60 shadow-2xl p-4 z-50 animate-slide-up">
                <div className="flex justify-between items-center pb-3 border-b border-slate-900">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-display">System Notifications</h4>
                  {unreadCount > 0 && (
                    <button 
                      onClick={markAllRead}
                      className="text-[10px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-semibold"
                    >
                      <Check size={12} /> Mark all read
                    </button>
                  )}
                </div>

                <div className="py-2 divide-y divide-slate-900/30 max-h-64 overflow-y-auto">
                  {alerts.map((alert) => (
                    <div 
                      key={alert.id} 
                      className={`py-3 group relative transition-colors ${alert.read ? 'opacity-60' : 'opacity-100'}`}
                    >
                      <div className="flex justify-between items-start gap-2">
                        <span className={`text-2xs font-extrabold px-1.5 py-0.5 rounded-full ${
                          alert.severity === 'High' ? 'bg-rose-500/10 text-rose-400' :
                          alert.severity === 'Medium' ? 'bg-amber-500/10 text-amber-400' :
                          'bg-emerald-500/10 text-emerald-400'
                        }`}>
                          {alert.severity}
                        </span>
                        <span className="text-[10px] text-slate-500">{alert.date}</span>
                      </div>
                      <p className="text-xs font-bold text-slate-200 mt-1.5">{alert.title}</p>
                      <p className="text-2xs text-slate-400 mt-0.5 leading-relaxed">{alert.message}</p>
                      
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-[10px] text-slate-500">Via {alert.channel}</span>
                        <button 
                          onClick={() => toggleAlertRead(alert.id)}
                          className="text-[10px] text-cyan-500 hover:underline opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          {alert.read ? 'Mark unread' : 'Mark read'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-900 flex justify-center">
                  <button 
                    onClick={() => {
                      setShowNotifications(false);
                      navigate('/alerts');
                    }}
                    className="text-xs text-slate-400 hover:text-cyan-400 flex items-center gap-1.5 font-semibold transition-colors"
                  >
                    View Alert Center <ExternalLink size={12} />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>

        {/* User shortcut avatar */}
        <div 
          onClick={() => navigate('/profile')}
          className="flex items-center gap-2 cursor-pointer p-1.5 rounded-xl hover:bg-slate-900/50 border border-transparent hover:border-slate-800/40 transition-all"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-500 text-slate-950 flex items-center justify-center font-extrabold text-sm">
            AI
          </div>
          <div className="hidden sm:block text-left">
            <span className="block text-xs font-bold text-white leading-none">Ashfaq</span>
            <span className="text-[10px] text-slate-400 leading-none">Premium Analyst</span>
          </div>
        </div>
      </div>
    </header>
  );
};
