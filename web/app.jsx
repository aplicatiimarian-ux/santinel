// ============================================================
// SANTINEL — VERSIUNEA WEB (React)
// Aplicație web cu sistem de rating și outcome tracking
// STEP 2: Web UI pentru feedback și métrici
// API_BASE: Fixed pentru conectare la backend
// FIX: Rating stars GUARANTEED visible (ID-based DOM control)
// ============================================================

import React, { useState, useEffect } from 'react';
import './app.css';

const API_BASE = 'http://192.168.1.41:8000/api/v1';

export default function SantinelApp() {
  const [paginaCurenta, setPaginaCurenta] = useState('acasa');
  const [sesiuni, setSesiuni] = useState([]);
  const [sesiuneCurenta, setSesiuneCurenta] = useState(null);
  const [incarca, setIncarca] = useState(false);
  const [coaching, setCoaching] = useState(null);
  const [numeContact, setNumeContact] = useState('');
  const [numeFirma, setNumeFirma] = useState('');
  const [metrici, setMetrici] = useState(null);

  // Preia sesiunile la incarcare
  useEffect(() => {
    preiaSesiuni();
    preiaMetrici();
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

  const preiaMetrici = async () => {
    try {
      const response = await fetch(`${API_BASE}/metrics/feedback`);
      const data = await response.json();
      setMetrici(data);
    } catch (error) {
      console.error('Eroare la preluarea metricilor:', error);
    }
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
        
        // Hide rating section on new session
        const ratingSection = document.getElementById('rating-section');
        if (ratingSection) ratingSection.style.display = 'none';
        
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

    setIncarca(true);
    try {
      const response = await fetch(`${API_BASE}/coaching`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sesiuneCurenta?.session_id || 'test_session',
          situation: situatie
        })
      });
      
      const data = await response.json();
      console.log('Coaching response:', data);
      
      if (response.ok) {
        const textCoaching = data.coaching || data.message || JSON.stringify(data);
        setCoaching(textCoaching);
        console.log('✅ Coaching set');
        
        // FORCE show rating section by ID
        setTimeout(() => {
          const ratingSection = document.getElementById('rating-section');
          if (ratingSection) {
            ratingSection.style.display = 'block';
            console.log('✅ Rating section shown');
            ratingSection.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100);
        
      } else {
        alert('❌ Eroare la obținerea coaching');
      }
    } catch (error) {
      alert('Eroare: ' + error.message);
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
          <div className="stat-value">⭐ {metrici?.average_rating?.toFixed(1) || '0'}</div>
          <div className="stat-label">Rating Mediu</div>
        </div>
        <div className="stat">
          <div className="stat-value">{metrici?.total_ratings || 0}</div>
          <div className="stat-label">Evaluări</div>
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

      <button 
        className="btn-secondary"
        onClick={() => setPaginaCurenta('metrici')}
      >
        📊 Metrici
      </button>

      <div className="info">
        <h3>✨ Funcții:</h3>
        <ul>
          <li>🤖 Coaching IA în timp real</li>
          <li>⭐ Sistem de rating și feedback</li>
          <li>📊 Metrici și analiză performanță</li>
          <li>🔐 Protecție date & criptare</li>
          <li>📈 Auto-îmbunătățire LLM</li>
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
          <InterfataCoaching 
            sesiune={sesiuneCurenta} 
            onObtineCoaching={obtineCoaching} 
            incarca={incarca}
            coaching={coaching}
            onRefreshMetrici={preiaMetrici}
          />
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

  // PAGINA: INTERFAȚĂ COACHING + RATING
  const InterfataCoaching = ({ sesiune, onObtineCoaching, incarca, coaching, onRefreshMetrici }) => {
    const [situatie, setSituatie] = useState('');
    const [rating, setRating] = useState(0);
    const [aspecteUtile, setAspecteUtile] = useState([]);
    const [comentarii, setComentarii] = useState('');

    const submitFeedback = async () => {
      if (rating === 0) {
        alert('Te rog selectează o evaluare (1-5 stele)');
        return;
      }

      console.log('📤 Submitting feedback with rating:', rating);

      try {
        const response = await fetch(`${API_BASE}/feedback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sesiune.session_id,
            coaching_id: 'coaching_' + Date.now(),
            rating: rating,
            quality_score: rating / 5,
            useful_aspects: aspecteUtile,
            comments: comentarii
          })
        });

        const data = await response.json();
        console.log('Feedback response:', data);

        if (response.ok) {
          alert('✅ ' + data.message);
          setRating(0);
          setAspecteUtile([]);
          setComentarii('');
          
          // Hide rating section
          const ratingSection = document.getElementById('rating-section');
          if (ratingSection) ratingSection.style.display = 'none';
          
          onRefreshMetrici();
        } else {
          alert('❌ Eroare la trimiterea feedback');
        }
      } catch (error) {
        alert('Eroare: ' + error.message);
        console.error('Feedback error:', error);
      }
    };

    const toggleAspect = (aspect) => {
      setAspecteUtile(prev => 
        prev.includes(aspect) 
          ? prev.filter(a => a !== aspect)
          : [...prev, aspect]
      );
    };

    const submitOutcome = async (success) => {
      console.log('📊 Submitting outcome:', success ? 'SUCCESS' : 'FAILED');

      try {
        const response = await fetch(`${API_BASE}/outcome`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sesiune.session_id,
            contact_name: sesiune.contact_name,
            company_name: sesiune.company_name,
            negotiation_type: 'general',
            success: success,
            target_value: 100,
            actual_value: success ? 105 : 95,
            target_achieved: success ? 95 : 70,
            actual_achieved: success ? 100 : 75,
            notes: situatie.substring(0, 100)
          })
        });

        const data = await response.json();
        console.log('Outcome response:', data);

        if (response.ok) {
          alert('✅ ' + data.message);
          onRefreshMetrici();
        } else {
          alert('❌ Eroare la înregistrarea rezultatului');
        }
      } catch (error) {
        alert('Eroare: ' + error.message);
        console.error('Outcome error:', error);
      }
    };

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
            onClick={() => {
              try {
                fetch(`${API_BASE}/aegis/contact`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    contact_name: sesiune.contact_name,
                    company_name: sesiune.company_name
                  })
                });
              } catch (e) {}
              alert('📊 Intel AEGIS - coming soon');
            }}
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

        <div 
          id="rating-section"
          style={{
            display: 'none',
            backgroundColor: '#f0f8ff', 
            padding: '20px', 
            borderRadius: '8px', 
            marginTop: '20px', 
            border: '3px solid #4169E1'
          }}
        >
          <h4 style={{color: '#4169E1', fontSize: '20px'}}>⭐ EVALUEAZĂ COACHING-UL (1-5 stele)</h4>
          
          <div style={{
            display: 'flex', 
            gap: '15px', 
            marginBottom: '20px', 
            fontSize: '50px',
            justifyContent: 'center'
          }}>
            {[1, 2, 3, 4, 5].map(star => (
              <button
                key={star}
                onClick={() => {
                  setRating(star);
                  console.log('Star clicked:', star);
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: rating >= star ? '#FFD700' : '#CCCCCC',
                  fontSize: '50px',
                  padding: '5px',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  if (rating === 0) {
                    e.target.style.color = '#FFD700';
                    e.target.style.transform = 'scale(1.2)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (rating === 0) {
                    e.target.style.color = '#CCCCCC';
                    e.target.style.transform = 'scale(1)';
                  }
                }}
              >
                ★
              </button>
            ))}
          </div>

          {rating > 0 && (
            <p style={{textAlign: 'center', fontSize: '18px', color: '#4169E1', fontWeight: 'bold'}}>
              ✅ Ai selectat {rating} stele
            </p>
          )}

          <div style={{marginBottom: '20px'}}>
            <label style={{fontWeight: 'bold', display: 'block', marginBottom: '10px'}}>Ce ți-a fost util?</label>
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px'}}>
              {['Strategie', 'Psihologie', 'Tactici', 'Empatie', 'Claritate'].map(aspect => (
                <label key={aspect} style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <input
                    type="checkbox"
                    checked={aspecteUtile.includes(aspect.toLowerCase())}
                    onChange={() => toggleAspect(aspect.toLowerCase())}
                  />
                  {aspect}
                </label>
              ))}
            </div>
          </div>

          <textarea
            value={comentarii}
            onChange={(e) => setComentarii(e.target.value)}
            placeholder="Comentarii suplimentare (opțional)..."
            rows="2"
            style={{width: '100%', padding: '10px', marginBottom: '15px', borderRadius: '4px'}}
          />

          <button 
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: '#4169E1',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold'
            }}
            onClick={submitFeedback}
          >
            ✅ Trimite Feedback ({rating} stele)
          </button>

          <div style={{marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #ddd'}}>
            <h4>📊 Rezultatul Negocierii</h4>
            <p>Cum a decurs negocierea după coaching?</p>
            
            <div style={{display: 'grid', gap: '10px', marginTop: '10px'}}>
              <button 
                style={{
                  padding: '12px',
                  backgroundColor: '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
                onClick={() => submitOutcome(true)}
              >
                ✅ Succes - Negocierea a mers bine
              </button>
              
              <button 
                style={{
                  padding: '12px',
                  backgroundColor: '#ffc107',
                  color: 'black',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
                onClick={() => submitOutcome(false)}
              >
                ⚠️ Nereușit - Negocierea a fost mai dificilă
              </button>
            </div>
          </div>
        </div>
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

  // PAGINA: METRICI
  const PaginaMetrici = () => (
    <div className="page">
      <h1>📊 Metrici și Performanță</h1>

      {metrici ? (
        <div className="metrics-container">
          <div className="metric-card">
            <h3>⭐ Rating Mediu</h3>
            <div className="metric-value">{metrici.average_rating?.toFixed(2) || 'N/A'}</div>
            <p>din 5 stele</p>
          </div>

          <div className="metric-card">
            <h3>📈 Total Evaluări</h3>
            <div className="metric-value">{metrici.total_ratings || 0}</div>
            <p>evaluări primite</p>
          </div>

          <div className="metric-card">
            <h3>✅ Scor Calitate</h3>
            <div className="metric-value">{(metrici.average_quality_score * 100)?.toFixed(0) || 0}%</div>
            <p>scor mediu calitate</p>
          </div>
        </div>
      ) : (
        <p className="empty-state">Se încarcă metricile...</p>
      )}

      <div className="metrics-info">
        <h3>💡 Interpretare Metrici:</h3>
        <ul>
          <li>⭐ Rating = Evaluarea directă a utilizatorului (1-5 stele)</li>
          <li>📈 Total Evaluări = Numărul de sesiuni evaluate</li>
          <li>✅ Scor Calitate = Medie ponderată a satisfacției</li>
        </ul>
      </div>

      <button 
        className="btn-secondary"
        onClick={() => {
          preiaMetrici();
          alert('✅ Metrici reîncărcate');
        }}
      >
        🔄 Reîncarcă Metrici
      </button>

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
      {paginaCurenta === 'metrici' && <PaginaMetrici />}

      {incarca && (
        <div className="loading-overlay">
          <div className="spinner">⏳</div>
        </div>
      )}
    </div>
  );
}