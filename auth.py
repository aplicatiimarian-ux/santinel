# -*- coding: utf-8 -*-
"""
SANTINEL — JWT authentication.

Stateless access tokens (15 min, HS256) + rotating refresh tokens (7 days) carried
in an httpOnly `SameSite=Lax` cookie. Access-token validation never touches the DB,
so protected endpoints stay cheap and the API scales horizontally; only
`/api/auth/*` (login / refresh / logout) reads or writes Postgres.

Routes (mounted under `/api/auth`, reached from the browser through the Vite
`/api` -> `:8000` dev proxy so the refresh cookie is same-origin):

    POST /register   {email, password}  -> access token + refresh cookie
    POST /login      {email, password}  -> access token + refresh cookie
    POST /refresh    (refresh cookie)   -> new access token + rotated refresh cookie
    POST /logout     (refresh cookie)   -> 204, cookie cleared, refresh row revoked
    GET  /me         (Bearer)           -> current user

`auth_guard.py` re-exports `get_current_user` as the dependency other route modules
(e.g. `start_api.py`) attach to protect their endpoints.
"""

import base64
import hashlib
import os
import re
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import bcrypt
import jwt
import psycopg2
import psycopg2.errors
import psycopg2.pool
from psycopg2.extras import RealDictCursor

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

load_dotenv()

# --------------------------------------------------------------------------- #
#  Config                                                                     #
# --------------------------------------------------------------------------- #

DEBUG = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes", "on")

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    if DEBUG:
        JWT_SECRET = "dev-insecure-secret-do-not-use-in-production"
        print("[auth] WARNING: JWT_SECRET unset — using an insecure dev fallback.")
    else:
        raise RuntimeError("JWT_SECRET environment variable is required")

JWT_ALGO = "HS256"
ACCESS_TTL_MIN = int(os.getenv("JWT_ACCESS_TTL_MIN", "15"))
REFRESH_TTL_DAYS = int(os.getenv("JWT_REFRESH_TTL_DAYS", "7"))

AUTH_DATABASE_URL = os.getenv(
    "AUTH_DATABASE_URL",
    "postgresql://postgres:postgres123@localhost:5432/santinel_prod",
)

COOKIE_NAME = "refresh_token"
COOKIE_PATH = "/api/auth"
COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "false").lower() in ("1", "true", "yes", "on")

MIN_PASSWORD_LEN = 8
MAX_PASSWORD_LEN = 128
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# --------------------------------------------------------------------------- #
#  Database (lazy pool — importing this module must not require a live DB)     #
# --------------------------------------------------------------------------- #

_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None


def _get_pool() -> psycopg2.pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.ThreadedConnectionPool(1, 10, dsn=AUTH_DATABASE_URL)
    return _pool


@contextmanager
def db_cursor(commit: bool = False):
    """Borrow a pooled connection, yield a RealDictCursor, always return it."""
    try:
        pool = _get_pool()
    except psycopg2.Error as exc:  # pragma: no cover - infra
        raise HTTPException(status_code=503, detail="auth database unavailable") from exc
    conn = pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        conn.commit() if commit else conn.rollback()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


# --------------------------------------------------------------------------- #
#  Passwords                                                                  #
# --------------------------------------------------------------------------- #

def _prehash(password: str) -> bytes:
    """SHA-256 -> base64 so long passwords survive bcrypt's 72-byte limit."""
    return base64.b64encode(hashlib.sha256(password.encode("utf-8")).digest())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_prehash(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_prehash(password), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# --------------------------------------------------------------------------- #
#  Tokens                                                                     #
# --------------------------------------------------------------------------- #

def _now() -> datetime:
    return datetime.now(timezone.utc)


def make_access(user_id: int) -> str:
    now = _now()
    payload = {
        "sub": str(user_id),
        "type": "access",
        "jti": secrets.token_urlsafe(12),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TTL_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def make_refresh(user_id: int) -> Tuple[str, str, datetime]:
    now = _now()
    jti = secrets.token_urlsafe(24)
    exp = now + timedelta(days=REFRESH_TTL_DAYS)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO), jti, exp


def decode_token(token: str, expected_type: str) -> dict:
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token expired",
                            headers={"WWW-Authenticate": "Bearer"})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid token",
                            headers={"WWW-Authenticate": "Bearer"})
    if claims.get("type") != expected_type:
        raise HTTPException(status_code=401, detail="wrong token type",
                            headers={"WWW-Authenticate": "Bearer"})
    if "sub" not in claims or "jti" not in claims:
        raise HTTPException(status_code=401, detail="malformed token")
    return claims


def _jti_hash(jti: str) -> str:
    return hashlib.sha256(jti.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
#  Bearer dependency (re-exported by auth_guard.py)                           #
# --------------------------------------------------------------------------- #

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> dict:
    """Require a valid access token; return {user_id, jti}. 401 otherwise."""
    if creds is None or (creds.scheme or "").lower() != "bearer" or not creds.credentials:
        raise HTTPException(status_code=401, detail="missing bearer token",
                            headers={"WWW-Authenticate": "Bearer"})
    claims = decode_token(creds.credentials, "access")
    return {"user_id": int(claims["sub"]), "jti": claims.get("jti")}


def get_current_user_optional(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> Optional[dict]:
    """Like get_current_user but returns None instead of raising."""
    if creds is None or not creds.credentials:
        return None
    try:
        claims = decode_token(creds.credentials, "access")
    except HTTPException:
        return None
    return {"user_id": int(claims["sub"]), "jti": claims.get("jti")}


# --------------------------------------------------------------------------- #
#  Cookie helpers                                                             #
# --------------------------------------------------------------------------- #

def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=REFRESH_TTL_DAYS * 24 * 3600,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path=COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, path=COOKIE_PATH)


# --------------------------------------------------------------------------- #
#  Request / response models & validation                                     #
# --------------------------------------------------------------------------- #

class Credentials(BaseModel):
    email: str
    password: str


def _clean_email(email: str) -> str:
    return (email or "").strip().lower()


def _validate_new_credentials(email: str, password: str) -> str:
    email = _clean_email(email)
    if not _EMAIL_RE.match(email) or len(email) > 255:
        raise HTTPException(status_code=422, detail="invalid email address")
    if not (MIN_PASSWORD_LEN <= len(password or "") <= MAX_PASSWORD_LEN):
        raise HTTPException(
            status_code=422,
            detail=f"password must be {MIN_PASSWORD_LEN}-{MAX_PASSWORD_LEN} characters",
        )
    return email


def _token_payload(access: str, user: Optional[dict] = None) -> dict:
    body = {
        "access_token": access,
        "token_type": "bearer",
        "expires_in": ACCESS_TTL_MIN * 60,
    }
    if user is not None:
        body["user"] = user
    return body


def _record_refresh(cur, user_id: int, jti: str, expires_at: datetime, request: Request) -> None:
    ua = (request.headers.get("user-agent") or "")[:255]
    ip = ((request.client.host if request.client else "") or "")[:64]
    cur.execute(
        "INSERT INTO refresh_tokens (user_id, jti_hash, expires_at, user_agent, ip) "
        "VALUES (%s, %s, %s, %s, %s)",
        (user_id, _jti_hash(jti), expires_at, ua, ip),
    )


def _revoke_all(cur, user_id: int) -> None:
    cur.execute(
        "UPDATE refresh_tokens SET revoked_at = now() "
        "WHERE user_id = %s AND revoked_at IS NULL",
        (user_id,),
    )


# --------------------------------------------------------------------------- #
#  Routes                                                                     #
# --------------------------------------------------------------------------- #

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(body: Credentials, request: Request, response: Response):
    email = _validate_new_credentials(body.email, body.password)
    pw_hash = hash_password(body.password)
    try:
        with db_cursor(commit=True) as cur:
            cur.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                raise HTTPException(status_code=409, detail="email already registered")
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING user_id",
                (email, pw_hash),
            )
            user_id = cur.fetchone()["user_id"]
            access = make_access(user_id)
            refresh, jti, exp = make_refresh(user_id)
            _record_refresh(cur, user_id, jti, exp, request)
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="email already registered")
    _set_refresh_cookie(response, refresh)
    return _token_payload(access, {"user_id": user_id, "email": email})


@router.post("/login")
def login(body: Credentials, request: Request, response: Response):
    email = _clean_email(body.email)
    with db_cursor(commit=True) as cur:
        cur.execute(
            "SELECT user_id, password_hash FROM users WHERE email = %s", (email,)
        )
        row = cur.fetchone()
        if not row or not verify_password(body.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="invalid email or password")
        user_id = row["user_id"]
        access = make_access(user_id)
        refresh, jti, exp = make_refresh(user_id)
        _record_refresh(cur, user_id, jti, exp, request)
    _set_refresh_cookie(response, refresh)
    return _token_payload(access, {"user_id": user_id, "email": email})


@router.post("/refresh")
def refresh(request: Request, response: Response):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="missing refresh token")
    claims = decode_token(token, "refresh")
    user_id = int(claims["sub"])
    jti_hash = _jti_hash(claims["jti"])

    reuse = False
    new_refresh = None
    with db_cursor(commit=True) as cur:
        cur.execute(
            "SELECT id, revoked_at, expires_at FROM refresh_tokens WHERE jti_hash = %s",
            (jti_hash,),
        )
        row = cur.fetchone()
        if row is None or row["revoked_at"] is not None or row["expires_at"] <= _now():
            # A validly-signed refresh token we don't recognise, or one that was
            # already rotated away: assume theft and drop every session.
            _revoke_all(cur, user_id)
            reuse = True
        else:
            cur.execute(
                "UPDATE refresh_tokens SET revoked_at = now() WHERE id = %s", (row["id"],)
            )
            access = make_access(user_id)
            new_refresh, new_jti, new_exp = make_refresh(user_id)
            _record_refresh(cur, user_id, new_jti, new_exp, request)

    if reuse:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="refresh token rejected")

    _set_refresh_cookie(response, new_refresh)
    return _token_payload(access)


@router.post("/logout")
def logout(request: Request):
    resp = Response(status_code=204)
    token = request.cookies.get(COOKIE_NAME)
    if token:
        try:
            claims = decode_token(token, "refresh")
            with db_cursor(commit=True) as cur:
                cur.execute(
                    "UPDATE refresh_tokens SET revoked_at = now() "
                    "WHERE jti_hash = %s AND revoked_at IS NULL",
                    (_jti_hash(claims["jti"]),),
                )
        except Exception:
            pass  # already-invalid token — still clear the cookie
    _clear_refresh_cookie(resp)
    return resp


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    with db_cursor() as cur:
        cur.execute(
            "SELECT user_id, email, created_at FROM users WHERE user_id = %s",
            (user["user_id"],),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="user not found")
    return {
        "user_id": row["user_id"],
        "email": row["email"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
    }
