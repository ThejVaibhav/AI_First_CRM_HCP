import React from "react";
import { useSelector, useDispatch } from "react-redux";
import {
  User,
  Briefcase,
  Calendar,
  Clock,
  Users,
  ClipboardList,
  FileText,
  Package,
  Heart,
  Target,
  Bell,
  Search,
  Plus,
  Stethoscope,
  RotateCcw,
  ChevronDown,
} from "lucide-react";
import { resetInteraction } from "../store/interactionSlice";
import { resetChat } from "../store/chatSlice";
import VoiceNote from "./VoiceNote";

const SENTIMENTS = [
  { key: "Positive", emoji: "😊", cls: "pos" },
  { key: "Neutral", emoji: "😐", cls: "neu" },
  { key: "Negative", emoji: "😟", cls: "neg" },
];

// Label row with a leading lucide icon.
function Label({ icon: Icon, children }) {
  return (
    <label className="field-label">
      <Icon size={13} className="label-icon" />
      {children}
    </label>
  );
}

// Read-only input with an icon inside on the left. Flashes when AI populates.
function IconInput({ icon: Icon, value, placeholder, updated, ...rest }) {
  return (
    <div className={`input-wrap ${updated ? "field--flash" : ""}`}>
      <Icon size={16} className="input-icon" />
      <input className="ro-input has-icon" value={value} placeholder={placeholder} readOnly {...rest} />
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
      <div className="accent-bar" />

      <div className="form-header">
        <div className="title-group">
          <div className="title-row">
            <Stethoscope size={26} className="title-icon" />
            <h1 className="form-title">Log HCP Interaction</h1>
          </div>
          <div className="form-tagline">Healthcare Professional Interaction Tracker</div>
        </div>
        <button className="btn-new" onClick={handleClear} title="Start a new interaction">
          <RotateCcw size={15} />
          New
        </button>
      </div>

      {/* Card 1 — Interaction Details */}
      <div className="card">
        <div className="card-title">Interaction Details</div>

        <div className="field-row">
          <div className="field">
            <Label icon={User}>HCP Name</Label>
            <IconInput
              icon={User}
              value={s.hcp_name}
              placeholder="Search or select HCP..."
              updated={updated("hcp_name")}
            />
          </div>
          <div className="field">
            <Label icon={Briefcase}>Interaction Type</Label>
            <div className={`input-wrap ${updated("interaction_type") ? "field--flash" : ""}`}>
              <Briefcase size={16} className="input-icon" />
              <input
                className="ro-input has-icon select-like"
                value={s.interaction_type || "Meeting"}
                readOnly
              />
              <ChevronDown size={16} className="select-chevron" />
            </div>
          </div>
        </div>

        <div className="field-row">
          <div className="field">
            <Label icon={Calendar}>Date</Label>
            <div className={`input-wrap ${updated("date") ? "field--flash" : ""}`}>
              <Calendar size={16} className="input-icon" />
              <input className="ro-input has-icon" type="date" value={s.date || ""} readOnly disabled />
            </div>
          </div>
          <div className="field">
            <Label icon={Clock}>Time</Label>
            <div className={`input-wrap ${updated("time") ? "field--flash" : ""}`}>
              <Clock size={16} className="input-icon" />
              <input className="ro-input has-icon" type="time" value={s.time || ""} readOnly disabled />
            </div>
          </div>
        </div>

        <div className="field">
          <Label icon={Users}>Attendees</Label>
          <IconInput
            icon={Users}
            value={s.attendees}
            placeholder="Enter names or search..."
            updated={updated("attendees")}
          />
        </div>
      </div>

      {/* Card 2 — Discussion & Materials */}
      <div className="card">
        <div className="card-title">Discussion &amp; Materials</div>

        <div className="field">
          <Label icon={ClipboardList}>Topics Discussed</Label>
          <div className={`input-wrap ${updated("topics_discussed") ? "field--flash" : ""}`}>
            <textarea
              className="ro-input ro-area"
              value={s.topics_discussed}
              placeholder="Enter key discussion points..."
              rows={3}
              readOnly
            />
          </div>
          <VoiceNote />
        </div>

        <div className="field">
          <Label icon={FileText}>Materials Shared</Label>
          <div className={`list-row ${updated("materials_shared") ? "field--flash" : ""}`}>
            <span className={materialsText ? "list-value" : "list-empty"}>
              {materialsText || "No materials added."}
            </span>
            <button className="btn-ghost">
              <Search size={14} /> Search/Add
            </button>
          </div>
        </div>

        <div className="field">
          <Label icon={Package}>Samples Distributed</Label>
          <div className={`list-row ${updated("samples_distributed") ? "field--flash" : ""}`}>
            <span className={samplesText ? "list-value" : "list-empty"}>
              {samplesText || "No samples added."}
            </span>
            <button className="btn-ghost">
              <Plus size={14} /> Add Sample
            </button>
          </div>
        </div>
      </div>

      {/* Card 3 — Assessment & Outcomes */}
      <div className="card">
        <div className="card-title">Assessment &amp; Outcomes</div>

        <div className={`field ${updated("sentiment") ? "field--flash" : ""}`}>
          <Label icon={Heart}>HCP Sentiment</Label>
          <div className="sentiment-group">
            {SENTIMENTS.map((opt) => (
              <button
                key={opt.key}
                className={`pill pill--${opt.cls} ${s.sentiment === opt.key ? "pill--on" : ""}`}
              >
                <span className="pill-emoji">{opt.emoji}</span>
                {opt.key}
              </button>
            ))}
          </div>
        </div>

        <div className="field">
          <Label icon={Target}>Outcomes</Label>
          <div className={`input-wrap ${updated("outcomes") ? "field--flash" : ""}`}>
            <textarea
              className="ro-input ro-area"
              value={s.outcomes}
              placeholder="Key outcomes or agreements..."
              rows={3}
              readOnly
            />
          </div>
        </div>

        <div className="field">
          <Label icon={Bell}>Follow-up Actions</Label>
          <div className={`input-wrap ${updated("follow_up_actions") ? "field--flash" : ""}`}>
            <textarea
              className="ro-input ro-area"
              value={s.follow_up_actions}
              placeholder="Planned next steps..."
              rows={2}
              readOnly
            />
          </div>
        </div>
      </div>
    </div>
  );
}
