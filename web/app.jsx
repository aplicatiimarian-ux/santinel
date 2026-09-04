import React, { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import './app.css';
import LoginPage from './LoginPage.jsx';
import {
  ensureFreshToken,
  getToken,
  clearToken,
  logout,
  signalAuthLost,
  AUTH_LOST_EVENT,
} from './authClient.js';

const API_BASE = 'http://192.168.1.50:8000';

/* -------------------------------------------------------------------------- */
/*  Framework metadata — icon, bilingual names, gradient palette              */
/* -------------------------------------------------------------------------- */

const FRAMEWORKS = [
  {
    key: 'cbt',
    icon: '\u{1F9E0}',
    name: { en: 'CBT', ro: 'TCC' },
    full: { en: 'Cognitive Behavioral Therapy', ro: 'Terapie Cognitiv-Comportamentală' },
    gradient: ['#6366f1', '#8b5cf6'],
  },
  {
    key: 'nlp',
    icon: '\u{1F5E3}\u{FE0F}',
    name: { en: 'NLP', ro: 'PNL' },
    full: { en: 'Neuro-Linguistic Programming', ro: 'Programare Neuro-Lingvistică' },
    gradient: ['#0ea5e9', '#22d3ee'],
  },
  {
    key: 'ta',
    icon: '\u{1F91D}',
    name: { en: 'TA', ro: 'AT' },
    full: { en: 'Transactional Analysis', ro: 'Analiză Tranzacțională' },
    gradient: ['#10b981', '#34d399'],
  },
  {
    key: 'ei',
    icon: '\u{2764}\u{FE0F}',
    name: { en: 'EI', ro: 'IE' },
    full: { en: 'Emotional Intelligence', ro: 'Inteligență Emoțională' },
    gradient: ['#f43f5e', '#fb7185'],
  },
  {
    key: 'attachment',
    icon: '\u{1F517}',
    name: { en: 'Attachment', ro: 'Atașament' },
    full: { en: 'Attachment Theory', ro: 'Teoria Atașamentului' },
    gradient: ['#f59e0b', '#fbbf24'],
  },
  {
    key: 'game_theory',
    icon: '\u{265F}\u{FE0F}',
    name: { en: 'Game Theory', ro: 'Teoria Jocurilor' },
    full: { en: 'Strategic Game Theory', ro: 'Teoria Strategică a Jocurilor' },
    gradient: ['#d946ef', '#a855f7'],
  },
  {
    key: 'behavioral_econ',
    icon: '\u{1F3B2}',
    name: { en: 'Behavioral Econ', ro: 'Economie Comp.' },
    full: { en: 'Behavioral Economics', ro: 'Economie Comportamentală' },
    gradient: ['#14b8a6', '#22c55e'],
  },
  {
    key: 'neuroscience',
    icon: '\u{26A1}',
    name: { en: 'Neuroscience', ro: 'Neuroștiință' },
    full: { en: 'Negotiation Neuroscience', ro: 'Neuroștiința Negocierii' },
    gradient: ['#7c3aed', '#6366f1'],
  },
  {
    key: 'narrative',
    icon: '\u{1F4D6}',
    name: { en: 'Narrative', ro: 'Narativ' },
    full: { en: 'Narrative Analysis', ro: 'Analiză Narativă' },
    gradient: ['#fb923c', '#ef4444'],
  },
  {
    key: 'somatic',
    icon: '\u{1F9D8}',
    name: { en: 'Somatic', ro: 'Somatic' },
    full: { en: 'Somatic Awareness', ro: 'Conștiență Somatică' },
    gradient: ['#84cc16', '#10b981'],
  },
];

/* -------------------------------------------------------------------------- */
/*  Helpers                                                                   */
/* -------------------------------------------------------------------------- */

// Accept a plain string or a { en, ro } object.
const loc = (val, lang) => {
  if (val == null) return '';
  if (typeof val === 'string') return val;
  return val[lang] || val.en || val.ro || '';
};

// Normalise a confidence value to a 0..100 integer.
const toPct = (c) => {
  if (typeof c !== 'number' || Number.isNaN(c)) return null;
  const pct = c <= 1 ? c * 100 : c;
  return Math.round(Math.max(0, Math.min(100, pct)));
};

const confColor = (pct) => {
  if (pct == null) return '#64748b';
  if (pct < 60) return '#ef4444';
  if (pct <= 80) return '#f59e0b';
  return '#10b981';
};

// close probability is 0..10; map to the same traffic-light scale.
const probColor = (p) => {
  if (p == null) return '#64748b';
  if (p < 5) return '#ef4444';
  if (p < 8) return '#f59e0b';
  return '#10b981';
};

const formatSize = (bytes) => {
  if (!bytes) return '';
  const kb = bytes / 1024;
  return kb < 1024 ? `${Math.round(kb)} KB` : `${(kb / 1024).toFixed(1)} MB`;
};

// close_probability may arrive as 0..1 or 0..10 — normalise to an integer 0..10.
const toProb10 = (v) => {
  if (typeof v !== 'number' || Number.isNaN(v)) return null;
  return Math.round(Math.max(0, Math.min(10, v <= 1 ? v * 10 : v)));
};

// Rank the framework keys by confidence, preferring the server's own order.
const rankFrameworks = (result) => {
  if (!result) return { fmap: {}, ranked: [] };
  const fmap = (!Array.isArray(result.frameworks) && result.frameworks) || result.summary || {};
  const ranked = Array.isArray(result.top_frameworks) && result.top_frameworks.length
    ? result.top_frameworks
    : Object.keys(fmap)
        .filter((k) => typeof (fmap[k]?.confidence) === 'number')
        .sort((a, b) => fmap[b].confidence - fmap[a].confidence);
  return { fmap, ranked };
};

/* -------------------------------------------------------------------------- */
/*  Live-coaching vocal signals (simulated — no audio pipeline wired yet)     */
/* -------------------------------------------------------------------------- */

const VOCAL_SIGNALS = [
  { key: 'pitch', icon: '\u{1F3B5}', label: { en: 'Pitch', ro: 'Ton' } },
  { key: 'pace', icon: '\u{23F1}\u{FE0F}', label: { en: 'Pace', ro: 'Ritm' } },
  { key: 'energy', icon: '\u{26A1}', label: { en: 'Energy', ro: 'Energie' } },
  { key: 'breathing', icon: '\u{1F32C}\u{FE0F}', label: { en: 'Breathing', ro: 'Respirație' } },
];

// Produce plausible-looking 0..100 signal levels, gently biased by close probability.
const simulateVocals = (prob) => {
  const base = prob == null ? 52 : 34 + prob * 4.2;
  const draw = () => Math.round(Math.max(8, Math.min(96, base + (Math.random() * 44 - 22))));
  return { pitch: draw(), pace: draw(), energy: draw(), breathing: draw() };
};

const signalTier = (v) => (v < 34 ? 0 : v < 67 ? 1 : 2);
const SIGNAL_COLORS = ['#0ea5e9', '#10b981', '#f59e0b'];
const SIGNAL_STATE = [
  { en: 'Low', ro: 'Scăzut' },
  { en: 'Steady', ro: 'Stabil' },
  { en: 'High', ro: 'Ridicat' },
];

// Shared API call — used by both the text and voice analysis pages.
// Carries the JWT access token and transparently refreshes it once on a 401.
function analyzeRequest(text) {
  return fetch(`${API_BASE}/analyze?text=${encodeURIComponent(text.trim())}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken() || ''}`,
    },
  });
}

async function postAnalyze(text) {
  await ensureFreshToken().catch(() => {});
  let response = await analyzeRequest(text);
  if (response.status === 401) {
    try {
      await ensureFreshToken();
    } catch (e) {
      signalAuthLost();
      throw new Error('HTTP 401');
    }
    response = await analyzeRequest(text);
    if (response.status === 401) {
      signalAuthLost();
      throw new Error('HTTP 401');
    }
  }
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  if (data.error) throw new Error(data.error);
  return data;
}

// Live transcription (FAZA 23.2) — POST one audio segment to the Groq Whisper
// proxy. Relative URL → rides the Vite `/api` proxy (same-origin, no CORS).
async function postTranscribe(blob, lang) {
  await ensureFreshToken().catch(() => {});
  const form = new FormData();
  form.append('file', blob, `segment.${(blob.type.split('/')[1] || 'webm').split(';')[0]}`);
  form.append('lang', lang === 'ro' || lang === 'en' ? lang : 'auto');
  const doPost = () => fetch('/api/transcribe', {
    method: 'POST',
    body: form,
    headers: { Authorization: `Bearer ${getToken() || ''}` },
  });
  let res = await doPost();
  if (res.status === 401) {
    try {
      await ensureFreshToken();
    } catch (e) {
      signalAuthLost();
      throw new Error('HTTP 401');
    }
    res = await doPost();
    if (res.status === 401) {
      signalAuthLost();
      throw new Error('HTTP 401');
    }
  }
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return (data && typeof data.text === 'string') ? data.text.trim() : '';
}

/* -------------------------------------------------------------------------- */
/*  Translations                                                              */
/* -------------------------------------------------------------------------- */

const t = {
  en: {
    dashboard: 'DASHBOARD', live: 'LIVE COACHING', voice: 'VOICE ANALYSIS', video: 'VIDEO ANALYSIS', history: 'HISTORY', scripts: 'SCRIPTS',
    profile: 'PROFILE', settings: 'SETTINGS', billing: 'BILLING', logout: 'LOGOUT',
    analyzeTitle: 'Analyze Negotiation',
    analyze: 'ANALYZE WITH ALL FRAMEWORKS',
    analyzing: 'Analyzing…',
    clear: 'CLEAR',
    paste: 'Paste negotiation text:',
    error: 'Error:',
    howItWorks: 'How it works',
    step1: 'Paste the negotiation exchange above',
    step2: 'Run the analysis across all ten frameworks',
    step3: 'Review each coaching insight and apply what fits',
    step4: 'Use the close probability to gauge momentum',
    closeProbability: 'Close probability',
    outOf10: '/ 10',
    topTriggers: 'Top frameworks triggered',
    overallCoaching: 'Overall coaching',
    primaryFinding: 'Primary finding',
    suggestion: 'Coaching suggestion',
    apply: 'Apply this',
    applied: 'Applied',
    noSignal: 'No clear signal in this exchange.',
    confidence: 'Confidence',
    rawJson: 'Show raw JSON',
    hideJson: 'Hide raw JSON',
    copyJson: 'Copy JSON',
    copied: 'Copied!',
    insights: 'Coaching insights',
    // voice analysis
    voiceTitle: 'Voice Call Analysis',
    audioFile: 'Audio recording',
    uploadPrompt: 'Drop an audio file or click to browse',
    uploadFormats: 'MP3, WAV or M4A',
    removeFile: 'Remove',
    transcriptLabel: 'Call transcript',
    transcriptPlaceholder: 'Paste the call transcript here…',
    transcriptHint: 'Automatic transcription runs on the backend and is not wired yet — paste the transcript manually to analyze.',
    needTranscript: 'Paste a transcript first',
    voiceStep1: 'Upload the recorded call (optional, for your reference)',
    voiceStep2: 'Paste the transcript of the conversation',
    voiceStep3: 'Run the 10-framework analysis on the transcript',
    voiceStep4: 'Apply the coaching insights to your next call',
    // live coaching
    liveTitle: 'Live Coaching',
    liveSubtitle: 'Record the call live — mic audio is transcribed by Whisper as you speak, and SANTINEL re-analyzes every 4-5 seconds.',
    liveTranscript: 'Live transcript',
    livePlaceholder: 'Lead: ...\nYou: ...',
    insertSpeaker: 'Insert speaker',
    startCoaching: 'START COACHING',
    stopCoaching: 'STOP',
    pause: 'PAUSE',
    resume: 'RESUME',
    analyzingLive: 'Analyzing…',
    nextAnalysis: 'to next analysis',
    coachingActive: 'Coaching active',
    coachingPaused: 'Paused',
    coachingIdle: 'Idle',
    liveWaiting: 'Start coaching to see live close probability, framework triggers and vocal signals.',
    liveEmptyTranscript: 'Transcript is empty',
    realtimeTips: 'Real-time coaching tips',
    vocalSignals: 'Vocal signals',
    vocalSignalsNote: 'Vocal signals are simulated for demonstration.',
    lastUpdated: 'Updated',
    momentum: 'Momentum',
    // live coaching (audio)
    startRecording: 'Start Audio Recording',
    stopRecording: 'Stop Recording',
    recording: 'REC',
    micRequesting: 'Requesting microphone…',
    micDenied: 'Microphone unavailable — running in demo mode.',
    demoMode: 'Demo mode',
    elapsed: 'Elapsed',
    downloadTranscript: 'Download transcript',
    waitingSignal: 'Waiting for speech…',
    tipsIdle: 'Coaching tips appear here after the first analysis.',
    triggersIdle: 'Framework triggers appear after the first analysis.',
    analysesDone: 'analyses',
    wordCount: 'words',
    vocalLiveNote: 'Energy & pitch are read from your microphone; pace & breathing are modeled.',
    vocalDemoNote: 'Microphone off — vocal signals are simulated for demonstration.',
    // speech recognition
    listening: 'Listening',
    speechUnsupported: 'Speech recognition isn’t supported in this browser. Try Chrome or Edge — you can still type or edit the transcript below.',
    speechUnsupportedShort: 'No speech-to-text',
    speechDenied: 'Microphone permission was denied for speech recognition.',
    hearing: 'Hearing',
    speakNow: 'Listening — start speaking',
    phraseConfidence: 'Last phrase',
    avgConfidence: 'avg',
    transcriptEditable: 'Recognized speech appears here — you can edit it.',
    latency: 'Latency',
    // live Whisper transcription (FAZA 23.2)
    whisperLabel: 'Whisper',
    whisperReady: 'ready',
    whisperTranscribing: 'transcribing…',
    whisperSegments: 'segments',
    whisperError: 'transcription error — retrying',
    whisperOffline: 'unavailable in this browser',
    finalizingTranscript: 'Finalizing transcript…',
    sttHybridNote: 'Instant captions from the browser; Whisper refines each segment for the analysis.',
    webCaptionsOff: 'Instant captions unavailable here — Whisper still transcribes every few seconds.',
    // speaker detection
    whoSpeaking: "Who's speaking?",
    spk_me: 'Me',
    spk_lead: 'Lead',
    spk_note: 'Note',
    autoOn: 'Auto-detect',
    autoArming: 'to auto',
    autoNeedsMe: 'Keep “Me” selected so SANTINEL learns your voice',
    autoDetected: 'Auto-detected',
    reassign: 'Change speaker',
    youLinesNote: 'Only your lines feed the coaching analysis.',
    yourWords: 'your words',
    // video analysis
    videoTitle: 'Video Analysis',
    videoSubtitle: 'Upload a negotiation recording — real MediaPipe pose + face-mesh per person, AudioContext paraverbal, the 10-framework verbal analysis per party, and an integrated psychological read synced to the timeline.',
    videoUploadPrompt: 'Drop a video or click to browse',
    videoFormats: 'MP4, MOV or WEBM',
    videoTranscriptLabel: 'Transcript — label each line by speaker ("A:", "Ana:"); optional [mm:ss] timestamps',
    videoTranscriptPlaceholder: 'A: Thanks for making time today.\nB: Of course. Let us get into the numbers.\nA: ...',
    analyzeVideo: 'ANALYZE VIDEO',
    cancel: 'CANCEL',
    loadingModels: 'Loading models…',
    modelsReady: 'models ready',
    modelsIdle: 'models not loaded',
    modelLoadFail: 'Could not load the vision models (MediaPipe CDN).',
    scanningFrames: 'Scanning frames (pose + face, per person)…',
    analyzingVerbal: 'Running the 10-framework verbal analysis per party…',
    needVideo: 'Load a video first.',
    playBlocked: 'The browser blocked playback — click the video once, then Analyze.',
    ctxTitle: 'Context',
    ctxParties: 'Parties',
    ctxParty: 'Party',
    ctxRole: 'Role',
    ctxAddParty: '+ Add party',
    ctxRemove: 'Remove',
    ctxObjective: 'Objective',
    ctxObjectiveHint: 'What each party wants out of the negotiation (optional — unlocks psychology-mapped coaching).',
    ctxStakes: 'Stakes',
    ctxBackground: 'Background',
    ctxEnvironment: 'Environment',
    ctxEnvNote: 'Notes on the setting',
    ctxParsedFrom: 'Detected speakers',
    ctxNoLabels: 'No "Speaker:" labels found — the whole transcript is treated as one party. Add labels for per-party analysis.',
    ctxTimestamps: 'timestamps found — paraverbal split per speaker',
    integratedCoaching: 'Combined coaching',
    combinedCoaching: 'Combined coaching — all parties',
    perPartyTitle: 'Per-party psychological profile',
    comparativeTitle: 'Comparative analysis',
    scenariosTitle: 'Outcome probability',
    vVerbal: 'Verbal', vNonVerbal: 'Non-verbal', vParaVerbal: 'Paraverbal',
    vCloseProb: 'Close probability',
    vNoTranscript: 'No transcript for this party.',
    vPosture: 'Posture', vGestures: 'Gestures', vMovement: 'Movement',
    vExpression: 'Expression', vEyeContact: 'Eye contact',
    vBody: 'Body', vVoice: 'Voice',
    paraShared: 'Shared audio channel — not split per speaker (no timestamps in transcript).',
    postureOpen: 'Open', postureLean: 'Leaning in', postureRigid: 'Rigid',
    postureDefensive: 'Defensive / closed', postureNeutral: 'Neutral',
    lvlLow: 'Low', lvlModerate: 'Moderate', lvlHigh: 'High',
    moveStill: 'Still', moveShift: 'Shifting', movePace: 'Restless',
    exprEngaged: 'Engaged', exprNeutral: 'Neutral', exprTense: 'Tense',
    pVolume: 'Volume', pPitch: 'Pitch', pPace: 'Pace', pTone: 'Tone',
    pitchLow: 'Low', pitchMid: 'Mid', pitchHigh: 'High',
    paceSlow: 'Slow', paceMeasured: 'Measured', paceFast: 'Fast',
    toneFlat: 'Flat / monotone', toneSteady: 'Steady', toneStrained: 'Strained',
    pUnavailable: 'Body/voice track could not be analysed for this party.',
    coverage: 'Detection coverage', face: 'face', pose: 'pose', metrics: 'Metrics',
    moment: 'Moment', sigStrong: 'Strong', sigNeutral: 'Neutral', sigWeak: 'Weak',
    apPersonality: 'Personality', apCognitive: 'Cognitive style', apEmotional: 'Emotional state',
    apDecision: 'Decision-making', apPower: 'Power dynamics', apAuthenticity: 'Authenticity',
    apVulnerabilities: 'Vulnerabilities', apStrengths: 'Strengths',
    tierTitle: '3-tier read', tierAmateur: 'Amateur', tierPro: 'Professional', tierExpert: 'Expert',
    cmpConfidence: 'Confidence', cmpAuthenticity: 'Authenticity', cmpPower: 'Power',
    cmpHidden: 'Possible hidden agendas', cmpNone: 'No strong incongruities detected.',
    stratTitle: 'Strategic paths', stratObjective: 'objective-mapped',
    stratGeneral: 'general leverage — set an objective for psychology-mapped moves',
    videoStep1: 'Fill in the context on the left — parties, roles, objectives, stakes, setting',
    videoStep2: 'Upload the recording and paste the transcript with "Speaker:" labels',
    videoStep3: 'Analyze runs MediaPipe pose + face-mesh per person and AudioContext paraverbal on every frame, then the 10 frameworks per party',
    videoStep4: 'Read the per-party profiles, the A-vs-B comparison and outcome odds, and scrub the color-coded per-party timeline',
    ctxToggle: 'Context & parties',
    ctxNoObj: 'no objectives set',
    ctxObjLower: 'objectives',
    ctxOpen: 'Open', ctxClose: 'Close',
    ctxFallback: 'Analyzing without objectives set — general profile only. Add per-party objectives in Context to unlock psychology-mapped coaching.',
    ctxMultiHint: 'Tip: label lines "A:", "B:" (or names) to profile each party separately.',
    ctxMultiActive: 'Multi-party — analysing each side separately',
    tlFlow: 'Conversation flow',
    tlLive: 'Session flow',
  },
  ro: {
    dashboard: 'TABLOU DE BORD', live: 'COACHING LIVE', voice: 'ANALIZĂ VOCALĂ', video: 'ANALIZĂ VIDEO', history: 'ISTORIC', scripts: 'SCRIPTURI',
    profile: 'PROFIL', settings: 'SETĂRI', billing: 'FACTURARE', logout: 'DECONECTARE',
    analyzeTitle: 'Analizează Negocierea',
    analyze: 'ANALIZEAZĂ CU TOATE FRAMEWORK-URILE',
    analyzing: 'Se analizează…',
    clear: 'ȘTERGE',
    paste: 'Lipește textul negocierii:',
    error: 'Eroare:',
    howItWorks: 'Cum funcționează',
    step1: 'Lipește schimbul de replici din negociere mai sus',
    step2: 'Rulează analiza pe toate cele zece framework-uri',
    step3: 'Parcurge fiecare recomandare și aplică ce se potrivește',
    step4: 'Folosește probabilitatea de închidere ca indicator de moment',
    closeProbability: 'Probabilitate de închidere',
    outOf10: '/ 10',
    topTriggers: 'Framework-uri principale activate',
    overallCoaching: 'Recomandare generală',
    primaryFinding: 'Constatare principală',
    suggestion: 'Recomandare de coaching',
    apply: 'Aplică',
    applied: 'Aplicat',
    noSignal: 'Niciun semnal clar în acest schimb.',
    confidence: 'Încredere',
    rawJson: 'Arată JSON brut',
    hideJson: 'Ascunde JSON brut',
    copyJson: 'Copiază JSON',
    copied: 'Copiat!',
    insights: 'Recomandări de coaching',
    // voice analysis
    voiceTitle: 'Analiză Apel Vocal',
    audioFile: 'Înregistrare audio',
    uploadPrompt: 'Trage un fișier audio sau dă clic pentru a răsfoi',
    uploadFormats: 'MP3, WAV sau M4A',
    removeFile: 'Elimină',
    transcriptLabel: 'Transcrierea apelului',
    transcriptPlaceholder: 'Lipește aici transcrierea apelului…',
    transcriptHint: 'Transcrierea automată rulează pe backend și nu este încă conectată — lipește manual transcrierea pentru analiză.',
    needTranscript: 'Lipește mai întâi o transcriere',
    voiceStep1: 'Încarcă apelul înregistrat (opțional, ca referință)',
    voiceStep2: 'Lipește transcrierea conversației',
    voiceStep3: 'Rulează analiza pe cele 10 framework-uri pe transcriere',
    voiceStep4: 'Aplică recomandările la următorul apel',
    // live coaching
    liveTitle: 'Coaching în Timp Real',
    liveSubtitle: 'Înregistrează apelul în direct — audio-ul de la microfon este transcris de Whisper pe măsură ce vorbești, iar SANTINEL reanalizează la fiecare 4-5 secunde.',
    liveTranscript: 'Transcriere live',
    livePlaceholder: 'Lead: ...\nYou: ...',
    insertSpeaker: 'Inserează vorbitor',
    startCoaching: 'ÎNCEPE COACHING',
    stopCoaching: 'STOP',
    pause: 'PAUZĂ',
    resume: 'RELUARE',
    analyzingLive: 'Se analizează…',
    nextAnalysis: 'până la următoarea analiză',
    coachingActive: 'Coaching activ',
    coachingPaused: 'În pauză',
    coachingIdle: 'Inactiv',
    liveWaiting: 'Începe coaching-ul pentru a vedea probabilitatea de închidere, framework-urile activate și semnalele vocale.',
    liveEmptyTranscript: 'Transcrierea este goală',
    realtimeTips: 'Sfaturi de coaching în timp real',
    vocalSignals: 'Semnale vocale',
    vocalSignalsNote: 'Semnalele vocale sunt simulate în scop demonstrativ.',
    lastUpdated: 'Actualizat',
    momentum: 'Moment',
    // live coaching (audio)
    startRecording: 'Începe înregistrarea audio',
    stopRecording: 'Oprește înregistrarea',
    recording: 'ÎNREG',
    micRequesting: 'Se solicită microfonul…',
    micDenied: 'Microfon indisponibil — se rulează în mod demo.',
    demoMode: 'Mod demo',
    elapsed: 'Durată',
    downloadTranscript: 'Descarcă transcrierea',
    waitingSignal: 'Se așteaptă vorbirea…',
    tipsIdle: 'Sfaturile de coaching apar aici după prima analiză.',
    triggersIdle: 'Framework-urile activate apar după prima analiză.',
    analysesDone: 'analize',
    wordCount: 'cuvinte',
    vocalLiveNote: 'Energia și tonul sunt citite din microfon; ritmul și respirația sunt estimate.',
    vocalDemoNote: 'Microfon oprit — semnalele vocale sunt simulate în scop demonstrativ.',
    // speech recognition
    listening: 'Ascult',
    speechUnsupported: 'Recunoașterea vocală nu este acceptată în acest browser. Încearcă Chrome sau Edge — poți totuși scrie sau edita transcrierea mai jos.',
    speechUnsupportedShort: 'Fără voce-în-text',
    speechDenied: 'Permisiunea pentru microfon a fost refuzată pentru recunoașterea vocală.',
    hearing: 'Se aude',
    speakNow: 'Ascult — începe să vorbești',
    phraseConfidence: 'Ultima frază',
    avgConfidence: 'medie',
    transcriptEditable: 'Textul recunoscut apare aici — îl poți edita.',
    latency: 'Latență',
    // live Whisper transcription (FAZA 23.2)
    whisperLabel: 'Whisper',
    whisperReady: 'gata',
    whisperTranscribing: 'transcrie…',
    whisperSegments: 'segmente',
    whisperError: 'eroare la transcriere — reîncerc',
    whisperOffline: 'indisponibil în acest browser',
    finalizingTranscript: 'Finalizez transcrierea…',
    sttHybridNote: 'Subtitrări instant din browser; Whisper rafinează fiecare segment pentru analiză.',
    webCaptionsOff: 'Subtitrările instant nu sunt disponibile aici — Whisper tot transcrie la câteva secunde.',
    // speaker detection
    whoSpeaking: 'Cine vorbește?',
    spk_me: 'Eu',
    spk_lead: 'Client',
    spk_note: 'Notă',
    autoOn: 'Detecție automată',
    autoArming: 'până la auto',
    autoNeedsMe: 'Ține „Eu" selectat ca SANTINEL să-ți învețe vocea',
    autoDetected: 'Detectat automat',
    reassign: 'Schimbă vorbitorul',
    youLinesNote: 'Doar replicile tale alimentează analiza de coaching.',
    yourWords: 'cuvintele tale',
    // video analysis
    videoTitle: 'Analiză Video',
    videoSubtitle: 'Încarcă o înregistrare de negociere — MediaPipe real pentru postură + rețea facială per persoană, paraverbal din AudioContext, analiza verbală pe 10 framework-uri per parte și o citire psihologică integrată, sincronizate cu cronologia.',
    videoUploadPrompt: 'Trage un video sau dă clic pentru a răsfoi',
    videoFormats: 'MP4, MOV sau WEBM',
    videoTranscriptLabel: 'Transcriere — etichetează fiecare rând cu vorbitorul ("A:", "Ana:"); opțional marcaje [mm:ss]',
    videoTranscriptPlaceholder: 'A: Mulțumesc că ți-ai făcut timp azi.\nB: Sigur. Hai să intrăm în cifre.\nA: ...',
    analyzeVideo: 'ANALIZEAZĂ VIDEO',
    cancel: 'ANULEAZĂ',
    loadingModels: 'Se încarcă modelele…',
    modelsReady: 'modele gata',
    modelsIdle: 'modele neîncărcate',
    modelLoadFail: 'Modelele de vizuală nu au putut fi încărcate (CDN MediaPipe).',
    scanningFrames: 'Se scanează cadrele (postură + față, per persoană)…',
    analyzingVerbal: 'Se rulează analiza verbală pe 10 framework-uri per parte…',
    needVideo: 'Încarcă mai întâi un video.',
    playBlocked: 'Browserul a blocat redarea — dă clic pe video o dată, apoi Analizează.',
    ctxTitle: 'Context',
    ctxParties: 'Părți',
    ctxParty: 'Partea',
    ctxRole: 'Rol',
    ctxAddParty: '+ Adaugă parte',
    ctxRemove: 'Elimină',
    ctxObjective: 'Obiectiv',
    ctxObjectiveHint: 'Ce vrea fiecare parte din negociere (opțional — deblochează coaching mapat pe psihologie).',
    ctxStakes: 'Mize',
    ctxBackground: 'Context / istoric',
    ctxEnvironment: 'Mediu',
    ctxEnvNote: 'Note despre cadru',
    ctxParsedFrom: 'Vorbitori detectați',
    ctxNoLabels: 'Nu s-au găsit etichete „Vorbitor:" — toată transcrierea e tratată ca o singură parte. Adaugă etichete pentru analiză per parte.',
    ctxTimestamps: 'marcaje de timp găsite — paraverbalul e împărțit per vorbitor',
    integratedCoaching: 'Coaching combinat',
    combinedCoaching: 'Coaching combinat — toate părțile',
    perPartyTitle: 'Profil psihologic per parte',
    comparativeTitle: 'Analiză comparativă',
    scenariosTitle: 'Probabilitatea rezultatelor',
    vVerbal: 'Verbal', vNonVerbal: 'Non-verbal', vParaVerbal: 'Paraverbal',
    vCloseProb: 'Probabilitate de închidere',
    vNoTranscript: 'Fără transcriere pentru această parte.',
    vPosture: 'Postură', vGestures: 'Gesturi', vMovement: 'Mișcare',
    vExpression: 'Expresie', vEyeContact: 'Contact vizual',
    vBody: 'Corp', vVoice: 'Voce',
    paraShared: 'Canal audio comun — neîmpărțit per vorbitor (fără marcaje de timp în transcriere).',
    postureOpen: 'Deschisă', postureLean: 'Aplecat înainte', postureRigid: 'Rigidă',
    postureDefensive: 'Defensivă / închisă', postureNeutral: 'Neutră',
    lvlLow: 'Scăzut', lvlModerate: 'Moderat', lvlHigh: 'Ridicat',
    moveStill: 'Nemișcat', moveShift: 'Se foiește', movePace: 'Agitat',
    exprEngaged: 'Implicat', exprNeutral: 'Neutru', exprTense: 'Tensionat',
    pVolume: 'Volum', pPitch: 'Ton', pPace: 'Ritm', pTone: 'Timbru',
    pitchLow: 'Jos', pitchMid: 'Mediu', pitchHigh: 'Înalt',
    paceSlow: 'Lent', paceMeasured: 'Măsurat', paceFast: 'Rapid',
    toneFlat: 'Plat / monoton', toneSteady: 'Constant', toneStrained: 'Încordat',
    pUnavailable: 'Pista corp/voce nu a putut fi analizată pentru această parte.',
    coverage: 'Acoperire detecție', face: 'față', pose: 'postură', metrics: 'Metrici',
    moment: 'Moment', sigStrong: 'Puternic', sigNeutral: 'Neutru', sigWeak: 'Slab',
    apPersonality: 'Personalitate', apCognitive: 'Stil cognitiv', apEmotional: 'Stare emoțională',
    apDecision: 'Luarea deciziilor', apPower: 'Dinamica puterii', apAuthenticity: 'Autenticitate',
    apVulnerabilities: 'Vulnerabilități', apStrengths: 'Puncte forte',
    tierTitle: 'Citire pe 3 niveluri', tierAmateur: 'Amator', tierPro: 'Profesionist', tierExpert: 'Expert',
    cmpConfidence: 'Încredere', cmpAuthenticity: 'Autenticitate', cmpPower: 'Putere',
    cmpHidden: 'Posibile agende ascunse', cmpNone: 'Nicio incongruență puternică detectată.',
    stratTitle: 'Căi strategice', stratObjective: 'mapat pe obiectiv',
    stratGeneral: 'pârghii generale — setează un obiectiv pentru mișcări mapate pe psihologie',
    videoStep1: 'Completează contextul din stânga — părți, roluri, obiective, mize, cadru',
    videoStep2: 'Încarcă înregistrarea și lipește transcrierea cu etichete „Vorbitor:"',
    videoStep3: 'Analiza rulează MediaPipe postură + rețea facială per persoană și paraverbal AudioContext pe fiecare cadru, apoi cele 10 framework-uri per parte',
    videoStep4: 'Citește profilurile per parte, comparația A-vs-B și șansele rezultatelor și parcurge cronologia colorată per parte',
    ctxToggle: 'Context și părți',
    ctxNoObj: 'fără obiective setate',
    ctxObjLower: 'obiective',
    ctxOpen: 'Deschide', ctxClose: 'Închide',
    ctxFallback: 'Analiză fără obiective setate — doar profil general. Adaugă obiective per parte în Context pentru coaching mapat pe psihologie.',
    ctxMultiHint: 'Sfat: etichetează rândurile cu „A:", „B:" (sau nume) pentru a profila fiecare parte separat.',
    ctxMultiActive: 'Multi-parte — se analizează fiecare parte separat',
    tlFlow: 'Firul conversației',
    tlLive: 'Firul sesiunii',
  },
};

/* -------------------------------------------------------------------------- */
/*  Sub-components                                                            */
/* -------------------------------------------------------------------------- */

function ConfidenceBar({ pct, label }) {
  const color = confColor(pct);
  return (
    <div className="si-conf">
      <div className="si-conf-head">
        <span>{label}</span>
        <span className="si-conf-val" style={{ color }}>
          {pct == null ? '—' : `${pct}%`}
        </span>
      </div>
      <div className="si-conf-track">
        <div
          className="si-conf-fill"
          style={{ width: `${pct == null ? 0 : pct}%`, background: color }}
        />
      </div>
    </div>
  );
}

function FrameworkCard({ meta, data, lang, index, applied, onApply }) {
  const pct = toPct(data?.confidence);
  const finding = loc(data?.primary_finding, lang);
  const suggestion = loc(data?.suggestion, lang);
  const hasData = Boolean(finding || suggestion || pct != null);
  const [g1, g2] = meta.gradient;

  return (
    <article
      className={`si-card${applied ? ' si-card--applied' : ''}${hasData ? '' : ' si-card--empty'}`}
      style={{ '--g1': g1, '--g2': g2, animationDelay: `${index * 70}ms` }}
    >
      <header className="si-card-head">
        <span className="si-card-icon" aria-hidden="true">{meta.icon}</span>
        <div className="si-card-titles">
          <h4 className="si-card-name">{meta.name[lang]}</h4>
          <p className="si-card-full">{meta.full[lang]}</p>
        </div>
      </header>

      <div className="si-card-body">
        <div className="si-field">
          <span className="si-field-label">{t[lang].primaryFinding}</span>
          <p className="si-finding">{finding || t[lang].noSignal}</p>
        </div>

        <ConfidenceBar pct={pct} label={t[lang].confidence} />

        {suggestion && (
          <div className="si-field">
            <span className="si-field-label">{t[lang].suggestion}</span>
            <p className="si-suggestion">
              <span className="si-suggestion-bullet" aria-hidden="true">{'\u{1F4A1}'}</span>
              {suggestion}
            </p>
          </div>
        )}
      </div>

      <button
        type="button"
        className="si-apply"
        onClick={() => onApply(meta.key, suggestion)}
        disabled={!suggestion}
      >
        {applied ? `✓ ${t[lang].applied}` : t[lang].apply}
      </button>
    </article>
  );
}

function SummaryHero({ result, lang }) {
  const prob = typeof result.close_probability === 'number'
    ? Math.round(result.close_probability <= 1 ? result.close_probability * 10 : result.close_probability)
    : null;
  const color = probColor(prob);
  const overall = loc(result.coaching, lang);

  // Rank frameworks by confidence — prefer server order, fall back to computed.
  const fmap = (!Array.isArray(result.frameworks) && result.frameworks) || result.summary || {};
  let ranked = Array.isArray(result.top_frameworks) && result.top_frameworks.length
    ? result.top_frameworks
    : Object.keys(fmap)
        .filter((k) => typeof (fmap[k]?.confidence) === 'number')
        .sort((a, b) => fmap[b].confidence - fmap[a].confidence);
  ranked = ranked.slice(0, 3);

  const metaOf = (k) => FRAMEWORKS.find((f) => f.key === k);

  return (
    <section className="si-hero">
      <div className="si-hero-score">
        <div
          className="si-gauge"
          style={{
            background: `conic-gradient(${color} ${(prob ?? 0) * 36}deg, rgba(148,163,184,0.18) 0deg)`,
          }}
        >
          <div className="si-gauge-inner">
            <span className="si-gauge-num" style={{ color }}>{prob ?? '—'}</span>
            <span className="si-gauge-unit">{t[lang].outOf10}</span>
          </div>
        </div>
        <span className="si-hero-label">{t[lang].closeProbability}</span>
      </div>

      <div className="si-hero-side">
        <div className="si-hero-block">
          <span className="si-field-label">{t[lang].topTriggers}</span>
          <ol className="si-triggers">
            {ranked.map((k, i) => {
              const meta = metaOf(k);
              const pct = toPct(fmap[k]?.confidence);
              if (!meta) return null;
              return (
                <li key={k} className="si-trigger" style={{ '--g1': meta.gradient[0], '--g2': meta.gradient[1] }}>
                  <span className="si-trigger-rank">{i + 1}</span>
                  <span className="si-trigger-icon" aria-hidden="true">{meta.icon}</span>
                  <span className="si-trigger-name">{meta.name[lang]}</span>
                  {pct != null && (
                    <span className="si-trigger-pct" style={{ color: confColor(pct) }}>{pct}%</span>
                  )}
                </li>
              );
            })}
          </ol>
        </div>

        {overall && (
          <div className="si-hero-block">
            <span className="si-field-label">{t[lang].overallCoaching}</span>
            <p className="si-hero-coaching">{overall}</p>
          </div>
        )}
      </div>
    </section>
  );
}

/**
 * Shared results view — the summary hero + the 10 framework cards + raw JSON.
 * Owns its own "applied" / "show JSON" state, reset whenever a new result lands.
 */
function ResultsView({ result, lang }) {
  const L = t[lang];
  const [applied, setApplied] = useState({});
  const [showJson, setShowJson] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setApplied({});
    setShowJson(false);
    setCopied(false);
  }, [result]);

  const frameworkData = useMemo(() => {
    if (!result) return {};
    if (result.frameworks && !Array.isArray(result.frameworks)) return result.frameworks;
    return result.summary || {};
  }, [result]);

  const handleApply = (key, suggestion) => {
    setApplied((prev) => ({ ...prev, [key]: !prev[key] }));
    if (suggestion && navigator.clipboard) {
      navigator.clipboard.writeText(suggestion).catch(() => {});
    }
  };

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="si-results">
      <SummaryHero result={result} lang={lang} />

      <div className="si-insights-head">
        <h3 className="si-h3">{L.insights}</h3>
        <button type="button" className="si-linkbtn" onClick={() => setShowJson((v) => !v)}>
          {showJson ? L.hideJson : L.rawJson}
        </button>
      </div>

      <div className="si-grid">
        {FRAMEWORKS.map((meta, i) => (
          <FrameworkCard
            key={meta.key}
            meta={meta}
            data={frameworkData[meta.key]}
            lang={lang}
            index={i}
            applied={!!applied[meta.key]}
            onApply={handleApply}
          />
        ))}
      </div>

      {showJson && (
        <div className="si-json">
          <button type="button" className="si-linkbtn" onClick={handleCopyJson}>
            {copied ? L.copied : L.copyJson}
          </button>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

function HelpPanel({ lang, steps }) {
  return (
    <div className="si-help">
      <h4 className="si-help-title">{t[lang].howItWorks}</h4>
      <ol className="si-help-list">
        {steps.map((s, i) => <li key={i}>{s}</li>)}
      </ol>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*  Pages                                                                     */
/* -------------------------------------------------------------------------- */

/* -------------------------------------------------------------------------- */
/*  SHARED — unified context / multi-party / objectives / 3-tier across pages  */
/* -------------------------------------------------------------------------- */

// Collapsible context bar (Dashboard / Voice / Live). Video uses the sidebar variant.
function ContextBar({ context, setContext, lang, defaultOpen = false }) {
  const L = t[lang];
  const [open, setOpen] = useState(defaultOpen);
  const nParties = context.parties.length;
  const nObj = context.parties.filter((p) => (context.objectives[p.id] || '').trim()).length;
  const summary = `${nParties} ${L.ctxParties.toLowerCase()} · ${nObj ? `${nObj} ${L.ctxObjLower}` : L.ctxNoObj}`;
  return (
    <div className={`cx-bar${open ? ' is-open' : ''}`}>
      <button type="button" className="cx-bar-toggle" onClick={() => setOpen((v) => !v)} aria-expanded={open}>
        <span className="cx-bar-caret" aria-hidden="true">{open ? '▾' : '▸'}</span>
        <span className="cx-bar-title">{L.ctxToggle}</span>
        <span className="cx-bar-summary">{summary}</span>
        <span className="cx-bar-action">{open ? L.ctxClose : L.ctxOpen}</span>
      </button>
      {open && (
        <div className="cx-bar-body">
          <ContextPanel context={context} setContext={setContext} lang={lang} variant="panel" />
        </div>
      )}
    </div>
  );
}

// "Analyzing without objectives set" banner — shown when no party has an objective.
function ContextFallbackNote({ context, lang }) {
  const any = context.parties.some((p) => (context.objectives[p.id] || '').trim());
  if (any) return null;
  return <div className="cx-fallback">{'⚠️'} {t[lang].ctxFallback}</div>;
}

// Single-track color-coded timeline (t0/t1 are 0..1 fractions). No playhead / seeking.
function FlowTimeline({ segments, lang, label }) {
  const L = t[lang];
  if (!segments || !segments.length) return null;
  return (
    <div className="va-timeline">
      <div className="va-tl-row">
        <span className="va-tl-tag">{label || L.tlFlow}</span>
        <div className="va-timeline-track">
          {segments.map((m, i) => (
            <div
              key={i}
              className="va-tl-seg"
              style={{ left: `${m.t0 * 100}%`, width: `${(m.t1 - m.t0) * 100}%`, background: m.color }}
              title={`${m.score}/100`}
            />
          ))}
        </div>
      </div>
      <div className="va-tl-legend">
        <span><i style={{ background: '#10b981' }} /> {L.sigStrong}</span>
        <span><i style={{ background: '#f59e0b' }} /> {L.sigNeutral}</span>
        <span><i style={{ background: '#ef4444' }} /> {L.sigWeak}</span>
      </div>
    </div>
  );
}

// A-vs-B comparative panel (shared by Video + the text/voice modules).
function ComparativePanel({ enriched, comparative, lang }) {
  const L = t[lang];
  if (!comparative) return null;
  return (
    <div className="va-cmp">
      <span className="si-field-label">{L.comparativeTitle}</span>
      <div className="va-cmp-parties">
        {enriched.map((pd, i) => (
          <span key={pd.id} style={{ color: partyColor(i) }}>■ {pd.label}</span>
        ))}
      </div>
      {comparative.rows.map((r) => (
        <CmpBar key={r.key} label={r.label} vals={r.vals} parties={enriched} />
      ))}
      <div className="va-cmp-hidden">
        <span className="va-pcol-h">{L.cmpHidden}</span>
        {comparative.hidden.every((h) => !h.flags.length) && <p className="va-sub">{L.cmpNone}</p>}
        {comparative.hidden.map((h, i) => h.flags.map((f, j) => (
          <p key={`${i}-${j}`} className="va-hidden-flag" style={{ borderColor: partyColor(i) }}>
            <b style={{ color: partyColor(i) }}>{h.label}</b> {f}
          </p>
        )))}
      </div>
    </div>
  );
}

function ScenarioPanel({ scenarios, lang }) {
  const L = t[lang];
  if (!scenarios || !scenarios.length) return null;
  return (
    <div className="va-scen">
      <span className="si-field-label">{L.scenariosTitle}</span>
      {scenarios.map((s) => (
        <div key={s.key} className="va-scen-row">
          <span className="va-scen-label">{s.label}</span>
          <div className="va-scen-track">
            <div className="va-scen-fill" style={{ width: `${s.p}%` }} />
          </div>
          <span className="va-scen-p">{s.p}%</span>
        </div>
      ))}
    </div>
  );
}

// Real /analyze over pasted text. If ≥2 speaker-labelled parties -> per-party; else single.
async function runContextAnalysis(rawText, context) {
  const parties = context.parties.slice(0, MAX_PARTIES);
  const dlg = parseDialogue(rawText, parties);
  const filled = parties.filter((p) => (dlg.perPartyText[p.id] || '').trim().length > 10);
  if (dlg.labeled && filled.length >= 2) {
    const results = await Promise.all(parties.map(async (p) => {
      const txt = (dlg.perPartyText[p.id] || '').trim();
      let verbal = null;
      if (txt.length > 10) {
        try { verbal = await postAnalyze(txt); } catch (e) { verbal = null; }
      }
      return {
        id: p.id, label: p.label || p.id, role: p.role || '',
        objective: context.objectives[p.id] || '', verbal, nv: null, pv: null,
      };
    }));
    const withV = results.filter((r) => r.verbal);
    if (withV.length >= 2) return { mode: 'multi', parties: withV, dlg, single: null };
  }
  const single = await postAnalyze(rawText);
  return { mode: 'single', parties: [], dlg, single };
}

// Real "conversation flow" timeline — cumulative windows through the text, each scored
// by its own /analyze close_probability. Empty for short inputs.
async function buildConversationTimeline(rawText) {
  const clean = String(rawText || '').replace(/\s+/g, ' ').trim();
  const words = clean ? clean.split(' ') : [];
  if (words.length < 45) return [];
  const k = Math.min(5, Math.max(3, Math.round(words.length / 70)));
  const size = Math.ceil(words.length / k);
  const wins = [];
  for (let i = 0; i < k; i += 1) wins.push(words.slice(0, (i + 1) * size).join(' '));
  const segs = await Promise.all(wins.map(async (w, i) => {
    let s = 50;
    try {
      const r = await postAnalyze(w);
      s = clamp(Math.round((toProb10(r.close_probability) || 0) * 10), 0, 100);
    } catch (e) { /* keep neutral */ }
    return { t0: i / k, t1: (i + 1) / k, score: s, color: signalColor(s) };
  }));
  return segs;
}

// Unified results renderer for the text / transcript modules (Dashboard, Voice).
function ContextResults({ analysis, context, lang, timeline, timelineLabel }) {
  const L = t[lang];
  if (!analysis) return null;
  const { mode, single, parties } = analysis;

  if (mode === 'single') {
    const p0 = context.parties[0] || { id: 'A', label: 'A', role: '' };
    const pd = {
      id: p0.id, label: p0.label || p0.id, role: p0.role || '',
      objective: context.objectives[p0.id] || '', verbal: single, nv: null, pv: null,
    };
    const prof = deriveProfile(pd, lang);
    const tiers = deriveTiers(pd, prof, lang);
    const paths = deriveStrategicPaths(pd, prof, null, pd.objective, lang);
    return (
      <div className="va-results">
        <ContextFallbackNote context={context} lang={lang} />
        {timeline && timeline.length > 0 && (
          <FlowTimeline segments={timeline} lang={lang} label={timelineLabel} />
        )}
        <ResultsView result={single} lang={lang} />
        <span className="si-field-label va-section-h">{L.perPartyTitle}</span>
        <div className="va-pcards">
          <ProfileCard pd={pd} prof={prof} tiers={tiers} paths={paths} index={0} lang={lang} />
        </div>
      </div>
    );
  }

  const enriched = parties.map((pd, i) => ({ ...pd, index: i, prof: deriveProfile(pd, lang) }));
  const comparative = deriveComparative(enriched, lang);
  const scenarios = deriveScenarios(enriched, context, lang);
  const combined = scenarios.length ? deriveCombined(enriched, comparative, scenarios, lang) : '';
  return (
    <div className="va-results">
      <ContextFallbackNote context={context} lang={lang} />
      <div className="cx-multi-note">{'\u{1F465}'} {L.ctxMultiActive}</div>
      {timeline && timeline.length > 0 && (
        <FlowTimeline segments={timeline} lang={lang} label={timelineLabel} />
      )}
      {combined && (
        <div className="va-integrated">
          <span className="si-field-label">{L.combinedCoaching}</span>
          <p>{combined}</p>
        </div>
      )}
      <ComparativePanel enriched={enriched} comparative={comparative} lang={lang} />
      <ScenarioPanel scenarios={scenarios} lang={lang} />
      <span className="si-field-label va-section-h">{L.perPartyTitle}</span>
      <div className="va-pcards">
        {enriched.map((pd) => {
          const opp = enriched.find((o) => o.id !== pd.id);
          const tiers = deriveTiers(pd, pd.prof, lang);
          const paths = deriveStrategicPaths(pd, pd.prof, opp, pd.objective, lang);
          return (
            <ProfileCard
              key={pd.id}
              pd={pd}
              prof={pd.prof}
              tiers={tiers}
              paths={paths}
              index={pd.index}
              lang={lang}
            />
          );
        })}
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*  Dashboard — text analysis + unified context                               */
/* -------------------------------------------------------------------------- */

function AnalyzePage({ lang }) {
  const L = t[lang];
  const [context, setContext] = useState(makeContext);
  const [text, setText] = useState(
    'A: "I\'m interested but the price is too high"\nB: "I understand cost is important. Let me show you the ROI..."'
  );
  const [analysis, setAnalysis] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = async () => {
    if (!text.trim()) {
      setError(lang === 'en' ? 'Please enter text' : 'Te rog introdu un text');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [a, tl] = await Promise.all([
        runContextAnalysis(text, context),
        buildConversationTimeline(text),
      ]);
      setAnalysis(a);
      setTimeline(tl);
    } catch (err) {
      setError(`${L.error} ${err.message}`);
      setAnalysis(null);
      setTimeline([]);
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const clear = () => {
    setText('');
    setAnalysis(null);
    setTimeline([]);
    setError(null);
  };

  return (
    <div className="si-page">
      <h2 className="si-h2">{L.analyzeTitle}</h2>

      <ContextBar context={context} setContext={setContext} lang={lang} />

      <div className="si-input-block">
        <label className="si-field-label" htmlFor="si-text">{L.paste}</label>
        <textarea
          id="si-text"
          className="si-textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={L.paste}
          onKeyDown={(e) => e.ctrlKey && e.key === 'Enter' && run()}
        />
        <p className="si-voice-hint">{L.ctxMultiHint}</p>
      </div>

      <div className="si-actions">
        <button
          type="button"
          className="si-btn si-btn--primary"
          onClick={run}
          disabled={loading || !text.trim()}
        >
          {loading ? L.analyzing : L.analyze}
        </button>
        {text && (
          <button type="button" className="si-btn si-btn--ghost" onClick={clear}>
            {L.clear}
          </button>
        )}
      </div>

      {error && <div className="si-error">{error}</div>}
      {analysis && (
        <ContextResults analysis={analysis} context={context} lang={lang} timeline={timeline} />
      )}
      {!analysis && !error && (
        <HelpPanel lang={lang} steps={[L.step1, L.step2, L.step3, L.step4]} />
      )}
    </div>
  );
}

function VoiceAnalysis({ lang }) {
  const L = t[lang];
  const inputRef = useRef(null);
  const [context, setContext] = useState(makeContext);
  const [fileName, setFileName] = useState('');
  const [fileSize, setFileSize] = useState(0);
  const [dragOver, setDragOver] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const acceptFile = (file) => {
    if (!file) return;
    setFileName(file.name);
    setFileSize(file.size || 0);
  };

  const removeFile = () => {
    setFileName('');
    setFileSize(0);
    if (inputRef.current) inputRef.current.value = '';
  };

  const run = async () => {
    if (!transcript.trim()) {
      setError(L.needTranscript);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [a, tl] = await Promise.all([
        runContextAnalysis(transcript, context),
        buildConversationTimeline(transcript),
      ]);
      setAnalysis(a);
      setTimeline(tl);
    } catch (err) {
      setError(`${L.error} ${err.message}`);
      setAnalysis(null);
      setTimeline([]);
      console.error('Voice analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    removeFile();
    setTranscript('');
    setAnalysis(null);
    setTimeline([]);
    setError(null);
  };

  return (
    <div className="si-page">
      <h2 className="si-h2">{L.voiceTitle}</h2>

      <ContextBar context={context} setContext={setContext} lang={lang} />

      <div className="si-input-block">
        <span className="si-field-label">{L.audioFile}</span>
        <div
          className={`si-voice-drop${dragOver ? ' si-voice-drop--over' : ''}`}
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            acceptFile(e.dataTransfer.files && e.dataTransfer.files[0]);
          }}
        >
          <span className="si-voice-drop-icon" aria-hidden="true">{'\u{1F399}\u{FE0F}'}</span>
          <span className="si-voice-drop-text">{L.uploadPrompt}</span>
          <span className="si-voice-drop-formats">{L.uploadFormats}</span>
          <input
            ref={inputRef}
            type="file"
            accept=".mp3,.wav,.m4a,audio/mpeg,audio/wav,audio/x-m4a,audio/mp4"
            onChange={(e) => acceptFile(e.target.files && e.target.files[0])}
            hidden
          />
        </div>

        {fileName && (
          <div className="si-voice-file">
            <span className="si-voice-file-icon" aria-hidden="true">{'\u{1F3A7}'}</span>
            <span className="si-voice-file-name">{fileName}</span>
            {fileSize > 0 && <span className="si-voice-file-size">{formatSize(fileSize)}</span>}
            <button type="button" className="si-voice-file-remove" onClick={removeFile}>
              {L.removeFile}
            </button>
          </div>
        )}
      </div>

      <div className="si-input-block">
        <label className="si-field-label" htmlFor="si-transcript">{L.transcriptLabel}</label>
        <textarea
          id="si-transcript"
          className="si-textarea"
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          placeholder={L.transcriptPlaceholder}
          onKeyDown={(e) => e.ctrlKey && e.key === 'Enter' && run()}
        />
        <p className="si-voice-hint">{L.transcriptHint} {L.ctxMultiHint}</p>
      </div>

      <div className="si-actions">
        <button
          type="button"
          className="si-btn si-btn--primary"
          onClick={run}
          disabled={loading || !transcript.trim()}
        >
          {loading ? L.analyzing : L.analyze}
        </button>
        {(transcript || fileName || analysis) && (
          <button type="button" className="si-btn si-btn--ghost" onClick={clearAll}>
            {L.clear}
          </button>
        )}
      </div>

      {error && <div className="si-error">{error}</div>}
      {analysis && (
        <ContextResults
          analysis={analysis}
          context={context}
          lang={lang}
          timeline={timeline}
          timelineLabel={L.tlFlow}
        />
      )}
      {!analysis && !error && (
        <HelpPanel lang={lang} steps={[L.voiceStep1, L.voiceStep2, L.voiceStep3, L.voiceStep4]} />
      )}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*  Live Coaching — Web Speech API transcription + 10-framework coaching       */
/* -------------------------------------------------------------------------- */

// Web Speech API. Chrome / Edge expose it prefixed; Firefox has no support.
const SpeechRecognitionCtor =
  typeof window !== 'undefined'
    ? (window.SpeechRecognition || window.webkitSpeechRecognition || null)
    : null;
const SPEECH_SUPPORTED = !!SpeechRecognitionCtor;

// --- Live-coaching latency tuning ---
const ANALYSIS_TICK_MS = 4000;      // check for new speech every 4s (was 30s)
const WORD_DELTA_TRIGGER = 20;      // ...but only call /analyze once >20 new words landed
const FIRST_ANALYSIS_MIN_WORDS = 10;
const FIRST_ANALYSIS_DELAY_MS = 1500;
const LATENCY_TARGET_MS = 500;      // perceived (API + UI render) budget

// --- Live Whisper transcription (FAZA 23.2) ---
const WHISPER_SEG_MS = 4000;        // rotate the MediaRecorder every 4s -> one Whisper call
const WHISPER_MIN_BLOB = 1400;      // ignore near-empty segments (bytes)
const WHISPER_MAX_QUEUE = 4;        // cap the backlog; drop oldest if Groq falls behind
const WHISPER_FINALIZE_MS = 8000;   // STOP won't wait longer than this for the tail segment
const WHISPER_MIME_CANDIDATES = [
  'audio/webm;codecs=opus',
  'audio/webm',
  'audio/ogg;codecs=opus',
  'audio/mp4',
];
const pickRecorderMime = () => {
  if (typeof MediaRecorder === 'undefined' || !MediaRecorder.isTypeSupported) return '';
  return WHISPER_MIME_CANDIDATES.find((m) => MediaRecorder.isTypeSupported(m)) || '';
};
// Drop trailing items while `pred` holds; returns the kept prefix.
const dropTrailingWhile = (arr, pred) => {
  let end = arr.length;
  while (end > 0 && pred(arr[end - 1])) end -= 1;
  return arr.slice(0, end);
};

// --- Speaker detection ---
// (default speaker is "me"; auto voice-fingerprinting kicks in after 3 untoggled phrases)
const SPEAKER_MODES = ['me', 'lead', 'note'];
const AUTO_AFTER_PHRASES = 3;       // no manual toggle for N phrases -> voice fingerprinting
const SPEAKER_MATCH_THRESHOLD = 0.55; // similarity >= this -> "Me" (You:)
const SPEAKER_DIST_SCALE = 0.5;    // vocal-profile distance that maps to 0 similarity

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

// Compare two {pitch,pace,energy} 0..100 profiles -> similarity 0..1.
const profileSimilarity = (a, b) => {
  if (!a || !b) return 0;
  const d = Math.sqrt(
    (((a.pitch || 0) - (b.pitch || 0)) / 100) ** 2
    + (((a.pace || 0) - (b.pace || 0)) / 100) ** 2
    + (((a.energy || 0) - (b.energy || 0)) / 100) ** 2
  ) / Math.sqrt(3);
  return Math.max(0, Math.min(1, 1 - d / SPEAKER_DIST_SCALE));
};
const emaProfile = (prev, cur, k) => ({
  pitch: prev.pitch + (cur.pitch - prev.pitch) * k,
  pace: prev.pace + (cur.pace - prev.pace) * k,
  energy: prev.energy + (cur.energy - prev.energy) * k,
});
// Map a value in [inLo, inHi] onto 0..100 with a log curve (good for pitch/Hz).
const mapLog100 = (v, inLo, inHi) => {
  if (!(v > 0)) return 0;
  const t01 = (Math.log(clamp(v, inLo, inHi)) - Math.log(inLo)) / (Math.log(inHi) - Math.log(inLo));
  return clamp(t01 * 100, 0, 100);
};
const fmtClock = (s) => {
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}`;
};
const capitalizeFirst = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);

function VocalSignal({ meta, value, lang, active }) {
  const v = clamp(Math.round(value || 0), 0, 100);
  const tier = signalTier(v);
  const color = SIGNAL_COLORS[tier];
  return (
    <div className={`lc-signal${active ? ' lc-signal--active' : ''}`}>
      <div className="lc-signal-head">
        <span className="lc-signal-icon" aria-hidden="true">{meta.icon}</span>
        <span className="lc-signal-name">{meta.label[lang]}</span>
        <span className="lc-signal-val" style={{ color }}>{v}</span>
        <span className="lc-signal-state" style={{ color }}>{SIGNAL_STATE[tier][lang]}</span>
      </div>
      <div className="lc-signal-track">
        <div className="lc-signal-fill" style={{ width: `${v}%`, background: color }} />
      </div>
    </div>
  );
}

// SVG close-probability ring — smoothly animates via stroke-dashoffset.
function ProbRing({ value, color, label, unit }) {
  const R = 46;
  const C = 2 * Math.PI * R;
  const v = clamp(value || 0, 0, 10);
  return (
    <div className="lc-ring">
      <svg viewBox="0 0 112 112" width="112" height="112" aria-hidden="true">
        <circle className="lc-ring-bg" cx="56" cy="56" r={R} />
        <circle
          className="lc-ring-fg"
          cx="56"
          cy="56"
          r={R}
          style={{ stroke: color, strokeDasharray: C, strokeDashoffset: C * (1 - v / 10) }}
        />
      </svg>
      <div className="lc-ring-inner">
        <span className="lc-ring-num" style={{ color }}>{label}</span>
        <span className="lc-ring-unit">{unit}</span>
      </div>
    </div>
  );
}

function LiveCoaching({ lang }) {
  const L = t[lang];
  const spkLabel = (m) => L[`spk_${m}`] || m;

  const [recording, setRecording] = useState(false);
  const [micState, setMicState] = useState('idle');   // idle | requesting | live | denied  (vocal-meter mic)
  const [sttState, setSttState] = useState(SPEECH_SUPPORTED ? 'idle' : 'unsupported'); // idle | listening | error | unsupported
  const [elapsed, setElapsed] = useState(0);
  const [phrases, setPhrases] = useState([]); // { id, speaker, text, sttConf, auto, autoConf }
  const [interim, setInterim] = useState('');
  const [speakerMode, setSpeakerMode] = useState('me'); // manual selection for incoming phrases
  const [autoMode, setAutoMode] = useState(false);       // voice fingerprinting active
  const [meReady, setMeReady] = useState(false);         // a "Me" voice profile has been captured
  const [phrasesSinceToggle, setPhrasesSinceToggle] = useState(0);
  const [lastConf, setLastConf] = useState(null);       // STT confidence, 0..100 | null
  const [confHistory, setConfHistory] = useState([]);   // per-phrase STT confidence
  const [result, setResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisCount, setAnalysisCount] = useState(0);
  const [lastAnalyzedWords, setLastAnalyzedWords] = useState(0);
  const [latency, setLatency] = useState(null); // { api, render, total, avgApi, avgTotal, n }
  const [updatedAt, setUpdatedAt] = useState(null);
  const [error, setError] = useState(null);
  const [vocals, setVocals] = useState({ pitch: 34, pace: 30, energy: 8, breathing: 46 });
  const [displayProb, setDisplayProb] = useState(0);
  const [context, setContext] = useState(makeContext);
  const [leadResult, setLeadResult] = useState(null);   // /analyze on the counterparty's lines
  const [liveSegs, setLiveSegs] = useState([]);          // real-time session-flow timeline
  const [whisperState, setWhisperState] = useState('idle'); // off | idle | transcribing | error
  const [whisperSegs, setWhisperSegs] = useState(0);        // Whisper segments finalized this session
  const [finalizing, setFinalizing] = useState(false);      // STOP -> flushing the tail segment

  // --- live Whisper transcription refs (FAZA 23.2) ---
  const recorderMimeRef = useRef('');
  const mediaRecorderRef = useRef(null);
  const segTimerRef = useRef(null);
  const segSpeakerRef = useRef('me');            // speaker captured at segment start
  const whisperQueueRef = useRef([]);            // [{ blob, speaker }]
  const whisperBusyRef = useRef(false);
  const whisperOnRef = useRef(false);            // segment loop should keep rotating

  const recognitionRef = useRef(null);
  const leadTextRef = useRef('');
  const liveSegRef = useRef([]);
  const restartWantedRef = useRef(false);
  const restartTimerRef = useRef(null);
  const langRef = useRef(lang);
  langRef.current = lang;

  const streamRef = useRef(null);
  const audioCtxRef = useRef(null);
  const analyserRef = useRef(null);
  const rafRef = useRef(null);
  const streamElRef = useRef(null);
  const lastWordsRef = useRef(0);        // "your" word count at the last completed analysis
  const inFlightRef = useRef(false);     // an /analyze request is currently open
  const pendingMeasureRef = useRef(null);// { started, apiMs } awaiting a render measurement
  const latSamplesRef = useRef([]);      // rolling latency samples
  const smoothRef = useRef({ pitch: 34, pace: 30, energy: 8, breathing: 46 });
  const displayProbRef = useRef(0);
  displayProbRef.current = displayProb;

  // --- speaker-detection refs (read inside the recognition closure) ---
  const speakerModeRef = useRef('me');
  const autoModeRef = useRef(false);
  const meProfileRef = useRef(null);          // { pitch, pace, energy } — the user's voice fingerprint
  const sinceToggleRef = useRef(0);           // final phrases since the last manual toggle
  const phraseAccumRef = useRef({ pitch: 0, pace: 0, energy: 0, n: 0 }); // vocal average for the phrase in progress
  const analysisTextRef = useRef('');

  // Text fed to /analyze = only the "Me" (You:) lines.
  const analysisText = useMemo(
    () => phrases.filter((p) => p.speaker === 'me').map((p) => p.text).join(' '),
    [phrases]
  );
  analysisTextRef.current = analysisText;
  // Counterparty lines feed a second /analyze -> party B read.
  const leadText = useMemo(
    () => phrases.filter((p) => p.speaker === 'lead').map((p) => p.text).join(' '),
    [phrases]
  );
  leadTextRef.current = leadText;
  const youWordCount = useMemo(
    () => (analysisText.trim() ? analysisText.trim().split(/\s+/).length : 0),
    [analysisText]
  );
  const totalWordCount = useMemo(
    () => phrases.reduce((n, p) => n + (p.text.trim() ? p.text.trim().split(/\s+/).length : 0), 0),
    [phrases]
  );
  const wordsSinceAnalysis = Math.max(0, youWordCount - lastAnalyzedWords);
  const avgConf = useMemo(
    () => (confHistory.length
      ? Math.round(confHistory.reduce((a, b) => a + b, 0) / confHistory.length)
      : null),
    [confHistory]
  );

  const targetProb = result ? toProb10(result.close_probability) : null;
  const probCol = probColor(result ? displayProb : null);

  const { fmap, ranked } = useMemo(() => rankFrameworks(result), [result]);
  const topThree = useMemo(
    () => ranked
      .slice(0, 3)
      .map((k) => ({ meta: FRAMEWORKS.find((f) => f.key === k), pct: toPct(fmap[k]?.confidence) }))
      .filter((x) => x.meta),
    [ranked, fmap]
  );
  const tips = useMemo(() => {
    if (!result) return [];
    const out = [];
    const overall = loc(result.coaching, lang);
    if (overall) out.push({ key: '_overall', icon: '\u{1F3AF}', text: overall });
    ranked.slice(0, 3).forEach((k) => {
      const meta = FRAMEWORKS.find((f) => f.key === k);
      const s = loc(fmap[k]?.suggestion, lang);
      if (meta && s) out.push({ key: k, icon: meta.icon, text: s });
    });
    return out;
  }, [result, ranked, fmap, lang]);

  // Per-party read (Me = A, Lead = B) — 10-framework verbal only + 3-tier output.
  const partyReads = useMemo(() => {
    const out = [];
    if (result) {
      const p = context.parties[0] || { id: 'A', label: 'A', role: '' };
      const pd = {
        id: p.id, label: p.label || 'A', role: p.role || '',
        objective: context.objectives[p.id] || '', verbal: result, nv: null, pv: null,
      };
      const prof = deriveProfile(pd, lang);
      out.push({ pd, prof, tiers: deriveTiers(pd, prof, lang), index: 0 });
    }
    if (leadResult) {
      const p = context.parties[1] || { id: 'B', label: 'B', role: '' };
      const pd = {
        id: p.id, label: p.label || 'B', role: p.role || '',
        objective: context.objectives[p.id] || '', verbal: leadResult, nv: null, pv: null,
      };
      const prof = deriveProfile(pd, lang);
      out.push({ pd, prof, tiers: deriveTiers(pd, prof, lang), index: 1 });
    }
    return out;
  }, [result, leadResult, context, lang]);

  /* ---- close-probability number tween (snappy, so frequent updates stay smooth) ---- */
  useEffect(() => {
    if (targetProb == null) return undefined;
    const from = displayProbRef.current;
    const startT = performance.now();
    const dur = 420;
    let raf;
    const step = (now) => {
      const p = Math.min(1, (now - startT) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      setDisplayProb(from + (targetProb - from) * eased);
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    // safety net: land on the exact value even if rAF is throttled (hidden tab)
    const settle = setTimeout(() => setDisplayProb(targetProb), dur + 80);
    return () => { cancelAnimationFrame(raf); clearTimeout(settle); };
  }, [targetProb]);

  /* ---- elapsed timer ---- */
  useEffect(() => {
    if (!recording) return undefined;
    const id = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, [recording]);

  /* ---- keep the transcript scrolled to the newest line ---- */
  useEffect(() => {
    const el = streamElRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [phrases.length, interim]);

  /* ---- fast analysis loop: tick every 4s, but only call /analyze once
         >20 new "your" words have landed (debounce). Measures API + UI latency. ---- */
  const runAnalysis = useCallback(async (opts = {}) => {
    if (inFlightRef.current) return;                       // never overlap requests
    const text = analysisTextRef.current.trim();
    const words = text ? text.split(/\s+/).length : 0;
    const isFirst = lastWordsRef.current === 0;
    const grew = words - lastWordsRef.current;
    if (!opts.force) {
      if (isFirst ? words < FIRST_ANALYSIS_MIN_WORDS : grew < WORD_DELTA_TRIGGER) return;
    }

    inFlightRef.current = true;
    lastWordsRef.current = words;
    setLastAnalyzedWords(words);
    setAnalyzing(true);
    setError(null);

    const tStart = performance.now();
    try {
      const data = await postAnalyze(text);
      const apiMs = performance.now() - tStart;
      pendingMeasureRef.current = { started: performance.now(), apiMs };
      setResult(data);
      setUpdatedAt(new Date());
      setAnalysisCount((n) => n + 1);

      // real-time session-flow timeline segment
      const sc = clamp(Math.round((toProb10(data.close_probability) || 0) * 10), 0, 100);
      liveSegRef.current = [...liveSegRef.current.slice(-39), sc];
      const n = liveSegRef.current.length;
      setLiveSegs(liveSegRef.current.map((s, i) => ({
        t0: i / n, t1: (i + 1) / n, score: s, color: signalColor(s),
      })));

      // counterparty (party B) read — non-blocking
      const lt = leadTextRef.current.trim();
      if (lt.split(/\s+/).filter(Boolean).length >= 8) {
        postAnalyze(lt).then(setLeadResult).catch(() => {});
      }
    } catch (err) {
      setError(`${L.error} ${err.message}`);
      console.error('[SANTINEL live] analysis error:', err);
    } finally {
      inFlightRef.current = false;
      setAnalyzing(false);
    }
  }, [L.error]);

  useEffect(() => {
    if (!recording) return undefined;
    const first = setTimeout(() => runAnalysis(), FIRST_ANALYSIS_DELAY_MS);
    const loop = setInterval(() => runAnalysis(), ANALYSIS_TICK_MS);
    return () => { clearTimeout(first); clearInterval(loop); };
  }, [recording, runAnalysis]);

  /* ---- latency measurement: API time + time-to-paint (post-paint useEffect) ---- */
  useEffect(() => {
    const p = pendingMeasureRef.current;
    if (!p) return;
    pendingMeasureRef.current = null;
    const renderMs = performance.now() - p.started;
    const total = p.apiMs + renderMs;
    const arr = latSamplesRef.current;
    arr.push({ api: p.apiMs, render: renderMs, total });
    if (arr.length > 20) arr.shift();
    const avg = (sel) => arr.reduce((s, x) => s + x[sel], 0) / arr.length;
    setLatency({
      api: Math.round(p.apiMs),
      render: Math.round(renderMs),
      total: Math.round(total),
      avgApi: Math.round(avg('api')),
      avgTotal: Math.round(avg('total')),
      n: arr.length,
    });
    console.log(
      `[SANTINEL live] api=${p.apiMs.toFixed(0)}ms ui=${renderMs.toFixed(0)}ms `
      + `perceived=${total.toFixed(0)}ms | avg api=${avg('api').toFixed(0)} `
      + `perceived=${avg('total').toFixed(0)} (n=${arr.length}, target<${LATENCY_TARGET_MS}ms)`
    );
  }, [result]);

  /* ---- vocal meters from the live microphone (also feeds the per-phrase profile) ---- */
  const feedPhraseProfile = (s) => {
    const acc = phraseAccumRef.current;
    acc.pitch += s.pitch;
    acc.pace += s.pace;
    acc.energy += s.energy;
    acc.n += 1;
  };

  const startVocalLoop = useCallback(() => {
    const analyser = analyserRef.current;
    if (!analyser) return;
    const timeBuf = new Uint8Array(analyser.fftSize);
    const freqBuf = new Uint8Array(analyser.frequencyBinCount);
    const nyquist = (audioCtxRef.current?.sampleRate || 44100) / 2;
    let lastPace = performance.now();
    let onsets = 0;
    let voicePrev = false;

    const tick = () => {
      analyser.getByteTimeDomainData(timeBuf);
      analyser.getByteFrequencyData(freqBuf);

      let sumSq = 0;
      for (let i = 0; i < timeBuf.length; i += 1) {
        const x = (timeBuf[i] - 128) / 128;
        sumSq += x * x;
      }
      const rms = Math.sqrt(sumSq / timeBuf.length);
      const energy = clamp(rms * 340, 0, 100);

      let mag = 0;
      let wsum = 0;
      for (let i = 0; i < freqBuf.length; i += 1) {
        mag += freqBuf[i];
        wsum += freqBuf[i] * i;
      }
      const centroidHz = mag > 0 ? (wsum / mag) / freqBuf.length * nyquist : 0;
      const pitch = mag > 4 ? mapLog100(centroidHz, 150, 2200) : smoothRef.current.pitch * 0.94;

      const voiceOn = energy > 12;
      if (voiceOn && !voicePrev) onsets += 1;
      voicePrev = voiceOn;
      const now = performance.now();
      let pace = smoothRef.current.pace;
      if (now - lastPace > 1400) {
        const perSec = onsets / ((now - lastPace) / 1000);
        pace = clamp(perSec * 24, 0, 100);
        onsets = 0;
        lastPace = now;
      }

      const breathing = clamp(52 + Math.sin(now / 3200) * 20 - (energy > 32 ? 10 : 0), 8, 96);

      const s = smoothRef.current;
      s.energy += (energy - s.energy) * 0.22;
      s.pitch += (pitch - s.pitch) * 0.12;
      s.pace += (pace - s.pace) * 0.09;
      s.breathing += (breathing - s.breathing) * 0.07;
      if (energy > 10) feedPhraseProfile(s);   // only sample while there is voice
      setVocals({
        pitch: Math.round(s.pitch),
        pace: Math.round(s.pace),
        energy: Math.round(s.energy),
        breathing: Math.round(s.breathing),
      });
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
  }, []);

  /* ---- simulated vocal meters when the meter-mic is unavailable ---- */
  useEffect(() => {
    if (!recording || micState === 'live') return undefined;
    let target = simulateVocals(displayProbRef.current);
    const retarget = setInterval(() => { target = simulateVocals(displayProbRef.current); }, 2400);
    const anim = setInterval(() => {
      setVocals((v) => {
        const next = {
          pitch: v.pitch + (target.pitch - v.pitch) * 0.12,
          pace: v.pace + (target.pace - v.pace) * 0.12,
          energy: v.energy + (target.energy - v.energy) * 0.18,
          breathing: v.breathing + (target.breathing - v.breathing) * 0.1,
        };
        smoothRef.current = { ...next };
        feedPhraseProfile(next);
        return next;
      });
    }, 110);
    return () => { clearInterval(retarget); clearInterval(anim); };
  }, [recording, micState]);

  /* ================= Web Speech API ================= */
  const stopRecognition = useCallback(() => {
    restartWantedRef.current = false;
    if (restartTimerRef.current) {
      clearTimeout(restartTimerRef.current);
      restartTimerRef.current = null;
    }
    const rec = recognitionRef.current;
    if (rec) {
      rec.onresult = null;
      rec.onerror = null;
      rec.onend = null;
      try { rec.stop(); } catch (e) { /* not running */ }
    }
    recognitionRef.current = null;
    setInterim('');
  }, []);

  const startRecognition = useCallback(() => {
    if (!SPEECH_SUPPORTED) { setSttState('unsupported'); return; }
    stopRecognition();
    let rec;
    try {
      rec = new SpeechRecognitionCtor();
    } catch (e) {
      console.warn('SpeechRecognition init failed:', e);
      setSttState('error');
      return;
    }
    rec.lang = langRef.current === 'ro' ? 'ro-RO' : 'en-US';
    rec.continuous = true;
    rec.interimResults = true;
    rec.maxAlternatives = 1;

    rec.onstart = () => setSttState('listening');

    rec.onresult = (event) => {
      let interimText = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const res = event.results[i];
        const alt = res[0];
        if (!alt) continue;
        if (res.isFinal) {
          const phrase = (alt.transcript || '').trim();
          if (!phrase) continue;
          const sttConf = typeof alt.confidence === 'number' && alt.confidence > 0
            ? clamp(Math.round(alt.confidence * 100), 1, 100)
            : null;

          // vocal fingerprint for this phrase
          const acc = phraseAccumRef.current;
          const prof = acc.n > 0
            ? { pitch: acc.pitch / acc.n, pace: acc.pace / acc.n, energy: acc.energy / acc.n }
            : { pitch: smoothRef.current.pitch, pace: smoothRef.current.pace, energy: smoothRef.current.energy };
          phraseAccumRef.current = { pitch: 0, pace: 0, energy: 0, n: 0 };

          // decide the speaker
          let speaker = speakerModeRef.current;
          let auto = false;
          let autoConf = null;
          if (autoModeRef.current && meProfileRef.current) {
            const sim = profileSimilarity(prof, meProfileRef.current);
            auto = true;
            if (sim >= SPEAKER_MATCH_THRESHOLD) { speaker = 'me'; autoConf = Math.round(sim * 100); }
            else { speaker = 'lead'; autoConf = Math.round((1 - sim) * 100); }
          }

          // learn / refine the "Me" fingerprint from confirmed-me phrases
          if (speaker === 'me') {
            if (!meProfileRef.current) {
              meProfileRef.current = prof;
              setMeReady(true);
            } else {
              meProfileRef.current = emaProfile(meProfileRef.current, prof, 0.3);
            }
          }

          // after N phrases with no manual toggle, switch to voice fingerprinting
          sinceToggleRef.current += 1;
          setPhrasesSinceToggle(sinceToggleRef.current);
          if (!autoModeRef.current
              && sinceToggleRef.current >= AUTO_AFTER_PHRASES
              && meProfileRef.current) {
            autoModeRef.current = true;
            setAutoMode(true);
          }

          setLastConf(sttConf);
          setConfHistory((h) => [...h.slice(-23), sttConf == null ? 0 : sttConf]);
          setPhrases((prev) => [...prev, {
            id: `p${prev.length}-${Math.round(performance.now())}`,
            speaker,
            text: capitalizeFirst(phrase) + (/[.!?]$/.test(phrase) ? '' : '.'),
            sttConf,
            auto,
            autoConf,
            // Web Speech gives instant captions; a Whisper segment supersedes these
            // (unless Whisper is off/errored, in which case they stand).
            engine: 'web',
            provisional: whisperOnRef.current,
          }]);
        } else {
          interimText += alt.transcript;
        }
      }
      setInterim(interimText.trim());
    };

    rec.onerror = (event) => {
      const err = event && event.error;
      if (err === 'not-allowed' || err === 'service-not-allowed') {
        restartWantedRef.current = false;
        setSttState('error');
      } else if (err === 'no-speech' || err === 'aborted') {
        // benign — onend will restart if we still want to listen
      } else if (err) {
        console.warn('SpeechRecognition error:', err);
      }
    };

    rec.onend = () => {
      setInterim('');
      if (restartWantedRef.current) {
        restartTimerRef.current = setTimeout(() => {
          const r = recognitionRef.current;
          if (r && restartWantedRef.current) {
            try { r.start(); } catch (e) { /* already started */ }
          }
        }, 300);
      } else {
        setSttState((prev) => (prev === 'error' || prev === 'unsupported' ? prev : 'idle'));
      }
    };

    recognitionRef.current = rec;
    restartWantedRef.current = true;
    try {
      rec.start();
    } catch (e) {
      console.warn('SpeechRecognition start failed:', e);
    }
  }, [stopRecognition]);

  // Language change while recording -> bounce recognition to pick up the new locale.
  useEffect(() => {
    const rec = recognitionRef.current;
    if (recording && rec && SPEECH_SUPPORTED) {
      rec.lang = lang === 'ro' ? 'ro-RO' : 'en-US';
      try { rec.stop(); } catch (e) { /* onend restarts with the new lang */ }
    }
  }, [lang, recording]);

  /* ---- teardown ---- */
  const teardownAudio = useCallback(() => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    whisperOnRef.current = false;
    if (segTimerRef.current) { clearTimeout(segTimerRef.current); segTimerRef.current = null; }
    const mr = mediaRecorderRef.current;
    if (mr && mr.state !== 'inactive') { try { mr.stop(); } catch (e) { /* already stopped */ } }
    mediaRecorderRef.current = null;
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((tr) => tr.stop());
      streamRef.current = null;
    }
    if (audioCtxRef.current) {
      audioCtxRef.current.close().catch(() => {});
      audioCtxRef.current = null;
    }
    analyserRef.current = null;
  }, []);

  useEffect(() => () => {
    stopRecognition();
    teardownAudio();
  }, [stopRecognition, teardownAudio]);

  /* ---- speaker controls ---- */
  const chooseSpeaker = (mode) => {
    setSpeakerMode(mode);
    speakerModeRef.current = mode;
    // manual override always wins: drop auto mode and restart the arming countdown
    if (autoModeRef.current) { autoModeRef.current = false; setAutoMode(false); }
    sinceToggleRef.current = 0;
    setPhrasesSinceToggle(0);
  };

  const cyclePhraseSpeaker = (id) => {
    setPhrases((prev) => prev.map((p) => {
      if (p.id !== id) return p;
      const next = p.speaker === 'me' ? 'lead' : p.speaker === 'lead' ? 'note' : 'me';
      return { ...p, speaker: next, auto: false, autoConf: null };
    }));
  };

  /* ================= live Whisper transcription (FAZA 23.2) ================= */

  // Fold a finalized Whisper segment into the transcript: it supersedes the
  // trailing provisional Web-Speech phrases from the same ~4s window.
  const applyWhisperText = useCallback((rawText, speaker) => {
    const text = (rawText || '').trim();
    if (!text) return;
    const clean = capitalizeFirst(text) + (/[.!?]$/.test(text) ? '' : '.');
    setPhrases((prev) => {
      const kept = dropTrailingWhile(prev, (p) => p.provisional && p.engine === 'web');
      return [...kept, {
        id: `w${kept.length}-${Math.round(performance.now())}`,
        speaker: speaker || 'me',
        text: clean,
        sttConf: null,
        auto: false,
        autoConf: null,
        engine: 'whisper',
        provisional: false,
      }];
    });
    setWhisperSegs((n) => n + 1);
  }, []);

  const drainWhisperQueue = useCallback(async () => {
    if (whisperBusyRef.current) return;
    whisperBusyRef.current = true;
    try {
      while (whisperQueueRef.current.length) {
        const { blob, speaker } = whisperQueueRef.current.shift();
        setWhisperState('transcribing');
        try {
          const text = await postTranscribe(blob, langRef.current);
          if (text) applyWhisperText(text, speaker);
          setWhisperState((s) => (s === 'off' ? 'off' : 'idle'));
        } catch (err) {
          console.warn('[SANTINEL live] whisper segment failed:', err);
          setWhisperState('error');
        }
      }
    } finally {
      whisperBusyRef.current = false;
    }
  }, [applyWhisperText]);

  const enqueueWhisperBlob = useCallback((blob, speaker) => {
    if (!blob || blob.size < WHISPER_MIN_BLOB) return;
    const q = whisperQueueRef.current;
    q.push({ blob, speaker });
    while (q.length > WHISPER_MAX_QUEUE) q.shift();
    drainWhisperQueue();
  }, [drainWhisperQueue]);

  function rotateWhisperSegment() {
    const mr = mediaRecorderRef.current;
    mediaRecorderRef.current = null;
    if (mr && mr.state !== 'inactive') {
      try { mr.stop(); } catch (e) { /* ignore */ }   // -> ondataavailable enqueues the segment
    }
    if (whisperOnRef.current) startWhisperSegment();
  }

  function startWhisperSegment() {
    const stream = streamRef.current;
    if (!stream || !whisperOnRef.current) return;
    let mr;
    try {
      mr = recorderMimeRef.current
        ? new MediaRecorder(stream, { mimeType: recorderMimeRef.current })
        : new MediaRecorder(stream);
    } catch (e) {
      console.warn('MediaRecorder init failed:', e);
      whisperOnRef.current = false;
      setWhisperState('off');
      return;
    }
    const speakerAtStart = speakerModeRef.current;
    segSpeakerRef.current = speakerAtStart;
    mr.ondataavailable = (e) => {
      if (e.data && e.data.size > WHISPER_MIN_BLOB) enqueueWhisperBlob(e.data, speakerAtStart);
    };
    mr.onerror = () => { /* the next rotation makes a fresh recorder */ };
    mediaRecorderRef.current = mr;
    try {
      mr.start();
    } catch (e) {
      console.warn('MediaRecorder start failed:', e);
      whisperOnRef.current = false;
      setWhisperState('off');
      return;
    }
    segTimerRef.current = setTimeout(rotateWhisperSegment, WHISPER_SEG_MS);
  }

  // Stop the segment loop. flushTail=true waits (bounded) for the final segment
  // + queue to transcribe so STOP's analysis sees the complete transcript.
  const stopWhisperLoop = useCallback(async ({ flushTail } = {}) => {
    whisperOnRef.current = false;
    if (segTimerRef.current) { clearTimeout(segTimerRef.current); segTimerRef.current = null; }
    const mr = mediaRecorderRef.current;
    mediaRecorderRef.current = null;
    if (mr && mr.state !== 'inactive') {
      try { mr.stop(); } catch (e) { /* ignore */ }
    }
    if (!flushTail) { whisperQueueRef.current = []; return; }
    await new Promise((r) => setTimeout(r, 80));   // let the tail ondataavailable land
    drainWhisperQueue();
    const deadline = performance.now() + WHISPER_FINALIZE_MS;
    while ((whisperQueueRef.current.length || whisperBusyRef.current)
           && performance.now() < deadline) {
      await new Promise((r) => setTimeout(r, 120));
    }
    whisperQueueRef.current = [];
  }, [drainWhisperQueue]);

  const startRecording = async () => {
    setError(null);
    setPhrases([]);
    setInterim('');
    setResult(null);
    setLeadResult(null);
    setLiveSegs([]);
    liveSegRef.current = [];
    setAnalysisCount(0);
    setLastAnalyzedWords(0);
    setLatency(null);
    setElapsed(0);
    setDisplayProb(0);
    setLastConf(null);
    setConfHistory([]);
    setSpeakerMode('me');
    setAutoMode(false);
    setMeReady(false);
    setPhrasesSinceToggle(0);
    setWhisperSegs(0);
    setWhisperState('idle');
    setFinalizing(false);
    whisperQueueRef.current = [];
    whisperBusyRef.current = false;
    whisperOnRef.current = false;
    lastWordsRef.current = 0;
    inFlightRef.current = false;
    pendingMeasureRef.current = null;
    latSamplesRef.current = [];
    smoothRef.current = { pitch: 34, pace: 30, energy: 8, breathing: 46 };
    speakerModeRef.current = 'me';
    autoModeRef.current = false;
    meProfileRef.current = null;
    sinceToggleRef.current = 0;
    phraseAccumRef.current = { pitch: 0, pace: 0, energy: 0, n: 0 };

    // 1) microphone for the vocal meters + fingerprint (independent of speech recognition)
    setMicState('requesting');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const Ctx = window.AudioContext || window.webkitAudioContext;
      const ctx = new Ctx();
      audioCtxRef.current = ctx;
      if (ctx.state === 'suspended') ctx.resume().catch(() => {});
      const srcNode = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 1024;
      analyser.smoothingTimeConstant = 0.82;
      srcNode.connect(analyser);
      analyserRef.current = analyser;
      setMicState('live');
      startVocalLoop();
    } catch (err) {
      console.warn('Meter microphone unavailable:', err);
      setMicState('denied');
    }

    // 1b) live Whisper transcription — reuse the meter stream (no second prompt)
    if (streamRef.current && typeof MediaRecorder !== 'undefined') {
      recorderMimeRef.current = pickRecorderMime();
      whisperOnRef.current = true;
      setWhisperState('idle');
      startWhisperSegment();
    } else {
      whisperOnRef.current = false;
      setWhisperState('off');
    }

    // 2) instant captions via Web Speech (Whisper segments supersede these)
    if (SPEECH_SUPPORTED) startRecognition();
    else setSttState('unsupported');

    setRecording(true);
  };

  const stopRecording = async () => {
    setRecording(false);
    stopRecognition();
    setSttState(SPEECH_SUPPORTED ? 'idle' : 'unsupported');

    // finalize the transcript: flush the tail Whisper segment before analyzing
    if (whisperOnRef.current || mediaRecorderRef.current || whisperQueueRef.current.length) {
      setFinalizing(true);
      try { await stopWhisperLoop({ flushTail: true }); } catch (e) { /* ignore */ }
      setWhisperState((s) => (s === 'off' ? 'off' : 'idle'));
    }

    setMicState('idle');
    teardownAudio();

    // one forced full analysis on the complete transcript (both parties, 3-tier)
    for (let i = 0; i < 25 && inFlightRef.current; i += 1) {
      await new Promise((r) => setTimeout(r, 100));
    }
    await new Promise((r) => setTimeout(r, 0));   // let the final setPhrases flush to the memo
    if (analysisTextRef.current.trim()) {
      try { await runAnalysis({ force: true }); } catch (e) { /* runAnalysis surfaces its own errors */ }
    }
    setFinalizing(false);
  };

  const downloadTranscript = () => {
    if (!phrases.length) return;
    const body = phrases.map((p) => `${spkLabel(p.speaker)}: ${p.text}`).join('\n');
    const blob = new Blob([body], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `santinel-transcript-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const statusKey = !recording ? 'idle' : (sttState === 'listening' ? 'live' : 'demo');
  const statusLabel = !recording
    ? L.coachingIdle
    : sttState === 'listening'
      ? L.listening
      : sttState === 'unsupported'
        ? L.speechUnsupportedShort
        : L.demoMode;
  const probLabel = result ? Math.round(displayProb) : '—';
  const confColorOf = (c) => (c == null ? 'var(--si-text-dim)' : confColor(c));

  const armProgress = autoMode
    ? L.autoOn
    : meReady
      ? `${Math.min(phrasesSinceToggle, AUTO_AFTER_PHRASES)}/${AUTO_AFTER_PHRASES} ${L.autoArming}`
      : L.autoNeedsMe;

  const whisperBadge = whisperState === 'off'
    ? L.whisperOffline
    : whisperState === 'error'
      ? L.whisperError
      : whisperState === 'transcribing'
        ? L.whisperTranscribing
        : whisperSegs > 0
          ? `${whisperSegs} ${L.whisperSegments}`
          : L.whisperReady;

  return (
    <div className="si-page lc">
      <div className="lc-head">
        <div>
          <h2 className="si-h2">{L.liveTitle}</h2>
          <p className="lc-sub">{L.liveSubtitle}</p>
        </div>
        <div className={`lc-status lc-status--${statusKey}`}>
          <span className="lc-status-dot" />
          {statusLabel}
        </div>
      </div>

      <ContextBar context={context} setContext={setContext} lang={lang} />

      <div className="lc-split">
        {/* ---- left: speech recognition + speaker-tagged transcript ---- */}
        <section className="lc-pane">
          <div className="lc-pane-head">
            <span className="si-field-label">{L.liveTranscript}</span>
            <div className="lc-meta-row">
              {recording && (
                <span className={`lc-rec lc-rec--${sttState === 'listening' ? 'live' : 'demo'}`}>
                  <span className="lc-rec-dot" />
                  {L.recording} · {fmtClock(elapsed)}
                </span>
              )}
              {lastConf != null && (
                <span className="lc-conf-chip" style={{ '--cc': confColorOf(lastConf) }}>
                  {L.phraseConfidence} {lastConf}%
                </span>
              )}
              {(recording || whisperSegs > 0) && (
                <span
                  className={`lc-eng-badge lc-eng-badge--${whisperState}`}
                  title={L.sttHybridNote}
                >
                  <span aria-hidden="true">{'\u{1F399}\u{FE0F}'}</span>
                  {' '}{L.whisperLabel} · {whisperBadge}
                </span>
              )}
              <button
                type="button"
                className="lc-download"
                onClick={downloadTranscript}
                disabled={!phrases.length}
              >
                {'↓'} {L.downloadTranscript}
              </button>
            </div>
          </div>

          {/* Who's speaking? segmented toggle */}
          <div className="lc-speaker-bar">
            <span className="si-field-label lc-speaker-label">{L.whoSpeaking}</span>
            <div className="lc-seg" role="group" aria-label={L.whoSpeaking}>
              {SPEAKER_MODES.map((m) => (
                <button
                  key={m}
                  type="button"
                  className={`lc-seg-btn lc-seg-btn--${m}${speakerMode === m && !autoMode ? ' is-active' : ''}`}
                  aria-pressed={speakerMode === m && !autoMode}
                  onClick={() => chooseSpeaker(m)}
                >
                  {spkLabel(m)}
                </button>
              ))}
            </div>
            <span className={`lc-auto-badge${autoMode ? ' is-on' : ''}`} title={L.autoDetected}>
              {autoMode && <span aria-hidden="true">🎯 </span>}{armProgress}
            </span>
          </div>

          {confHistory.length > 1 && (
            <div className="lc-conf-spark" title={avgConf != null ? `${L.avgConfidence} ${avgConf}%` : ''}>
              {confHistory.map((c, i) => (
                <i key={i} style={{ height: `${clamp(c, 6, 100)}%`, background: confColorOf(c || null) }} />
              ))}
              {avgConf != null && <span className="lc-conf-avg">{L.avgConfidence} {avgConf}%</span>}
            </div>
          )}

          <div className="lc-stream" ref={streamElRef} aria-live="polite">
            {phrases.length === 0 && !interim && (
              <div className="lc-stream-empty">
                {recording ? (
                  <span className="lc-listening"><i /><i /><i /> {L.speakNow}</span>
                ) : (
                  <p>{L.liveWaiting}</p>
                )}
              </div>
            )}
            {phrases.map((p) => (
              <div
                key={p.id}
                className={`lc-ph lc-ph--${p.speaker} lc-ph--in${p.provisional ? ' lc-ph--prov' : ''}`}
              >
                <button
                  type="button"
                  className="lc-ph-spk"
                  onClick={() => cyclePhraseSpeaker(p.id)}
                  title={L.reassign}
                >
                  {spkLabel(p.speaker)}
                </button>
                <span className="lc-ph-text">{p.text}</span>
                {p.engine === 'whisper' && (
                  <span className="lc-ph-eng" title={L.whisperLabel} aria-hidden="true">
                    {'\u{1F399}\u{FE0F}'}
                  </span>
                )}
                {p.auto && p.autoConf != null && (
                  <span className="lc-ph-auto" title={L.autoDetected}>{'\u{1F3AF}'} {p.autoConf}%</span>
                )}
              </div>
            ))}
            {interim && (
              <div className={`lc-ph lc-ph--${speakerMode} lc-ph--interim`}>
                <span className="lc-ph-spk">{spkLabel(speakerMode)}</span>
                <span className="lc-ph-text">{interim}<span className="lc-ph-caret" aria-hidden="true" /></span>
              </div>
            )}
          </div>

          <div className={`lc-interim-line${interim ? ' is-active' : ''}`} aria-live="polite">
            {sttState === 'unsupported' && whisperState !== 'off'
              ? <span className="lc-interim-msg">{L.webCaptionsOff}</span>
              : sttState === 'unsupported'
                ? <span className="lc-interim-msg">{L.speechUnsupported}</span>
                : interim
                  ? <><span className="lc-interim-mic" aria-hidden="true"><i /><i /><i /></span><span>{L.hearing}…</span></>
                  : recording && sttState === 'listening'
                    ? <span className="lc-interim-msg">{L.youLinesNote}</span>
                    : null}
          </div>

          <div className="lc-controls">
            {!recording ? (
              <button
                type="button"
                className="si-btn si-btn--primary lc-start"
                onClick={startRecording}
                disabled={micState === 'requesting' || finalizing}
              >
                {'\u{1F3A4}'} {micState === 'requesting' ? L.micRequesting : L.startRecording}
              </button>
            ) : (
              <button
                type="button"
                className="si-btn lc-stop"
                onClick={stopRecording}
                disabled={finalizing}
              >
                {'■'} {finalizing ? L.finalizingTranscript : L.stopRecording}
              </button>
            )}
            {finalizing && !recording && (
              <span className="lc-countdown lc-countdown--busy">⚡ {L.finalizingTranscript}</span>
            )}
            {recording && (
              <span className={`lc-countdown${analyzing ? ' lc-countdown--busy' : ''}`}>
                {analyzing
                  ? `⚡ ${L.analyzingLive}`
                  : `${Math.min(wordsSinceAnalysis, WORD_DELTA_TRIGGER)}/${WORD_DELTA_TRIGGER} ${L.yourWords} → ${L.nextAnalysis}`}
              </span>
            )}
            <span className="lc-wordcount">{youWordCount} {L.yourWords} · {totalWordCount} {L.wordCount}</span>
          </div>

          {sttState === 'unsupported' && !recording && (
            <div className="lc-hint">{L.speechUnsupported}</div>
          )}
          {sttState === 'error' && <div className="lc-hint">{L.speechDenied}</div>}
          {micState === 'denied' && <div className="lc-hint">{L.micDenied}</div>}
          {error && <div className="si-error">{error}</div>}
        </section>

        {/* ---- right: live coaching panel ---- */}
        <section className="lc-pane lc-pane--coach">
          <div className="lc-coach">
            <div className="lc-gauge-row">
              <ProbRing value={displayProb} color={probCol} label={probLabel} unit={L.outOf10} />
              <div className="lc-gauge-meta">
                <span className="si-field-label">{L.closeProbability}</span>
                <span className="lc-updated">
                  {updatedAt
                    ? `${L.lastUpdated} ${updatedAt.toLocaleTimeString(lang === 'ro' ? 'ro-RO' : 'en-US')}`
                    : (recording ? L.analyzingLive : L.liveWaiting)}
                </span>
                {analysisCount > 0 && (
                  <span className="lc-count-pill" key={analysisCount}>{analysisCount} {L.analysesDone}</span>
                )}
                {latency && (
                  <span
                    className="lc-latency"
                    data-good={latency.total <= LATENCY_TARGET_MS ? 'true' : 'false'}
                    title={`${L.avgConfidence} ${latency.avgTotal}ms · n=${latency.n}`}
                  >
                    {L.latency} {latency.total}ms
                    <span className="lc-latency-split">
                      API {latency.api} · UI {latency.render} · {L.avgConfidence} {latency.avgTotal}
                    </span>
                  </span>
                )}
              </div>
            </div>

            <div className="lc-block">
              <span className="si-field-label">{L.topTriggers}</span>
              {topThree.length ? (
                <ol className="si-triggers lc-triggers">
                  {topThree.map(({ meta, pct }, i) => (
                    <li
                      key={meta.key}
                      className="si-trigger"
                      style={{ '--g1': meta.gradient[0], '--g2': meta.gradient[1] }}
                    >
                      <span className="si-trigger-rank">{i + 1}</span>
                      <span className="si-trigger-icon" aria-hidden="true">{meta.icon}</span>
                      <span className="si-trigger-name">{meta.name[lang]}</span>
                      {pct != null && (
                        <span className="si-trigger-pct" style={{ color: confColor(pct) }}>{pct}%</span>
                      )}
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="lc-idle-note">{L.triggersIdle}</p>
              )}
            </div>

            <div className="lc-block">
              <span className="si-field-label">{L.vocalSignals}</span>
              <div className="lc-signals">
                {VOCAL_SIGNALS.map((m) => (
                  <VocalSignal key={m.key} meta={m} value={vocals[m.key]} lang={lang} active={recording} />
                ))}
              </div>
              <span className="lc-note">{micState === 'live' ? L.vocalLiveNote : L.vocalDemoNote}</span>
            </div>

            <div className="lc-block">
              <span className="si-field-label">{L.realtimeTips}</span>
              {tips.length ? (
                <ul className="lc-tips">
                  {tips.map((tip) => (
                    <li key={tip.key} className="lc-tip">
                      <span className="lc-tip-icon" aria-hidden="true">{tip.icon}</span>
                      {/* keyed by text so only a changed tip cross-fades — no full-list flash */}
                      <span key={tip.text} className="lc-tip-text">{tip.text}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="lc-idle-note">{L.tipsIdle}</p>
              )}
            </div>

            <div className="lc-block">
              <span className="si-field-label">{L.perPartyTitle}</span>
              <ContextFallbackNote context={context} lang={lang} />
              {liveSegs.length > 1 && (
                <FlowTimeline segments={liveSegs} lang={lang} label={L.tlLive} />
              )}
              {partyReads.length === 0 ? (
                <p className="lc-idle-note">{L.triggersIdle}</p>
              ) : (
                partyReads.map((pr) => (
                  <div key={pr.pd.id} className="lc-party" style={{ '--pc': partyColor(pr.index) }}>
                    <div className="lc-party-head">
                      <span className="lc-party-dot" />
                      <b>{pr.pd.label}</b>
                      <span
                        className="lc-party-prob"
                        style={{ color: probColor(toProb10(pr.pd.verbal.close_probability)) }}
                      >
                        {toProb10(pr.pd.verbal.close_probability) ?? '—'}/10
                      </span>
                    </div>
                    <TierTabs tiers={pr.tiers} lang={lang} />
                    {pr.pd.objective && pr.pd.objective.trim() && (
                      <p className="lc-party-obj">{'\u{1F3AF}'} {pr.pd.objective.trim()}</p>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}


/* -------------------------------------------------------------------------- */
/*  Video Analysis — real MediaPipe pose + face-mesh + live-audio paraverbal   */
/* -------------------------------------------------------------------------- */

const MP_VER = '0.10.14';
const MP_ESM = `https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@${MP_VER}/vision_bundle.mjs`;
const MP_WASM = `https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@${MP_VER}/wasm`;
const POSE_MODEL = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task';
const FACE_MODEL = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task';

const VIDEO_RATE = 1.75;       // playback speed for the analysis pass
const DETECT_GAP_S = 0.28;     // min video-time between MediaPipe detections
const PARA_GAP_S = 0.06;       // audio sample cadence

const _visionByCount = new Map();
// Load MediaPipe Tasks-Vision (pose + face-mesh) from CDN, once per subject count.
// -> { pose, face, loadMs, count }
async function loadVisionModels(count = 2) {
  const n = clamp(Math.round(count) || 1, 1, 4);
  if (_visionByCount.has(n)) return _visionByCount.get(n);
  const p = (async () => {
    const t0 = performance.now();
    const vision = await import(/* @vite-ignore */ MP_ESM);
    const { FilesetResolver, PoseLandmarker, FaceLandmarker } = vision;
    const fileset = await FilesetResolver.forVisionTasks(MP_WASM);
    const build = (delegate) => Promise.all([
      PoseLandmarker.createFromOptions(fileset, {
        baseOptions: { modelAssetPath: POSE_MODEL, delegate },
        runningMode: 'VIDEO',
        numPoses: n,
      }),
      FaceLandmarker.createFromOptions(fileset, {
        baseOptions: { modelAssetPath: FACE_MODEL, delegate },
        runningMode: 'VIDEO',
        numFaces: n,
        outputFaceBlendshapes: true,
        outputFacialTransformationMatrixes: true,
      }),
    ]);
    let pair;
    try { pair = await build('GPU'); }
    catch (e) { console.warn('[SANTINEL video] GPU delegate failed -> CPU', e); pair = await build('CPU'); }
    return { pose: pair[0], face: pair[1], loadMs: performance.now() - t0, count: n };
  })().catch((e) => { _visionByCount.delete(n); throw e; });
  _visionByCount.set(n, p);
  return p;
}

const POSE_BONES = [
  [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
  [11, 23], [12, 24], [23, 24], [23, 25], [24, 26], [25, 27], [26, 28],
];
const dist2 = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
const mid = (a, b) => ({ x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 });
const bcat = (cats, name) => {
  const c = cats && cats.find((x) => x.categoryName === name);
  return c ? c.score : 0;
};
const meanBy = (arr, f) => (arr.length ? arr.reduce((s, x) => s + f(x), 0) / arr.length : 0);
const stdevBy = (arr, f) => {
  if (arr.length < 2) return 0;
  const m = meanBy(arr, f);
  return Math.sqrt(arr.reduce((s, x) => s + (f(x) - m) ** 2, 0) / arr.length);
};

// Pose (33 normalised landmarks) -> posture / openness / gesture anchors.
function readPose(lm) {
  if (!lm || lm.length < 29) return null;
  const shMid = mid(lm[11], lm[12]);
  const hipMid = mid(lm[23], lm[24]);
  const shW = Math.max(0.05, dist2(lm[11], lm[12]));
  const earMid = mid(lm[7], lm[8]);
  const torsoDx = shMid.x - hipMid.x;
  const torsoDy = Math.max(0.01, hipMid.y - shMid.y);
  const leanDeg = Math.abs(Math.atan2(torsoDx, torsoDy) * 180 / Math.PI);
  const wristSpread = (Math.abs(lm[15].x - shMid.x) + Math.abs(lm[16].x - shMid.x)) / (2 * shW);
  const wristsHigh = (lm[15].y < hipMid.y) && (lm[16].y < hipMid.y);
  const crossed = wristsHigh
    && Math.abs(lm[15].x - shMid.x) < shW * 0.6
    && Math.abs(lm[16].x - shMid.x) < shW * 0.6
    && ((lm[15].x - lm[16].x) * (lm[11].x - lm[12].x) < 0);
  const shoulderRaise = clamp(1 - (shMid.y - earMid.y) / (shW * 1.1), 0, 1);
  return {
    leanDeg,
    openness: clamp((wristSpread - 0.6) / 1.4, 0, 1),
    defensive: crossed ? clamp(0.6 + shoulderRaise * 0.4, 0, 1) : clamp(shoulderRaise * 0.5, 0, 1),
    tension: shoulderRaise,
    wristL: { x: lm[15].x, y: lm[15].y },
    wristR: { x: lm[16].x, y: lm[16].y },
    centroid: mid(shMid, hipMid),
  };
}

// Face (478 landmarks) + 52 blendshapes + head matrix -> expression / gaze / eye-contact.
function readFace(lm, cats, matrix) {
  if (!lm || lm.length < 468) return null;
  const smile = (bcat(cats, 'mouthSmileLeft') + bcat(cats, 'mouthSmileRight')) / 2;
  const browDown = (bcat(cats, 'browDownLeft') + bcat(cats, 'browDownRight')) / 2;
  const browUp = (bcat(cats, 'browInnerUp') + bcat(cats, 'browOuterUpLeft') + bcat(cats, 'browOuterUpRight')) / 3;
  const squint = (bcat(cats, 'eyeSquintLeft') + bcat(cats, 'eyeSquintRight')) / 2;
  const blink = (bcat(cats, 'eyeBlinkLeft') + bcat(cats, 'eyeBlinkRight')) / 2;
  const press = (bcat(cats, 'mouthPressLeft') + bcat(cats, 'mouthPressRight')) / 2;
  const eyeOpen = clamp(1 - blink, 0, 1);
  const engagement = clamp(eyeOpen * 0.45 + browUp * 0.3 + smile * 0.25, 0, 1);
  const tensionF = clamp(browDown * 0.45 + squint * 0.3 + press * 0.25, 0, 1);

  let yaw = 0;
  let pitch = 0;
  if (matrix && matrix.length >= 12) {
    yaw = Math.atan2(matrix[8], matrix[10]) * 180 / Math.PI;
    pitch = Math.atan2(-matrix[9], Math.hypot(matrix[8], matrix[10])) * 180 / Math.PI;
  } else if (lm.length > 454) {
    const faceW = Math.max(0.05, Math.abs(lm[234].x - lm[454].x));
    yaw = ((lm[454].x - lm[1].x) - (lm[1].x - lm[234].x)) / faceW * 60;
  }
  let irisOff = 0;
  if (lm.length >= 478) {
    const rW = Math.max(0.01, Math.abs(lm[33].x - lm[133].x));
    const lW = Math.max(0.01, Math.abs(lm[362].x - lm[263].x));
    irisOff = (lm[468].x - (lm[33].x + lm[133].x) / 2) / rW
      + (lm[473].x - (lm[362].x + lm[263].x) / 2) / lW;
  }
  const eyeContact = Math.abs(yaw) < 16 && Math.abs(pitch) < 14 && Math.abs(irisOff) < 0.22 && eyeOpen > 0.35;
  return { smile, engagement, tension: tensionF, eyeOpen, yaw, pitch, irisOff, eyeContact };
}

// Transparent 0..100 coaching signal for a slice of the timeline.
function scoreSlice(a) {
  let s = 50;
  s += (a.openness - 0.35) * 26;
  s -= a.defensive * 24;
  s += (a.smile - 0.15) * 16;
  s += a.engagement * 14;
  s -= a.faceTension * 20;
  s += (a.eyeContact - 0.4) * 22;
  s -= Math.max(0, a.movement - 0.05) * 120;
  s -= Math.abs(a.gesture - 0.04) * 90;
  if (a.para) {
    s += (a.para.volNorm - 0.35) * 8;
    s -= Math.max(0, a.para.volVar - 0.25) * 20;
    s += Math.min(a.para.pitchVar, 0.3) * 18;
    s -= Math.max(0, a.para.pitchVar - 0.45) * 24;
  }
  return clamp(Math.round(s), 0, 100);
}
const signalColor = (s) => (s >= 62 ? '#10b981' : s >= 38 ? '#f59e0b' : '#ef4444');

/* -------------------------------------------------------------------------- */
/*  Video Analysis — multi-party: context, transcript diarisation, per-party   */
/*  MediaPipe (pose + face), AudioContext paraverbal, 10-framework verbal, and */
/*  a transparent synthesis layer over the real measured signals only.         */
/* -------------------------------------------------------------------------- */

const MAX_PARTIES = 4;
const PARTY_IDS = ['A', 'B', 'C', 'D'];
const VA_PARTY_COLORS = ['#818cf8', '#22d3ee', '#fbbf24', '#34d399'];
const VA_PARTY_GRAD = [
  ['#6366f1', '#8b5cf6'], ['#0ea5e9', '#22d3ee'],
  ['#f59e0b', '#fbbf24'], ['#10b981', '#34d399'],
];
const VA_ENVIRONMENTS = [
  { key: 'in_person', en: 'In-person', ro: 'Față în față' },
  { key: 'video_call', en: 'Video call', ro: 'Apel video' },
  { key: 'phone', en: 'Phone', ro: 'Telefonic' },
  { key: 'hybrid', en: 'Hybrid', ro: 'Hibrid' },
];

const makeContext = () => ({
  parties: [{ id: 'A', label: 'A', role: '' }, { id: 'B', label: 'B', role: '' }],
  objectives: { A: '', B: '' },
  stakes: '',
  background: '',
  environment: 'video_call',
  environmentNote: '',
});

const capFirst = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);
const partyColor = (i) => VA_PARTY_COLORS[i % VA_PARTY_COLORS.length];
const partyGrad = (i) => VA_PARTY_GRAD[i % VA_PARTY_GRAD.length];

/* ---- transcript: "[mm:ss] Speaker: text" -> per-party text + timed lines ---- */
const VA_TS_RE = /^\s*[[(]?(\d{1,2}):(\d{2})(?::(\d{2}))?[\])]?\s+/;
const VA_SPK_RE = /^\s*([\p{L}][\p{L}\d ._'-]{0,28}?)\s*[:–—-]\s+(.+)$/u;

function parseDialogue(raw, parties) {
  const rawLines = String(raw || '').split(/\r?\n/);
  const seen = new Map(); // lowerName -> { name, order }
  const parsed = []; // { name|null, text, t|null }
  rawLines.forEach((line) => {
    let s = line;
    let tt = null;
    const tm = s.match(VA_TS_RE);
    if (tm) {
      tt = tm[3]
        ? (+tm[1]) * 3600 + (+tm[2]) * 60 + (+tm[3])
        : (+tm[1]) * 60 + (+tm[2]);
      s = s.slice(tm[0].length);
    }
    const m = s.match(VA_SPK_RE);
    if (m) {
      const name = m[1].trim();
      const text = m[2].trim();
      if (!text) return;
      const key = name.toLowerCase();
      if (!seen.has(key)) seen.set(key, { name, order: seen.size });
      parsed.push({ name: key, text, t: tt });
    } else if (s.trim()) {
      if (parsed.length) {
        parsed[parsed.length - 1].text += ' ' + s.trim();
        if (tt != null && parsed[parsed.length - 1].t == null) parsed[parsed.length - 1].t = tt;
      } else {
        parsed.push({ name: null, text: s.trim(), t: tt });
      }
    }
  });

  const speakers = [...seen.values()].sort((a, b) => a.order - b.order);
  const nameToParty = {};
  speakers.forEach((sp, i) => {
    const hit = parties.findIndex((p) =>
      p.label.trim().toLowerCase() === sp.name.toLowerCase()
      || (p.role && p.role.trim().toLowerCase() === sp.name.toLowerCase()));
    nameToParty[sp.name.toLowerCase()] = hit >= 0
      ? parties[hit].id
      : (parties[i % parties.length] || parties[0]).id;
  });

  const perParty = {};
  parties.forEach((p) => { perParty[p.id] = []; });
  const timed = [];
  parsed.forEach((l) => {
    const pid = l.name ? (nameToParty[l.name] || parties[0].id) : parties[0].id;
    if (!perParty[pid]) perParty[pid] = [];
    perParty[pid].push(l.text);
    timed.push({ pid, text: l.text, t: l.t });
  });

  const tsCount = timed.filter((l) => l.t != null).length;
  return {
    perPartyText: Object.fromEntries(
      parties.map((p) => [p.id, (perParty[p.id] || []).join(' ').trim()])
    ),
    timed,
    speakers: speakers.map((s) => s.name),
    nameToParty,
    hasTimestamps: tsCount >= 3,
    labeled: speakers.length > 0,
  };
}

/* ---- per-frame subject tracking: assign detections to party slots by a
       running horizontal anchor (parties keep their seats in a recording) ---- */
function assignSlots(dets, anchors, n) {
  const out = new Array(dets.length).fill(-1);
  if (!dets.length) return out;
  const haveAnchor = anchors.some((a) => a != null);
  if (!haveAnchor) {
    dets.map((d, i) => ({ i, x: d.x }))
      .sort((a, b) => a.x - b.x)
      .slice(0, n)
      .forEach((d, slot) => { out[d.i] = slot; anchors[slot] = d.x; });
    return out;
  }
  const pairs = [];
  dets.forEach((d, di) => anchors.forEach((a, si) => {
    if (a != null) pairs.push({ di, si, dd: Math.abs(a - d.x) });
  }));
  pairs.sort((a, b) => a.dd - b.dd);
  const dTaken = new Set();
  const sTaken = new Set();
  pairs.forEach(({ di, si, dd }) => {
    if (dTaken.has(di) || sTaken.has(si) || dd > 0.3) return;
    out[di] = si; dTaken.add(di); sTaken.add(si);
    anchors[si] += (dets[di].x - anchors[si]) * 0.35;
  });
  dets.forEach((d, di) => {
    if (out[di] >= 0) return;
    const free = anchors.findIndex((a, si) => a == null && !sTaken.has(si));
    if (free >= 0) { out[di] = free; anchors[free] = d.x; sTaken.add(free); }
  });
  return out;
}

const poseCentroidX = (lm) => {
  if (lm && lm[11] && lm[12]) return (lm[11].x + lm[12].x) / 2;
  if (lm && lm.length) return lm.reduce((s, p) => s + p.x, 0) / lm.length;
  return 0.5;
};
const faceCentroidX = (lm) => {
  if (lm && lm[1]) return lm[1].x;
  if (lm && lm.length) return lm.reduce((s, p) => s + p.x, 0) / lm.length;
  return 0.5;
};

/* ---- synthesis accessors over a real /analyze result ---- */
const vaPF = (v, slug) => {
  const f = v && v.frameworks && v.frameworks[slug];
  return f ? String(loc(f.primary_finding, 'en')).toLowerCase() : '';
};
const vaConf = (v, slug) => {
  const f = v && v.frameworks && v.frameworks[slug];
  return f ? (toPct(f.confidence) || 0) : 0;
};
const vaTrig = (v, slug) => !!(v && v.frameworks && v.frameworks[slug] && v.frameworks[slug].triggered);
const vaDetail = (v, slug) => {
  const f = v && v.frameworks && v.frameworks[slug];
  return f && f.detail ? String(f.detail).toLowerCase() : '';
};
const vaFwName = (slug, lang) => {
  const m = FRAMEWORKS.find((f) => f.key === slug);
  return m ? m.name[lang] : slug;
};

function nvSentiment(nv) {
  if (!nv) return null;
  return clamp(
    50 + (nv.openness - 0.35) * 42 - nv.defensive * 38 + (nv.smile - 0.12) * 26
    + nv.engagement * 20 - nv.faceTension * 30 + (nv.eyeContact - 0.4) * 30
    - Math.max(0, nv.movement - 0.05) * 120,
    0, 100,
  );
}
function pvSentiment(pv) {
  if (!pv) return null;
  return clamp(
    50 + (pv.volNorm - 0.4) * 20 - Math.max(0, pv.volVar - 0.3) * 40
    + Math.min(pv.pitchVar, 0.3) * 40 - Math.max(0, pv.pitchVar - 0.5) * 50
    - Math.abs(pv.pace - 0.5) * 26,
    0, 100,
  );
}
function authenticityScore(pd) {
  const v = pd.verbal ? toProb10(pd.verbal.close_probability) * 10 : null;
  const n = nvSentiment(pd.nv);
  const p = pvSentiment(pd.pv);
  const vals = [v, n, p].filter((x) => x != null);
  if (!vals.length) return 60;
  const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
  const spread = Math.sqrt(vals.reduce((s, x) => s + (x - mean) ** 2, 0) / vals.length);
  let a = 84 - spread * 1.15;
  if (pd.nv) a += (pd.nv.eyeContact - 0.45) * 24 - pd.nv.faceTension * 22 - pd.nv.defensive * 14;
  if (pd.verbal && pd.nv) {
    const collab = vaPF(pd.verbal, 'narrative').includes('collaborative')
      || ['openness', 'acceptance', 'calm'].some((k) => vaPF(pd.verbal, 'ei').includes(k));
    if (collab && (pd.nv.defensive > 0.45 || pd.nv.eyeContact < 0.35)) a -= 18;
  }
  return clamp(Math.round(a), 0, 100);
}
function powerScore(pd) {
  let s = 50;
  const v = pd.verbal;
  if (v) {
    const gd = vaDetail(v, 'game_theory');
    if (gd.includes('dominant')) s += 16;
    else if (gd.includes('advantageous')) s += 8;
    else if (gd.includes('disadvantaged')) s -= 16;
    s += (toProb10(v.close_probability) - 5) * 1.6;
    if (vaPF(v, 'ta').includes('adult')) s += 5;
    if (vaPF(v, 'attachment').includes('anxious')) s -= 8;
    if (vaTrig(v, 'cbt') && !vaPF(v, 'cbt').includes('clear')) s -= 5;
  }
  if (pd.nv) {
    s += (pd.nv.openness - 0.35) * 20 - pd.nv.defensive * 22 - pd.nv.faceTension * 16
      + (pd.nv.eyeContact - 0.45) * 20 - Math.max(0, pd.nv.bodyTension - 0.4) * 18;
  }
  if (pd.pv) s += (pd.pv.volNorm - 0.4) * 14 - Math.max(0, pd.pv.pitchVar - 0.5) * 20;
  return clamp(Math.round(s), 1, 99);
}

function objectivesAlignment(context) {
  const objs = context.parties
    .map((p) => (context.objectives[p.id] || '').toLowerCase())
    .filter(Boolean);
  if (objs.length < 2) return 0.5;
  const words = (str) => new Set(str.split(/[^a-zăâîșț]+/i).filter((w) => w.length > 3));
  const a = words(objs[0]);
  const b = words(objs[1]);
  if (!a.size || !b.size) return 0.5;
  let inter = 0;
  a.forEach((w) => { if (b.has(w)) inter += 1; });
  return clamp(0.3 + inter / Math.min(a.size, b.size), 0, 1);
}

/* ---- the transparent profile: every line traces to a measured signal ---- */
function deriveProfile(pd, lang) {
  const ro = lang === 'ro';
  const P = (en, r) => (ro ? r : en);
  const v = pd.verbal;
  const nv = pd.nv;
  const pv = pd.pv;
  const authScore = authenticityScore(pd);
  const powerRaw = powerScore(pd);
  const nvS = nvSentiment(nv);
  const pvS = pvSentiment(pv);
  const vS = v ? toProb10(v.close_probability) * 10 : null;
  const S = [];
  const W = [];
  const add = (arr, s) => { if (s && !arr.includes(s)) arr.push(s); };

  /* personality */
  const per = [];
  if (v) {
    const ta = vaPF(v, 'ta');
    const att = vaPF(v, 'attachment');
    const nlp = vaPF(v, 'nlp');
    if (ta.includes('adult')) {
      per.push(P('holds an adult, task-focused stance', 'menține o poziție adultă, centrată pe sarcină'));
      add(S, P('stays in the Adult ego-state', 'rămâne în starea de Adult'));
    } else if (ta.includes('parent')) {
      per.push(P('speaks from a parental, evaluative register', 'vorbește dintr-un registru parental, evaluativ'));
    } else if (ta.includes('child')) {
      per.push(P('reacts from a Child ego-state under pressure', 'reacționează dintr-o stare de Copil sub presiune'));
      add(W, P('emotional reactivity under pressure', 'reactivitate emoțională sub presiune'));
    }
    if (att.includes('secure')) {
      per.push(P('secure relational baseline', 'bază relațională securizantă'));
      add(S, P('secure attachment', 'atașament securizant'));
    } else if (att.includes('fearful')) {
      per.push(P('fearful-avoidant — approach/withdraw swings', 'anxios-evitant — oscilează apropiere/retragere'));
      add(W, P('unstable approach/withdraw pattern', 'tipar instabil apropiere/retragere'));
    } else if (att.includes('anxious')) {
      per.push(P('anxious attachment — seeks reassurance', 'atașament anxios — caută reasigurare'));
      add(W, P('needs reassurance, fears rejection', 'nevoie de reasigurare, teama de respingere'));
    } else if (att.includes('avoidant')) {
      per.push(P('keeps relational distance (avoidant)', 'păstrează distanță relațională (evitant)'));
      add(W, P('withdraws when pushed', 'se retrage când e presat'));
    }
    if (nlp.includes('visual')) per.push(P('thinks in pictures (visual)', 'gândește în imagini (vizual)'));
    else if (nlp.includes('auditory')) per.push(P('tracks logic and wording (auditory)', 'urmărește logica și formularea (auditiv)'));
    else if (nlp.includes('kinesthetic')) per.push(P('decides on felt sense (kinesthetic)', 'decide pe senzație (kinestezic)'));
  }
  if (nv) {
    if (nv.openness > 0.5) per.push(P('open body posture', 'postură corporală deschisă'));
    if (nv.defensive > 0.5) per.push(P('closed, guarded posture', 'postură închisă, defensivă'));
    if (nv.lean > 13) per.push(P('leans in, physically engaged', 'se apleacă înainte, implicat fizic'));
  }
  const personality = per.length
    ? capFirst(per.join('; ')) + '.'
    : P('Not enough signal for a personality read.', 'Semnal insuficient pentru un profil de personalitate.');

  /* cognitive style */
  const cog = [];
  if (v) {
    if (vaTrig(v, 'cbt') && !vaPF(v, 'cbt').includes('clear')) {
      cog.push(P(`reasoning skewed by ${loc(v.frameworks.cbt.primary_finding, lang).toLowerCase()}`,
        `raționament distorsionat de ${loc(v.frameworks.cbt.primary_finding, lang).toLowerCase()}`));
      add(W, P(`cognitive distortion: ${loc(v.frameworks.cbt.primary_finding, lang).toLowerCase()}`,
        `distorsiune cognitivă: ${loc(v.frameworks.cbt.primary_finding, lang).toLowerCase()}`));
    } else {
      cog.push(P('clear, evidence-based thinking', 'gândire clară, bazată pe dovezi'));
      add(S, P('clear thinking, no distortions', 'gândire clară, fără distorsiuni'));
    }
    if (vaTrig(v, 'behavioral_econ')) {
      cog.push(P(`decision bias present: ${loc(v.frameworks.behavioral_econ.primary_finding, lang).toLowerCase()}`,
        `distorsiune decizională: ${loc(v.frameworks.behavioral_econ.primary_finding, lang).toLowerCase()}`));
      add(W, P(`exploitable bias: ${loc(v.frameworks.behavioral_econ.primary_finding, lang).toLowerCase()}`,
        `distorsiune exploatabilă: ${loc(v.frameworks.behavioral_econ.primary_finding, lang).toLowerCase()}`));
    }
  }
  const cognitive = cog.length
    ? capFirst(cog.join('; ')) + '.'
    : P('No transcript — cognitive style not assessed.', 'Fără transcriere — stilul cognitiv nu a fost evaluat.');

  /* emotional state */
  const emo = [];
  if (v) {
    const ei = vaPF(v, 'ei');
    if (['openness', 'acceptance', 'curiosity', 'calm', 'enthusiasm', 'excitement'].some((k) => ei.includes(k))) {
      emo.push(P('receptive and emotionally available', 'receptiv și disponibil emoțional'));
      add(S, P('open emotional window', 'fereastră emoțională deschisă'));
    } else if (ei.includes('skepticism')) emo.push(P('skeptical, holding back', 'sceptic, rezervat'));
    else if (ei.includes('frustration')) { emo.push(P('frustrated', 'frustrat')); add(W, P('frustration in play', 'frustrare activă')); }
    else if (ei.includes('fear') || ei.includes('anxiety')) { emo.push(P('anxious, threat-sensitive', 'anxios, sensibil la amenințare')); add(W, P('threat sensitivity', 'sensibilitate la amenințare')); }
    const ns = vaPF(v, 'neuroscience');
    if (ns.includes('sympathetic')) { emo.push(P('nervous system in alert (sympathetic)', 'sistem nervos în alertă (simpatic)')); add(W, P('sympathetic arousal — de-escalate first', 'activare simpatică — de-escaladează întâi')); }
    else if (ns.includes('parasympathetic')) { emo.push(P('calm nervous system (parasympathetic)', 'sistem nervos calm (parasimpatic)')); add(S, P('regulated, calm state', 'stare reglată, calmă')); }
    if (vaTrig(v, 'somatic') && vaPF(v, 'somatic').includes('dysregulat')) { emo.push(P('somatically dysregulated', 'dereglat somatic')); add(W, P('somatic dysregulation', 'dereglare somatică')); }
  }
  if (nv && nv.faceTension > 0.4) emo.push(P('visible facial tension', 'tensiune facială vizibilă'));
  if (pv && pvS != null && pvS < 42 && pv.pitchVar > 0.5) emo.push(P('strained vocal delivery', 'livrare vocală încordată'));
  const emotional = emo.length
    ? capFirst(emo.join('; ')) + '.'
    : P('Neutral / no strong emotional signal.', 'Neutru / niciun semnal emoțional puternic.');

  /* decision-making */
  const dec = [];
  if (v) {
    const ga = vaPF(v, 'game_theory');
    if (ga.includes('zero') || ga.includes('prisoner')) { dec.push(P('frames the deal as win-lose', 'încadrează acordul ca câștig-pierdere')); add(W, P('win-lose framing', 'încadrare câștig-pierdere')); }
    else if (ga.includes('coordination') || ga.includes('cooperative') || ga.includes('non-zero') || ga.includes('non_zero')) { dec.push(P('open to joint problem-solving', 'deschis la rezolvarea comună')); add(S, P('cooperative game framing', 'încadrare cooperativă a jocului')); }
    const gp = vaDetail(v, 'game_theory');
    if (gp.includes('dominant')) dec.push(P('negotiating from strength', 'negociază din poziție de forță'));
    else if (gp.includes('disadvantaged')) { dec.push(P('negotiating from a weak position', 'negociază din poziție slabă')); add(W, P('weak strategic position', 'poziție strategică slabă')); }
    if (vaPF(v, 'behavioral_econ').includes('loss')) dec.push(P('loss-averse — anchors on what could be lost', 'aversiune la pierdere — se ancorează pe ce ar putea pierde'));
    if (vaPF(v, 'cbt').includes('should')) dec.push(P('rigid rules about how talks must go', 'reguli rigide despre cum trebuie să decurgă discuția'));
  }
  const decision = dec.length
    ? capFirst(dec.join('; ')) + '.'
    : P('Decisions look pragmatic and incremental.', 'Deciziile par pragmatice și incrementale.');

  /* power dynamics */
  let powerTxt;
  if (powerRaw > 62) powerTxt = P('Currently holds the upper hand', 'Deține momentan avantajul');
  else if (powerRaw < 38) powerTxt = P('Currently the weaker party at the table', 'Momentan partea mai slabă la masă');
  else powerTxt = P('Roughly balanced with the other side', 'Aproximativ echilibrat cu cealaltă parte');
  const pdriv = [];
  if (v && vaDetail(v, 'game_theory').includes('dominant')) pdriv.push(P('dominant strategic position', 'poziție strategică dominantă'));
  if (nv && nv.openness > 0.5 && nv.defensive < 0.3) pdriv.push(P('open, unthreatened posture', 'postură deschisă, neamenințată'));
  if (nv && nv.defensive > 0.5) pdriv.push(P('defensive posture undercuts standing', 'postura defensivă îi scade poziția'));
  if (vS != null && vS >= 70) pdriv.push(P('verbal content trends to agreement', 'conținutul verbal tinde spre acord'));
  const power = `${powerTxt}${pdriv.length ? ' — ' + pdriv.join(', ') : ''}. (${powerRaw}/100)`;

  /* authenticity */
  let authTxt;
  if (authScore >= 70) { authTxt = P('Verbal, body and voice signals align — reads as candid', 'Semnalele verbale, corporale și vocale se aliniază — pare sincer'); add(S, P('congruent across channels', 'congruent pe toate canalele')); }
  else if (authScore >= 50) authTxt = P('Mostly congruent, with minor tells', 'În general congruent, cu mici indicii');
  else { authTxt = P('Notable gap between what is said and how the body and voice behave', 'Diferență notabilă între ce spune și cum se comportă corpul și vocea'); add(W, P('low channel congruence — verify claims', 'congruență scăzută — verifică afirmațiile')); }
  const authenticity = `${authTxt}. (${authScore}/100)`;

  /* extra strengths / vulnerabilities straight from measured non/para-verbal */
  if (nv) {
    if (nv.eyeContact < 0.35) add(W, P('avoids eye contact', 'evită contactul vizual'));
    if (nv.defensive > 0.5) add(W, P('closed / defensive posture', 'postură închisă / defensivă'));
    if (nv.movement > 0.06) add(W, P('restless — shifting and fidgeting', 'agitat — se foiește'));
    if (nv.openness > 0.5) add(S, P('open, receptive body language', 'limbaj corporal deschis'));
    if (nv.engagement > 0.5) add(S, P('visibly engaged', 'vizibil implicat'));
    if (nv.eyeContact > 0.6) add(S, P('steady eye contact', 'contact vizual constant'));
  }
  if (pv) {
    if (pv.pitchVar >= 0.15 && pv.pitchVar <= 0.45) add(S, P('expressive, steady voice', 'voce expresivă, constantă'));
    if (pv.pitchVar > 0.55) add(W, P('voice under strain', 'voce sub tensiune'));
    if (pv.pace > 0.66) add(W, P('talks fast — may signal nerves', 'vorbește repede — posibil semn de nervozitate'));
  }
  if (vS != null && vS <= 30) add(W, P('verbal content trends to resistance', 'conținutul verbal tinde spre rezistență'));
  if (vS != null && vS >= 80) add(S, P('verbal content trends to agreement', 'conținutul verbal tinde spre acord'));

  return {
    personality, cognitive, emotional, decision, power, authenticity,
    strengths: S.slice(0, 6),
    vulnerabilities: W.slice(0, 6),
    authScore, powerRaw, nvS, pvS, vS,
  };
}

/* ---- 3-tier read (Amateur / Professional / Expert) over the same profile ---- */
function primaryLever(pd, prof, lang) {
  const ro = lang === 'ro';
  const P = (en, r) => (ro ? r : en);
  if (prof.authScore < 50) return P('do not trust the surface — verify every claim before conceding', 'nu te încrede în aparență — verifică fiecare afirmație înainte de a ceda');
  if (prof.powerRaw < 42) return P('you hold leverage — press calmly for a concrete commitment', 'ai avantajul — cere calm un angajament concret');
  if (prof.powerRaw > 62) return P('they hold leverage — widen the pie, add options, avoid a head-on price fight', 'ei au avantajul — mărește tortul, adaugă opțiuni, evită lupta frontală pe preț');
  if (pd.nv && pd.nv.defensive > 0.5) return P('lower the pressure and slow down — the body has closed', 'scade presiunea și încetinește — corpul s-a închis');
  if (pd.verbal && vaPF(pd.verbal, 'ei').includes('skepticism')) return P('surface the doubt out loud, then ask for their criterion', 'numește îndoiala cu voce tare, apoi cere criteriul lor');
  if (prof.vulnerabilities[0]) return P(`work the opening: ${prof.vulnerabilities[0]}`, `folosește deschiderea: ${prof.vulnerabilities[0]}`);
  return P('stay in Adult, keep it factual, advance one concrete step', 'rămâi în Adult, ține discuția factuală, avansează un pas concret');
}
function deriveTiers(pd, prof, lang) {
  const ro = lang === 'ro';
  const P = (en, r) => (ro ? r : en);
  const lever = primaryLever(pd, prof, lang);
  const amateur = capFirst(lever) + '.';
  const caution = prof.vulnerabilities[0]
    ? P(`Watch for ${prof.vulnerabilities[0]}.`, `Atenție la ${prof.vulnerabilities[0]}.`)
    : P('Keep verifying as you go.', 'Continuă să verifici pe parcurs.');
  const professional = `${prof.personality} ${P('Main lever', 'Pârghia principală')}: ${lever}. ${caution}`;
  const topFw = pd.verbal && Array.isArray(pd.verbal.top_frameworks)
    ? pd.verbal.top_frameworks.slice(0, 2)
      .map((k) => `${vaFwName(k, lang)} ${vaConf(pd.verbal, k)}%`).join(', ')
    : '—';
  const cov = pd.poseCov != null
    ? `pose ${Math.round(pd.poseCov * 100)}% / face ${Math.round(pd.faceCov * 100)}%`
    : '—';
  const expert = [
    `${P('Verbal', 'Verbal')}: ${prof.vS != null ? prof.vS + '/100' : '—'} · ${P('top frameworks', 'framework-uri principale')}: ${topFw}.`,
    `${P('Non-verbal', 'Non-verbal')}: ${prof.nvS != null ? prof.nvS + '/100' : '—'} (${cov}). ${P('Paraverbal', 'Paraverbal')}: ${prof.pvS != null ? prof.pvS + '/100' : P('shared channel', 'canal comun')}.`,
    `${P('Power', 'Putere')} ${prof.powerRaw}/100 · ${P('Authenticity', 'Autenticitate')} ${prof.authScore}/100. ${prof.decision}`,
    `${P('Play', 'Mișcare')}: ${lever}.`,
  ].join(' ');
  return { amateur, professional, expert };
}

/* ---- strategic paths for one party (objective-mapped when an objective is set) ---- */
function deriveStrategicPaths(pd, prof, opp, objective, lang) {
  const ro = lang === 'ro';
  const P = (en, r) => (ro ? r : en);
  const paths = [];
  if (objective && objective.trim()) {
    const topK = pd.verbal && Array.isArray(pd.verbal.top_frameworks) && pd.verbal.top_frameworks[0];
    paths.push({
      move: P(`Toward the objective "${objective.trim()}": open with ${topK ? vaFwName(topK, lang) : 'an Adult-to-Adult'} framing.`,
        `Spre obiectivul „${objective.trim()}": deschide cu o abordare ${topK ? vaFwName(topK, lang) : 'Adult–Adult'}.`),
      why: topK
        ? P(`${vaFwName(topK, lang)} is this party's strongest active lever (${vaConf(pd.verbal, topK)}%).`,
          `${vaFwName(topK, lang)} este cea mai puternică pârghie activă a acestei părți (${vaConf(pd.verbal, topK)}%).`)
        : P('No verbal signal — anchor on shared criteria.', 'Fără semnal verbal — ancorează pe criterii comune.'),
    });
  }
  const sugg = pd.verbal && Array.isArray(pd.verbal.top_frameworks)
    ? pd.verbal.top_frameworks.slice(0, 3)
    : [];
  sugg.forEach((k) => {
    const s = loc(pd.verbal.frameworks[k] && pd.verbal.frameworks[k].suggestion, lang);
    if (s) paths.push({ move: s, why: `${P('maps to', 'corespunde')} ${vaFwName(k, lang)} (${vaConf(pd.verbal, k)}%).` });
  });
  if (opp && opp.prof && opp.prof.vulnerabilities[0]) {
    paths.push({
      move: P(`Use ${opp.label}'s exposure: ${opp.prof.vulnerabilities[0]}.`,
        `Folosește expunerea ${opp.label}: ${opp.prof.vulnerabilities[0]}.`),
      why: P('Their weakest measured signal — press here, gently.', 'Cel mai slab semnal măsurat al lor — apasă aici, cu tact.'),
    });
  }
  if (!paths.length) {
    paths.push({
      move: P('Match their pace for one exchange, then lead toward your agenda.', 'Fă pacing la ritmul lor un schimb, apoi condu spre agenda ta.'),
      why: P('No transcript to map psychology — use the non-verbal read.', 'Fără transcriere pentru psihologie — folosește citirea non-verbală.'),
    });
  }
  return paths.slice(0, 4);
}

/* ---- comparative A-vs-B ---- */
function deriveComparative(list, lang) {
  if (list.length < 2) return null;
  const ro = lang === 'ro';
  const P = (en, r) => (ro ? r : en);
  const conf = (pd) => {
    const cp = pd.verbal ? toProb10(pd.verbal.close_probability) * 10 : 50;
    const eng = pd.nv ? pd.nv.engagement * 100 : 50;
    return Math.round(cp * 0.6 + eng * 0.4);
  };
  const rows = [
    { key: 'confidence', label: P('Confidence', 'Încredere'), vals: list.map(conf) },
    { key: 'authenticity', label: P('Authenticity', 'Autenticitate'), vals: list.map((pd) => pd.prof.authScore) },
    {
      key: 'power',
      label: P('Power', 'Putere'),
      vals: (() => {
        const raw = list.map((pd) => pd.prof.powerRaw);
        const sum = raw.reduce((a, b) => a + b, 0) || 1;
        return raw.map((x) => Math.round((x / sum) * 100));
      })(),
    },
  ];
  const hidden = list.map((pd) => {
    const flags = [];
    const v = pd.verbal;
    if (pd.prof.authScore < 55 && pd.nv && (pd.nv.defensive > 0.45 || pd.nv.eyeContact < 0.35)
      && (v && (vaPF(v, 'narrative').includes('collaborative') || vaPF(v, 'ei').includes('openness')))) {
      flags.push(P('States cooperation, body language says otherwise.', 'Declară cooperare, limbajul corpului spune altceva.'));
    }
    if (v && (vaPF(v, 'game_theory').includes('zero') || vaPF(v, 'narrative').includes('victor'))
      && pd.objective && pd.objective.trim()) {
      flags.push(P('Stated goal may mask a win-lose intent.', 'Obiectivul declarat poate ascunde o intenție câștig-pierdere.'));
    }
    if (v && toProb10(v.close_probability) >= 7 && pd.nv && pd.nv.faceTension > 0.42) {
      flags.push(P('Agreeable words over visible tension — a reservation is likely.', 'Cuvinte agreabile peste tensiune vizibilă — probabil o rezervă.'));
    }
    return { pid: pd.id, label: pd.label, flags };
  });
  return { rows, hidden };
}

/* ---- outcome probability per scenario ---- */
function deriveScenarios(list, context, lang) {
  const ro = lang === 'ro';
  const P = (en, r) => (ro ? r : en);
  const cps = list.map((pd) => (pd.verbal ? toProb10(pd.verbal.close_probability) : 5));
  const avg = cps.reduce((a, b) => a + b, 0) / cps.length;
  const defens = list.reduce((s, pd) => s + (pd.nv ? pd.nv.defensive : 0), 0) / list.length;
  const align = objectivesAlignment(context);
  const norm = (w) => {
    const tot = Object.values(w).reduce((a, b) => a + b, 0) || 1;
    return Object.fromEntries(Object.entries(w).map(([k, x]) => [k, Math.round((x / tot) * 100)]));
  };

  if (list.length === 2) {
    const [a, b] = list;
    const aP = a.prof.powerRaw;
    const bP = b.prof.powerRaw;
    const gap = Math.abs(aP - bP);
    const weaker = aP < bP ? a.label : b.label;
    const w = {
      close_now: Math.max(0.5, avg * 9 + (1 - defens) * 20 + align * 12 - gap * 0.5),
      close_concede: Math.max(0.5, gap * 1.5 + avg * 4),
      extended: Math.max(0.5, 24 + defens * 12 + (1 - align) * 8),
      breakdown: Math.max(0.5, (10 - avg) * 7 + defens * 30 - align * 16),
    };
    const pct = norm(w);
    return [
      { key: 'close_now', label: P(`${a.label} and ${b.label} agree on current terms`, `${a.label} și ${b.label} cad de acord pe termenii actuali`), p: pct.close_now },
      { key: 'close_concede', label: P(`Deal closes after ${weaker} concedes`, `Acord după ce ${weaker} cedează`), p: pct.close_concede },
      { key: 'extended', label: P('Extended talks / partial agreement', 'Negocieri prelungite / acord parțial'), p: pct.extended },
      { key: 'breakdown', label: P('Breakdown — no agreement', 'Blocaj — fără acord'), p: pct.breakdown },
    ].sort((x, y) => y.p - x.p);
  }
  const w = {
    consensus: Math.max(0.5, avg * 8 + (1 - defens) * 20 + align * 12),
    partial: Math.max(0.5, 28 + defens * 10),
    breakdown: Math.max(0.5, (10 - avg) * 7 + defens * 26 - align * 14),
  };
  const pct = norm(w);
  return [
    { key: 'consensus', label: P('All parties reach consensus', 'Toate părțile ajung la consens'), p: pct.consensus },
    { key: 'partial', label: P('Partial agreement / subset aligns', 'Acord parțial / un subgrup se aliniază'), p: pct.partial },
    { key: 'breakdown', label: P('Breakdown — no agreement', 'Blocaj — fără acord'), p: pct.breakdown },
  ].sort((x, y) => y.p - x.p);
}

/* ---- combined coaching: all parties integrated ---- */
function deriveCombined(list, comparative, scenarios, lang) {
  const ro = lang === 'ro';
  const P = (en, r) => (ro ? r : en);
  const cps = list.map((pd) => (pd.verbal ? toProb10(pd.verbal.close_probability) : null)).filter((x) => x != null);
  const range = cps.length
    ? (cps.length > 1 ? `${Math.min(...cps)}–${Math.max(...cps)}` : `${cps[0]}`)
    : '—';
  const strongest = [...list].sort((a, b) => b.prof.powerRaw - a.prof.powerRaw)[0];
  const lowestAuth = [...list].sort((a, b) => a.prof.authScore - b.prof.authScore)[0];
  const top = scenarios[0];
  const parts = [];
  parts.push(P(`Close probability runs ${range}/10 across the parties.`,
    `Probabilitatea de închidere este ${range}/10 între părți.`));
  if (list.length > 1) {
    parts.push(P(`${strongest.label} holds the balance of power.`,
      `${strongest.label} deține balanța puterii.`));
  }
  if (top) {
    parts.push(P(`Most likely outcome: ${top.label.toLowerCase()} (${top.p}%).`,
      `Cel mai probabil rezultat: ${top.label.toLowerCase()} (${top.p}%).`));
  }
  list.forEach((pd) => {
    parts.push(P(`With ${pd.label}: ${primaryLever(pd, pd.prof, lang)}.`,
      `Cu ${pd.label}: ${primaryLever(pd, pd.prof, lang)}.`));
  });
  if (lowestAuth && lowestAuth.prof.authScore < 60) {
    parts.push(P(`Watch ${lowestAuth.label}'s authenticity (${lowestAuth.prof.authScore}/100) — say-do gap.`,
      `Atenție la autenticitatea ${lowestAuth.label} (${lowestAuth.prof.authScore}/100) — diferență între vorbe și fapte.`));
  }
  return parts.join(' ');
}

/* -------------------------------------------------------------------------- */
/*  Sub-components                                                            */
/* -------------------------------------------------------------------------- */

function ContextPanel({ context, setContext, lang, variant = 'sidebar' }) {
  const L = t[lang];
  const set = (patch) => setContext({ ...context, ...patch });
  const setParty = (i, patch) => {
    const parties = context.parties.map((p, k) => (k === i ? { ...p, ...patch } : p));
    set({ parties });
  };
  const addParty = () => {
    if (context.parties.length >= MAX_PARTIES) return;
    const id = PARTY_IDS[context.parties.length];
    set({
      parties: [...context.parties, { id, label: id, role: '' }],
      objectives: { ...context.objectives, [id]: '' },
    });
  };
  const removeParty = (i) => {
    if (context.parties.length <= 2) return;
    const gone = context.parties[i].id;
    const objectives = { ...context.objectives };
    delete objectives[gone];
    set({ parties: context.parties.filter((_, k) => k !== i), objectives });
  };

  return (
    <aside className={`va-context${variant === 'panel' ? ' va-context--panel' : ''}`}>
      <h3 className="va-context-title">{L.ctxTitle}</h3>

      <div className="va-ctx-group">
        <span className="si-field-label">{L.ctxParties}</span>
        {context.parties.map((p, i) => (
          <div key={p.id} className="va-ctx-party" style={{ '--pc': partyColor(i) }}>
            <span className="va-ctx-dot" />
            <input
              className="va-ctx-input"
              value={p.label}
              onChange={(e) => setParty(i, { label: e.target.value })}
              placeholder={`${L.ctxParty} ${p.id}`}
              aria-label={`${L.ctxParty} ${p.id}`}
            />
            <input
              className="va-ctx-input"
              value={p.role}
              onChange={(e) => setParty(i, { role: e.target.value })}
              placeholder={L.ctxRole}
              aria-label={L.ctxRole}
            />
            {context.parties.length > 2 && (
              <button type="button" className="va-ctx-x" onClick={() => removeParty(i)} title={L.ctxRemove}>×</button>
            )}
          </div>
        ))}
        {context.parties.length < MAX_PARTIES && (
          <button type="button" className="va-ctx-add" onClick={addParty}>{L.ctxAddParty}</button>
        )}
      </div>

      <div className="va-ctx-group">
        <span className="si-field-label">{L.ctxObjective}</span>
        {context.parties.map((p, i) => (
          <div key={p.id} className="va-ctx-obj">
            <label className="va-ctx-obj-label" style={{ color: partyColor(i) }}>{p.label || p.id}</label>
            <textarea
              className="va-ctx-area"
              rows={2}
              value={context.objectives[p.id] || ''}
              onChange={(e) => set({ objectives: { ...context.objectives, [p.id]: e.target.value } })}
              placeholder={L.ctxObjective}
            />
          </div>
        ))}
        <p className="va-ctx-hint">{L.ctxObjectiveHint}</p>
      </div>

      <div className="va-ctx-group">
        <label className="si-field-label" htmlFor="va-ctx-stakes">{L.ctxStakes}</label>
        <textarea id="va-ctx-stakes" className="va-ctx-area" rows={2}
          value={context.stakes} onChange={(e) => set({ stakes: e.target.value })} />
      </div>
      <div className="va-ctx-group">
        <label className="si-field-label" htmlFor="va-ctx-bg">{L.ctxBackground}</label>
        <textarea id="va-ctx-bg" className="va-ctx-area" rows={3}
          value={context.background} onChange={(e) => set({ background: e.target.value })} />
      </div>
      <div className="va-ctx-group">
        <label className="si-field-label" htmlFor="va-ctx-env">{L.ctxEnvironment}</label>
        <select id="va-ctx-env" className="va-ctx-select"
          value={context.environment} onChange={(e) => set({ environment: e.target.value })}>
          {VA_ENVIRONMENTS.map((o) => <option key={o.key} value={o.key}>{o[lang]}</option>)}
        </select>
        <input className="va-ctx-input" style={{ marginTop: 8 }}
          value={context.environmentNote} onChange={(e) => set({ environmentNote: e.target.value })}
          placeholder={L.ctxEnvNote} />
      </div>
    </aside>
  );
}

function PartyTimeline({ tracks, parties, duration, current, onSeek, lang }) {
  const L = t[lang];
  if (!duration) return null;
  return (
    <div className="va-timeline">
      {tracks.map((segs, pi) => (
        <div key={pi} className="va-tl-row">
          <span className="va-tl-tag" style={{ color: partyColor(pi) }}>
            {parties[pi] ? (parties[pi].label || parties[pi].id) : `#${pi + 1}`}
          </span>
          <div className="va-timeline-track">
            {segs.map((m, i) => (
              <button
                key={i}
                type="button"
                className="va-tl-seg"
                style={{
                  left: `${(m.t0 / duration) * 100}%`,
                  width: `${((m.t1 - m.t0) / duration) * 100}%`,
                  background: m.color,
                }}
                title={`${m.t0.toFixed(1)}s · ${m.score}/100`}
                onClick={() => onSeek(m.t0)}
                aria-label={`${L.moment} ${m.t0.toFixed(0)}s`}
              />
            ))}
            <div className="va-tl-playhead" style={{ left: `${(current / duration) * 100}%` }} />
          </div>
        </div>
      ))}
      <div className="va-tl-legend">
        <span><i style={{ background: '#10b981' }} /> {L.sigStrong}</span>
        <span><i style={{ background: '#f59e0b' }} /> {L.sigNeutral}</span>
        <span><i style={{ background: '#ef4444' }} /> {L.sigWeak}</span>
      </div>
    </div>
  );
}

function CmpBar({ label, vals, parties }) {
  const total = vals.reduce((a, b) => a + b, 0) || 1;
  return (
    <div className="va-cmp-row">
      <span className="va-cmp-label">{label}</span>
      <div className="va-cmp-track">
        {vals.map((v, i) => (
          <div
            key={i}
            className="va-cmp-fill"
            style={{ width: `${(v / total) * 100}%`, background: partyColor(i) }}
            title={`${parties[i] ? parties[i].label : i} · ${v}`}
          >
            <span>{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function TierTabs({ tiers, lang }) {
  const L = t[lang];
  const [tier, setTier] = useState('professional');
  return (
    <div className="va-tier">
      <div className="va-tier-tabs">
        {[['amateur', L.tierAmateur], ['professional', L.tierPro], ['expert', L.tierExpert]].map(([k, lbl]) => (
          <button key={k} type="button"
            className={`va-tier-tab${tier === k ? ' is-active' : ''}`}
            onClick={() => setTier(k)}>{lbl}</button>
        ))}
      </div>
      <p className="va-tier-body">{tiers[tier]}</p>
    </div>
  );
}

function ProfileCard({ pd, prof, tiers, paths, index, lang }) {
  const L = t[lang];
  const col = partyColor(index);
  const nv = pd.nv;
  const pv = pd.pv;
  const v = pd.verbal;
  const bodyless = !nv && !pv;
  const dominantPosture = () => {
    if (!nv) return '—';
    if (nv.defensive > 0.5) return L.postureDefensive;
    if (nv.bodyTension > 0.55) return L.postureRigid;
    if (nv.lean > 12) return L.postureLean;
    if (nv.openness > 0.45) return L.postureOpen;
    return L.postureNeutral;
  };
  const lvl = (x, a, b, lo, md, hi) => (x < a ? lo : x < b ? md : hi);
  const aspects = [
    [L.apPersonality, prof.personality],
    [L.apCognitive, prof.cognitive],
    [L.apEmotional, prof.emotional],
    [L.apDecision, prof.decision],
    [L.apPower, prof.power],
    [L.apAuthenticity, prof.authenticity],
  ];

  return (
    <article className="va-pcard" style={{ '--pc': col }}>
      <header className="va-pcard-head">
        <span className="va-pcard-dot" />
        <div>
          <h4>{pd.label || pd.id}</h4>
          {pd.role && <p>{pd.role}</p>}
        </div>
        {!bodyless && (
          <span className="va-pcard-cov">
            {L.coverage}: {L.pose} {Math.round((pd.poseCov || 0) * 100)}% · {L.face} {Math.round((pd.faceCov || 0) * 100)}%
          </span>
        )}
      </header>

      <div className={`va-pcard-3col${bodyless ? ' va-pcard-3col--solo' : ''}`}>
        <div className="va-pcol">
          <span className="va-pcol-h">{'\u{1F4AC}'} {L.vVerbal}</span>
          {v ? (
            <>
              <p className="va-metric-lg" style={{ color: probColor(toProb10(v.close_probability)) }}>
                {toProb10(v.close_probability) ?? '—'}<span>/10</span>
              </p>
              <p className="va-sub">{L.vCloseProb}</p>
              <ul className="va-mini-list">
                {(Array.isArray(v.top_frameworks) ? v.top_frameworks : []).slice(0, 3).map((k) => {
                  const meta = FRAMEWORKS.find((f) => f.key === k);
                  return meta ? <li key={k}>{meta.icon} {meta.name[lang]} · {vaConf(v, k)}%</li> : null;
                })}
              </ul>
            </>
          ) : <p className="va-sub">{L.vNoTranscript}</p>}
        </div>

        {!bodyless && (
          <div className="va-pcol">
            <span className="va-pcol-h">{'\u{1F9CD}'} {L.vNonVerbal}</span>
            {nv ? (
              <dl className="va-dl">
                <div><dt>{L.vPosture}</dt><dd>{dominantPosture()}</dd></div>
                <div><dt>{L.vGestures}</dt><dd>{lvl(nv.gesture, 0.02, 0.06, L.lvlLow, L.lvlModerate, L.lvlHigh)}</dd></div>
                <div><dt>{L.vMovement}</dt><dd>{lvl(nv.movement, 0.015, 0.05, L.moveStill, L.moveShift, L.movePace)}</dd></div>
                <div><dt>{L.vExpression}</dt><dd>{nv.faceTension > 0.4 ? L.exprTense : nv.engagement > 0.45 ? L.exprEngaged : L.exprNeutral}</dd></div>
                <div><dt>{L.vEyeContact}</dt><dd>{Math.round(nv.eyeContact * 100)}%</dd></div>
              </dl>
            ) : <p className="va-sub">{L.pUnavailable}</p>}
          </div>
        )}

        {!bodyless && (
          <div className="va-pcol">
            <span className="va-pcol-h">{'\u{1F50A}'} {L.vParaVerbal}</span>
            {pv ? (
              <dl className="va-dl">
                <div><dt>{L.pVolume}</dt><dd>{lvl(pv.volNorm, 0.3, 0.6, L.lvlLow, L.lvlModerate, L.lvlHigh)}</dd></div>
                <div><dt>{L.pPitch}</dt><dd>{lvl(pv.pitchNorm, 0.33, 0.66, L.pitchLow, L.pitchMid, L.pitchHigh)}</dd></div>
                <div><dt>{L.pPace}</dt><dd>{lvl(pv.pace, 0.33, 0.66, L.paceSlow, L.paceMeasured, L.paceFast)}</dd></div>
                <div><dt>{L.pTone}</dt><dd>{lvl(pv.pitchVar, 0.2, 0.5, L.toneFlat, L.toneSteady, L.toneStrained)}</dd></div>
              </dl>
            ) : <p className="va-sub">{pd.paraShared ? L.paraShared : L.pUnavailable}</p>}
          </div>
        )}
      </div>

      <div className="va-aspects">
        {aspects.map(([k, txt]) => (
          <div key={k} className="va-aspect">
            <span className="va-aspect-k">{k}</span>
            <p>{txt}</p>
          </div>
        ))}
      </div>

      <div className="va-sw">
        <div className="va-sw-col">
          <span className="va-sw-h va-sw-h--s">{L.apStrengths}</span>
          <ul>{prof.strengths.length ? prof.strengths.map((s, i) => <li key={i}>{s}</li>) : <li className="va-sw-none">—</li>}</ul>
        </div>
        <div className="va-sw-col">
          <span className="va-sw-h va-sw-h--w">{L.apVulnerabilities}</span>
          <ul>{prof.vulnerabilities.length ? prof.vulnerabilities.map((s, i) => <li key={i}>{s}</li>) : <li className="va-sw-none">—</li>}</ul>
        </div>
      </div>

      <TierTabs tiers={tiers} lang={lang} />

      <div className="va-paths">
        <span className="va-pcol-h">{'\u{1F9ED}'} {L.stratTitle}
          {pd.objective && pd.objective.trim()
            ? <em className="va-paths-tag va-paths-tag--obj">{L.stratObjective}</em>
            : <em className="va-paths-tag">{L.stratGeneral}</em>}
        </span>
        <ol className="va-paths-list">
          {paths.map((p, i) => (
            <li key={i}><b>{p.move}</b><span>{p.why}</span></li>
          ))}
        </ol>
      </div>

      {v && (
        <details className="va-details">
          <summary>{L.insights} — {pd.label || pd.id}</summary>
          <ResultsView result={v} lang={lang} />
        </details>
      )}
    </article>
  );
}

/* -------------------------------------------------------------------------- */
/*  Video Analysis page                                                       */
/* -------------------------------------------------------------------------- */

function VideoAnalysis({ lang }) {
  const L = t[lang];
  const inputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const poseRef = useRef(null);
  const faceRef = useRef(null);
  const framesRef = useRef({});   // { [slot]: [{t, pose, face, poseLm, faceLm}] }
  const paraRef = useRef([]);     // [{t, rms, centroid, flux}]  (global audio channel)
  const anchorsRef = useRef([]);  // running horizontal anchor per slot
  const cancelRef = useRef(false);
  const fileRef = useRef(null);
  const audioRef = useRef(null);

  const [context, setContext] = useState(makeContext);
  const [fileName, setFileName] = useState('');
  const [fileSize, setFileSize] = useState(0);
  const [fileUrl, setFileUrl] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  const [modelState, setModelState] = useState('idle'); // idle | loading | ready | error
  const [phase, setPhase] = useState('idle');           // idle | scanning | verbal | done
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const [partiesData, setPartiesData] = useState([]);   // [{ id, label, role, verbal, nv, pv, poseCov, faceCov, paraShared, objective }]
  const [tracks, setTracks] = useState([]);             // [[{t0,t1,score,color}]]
  const [metrics, setMetrics] = useState(null);
  const [dlgInfo, setDlgInfo] = useState(null);

  useEffect(() => () => {
    if (fileUrl) URL.revokeObjectURL(fileUrl);
    if (audioRef.current && audioRef.current.ctx) audioRef.current.ctx.close().catch(() => {});
  }, [fileUrl]);

  const softReset = () => {
    setPartiesData([]); setTracks([]); setMetrics(null); setDlgInfo(null);
    setPhase('idle'); setProgress(0); setError(null);
    framesRef.current = {};
    paraRef.current = [];
    anchorsRef.current = [];
  };

  const nParties = () => Math.min(MAX_PARTIES, Math.max(1, context.parties.length));

  const acceptFile = (file) => {
    if (!file) return;
    if (fileUrl) URL.revokeObjectURL(fileUrl);
    fileRef.current = file;
    setFileName(file.name);
    setFileSize(file.size || 0);
    setFileUrl(URL.createObjectURL(file));
    softReset();
    if (!poseRef.current) {
      setModelState('loading');
      loadVisionModels(nParties())
        .then(({ pose, face, loadMs }) => {
          poseRef.current = pose; faceRef.current = face;
          setModelState('ready');
          console.log(`[SANTINEL video] MediaPipe ready in ${Math.round(loadMs)}ms (${nParties()} subjects)`);
        })
        .catch((e) => { console.error('[SANTINEL video] model load failed', e); setModelState('error'); });
    }
  };

  const resetAll = () => {
    if (fileUrl) URL.revokeObjectURL(fileUrl);
    fileRef.current = null;
    if (inputRef.current) inputRef.current.value = '';
    setFileName(''); setFileSize(0); setFileUrl(''); setTranscript('');
    setDuration(0); setCurrentTime(0);
    softReset();
  };

  /* ---- overlay: draw stored landmarks for the nearest sampled frame, per party ---- */
  const drawOverlay = useCallback(() => {
    const cv = canvasRef.current;
    const vd = videoRef.current;
    if (!cv || !vd) return;
    const w = vd.clientWidth || 1;
    const h = vd.clientHeight || 1;
    if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
    const ctx = cv.getContext('2d');
    ctx.clearRect(0, 0, w, h);
    const tt = vd.currentTime || 0;
    Object.keys(framesRef.current).forEach((slotKey) => {
      const slot = +slotKey;
      const fr = framesRef.current[slot];
      if (!fr || !fr.length) return;
      let best = fr[0];
      let bd = Infinity;
      for (let i = 0; i < fr.length; i += 1) {
        const d = Math.abs(fr[i].t - tt);
        if (d < bd) { bd = d; best = fr[i]; }
      }
      if (!best || bd > 1.4) return;
      const col = partyColor(slot);
      if (best.poseLm) {
        ctx.strokeStyle = col;
        ctx.lineWidth = 2;
        POSE_BONES.forEach(([a, b]) => {
          const p = best.poseLm[a];
          const q = best.poseLm[b];
          if (!p || !q) return;
          ctx.beginPath();
          ctx.moveTo(p.x * w, p.y * h);
          ctx.lineTo(q.x * w, q.y * h);
          ctx.stroke();
        });
        ctx.fillStyle = col;
        best.poseLm.forEach((p, i) => {
          if (i > 24) return;
          ctx.beginPath();
          ctx.arc(p.x * w, p.y * h, 2.4, 0, Math.PI * 2);
          ctx.fill();
        });
      }
      if (best.faceLm) {
        ctx.fillStyle = col;
        ctx.globalAlpha = 0.55;
        for (let i = 0; i < best.faceLm.length; i += 6) {
          const p = best.faceLm[i];
          ctx.beginPath();
          ctx.arc(p.x * w, p.y * h, 1, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.globalAlpha = 1;
      }
    });
  }, []);

  useEffect(() => {
    if (phase === 'done') drawOverlay();
  }, [currentTime, phase, drawOverlay]);

  const ensureAudioGraph = () => {
    if (audioRef.current) return audioRef.current;
    const vd = videoRef.current;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    const ctx = new Ctx();
    const src = ctx.createMediaElementSource(vd);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 1024;
    analyser.smoothingTimeConstant = 0.8;
    const gain = ctx.createGain();
    gain.gain.value = 0;
    src.connect(analyser);
    analyser.connect(gain);
    gain.connect(ctx.destination);
    audioRef.current = { ctx, analyser, src, gain };
    return audioRef.current;
  };

  /* ---- one analysis pass ---- */
  const analyze = async () => {
    const file = fileRef.current;
    const vd = videoRef.current;
    if (!file || !vd) { setError(L.needVideo); return; }
    if (!vd.duration || !isFinite(vd.duration)) { setError(L.needVideo); return; }

    const parties = context.parties.slice(0, MAX_PARTIES);
    const n = parties.length;
    const dlg = parseDialogue(transcript, parties);
    setDlgInfo({ speakers: dlg.speakers, labeled: dlg.labeled, hasTimestamps: dlg.hasTimestamps });

    cancelRef.current = false;
    setError(null);
    setPhase('scanning');
    setProgress(0);
    framesRef.current = {};
    for (let i = 0; i < n; i += 1) framesRef.current[i] = [];
    paraRef.current = [];
    anchorsRef.current = new Array(n).fill(null);

    const M = {
      modelLoadMs: 0, frames: 0, detPose: 0, detFace: 0, inferMs: 0,
      scanMs: 0, paraSamples: 0, apiMs: 0, avgInferMs: 0, subjects: n,
    };

    if (!poseRef.current || !faceRef.current || (poseRef.current && faceRef.current && false)) {
      setModelState('loading');
      try {
        const r = await loadVisionModels(n);
        poseRef.current = r.pose; faceRef.current = r.face;
        M.modelLoadMs = Math.round(r.loadMs);
        setModelState('ready');
      } catch (e) {
        setModelState('error');
        setError(`${L.modelLoadFail} ${e.message || e}`);
        setPhase('idle');
        return;
      }
    } else {
      // ensure the loaded models cover this subject count
      try {
        const r = await loadVisionModels(n);
        poseRef.current = r.pose; faceRef.current = r.face;
        M.modelLoadMs = Math.round(r.loadMs);
      } catch (e) { /* keep existing */ }
    }

    let analyser = null;
    try {
      const g = ensureAudioGraph();
      if (g.ctx.state === 'suspended') await g.ctx.resume().catch(() => {});
      analyser = g.analyser;
    } catch (e) {
      console.warn('[SANTINEL video] audio graph unavailable', e);
    }

    const dur = vd.duration;
    const scanT0 = performance.now();
    let lastDet = -1;
    let lastPara = -1;
    let prevRms = 0;
    const timeBuf = analyser ? new Uint8Array(analyser.fftSize) : null;
    const freqBuf = analyser ? new Uint8Array(analyser.frequencyBinCount) : null;
    const nyq = analyser && audioRef.current ? audioRef.current.ctx.sampleRate / 2 : 22050;

    const sampleAudio = (tt) => {
      if (!analyser) return;
      analyser.getByteTimeDomainData(timeBuf);
      analyser.getByteFrequencyData(freqBuf);
      let sq = 0;
      for (let i = 0; i < timeBuf.length; i += 1) { const x = (timeBuf[i] - 128) / 128; sq += x * x; }
      const rms = Math.sqrt(sq / timeBuf.length);
      let mag = 0;
      let wsum = 0;
      for (let i = 0; i < freqBuf.length; i += 1) { mag += freqBuf[i]; wsum += freqBuf[i] * i; }
      const centroidHz = mag > 0 ? (wsum / mag) / freqBuf.length * nyq : 0;
      const flux = Math.max(0, rms - prevRms);
      prevRms = rms;
      paraRef.current.push({ t: tt, rms, centroid: centroidHz, flux });
    };

    vd.pause();
    vd.muted = true;
    vd.playbackRate = VIDEO_RATE;
    try { vd.currentTime = 0; } catch (e) { /* noop */ }
    try {
      await vd.play();
    } catch (e) {
      console.warn('[SANTINEL video] play() rejected', e);
      setError(L.playBlocked);
      setPhase('idle');
      return;
    }

    await new Promise((resolve) => {
      const useRVFC = 'requestVideoFrameCallback' in HTMLVideoElement.prototype;
      let lastProgress = performance.now();
      let watchTt = -1;
      const watchdog = setInterval(() => {
        if (vd.currentTime > watchTt + 0.01) { watchTt = vd.currentTime; lastProgress = performance.now(); }
        else if (performance.now() - lastProgress > 9000) {
          clearInterval(watchdog);
          setError(L.playBlocked);
          resolve();
        }
      }, 1000);
      const finish = () => { clearInterval(watchdog); resolve(); };
      const step = () => {
        if (cancelRef.current || vd.ended || vd.currentTime >= dur - 0.05) { finish(); return; }
        const tt = vd.currentTime;
        if (tt - lastPara >= PARA_GAP_S) { sampleAudio(tt); lastPara = tt; M.paraSamples += 1; }
        if (tt - lastDet >= DETECT_GAP_S && vd.readyState >= 2) {
          lastDet = tt;
          const i0 = performance.now();
          let pr;
          let frRes;
          try { pr = poseRef.current.detectForVideo(vd, performance.now()); } catch (e) { pr = null; }
          try { frRes = faceRef.current.detectForVideo(vd, performance.now() + 0.5); } catch (e) { frRes = null; }
          M.inferMs += performance.now() - i0;

          const poseSets = (pr && pr.landmarks) ? pr.landmarks : [];
          const faceSets = (frRes && frRes.faceLandmarks) ? frRes.faceLandmarks : [];
          const faceCats = (frRes && frRes.faceBlendshapes) ? frRes.faceBlendshapes : [];
          const faceMats = (frRes && frRes.facialTransformationMatrixes) ? frRes.facialTransformationMatrixes : [];

          // assign poses to slots by horizontal anchor
          const poseDets = poseSets.map((lm) => ({ x: poseCentroidX(lm) }));
          const poseSlot = assignSlots(poseDets, anchorsRef.current, n);
          // assign faces to the same anchors (poses drive the anchor)
          const faceDets = faceSets.map((lm) => ({ x: faceCentroidX(lm) }));
          const faceSlot = assignSlots(faceDets, anchorsRef.current.map((a) => a), n);

          const seen = new Set();
          poseSets.forEach((lm, di) => {
            const slot = poseSlot[di];
            if (slot < 0 || slot >= n) return;
            const fi = faceSlot.findIndex((s) => s === slot);
            const faceLm = fi >= 0 ? faceSets[fi] : null;
            const cats = fi >= 0 && faceCats[fi] ? faceCats[fi].categories : null;
            const matrix = fi >= 0 && faceMats[fi] ? faceMats[fi].data : null;
            framesRef.current[slot].push({
              t: tt,
              pose: readPose(lm),
              face: readFace(faceLm, cats, matrix),
              poseLm: lm || null,
              faceLm: faceLm || null,
            });
            if (lm) M.detPose += 1;
            if (faceLm) M.detFace += 1;
            seen.add(slot);
          });
          // faces with no matched pose (person off-frame from waist up)
          faceSets.forEach((lm, di) => {
            const slot = faceSlot[di];
            if (slot < 0 || slot >= n || seen.has(slot)) return;
            framesRef.current[slot].push({
              t: tt,
              pose: null,
              face: readFace(lm, faceCats[di] ? faceCats[di].categories : null, faceMats[di] ? faceMats[di].data : null),
              poseLm: null,
              faceLm: lm || null,
            });
            if (lm) M.detFace += 1;
          });

          M.frames += 1;
          drawOverlay();
          setProgress(Math.min(0.9, tt / dur));
        }
        if (useRVFC) vd.requestVideoFrameCallback(step);
        else requestAnimationFrame(step);
      };
      if (useRVFC) vd.requestVideoFrameCallback(step);
      else requestAnimationFrame(step);
    });

    vd.pause();
    vd.muted = false;
    vd.playbackRate = 1;
    try { vd.currentTime = 0; } catch (e) { /* noop */ }
    M.scanMs = Math.round(performance.now() - scanT0);
    if (cancelRef.current) { setPhase('idle'); return; }

    /* ---- speaking timeline (only if the transcript carries [mm:ss]) ---- */
    const speakAt = (tt) => {
      if (!dlg.hasTimestamps) return null;
      let cur = null;
      for (let i = 0; i < dlg.timed.length; i += 1) {
        if (dlg.timed[i].t == null) continue;
        if (dlg.timed[i].t <= tt) cur = dlg.timed[i].pid;
        else break;
      }
      return cur;
    };
    const partyIndex = (pid) => parties.findIndex((p) => p.id === pid);

    /* ---- per-party paraverbal ---- */
    const ps = paraRef.current;
    const globalPara = (() => {
      if (ps.length <= 4) return null;
      const volMean = meanBy(ps, (x) => x.rms) || 1e-6;
      const maxRms = Math.max(...ps.map((x) => x.rms), 1e-6);
      return {
        windows: ps.length,
        volNorm: clamp(volMean / maxRms, 0, 1),
        volVar: clamp(stdevBy(ps, (x) => x.rms) / volMean, 0, 2),
        pitchNorm: clamp(mapLog100(meanBy(ps, (x) => x.centroid), 120, 2600) / 100, 0, 1),
        pitchVar: clamp(stdevBy(ps, (x) => x.centroid) / 900, 0, 1),
        pace: clamp(meanBy(ps, (x) => (x.flux > volMean * 0.2 ? 1 : 0)) * 3.4, 0, 1),
      };
    })();
    const paraForParty = (pid) => {
      if (!dlg.hasTimestamps) return { pv: globalPara, shared: true };
      const win = ps.filter((x) => speakAt(x.t) === pid);
      if (win.length <= 4) return { pv: globalPara, shared: true };
      const volMean = meanBy(win, (x) => x.rms) || 1e-6;
      const maxRms = Math.max(...ps.map((x) => x.rms), 1e-6);
      return {
        shared: false,
        pv: {
          windows: win.length,
          volNorm: clamp(volMean / maxRms, 0, 1),
          volVar: clamp(stdevBy(win, (x) => x.rms) / volMean, 0, 2),
          pitchNorm: clamp(mapLog100(meanBy(win, (x) => x.centroid), 120, 2600) / 100, 0, 1),
          pitchVar: clamp(stdevBy(win, (x) => x.centroid) / 900, 0, 1),
          pace: clamp(meanBy(win, (x) => (x.flux > volMean * 0.2 ? 1 : 0)) * 3.4, 0, 1),
        },
      };
    };

    /* ---- per-party non-verbal aggregate ---- */
    const aggregateNV = (fr) => {
      const wp = fr.filter((f) => f.pose);
      const wf = fr.filter((f) => f.face);
      if (!fr.length) return null;
      let gSum = 0;
      let mSum = 0;
      let nn = 0;
      for (let i = 1; i < fr.length; i += 1) {
        if (fr[i - 1].pose && fr[i].pose) {
          gSum += (dist2(fr[i - 1].pose.wristL, fr[i].pose.wristL) + dist2(fr[i - 1].pose.wristR, fr[i].pose.wristR)) / 2;
          mSum += dist2(fr[i - 1].pose.centroid, fr[i].pose.centroid);
          nn += 1;
        }
      }
      return {
        framesTotal: fr.length,
        poseCoverage: wp.length / fr.length,
        faceCoverage: wf.length / fr.length,
        lean: meanBy(wp, (f) => f.pose.leanDeg),
        openness: meanBy(wp, (f) => f.pose.openness),
        defensive: meanBy(wp, (f) => f.pose.defensive),
        bodyTension: meanBy(wp, (f) => f.pose.tension),
        gesture: nn ? gSum / nn : 0,
        movement: nn ? mSum / nn : 0,
        smile: meanBy(wf, (f) => f.face.smile),
        engagement: meanBy(wf, (f) => f.face.engagement),
        faceTension: meanBy(wf, (f) => f.face.tension),
        eyeContact: wf.length ? wf.filter((f) => f.face.eyeContact).length / wf.length : 0,
      };
    };

    /* ---- verbal: real /analyze per party (in parallel) ---- */
    setPhase('verbal');
    const vT0 = performance.now();
    const verbalByPid = {};
    await Promise.all(parties.map(async (p) => {
      const txt = (dlg.perPartyText[p.id] || '').trim();
      if (txt.length <= 10) { verbalByPid[p.id] = null; return; }
      try {
        verbalByPid[p.id] = await postAnalyze(txt);
      } catch (e) {
        console.error(`[SANTINEL video] /analyze failed for ${p.id}`, e);
        verbalByPid[p.id] = null;
      }
    }));
    M.apiMs = Math.round(performance.now() - vT0);

    /* ---- assemble per-party data ---- */
    const pdList = parties.map((p, idx) => {
      const fr = framesRef.current[idx] || [];
      const nv = aggregateNV(fr);
      const { pv, shared } = paraForParty(p.id);
      return {
        id: p.id,
        label: p.label || p.id,
        role: p.role || '',
        objective: context.objectives[p.id] || '',
        verbal: verbalByPid[p.id],
        nv,
        pv,
        paraShared: shared,
        poseCov: nv ? nv.poseCoverage : 0,
        faceCov: nv ? nv.faceCoverage : 0,
        frameCount: fr.length,
      };
    });
    setPartiesData(pdList);

    /* ---- per-party colour-coded timeline ---- */
    const segCount = Math.max(8, Math.round(dur / 2));
    const segLen = dur / segCount;
    const maxRms = ps.length ? Math.max(...ps.map((z) => z.rms), 1e-6) : 1;
    const newTracks = parties.map((p, idx) => {
      const fr = framesRef.current[idx] || [];
      const segs = [];
      for (let k = 0; k < segCount; k += 1) {
        const t0 = k * segLen;
        const t1 = (k + 1) * segLen;
        const ff = fr.filter((f) => f.t >= t0 && f.t < t1);
        const pf = ff.filter((f) => f.pose);
        const cf = ff.filter((f) => f.face);
        let g = 0;
        let mv = 0;
        let c = 0;
        for (let i = 1; i < ff.length; i += 1) {
          if (ff[i - 1].pose && ff[i].pose) {
            g += (dist2(ff[i - 1].pose.wristL, ff[i].pose.wristL) + dist2(ff[i - 1].pose.wristR, ff[i].pose.wristR)) / 2;
            mv += dist2(ff[i - 1].pose.centroid, ff[i].pose.centroid);
            c += 1;
          }
        }
        const pw = ps.filter((x) => x.t >= t0 && x.t < t1 && (!dlg.hasTimestamps || speakAt(x.t) === p.id));
        const agg = {
          openness: meanBy(pf, (f) => f.pose.openness),
          defensive: meanBy(pf, (f) => f.pose.defensive),
          smile: meanBy(cf, (f) => f.face.smile),
          engagement: meanBy(cf, (f) => f.face.engagement),
          faceTension: meanBy(cf, (f) => f.face.tension),
          eyeContact: cf.length ? cf.filter((f) => f.face.eyeContact).length / cf.length : 0.4,
          gesture: c ? g / c : 0,
          movement: c ? mv / c : 0,
          para: pw.length ? {
            volNorm: clamp(meanBy(pw, (x) => x.rms) / maxRms, 0, 1),
            volVar: globalPara ? globalPara.volVar : 0,
            pitchVar: clamp(stdevBy(pw, (x) => x.centroid) / 900, 0, 1),
          } : null,
        };
        const score = ff.length || pw.length ? scoreSlice(agg) : 50;
        segs.push({ t0, t1, score, color: signalColor(score) });
      }
      return segs;
    });
    setTracks(newTracks);

    M.avgInferMs = M.frames ? Math.round(M.inferMs / M.frames) : 0;
    setMetrics(M);
    setProgress(1);
    setPhase('done');
    console.log(
      `[SANTINEL video] ${M.subjects} subjects · ${M.frames} frames / ${M.scanMs}ms (avg ${M.avgInferMs}ms) · `
      + `pose ${M.detPose} face ${M.detFace} · para ${M.paraSamples} · /analyze ${M.apiMs}ms · models ${M.modelLoadMs}ms`
    );
  };

  const cancel = () => { cancelRef.current = true; };
  const busy = phase === 'scanning' || phase === 'verbal';

  /* ---- synthesis (memoised over the raw measured data + language) ---- */
  const enriched = useMemo(() => {
    if (!partiesData.length) return [];
    return partiesData.map((pd, i) => {
      const prof = deriveProfile(pd, lang);
      return { ...pd, index: i, prof };
    });
  }, [partiesData, lang]);

  const comparative = useMemo(() => deriveComparative(enriched, lang), [enriched, lang]);
  const scenarios = useMemo(
    () => (enriched.length ? deriveScenarios(enriched, context, lang) : []),
    [enriched, context, lang],
  );
  const perParty = useMemo(() => enriched.map((pd) => {
    const opp = enriched.find((o) => o.id !== pd.id);
    const tiers = deriveTiers(pd, pd.prof, lang);
    const paths = deriveStrategicPaths(pd, pd.prof, opp, pd.objective, lang);
    return { pd, tiers, paths };
  }), [enriched, lang]);
  const combined = useMemo(
    () => (enriched.length && scenarios.length ? deriveCombined(enriched, comparative, scenarios, lang) : ''),
    [enriched, comparative, scenarios, lang],
  );

  const seek = (tt) => { if (videoRef.current) videoRef.current.currentTime = tt; };

  return (
    <div className="si-page va">
      <h2 className="si-h2">{L.videoTitle}</h2>
      <p className="lc-sub">{L.videoSubtitle}</p>

      <ContextBar context={context} setContext={setContext} lang={lang} />

      {!fileUrl && (
        <div
          className={`si-voice-drop${dragOver ? ' si-voice-drop--over' : ''}`}
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current && inputRef.current.click()}
          onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && inputRef.current && inputRef.current.click()}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); acceptFile(e.dataTransfer.files && e.dataTransfer.files[0]); }}
        >
          <span className="si-voice-drop-icon" aria-hidden="true">{'\u{1F3AC}'}</span>
          <span className="si-voice-drop-text">{L.videoUploadPrompt}</span>
          <span className="si-voice-drop-formats">{L.videoFormats}</span>
          <input
            ref={inputRef}
            type="file"
            accept=".mp4,.mov,.webm,video/mp4,video/quicktime,video/webm"
            onChange={(e) => acceptFile(e.target.files && e.target.files[0])}
            hidden
          />
        </div>
      )}

      {fileUrl && (
        <div className="va-main">
            <div className="va-stage">
              <video
                ref={videoRef}
                className="va-video"
                src={fileUrl}
                controls
                playsInline
                crossOrigin="anonymous"
                onLoadedMetadata={(e) => setDuration(e.currentTarget.duration || 0)}
                onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime || 0)}
                onSeeked={(e) => setCurrentTime(e.currentTarget.currentTime || 0)}
              />
              <canvas ref={canvasRef} className="va-overlay" />
            </div>

            <div className="va-file">
              <span aria-hidden="true">{'\u{1F39E}\u{FE0F}'}</span>
              <span className="si-voice-file-name">{fileName}</span>
              {fileSize > 0 && <span className="si-voice-file-size">{formatSize(fileSize)}</span>}
              <span className={`va-model va-model--${modelState}`}>
                {modelState === 'loading' ? L.loadingModels
                  : modelState === 'ready' ? L.modelsReady
                    : modelState === 'error' ? L.modelLoadFail : L.modelsIdle}
              </span>
            </div>

            {phase === 'done' && duration > 0 && tracks.length > 0 && (
              <PartyTimeline
                tracks={tracks}
                parties={context.parties}
                duration={duration}
                current={currentTime}
                onSeek={seek}
                lang={lang}
              />
            )}

            <label className="si-field-label" htmlFor="va-transcript">{L.videoTranscriptLabel}</label>
            <textarea
              id="va-transcript"
              className="si-textarea"
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder={L.videoTranscriptPlaceholder}
            />
            {dlgInfo && (
              <p className="va-dlg-info">
                {dlgInfo.labeled
                  ? <>{L.ctxParsedFrom}: <b>{dlgInfo.speakers.join(', ')}</b>{dlgInfo.hasTimestamps ? ` · ${L.ctxTimestamps}` : ''}</>
                  : L.ctxNoLabels}
              </p>
            )}

            <div className="si-actions">
              {!busy ? (
                <button type="button" className="si-btn si-btn--primary" onClick={analyze} disabled={modelState === 'loading'}>
                  {modelState === 'loading' ? L.loadingModels : L.analyzeVideo}
                </button>
              ) : (
                <button type="button" className="si-btn si-btn--ghost" onClick={cancel}>
                  {L.cancel} · {Math.round(progress * 100)}%
                </button>
              )}
              <button type="button" className="si-btn si-btn--ghost" onClick={resetAll}>{L.clear}</button>
            </div>

            {busy && (
              <div className="va-progress">
                <div className="va-progress-bar" style={{ width: `${Math.round(progress * 100)}%` }} />
                <span>{phase === 'verbal' ? L.analyzingVerbal : L.scanningFrames}</span>
              </div>
            )}
            {modelState === 'error' && <div className="lc-hint">{L.modelLoadFail}</div>}
            {error && <div className="si-error">{error}</div>}

            {phase !== 'done' && (
              <HelpPanel lang={lang} steps={[L.videoStep1, L.videoStep2, L.videoStep3, L.videoStep4]} />
            )}
        </div>
      )}

      {phase === 'done' && enriched.length > 0 && (
        <div className="va-results">
          <ContextFallbackNote context={context} lang={lang} />
          {combined && (
            <div className="va-integrated">
              <span className="si-field-label">{L.combinedCoaching}</span>
              <p>{combined}</p>
            </div>
          )}

          <ComparativePanel enriched={enriched} comparative={comparative} lang={lang} />
          <ScenarioPanel scenarios={scenarios} lang={lang} />

          <span className="si-field-label va-section-h">{L.perPartyTitle}</span>
          <div className="va-pcards">
            {perParty.map(({ pd, tiers, paths }) => (
              <ProfileCard
                key={pd.id}
                pd={pd}
                prof={pd.prof}
                tiers={tiers}
                paths={paths}
                index={pd.index}
                lang={lang}
              />
            ))}
          </div>

          {metrics && (
            <div className="va-metrics">
              <span className="si-field-label">{L.metrics}</span>
              <code>
                {metrics.subjects} subjects · scan {metrics.scanMs}ms / {metrics.frames}f (avg {metrics.avgInferMs}ms)
                · pose {metrics.detPose} · face {metrics.detFace} · para {metrics.paraSamples}
                · /analyze {metrics.apiMs}ms · models {metrics.modelLoadMs}ms
              </code>
            </div>
          )}
        </div>
      )}
    </div>
  );
}



/* -------------------------------------------------------------------------- */
/*  App shell                                                                 */
/* -------------------------------------------------------------------------- */

const NAV_PAGES = ['dashboard', 'live', 'voice', 'video', 'history', 'scripts', 'profile', 'settings', 'billing'];

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [darkMode, setDarkMode] = useState(true);
  const [language, setLanguage] = useState('en');
  const [token, setTokenState] = useState(getToken);
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    setAuthReady(true);
  }, []);

  useEffect(() => {
    setAuthReady(true);
  }, []);

  const L = t[language];

  const handleLogout = useCallback(async () => {
    try {
      await logout();
    } finally {
      clearToken();
      setTokenState(null);
    }
  }, []);

  // On load, try to restore a session from the refresh cookie.
  useEffect(() => {
    let alive = true;
    ensureFreshToken()
      .then(() => { if (alive) setTokenState(getToken()); })
      .catch(() => { if (alive) setTokenState(null); })
      .finally(() => { if (alive) setAuthReady(true); });
    return () => { alive = false; };
  }, []);

  // While signed in: refresh ahead of expiry, and drop to the login screen
  // if the session is lost mid-use (e.g. a 401 from /analyze).
  useEffect(() => {
    if (!token) return undefined;
    const id = setInterval(() => {
      ensureFreshToken().catch(() => handleLogout());
    }, 60000);
    const onLost = () => setTokenState(null);
    window.addEventListener(AUTH_LOST_EVENT, onLost);
    return () => {
      clearInterval(id);
      window.removeEventListener(AUTH_LOST_EVENT, onLost);
    };
  }, [token, handleLogout]);

  if (!authReady) {
    return (
      <div className={`si-root ${darkMode ? 'si-dark' : 'si-light'}`}>
        <div className="si-splash">
          <span className="si-splash-dot" />
          SANTINEL
        </div>
      </div>
    );
  }

  if (!token) {
    return (
      <div className={`si-root ${darkMode ? 'si-dark' : 'si-light'}`}>
        <LoginPage
          lang={language}
          darkMode={darkMode}
          onToggleLang={() => setLanguage(language === 'en' ? 'ro' : 'en')}
          onToggleTheme={() => setDarkMode(!darkMode)}
          onAuthed={(tok) => {
            setTokenState(tok);
            setCurrentPage('dashboard');
          }}
        />
      </div>
    );
  }

  return (
    <div className={`si-root ${darkMode ? 'si-dark' : 'si-light'}`}>
      <header className="si-topbar">
        <div className="si-topbar-inner">
          <h1 className="si-brand">SANTINEL</h1>
          <div className="si-topbar-actions">
            <button type="button" className="si-chip" onClick={() => setDarkMode(!darkMode)}>
              {darkMode ? '☀️' : '\u{1F319}'}
            </button>
            <button
              type="button"
              className="si-chip"
              onClick={() => setLanguage(language === 'en' ? 'ro' : 'en')}
            >
              {language === 'en' ? 'RO' : 'EN'}
            </button>
          </div>
        </div>
      </header>

      <div className="si-shell">
        <nav className="si-sidebar">
          {NAV_PAGES.map((page) => (
            <button
              key={page}
              type="button"
              onClick={() => setCurrentPage(page)}
              className={`si-nav-item${currentPage === page ? ' si-nav-item--active' : ''}`}
            >
              {L[page]}
            </button>
          ))}
          <button
            type="button"
            className="si-nav-item si-nav-item--logout"
            onClick={handleLogout}
          >
            {L.logout}
          </button>
        </nav>

        <main className="si-main">
          {currentPage === 'dashboard' && <AnalyzePage lang={language} />}
          {currentPage === 'live' && <LiveCoaching lang={language} />}
          {currentPage === 'voice' && <VoiceAnalysis lang={language} />}
          {currentPage === 'video' && <VideoAnalysis lang={language} />}
          {currentPage !== 'dashboard' && currentPage !== 'live' && currentPage !== 'voice' && currentPage !== 'video' && (
            <div className="si-page si-empty-page">
              <h2 className="si-h2">{L[currentPage]}</h2>
              <p>Coming soon…</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

