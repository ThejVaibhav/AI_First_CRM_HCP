import { createSlice } from "@reduxjs/toolkit";

// BRD 11.3 — chat thread history + agent loading state.
const initialGreeting = {
  role: "ai",
  variant: "greeting",
  content:
    "Log interaction details here (e.g., Met Dr. Smith, discussed Prodo-X efficacy, positive sentiment, shared brochure) or ask for help.",
  timestamp: new Date().toISOString(),
};

const chatSlice = createSlice({
  name: "chat",
  initialState: { messages: [initialGreeting], isLoading: false },
  reducers: {
    addMessage(state, action) {
      state.messages.push({
        timestamp: new Date().toISOString(),
        ...action.payload,
      });
    },
    setLoading(state, action) {
      state.isLoading = action.payload;
    },
    resetChat(state) {
      state.messages = [initialGreeting];
      state.isLoading = false;
    },
  },
});

export const { addMessage, setLoading, resetChat } = chatSlice.actions;
export default chatSlice.reducer;
