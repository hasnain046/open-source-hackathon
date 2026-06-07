import { createSlice } from '@reduxjs/toolkit';

const initialUser = localStorage.getItem('auth_user') 
  ? JSON.parse(localStorage.getItem('auth_user')) 
  : null;
const initialToken = localStorage.getItem('access_token') || null;
const initialRefreshToken = localStorage.getItem('refresh_token') || null;

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: initialUser,
    token: initialToken,
    refreshToken: initialRefreshToken,
    isAuthenticated: !!initialToken,
    loading: false,
    error: null,
  },
  reducers: {
    authStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    authSuccess: (state, action) => {
      state.loading = false;
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.refreshToken = action.payload.refreshToken;
      state.isAuthenticated = true;
      localStorage.setItem('auth_user', JSON.stringify(action.payload.user));
      localStorage.setItem('access_token', action.payload.token);
      if (action.payload.refreshToken) {
        localStorage.setItem('refresh_token', action.payload.refreshToken);
      }
    },
    authFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    setCredentials: (state, action) => {
      state.token = action.payload.token;
      localStorage.setItem('access_token', action.payload.token);
      if (action.payload.refreshToken) {
        state.refreshToken = action.payload.refreshToken;
        localStorage.setItem('refresh_token', action.payload.refreshToken);
      }
      if (action.payload.user) {
        state.user = action.payload.user;
        localStorage.setItem('auth_user', JSON.stringify(action.payload.user));
      }
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.loading = false;
      state.error = null;
      localStorage.removeItem('auth_user');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
  },
});

export const { authStart, authSuccess, authFailure, setCredentials, logout } = authSlice.actions;
export default authSlice.reducer;
