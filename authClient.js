/* -------------------------------------------------------------------------- */
/*  authClient.js — JWT session handling for the SANTINEL web app             */
/*                                                                            */
/*  Access token  : short-lived (15 min), kept in localStorage, sent as       */
/*                  `Authorization: Bearer` on API calls.                      */
/*  Refresh token : httpOnly SameSite=Lax cookie set by the backend. Never    */
/*                  visible to JS. Rides along automatically on same-origin    */
/*                  `/api/auth/*` requests (Vite proxies `/api` -> :8000).     */
/*                                                                            */
/*  Call `ensureFreshToken()` before an authenticated request: it refreshes   */
/*  in place when the access token is missing or within 5 min of expiry, and  */
/*  coalesces concurrent callers onto a single in-flight refresh.             */
/* -------------------------------------------------------------------------- */

import axios from 'axios';

const TOKEN_KEY = 'si_access_token';
const REFRESH_SKEW_SEC = 300;

/** Fired on `window` when the session can no longer be recovered. */
export const AUTH_LOST_EVENT = 'si-auth-lost';

export const api = axios.create({ baseURL: '/api', withCredentials: true });

/* ---- token storage ------------------------------------------------------- */

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || null;
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* private mode / storage disabled — session lasts only this page load */
  }
}

export function clearToken() {
  setToken(null);
}

/* ---- expiry ------------------------------------------------------------- */

function decodeExp(token) {
  if (!token) return 0;
  try {
    const part = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(part));
    return typeof payload.exp === 'number' ? payload.exp : 0;
  } catch {
    return 0;
  }
}

export function isExpiringSoon(skewSec = REFRESH_SKEW_SEC) {
  const exp = decodeExp(getToken());
  if (!exp) return true;
  return exp - Math.floor(Date.now() / 1000) < skewSec;
}

/* ---- refresh (single-flight) ------------------------------------------- */

let inflightRefresh = null;

export function ensureFreshToken() {
  const current = getToken();
  if (current && !isExpiringSoon()) return Promise.resolve(current);

  if (!inflightRefresh) {
    inflightRefresh = api
      .post('/auth/refresh')
      .then((res) => {
        const next = res.data && res.data.access_token;
        setToken(next);
        return next;
      })
      .catch((err) => {
        clearToken();
        throw err;
      })
      .finally(() => {
        inflightRefresh = null;
      });
  }
  return inflightRefresh;
}

export function signalAuthLost() {
  clearToken();
  try {
    window.dispatchEvent(new Event(AUTH_LOST_EVENT));
  } catch {
    /* non-browser context */
  }
}

/* ---- auth actions ----------------------------------------------------- */

export async function login(email, password) {
  const res = await api.post('/auth/login', { email, password });
  setToken(res.data.access_token);
  return res.data;
}

export async function register(email, password) {
  const res = await api.post('/auth/register', { email, password });
  setToken(res.data.access_token);
  return res.data;
}

export async function logout() {
  try {
    await api.post('/auth/logout');
  } finally {
    clearToken();
  }
}

/* ---- axios wiring ---------------------------------------------------- */

api.interceptors.request.use((config) => {
  const url = config.url || '';
  const token = getToken();
  if (token && !url.includes('/auth/')) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config || {};
    const status = error.response && error.response.status;
    const url = config.url || '';
    const isAuthCall = url.includes('/auth/');

    if (status === 401 && !config._retry && !isAuthCall) {
      config._retry = true;
      try {
        const token = await ensureFreshToken();
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${token}`;
        return await api(config);
      } catch {
        signalAuthLost();
      }
    }
    return Promise.reject(error);
  },
);
