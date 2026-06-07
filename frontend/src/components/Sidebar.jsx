import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, LineChart, PieChart, History, 
  Newspaper, Coins, BrainCircuit, Map, Sliders, 
  Bell, User, Settings, LogOut, ShieldAlert, TrendingUp, X
} from 'lucide-react';

export const Sidebar = ({ isOpen, toggleSidebar }) => {
  const navigate = useNavigate();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Forecasting', path: '/forecasting', icon: LineChart },
    { name: 'CPI Analytics', path: '/cpi-analytics', icon: PieChart },
    { name: 'Historical Trends', path: '/historical-trends', icon: History },
    { name: 'News Intelligence', path: '/news-intelligence', icon: Newspaper },
    { name: 'Currency Impact', path: '/currency-impact', icon: Coins },
    { name: 'AI Copilot', path: '/ai-copilot', icon: BrainCircuit },
    { name: 'Heatmap', path: '/heatmap', icon: Map },
    { name: 'Simulator', path: '/simulator', icon: Sliders },
    { name: 'Alerts', path: '/alerts', icon: Bell },
    { name: 'Profile', path: '/profile', icon: User },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  const handleLogout = () => {
    localStorage.removeItem('auth_user');
    navigate('/login');
  };

  return (
    <>
      {/* Mobile Overlay backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 lg:static lg:block
        glass-panel border-r border-slate-800/40 min-h-screen flex flex-col
        transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Brand header */}
        <div className="p-6 border-b border-slate-800/40 flex items-center justify-between">
          <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => navigate('/')}>
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <TrendingUp size={22} className="animate-pulse" />
            </div>
            <div>
              <span className="font-display font-extrabold text-lg bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">InflationIQ</span>
              <p className="text-[10px] text-slate-500 font-semibold tracking-wider uppercase">AI Econometrics</p>
            </div>
          </div>
          
          <button 
            className="p-1 text-slate-400 hover:text-white lg:hidden rounded-lg hover:bg-slate-900/50"
            onClick={toggleSidebar}
          >
            <X size={18} />
          </button>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 px-4 py-6 overflow-y-auto space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.path}
                onClick={() => {
                  if (window.innerWidth < 1024) toggleSidebar();
                }}
                className={({ isActive }) => `
                  flex items-center gap-3.5 px-4 py-3 rounded-xl text-sm font-semibold tracking-wide
                  transition-all duration-200 group
                  ${isActive 
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-inner' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/40 border border-transparent'}
                `}
              >
                {({ isActive }) => (
                  <>
                    <Icon size={18} className={`transition-transform duration-300 group-hover:scale-110 ${isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
                    <span>{item.name}</span>
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Footer shortcuts (Admin + Logout) */}
        <div className="p-4 border-t border-slate-800/40 space-y-1">
          <NavLink
            to="/admin"
            className={({ isActive }) => `
              flex items-center gap-3.5 px-4 py-2.5 rounded-xl text-xs font-semibold
              transition-all duration-200
              ${isActive 
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' 
                : 'text-slate-400 hover:text-rose-400 hover:bg-rose-500/5'}
            `}
          >
            <ShieldAlert size={16} />
            <span>Admin Terminal</span>
          </NavLink>
          
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3.5 px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-rose-400 hover:bg-rose-500/5 transition-all duration-200"
          >
            <LogOut size={16} />
            <span>Terminate Session</span>
          </button>
        </div>
      </aside>
    </>
  );
};
