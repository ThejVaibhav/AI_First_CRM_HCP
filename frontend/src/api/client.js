import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL });

// POST /api/agent — main LangGraph agent call.
export async function callAgent({ message, interactionData }) {
  const { data } = await api.post("/api/agent", {
    message,
    interaction_data: interactionData,
    interaction_id: interactionData.interaction_id || null,
  });
  return data; // { fields_to_update, ai_message, interaction_id, tool_called }
}

// POST /api/voice/transcribe — Voice Note input path.
export async function transcribeAudio(blob) {
  const form = new FormData();
  form.append("audio", blob, "voice.webm");
  const { data } = await api.post("/api/voice/transcribe", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data.text;
}

export async function fetchHcps() {
  const { data } = await api.get("/api/hcps");
  return data;
}
