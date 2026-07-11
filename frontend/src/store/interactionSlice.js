import { createSlice } from "@reduxjs/toolkit";

// BRD 11.3 — all form field values; updated ONLY by AI agent responses.
const emptyInteraction = {
  hcp_name: "",
  interaction_type: "",
  date: "",
  time: "",
  attendees: "",
  topics_discussed: "",
  materials_shared: [],
  samples_distributed: [],
  sentiment: "",
  outcomes: "",
  follow_up_actions: "",
  interaction_id: null,
};

const interactionSlice = createSlice({
  name: "interaction",
  initialState: { ...emptyInteraction, recentlyUpdated: [] },
  reducers: {
    // Merge (never replace) the AI-produced field updates into the store.
    mergeFields(state, action) {
      const fields = action.payload || {};
      const updatedKeys = [];
      Object.entries(fields).forEach(([key, value]) => {
        if (value === null || value === undefined) return;
        state[key] = value;
        if (key !== "interaction_id") updatedKeys.push(key);
      });
      state.recentlyUpdated = updatedKeys; // drives the highlight animation
    },
    clearHighlights(state) {
      state.recentlyUpdated = [];
    },
    resetInteraction() {
      return { ...emptyInteraction, recentlyUpdated: [] };
    },
  },
});

export const { mergeFields, clearHighlights, resetInteraction } =
  interactionSlice.actions;
export default interactionSlice.reducer;
