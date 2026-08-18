import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import './app.css';

function SantinelApp() {
  const [currentView, setCurrentView] = useState('home');
  const [userId, setUserId] = useState('2');
  const [sessionId, setSessionId] = useState('');
  const [contactName, setContactName] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [situation, setSituation] = useState('');
  const [coaching, setCoaching] = useState('');
  const [rating, setRating] = useState(5);
  const [qualityScore, setQualityScore] = useState(0.95);
  const [comments, setComments] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [patterns, setPatterns] = useState([]);
  const [darkMode, setDarkMode] = useState(true);
  const [frameworksUsed, setFrameworksUsed] = useState([]);

  const API_BASE = 'http://localhost:8002/api/v1';

  useEffect(() => {
    if (darkMode) {
      document.body.classList.remove('light-mode');
    } else {
      document.body.classList.add('light-mode');
    }
  }, [darkMode]);

  const showMessage = (text, type = 'error') => {
    setMessage(text);
    setMessageType(type);
    setTimeout(() => setMessage(''), 5000);
  };

  const handleCreateSession = async () => {
    if (!contactName || !companyName) {
      showMessage('Please fill in all fields', 'error');
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
          user_id: userId
        })
      });

      const data = await response.json();
      if (response.ok) {
        setSessionId(data.session_id);
        showMessage(`Session created for ${data.contact_name}`, 'success');
        setCurrentView('coaching');
        setContactName('');
        setCompanyName('');
      } else {
        showMessage(`Error: ${data.detail}`, 'error');
      }
    } catch (error) {
      showMessage(`Network error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleGetCoaching = async () => {
    if (!situation) {
      showMessage('Please describe your situation', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/coaching`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          situation: situation,
          is_reactive: false
        })
      });

      const data = await response.json();
      if (response.ok) {
        setCoaching(data.coaching);
        const frameworks = data.frameworks_applied?.frameworks_applied || 
          data.frameworks_applied || 
          ['CBT', 'NLP', 'TA'];
        setFrameworksUsed(Array.isArray(frameworks) ? frameworks : []);
        showMessage('Coaching delivered', 'success');
        setSituation('');
        setCurrentView('feedback');
      } else {
        showMessage(`Error: ${data.detail}`, 'error');
      }
    } catch (error) {
      showMessage(`Network error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFeedback = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          coaching_id: `coaching_${Date.now()}`,
          rating: parseInt(rating),
          quality_score: parseFloat(qualityScore),
          useful_aspects: ['Strategy', 'Clarity', 'Framework'],
          comments: comments
        })
      });

      const data = await response.json();
      if (response.ok) {
        showMessage('Feedback saved successfully', 'success');
        setComments('');
        setCurrentView('export');
      } else {
        showMessage(`Error: ${data.detail}`, 'error');
      }
    } catch (error) {
      showMessage(`Network error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPatterns = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/finetuning/export`);
      const data = await response.json();
      if (response.ok) {
        setPatterns(data.data.training_examples);
        showMessage(`Exported ${data.patterns} patterns`, 'success');
      } else {
        showMessage(`Error: ${data.detail}`, 'error');
      }
    } catch (error) {
      showMessage(`Network error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const resetSession = () => {
    setContactName('');
    setCompanyName('');
    setSituation('');
    setCoaching('');
    setRating(5);
    setQualityScore(0.95);
    setComments('');
    setSessionId('');
    setFrameworksUsed([]);
    setCurrentView('home');
  };

  const ThemeToggle = () => (
    <button 
      onClick={() => setDarkMode(!darkMode)}
      title="Toggle dark/light mode"
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: '1000',
        padding: '8px 12px',
        fontSize: '1.4rem',
        background: darkMode ? 'rgba(30, 41, 59, 0.95)' : 'rgba(248, 250, 252, 0.95)',
        border: darkMode ? '1px solid #475569' : '1px solid #cbd5e1',
        borderRadius: '50%',
        cursor: 'pointer',
        width: '50px',
        height: '50px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'all 0.2s ease',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
      }}
      onMouseEnter={(e) => {
        e.target.style.transform = 'scale(1.1)';
        e.target.style.boxShadow = '0 6px 16px rgba(99, 102, 241, 0.3)';
      }}
      onMouseLeave={(e) => {
        e.target.style.transform = 'scale(1)';
        e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
      }}
    >
      {darkMode ? '☀️' : '🌙'}
    </button>
  );

  if (currentView === 'home') {
    return (
      <div className="container">
        <ThemeToggle />
        <h1>SANTINEL</h1>
        <p>Professional Psychological Negotiation Coach</p>

        <div className="form-section">
          <h2>Start New Session</h2>
          <label>Contact Name:</label>
          <input
            type="text"
            placeholder="Who are you negotiating with?"
            value={contactName}
            onChange={(e) => setContactName(e.target.value)}
          />
          <label>Company Name:</label>
          <input
            type="text"
            placeholder="Their organization"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
          />
          <button onClick={handleCreateSession} disabled={loading}>
            {loading ? 'Creating...' : 'Create Session'}
          </button>
        </div>

        {message && (
          <div className={`message ${messageType === 'success' ? 'success' : ''}`}>
            {message}
          </div>
        )}
        {sessionId && (
          <div className="success">
            Session ID: {sessionId}
          </div>
        )}
      </div>
    );
  }

  if (currentView === 'coaching') {
    return (
      <div className="container">
        <ThemeToggle />
        <h1>Negotiation Coaching</h1>
        <p>Session: {sessionId}</p>

        <div className="form-section">
          <h2>Describe Your Situation</h2>
          <label>Negotiation Scenario:</label>
          <textarea
            placeholder="What's your negotiation scenario? Provide context, goals, challenges, and what you want to achieve."
            value={situation}
            onChange={(e) => setSituation(e.target.value)}
          />
          <button onClick={handleGetCoaching} disabled={loading}>
            {loading ? 'Generating...' : 'Get Coaching'}
          </button>
        </div>

        {coaching && (
          <div className="coaching-section">
            <h2>Professional Coaching Response</h2>
            <div className="coaching-text">{coaching}</div>
            {frameworksUsed.length > 0 && (
              <p style={{ marginTop: '15px', fontSize: '0.85rem', color: '#a1a5b0' }}>
                <strong>Psychology Frameworks Applied:</strong><br/>
                {frameworksUsed.join(', ')}
              </p>
            )}
          </div>
        )}

        {message && (
          <div className={`message ${messageType === 'success' ? 'success' : ''}`}>
            {message}
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
          <button onClick={() => setCurrentView('home')} style={{ flex: 1 }}>
            Back to Home
          </button>
          {coaching && (
            <button onClick={() => setCurrentView('feedback')} style={{ flex: 1 }}>
              Rate This Coaching
            </button>
          )}
        </div>
      </div>
    );
  }

  if (currentView === 'feedback') {
    return (
      <div className="container">
        <ThemeToggle />
        <h1>Rate Coaching Quality</h1>
        <p>Session: {sessionId}</p>

        <div className="form-section">
          <h2>Feedback Form</h2>
          
          <label>How helpful was this coaching?</label>
          <select value={rating} onChange={(e) => setRating(e.target.value)}>
            <option value="1">1 - Not helpful</option>
            <option value="2">2 - Somewhat helpful</option>
            <option value="3">3 - Neutral</option>
            <option value="4">4 - Very helpful</option>
            <option value="5">5 - Extremely helpful</option>
          </select>

          <label>Quality Score (0.0 - 1.0):</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={qualityScore}
            onChange={(e) => setQualityScore(e.target.value)}
          />

          <label>Your Comments:</label>
          <textarea
            placeholder="What worked well? What could improve? Any specific insights?"
            value={comments}
            onChange={(e) => setComments(e.target.value)}
          />

          <button onClick={handleSubmitFeedback} disabled={loading}>
            {loading ? 'Submitting...' : 'Submit Feedback'}
          </button>
        </div>

        {message && (
          <div className={`message ${messageType === 'success' ? 'success' : ''}`}>
            {message}
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
          <button onClick={() => setCurrentView('coaching')} style={{ flex: 1 }}>
            Back to Coaching
          </button>
        </div>
      </div>
    );
  }

  if (currentView === 'export') {
    return (
      <div className="container">
        <ThemeToggle />
        <h1>Export High-Quality Patterns</h1>
        <p>Ready for continuous improvement and model refinement</p>

        <div className="form-section">
          <h2>Pattern Analysis & Export</h2>
          <p>Export your coaching patterns to create high-quality training data for the system to learn from your best coaching moments.</p>
          <button onClick={handleExportPatterns} disabled={loading}>
            {loading ? 'Exporting...' : 'Export Patterns'}
          </button>
        </div>

        {patterns.length > 0 && (
          <div className="patterns-section">
            <h2>High-Quality Patterns ({patterns.length} found)</h2>
            {patterns.map((pattern, idx) => (
              <div key={idx} className="pattern-card">
                <h4>Pattern {pattern.pattern_id}</h4>
                <p><strong>Rating:</strong> {pattern.rating}/5 ⭐</p>
                <p><strong>Quality Score:</strong> {(pattern.quality_score * 100).toFixed(0)}%</p>
                <p><strong>Coaching Excerpt:</strong></p>
                <p style={{ fontSize: '0.85rem', fontStyle: 'italic' }}>
                  "{pattern.coaching_text.substring(0, 120)}..."
                </p>
                <p><strong>Frameworks Used:</strong> {pattern.frameworks_used.join(', ')}</p>
              </div>
            ))}
          </div>
        )}

        {message && (
          <div className={`message ${messageType === 'success' ? 'success' : ''}`}>
            {message}
          </div>
        )}

        <button 
          onClick={resetSession}
          style={{ marginTop: '20px' }}
        >
          Start New Session
        </button>
      </div>
    );
  }

  return (
    <div className="container">
      <ThemeToggle />
      <h1>Unknown View</h1>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <SantinelApp />
  </React.StrictMode>,
)