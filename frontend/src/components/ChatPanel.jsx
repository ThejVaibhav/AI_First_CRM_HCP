import React, { useState, useRef, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Bot, Send, CheckCircle2 } from "lucide-react";
import { sendMessageToAgent } from "../store/sendMessage";

function formatTime(ts) {
  try {
    return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

export default function ChatPanel() {
  const dispatch = useDispatch();
  const { messages, isLoading } = useSelector((state) => state.chat);
  const [input, setInput] = useState("");
  const threadRef = useRef(null);

  useEffect(() => {
    if (threadRef.current) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const submit = () => {
    if (!input.trim() || isLoading) return;
    dispatch(sendMessageToAgent(input));
    setInput("");
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="chat">
      <div className="chat-accent" />
      <div className="chat-header">
        <div className="chat-header-title">
          <span className="chat-bot">
            <Bot size={20} />
          </span>
          <span>AI Assistant</span>
          <span className="status-badge">
            <span className="status-dot" /> Connected
          </span>
        </div>
        <div className="chat-header-sub">Log Interaction details here via chat</div>
      </div>

      <div className="chat-thread" ref={threadRef}>
        {messages.map((m, i) => (
          <div key={i} className={`bubble bubble--${m.role} bubble--${m.variant || "default"}`}>
            {m.variant === "success" && (
              <CheckCircle2 size={15} className="bubble-check" />
            )}
            <span className="bubble-text">{m.content}</span>
            <span className="bubble-time">{formatTime(m.timestamp)}</span>
          </div>
        ))}
        {isLoading && (
          <div className="bubble bubble--ai bubble--typing">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </div>
        )}
      </div>

      <div className="chat-input-bar">
        <textarea
          className="chat-input"
          placeholder="Describe Interaction..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          rows={2}
        />
        <button className="btn-send" onClick={submit} disabled={isLoading} title="Log Interaction">
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}
