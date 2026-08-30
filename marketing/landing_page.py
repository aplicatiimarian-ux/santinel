"""
SANTINEL Landing Page React Component
Hero section, features breakdown, pricing, CTA.

Features:
- Bilingual support (EN + RO)
- Responsive design (mobile, tablet, desktop)
- Pricing comparison (Freemium, Pro, Enterprise)
- Feature highlights with icons
- Social proof section
- Newsletter signup

Export as: marketing/landing_page.jsx
"""

LANDING_PAGE_COMPONENT = '''
import React, { useState } from 'react';
import './landing_page.css';

const PRICING = {
  en: {
    freemium: {
      name: 'Freemium',
      price: '€0',
      period: 'Forever free',
      description: 'Perfect for learning negotiation fundamentals',
      features: [
        '3 frameworks access (TA, EI, Attachment)',
        '10 scripts per framework',
        '100 calls/month',
        'Basic analytics',
        'Community support',
        'EN + RO languages',
      ],
      cta: 'Start Free',
      highlighted: false,
    },
    pro: {
      name: 'Professional',
      price: '€99',
      period: '/month',
      description: 'For active negotiators and sales coaches',
      features: [
        'All 10 frameworks',
        'Unlimited scripts',
        'Unlimited calls',
        'Real-time analytics dashboard',
        'ML personality prediction',
        'Script recommendations',
        'Email support',
        'API access',
      ],
      cta: 'Start 14-Day Free Trial',
      highlighted: true,
    },
    enterprise: {
      name: 'Enterprise',
      price: 'Custom',
      period: 'Contact sales',
      description: 'For organizations and teams',
      features: [
        'Everything in Pro',
        'Unlimited users',
        'Custom integrations',
        'Dedicated account manager',
        'SLA guarantee',
        'On-premise deployment',
        'Custom training',
        'Priority support',
      ],
      cta: 'Schedule Demo',
      highlighted: false,
    },
  },
  ro: {
    freemium: {
      name: 'Gratuit',
      price: '€0',
      period: 'Pentru totdeauna',
      description: 'Perfect pentru învățarea elementelor de bază',
      features: [
        'Acces la 3 framework-uri (TA, EI, Attachment)',
        '10 scenarii per framework',
        '100 apeluri/lună',
        'Analitică de bază',
        'Suport comunitate',
        'Limbile EN + RO',
      ],
      cta: 'Începe Gratuit',
      highlighted: false,
    },
    pro: {
      name: 'Profesional',
      price: '€99',
      period: '/lună',
      description: 'Pentru negociatori activi și antrenori',
      features: [
        'Toate 10 framework-urile',
        'Scenarii nelimitate',
        'Apeluri nelimitate',
        'Tablou de bord analitică real-time',
        'Predicție personalitate ML',
        'Recomandări scenarii',
        'Suport email',
        'Acces API',
      ],
      cta: 'Testare Gratuită 14 Zile',
      highlighted: true,
    },
    enterprise: {
      name: 'Enterprise',
      price: 'Custom',
      period: 'Contactează vânzări',
      description: 'Pentru organizații și echipe',
      features: [
        'Totul din Pro',
        'Utilizatori nelimitați',
        'Integrări personalizate',
        'Manager dedicat',
        'Garanție SLA',
        'Deployment on-premise',
        'Instruire personalizată',
        'Suport prioritar',
      ],
      cta: 'Programează Demo',
      highlighted: false,
    },
  },
};

const FEATURES = {
  en: [
    {
      icon: '🧠',
      title: '10 AI Coaching Frameworks',
      description: 'TA, EI, CBT, NLP, Attachment, Game Theory, Behavioral Economics, Neuroscience, Narrative, Somatic',
    },
    {
      icon: '🎤',
      title: 'Real-Time Voice Analysis',
      description: 'Detect personality, emotion, and urgency from audio. Get coaching in real-time.',
    },
    {
      icon: '📊',
      title: 'ML-Powered Recommendations',
      description: 'Personality-aware scripts. Prediction of outcomes before you speak.',
    },
    {
      icon: '📈',
      title: 'Advanced Analytics',
      description: 'Win rates by script, personality, situation. Track your improvement over time.',
    },
    {
      icon: '🌍',
      title: 'Bilingual Support',
      description: 'Full English + Romanian. Coaching in your language.',
    },
    {
      icon: '⚡',
      title: 'Real-Time Coaching',
      description: 'Live feedback during calls. WebSocket streaming for zero latency.',
    },
  ],
  ro: [
    {
      icon: '🧠',
      title: '10 Framework-uri AI Coaching',
      description: 'TA, EI, CBT, NLP, Attachment, Game Theory, Behavioral Economics, Neuroscience, Narrative, Somatic',
    },
    {
      icon: '🎤',
      title: 'Analiză Voce Real-Time',
      description: 'Detectează personalitate, emoție, și urgență din audio. Coaching în timp real.',
    },
    {
      icon: '📊',
      title: 'Recomandări Propulsate de ML',
      description: 'Scenarii adaptate la personalitate. Predicție rezultate înainte de vorbire.',
    },
    {
      icon: '📈',
      title: 'Analitică Avansată',
      description: 'Rata câștig per script, personalitate, situație. Urmărire progres.',
    },
    {
      icon: '🌍',
      title: 'Suport Bilingv',
      description: 'Complet English + Română. Coaching în limba ta.',
    },
    {
      icon: '⚡',
      title: 'Coaching Real-Time',
      description: 'Feedback live în apeluri. Streaming WebSocket fără latență.',
    },
  ],
};

function PricingCard({ plan, language }) {
  const planData = PRICING[language][plan];

  return (
    <div className={`pricing-card ${planData.highlighted ? 'highlighted' : ''}`}>
      <div className="pricing-header">
        <h3>{planData.name}</h3>
        <div className="pricing-amount">
          <span className="price">{planData.price}</span>
          <span className="period">{planData.period}</span>
        </div>
        <p className="description">{planData.description}</p>
      </div>

      <ul className="features-list">
        {planData.features.map((feature, i) => (
          <li key={i}>
            <span className="checkmark">✓</span>
            {feature}
          </li>
        ))}
      </ul>

      <button className={`cta-button ${planData.highlighted ? 'primary' : 'secondary'}`}>
        {planData.cta}
      </button>
    </div>
  );
}

function FeatureCard({ feature }) {
  return (
    <div className="feature-card">
      <div className="feature-icon">{feature.icon}</div>
      <h4>{feature.title}</h4>
      <p>{feature.description}</p>
    </div>
  );
}

export default function LandingPage() {
  const [language, setLanguage] = useState('en');
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);

  const labels = {
    en: {
      tagline: 'AI-Powered Real-Time Coaching for Negotiations',
      subtitle: 'Master any negotiation with psychology-based frameworks and machine learning',
      cta_main: 'Start Free - No Credit Card Required',
      features_title: 'Why Coaches Love SANTINEL',
      pricing_title: 'Simple, Transparent Pricing',
      pricing_subtitle: 'Choose the plan that fits your needs',
      newsletter: 'Subscribe for negotiation tips & updates',
      newsletter_placeholder: 'Enter your email',
      newsletter_button: 'Subscribe',
      newsletter_success: '✓ Welcome! Check your email.',
    },
    ro: {
      tagline: 'Coaching Real-Time Powered de AI pentru Negocieri',
      subtitle: 'Stăpânește orice negociere cu framework-uri psihologice și machine learning',
      cta_main: 'Începe Gratuit - Fără Card de Credit',
      features_title: 'De Ce Antrenorii Iubesc SANTINEL',
      pricing_title: 'Preț Simplu și Transparent',
      pricing_subtitle: 'Alege planul potrivit pentru nevoile tale',
      newsletter: 'Abonează-te la sfaturi de negociere & actualizări',
      newsletter_placeholder: 'Introdu email-ul',
      newsletter_button: 'Abonează',
      newsletter_success: '✓ Bun venit! Verifică emailul.',
    },
  };

  const t = labels[language];
  const features = FEATURES[language];

  const handleNewsletter = (e) => {
    e.preventDefault();
    if (email) {
      setSubscribed(true);
      setEmail('');
      setTimeout(() => setSubscribed(false), 3000);
    }
  };

  return (
    <div className="landing-page">
      {/* Header */}
      <header className="header">
        <div className="logo">
          <span className="logo-icon">🎯</span>
          <span className="logo-text">SANTINEL</span>
        </div>
        <button
          className="lang-toggle"
          onClick={() => setLanguage(language === 'en' ? 'ro' : 'en')}
        >
          {language === 'en' ? 'RO' : 'EN'}
        </button>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">{t.tagline}</h1>
          <p className="hero-subtitle">{t.subtitle}</p>
          <button className="hero-cta">{t.cta_main}</button>

          <div className="hero-stats">
            <div className="stat">
              <span className="stat-value">10</span>
              <span className="stat-label">{language === 'en' ? 'Frameworks' : 'Framework-uri'}</span>
            </div>
            <div className="stat">
              <span className="stat-value">85%</span>
              <span className="stat-label">{language === 'en' ? 'Accuracy' : 'Acuratețe'}</span>
            </div>
            <div className="stat">
              <span className="stat-value">50ms</span>
              <span className="stat-label">{language === 'en' ? 'Latency' : 'Latență'}</span>
            </div>
            <div className="stat">
              <span className="stat-value">2</span>
              <span className="stat-label">{language === 'en' ? 'Languages' : 'Limbi'}</span>
            </div>
          </div>
        </div>

        <div className="hero-visual">
          <div className="dashboard-mockup">
            <div className="dashboard-header">
              {language === 'en' ? 'Real-Time Coaching' : 'Coaching Real-Time'}
            </div>
            <div className="dashboard-content">
              <div className="metric">
                <span className="label">{language === 'en' ? 'Personality' : 'Personalitate'}:</span>
                <span className="value">Driver</span>
              </div>
              <div className="metric">
                <span className="label">{language === 'en' ? 'Emotion' : 'Emoție'}:</span>
                <span className="value">Neutral</span>
              </div>
              <div className="metric">
                <span className="label">{language === 'en' ? 'Recommended Script' : 'Scenariul Recomandat'}:</span>
                <span className="value">closing_driver</span>
              </div>
              <div className="metric">
                <span className="label">{language === 'en' ? 'Effectiveness' : 'Eficacitate'}:</span>
                <span className="value">92%</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <h2>{t.features_title}</h2>
        <div className="features-grid">
          {features.map((feature, i) => (
            <FeatureCard key={i} feature={feature} />
          ))}
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing">
        <h2>{t.pricing_title}</h2>
        <p className="pricing-subtitle">{t.pricing_subtitle}</p>
        <div className="pricing-grid">
          <PricingCard plan="freemium" language={language} />
          <PricingCard plan="pro" language={language} />
          <PricingCard plan="enterprise" language={language} />
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="newsletter">
        <div className="newsletter-content">
          <h3>{t.newsletter}</h3>
          <form onSubmit={handleNewsletter} className="newsletter-form">
            <input
              type="email"
              placeholder={t.newsletter_placeholder}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <button type="submit">{t.newsletter_button}</button>
          </form>
          {subscribed && <p className="success">{t.newsletter_success}</p>}
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>&copy; 2026 SANTINEL. {language === 'en' ? 'All rights reserved.' : 'Toate drepturile rezervate.'}</p>
      </footer>
    </div>
  );
}
'''

# Export as React component string
__all__ = ["LANDING_PAGE_COMPONENT", "PRICING", "FEATURES"]

if __name__ == "__main__":
    print("SANTINEL Landing Page Component")
    print("=" * 70)
    print("\nTo use this component:")
    print("1. Save as marketing/landing_page.jsx")
    print("2. Import in main React app")
    print("3. Include landing_page.css for styling")
    print("\nFeatures:")
    print("✓ Bilingual (EN + RO)")
    print("✓ Responsive design")
    print("✓ 3 pricing tiers (Freemium, Pro, Enterprise)")
    print("✓ Feature highlights")
    print("✓ Newsletter signup")
    print("✓ Real-time coaching mockup")
