import React, { useState } from 'react';
import './app.css';

export default function App() {
  const [lang, setLang] = useState('en');

  const content = {
    en: {
      title: '🎯 SANTINEL',
      subtitle: 'AI Coaching for Active Listening',
      status: '✅ Development Server Active',
      button: 'Schimbă în Română'
    },
    ro: {
      title: '🎯 SANTINEL',
      subtitle: 'Asistent AI pentru Ascultare Activă',
      status: '✅ Server de Dezvoltare Activ',
      button: 'Switch to English'
    }
  };

  const t = content[lang];

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      backgroundColor: '#f8f9fa',
      padding: '20px'
    }}>
      <div style={{ textAlign: 'center', maxWidth: '600px' }}>
        <h1 style={{ fontSize: '3rem', margin: '0 0 10px 0' }}>{t.title}</h1>
        <p style={{ fontSize: '1.3rem', color: '#666', margin: '0 0 20px 0' }}>{t.subtitle}</p>
        <p style={{ fontSize: '1.1rem', color: '#0066cc', margin: '20px 0' }}>{t.status}</p>

        <button
          onClick={() => setLang(lang === 'en' ? 'ro' : 'en')}
          style={{
            padding: '12px 24px',
            fontSize: '1rem',
            backgroundColor: '#0066cc',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            marginTop: '20px',
            fontWeight: 'bold'
          }}
        >
          {t.button}
        </button>

        <div style={{
          marginTop: '40px',
          padding: '20px',
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <p style={{ fontSize: '0.9rem', color: '#666' }}>
            {lang === 'en'
              ? 'Development environment ready. Full app loading...'
              : 'Mediu de dezvoltare gata. Aplicația completă se încarcă...'}
          </p>
        </div>
      </div>
    </div>
  );
}
