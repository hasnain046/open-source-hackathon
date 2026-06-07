import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const fetchPredictions = createAsyncThunk(
  'forecast/fetchPredictions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/forecasting/predictions');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

const forecastSlice = createSlice({
  name: 'forecast',
  initialState: {
    predictions: null,
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchPredictions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPredictions.fulfilled, (state, action) => {
        state.loading = false;
        state.predictions = action.payload;
      })
      .addCase(fetchPredictions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export default forecastSlice.reducer;
