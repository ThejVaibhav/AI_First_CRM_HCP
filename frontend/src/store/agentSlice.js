import { createSlice } from "@reduxjs/toolkit";

// BRD 11.3 — agent execution metadata and error state.
const agentSlice = createSlice({
  name: "agent",
  initialState: { lastToolCalled: null, agentError: null },
  reducers: {
    setAgentMeta(state, action) {
      state.lastToolCalled = action.payload.lastToolCalled ?? state.lastToolCalled;
      state.agentError = action.payload.agentError ?? null;
    },
    clearAgentError(state) {
      state.agentError = null;
    },
  },
});

export const { setAgentMeta, clearAgentError } = agentSlice.actions;
export default agentSlice.reducer;
