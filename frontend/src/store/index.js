import { configureStore } from "@reduxjs/toolkit";

import interactionReducer from "./interactionSlice";
import chatReducer from "./chatSlice";
import agentReducer from "./agentSlice";

export const store = configureStore({
  reducer: {
    interaction: interactionReducer,
    chat: chatReducer,
    agent: agentReducer,
  },
});
