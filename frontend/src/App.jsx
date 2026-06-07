import React, { useState, useEffect, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Layout imports
import { DashboardLayout } from './layouts/DashboardLayout';
import { AuthLayout } from './layouts/AuthLayout';

// Auth Guard helper
import { AuthGuard } from './components/AuthGuard';

// Public Landing Page remains static for fast initial paint
import { LandingPage } from './pages/LandingPage';
import { NotFound } from './pages/NotFound';

// Lazy Loaded Pages (mapping named exports)
const Dashboard = React.lazy(() => import('./pages/Dashboard').then(module => ({ default: module.Dashboard })));
const Forecasting = React.lazy(() => import('./pages/Forecasting').then(module => ({ default: module.Forecasting })));
const CpiAnalytics = React.lazy(() => import('./pages/CpiAnalytics').then(module => ({ default: module.CpiAnalytics })));
const HistoricalTrends = React.lazy(() => import('./pages/HistoricalTrends').then(module => ({ default: module.HistoricalTrends })));
const NewsIntelligence = React.lazy(() => import('./pages/NewsIntelligence').then(module => ({ default: module.NewsIntelligence })));
const CurrencyImpact = React.lazy(() => import('./pages/CurrencyImpact').then(module => ({ default: module.CurrencyImpact })));
const Copilot = React.lazy(() => import('./pages/Copilot').then(module => ({ default: module.Copilot })));
const Heatmap = React.lazy(() => import('./pages/Heatmap').then(module => ({ default: module.Heatmap })));
const Simulator = React.lazy(() => import('./pages/Simulator').then(module => ({ default: module.Simulator })));
const Alerts = React.lazy(() => import('./pages/Alerts').then(module => ({ default: module.Alerts })));
const Profile = React.lazy(() => import('./pages/Profile').then(module => ({ default: module.Profile })));
const SettingsPage = React.lazy(() => import('./pages/Settings').then(module => ({ default: module.SettingsPage })));
const AdminDashboard = React.lazy(() => import('./pages/AdminDashboard').then(module => ({ default: module.AdminDashboard })));
const Login = React.lazy(() => import('./pages/Login').then(module => ({ default: module.Login })));
const Register = React.lazy(() => import('./pages/Register').then(module => ({ default: module.Register })));

// Loading component
const PageLoader = () => (
  <div className="flex h-[60vh] w-full items-center justify-center">
    <div className="flex flex-col items-center gap-4 p-8 rounded-2xl bg-slate-900/40 border border-slate-800/40 backdrop-blur-md">
      <div className="w-8 h-8 rounded-full border-2 border-cyan-500/25 border-t-cyan-500 animate-spin" />
      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest animate-pulse">Syncing Data Streams...</span>
    </div>
  </div>
);

export const App = () => {
  const [darkTheme, setDarkTheme] = useState(true);

  // Synchronize dark theme class with document root element
  useEffect(() => {
    if (darkTheme) {
      document.documentElement.classList.add('dark');
      document.documentElement.style.colorScheme = 'dark';
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.style.colorScheme = 'light';
    }
  }, [darkTheme]);

  const toggleTheme = () => {
    setDarkTheme(!darkTheme);
  };

  return (
    <Router>
      <Suspense fallback={<PageLoader />}>
        <Routes>
        {/* Public Landing Page */}
        <Route path="/" element={<LandingPage />} />

        {/* Authentication Pages (AuthLayout) */}
        <Route 
          path="/login" 
          element={
            <AuthLayout>
              <Login />
            </AuthLayout>
          } 
        />
        <Route 
          path="/register" 
          element={
            <AuthLayout>
              <Register />
            </AuthLayout>
          } 
        />

        {/* Dashboard Layout Wrapper for Internal Console Pages */}
        <Route 
          path="/dashboard" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <Dashboard />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/forecasting" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <Forecasting />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/cpi-analytics" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <CpiAnalytics />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/historical-trends" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <HistoricalTrends />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/news-intelligence" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <NewsIntelligence />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/currency-impact" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <CurrencyImpact />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/ai-copilot" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <Copilot />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/heatmap" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <Heatmap />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/simulator" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <Simulator />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/alerts" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <Alerts />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/profile" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <Profile />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/settings" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <SettingsPage />
              </DashboardLayout>
            </AuthGuard>
          } 
        />
        <Route 
          path="/admin" 
          element={
            <AuthGuard>
              <DashboardLayout darkTheme={darkTheme} toggleTheme={toggleTheme}>
                <AdminDashboard />
              </DashboardLayout>
            </AuthGuard>
          } 
        />

        {/* 404 Fallback page */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  </Router>
);
};

