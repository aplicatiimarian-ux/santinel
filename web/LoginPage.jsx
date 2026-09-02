import React, { useState } from 'react';
import { login, register } from './authClient.js';

/* Auth-screen copy is kept local so this component stays decoupled from the
   large `t` table in app.jsx. */
const AUTH_T = {
  en: {
    tagline: 'AI coaching for negotiations',
    signIn: 'Sign in',
    createAccount: 'Create account',
    email: 'Email',
    password: 'Password',
    pwHint: 'At least 8 characters',
    working: 'Please wait…',
    noAccount: "Don't have an account?",
    hasAccount: 'Already have an account?',
    toRegister: 'Create one',
    toLogin: 'Sign in',
    genericError: 'Something went wrong. Please try again.',
  },
  ro: {
    tagline: 'Coaching AI pentru negocieri',
    signIn: 'Autentificare',
    createAccount: 'Creează cont',
    email: 'Email',
    password: 'Parolă',
    pwHint: 'Minim 8 caractere',
    working: 'Te rugăm așteaptă…',
    noAccount: 'Nu ai cont?',
    hasAccount: 'Ai deja cont?',
    toRegister: 'Creează unul',
    toLogin: 'Autentifică-te',
    genericError: 'Ceva nu a mers. Încearcă din nou.',
  },
};

export default function LoginPage({
  lang = 'en',
  onAuthed,
  onToggleLang,
  onToggleTheme,
  darkMode = true,
}) {
  const T = AUTH_T[lang] || AUTH_T.en;
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const isRegister = mode === 'register';

  const submit = async (e) => {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError('');
    try {
      const fn = isRegister ? register : login;
      const data = await fn(email.trim().toLowerCase(), password);
      onAuthed(data.access_token);
    } catch (err) {
      const detail = err && err.response && err.response.data && err.response.data.detail;
      setError(typeof detail === 'string' ? detail : T.genericError);
      setBusy(false);
    }
  };

  return (
    <div className="si-auth-wrap">
      <div className="si-auth-topbar">
        <span className="si-auth-brand">SANTINEL</span>
        <span className="si-auth-actions">
          <button type="button" className="si-chip" onClick={onToggleTheme} aria-label="Toggle theme">
            {darkMode ? '☀️' : '\u{1F319}'}
          </button>
          <button type="button" className="si-chip" onClick={onToggleLang}>
            {lang === 'en' ? 'RO' : 'EN'}
          </button>
        </span>
      </div>

      <form className="si-auth-card" onSubmit={submit}>
        <h1 className="si-auth-title">{isRegister ? T.createAccount : T.signIn}</h1>
        <p className="si-auth-tagline">{T.tagline}</p>

        <label className="si-auth-field">
          <span>{T.email}</span>
          <input
            className="si-auth-input"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>

        <label className="si-auth-field">
          <span>{T.password}</span>
          <input
            className="si-auth-input"
            type="password"
            autoComplete={isRegister ? 'new-password' : 'current-password'}
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {isRegister && <small className="si-auth-hint">{T.pwHint}</small>}
        </label>

        {error && <div className="si-auth-error">{error}</div>}

        <button type="submit" className="si-auth-btn" disabled={busy}>
          {busy ? T.working : isRegister ? T.createAccount : T.signIn}
        </button>

        <div className="si-auth-switch">
          {isRegister ? T.hasAccount : T.noAccount}{' '}
          <button
            type="button"
            onClick={() => {
              setError('');
              setMode(isRegister ? 'login' : 'register');
            }}
          >
            {isRegister ? T.toLogin : T.toRegister}
          </button>
        </div>
      </form>
    </div>
  );
}
