/**
 * SANTINEL Analytics Dashboard
 * Real-time coaching effectiveness tracking and visualization
 *
 * Features:
 * - Script performance heatmap (personality × situation)
 * - Win/loss funnel analysis
 * - Framework effectiveness by personality
 * - Signal accuracy metrics
 * - Personality strengths/weaknesses breakdown
 * - Key metrics summary (KPIs)
 */

import React, { useState, useEffect } from 'react';
import './dashboard.css';

// Mock analytics data (in production: fetch from /api/v2/analytics)
const mockAnalyticsData = {
  summary: {
    total_calls: 42,
    win_rate: 0.76,
    loss_rate: 0.12,
    stalled_rate: 0.12,
    average_effectiveness: 0.84,
    top_script: "script_closing_driver",
    top_personality: "driver"
  },
  script_heatmap: {
    driver: { cold_call: 0.68, discovery: 0.72, objection: 0.65, closing: 0.94, follow_up: 0.70 },
    expressive: { cold_call: 0.85, discovery: 0.78, objection: 0.71, closing: 0.89, follow_up: 0.75 },
    amiable: { cold_call: 0.55, discovery: 0.82, objection: 0.87, closing: 0.61, follow_up: 0.79 },
    analytical: { cold_call: 0.42, discovery: 0.88, objection: 0.51, closing: 0.48, follow_up: 0.60 }
  },
  top_scripts: [
    { script_id: "script_closing_driver", win_rate: 0.94, total_uses: 17, trending: "up" },
    { script_id: "script_discovery_amiable", win_rate: 0.87, total_uses: 15, trending: "up" },
    { script_id: "script_cold_call_expressive", win_rate: 0.85, total_uses: 13, trending: "neutral" },
    { script_id: "script_objection_amiable", win_rate: 0.83, total_uses: 12, trending: "up" },
  ],
  framework_effectiveness: [
    { framework: "attachment", close_rate: 0.82, closes: 18, avg_confidence: 0.87 },
    { framework: "ei", close_rate: 0.79, closes: 16, avg_confidence: 0.85 },
    { framework: "neuroscience", close_rate: 0.76, closes: 14, avg_confidence: 0.81 },
    { framework: "ta", close_rate: 0.74, closes: 12, avg_confidence: 0.78 },
  ],
  signal_accuracy: [
    { signal: "verbal_agreement", f1_score: 0.91, precision: 0.92, recall: 0.89 },
    { signal: "vocal_high_energy", f1_score: 0.87, precision: 0.88, recall: 0.85 },
    { signal: "verbal_urgency", f1_score: 0.79, precision: 0.81, recall: 0.77 },
    { signal: "vocal_warm_tone", f1_score: 0.75, precision: 0.76, recall: 0.73 },
  ],
  personality_analysis: {
    driver: { avg_win_rate: 0.82, best_situation: "closing", patterns: ["driver_quick_close"] },
    expressive: { avg_win_rate: 0.81, best_situation: "cold_call", patterns: ["expressive_high_energy"] },
    amiable: { avg_win_rate: 0.79, best_situation: "objection", patterns: ["amiable_long_engagement"] },
    analytical: { avg_win_rate: 0.58, best_situation: "discovery", patterns: ["analytical_needs_proof"] }
  }
};

// KPI Card Component
function KPICard({ label, value, unit = '%', trend = null }) {
  const displayValue = typeof value === 'number' && unit === '%' ? (value * 100).toFixed(1) : value;

  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{displayValue}{unit}</div>
      {trend && (
        <div className={`kpi-trend ${trend > 0 ? 'up' : trend < 0 ? 'down' : 'neutral'}`}>
          {trend > 0 ? '↑' : trend < 0 ? '↓' : '→'} {Math.abs(trend).toFixed(1)}%
        </div>
      )}
    </div>
  );
}

// Script Heatmap Component
function ScriptHeatmap({ data }) {
  const situations = ['cold_call', 'discovery', 'objection', 'closing', 'follow_up'];
  const personalities = ['driver', 'expressive', 'amiable', 'analytical'];

  const getColorClass = (value) => {
    if (value >= 0.8) return 'heat-hot';
    if (value >= 0.6) return 'heat-warm';
    if (value >= 0.4) return 'heat-cool';
    return 'heat-cold';
  };

  return (
    <div className="heatmap">
      <table className="heatmap-table">
        <thead>
          <tr>
            <th>Personality</th>
            {situations.map(s => (
              <th key={s} className="situation-header">
                {s.replace('_', ' ').toUpperCase()}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {personalities.map(p => (
            <tr key={p}>
              <td className="personality-label">{p.toUpperCase()}</td>
              {situations.map(s => (
                <td key={`${p}-${s}`} className={`heatmap-cell ${getColorClass(data[p][s])}`}>
                  {(data[p][s] * 100).toFixed(0)}%
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="heatmap-legend">
        <span><span className="heat-hot"></span> 80%+ (Hot)</span>
        <span><span className="heat-warm"></span> 60-79% (Warm)</span>
        <span><span className="heat-cool"></span> 40-59% (Cool)</span>
        <span><span className="heat-cold"></span> &lt;40% (Cold)</span>
      </div>
    </div>
  );
}

// Win/Loss Funnel Component
function WinLossFunnel({ summary }) {
  const total = summary.total_calls;
  const won = summary.win_rate * total;
  const lost = summary.loss_rate * total;
  const stalled = summary.stalled_rate * total;

  const max = Math.max(won, lost, stalled);

  return (
    <div className="funnel">
      <div className="funnel-stage">
        <div className="funnel-bar" style={{ width: `${(won / max) * 100}%`, backgroundColor: '#10b981' }}>
          <span>{won.toFixed(0)} Won</span>
        </div>
        <span className="funnel-label">{(summary.win_rate * 100).toFixed(1)}% Win Rate</span>
      </div>
      <div className="funnel-stage">
        <div className="funnel-bar" style={{ width: `${(lost / max) * 100}%`, backgroundColor: '#ef4444' }}>
          <span>{lost.toFixed(0)} Lost</span>
        </div>
        <span className="funnel-label">{(summary.loss_rate * 100).toFixed(1)}% Loss Rate</span>
      </div>
      <div className="funnel-stage">
        <div className="funnel-bar" style={{ width: `${(stalled / max) * 100}%`, backgroundColor: '#f59e0b' }}>
          <span>{stalled.toFixed(0)} Stalled</span>
        </div>
        <span className="funnel-label">{(summary.stalled_rate * 100).toFixed(1)}% Stall Rate</span>
      </div>
    </div>
  );
}

// Top Scripts Table Component
function TopScriptsTable({ scripts }) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Script</th>
          <th>Win Rate</th>
          <th>Uses</th>
          <th>Trend</th>
        </tr>
      </thead>
      <tbody>
        {scripts.map(script => (
          <tr key={script.script_id}>
            <td className="script-name">{script.script_id.replace('script_', '').replace(/_/g, ' ').toUpperCase()}</td>
            <td>
              <span className={`badge badge-${script.win_rate >= 0.8 ? 'success' : 'warning'}`}>
                {(script.win_rate * 100).toFixed(1)}%
              </span>
            </td>
            <td>{script.total_uses}</td>
            <td>
              <span className={`trend ${script.trending}`}>
                {script.trending === 'up' ? '↑' : script.trending === 'down' ? '↓' : '→'}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// Framework Effectiveness Component
function FrameworkEffectiveness({ data }) {
  return (
    <div className="framework-bars">
      {data.map(fw => (
        <div key={fw.framework} className="framework-bar">
          <div className="framework-name">{fw.framework.toUpperCase()}</div>
          <div className="bar-container">
            <div
              className="bar-fill"
              style={{ width: `${fw.close_rate * 100}%` }}
            >
              <span className="bar-value">{(fw.close_rate * 100).toFixed(1)}%</span>
            </div>
          </div>
          <div className="framework-meta">
            {fw.closes} closes · {fw.avg_confidence.toFixed(2)} conf
          </div>
        </div>
      ))}
    </div>
  );
}

// Personality Breakdown Component
function PersonalityBreakdown({ analysis }) {
  return (
    <div className="personality-grid">
      {Object.entries(analysis).map(([personality, data]) => (
        <div key={personality} className="personality-card">
          <h4>{personality.toUpperCase()}</h4>
          <div className="personality-stat">
            <span className="stat-label">Avg Win Rate:</span>
            <span className="stat-value">{(data.avg_win_rate * 100).toFixed(1)}%</span>
          </div>
          <div className="personality-stat">
            <span className="stat-label">Best Situation:</span>
            <span className="stat-value">{data.best_situation.replace(/_/g, ' ')}</span>
          </div>
          <div className="personality-patterns">
            <span className="label">Patterns:</span>
            {data.patterns.map(p => (
              <span key={p} className="pattern-tag">{p.replace(/_/g, ' ')}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// Signal Accuracy Component
function SignalAccuracy({ signals }) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Signal</th>
          <th>F1 Score</th>
          <th>Precision</th>
          <th>Recall</th>
        </tr>
      </thead>
      <tbody>
        {signals.map(signal => (
          <tr key={signal.signal}>
            <td>{signal.signal.replace(/_/g, ' ').toUpperCase()}</td>
            <td>
              <span className={`badge badge-${signal.f1_score >= 0.8 ? 'success' : 'info'}`}>
                {(signal.f1_score * 100).toFixed(1)}%
              </span>
            </td>
            <td>{(signal.precision * 100).toFixed(1)}%</td>
            <td>{(signal.recall * 100).toFixed(1)}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// Main Dashboard Component
export default function AnalyticsDashboard() {
  const [data, setData] = useState(mockAnalyticsData);
  const [activeTab, setActiveTab] = useState('overview');
  const [language, setLanguage] = useState('en');

  useEffect(() => {
    // In production: fetch from API
    // const fetchAnalytics = async () => {
    //   const response = await fetch('/api/v2/analytics');
    //   setData(await response.json());
    // };
    // fetchAnalytics();
  }, []);

  const labels = {
    en: {
      title: 'SANTINEL Analytics Dashboard',
      overview: 'Overview',
      performance: 'Performance',
      patterns: 'Patterns',
      signals: 'Signals',
      summary: 'Summary',
      topScripts: 'Top Performing Scripts',
      scriptHeatmap: 'Script Performance Heatmap',
      winLossFunnel: 'Win/Loss Funnel',
      frameworkEff: 'Framework Effectiveness',
      personality: 'Personality Breakdown',
      signalAccuracy: 'Signal Accuracy',
      totalCalls: 'Total Calls',
      winRate: 'Win Rate',
      lossRate: 'Loss Rate',
      avgEffectiveness: 'Avg Effectiveness'
    },
    ro: {
      title: 'Tabloul de Bord Analitică SANTINEL',
      overview: 'Prezentare Generală',
      performance: 'Performanță',
      patterns: 'Modele',
      signals: 'Semnale',
      summary: 'Rezumat',
      topScripts: 'Scenarii cu Performanță Ridicată',
      scriptHeatmap: 'Hartă Termostatică Performanță',
      winLossFunnel: 'Pâlnie Câștig/Pierdere',
      frameworkEff: 'Eficacitate Framework',
      personality: 'Clasificare Personalitate',
      signalAccuracy: 'Acuratețe Semnal',
      totalCalls: 'Total Apeluri',
      winRate: 'Rata Câștig',
      lossRate: 'Rata Pierdere',
      avgEffectiveness: 'Eficacitate Medie'
    }
  };

  const t = labels[language];

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>{t.title}</h1>
        <button className="lang-toggle" onClick={() => setLanguage(language === 'en' ? 'ro' : 'en')}>
          {language === 'en' ? 'EN' : 'RO'}
        </button>
      </header>

      {/* KPI Summary */}
      <section className="kpi-section">
        <div className="kpi-grid">
          <KPICard label={t.totalCalls} value={data.summary.total_calls} unit="" />
          <KPICard label={t.winRate} value={data.summary.win_rate} />
          <KPICard label={t.lossRate} value={data.summary.loss_rate} />
          <KPICard label={t.avgEffectiveness} value={data.summary.average_effectiveness} unit="" />
        </div>
      </section>

      {/* Tab Navigation */}
      <nav className="tab-navigation">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          {t.overview}
        </button>
        <button
          className={`tab-btn ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          {t.performance}
        </button>
        <button
          className={`tab-btn ${activeTab === 'patterns' ? 'active' : ''}`}
          onClick={() => setActiveTab('patterns')}
        >
          {t.patterns}
        </button>
        <button
          className={`tab-btn ${activeTab === 'signals' ? 'active' : ''}`}
          onClick={() => setActiveTab('signals')}
        >
          {t.signals}
        </button>
      </nav>

      {/* Tab Content */}
      <main className="dashboard-content">
        {activeTab === 'overview' && (
          <div className="tab-content">
            <section className="card">
              <h2>{t.scriptHeatmap}</h2>
              <ScriptHeatmap data={data.script_heatmap} />
            </section>

            <section className="card">
              <h2>{t.winLossFunnel}</h2>
              <WinLossFunnel summary={data.summary} />
            </section>
          </div>
        )}

        {activeTab === 'performance' && (
          <div className="tab-content">
            <section className="card">
              <h2>{t.topScripts}</h2>
              <TopScriptsTable scripts={data.top_scripts} />
            </section>

            <section className="card">
              <h2>{t.frameworkEff}</h2>
              <FrameworkEffectiveness data={data.framework_effectiveness} />
            </section>
          </div>
        )}

        {activeTab === 'patterns' && (
          <div className="tab-content">
            <section className="card">
              <h2>{t.personality}</h2>
              <PersonalityBreakdown analysis={data.personality_analysis} />
            </section>
          </div>
        )}

        {activeTab === 'signals' && (
          <div className="tab-content">
            <section className="card">
              <h2>{t.signalAccuracy}</h2>
              <SignalAccuracy signals={data.signal_accuracy} />
            </section>
          </div>
        )}
      </main>
    </div>
  );
}
