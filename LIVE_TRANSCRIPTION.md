# FAZA 23.2 — Live Whisper transcription (Live Coaching)

Replaces the "paste a transcript" flow in **Live Coaching** with automatic
speech-to-text while the call is recorded.

## How it works — hybrid STT

| Layer | Engine | Role |
|---|---|---|
| Instant captions | Browser **Web Speech API** | word-by-word interim text as you speak (Chrome/Edge). Marked *provisional*. |
| Authoritative transcript | **Groq Whisper** (`whisper-large-v3-turbo`) | a `MediaRecorder` cuts the mic into ~4 s webm/opus segments; each is POSTed to `/api/transcribe` and its text **supersedes** the provisional Web-Speech phrases from that window. |

- If Web Speech is unavailable (Firefox/Safari), it degrades to **Whisper-only** —
  the transcript fills in ~4 s bursts.
- If the mic is blocked or `MediaRecorder`/`GROQ_API_KEY` is missing, the module
  still records for the vocal meters; the Whisper badge shows *unavailable* /
  *error* and the transcript can be typed/edited as before.
- **START RECORDING** opens the mic once (shared by the meters, Web Speech, and the
  Whisper recorder — no second prompt) and starts the segment loop.
- **STOP RECORDING** flushes the final segment (bounded wait, 8 s), then runs one
  forced full `/analyze` on the complete transcript — both parties, 3-tier,
  bilingual — on top of the continuous live analysis that already runs every ~4 s.

## Backend — `POST /api/transcribe` (`start_api.py`)

Thin, stateless proxy to Groq. Audio bytes are read, forwarded, and discarded —
nothing is written to disk or DB.

- **Auth:** requires a valid Bearer access token (`get_current_user`), same as
  `/analyze`.
- **Request:** `multipart/form-data` — `file` (audio blob), `lang` (`en` | `ro` |
  `auto`).
- **Response:** `200 {"text": "...", "model": "whisper-large-v3-turbo"}`.
- **Errors:** `401` no/invalid token · `503` `GROQ_API_KEY` unset · `413` segment
  > 25 MB · `502` Groq upstream error (message forwarded).

```bash
TOK=$(curl -s -X POST localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"me@example.com","password":"hunter2hunter"}' | jq -r .access_token)

curl -sS -H "Authorization: Bearer $TOK" \
  -F file=@segment.webm -F lang=en \
  http://localhost:8000/api/transcribe
# {"text":"They opened by asking for a fifteen percent discount.","model":"whisper-large-v3-turbo"}
```

## Setup

1. **Groq API key** — get one at <https://console.groq.com/keys>, then in `.env`:

   ```ini
   GROQ_API_KEY=gsk_...
   GROQ_STT_MODEL=whisper-large-v3-turbo   # or whisper-large-v3 for max accuracy
   ```

   Restart `start_api.py` to pick it up. Until it's set, `/api/transcribe`
   returns `503` and the UI badge reads *transcription error — retrying*.

2. No new packages — `requests` (already a dep) is used for the upstream call;
   `python-multipart` (already installed for auth) handles the upload. The pinned
   `groq==0.4.1` SDK is too old, hence the direct REST call.

3. Frontend: no new deps. The browser posts to the relative `/api/transcribe`, so
   it rides the existing Vite `/api` → `:8000` proxy (same-origin, no CORS) and
   reuses the JWT refresh flow in `web/authClient.js`.

## Scale notes ("100M+ users")

- **Stateless:** the endpoint holds no session and stores no audio — any number of
  API workers/hosts behind a load balancer are equivalent.
- **Inference is offloaded:** Groq owns the GPU fleet and autoscaling;
  `start_api.py` is a passthrough. Cost/latency scale linearly with audio minutes
  (~1–2 s per 4 s segment on `-turbo`).
- **Guardrails in place:** 25 MB per-segment cap, 30 s upstream timeout, client
  queue capped at 4 segments (drops oldest if Groq falls behind), single-flight
  drain to preserve order.
- **For very high volume (not built):** move rate-limiting per user to the edge
  proxy; consider signed, short-lived direct browser→Groq uploads so audio never
  transits our API; add a regional Groq endpoint pool.

## Files touched

- `start_api.py` — `POST /api/transcribe` + Groq config.
- `web/app.jsx` — `postTranscribe()` helper; `LiveCoaching` segment loop
  (`startWhisperSegment` / `rotateWhisperSegment` / `drainWhisperQueue` /
  `stopWhisperLoop`), `applyWhisperText` supersede logic, STOP finalize +
  forced analysis, engine badge + per-phrase tags, EN/RO strings.
- `web/app.css` — `.lc-eng-badge*`, `.lc-ph-eng`, `.lc-ph--prov`.
- `.env` / `.env.example` — `GROQ_API_KEY`, `GROQ_STT_MODEL`.
