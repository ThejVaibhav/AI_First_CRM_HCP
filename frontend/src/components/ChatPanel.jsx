import React, { useState, useRef, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { sendMessageToAgent } from "../store/sendMessage";

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
      <div className="chat-header">
        <div className="chat-header-title">
          <span className="chat-bot">🤖</span>
          <span>AI Assistant</span>
        </div>
        <div className="chat-header-sub">Log Interaction details here via chat</div>
      </div>

      <div className="chat-thread" ref={threadRef}>
        {messages.map((m, i) => (
          <div
            key={i}
            className={`bubble bubble--${m.role} bubble--${m.variant || "default"}`}
          >
            {m.content}
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
        <button className="btn-log" onClick={submit} disabled={isLoading}>
          <span className="btn-log-a">A</span>
          <span className="btn-log-label">Log</span>
        </button>
      </div>
    </div>
  );
}
