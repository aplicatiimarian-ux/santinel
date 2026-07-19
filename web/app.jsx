import React, { useState } from 'react';
import './app.css';

export default function SantinelApp() {
  const [currentView, setCurrentView] = useState('home');
  const [userId, setUserId] = useState('1');
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
  const [patterns, setPatterns] = useState([]);

  const API_BASE = 'http://localhost:8002/api/v1';

  // ===== SESSION MANAGEMENT =====

  const handleCreateSession = async () => {
    if (!contactName || !companyName) {
      setMessage('❌ Please fill in all fields');
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
        setMessage(`✅ ${data.message}`);
        setCurrentView('coaching');
      } else {
        setMessage(`❌ Error: ${data.detail}`);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ===== COACHING =====

  const handleGetCoaching = async () => {
    if (!situation) {
      setMessage('❌ Please describe your situation');
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
        setMessage('✅ Coaching delivered');
        setCurrentView('feedback');
      } else {
        setMessage(`❌ Error: ${data.detail}`);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ===== FEEDBACK =====

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
        setMessage(`✅ ${data.message}`);
        setCurrentView('export');
      } else {
        setMessage(`❌ Error: ${data.detail}`);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ===== EXPORT PATTERNS =====

  const handleExportPatterns = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/finetuning/export`);
      const data = await response.json();
      if (response.ok) {
        setPatterns(data.data.training_examples);
        setMessage(`✅ Exported ${data.patterns} patterns`);
      } else {
        setMessage(`❌ Error: ${data.detail}`);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ===== RENDER: HOME VIEW =====

  if (currentView === 'home') {
    return (
      <div className="container">
        <h1>🧠 SANTINEL v3.0</h1>
        <p>AI-Powered Psychological Negotiation Coach</p>

        <div className="form-section">
          <h2>Create Session</h2>
          <input
            type="text"
            placeholder="Contact Name"
            value={contactName}
            onChange={(e) => setContactName(e.target.value)}
          />
          <input
            type="text"
            placeholder="Company Name"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
          />
          <button onClick={handleCreateSession} disabled={loading}>
            {loading ? 'Creating...' : 'Create Session'}
          </button>
        </div>

        {message && <p className="message">{message}</p>}
        {sessionId && <p className="success">Session ID: {sessionId}</p>}
      </div>
    );
  }

  // ===== RENDER: COACHING VIEW =====

  if (currentView === 'coaching') {
    return (
      <div className="container">
        <h1>🎯 Negotiation Coaching</h1>
        <p>Session: {sessionId}</p>

        <div className="form-section">
          <h2>Describe Your Situation</h2>
          <textarea
            placeholder="What's the negotiation scenario?"
            value={situation}
            onChange={(e) => setSituation(e.target.value)}
            rows={5}
          />
          <button onClick={handleGetCoaching} disabled={loading}>
            {loading ? 'Generating...' : 'Get Coaching'}
          </button>
        </div>

        {coaching && (
          <div className="coaching-section">
            <h2>💡 Coaching Response</h2>
            <div className="coaching-text">{coaching}</div>
          </div>
        )}

        {message && <p className="message">{message}</p>}

        <button onClick={() => setCurrentView('home')}>Back</button>
      </div>
    );
  }

  // ===== RENDER: FEEDBACK VIEW =====

  if (currentView === 'feedback') {
    return (
      <div className="container">
        <h1>⭐ Rate Coaching</h1>
        <p>Session: {sessionId}</p>

        <div className="form-section">
          <h2>How helpful was the coaching?</h2>
          
          <label>Rating (1-5):</label>
          <select value={rating} onChange={(e) => setRating(e.target.value)}>
            <option value="1">1 - Not helpful</option>
            <option value="2">2 - Somewhat helpful</option>
            <option value="3">3 - Neutral</option>
            <option value="4">4 - Very helpful</option>
            <option value="5">5 - Extremely helpful</option>
          </select>

          <label>Quality Score (0-1):</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={qualityScore}
            onChange={(e) => setQualityScore(e.target.value)}
          />

          <label>Comments:</label>
          <textarea
            placeholder="What worked? What could improve?"
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            rows={3}
          />

          <button onClick={handleSubmitFeedback} disabled={loading}>
            {loading ? 'Submitting...' : 'Submit Feedback'}
          </button>
        </div>

        {message && <p className="message">{message}</p>}

        <button onClick={() => setCurrentView('coaching')}>Back</button>
      </div>
    );
  }

  // ===== RENDER: EXPORT VIEW =====

  if (currentView === 'export') {
    return (
      <div className="container">
        <h1>📊 Export Patterns</h1>

        <div className="form-section">
          <h2>High-Quality Coaching Patterns</h2>
          <p>Ready for fine-tuning</p>
          <button onClick={handleExportPatterns} disabled={loading}>
            {loading ? 'Exporting...' : 'Export Patterns'}
          </button>
        </div>

        {patterns.length > 0 && (
          <div className="patterns-section">
            <h2>📈 Patterns Found: {patterns.length}</h2>
            {patterns.map((pattern, idx) => (
              <div key={idx} className="pattern-card">
                <h4>Pattern {pattern.pattern_id}</h4>
                <p><strong>Rating:</strong> {pattern.rating}/5</p>
                <p><strong>Quality:</strong> {pattern.quality_score.toFixed(2)}</p>
                <p><strong>Text:</strong> {pattern.coaching_text.substring(0, 100)}...</p>
                <p><strong>Frameworks:</strong> {pattern.frameworks_used.join(', ')}</p>
              </div>
            ))}
          </div>
        )}

        {message && <p className="message">{message}</p>}

        <button onClick={() => setCurrentView('home')}>New Session</button>
      </div>
    );
  }

  return <div className="container">Unknown view</div>;
}