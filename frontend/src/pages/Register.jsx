import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Mail, Lock, User, Eye, EyeOff } from 'lucide-react';
import { Button } from '../components/ui/Button';
import api from '../services/api';
import { authStart, authSuccess, authFailure } from '../store/slices/authSlice';

export const Register = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.auth);
  
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (!name || !email || !password) {
      setErrorMsg("All registration inputs are required.");
      return;
    }

    dispatch(authStart());
    try {
      // Register request
      await api.post('/auth/register', {
        email: email,
        full_name: name,
        password: password,
        role: 'analyst'
      });

      // After successful registration, log the user in immediately
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const loginResponse = await api.post('/auth/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token, refresh_token } = loginResponse.data;

      // Retrieve registered user details
      const profileResponse = await api.get('/profile/me', {
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      });

      dispatch(authSuccess({
        user: profileResponse.data,
        token: access_token,
        refreshToken: refresh_token,
      }));

      navigate('/dashboard');
    } catch (err) {
      let errMsg = err.response?.data?.detail;
      if (Array.isArray(errMsg)) {
        errMsg = errMsg.map(e => e.msg).join(', ');
      } else if (typeof errMsg === 'object') {
        errMsg = JSON.stringify(errMsg);
      }
      errMsg = errMsg || err.message || 'Registration failed';
      setErrorMsg(errMsg);
      dispatch(authFailure(errMsg));
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold font-display text-white text-center">Create Account</h2>
        <p className="text-2xs text-slate-500 mt-1 text-center font-semibold uppercase tracking-wider">Configure your economic sandbox profile</p>
      </div>

      {(errorMsg || error) && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400 font-semibold text-center animate-shake">
          {errorMsg || error}
        </div>
      )}

      <form onSubmit={handleRegister} className="space-y-4">
        {/* Name */}
        <div className="space-y-1.5">
          <label className="text-2xs font-bold text-slate-400 uppercase tracking-wider">Full Name</label>
          <div className="flex items-center gap-3 px-3.5 py-3 rounded-xl bg-slate-950/70 border border-slate-900 focus-within:border-cyan-500/50 transition-colors">
            <User size={16} className="text-slate-500" />
            <input 
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ashfaq"
              className="bg-transparent text-xs text-slate-300 focus:outline-none w-full placeholder:text-slate-700"
            />
          </div>
        </div>

        {/* Email */}
        <div className="space-y-1.5">
          <label className="text-2xs font-bold text-slate-400 uppercase tracking-wider">Email Address</label>
          <div className="flex items-center gap-3 px-3.5 py-3 rounded-xl bg-slate-950/70 border border-slate-900 focus-within:border-cyan-500/50 transition-colors">
            <Mail size={16} className="text-slate-500" />
            <input 
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="analyst@inflationiq.ai"
              className="bg-transparent text-xs text-slate-300 focus:outline-none w-full placeholder:text-slate-700"
            />
          </div>
        </div>

        {/* Password */}
        <div className="space-y-1.5">
          <label className="text-2xs font-bold text-slate-400 uppercase tracking-wider">Workspace Password</label>
          <div className="flex items-center gap-3 px-3.5 py-3 rounded-xl bg-slate-950/70 border border-slate-900 focus-within:border-cyan-500/50 transition-colors">
            <Lock size={16} className="text-slate-500" />
            <input 
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="bg-transparent text-xs text-slate-300 focus:outline-none w-full placeholder:text-slate-700"
            />
            <button 
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="text-slate-500 hover:text-slate-300"
            >
              {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
            </button>
          </div>
        </div>

        <Button 
          type="submit"
          className="w-full justify-center text-xs py-3 mt-4"
          disabled={loading}
        >
          {loading ? 'Registering Workspace...' : 'Initialize Workspace'}
        </Button>
      </form>

      <div className="text-center pt-4 border-t border-slate-900 text-xs">
        <span className="text-slate-500 font-medium">Already have an account?</span>{' '}
        <button 
          onClick={() => navigate('/login')}
          className="text-cyan-400 font-semibold hover:underline"
        >
          Log In
        </button>
      </div>
    </div>
  );
};
