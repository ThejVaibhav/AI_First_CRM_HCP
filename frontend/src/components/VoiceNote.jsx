import React, { useState, useRef } from "react";
import { useDispatch } from "react-redux";
import { Mic, Square } from "lucide-react";
import { transcribeAudio } from "../api/client";
import { sendMessageToAgent } from "../store/sendMessage";
import { addMessage } from "../store/chatSlice";

// Voice Note input path (BRD 8.4 & C9): consent -> MediaRecorder -> Groq
// Whisper STT -> transcribed text injected into the SAME log_interaction flow.
// This is NOT a separate LangGraph tool.
export default function VoiceNote() {
  const dispatch = useDispatch();
  const [status, setStatus] = useState("idle"); // idle | recording | working
  const recorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    try {
      // Browser requests microphone consent here (BRD Compliance NFR).
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = handleStop;
      recorder.start();
      recorderRef.current = recorder;
      setStatus("recording");
    } catch (err) {
      dispatch(
        addMessage({
          role: "ai",
          variant: "error",
          content:
            "Microphone access was denied. Please enable it in your browser settings to use Voice Note.",
        })
      );
    }
  };

  const stopRecording = () => {
    const recorder = recorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
      recorder.stream.getTracks().forEach((t) => t.stop());
    }
  };

  const handleStop = async () => {
    setStatus("working");
    try {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      const text = await transcribeAudio(blob);
      // The transcript flows into the chat exactly like a typed message.
      dispatch(sendMessageToAgent(text));
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        "I couldn't transcribe the audio clearly. Please try again or type your interaction details.";
      dispatch(addMessage({ role: "ai", variant: "error", content: detail }));
    } finally {
      setStatus("idle");
    }
  };

  return (
    <div className="voice-note">
      {status === "idle" && (
        <button className="voice-link" onClick={startRecording}>
          <Mic size={14} /> Summarize from Voice Note (Requires Consent)
        </button>
      )}
      {status === "recording" && (
        <button className="voice-link voice-link--recording" onClick={stopRecording}>
          <Square size={13} fill="currentColor" /> Recording… tap to stop
        </button>
      )}
      {status === "working" && (
        <span className="voice-link voice-link--working">Transcribing…</span>
      )}
    </div>
  );
}
