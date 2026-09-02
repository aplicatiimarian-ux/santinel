# SANTINEL — JWT Authentication

Adds register / login / logout / refresh to the live web app (`start_api.py` on
`:8000` + `web/app.jsx` on `:5173`). Access-token checks are stateless (pure JWT
verification, no DB round-trip), so the API scales horizontally and guarding an
endpoint adds well under a millisecond.

## Token model

| | Lifetime | Where it lives | Sent as |
|---|---|---|---|
| **Access token** | 15 min (`JWT_ACCESS_TTL_MIN`) | `localStorage['si_access_token']` | `Authorization: Bearer …` |
| **Refresh token** | 7 days (`JWT_REFRESH_TTL_DAYS`) | httpOnly `SameSite=Lax` cookie, path `/api/auth` | automatically, on `/api/auth/*` |

- Both are HS256 JWTs signed with `JWT_SECRET`.
- The browser reaches `/api/auth/*` **through the Vite dev proxy** (`/api` →
  `http://localhost:8000`), so the refresh cookie is same-origin and needs no
  HTTPS in dev. In production put the API behind the same origin as the SPA (or a
  parent domain) and set `AUTH_COOKIE_SECURE=true`.
- Refresh tokens **rotate** on every `/refresh`; the previous one is revoked. Only
  `sha256(jti)` is stored (table `refresh_tokens`), never the token itself.
- **Reuse detection:** presenting an already-rotated or unknown refresh token
  revokes every session for that user.

## One-time setup

1. **Python deps** (into the committed venv):

   ```bash
   ./venv/Scripts/python.exe -m pip install PyJWT bcrypt python-dotenv
   ```

   (Also in `requirements.txt`, alongside `fastapi`, `uvicorn`, `psycopg2-binary`.)

2. **Database migration** — `users` already exists; this adds `refresh_tokens`:

   ```bash
   ./pg.bat -d santinel_prod -f migrations/001_auth.sql
   ```

   or apply it with any Postgres client. It is idempotent (`IF NOT EXISTS`).

3. **Environment** — add to `.env` (gitignored; see `.env.example` for the template):

   ```ini
   JWT_SECRET=<64+ hex chars>
   JWT_ACCESS_TTL_MIN=15
   JWT_REFRESH_TTL_DAYS=7
   AUTH_DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/santinel_prod
   CORS_ORIGINS=http://localhost:5173,http://192.168.1.50:5173
   AUTH_COOKIE_SECURE=false
   ```

   Generate a secret:

   ```bash
   ./venv/Scripts/python.exe -c "import secrets; print(secrets.token_hex(48))"
   ```

   If `JWT_SECRET` is unset the API refuses to start unless `DEBUG=true` (then it
   uses an insecure dev fallback and prints a warning).

## Run

```bash
./venv/Scripts/python.exe start_api.py      # API + auth on http://0.0.0.0:8000
npm run dev                                  # SPA on http://localhost:5173 (repo root)
```

`GET /health` stays public. `GET|POST /analyze` now requires a valid Bearer token.

## Endpoints (`/api/auth`)

| Method | Path | Body | Result |
|---|---|---|---|
| POST | `/register` | `{email, password}` | `{access_token, token_type, expires_in, user}` + refresh cookie |
| POST | `/login` | `{email, password}` | same as register |
| POST | `/refresh` | — (refresh cookie) | `{access_token, token_type, expires_in}` + rotated cookie |
| POST | `/logout` | — (refresh cookie) | `204`, cookie cleared, refresh row revoked |
| GET | `/me` | — (Bearer) | `{user_id, email, created_at}` |

Password rules: 8–128 chars. Login returns a generic `401` for both unknown email
and wrong password (no user enumeration). Duplicate email on register → `409`.

## curl walkthrough

```bash
# register (save cookies to a jar)
curl -s -c jar.txt -X POST http://localhost:8000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"me@example.com","password":"hunter2hunter"}'

ACCESS=<access_token from the response>

# protected call succeeds with the token, 401 without it
curl -s -H "Authorization: Bearer $ACCESS" \
  "http://localhost:8000/analyze?text=they%20want%20a%20discount&lang=en"
curl -s -o /dev/null -w '%{http_code}\n' \
  "http://localhost:8000/analyze?text=hello"      # -> 401

# rotate the refresh token
curl -s -b jar.txt -c jar.txt -X POST http://localhost:8000/api/auth/refresh

# logout, then refresh fails
curl -s -b jar.txt -c jar.txt -X POST http://localhost:8000/api/auth/logout
curl -s -o /dev/null -w '%{http_code}\n' \
  -b jar.txt -X POST http://localhost:8000/api/auth/refresh   # -> 401
```

## Frontend behaviour

- `web/authClient.js` owns storage, expiry checks, single-flight refresh, and an
  axios instance (`baseURL: '/api'`, `withCredentials: true`) with interceptors
  that attach the Bearer header and retry once on `401`.
- `web/app.jsx` `App()` gates the whole shell: no valid session → `<LoginPage>`.
  On mount it calls `ensureFreshToken()` once to silently restore a session from
  the refresh cookie (survives page reload). A 60 s timer refreshes ahead of
  expiry; `postAnalyze()` also refreshes just-in-time and retries once on `401`.
- The sidebar **LOGOUT** button calls `/api/auth/logout` and clears local state.
- `web/ProtectedRoute.jsx` — thin `authed ? children : fallback` wrapper, unused
  by the root gate, kept for future per-section guarding.

## Production notes

- `AUTH_COOKIE_SECURE=true` behind TLS; serve SPA and API same-origin (Nginx
  proxying `/api/` to Uvicorn) so the `SameSite=Lax` cookie works without
  `SameSite=None`.
- Set a strong, per-environment `JWT_SECRET` (rotating it invalidates all tokens).
- Tighten `CORS_ORIGINS` to the real web origin(s).
- Rate-limit `/api/auth/login` and `/api/auth/register` at the proxy.
- Prune expired refresh rows on a schedule:
  `DELETE FROM refresh_tokens WHERE expires_at < now() - INTERVAL '7 days';`
- Multiple API workers/hosts are fine — access-token validation needs only
  `JWT_SECRET`; only refresh/logout touch the shared `refresh_tokens` table.
