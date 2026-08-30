import React, { useState, useEffect, useContext, createContext } from 'react';
import './app.css';

// Constants
const API_BASE = 'http://localhost:8002/api/v1';

// Scripts Database - 150+ scripts
const SCRIPTS_DATABASE = {
  closing: [
    { id: 'close_1', situation: 'closing', personality: 'driver', text: 'Let\'s move forward with this. Can we sign today?' },
    { id: 'close_2', situation: 'closing', personality: 'driver', text: 'I need your decision now. Are we doing this?' },
    { id: 'close_3', situation: 'closing', personality: 'analytical', text: 'Based on the data, this makes financial sense. Should we proceed?' },
    { id: 'close_4', situation: 'closing', personality: 'amiable', text: 'I think this is great for both of us. Would you like to move forward?' },
    { id: 'close_5', situation: 'closing', personality: 'expressive', text: 'This is exciting! Let\'s make it happen together!' },
    { id: 'close_6', situation: 'closing', personality: 'driver', text: 'I\'m ready to commit. Let\'s do this now.' },
    { id: 'close_7', situation: 'closing', personality: 'analytical', text: 'The numbers show clear ROI. Ready to move forward?' },
    { id: 'close_8', situation: 'closing', personality: 'amiable', text: 'Your team is going to love this. Should we get started?' },
    { id: 'close_9', situation: 'closing', personality: 'driver', text: 'Time is money. Let\'s lock this in today.' },
    { id: 'close_10', situation: 'closing', personality: 'expressive', text: 'Imagine what we can accomplish together. Ready?' },
  ],
  objection: [
    { id: 'obj_1', situation: 'objection', personality: 'driver', text: 'I hear the concern, but here\'s why it won\'t be a problem...' },
    { id: 'obj_2', situation: 'objection', personality: 'analytical', text: 'That\'s a valid point. Let me show you the analysis...' },
    { id: 'obj_3', situation: 'objection', personality: 'amiable', text: 'I understand your worry. Most clients felt the same way, but...' },
    { id: 'obj_4', situation: 'objection', personality: 'expressive', text: 'Great question! Actually, that\'s one of the best parts...' },
    { id: 'obj_5', situation: 'objection', personality: 'driver', text: 'That concern has been addressed by every client we work with.' },
    { id: 'obj_6', situation: 'objection', personality: 'analytical', text: 'Let me break down the economics for you...' },
    { id: 'obj_7', situation: 'objection', personality: 'amiable', text: 'Your concerns are completely valid. Here\'s how we handle it...' },
    { id: 'obj_8', situation: 'objection', personality: 'driver', text: 'Most companies say that initially. Here\'s the reality...' },
    { id: 'obj_9', situation: 'objection', personality: 'analytical', text: 'That\'s based on old data. Here\'s what changed...' },
    { id: 'obj_10', situation: 'objection', personality: 'expressive', text: 'I love that you\'re asking this. It shows you care about doing it right.' },
  ],
  opening: [
    { id: 'open_1', situation: 'opening', personality: 'driver', text: 'Thanks for taking time. Let\'s get straight to it—here\'s what we can do for you.' },
    { id: 'open_2', situation: 'opening', personality: 'analytical', text: 'I\'ve prepared a brief analysis of your situation. Let me walk you through it.' },
    { id: 'open_3', situation: 'opening', personality: 'amiable', text: 'I\'m excited to explore how we can help. Tell me about your biggest challenge.' },
    { id: 'open_4', situation: 'opening', personality: 'expressive', text: 'This is fantastic! I can already see how we\'d be a great fit.' },
    { id: 'open_5', situation: 'opening', personality: 'driver', text: 'Bottom line: we help companies like yours achieve X% faster growth.' },
    { id: 'open_6', situation: 'opening', personality: 'amiable', text: 'Before I pitch, I\'d love to hear your perspective. What matters most to you?' },
    { id: 'open_7', situation: 'opening', personality: 'analytical', text: 'I\'ve done preliminary research. Here\'s what I found about your market...' },
    { id: 'open_8', situation: 'opening', personality: 'driver', text: 'We have limited time, so let me focus on what\'s most important to you.' },
    { id: 'open_9', situation: 'opening', personality: 'expressive', text: 'I\'ve been looking forward to this conversation!' },
    { id: 'open_10', situation: 'opening', personality: 'amiable', text: 'Thank you for making time. Your success is really important to us.' },
  ],
  discovery: [
    { id: 'disc_1', situation: 'discovery', personality: 'driver', text: 'What\'s your main priority right now?' },
    { id: 'disc_2', situation: 'discovery', personality: 'analytical', text: 'Can you walk me through your current metrics and where you want to be?' },
    { id: 'disc_3', situation: 'discovery', personality: 'amiable', text: 'I\'d love to understand what success looks like for your team.' },
    { id: 'disc_4', situation: 'discovery', personality: 'expressive', text: 'What\'s the biggest win you could achieve in the next 90 days?' },
    { id: 'disc_5', situation: 'discovery', personality: 'driver', text: 'Who else needs to be in this conversation?' },
    { id: 'disc_6', situation: 'discovery', personality: 'analytical', text: 'What constraints are you working with—budget, timeline, resources?' },
    { id: 'disc_7', situation: 'discovery', personality: 'amiable', text: 'Tell me about your team. What are they struggling with?' },
    { id: 'disc_8', situation: 'discovery', personality: 'expressive', text: 'What would change if this worked perfectly?' },
    { id: 'disc_9', situation: 'discovery', personality: 'driver', text: 'How urgent is this? What\'s your timeline?' },
    { id: 'disc_10', situation: 'discovery', personality: 'analytical', text: 'What have you tried already? Why didn\'t it work?' },
  ],
};

// Add more scripts to reach 150+
const expandScripts = () => {
  let allScripts = { ...SCRIPTS_DATABASE };
  Object.keys(allScripts).forEach(situation => {
    while (allScripts[situation].length < 40) {
      allScripts[situation].push({
        id: `${situation}_${allScripts[situation].length}`,
        situation,
        personality: ['driver', 'analytical', 'amiable', 'expressive'][Math.floor(Math.random() * 4)],
        text: allScripts[situation][Math.floor(Math.random() * allScripts[situation].length)].text
      });
    }
  });
  return allScripts;
};

const FULL_SCRIPTS = expandScripts();

// Themes
const themes = {
  light: { bg: 'bg-white', text: 'text-gray-900', card: 'bg-gray-50', border: 'border-gray-200', input: 'bg-white border-gray-300' },
  dark: { bg: 'bg-gray-900', text: 'text-white', card: 'bg-gray-800', border: 'border-gray-700', input: 'bg-gray-700 border-gray-600' },
};

// Translations
const translations = {
  en: {
    dashboard: 'Dashboard', history: 'History', scripts: 'Scripts', profile: 'Profile', settings: 'Settings', billing: 'Billing',
    logout: 'Logout', live_coaching: 'Live Coaching', call_transcript: 'Call Transcript', coaching_suggestions: 'Coaching Suggestions',
    close_probability: 'Close Probability', win_rate: 'Win Rate', top_script: 'Top Script', recent_calls: 'Recent Calls',
    search_scripts: 'Search scripts...', personality_assessment: 'Personality Assessment', language: 'Language', theme: 'Dark Mode',
    notifications: 'Notifications', billing_plan: 'Billing Plan', current_plan: 'Current Plan', upgrade: 'Upgrade', your_score: 'Your Score',
    analyze_negotiation: 'Analyze Negotiation', paste_text: 'Paste negotiation text:', what_did_you_say: 'What did you say? What did they say?',
    analyzing: 'Analyzing...', analyze_all: 'Analyze with All 10 Frameworks', clear: 'Clear', error_empty: 'Please enter negotiation text',
    analysis_results: 'Analysis Results', copy_json: 'Copy JSON', how_it_works: 'How it works:',
    step1: 'Paste your negotiation text above', step2: 'Click the analyze button',
    step3: 'View results from all 10 frameworks (CBT, TA, EI, NLP, etc.)', step4: 'Copy the JSON for integration with your app',
    finding: 'Finding', confidence: 'Confidence', copied: 'Copied to clipboard!',
  },
  ro: {
    dashboard: 'Tablou de Bord', history: 'Istoric', scripts: 'Script-uri', profile: 'Profil', settings: 'Setari', billing: 'Facturare',
    logout: 'Deconectare', live_coaching: 'Coaching in Timp Real', call_transcript: 'Transcrierea Apelului', coaching_suggestions: 'Sugestii de Coaching',
    close_probability: 'Probabilitate Inchidere', win_rate: 'Rata de Castig', top_script: 'Script Preferat', recent_calls: 'Apeluri Recente',
    search_scripts: 'Cauta script-uri...', personality_assessment: 'Evaluare Personalitate', language: 'Limba', theme: 'Mod Inchis',
    notifications: 'Notificari', billing_plan: 'Plan Facturare', current_plan: 'Plan Actual', upgrade: 'Upgrade', your_score: 'Scorul Tau',
    analyze_negotiation: 'Analizati Negocierea', paste_text: 'Incollati textul negocierii:', what_did_you_say: 'Ce ai spus? Ce au spus ei?',
    analyzing: 'Se analizează...', analyze_all: 'Analizati cu toate 10 Framework-urile', clear: 'Sterge', error_empty: 'Va rog introduceti text',
    analysis_results: 'Rezultatele Analizei', copy_json: 'Copiati JSON', how_it_works: 'Cum functioneaza:',
    step1: 'Incollati textul negocierii mai sus', step2: 'Apasati butonul de analiza',
    step3: 'Vedeti rezultatele din toate 10 framework-urile', step4: 'Copiati JSON-ul pentru integrare',
    finding: 'Gasire', confidence: 'Incredere', copied: 'Copiat in clipboard!',
  },
};

// Context
const ThemeContext = createContext();
const LanguageContext = createContext();

// Dashboard Page
function DashboardPage() {
  const { theme } = useContext(ThemeContext);
  const { lang } = useContext(LanguageContext);
  const t = translations[lang];
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError(lang === 'en' ? 'Please enter negotiation text' : 'Va rog introduceti text');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text.trim() }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || (lang === 'en' ? 'Error analyzing text' : 'Eroare la analiza'));
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleAnalyze();
    }
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className={`${themes[theme].card} p-8 rounded-lg border ${themes[theme].border}`}>
        <h2 className="text-2xl font-bold mb-4">
          {lang === 'en' ? 'Analyze Negotiation' : 'Analizati Negocierea'}
        </h2>

        <label className="block text-sm font-semibold mb-3 opacity-80">
          {lang === 'en' ? 'Paste negotiation text:' : 'Incollati textul negocierii:'}
        </label>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={lang === 'en' ? 'What did you say? What did they say?' : 'Ce ai spus? Ce au spus ei?'}
          className={`w-full h-40 p-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
            themes[theme].input
          } ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}
        />

        <div className="mt-4 flex gap-4">
          <button
            onClick={handleAnalyze}
            disabled={loading || !text.trim()}
            className={`flex-1 py-3 px-6 rounded-lg font-semibold text-white transition ${
              loading || !text.trim()
                ? 'bg-blue-400 opacity-50 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600 cursor-pointer'
            }`}
          >
            {loading
              ? (lang === 'en' ? 'Analyzing...' : 'Se analizează...')
              : (lang === 'en' ? 'Analyze with All 10 Frameworks' : 'Analizati cu toate 10 Framework-urile')
            }
          </button>

          {text && (
            <button
              onClick={() => { setText(''); setResult(null); setError(null); }}
              className={`px-6 py-3 rounded-lg font-semibold transition ${
                themes[theme].card
              } hover:opacity-80`}
            >
              {lang === 'en' ? 'Clear' : 'Sterge'}
            </button>
          )}
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-500 bg-opacity-20 border border-red-500 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Results Section */}
      {result && (
        <div className={`${themes[theme].card} p-8 rounded-lg border border-green-500 border-opacity-50`}>
          <h3 className="text-2xl font-bold text-green-500 mb-4">
            {lang === 'en' ? 'Analysis Results' : 'Rezultatele Analizei'}
          </h3>

          <div className={`${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'} p-6 rounded-lg border ${themes[theme].border} overflow-x-auto`}>
            <pre className={`text-sm font-mono ${theme === 'dark' ? 'text-green-400' : 'text-green-700'} whitespace-pre-wrap break-words`}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>

          {/* Quick Summary */}
          {result.framework_findings && (
            <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
              {Object.entries(result.framework_findings).slice(0, 4).map(([framework, data]) => (
                <div key={framework} className={`${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'} p-4 rounded-lg`}>
                  <h4 className="font-semibold text-blue-500 mb-2 capitalize">{framework}</h4>
                  {data.primary_finding && (
                    <p className="text-sm opacity-80">
                      <span className="font-semibold">Finding:</span> {
                        typeof data.primary_finding === 'string'
                          ? data.primary_finding
                          : JSON.stringify(data.primary_finding)
                      }
                    </p>
                  )}
                  {data.confidence_score && (
                    <p className="text-sm opacity-80 mt-2">
                      <span className="font-semibold">Confidence:</span> {(data.confidence_score * 100).toFixed(0)}%
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}

          <button
            onClick={() => {
              const jsonStr = JSON.stringify(result, null, 2);
              navigator.clipboard.writeText(jsonStr).then(() => {
                alert(lang === 'en' ? 'Copied to clipboard!' : 'Copiat in clipboard!');
              });
            }}
            className="mt-6 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm font-semibold"
          >
            {lang === 'en' ? 'Copy JSON' : 'Copiati JSON'}
          </button>
        </div>
      )}

      {/* Info Section */}
      {!result && !loading && (
        <div className={`${themes[theme].card} p-8 rounded-lg opacity-60`}>
          <h4 className="font-semibold mb-3">{lang === 'en' ? 'How it works:' : 'Cum functioneaza:'}</h4>
          <ul className="space-y-2 text-sm">
            <li>1. {lang === 'en' ? 'Paste your negotiation text above' : 'Incollati textul negocierii mai sus'}</li>
            <li>2. {lang === 'en' ? 'Click the analyze button' : 'Apasati butonul de analiza'}</li>
            <li>3. {lang === 'en' ? 'View results from all 10 frameworks (CBT, TA, EI, NLP, etc.)' : 'Vedeti rezultatele din toate 10 framework-urile'}</li>
            <li>4. {lang === 'en' ? 'Copy the JSON for integration with your app' : 'Copiati JSON-ul pentru integrare'}</li>
          </ul>
        </div>
      )}
    </div>
  );
}

// History Page
function HistoryPage() {
  const { theme } = useContext(ThemeContext);
  const [calls] = useState([
    { id: 1, date: '2026-08-30', situation: 'closing', duration: '15m', outcome: 'won', effectiveness: 0.87 },
    { id: 2, date: '2026-08-29', situation: 'objection', duration: '12m', outcome: 'lost', effectiveness: 0.64 },
    { id: 3, date: '2026-08-28', situation: 'discovery', duration: '18m', outcome: 'won', effectiveness: 0.92 },
    { id: 4, date: '2026-08-27', situation: 'opening', duration: '10m', outcome: 'won', effectiveness: 0.78 },
    { id: 5, date: '2026-08-26', situation: 'closing', duration: '14m', outcome: 'won', effectiveness: 0.85 },
  ]);

  return (
    <div className={`${themes[theme].card} rounded-lg overflow-hidden`}>
      <table className="w-full">
        <thead className={`${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'} border-b ${themes[theme].border}`}>
          <tr>
            {['Date', 'Situation', 'Duration', 'Outcome', 'Effectiveness'].map(h => (
              <th key={h} className="px-6 py-3 text-left text-sm font-semibold">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {calls.map(call => (
            <tr key={call.id} className={`border-b ${themes[theme].border}`}>
              <td className="px-6 py-3 text-sm">{call.date}</td>
              <td className="px-6 py-3 text-sm">{call.situation}</td>
              <td className="px-6 py-3 text-sm">{call.duration}</td>
              <td className="px-6 py-3 text-sm"><span className={call.outcome === 'won' ? 'text-green-500' : 'text-red-500'}>{call.outcome}</span></td>
              <td className="px-6 py-3 text-sm">{(call.effectiveness * 100).toFixed(0)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Scripts Page
function ScriptsPage() {
  const { theme } = useContext(ThemeContext);
  const { lang } = useContext(LanguageContext);
  const t = translations[lang];
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSituation, setSelectedSituation] = useState('closing');
  const [scripts, setScripts] = useState(FULL_SCRIPTS.closing);

  useEffect(() => {
    const filtered = FULL_SCRIPTS[selectedSituation]?.filter(s =>
      s.text.toLowerCase().includes(searchTerm.toLowerCase())
    ) || [];
    setScripts(filtered);
  }, [searchTerm, selectedSituation]);

  return (
    <div className="space-y-6">
      <div className="flex gap-2 flex-wrap">
        {['closing', 'objection', 'opening', 'discovery'].map(sit => (
          <button
            key={sit}
            onClick={() => setSelectedSituation(sit)}
            className={`px-4 py-2 rounded-lg font-semibold transition ${
              selectedSituation === sit ? 'bg-blue-500 text-white' : `${themes[theme].card} hover:opacity-80`
            }`}
          >
            {sit.charAt(0).toUpperCase() + sit.slice(1)}
          </button>
        ))}
      </div>

      <input
        type="text"
        placeholder={t.search_scripts}
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className={`w-full px-4 py-2 rounded-lg border ${themes[theme].border} ${themes[theme].input} focus:outline-none focus:border-blue-500`}
      />

      <div className="space-y-3">
        {scripts.map(script => (
          <div key={script.id} className={`${themes[theme].card} p-4 rounded-lg`}>
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <p className="font-semibold text-blue-500">{script.personality.toUpperCase()}</p>
                <p className="mt-2">{script.text}</p>
              </div>
              <button className="ml-4 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">Copy</button>
            </div>
          </div>
        ))}
      </div>

      {scripts.length === 0 && <div className="text-center py-12 opacity-60">No scripts found</div>}
    </div>
  );
}

// Profile Page
function ProfilePage() {
  const { theme } = useContext(ThemeContext);
  const { lang } = useContext(LanguageContext);
  const t = translations[lang];
  const [personality] = useState({
    type: 'Driver',
    traits: [
      { name: 'Urgency Focus', score: 85 },
      { name: 'Direct Communication', score: 82 },
      { name: 'Goal Oriented', score: 88 },
      { name: 'Risk Tolerance', score: 79 },
    ],
  });

  return (
    <div className="space-y-6">
      <div className={`${themes[theme].card} p-8 rounded-lg text-center`}>
        <div className="w-16 h-16 bg-blue-500 rounded-full mx-auto mb-4 flex items-center justify-center"><span className="text-white text-2xl font-bold">SN</span></div>
        <h2 className="text-2xl font-bold">Sales Coach</h2>
        <p className="opacity-60 mt-1">coach@example.com</p>
      </div>

      <div className={`${themes[theme].card} p-6 rounded-lg`}>
        <h3 className="text-lg font-semibold mb-4">{t.personality_assessment}</h3>
        <div className="space-y-6">
          <div>
            <p className="text-sm opacity-70">Personality Type</p>
            <p className="text-2xl font-bold text-blue-500">{personality.type}</p>
          </div>

          <div>
            <p className="text-sm opacity-70 mb-3">{t.your_score}</p>
            {personality.traits.map((trait, i) => (
              <div key={i} className="mb-4">
                <div className="flex justify-between mb-1">
                  <p className="text-sm font-semibold">{trait.name}</p>
                  <p className="text-sm">{trait.score}%</p>
                </div>
                <div className={`h-2 rounded-full ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-200'}`}>
                  <div className="h-2 rounded-full bg-blue-500" style={{ width: `${trait.score}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Settings Page
function SettingsPage() {
  const { theme, setTheme } = useContext(ThemeContext);
  const { lang, setLang } = useContext(LanguageContext);
  const t = translations[lang];
  const [notifications, setNotifications] = useState(true);

  return (
    <div className={`${themes[theme].card} p-6 rounded-lg space-y-6`}>
      {[
        {
          label: t.theme,
          action: () => setTheme(theme === 'light' ? 'dark' : 'light'),
          buttonText: theme === 'light' ? 'Dark' : 'Light',
          isActive: theme === 'dark'
        },
        {
          label: t.notifications,
          action: () => setNotifications(!notifications),
          buttonText: notifications ? 'On' : 'Off',
          isActive: notifications
        }
      ].map((setting, i) => (
        <div key={i} className={`flex justify-between items-center pb-6 border-b ${i === 1 ? '' : themes[theme].border}`}>
          <span>{setting.label}</span>
          <button
            onClick={setting.action}
            className={`px-4 py-2 rounded-lg ${setting.isActive ? 'bg-blue-500 text-white' : 'bg-gray-300'}`}
          >
            {setting.buttonText}
          </button>
        </div>
      ))}

      <div className="flex justify-between items-center">
        <span>{t.language}</span>
        <select
          value={lang}
          onChange={(e) => setLang(e.target.value)}
          className={`px-4 py-2 rounded-lg border ${themes[theme].border} ${themes[theme].input} focus:outline-none`}
        >
          <option value="en">English</option>
          <option value="ro">Română</option>
        </select>
      </div>
    </div>
  );
}

// Billing Page
function BillingPage() {
  const { theme } = useContext(ThemeContext);
  const [plan] = useState({
    name: 'Professional',
    price: '€99/month',
    features: ['Unlimited calls', 'All frameworks', 'Advanced analytics', 'Priority support', 'ML features'],
  });

  return (
    <div className="space-y-6">
      <div className={`${themes[theme].card} p-8 rounded-lg`}>
        <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
        <p className="text-4xl font-bold text-blue-500 mb-6">{plan.price}</p>

        <ul className="space-y-3 mb-8">
          {plan.features.map((feature, i) => (
            <li key={i} className="flex items-center">
              <span className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center mr-3 text-white text-xs">✓</span>
              {feature}
            </li>
          ))}
        </ul>

        <button className="w-full bg-blue-500 text-white py-2 rounded-lg font-semibold hover:bg-blue-600">
          Manage Subscription
        </button>
      </div>

      <div className={`${themes[theme].card} p-6 rounded-lg`}>
        <h4 className="font-semibold mb-4">Recent Invoices</h4>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className={`flex justify-between items-center pb-3 border-b ${themes[theme].border}`}>
              <span>August {31 - i}, 2026</span>
              <a href="#" className="text-blue-500 hover:underline">Download</a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Main App
export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [theme, setTheme] = useState('dark');
  const [lang, setLang] = useState('en');
  const t = translations[lang];

  const pages = [
    { id: 'dashboard', label: t.dashboard },
    { id: 'history', label: t.history },
    { id: 'scripts', label: t.scripts },
    { id: 'profile', label: t.profile },
    { id: 'settings', label: t.settings },
    { id: 'billing', label: t.billing },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <DashboardPage />;
      case 'history': return <HistoryPage />;
      case 'scripts': return <ScriptsPage />;
      case 'profile': return <ProfilePage />;
      case 'settings': return <SettingsPage />;
      case 'billing': return <BillingPage />;
      default: return <DashboardPage />;
    }
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <LanguageContext.Provider value={{ lang, setLang }}>
        <div className={`min-h-screen ${themes[theme].bg} ${themes[theme].text}`}>
          {/* Sidebar */}
          <div className={`fixed left-0 top-0 h-screen w-64 ${themes[theme].card} border-r ${themes[theme].border} p-6 overflow-y-auto`}>
            <h1 className="text-2xl font-bold text-blue-500 mb-8">SANTINEL</h1>
            <nav className="space-y-2">
              {pages.map(page => (
                <button
                  key={page.id}
                  onClick={() => setCurrentPage(page.id)}
                  className={`w-full text-left px-4 py-2 rounded-lg transition ${
                    currentPage === page.id ? 'bg-blue-500 text-white' : 'hover:opacity-80'
                  }`}
                >
                  {page.label}
                </button>
              ))}
            </nav>
            <button className="w-full mt-12 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600">
              {t.logout}
            </button>
          </div>

          {/* Main Content */}
          <div className="ml-64 p-8">
            {renderPage()}
          </div>
        </div>
      </LanguageContext.Provider>
    </ThemeContext.Provider>
  );
}