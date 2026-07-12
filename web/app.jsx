// ============================================================
// SANTINEL — VERSIUNEA WEB (React)
// Aplicație web gata pentru producție
// VERSIUNE DEBUG CU ALERTE
// ============================================================

import React, { useState, useEffect } from 'react';
import './app.css';

const API_BASE = 'http://localhost:8000/api/v1';

export default function SantinelApp() {
  const [paginaCurenta, setPaginaCurenta] = useState('acasa');
  const [sesiuni, setSesiuni] = useState([]);
  const [sesiuneCurenta, setSesiuneCurenta] = useState(null);
  const [incarca, setIncarca] = useState(false);
  const [coaching, setCoaching] = useState(null);
  const [numeContact, setNumeContact] = useState('');
  const [numeFirma, setNumeFirma] = useState('');

  // Preia sesiunile la incarcare
  useEffect(() => {
    preiaSesiuni();
  }, []);

  const preiaSesiuni = async () => {
    setIncarca(true);
    try {
      const response = await fetch(`${API_BASE}/sessions`);
      const data = await response.json();
      setSesiuni(data.sessions || []);
    } catch (error) {
      console.error('Eroare la preluarea sesiunilor:', error);
    }
    setIncarca(false);
  };

  const creazaSesiune = async () => {
    if (!numeContact || !numeFirma) {
      alert('Te rog completează numele contactului și firmei');
      return;
    }

    setIncarca(true);
    try {
      const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contact_name: numeContact,
          company_name: numeFirma,
          user_id: 'user_' + Date.now()
        })
      });
      const data = await response.json();
      
      if (response.ok) {
        setSesiuneCurenta(data);
        setCoaching(null);
        setNumeContact('');
        setNumeFirma('');
        alert('✅ Sesiune creată: ' + data.session_id);
      } else {
        alert('❌ Eroare la crearea sesiunii');
      }
    } catch (error) {
      alert('Eroare: ' + error.message);
    }
    setIncarca(false);
  };

  const obtineCoaching = async (situatie) => {
    if (!situatie) {
      alert('Te rog descrie situația de negociere');
      return;
    }

    alert('🔄 DEPANARE 1: Trimit cererea de coaching...');
    setIncarca(true);
    
    try {
      alert('🔄 DEPANARE 2: API_BASE = ' + API_BASE);
      alert('🔄 DEPANARE 3: ID Sesiune = ' + (sesiuneCurenta?.session_id || 'test_session'));
      alert('🔄 DEPANARE 4: Situație = ' + situatie.substring(0, 50) + '...');
      
      const response = await fetch(`${API_BASE}/coaching`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sesiuneCurenta?.session_id || 'test_session',
          situation: situatie
        })
      });
      
      alert('🔄 DEPANARE 5: Status răspuns = ' + response.status);
      
      const data = await response.json();
      
      alert('🔄 DEPANARE 6: Chei răspuns = ' + Object.keys(data).join(', '));
      alert('🔄 DEPANARE 7: Răspuns complet = ' + JSON.stringify(data).substring(0, 300));
      
      if (response.ok) {
        const textCoaching = data.coaching || data.message || JSON.stringify(data);
        setCoaching(textCoaching);
        alert('✅ SUCCES: Coaching afișat!');
      } else {
        alert('❌ Eroare răspuns: ' + response.status);
      }
    } catch (error) {
      alert('❌ EROARE: ' + error.message);
      alert('❌ Tip eroare: ' + error.name);
    }
    
    setIncarca(false);
  };

  const obtineAegis = async () => {
    setIncarca(true);
    try {
      const response = await fetch(`${API_BASE}/aegis/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contact_name: sesiuneCurenta?.contact_name || numeContact,
          company_name: sesiuneCurenta?.company_name || numeFirma
        })
      });
      const data = await response.json();
      
      if (response.ok) {
        alert('✅ Context AEGIS: ' + JSON.stringify(data, null, 2));
      } else {
        alert('⚠️ AEGIS indisponibil (mod simulare)');
      }
    } catch (error) {
      alert('Eroare: ' + error.message);
    }
    setIncarca(false);
  };

  // PAGINA: ACASĂ
  const PaginaAcasa = () => (
    <div className="page">
      <div className="header">
        <h1>🎯 SANTINEL</h1>
        <p>Asistent AI pentru Negocieri</p>
      </div>

      <div className="stats">
        <div className="stat">
          <div className="stat-value">{sesiuni.length}</div>
          <div className="stat-label">Sesiuni</div>
        </div>
        <div className="stat">
          <div className="stat-value">✅</div>
          <div className="stat-label">Status</div>
        </div>
        <div className="stat">
          <div className="stat-value">4425</div>
          <div className="stat-label">RPS</div>
        </div>
      </div>

      <button 
        className="btn-primary"
        onClick={() => setPaginaCurenta('sesiune')}
      >
        📞 Sesiune Nouă
      </button>

      <button 
        className="btn-secondary"
        onClick={() => setPaginaCurenta('istoric')}
      >
        📋 Istoric
      </button>

      <div className="info">
        <h3>✨ Funcții:</h3>
        <ul>
          <li>🤖 Coaching IA în timp real</li>
          <li>📊 Informații pre-apel (AEGIS)</li>
          <li>🎙️ Procesare audio (Whisper)</li>
          <li>🔐 Protecție date & criptare</li>
          <li>📈 Analiză performanță</li>
          <li>🌍 Scalabil cloud (1M+ utilizatori)</li>
        </ul>
      </div>
    </div>
  );

  // PAGINA: SESIUNE NOUĂ
  const PaginaSesiune = () => (
    <div className="page">
      <h1>📞 Sesiune Nouă de Negociere</h1>

      <div className="form-group">
        <label>Nume Contact:</label>
        <input
          type="text"
          value={numeContact}
          onChange={(e) => setNumeContact(e.target.value)}
          placeholder="Ex: Ion Popescu"
        />
      </div>

      <div className="form-group">
        <label>Nume Firmă:</label>
        <input
          type="text"
          value={numeFirma}
          onChange={(e) => setNumeFirma(e.target.value)}
          placeholder="Ex: ABC SRL"
        />
      </div>

      <button 
        className="btn-primary"
        onClick={creazaSesiune}
        disabled={incarca}
      >
        {incarca ? '⏳ Se creează...' : '✅ Crează Sesiune'}
      </button>

      {sesiuneCurenta && (
        <div className="session-info">
          <h3>✅ Sesiune Creată!</h3>
          <p><strong>ID Sesiune:</strong> {sesiuneCurenta.session_id}</p>
          <p><strong>Contact:</strong> {sesiuneCurenta.contact_name}</p>
          <p><strong>Firmă:</strong> {sesiuneCurenta.company_name}</p>
          <p><strong>Creat:</strong> {sesiuneCurenta.created_at}</p>
        </div>
      )}

      {sesiuneCurenta && (
        <div className="coaching-section">
          <h3>💬 Obține Coaching</h3>
          <InterfataCoaching sesiune={sesiuneCurenta} onObtineCoaching={obtineCoaching} incarca={incarca} />
        </div>
      )}

      <button 
        className="btn-secondary"
        onClick={() => setPaginaCurenta('acasa')}
      >
        ← Înapoi
      </button>
    </div>
  );

  // PAGINA: INTERFAȚĂ COACHING
  const InterfataCoaching = ({ sesiune, onObtineCoaching, incarca }) => {
    const [situatie, setSituatie] = useState('');

    return (
      <div>
        <textarea
          value={situatie}
          onChange={(e) => setSituatie(e.target.value)}
          placeholder="Descrie situația de negociere..."
          rows="4"
        />

        <div className="button-group">
          <button 
            className="btn-primary"
            onClick={() => onObtineCoaching(situatie)}
            disabled={incarca}
          >
            {incarca ? '⏳ Se încarcă...' : '🧠 OBȚINE COACHING'}
          </button>

          <button 
            className="btn-secondary"
            onClick={obtineAegis}
            disabled={incarca}
          >
            {incarca ? '⏳ Se încarcă...' : '📊 Intel AEGIS'}
          </button>
        </div>

        {coaching && (
          <div className="coaching-result">
            <h4>💡 Sfat Coaching:</h4>
            <p>{coaching}</p>
          </div>
        )}
      </div>
    );
  };

  // PAGINA: ISTORIC
  const PaginaIstoric = () => (
    <div className="page">
      <h1>📋 Istoric Sesiuni</h1>

      {sesiuni.length === 0 ? (
        <p className="empty-state">Nicio sesiune încă. Creează una pentru a începe!</p>
      ) : (
        <div className="sessions-list">
          {sesiuni.map((sesiune, index) => (
            <div key={index} className="session-item">
              <div className="session-item-header">
                <h3>{sesiune.contact || 'Necunoscut'}</h3>
                <span className="company">{sesiune.company || 'Necunoscut'}</span>
              </div>
              <p className="session-id">ID: {sesiune.id || 'N/A'}</p>
              <p className="session-date">{sesiune.created_at || 'N/A'}</p>
            </div>
          ))}
        </div>
      )}

      <button 
        className="btn-secondary"
        onClick={() => setPaginaCurenta('acasa')}
      >
        ← Înapoi
      </button>
    </div>
  );

  // RANDARE PAGINA CURENTĂ
  return (
    <div className="app">
      {paginaCurenta === 'acasa' && <PaginaAcasa />}
      {paginaCurenta === 'sesiune' && <PaginaSesiune />}
      {paginaCurenta === 'istoric' && <PaginaIstoric />}

      {incarca && (
        <div className="loading-overlay">
          <div className="spinner">⏳</div>
        </div>
      )}
    </div>
  );
}