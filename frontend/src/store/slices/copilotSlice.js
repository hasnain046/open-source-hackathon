import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const postCopilotMessage = createAsyncThunk(
  'copilot/postMessage',
  async (message, { getState, rejectWithValue }) => {
    try {
      const state = getState().copilot;
      const response = await api.post('/copilot/chat', {
        message,
        conversation_id: state.conversationId || null,
        mode: state.mode || 'analyst'
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

const copilotSlice = createSlice({
  name: 'copilot',
  initialState: {
    messages: [
      {
        role: 'assistant',
        content: 'Hello Ashfaq! I am your AI Economist Copilot, trained on global central bank policies, historical macroeconomic data, and thousands of research publications. How can I help you analyze the inflation outlook today?',
        timestamp: 'Just now'
      }
    ],
    conversationId: null,
    loading: false,
    error: null,
    mode: 'analyst', // 'analyst', 'economist', 'executive'
  },
  reducers: {
    clearHistory: (state) => {
      state.messages = [
        {
          role: 'assistant',
          content: 'Chat history re-initialized. What macroeconomic questions can I help you resolve?',
          timestamp: 'Just now'
        }
      ];
      state.conversationId = null;
    },
    setMode: (state, action) => {
      state.mode = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(postCopilotMessage.pending, (state, action) => {
        state.loading = true;
        state.error = null;
        // Pre-append the user's message for instant visual feedback
        state.messages.push({
          role: 'user',
          content: action.meta.arg,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
      })
      .addCase(postCopilotMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.conversationId = action.payload.conversation_id;
        // Map backend history format to UI format
        state.messages = action.payload.history.map(msg => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Just now'
        }));
      })
      .addCase(postCopilotMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearHistory, setMode } = copilotSlice.actions;
export default copilotSlice.reducer;
