// Thunk-like orchestrator: send a user message to the agent and wire the
// response back into all three slices. Used by both chat text and voice input.
import { callAgent } from "../api/client";
import { addMessage, setLoading } from "./chatSlice";
import { mergeFields, clearHighlights } from "./interactionSlice";
import { setAgentMeta } from "./agentSlice";

export function sendMessageToAgent(text) {
  return async (dispatch, getState) => {
    const trimmed = (text || "").trim();
    if (!trimmed) return;

    dispatch(addMessage({ role: "user", content: trimmed }));
    dispatch(setLoading(true));
    dispatch(clearHighlights());

    const interactionData = getState().interaction;

    try {
      const res = await callAgent({ message: trimmed, interactionData });
      if (res.fields_to_update && Object.keys(res.fields_to_update).length) {
        dispatch(mergeFields(res.fields_to_update));
        // Clear the highlight animation after it plays.
        setTimeout(() => dispatch(clearHighlights()), 1600);
      }
      dispatch(
        setAgentMeta({ lastToolCalled: res.tool_called, agentError: null })
      );
      dispatch(
        addMessage({ role: "ai", variant: "success", content: res.ai_message })
      );
    } catch (err) {
      // BRD Section 14 — graceful error message, never crash the UI.
      const detail =
        err?.response?.data?.detail ||
        "Something went wrong talking to the AI. Please try again.";
      dispatch(setAgentMeta({ lastToolCalled: null, agentError: detail }));
      dispatch(addMessage({ role: "ai", variant: "error", content: detail }));
    } finally {
      dispatch(setLoading(false));
    }
  };
}
