# AI-First CRM — HCP Module: Log Interaction Screen

An **AI-First** CRM screen for pharma field reps. The rep **never fills the form
manually** — a **LangGraph** agent (driven by **Groq** LLMs) reads a natural-language
message (typed or spoken) and populates a read-only form on the left. Everything
flows through the AI Assistant chat on the right.

> Built per BRD v2.0. The video instructions are authoritative: **the left form is
> display-only; all data entry flows through the AI Assistant.**

---

## Architecture (BRD §11)

| Layer            | Technology                                             |
| ---------------- | ------------------------------------------------------ |
| Frontend         | React 18 (Hooks) + Redux Toolkit + Vite + Axios        |
| Font             | Google **Inter** (throughout)                          |
| Backend          | Python 3.11+ · FastAPI · CORS enabled                  |
| Agent framework  | **LangGraph** (graph: `llm_node` ⇄ `tool_executor_node`) |
| LLM — primary    | Groq **`gemma2-9b-it`** (routing + extraction)         |
| LLM — secondary  | Groq **`llama-3.3-70b-versatile`** (summaries / NBA)   |
| Speech-to-Text   | Groq **Whisper** (`/api/voice/transcribe`)             |
| Database         | PostgreSQL (JSONB) via SQLAlchemy + Alembic            |

**Zero hardcoded extraction** — no regex/keyword parsing anywhere. The LLM performs
all entity extraction, date resolution, and sentiment inference (BRD C2).

### The exactly-5 LangGraph tools (BRD §9, C8)

1. `log_interaction` — extract & log a new interaction (also the target of Voice Note)
2. `edit_interaction` — update only the named field(s), leave others untouched (C4)
3. `schedule_followup` — add a follow-up to the record
4. `suggest_next_action` — LLM-generated next-best-action from current + past history
5. `search_hcp_history` — summarize past interactions for an HCP

**Voice Note is an input _path_, not a 6th tool (C9):** MediaRecorder (with browser
consent) → Groq Whisper → transcribed text → injected into the chat → `log_interaction`.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ running locally
- A **new** Groq API key (BRD C6)

### Create a new Groq API key

1. Go to <https://console.groq.com> and sign in.
2. Create a **new** API key (do not reuse an existing token).
3. Copy it into `backend/.env` as `GROQ_API_KEY`.

---

## Backend setup

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
#   → set GROQ_API_KEY and DATABASE_URL

# Create the database (once)
createdb hcp_crm         # or: psql -c "CREATE DATABASE hcp_crm;"

# Apply the schema
alembic upgrade head

# Run the API (http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```

Health check: <http://localhost:8000/api/health> → `{"status":"ok"}`
Interactive docs: <http://localhost:8000/docs>

### Environment variables (`backend/.env`)

| Variable          | Example                                            |
| ----------------- | -------------------------------------------------- |
| `GROQ_API_KEY`    | `gsk_...` (new token from console.groq.com)        |
| `DATABASE_URL`    | `postgresql://user:pass@localhost:5432/hcp_crm`    |
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:5173`      |
| `BACKEND_PORT`    | `8000`                                             |

---

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_URL=http://localhost:8000
npm run dev                 # http://localhost:5173
```

CORS is preconfigured for `localhost:3000` and `localhost:5173` (BRD C13).

---

## Using it

Type (or speak via the Voice Note link) something like:

> _Met Dr. Smith today, discussed Prodo-X efficacy, positive sentiment, shared the
> clinical brochure and left 2 samples._

The agent extracts every field, infers sentiment, resolves "today" to a real date,
saves to PostgreSQL, and the left form animates as it fills in. Then try:

- **Edit:** _"Change the sentiment to Neutral"_ → only sentiment changes.
- **Follow-up:** _"Schedule a follow-up with Dr. Smith next Monday at 2pm"_
- **Next action:** _"What should I do next?"_
- **History:** _"What did I last discuss with Dr. Smith?"_

---

## API endpoints (BRD §13)

| Method | Endpoint                          | Purpose                          |
| ------ | --------------------------------- | -------------------------------- |
| POST   | `/api/agent`                      | Main LangGraph agent             |
| POST   | `/api/voice/transcribe`           | Voice Note → Whisper STT         |
| POST   | `/api/interactions`               | Create record                    |
| GET    | `/api/interactions/{id}`          | Get record                       |
| PUT    | `/api/interactions/{id}`          | Update record                    |
| GET    | `/api/interactions/hcp/{name}`    | All records for an HCP           |
| GET    | `/api/hcps`                       | HCP list for typeahead           |
| GET    | `/api/health`                     | Health check                     |

---

## Project structure

```
backend/
  app/
    main.py           # FastAPI app + CORS
    config.py         # env settings
    database.py       # SQLAlchemy engine/session
    models.py         # hcp_interactions ORM
    schemas.py        # Pydantic models
    agent/
      llm.py          # Groq model factories
      state.py        # LangGraph state (BRD 9.1)
      graph.py        # llm_node ⇄ tool_executor_node (BRD 9.2)
      tools.py        # the 5 tools (schemas + handlers)
    routers/          # agent, voice, interactions, hcps, health
  alembic/            # migrations
frontend/
  src/
    App.jsx           # split-screen layout
    store/            # interaction / chat / agent slices (BRD 11.3)
    components/       # InteractionForm, ChatPanel, VoiceNote
    api/client.js     # Axios calls
```

---

## Notes

- All code in this repo was generated with AI tooling per the assignment rules.
- Mock/seed HCP data is used for the typeahead (BRD §7.2).
- Errors (Groq timeout, mic denied, empty message) surface as graceful chat
  messages and never crash the UI (BRD §14).
