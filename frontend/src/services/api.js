import axios from 'axios';
import { store } from '../store';
import { logout, setCredentials } from '../store/slices/authSlice';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to dynamically inject the bearer token
api.interceptors.request.use(
  (config) => {
    const state = store.getState();
    const token = state.auth?.token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh (401 status)
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const state = store.getState();
        const refresh_token = state.auth?.refreshToken || localStorage.getItem('refresh_token');

        if (!refresh_token) {
          throw new Error('No refresh token available');
        }

        // Call the refresh endpoint (this endpoint can accept custom refresh tokens depending on the backend design)
        // Here we post to /auth/refresh
        const response = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          {},
          {
            headers: {
              Authorization: `Bearer ${refresh_token}`,
            },
          }
        );

        const { access_token, refresh_token: new_refresh_token } = response.data;

        store.dispatch(
          setCredentials({
            token: access_token,
            refreshToken: new_refresh_token || refresh_token,
          })
        );

        if (new_refresh_token) {
          localStorage.setItem('refresh_token', new_refresh_token);
        }

        processQueue(null, access_token);
        isRefreshing = false;

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;
        store.dispatch(logout());
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
