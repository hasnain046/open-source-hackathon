import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const fetchAlertPreferences = createAsyncThunk(
  'alerts/fetchPreferences',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/alerts/preferences');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

export const updateAlertPreferences = createAsyncThunk(
  'alerts/updatePreferences',
  async (preferences, { rejectWithValue }) => {
    try {
      const response = await api.put('/alerts/preferences', preferences);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

export const updatePreferences = updateAlertPreferences;

export const fetchAlertRules = createAsyncThunk(
  'alerts/fetchRules',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/alerts/rules');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

export const createAlertRule = createAsyncThunk(
  'alerts/createRule',
  async (rule, { rejectWithValue }) => {
    try {
      const response = await api.post('/alerts/rules', rule);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

export const deleteAlertRule = createAsyncThunk(
  'alerts/deleteRule',
  async (ruleId, { rejectWithValue }) => {
    try {
      await api.delete(`/alerts/rules/${ruleId}`);
      return ruleId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

const alertsSlice = createSlice({
  name: 'alerts',
  initialState: {
    preferences: null,
    rules: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchAlertPreferences.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAlertPreferences.fulfilled, (state, action) => {
        state.loading = false;
        state.preferences = action.payload;
      })
      .addCase(fetchAlertPreferences.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(updateAlertPreferences.fulfilled, (state, action) => {
        state.preferences = action.payload;
      })
      .addCase(fetchAlertRules.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAlertRules.fulfilled, (state, action) => {
        state.loading = false;
        state.rules = action.payload;
      })
      .addCase(fetchAlertRules.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(createAlertRule.fulfilled, (state, action) => {
        state.rules.push(action.payload);
      })
      .addCase(deleteAlertRule.fulfilled, (state, action) => {
        state.rules = state.rules.filter((rule) => rule.id !== action.payload);
      });
  },
});

export default alertsSlice.reducer;
