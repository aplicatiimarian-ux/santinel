/**
 * SANTINEL Reusable UI Components
 * Tailwind CSS + shadcn/ui compatible components
 */

// ============================================================
// COACHING CARD
// ============================================================

export function CoachingCard({ title, content, framework, confidence, onClick }) {
  const frameworkColors = {
    cbt: 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
    nlp: 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
    ta: 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200',
    ego: 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200',
  };

  return (
    <div
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-all cursor-pointer p-4 border-l-4 border-blue-600 dark:border-blue-400"
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-gray-900 dark:text-white text-sm">{title}</h3>
        <span className={`text-xs font-medium px-2 py-1 rounded-full ${frameworkColors[framework] || frameworkColors.cbt}`}>
          {framework.toUpperCase()}
        </span>
      </div>
      <p className="text-sm text-gray-700 dark:text-gray-300 mb-3 line-clamp-2">{content}</p>
      <div className="flex items-center justify-between">
        <div className="text-xs text-gray-600 dark:text-gray-400">Confidence: {(confidence * 100).toFixed(0)}%</div>
        <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
          <div
            className="bg-blue-600 dark:bg-blue-400 h-1.5 rounded-full"
            style={{ width: `${confidence * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// SCRIPT CARD
// ============================================================

export function ScriptCard({ number, title, category, text, rating, timesUsed, onSelect }) {
  return (
    <div
      onClick={onSelect}
      className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 p-6 rounded-lg hover:shadow-lg transition-all cursor-pointer border border-gray-200 dark:border-gray-600"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-semibold text-gray-900 dark:text-white">Script {number}: {title}</h4>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{category}</p>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-yellow-500">{'⭐'.repeat(Math.floor(rating))}</span>
          <span className="text-xs text-gray-600 dark:text-gray-400">{rating.toFixed(1)}</span>
        </div>
      </div>
      <p className="text-sm text-gray-700 dark:text-gray-300 mb-4 line-clamp-3">"{text}"</p>
      <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-600">
        <span className="text-xs text-gray-600 dark:text-gray-400">Used {timesUsed} times</span>
        <button className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded transition-colors">
          Use Script
        </button>
      </div>
    </div>
  );
}

// ============================================================
// TRANSCRIPT VIEWER
// ============================================================

export function TranscriptViewer({ messages, isLive = false }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900 dark:text-white">Conversation</h3>
        {isLive && (
          <span className="text-xs bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 px-3 py-1 rounded-full flex items-center gap-1">
            <span className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></span>
            Live
          </span>
        )}
      </div>

      <div className="space-y-3 h-64 overflow-y-auto">
        {messages.map((msg, idx) => (
          <div key={idx} className={`p-3 rounded-lg ${
            msg.speaker === 'You'
              ? 'bg-blue-100 dark:bg-blue-900 text-gray-900 dark:text-white ml-4'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white mr-4'
          }`}>
            <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              {msg.speaker}
            </p>
            <p className="text-sm">{msg.text}</p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{msg.time}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================
// ANALYTICS CHART
// ============================================================

export function AnalyticsChart({ title, data, type = 'bar' }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="font-semibold text-gray-900 dark:text-white mb-4">{title}</h3>

      <div className="space-y-4">
        {data.map((item, idx) => (
          <div key={idx}>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.label}</span>
              <span className="text-sm text-gray-600 dark:text-gray-400">{item.value}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${item.value}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{data.reduce((a, b) => a + b.value, 0) / data.length}%</p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Average</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">{Math.max(...data.map(d => d.value))}%</p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Maximum</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">{Math.min(...data.map(d => d.value))}%</p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Minimum</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// VOICE WAVEFORM
// ============================================================

export function VoiceWaveform({ isActive = false, speakerId = 'you' }) {
  return (
    <div className={`flex items-center gap-1 p-3 rounded-lg ${
      isActive
        ? 'bg-blue-100 dark:bg-blue-900'
        : 'bg-gray-100 dark:bg-gray-700'
    }`}>
      {[...Array(8)].map((_, i) => (
        <div
          key={i}
          className={`w-1 rounded-full transition-all duration-100 ${
            isActive
              ? 'bg-blue-600 dark:bg-blue-400'
              : 'bg-gray-400 dark:bg-gray-600'
          }`}
          style={{
            height: isActive ? `${Math.random() * 20 + 8}px` : '4px',
          }}
        ></div>
      ))}
      <span className="text-xs font-medium text-gray-700 dark:text-gray-300 ml-2">
        {speakerId === 'you' ? 'You' : 'Speaker'}
      </span>
    </div>
  );
}

// ============================================================
// PERSONALITY GAUGE
// ============================================================

export function PersonalityGauge({ trait, value, maxValue = 100 }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
      <div className="flex justify-between mb-2">
        <h4 className="font-semibold text-gray-900 dark:text-white text-sm">{trait}</h4>
        <span className="text-sm font-bold text-blue-600 dark:text-blue-400">{value}%</span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
        <div
          className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
          style={{ width: `${(value / maxValue) * 100}%` }}
        ></div>
      </div>
    </div>
  );
}

// ============================================================
// CALL SUMMARY CARD
// ============================================================

export function CallSummaryCard({ callId, date, duration, result, frameworks, tips, onViewDetails }) {
  return (
    <div
      onClick={onViewDetails}
      className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-all cursor-pointer p-6 border border-gray-200 dark:border-gray-700"
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-gray-900 dark:text-white">Call #{callId}</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{date}</p>
        </div>
        <div className={`font-semibold text-lg ${
          result === 'Won'
            ? 'text-green-600 dark:text-green-400'
            : 'text-red-600 dark:text-red-400'
        }`}>
          {result}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-600 dark:text-gray-400">Duration</p>
          <p className="font-semibold text-gray-900 dark:text-white">{duration}</p>
        </div>
        <div>
          <p className="text-xs text-gray-600 dark:text-gray-400">Tips Used</p>
          <p className="font-semibold text-gray-900 dark:text-white">{tips}</p>
        </div>
      </div>

      <div className="flex gap-2">
        {frameworks.map((fw) => (
          <span key={fw} className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded-full">
            {fw}
          </span>
        ))}
      </div>
    </div>
  );
}

// ============================================================
// ALERT COMPONENT
// ============================================================

export function Alert({ type = 'info', title, message, onClose }) {
  const colors = {
    info: 'bg-blue-100 dark:bg-blue-900 border-blue-400 text-blue-800 dark:text-blue-200',
    warning: 'bg-yellow-100 dark:bg-yellow-900 border-yellow-400 text-yellow-800 dark:text-yellow-200',
    error: 'bg-red-100 dark:bg-red-900 border-red-400 text-red-800 dark:text-red-200',
    success: 'bg-green-100 dark:bg-green-900 border-green-400 text-green-800 dark:text-green-200',
  };

  return (
    <div className={`${colors[type]} border-l-4 p-4 rounded-lg flex items-start justify-between`}>
      <div>
        <h3 className="font-semibold">{title}</h3>
        <p className="text-sm mt-1">{message}</p>
      </div>
      {onClose && (
        <button onClick={onClose} className="text-lg">×</button>
      )}
    </div>
  );
}

// ============================================================
// BUTTON COMPONENTS
// ============================================================

export function Button({ children, variant = 'primary', size = 'md', ...props }) {
  const baseClasses = 'font-semibold rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variantClasses = {
    primary: 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white focus:ring-blue-500',
    secondary: 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
    success: 'bg-green-600 hover:bg-green-700 text-white focus:ring-green-500',
  };

  const sizeClasses = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}
      {...props}
    >
      {children}
    </button>
  );
}

// ============================================================
// BADGE COMPONENT
// ============================================================

export function Badge({ text, variant = 'blue', icon = null }) {
  const colors = {
    blue: 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
    green: 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
    red: 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200',
    yellow: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200',
    purple: 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200',
  };

  return (
    <span className={`${colors[variant]} text-xs font-semibold px-3 py-1 rounded-full inline-flex items-center gap-1`}>
      {icon && <span>{icon}</span>}
      {text}
    </span>
  );
}
