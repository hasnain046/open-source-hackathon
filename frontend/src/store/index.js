import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import dashboardReducer from './slices/dashboardSlice';
import forecastReducer from './slices/forecastSlice';
import copilotReducer from './slices/copilotSlice';
import alertsReducer from './slices/alertsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    dashboard: dashboardReducer,
    forecast: forecastReducer,
    copilot: copilotReducer,
    alerts: alertsReducer,
  },
});

export default store;
