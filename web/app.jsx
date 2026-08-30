/**
 * SANTINEL Web Application - PHASE 15
 * Modern React + Tailwind CSS + shadcn/ui Design System
 * Production-ready negotiation coaching interface
 */

import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import './app.css';

// ============================================================
// MAIN APP COMPONENT
// ============================================================

export default function SantinelApp() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [darkMode, setDarkMode] = useState(localStorage.getItem('theme') === 'dark');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize theme
  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  // Load user
  useEffect(() => {
    setTimeout(() => {
      setUser({
        id: 'user-123',
        email: 'contact@example.com',
        name: 'John Doe',
        tier: 'pro',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=John',
        attachmentStyle: 'secure',
        successRate: 0.78,
        totalCalls: 247,
        winRate: 0.82
      });
      setLoading(false);
    }, 800);
  }, []);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'history', label: 'Call History', icon: '📞' },
    { id: 'scripts', label: 'Scripts', icon: '📝' },
    { id: 'profile', label: 'Profile', icon: '👤' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
    { id: 'billing', label: 'Billing', icon: '💳' },
  ];

  if (loading) return <LoadingScreen />;
  if (!user) return <LoginScreen setUser={setUser} />;

  return (
    <div className={`${darkMode ? 'dark' : ''} min-h-screen bg-gray-50 dark:bg-gray-900`}>
      <div className="flex h-screen">
        {/* SIDEBAR */}
        <Sidebar
          menuItems={menuItems}
          currentPage={currentPage}
          onPageChange={setCurrentPage}
          user={user}
          sidebarOpen={sidebarOpen}
        />

        {/* MAIN CONTENT */}
        <div className="flex-1 flex flex-col">
          {/* TOP NAV */}
          <TopNav
            currentPage={currentPage}
            menuItems={menuItems}
            user={user}
            sidebarOpen={sidebarOpen}
            onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}
            darkMode={darkMode}
            onThemeToggle={() => setDarkMode(!darkMode)}
            onPageChange={setCurrentPage}
          />

          {/* PAGE CONTENT */}
          <main className="flex-1 overflow-auto">
            <PageRouter currentPage={currentPage} user={user} />
          </main>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// SIDEBAR COMPONENT
// ============================================================

function Sidebar({ menuItems, currentPage, onPageChange, user, sidebarOpen }) {
  return (
    <div className={`${
      sidebarOpen ? 'w-64' : 'w-20'
    } hidden md:flex flex-col bg-gradient-to-b from-blue-600 to-blue-700 dark:from-gray-800 dark:to-gray-900 text-white transition-all duration-300 border-r border-blue-700 dark:border-gray-700`}>
      {/* Logo */}
      <div className="flex items-center justify-between p-6 border-b border-blue-500 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white dark:bg-blue-500 rounded-lg flex items-center justify-center font-bold text-blue-600 dark:text-white">
            S
          </div>
          {sidebarOpen && (
            <div>
              <h1 className="font-bold text-lg">SANTINEL</h1>
              <p className="text-xs text-blue-100">AI Coaching</p>
            </div>
          )}
        </div>
      </div>

      {/* Menu */}
      <nav className="flex-1 px-3 py-6 space-y-2 overflow-y-auto">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onPageChange(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              currentPage === item.id
                ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 font-semibold'
                : 'text-blue-100 dark:text-gray-400 hover:bg-blue-500 dark:hover:bg-gray-700'
            }`}
            title={item.label}
          >
            <span className="text-xl">{item.icon}</span>
            {sidebarOpen && <span className="text-sm font-medium">{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* User Profile */}
      {sidebarOpen && (
        <div className="p-4 border-t border-blue-500 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-4">
            <img src={user.avatar} alt={user.name} className="w-10 h-10 rounded-full" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate">{user.name}</p>
              <p className="text-xs text-blue-100 dark:text-gray-400">{user.tier}</p>
            </div>
          </div>
          <button className="w-full px-3 py-2 rounded-lg bg-blue-500 dark:bg-gray-700 hover:bg-blue-400 dark:hover:bg-gray-600 text-white text-sm font-medium transition-colors">
            Logout
          </button>
        </div>
      )}
    </div>
  );
}

// ============================================================
// TOP NAVIGATION
// ============================================================

function TopNav({ currentPage, menuItems, user, sidebarOpen, onSidebarToggle, darkMode, onThemeToggle, onPageChange }) {
  const pageLabel = menuItems.find(item => item.id === currentPage)?.label || 'Dashboard';

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onSidebarToggle}
            className="hidden md:flex items-center justify-center w-10 h-10 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"
          >
            {sidebarOpen ? '←' : '→'}
          </button>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{pageLabel}</h2>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={onThemeToggle}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"
            title="Toggle theme"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
          <button
            onClick={() => onPageChange('settings')}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"
          >
            ⚙️
          </button>
        </div>
      </div>
    </header>
  );
}

// ============================================================
// PAGE ROUTER
// ============================================================

function PageRouter({ currentPage, user }) {
  const pages = {
    dashboard: <DashboardPage user={user} />,
    history: <HistoryPage user={user} />,
    scripts: <ScriptsPage user={user} />,
    profile: <ProfilePage user={user} />,
    settings: <SettingsPage user={user} />,
    billing: <BillingPage user={user} />,
  };

  return pages[currentPage] || pages.dashboard;
}

// ============================================================
// PAGES
// ============================================================

function DashboardPage({ user }) {
  const [isLiveCall, setIsLiveCall] = useState(false);

  return (
    <div className="p-6 space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Stats */}
        <StatCard label="Win Rate" value="82%" icon="📊" trend="+5%" />
        <StatCard label="Total Calls" value="247" icon="📞" trend="+12" />
        <StatCard label="Success Rate" value="78%" icon="⭐" trend="+3%" />
        <StatCard label="Next Call" value="in 2h" icon="⏰" trend="scheduled" />
      </div>

      {/* Live Coaching Area */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-gray-700 dark:to-gray-800 p-6 text-white">
          <h3 className="text-xl font-bold mb-2">Live Coaching</h3>
          <p className="text-blue-100 dark:text-gray-400">Real-time negotiation support</p>
        </div>

        {isLiveCall ? <LiveCoachingInterface user={user} onEnd={() => setIsLiveCall(false)} /> : (
          <div className="p-8 text-center">
            <div className="text-6xl mb-4">📞</div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Active Call</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">Start a call to receive real-time coaching</p>
            <button
              onClick={() => setIsLiveCall(true)}
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all"
            >
              Start Live Call
            </button>
          </div>
        )}
      </div>

      {/* Recent Calls */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Recent Calls</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer transition-colors">
              <div className="flex-1">
                <p className="font-semibold text-gray-900 dark:text-white">Client Call #{i}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">2 hours ago</p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-green-600 dark:text-green-400">Won</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">5 tips used</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function HistoryPage({ user }) {
  return (
    <div className="p-6 space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Call Analytics</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Successful Calls</p>
            <p className="text-3xl font-bold text-green-600 dark:text-green-400">203</p>
          </div>
          <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900 dark:to-red-800 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Unsuccessful</p>
            <p className="text-3xl font-bold text-red-600 dark:text-red-400">44</p>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Avg Duration</p>
            <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">24m</p>
          </div>
        </div>

        <div className="space-y-3">
          <h4 className="font-semibold text-gray-900 dark:text-white">Recent Calls</h4>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex-1">
                <p className="font-semibold text-gray-900 dark:text-white">Call #{i}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">{i} day(s) ago</p>
              </div>
              <div className="text-right">
                <p className={`font-semibold ${i % 3 === 0 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
                  {i % 3 === 0 ? 'Lost' : 'Won'}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">CBT Framework</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ScriptsPage({ user }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');

  return (
    <div className="p-6 space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Script Library</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <input
            type="text"
            placeholder="Search scripts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
          <select
            value={selectedFilter}
            onChange={(e) => setSelectedFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="all">All Situations</option>
            <option value="price">Price Negotiation</option>
            <option value="terms">Terms & Conditions</option>
            <option value="objections">Handling Objections</option>
          </select>
          <div className="px-4 py-2 bg-blue-50 dark:bg-gray-700 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">150+ Scripts Available</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 p-6 rounded-lg hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white">Script {i}: Opening</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Price Negotiation</p>
                </div>
                <span className="text-yellow-500">{'⭐'.repeat(4)} 4.5</span>
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300 mb-4 line-clamp-2">
                "I appreciate your offer. Let me share why our solution is worth the investment..."
              </p>
              <div className="flex items-center justify-between">
                <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-1 rounded-full">CBT</span>
                <span className="text-xs text-gray-600 dark:text-gray-400">Used 24 times</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ProfilePage({ user }) {
  return (
    <div className="p-6 space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">Personality Profile</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="text-center">
            <img src={user.avatar} alt={user.name} className="w-24 h-24 rounded-full mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white">{user.name}</h4>
            <p className="text-gray-600 dark:text-gray-400">{user.email}</p>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 p-6 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Attachment Style</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">Secure</p>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900 dark:to-purple-800 p-6 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Ego State</p>
            <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">Adult</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Big Five Traits</h4>
            <div className="space-y-3">
              {[
                { trait: 'Openness', value: 85 },
                { trait: 'Conscientiousness', value: 92 },
                { trait: 'Extraversion', value: 72 },
                { trait: 'Agreeableness', value: 68 },
              ].map((item) => (
                <div key={item.trait}>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.trait}</span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">{item.value}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-blue-600 dark:bg-blue-400 h-2 rounded-full" style={{ width: `${item.value}%` }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Coaching Preferences</h4>
            <div className="space-y-2">
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" defaultChecked className="w-4 h-4 text-blue-600" />
                <span className="text-gray-700 dark:text-gray-300">Real-time coaching</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" defaultChecked className="w-4 h-4 text-blue-600" />
                <span className="text-gray-700 dark:text-gray-300">Post-call analysis</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" defaultChecked className="w-4 h-4 text-blue-600" />
                <span className="text-gray-700 dark:text-gray-300">Weekly insights</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 text-blue-600" />
                <span className="text-gray-700 dark:text-gray-300">AI-generated scripts</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SettingsPage({ user }) {
  return (
    <div className="p-6 space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">Preferences</h3>

        <div className="space-y-6">
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Notification Settings</h4>
            <div className="space-y-2">
              {['Email notifications', 'Push notifications', 'SMS alerts'].map((item) => (
                <label key={item} className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" defaultChecked className="w-4 h-4 text-blue-600" />
                  <span className="text-gray-700 dark:text-gray-300">{item}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Integrations</h4>
            <div className="space-y-3">
              {['Slack', 'Microsoft Teams', 'Google Calendar'].map((app) => (
                <div key={app} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <span className="text-gray-700 dark:text-gray-300">{app}</span>
                  <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors">
                    Connect
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function BillingPage({ user }) {
  return (
    <div className="p-6 space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">Subscription</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="border-2 border-blue-600 dark:border-blue-400 rounded-lg p-6">
            <div className="text-center">
              <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Professional</h4>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-4">$29<span className="text-lg">/mo</span></p>
              <button className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors mb-4">
                Current Plan
              </button>
              <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <li>✓ Unlimited calls</li>
                <li>✓ Real-time coaching</li>
                <li>✓ Script library</li>
                <li>✓ Analytics</li>
              </ul>
            </div>
          </div>

          <div className="border-2 border-gray-300 dark:border-gray-600 rounded-lg p-6 opacity-60">
            <div className="text-center">
              <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Enterprise</h4>
              <p className="text-3xl font-bold text-gray-600 dark:text-gray-400 mb-4">Custom</p>
              <button className="w-full px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-lg transition-colors mb-4">
                Contact Sales
              </button>
              <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                <li>✓ Everything in Pro</li>
                <li>✓ Custom integrations</li>
                <li>✓ Dedicated support</li>
                <li>✓ SLA guarantee</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
          <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Billing History</h4>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-white dark:bg-gray-600 rounded">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">Invoice #{1000 + i}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">August {i}, 2024</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900 dark:text-white">$29.00</p>
                  <button className="text-blue-600 dark:text-blue-400 text-sm hover:underline">Download</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// COMPONENTS
// ============================================================

function StatCard({ label, value, icon, trend }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-2">{label}</p>
          <h3 className="text-3xl font-bold text-gray-900 dark:text-white">{value}</h3>
          {trend && <p className="text-xs text-green-600 dark:text-green-400 mt-1">{trend}</p>}
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  );
}

function LiveCoachingInterface({ user, onEnd }) {
  const [transcript, setTranscript] = useState([
    { speaker: 'You', text: 'So, regarding the pricing...' },
    { speaker: 'Client', text: 'We have limited budget' },
  ]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 p-6">
      {/* Call Video/Audio */}
      <div className="lg:col-span-2">
        <div className="bg-black rounded-lg flex items-center justify-center h-64 lg:h-96 mb-4">
          <div className="text-center text-white">
            <div className="text-6xl mb-4">📞</div>
            <p className="text-lg font-semibold">In Call - 5:24</p>
            <p className="text-gray-400 text-sm">Client: John Smith</p>
          </div>
        </div>

        {/* Transcript */}
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 h-40 overflow-y-auto space-y-3">
          {transcript.map((msg, idx) => (
            <div key={idx} className={`p-3 rounded-lg ${msg.speaker === 'You' ? 'bg-blue-100 dark:bg-blue-900 text-gray-900 dark:text-white ml-4' : 'bg-gray-200 dark:bg-gray-600 text-gray-900 dark:text-white mr-4'}`}>
              <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">{msg.speaker}</p>
              <p className="text-sm">{msg.text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Coaching Suggestions */}
      <div>
        <div className="bg-gradient-to-b from-yellow-50 to-orange-50 dark:from-yellow-900 dark:to-orange-900 rounded-lg p-4 h-full">
          <h4 className="font-bold text-gray-900 dark:text-white mb-3">💡 Real-Time Tips</h4>
          <div className="space-y-3">
            <div className="bg-white dark:bg-gray-800 p-3 rounded border-l-4 border-blue-600">
              <p className="text-xs font-semibold text-gray-900 dark:text-white">CBT: Challenge Assumptions</p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Ask about their budget constraints</p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-3 rounded border-l-4 border-green-600">
              <p className="text-xs font-semibold text-gray-900 dark:text-white">NLP: Reframing</p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Focus on ROI, not cost</p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-3 rounded border-l-4 border-purple-600">
              <p className="text-xs font-semibold text-gray-900 dark:text-white">TA: Adult Ego State</p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Stay factual and logical</p>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-gray-300 dark:border-gray-700">
            <div className="bg-white dark:bg-gray-800 p-3 rounded mb-3">
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">Win Probability</p>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                <div className="bg-gradient-to-r from-green-500 to-blue-500 h-3 rounded-full" style={{ width: '72%' }}></div>
              </div>
              <p className="text-sm font-bold text-gray-900 dark:text-white mt-2">72% Win Chance</p>
            </div>

            <button
              onClick={onEnd}
              className="w-full px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold rounded-lg transition-colors"
            >
              End Call
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// LOGIN SCREEN
// ============================================================

function LoginScreen({ setUser }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    setUser({
      id: 'user-123',
      email,
      name: 'User',
      tier: 'pro',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=User'
    });
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 dark:from-gray-900 dark:to-gray-800">
      <div className="w-full max-w-md p-8 bg-white dark:bg-gray-800 rounded-2xl shadow-xl">
        <div className="flex justify-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
            <span className="text-3xl font-bold text-white">S</span>
          </div>
        </div>

        <h1 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-2">SANTINEL</h1>
        <p className="text-center text-gray-600 dark:text-gray-400 mb-8">AI-Powered Negotiation Coaching</p>

        <form onSubmit={handleLogin} className="space-y-4">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Email"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Password"
            required
          />
          <button
            type="submit"
            className="w-full py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all"
          >
            Sign In
          </button>
        </form>

        <p className="text-center text-gray-600 dark:text-gray-400 text-sm mt-6">
          Demo: Any email and password
        </p>
      </div>
    </div>
  );
}

// ============================================================
// LOADING SCREEN
// ============================================================

function LoadingScreen() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 dark:from-gray-900 dark:to-gray-800">
      <div className="text-center">
        <div className="w-16 h-16 bg-blue-600 dark:bg-blue-500 rounded-lg flex items-center justify-center mx-auto mb-4 animate-pulse">
          <span className="text-2xl font-bold text-white">S</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">SANTINEL</h1>
        <p className="text-gray-600 dark:text-gray-400">Loading...</p>
      </div>
    </div>
  );
}
      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          onClick={handleReject}
          style={{
            padding: '10px 20px',
            backgroundColor: 'transparent',
            border: '1px solid #475569',
            color: '#cbd5e1',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: '600',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = 'rgba(71, 85, 105, 0.2)';
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = 'transparent';
          }}
        >
          Reject
        </button>
        <button
          onClick={handleAccept}
          style={{
            padding: '10px 20px',
            background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
            border: 'none',
            color: 'white',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: '600',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            e.target.style.boxShadow = '0 4px 12px rgba(99, 102, 241, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.target.style.boxShadow = 'none';
          }}
        >
          Accept All
        </button>
      </div>
    </div>
  );
}

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
                <p><strong>Rating:</strong> {pattern.rating}/5</p>
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

function AppWithConsent() {
  return (
    <>
      <SantinelApp />
      <CookieConsent />
    </>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppWithConsent />
  </React.StrictMode>,
)