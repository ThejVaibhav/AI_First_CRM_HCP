import React from "react";
import { useSelector, useDispatch } from "react-redux";
import { resetInteraction } from "../store/interactionSlice";
import { resetChat } from "../store/chatSlice";
import VoiceNote from "./VoiceNote";

const SENTIMENTS = [
  { key: "Positive", emoji: "😊" },
  { key: "Neutral", emoji: "😐" },
  { key: "Negative", emoji: "😟" },
];

// Read-only field wrapper. Flashes yellow when the AI just populated it.
function Field({ label, name, updated, className = "", children }) {
  return (
    <div className={`field ${className} ${updated ? "field--flash" : ""}`}>
      {label && <label className="field-label">{label}</label>}
      {children}
    </div>
  );
}

export default function InteractionForm() {
  const dispatch = useDispatch();
  const s = useSelector((state) => state.interaction);
  const updated = (name) => s.recentlyUpdated?.includes(name);

  const handleClear = () => {
    dispatch(resetInteraction());
    dispatch(resetChat());
  };

  const materialsText = (s.materials_shared || []).join(", ");
  const samplesText = (s.samples_distributed || []).join(", ");

  return (
    <div className="form">
      <div className="form-header">
        <h1 className="form-title">Log HCP Interaction</h1>
        <button className="btn-clear" onClick={handleClear} title="Start a new interaction">
          Clear / New
        </button>
      </div>

      <div className="section-label">Interaction Details</div>

      <div className="field-row">
        <Field label="HCP Name" name="hcp_name" updated={updated("hcp_name")}>
          <div className="input-wrap">
            <span className="input-icon">🔍</span>
            <input
              className="ro-input has-icon"
              value={s.hcp_name}
              placeholder="Search or select HCP..."
              readOnly
            />
          </div>
        </Field>

        <Field
          label="Interaction Type"
          name="interaction_type"
          updated={updated("interaction_type")}
        >
          <div className="input-wrap">
            <input
              className="ro-input select-like"
              value={s.interaction_type || "Meeting"}
              readOnly
            />
            <span className="select-chevron">▾</span>
          </div>
        </Field>
      </div>

      <div className="field-row">
        <Field label="Date" name="date" updated={updated("date")}>
          <input className="ro-input" type="date" value={s.date || ""} readOnly disabled />
        </Field>
        <Field label="Time" name="time" updated={updated("time")}>
          <input className="ro-input" type="time" value={s.time || ""} readOnly disabled />
        </Field>
      </div>

      <Field label="Attendees" name="attendees" updated={updated("attendees")}>
        <input
          className="ro-input"
          value={s.attendees}
          placeholder="Enter names or search..."
          readOnly
        />
      </Field>

      <Field
        label="Topics Discussed"
        name="topics_discussed"
        updated={updated("topics_discussed")}
      >
        <textarea
          className="ro-input ro-area"
          value={s.topics_discussed}
          placeholder="Enter key discussion points..."
          rows={3}
          readOnly
        />
      </Field>

      {/* Voice Note input path (BRD 8.4). */}
      <VoiceNote />

      <div className="group-header">Materials Shared / Samples Distributed</div>

      <div className="field">
        <div className="sub-header">Materials Shared</div>
        <div className={`list-row ${updated("materials_shared") ? "field--flash" : ""}`}>
          <span className={materialsText ? "list-value" : "list-empty"}>
            {materialsText || "No materials added."}
          </span>
          <button className="btn-ghost">🔍 Search/Add</button>
        </div>
      </div>

      <div className="field">
        <div className="sub-header">Samples Distributed</div>
        <div className={`list-row ${updated("samples_distributed") ? "field--flash" : ""}`}>
          <span className={samplesText ? "list-value" : "list-empty"}>
            {samplesText || "No samples added."}
          </span>
          <button className="btn-ghost">+ Add Sample</button>
        </div>
      </div>

      <Field label="Observed/Inferred HCP Sentiment" name="sentiment" updated={updated("sentiment")}>
        <div className="sentiment-row">
          {SENTIMENTS.map((opt) => (
            <label
              key={opt.key}
              className={`sentiment ${s.sentiment === opt.key ? "sentiment--active" : ""}`}
            >
              <span className={`radio ${s.sentiment === opt.key ? "radio--on" : ""}`} />
              <span className="sentiment-emoji">{opt.emoji}</span>
              <span>{opt.key}</span>
            </label>
          ))}
        </div>
      </Field>

      <Field label="Outcomes" name="outcomes" updated={updated("outcomes")}>
        <textarea
          className="ro-input ro-area"
          value={s.outcomes}
          placeholder="Key outcomes or agreements..."
          rows={3}
          readOnly
        />
      </Field>

      <Field
        label="Follow-up Actions"
        name="follow_up_actions"
        updated={updated("follow_up_actions")}
      >
        <textarea
          className="ro-input ro-area"
          value={s.follow_up_actions}
          placeholder="Planned next steps..."
          rows={2}
          readOnly
        />
      </Field>
    </div>
  );
}
