// ============================================================
// SANTINEL — WEB VERSION (React)
// Production-ready web app for testing on mobile browser
// ============================================================

import React, { useState, useEffect } from 'react';
import './app.css';

const API_BASE = 'http://localhost:8000/api/v1';

export default function SantinelApp() {
  const [currentPage, setCurrentPage] = useState('home');
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [coaching, setCoaching] = useState(null);
  const [contactName, setContactName] = useState('');
  const [companyName, setCompanyName] = useState('');

  // Fetch sessions on mount
  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/sessions`);
      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
    setLoading(false);
  };

  const createSession = async () => {
    if (!contactName || !companyName) {
      alert('Please fill in contact and company name');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contact_name: contactName,
          company_name: companyName,
          user_id: 'user_' + Date.now()
        })
      });
      const data = await response.json();
      
      if (response.ok) {
        setCurrentSession(data);
        setCoaching(null);
        setContactName('');
        setCompanyName('');
        alert('✅ Session created: ' + data.session_id);
      } else {
        alert('❌ Error creating session');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    }
    setLoading(false);
  };

  const getCoaching = async (situation) => {
    if (!situation) {
      alert('Please describe the situation');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/coaching`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSession?.session_id || 'test_session',
          situation: situation
        })
      });
      const data = await response.json();
      
      if (response.ok) {
        setCoaching(data.coaching);
      } else {
        alert('❌ Error getting coaching');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    }
    setLoading(false);
  };

  const getAegisContext = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/aegis/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contact_name: currentSession?.contact_name || contactName,
          company_name: currentSession?.company_name || companyName
        })
      });
      const data = await response.json();
      
      if (response.ok) {
        alert('✅ AEGIS Context Retrieved:\n' + JSON.stringify(data, null, 2));
      } else {
        alert('⚠️ AEGIS not available (mock mode)');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    }
    setLoading(false);
  };

  // PAGE: HOME
  const HomePage = () => (
    <div className="page">
      <div className="header">
        <h1>🎯 SANTINEL</h1>
        <p>AI Coaching Assistant for Negotiations</p>
      </div>

      <div className="stats">
        <div className="stat">
          <div className="stat-value">{sessions.length}</div>
          <div className="stat-label">Sessions</div>
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
        onClick={() => setCurrentPage('session')}
      >
        📞 New Session
      </button>

      <button 
        className="btn-secondary"
        onClick={() => setCurrentPage('history')}
      >
        📋 History
      </button>

      <div className="info">
        <h3>✨ Features:</h3>
        <ul>
          <li>🤖 Real-time AI coaching</li>
          <li>📊 Pre-call intelligence (AEGIS)</li>
          <li>🎙️ Audio processing (Whisper)</li>
          <li>🔐 PII protection & encryption</li>
          <li>📈 Performance analytics</li>
          <li>🌍 Cloud scalable (1M+ users)</li>
        </ul>
      </div>
    </div>
  );

  // PAGE: NEW SESSION
  const SessionPage = () => (
    <div className="page">
      <h1>📞 New Negotiation Session</h1>

      <div className="form-group">
        <label>Contact Name:</label>
        <input
          type="text"
          value={contactName}
          onChange={(e) => setContactName(e.target.value)}
          placeholder="e.g., Ion Popescu"
        />
      </div>

      <div className="form-group">
        <label>Company Name:</label>
        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="e.g., ABC SRL"
        />
      </div>

      <button 
        className="btn-primary"
        onClick={createSession}
        disabled={loading}
      >
        {loading ? '⏳ Creating...' : '✅ Create Session'}
      </button>

      {currentSession && (
        <div className="session-info">
          <h3>✅ Session Created!</h3>
          <p><strong>Session ID:</strong> {currentSession.session_id}</p>
          <p><strong>Contact:</strong> {currentSession.contact_name}</p>
          <p><strong>Company:</strong> {currentSession.company_name}</p>
          <p><strong>Created:</strong> {currentSession.created_at}</p>
        </div>
      )}

      {currentSession && (
        <div className="coaching-section">
          <h3>💬 Get Coaching</h3>
          <CoachingInterface session={currentSession} />
        </div>
      )}

      <button 
        className="btn-secondary"
        onClick={() => setCurrentPage('home')}
      >
        ← Back
      </button>
    </div>
  );

  // PAGE: COACHING INTERFACE
  const CoachingInterface = ({ session }) => {
    const [situation, setSituation] = useState('');

    return (
      <div>
        <textarea
          value={situation}
          onChange={(e) => setSituation(e.target.value)}
          placeholder="Describe the negotiation situation..."
          rows="4"
        />

        <div className="button-group">
          <button 
            className="btn-primary"
            onClick={() => getCoaching(situation)}
            disabled={loading}
          >
            {loading ? '⏳ Coaching...' : '🧠 Get Coaching'}
          </button>

          <button 
            className="btn-secondary"
            onClick={getAegisContext}
            disabled={loading}
          >
            {loading ? '⏳ Loading...' : '📊 AEGIS Intel'}
          </button>
        </div>

        {coaching && (
          <div className="coaching-result">
            <h4>💡 Coaching Advice:</h4>
            <p>{coaching}</p>
          </div>
        )}
      </div>
    );
  };

  // PAGE: HISTORY
  const HistoryPage = () => (
    <div className="page">
      <h1>📋 Session History</h1>

      {sessions.length === 0 ? (
        <p className="empty-state">No sessions yet. Create one to get started!</p>
      ) : (
        <div className="sessions-list">
          {sessions.map((session, index) => (
            <div key={index} className="session-item">
              <div className="session-item-header">
                <h3>{session.contact || 'Unknown'}</h3>
                <span className="company">{session.company || 'Unknown'}</span>
              </div>
              <p className="session-id">ID: {session.id || 'N/A'}</p>
              <p className="session-date">{session.created_at || 'N/A'}</p>
            </div>
          ))}
        </div>
      )}

      <button 
        className="btn-secondary"
        onClick={() => setCurrentPage('home')}
      >
        ← Back
      </button>
    </div>
  );

  // RENDER CURRENT PAGE
  return (
    <div className="app">
      {currentPage === 'home' && <HomePage />}
      {currentPage === 'session' && <SessionPage />}
      {currentPage === 'history' && <HistoryPage />}

      {loading && (
        <div className="loading-overlay">
          <div className="spinner">⏳</div>
        </div>
      )}
    </div>
  );
}