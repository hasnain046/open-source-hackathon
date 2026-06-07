import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { User, Key, Shield, Eye, EyeOff, CheckCircle } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import api from '../services/api';
import { setCredentials } from '../store/slices/authSlice';

export const Profile = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);

  const [showToken, setShowToken] = useState(false);
  const [tokenCopied, setTokenCopied] = useState(false);
  const [developerToken, setDeveloperToken] = useState('');
  
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [password, setPassword] = useState('');
  const [updateMsg, setUpdateMsg] = useState('');
  const [updateError, setUpdateError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // If we have an existing developer token saved on the user model, display it.
    if (user?.api_token) {
      setDeveloperToken(user.api_token);
    }
  }, [user]);

  const handleCopyToken = () => {
    if (developerToken) {
      navigator.clipboard.writeText(developerToken);
      setTokenCopied(true);
      setTimeout(() => setTokenCopied(false), 2000);
    }
  };

  const generateToken = async () => {
    try {
      const response = await api.post('/profile/token');
      setDeveloperToken(response.data.api_token);
      
      // Update store user profile too
      const profileResponse = await api.get('/profile/me');
      dispatch(setCredentials({ user: profileResponse.data }));
    } catch (error) {
      console.error('Failed to generate developer token:', error);
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setUpdateMsg('');
    setUpdateError('');
    setLoading(true);

    try {
      const payload = {
        full_name: fullName,
        email: email,
      };
      if (password) {
        payload.password = password;
      }

      const response = await api.put('/profile/update', payload);
      dispatch(setCredentials({ user: response.data }));
      setUpdateMsg('Profile updated successfully.');
      setPassword('');
    } catch (error) {
      const msg = error.response?.data?.detail;
      setUpdateError(typeof msg === 'string' ? msg : 'Failed to update profile.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Profile Header card */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div>
          <h2 className="text-xl font-bold font-display text-white">Profile Workspace</h2>
          <p className="text-xs text-slate-400 mt-1">Manage economic analyst roles, workspace parameters, and console security keys.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Info card */}
        <Card className="lg:col-span-1 space-y-6">
          <div className="flex flex-col items-center text-center pb-4 border-b border-slate-900">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-cyan-500 to-indigo-500 text-slate-950 flex items-center justify-center font-black text-3xl font-display shadow-lg shadow-cyan-500/10">
              {fullName ? fullName.slice(0, 2).toUpperCase() : 'AI'}
            </div>
            <h3 className="text-lg font-bold font-display text-white mt-4">{fullName || 'Analyst'}</h3>
            <span className="text-2xs font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 px-2.5 py-0.5 rounded-full mt-1.5 uppercase">
              {user?.role || 'Analyst'}
            </span>
          </div>

          <div className="space-y-4 text-xs font-semibold">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Linked Email</span>
              <span className="text-slate-200">{email || 'Not verified'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Status</span>
              <span className="text-slate-200">{user?.is_active ? 'Active' : 'Inactive'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Member Since</span>
              <span className="text-slate-200">{user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</span>
            </div>
          </div>
        </Card>

        {/* Configurations preferences */}
        <Card className="lg:col-span-2 space-y-6">
          <h3 className="text-base font-bold font-display text-white mb-2 font-display">Workspace Configuration</h3>
          
          {updateMsg && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-xs text-emerald-400">
              {updateMsg}
            </div>
          )}
          {updateError && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-xs text-rose-400">
              {updateError}
            </div>
          )}

          <form onSubmit={handleUpdateProfile} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-[10px] text-slate-400 font-bold uppercase">Full Name</label>
                <input 
                  type="text" 
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-slate-950/70 border border-slate-900 rounded-xl px-3.5 py-2.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500/50"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] text-slate-400 font-bold uppercase">Email Address</label>
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950/70 border border-slate-900 rounded-xl px-3.5 py-2.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500/50"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-[10px] text-slate-400 font-bold uppercase">Change Password (Leave blank to keep current)</label>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="New Password (optional)"
                className="w-full bg-slate-950/70 border border-slate-900 rounded-xl px-3.5 py-2.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500/50"
              />
            </div>

            <Button type="submit" disabled={loading}>
              {loading ? 'Updating...' : 'Update Details'}
            </Button>
          </form>

          <hr className="border-slate-900 my-6" />

          <h3 className="text-base font-bold font-display text-white mb-2">Developer Keys & Sandbox Tokens</h3>
          
          <div className="space-y-5">
            <div className="p-4 rounded-xl bg-slate-950/45 border border-slate-900">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Production Sandbox Key</span>
              <p className="text-[11px] text-slate-400 mt-2">
                Use this token to query the model forecast streams inside third-party APIs (e.g. Jupyter or Bloomberg terminal integrations).
              </p>
              
              <div className="flex gap-2 items-center mt-3.5">
                <div className="flex-1 bg-slate-950 border border-slate-900 rounded-xl px-4 py-3 text-2xs text-slate-400 font-mono flex items-center justify-between">
                  <span>{showToken && developerToken ? developerToken : (developerToken ? "••••••••••••••••••••••••••••••••••••••••" : "No token generated")}</span>
                  {developerToken && (
                    <button 
                      onClick={() => setShowToken(!showToken)}
                      className="text-slate-500 hover:text-slate-300"
                    >
                      {showToken ? <EyeOff size={14} /> : <Eye size={14} />}
                    </button>
                  )}
                </div>
                {developerToken ? (
                  <Button 
                    onClick={handleCopyToken}
                    variant="glass"
                    className="px-4 py-3 text-xs"
                  >
                    {tokenCopied ? 'Copied' : 'Copy'}
                  </Button>
                ) : (
                  <Button 
                    onClick={generateToken}
                    className="px-4 py-3 text-xs"
                  >
                    Generate
                  </Button>
                )}
              </div>

              {developerToken && (
                <button 
                  onClick={generateToken}
                  className="text-cyan-500 hover:text-cyan-400 text-[10px] mt-2.5 font-bold uppercase block transition-colors"
                >
                  Regenerate / Rotate Sandbox Key
                </button>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

