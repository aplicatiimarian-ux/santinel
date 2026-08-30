# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

SANTINEL is an AI coaching assistant that gives real-time strategy suggestions during
business negotiations. Coaching output is written in **Romanian**; source comments mix
Romanian and English. Domain vocabulary: CBT / NLP / TA (Transactional Analysis) are the
psychology "frameworks", "dual-speaker" = analyzing both you and the counterparty, AEGIS
Veritas = a separate (external, not in this repo) company-intelligence platform.

## ⚠️ Secrets

`.env` and `.env.txt` were previously committed with **real API keys** (Groq, Mistral,
OpenAI, Pinecone). They have been purged from all of git history with `git-filter-repo`, and
`.gitignore` now excludes `.env` and `.env.*` (allowing only `*.example` templates). The
keys that were exposed must be treated as compromised and rotated at each provider.

Still present and unaddressed: `santinel.db` / `santinel_feedback.db` are committed SQLite
files, and `backend/fastapi_backend.py` + `migrate_data.py` hardcode
`postgresql://postgres:postgres123@localhost:5432/santinel_prod`. Keep new secrets out of
tracked files; real deployment values belong in `.env.production` (gitignored).

## Architecture — two disconnected halves

The repo contains two bodies of code that do **not** call each other. Know which one you are
touching.

### 1. The live web app (what actually runs)

**Backend — `backend/fastapi_backend.py`** (the current production API):

- FastAPI served by Uvicorn on **port 8002**, `host="0.0.0.0"` (`python backend/fastapi_backend.py`).
- Single flat module: Pydantic request models, framework helpers, and route handlers all in
  one file, no routers/packages/dependency-injection layering.
- **Persistence:** PostgreSQL `santinel_prod` via raw `psycopg2` + `RealDictCursor`.
  `DATABASE_URL` is hardcoded at the top of the file (not read from env). Every handler opens
  its own connection with `get_db_connection()`, runs inline SQL string literals, and closes
  in a `finally:` — no pooling, no ORM, no migrations framework. Table DDL lives in
  `schema.sql`.
- **Auth:** JWT (`pyjwt`, HS256, 24h expiry). `JWT_SECRET` from env with an insecure
  fallback. `create_token` / `verify_token` helpers exist, but **no endpoint actually
  depends on `verify_token`** — `/api/v1/login` only checks that the `users` row exists and
  never verifies the password (`hash_password` is defined but unused). Treat the whole API as
  effectively unauthenticated today.
- **Endpoints (all under `/api/v1`):** `POST /login`, `POST /sessions`,
  `GET /sessions/{id}`, `POST /coaching`, `POST /feedback`, `GET /finetuning/export`,
  `GET /finetuning/status/{job_id}` (stub), `GET /health`.
- **Coaching generation (`POST /coaching`):** calls `apply_cbt` / `apply_nlp` / `apply_ta` /
  `apply_dual_speaker` / `apply_goal_based`, which are **substring keyword matching** over the
  situation text that assemble a fixed Romanian coaching string. No LLM call, no use of the
  `core/` modules. Each call also inserts a row into `coaching_interactions`.
- **Caching:** `GET /finetuning/export` is memoised in **module-level globals**
  (`cache_export`, `cache_export_time`, 5-min TTL). The write endpoints (`sessions`,
  `coaching`, `feedback`) manually reset those globals to invalidate. Not multi-process safe.
- **CORS:** wide open — explicit localhost origins plus `"*"` with `allow_credentials=True`.

**Backend — `backend/feedback_database.py`** (previous generation, still in the tree):

- FastAPI on **port 8000**, persistence via a `FeedbackDatabase` class wrapping SQLite
  (`santinel_feedback.db`). Overlapping `/api/v1` paths plus extras that `fastapi_backend.py`
  dropped: `goals/add`, `audio/transcribe` + `audio/emotions` (stubs), `session/{id}/status`,
  `outcome`, `metrics/*` (feedback/outcomes/top-patterns). Superseded by
  `fastapi_backend.py`; keep changes in the port-8002 file unless a task explicitly concerns
  this one.

**Frontend:**

- **`web/`** — the React frontend that is actually served. Vite + React 18, a single
  component file `web/app.jsx` (dark/light mode, session form, coaching view, feedback,
  legal pages). Hardcodes `API_BASE = 'http://localhost:8002/api/v1'` at `web/app.jsx:119` —
  change there to repoint. `web/index.html` loads `/app.jsx` directly (JSX served by Vite).
- **`ui/ui_streamlit.py`** — an alternative Streamlit UI, not part of the web deployment.
- **`src/main.jsx`** + root `vite.config.js` — a second, half-wired Vite entry (`root: './web'`,
  imports `./app.css`). `web/vite.config.js` is the one that matches `web/index.html`. When
  building, prefer running Vite from inside `web/`.

### 2. The "SessionManager" pipeline (library code, wired only into tests)

Assembled top-down in **`module/session_complete.py`** (`SessionManager`), which composes:

- `core/core_complete.py` — `OrchestratorDualLLM` (Groq primary + Mistral fallback via HTTP),
  SQLAlchemy models + `Database` (SQLite `santinel.db`), `Config`.
- `anonimizare/anon_complete.py` — Presidio-based PII detection/anonymization with custom
  Romanian recognizers (CNP, phone, IBAN) + AES encryption of the mapping.
- `module/llm_complete.py` — `LLMClient` + Romanian `PromptTemplates`.
- `module/audio_complete.py`, `module/audio_whisper_bridge.py`,
  `module/whisper_real_integration.py` — audio capture + Whisper transcription.
- `bridge/aegis_bridge.py` — `AEGISBridge` / `ContextInjector`, HTTP client for the external
  AEGIS intel API (`AEGIS_API_URL`, default `http://localhost:8000`).
- `core/cbt_module.py`, `core/nlp_module.py`, `core/ta_module.py`,
  `core/dual_speaker_analyzer.py`, `core/goal_coaching_engine.py` — the real framework logic.

This pipeline is exercised by `tests/integration_test.py` and by `if __name__ == "__main__"`
blocks in individual modules. It is **not** reachable from the web API. If a task is about
"the coaching the app produces", that is half 1; if it's about LLMs / PII / audio / AEGIS,
it's half 2.

### Databases

- **SQLite** — `santinel.db` (SQLAlchemy, used by `core/` pipeline),
  `santinel_feedback.db` (used by `feedback_database.py`). Both committed.
- **PostgreSQL** — `santinel_prod`, used by `fastapi_backend.py`. Full schema in
  `schema.sql` (~18 tables: users, third_parties, sessions, coaching_interactions,
  feedback, outcomes, vector_patterns, finetuning_jobs, voice_fingerprints, …).
- `migrate_data.py` — one-off SQLite→Postgres data copy. `database/postgresql_migration.py`
  — schema/DDL migration helper for the SQLAlchemy models.
- `check_db.py` — quick table/row dump of `santinel_feedback.db`.

### Forward-looking / not yet integrated

`backend/vector_db_integration.py` (Pinecone), `backend/finetuning_pipeline.py`,
`PHASE2_VECTORDB_SCHEMA.md`, `mobile/mobile_ui_scaffold.py` — design/scaffold code for the
self-improvement loop; `USE_MOCK_VECTORDB=true` in `.env`.

## Commands

Python: no venv is committed (`venv/` is gitignored but present locally). Use Python 3.10+.

```bash
pip install -r requirements.txt   # groq, mistralai, presidio, sqlalchemy, pydantic, python-dotenv
```

Note `requirements.txt` is incomplete — the running backend also needs
`fastapi uvicorn psycopg2-binary pyjwt`, and the `core/` pipeline needs `pycryptodome`,
`requests`, plus Whisper deps for audio.

### Run the live app

```bash
python backend/fastapi_backend.py        # API on http://0.0.0.0:8002
cd web && npm install && npm run dev      # frontend on http://localhost:5173
```

Requires a running PostgreSQL with `santinel_prod` loaded from `schema.sql`.

```bash
npm run build      # (in web/) outputs to ../dist per root vite.config.js, or web/dist otherwise
```

### Tests

There is no pytest setup. The `test_*` methods in `tests/integration_test.py` are run by a
custom harness — execute the file directly:

```bash
python tests/integration_test.py          # end-to-end: SessionManager + LLM + AEGIS
python testing/load_testing.py            # load/stress scenarios against the API
python security/security_audit.py         # PII / auth / config audit checks
```

Most `core/` and `module/` files have their own `__main__` self-test — run a single module in
isolation with e.g. `python -m core.core_complete` or `python module/llm_complete.py`.

### DB helpers

```bash
python check_db.py            # inspect santinel_feedback.db
python migrate_data.py        # SQLite -> PostgreSQL (expects postgres123 / santinel_prod)
./pg.bat -d santinel_prod     # wrapper around the PostgreSQL 18 psql.exe
```

## Deployment

`README_PRODUCTION.md` + `LAUNCH_CHECKLIST.md` describe the target prod setup: Nginx
terminating TLS and proxying `/api/` to the backend, Uvicorn (or gunicorn `-w 4`) under a
systemd unit, `.env.production` with `chmod 600`. Frontend build served as static files from
`dist/`.
