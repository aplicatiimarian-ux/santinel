import React, { useState } from 'react';
import './app.css';

export default function SantinelApp() {
  const [message, setMessage] = useState('');
  const [contactName, setContactName] = useState('');
  const [companyName, setCompanyName] = useState('');

  const handleClick = async () => {
    console.log('Button clicked');
    console.log('API_BASE would be: http://localhost:8002/api/v1');
    
    if (!contactName || !companyName) {
      setMessage('Fill fields');
      return;
    }

    setMessage('🔄 Creating...');
    
    try {
      const url = 'http://localhost:8002/api/v1/sessions';
      console.log('Fetching:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contact_name: contactName,
          company_name: companyName,
          user_id: '2'
        })
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);
      
      if (response.ok) {
        setMessage(`✅ Session: ${data.session_id}`);
      } else {
        setMessage(`❌ ${data.detail}`);
      }
    } catch (error) {
      console.error('Full error:', error);
      setMessage(`❌ ${error.message}`);
    }
  };

  return (
    <div className="container">
      <h1>🧠 SANTINEL v3.0</h1>
      <p>Test</p>

      <input
        type="text"
        placeholder="Contact"
        value={contactName}
        onChange={(e) => setContactName(e.target.value)}
      />
      <input
        type="text"
        placeholder="Company"
        value={companyName}
        onChange={(e) => setCompanyName(e.target.value)}
      />
      <button onClick={handleClick}>Create Session</button>

      {message && <p>{message}</p>}
    </div>
  );
}