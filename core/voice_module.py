# ============================================================
# SANTINEL — VOICE MODULE
# Real-time vocal signal detection + STT integration
# ============================================================

import os
import logging
import json
import time
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


# ============================================================
# ENUMS & DATA MODELS
# ============================================================

class VoiceProvider(Enum):
    """Supported speech-to-text providers"""
    DEEPGRAM = "deepgram"
    GOOGLE_CLOUD = "google_cloud"
    OPENAI_WHISPER = "openai_whisper"
    MOCK = "mock"


@dataclass
class VocalSignals:
    """Detected vocal characteristics"""
    pitch_hz: float  # Fundamental frequency
    pitch_variance: float  # Pitch stability (low = monotone, high = expressive)
    pace_wpm: float  # Words per minute
    pace_variance: float  # Speech rate consistency
    energy_db: float  # Overall loudness
    energy_variance: float  # Loudness consistency
    breathing_detected: bool  # Detected breath sounds
    pause_count: int  # Number of pauses
    pause_duration_ms: float  # Average pause duration
    confidence: float  # 0-1 confidence score


@dataclass
class TranscriptionResult:
    """STT output"""
    text: str
    language: str  # 'en', 'ro', 'mixed'
    confidence: float  # 0-1
    duration_ms: int
    provider: str
    timestamp: str


@dataclass
class LatencyMetrics:
    """Real-time latency tracking"""
    total_latency_ms: float
    sts_latency_ms: float  # Speech-to-text latency
    signal_analysis_latency_ms: float  # Vocal signal analysis latency
    processing_latency_ms: float  # Total processing
    end_to_end_latency_ms: float  # From audio start to result
    within_target: bool  # Within 300ms target


# ============================================================
# VOCAL SIGNAL DETECTOR
# ============================================================

class VocalSignalDetector:
    """Analyzes vocal characteristics from audio signal"""

    def __init__(self, sample_rate: int = 16000):
        """
        Initialize detector
        Args:
            sample_rate: Audio sample rate in Hz (default 16kHz for speech)
        """
        self.sample_rate = sample_rate
        self.frame_duration_ms = 20  # 20ms frames for analysis
        self.hop_length = int(sample_rate * self.frame_duration_ms / 1000)

        # Thresholds for acoustic analysis
        self.silence_threshold_db = -40
        self.breath_threshold_db = -25
        self.pitch_min_hz = 50  # Minimum pitch
        self.pitch_max_hz = 400  # Maximum pitch for speech

        logger.info(f"VocalSignalDetector initialized (sample_rate={sample_rate}Hz)")

    def detect_signals(self, audio_data: np.ndarray) -> VocalSignals:
        """
        Analyze audio signal for vocal characteristics

        Args:
            audio_data: Audio samples as numpy array (mono, float32, normalized -1..1)

        Returns:
            VocalSignals with detected characteristics
        """
        start_time = time.time()

        # Compute energy (loudness) contour
        energy = self._compute_energy(audio_data)
        energy_db = 20 * np.log10(np.mean(np.abs(audio_data)) + 1e-10)
        energy_variance = float(np.std(energy))

        # Detect pauses (silence regions)
        pause_info = self._detect_pauses(audio_data, energy)

        # Estimate pitch (fundamental frequency)
        pitch_hz, pitch_variance = self._estimate_pitch(audio_data)

        # Estimate speech rate (words per minute equivalent)
        pace_wpm, pace_variance = self._estimate_pace(energy, audio_data)

        # Detect breathing/breath sounds
        breathing_detected = self._detect_breathing(energy, audio_data)

        # Aggregate confidence
        confidence = self._compute_confidence(
            pitch_hz, energy_db, pause_info['count'], breathing_detected
        )

        signals = VocalSignals(
            pitch_hz=float(pitch_hz),
            pitch_variance=float(pitch_variance),
            pace_wpm=float(pace_wpm),
            pace_variance=float(pace_variance),
            energy_db=float(energy_db),
            energy_variance=float(energy_variance),
            breathing_detected=breathing_detected,
            pause_count=pause_info['count'],
            pause_duration_ms=pause_info['avg_duration_ms'],
            confidence=confidence
        )

        elapsed = (time.time() - start_time) * 1000
        logger.debug(f"Vocal signal analysis completed in {elapsed:.1f}ms")

        return signals

    def _compute_energy(self, audio_data: np.ndarray) -> np.ndarray:
        """Compute energy envelope using sliding window"""
        frame_size = self.hop_length
        n_frames = len(audio_data) // frame_size

        energy = np.zeros(n_frames)
        for i in range(n_frames):
            frame = audio_data[i*frame_size:(i+1)*frame_size]
            energy[i] = np.sum(frame ** 2)

        return energy

    def _detect_pauses(self, audio_data: np.ndarray, energy: np.ndarray) -> Dict:
        """Detect silence/pause regions"""
        # Normalize energy
        energy_normalized = 10 * np.log10(energy + 1e-10)

        # Silence threshold
        is_silent = energy_normalized < self.silence_threshold_db

        # Find silence regions
        pause_durations = []
        in_pause = False
        pause_start = 0

        for i, silent in enumerate(is_silent):
            if silent and not in_pause:
                pause_start = i
                in_pause = True
            elif not silent and in_pause:
                pause_duration = (i - pause_start) * self.frame_duration_ms
                pause_durations.append(pause_duration)
                in_pause = False

        # Handle last frame if in pause
        if in_pause:
            pause_duration = (len(is_silent) - pause_start) * self.frame_duration_ms
            pause_durations.append(pause_duration)

        # Filter out very short pauses (< 100ms)
        significant_pauses = [p for p in pause_durations if p >= 100]

        return {
            'count': len(significant_pauses),
            'avg_duration_ms': float(np.mean(significant_pauses)) if significant_pauses else 0,
            'max_duration_ms': float(np.max(significant_pauses)) if significant_pauses else 0
        }

    def _estimate_pitch(self, audio_data: np.ndarray) -> Tuple[float, float]:
        """Estimate fundamental frequency using autocorrelation"""
        # Simple autocorrelation-based pitch detection
        frame_size = int(0.05 * self.sample_rate)  # 50ms frame

        if len(audio_data) < frame_size * 2:
            return 0.0, 0.0

        pitches = []

        for start in range(0, len(audio_data) - frame_size, frame_size // 2):
            frame = audio_data[start:start+frame_size]

            # Skip silent frames
            if np.max(np.abs(frame)) < 0.01:
                continue

            # Apply window
            window = np.hanning(len(frame))
            frame = frame * window

            # Autocorrelation
            autocorr = np.correlate(frame, frame, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            autocorr = autocorr / (autocorr[0] + 1e-10)

            # Find peak in pitch range
            min_lag = int(self.sample_rate / self.pitch_max_hz)
            max_lag = int(self.sample_rate / self.pitch_min_hz)

            if max_lag < len(autocorr):
                lag = np.argmax(autocorr[min_lag:max_lag]) + min_lag
                pitch = self.sample_rate / lag if lag > 0 else 0

                if self.pitch_min_hz < pitch < self.pitch_max_hz:
                    pitches.append(pitch)

        if pitches:
            mean_pitch = float(np.mean(pitches))
            pitch_variance = float(np.std(pitches))
        else:
            mean_pitch, pitch_variance = 0.0, 0.0

        return mean_pitch, pitch_variance

    def _estimate_pace(self, energy: np.ndarray, audio_data: np.ndarray) -> Tuple[float, float]:
        """Estimate speech rate (words per minute equivalent)"""
        # Detect speech vs silence
        energy_normalized = 10 * np.log10(energy + 1e-10)
        is_speech = energy_normalized > self.silence_threshold_db

        # Speech duration in seconds
        speech_frames = np.sum(is_speech)
        speech_duration_s = (speech_frames * self.frame_duration_ms) / 1000

        if speech_duration_s < 0.1:
            return 0.0, 0.0

        # Estimate words from phoneme rate
        # Assuming ~3-4 phonemes per word, 10 phonemes per second average
        phoneme_rate = 12  # Conservative estimate
        words_estimated = (speech_duration_s * phoneme_rate) / 3.5
        wpm = (words_estimated / speech_duration_s) * 60 if speech_duration_s > 0 else 0

        # Estimate variance in pace (variability)
        # Split into 500ms windows
        window_samples = int(0.5 * self.sample_rate)
        pace_window = []

        for i in range(0, len(audio_data) - window_samples, window_samples):
            window = audio_data[i:i+window_samples]
            window_energy = np.mean(np.abs(window))
            if window_energy > 0.01:
                pace_window.append(window_energy)

        pace_variance = float(np.std(pace_window)) if pace_window else 0.0

        return float(wpm), float(pace_variance)

    def _detect_breathing(self, energy: np.ndarray, audio_data: np.ndarray) -> bool:
        """Detect breath sounds (characteristic fricative noise)"""
        # Breath sounds typically have specific spectral characteristics
        # For now, detect as high-energy low-amplitude events between speech

        energy_normalized = 10 * np.log10(energy + 1e-10)
        near_silence = (energy_normalized < self.silence_threshold_db) & \
                       (energy_normalized > self.breath_threshold_db)

        # If we detect regions between silence and speech, likely breathing
        detected = np.sum(near_silence) > len(energy) * 0.05  # > 5% of frames

        return bool(detected)

    def _compute_confidence(self, pitch: float, energy_db: float,
                           pause_count: int, breathing: bool) -> float:
        """Compute overall confidence in analysis"""
        confidence = 0.5

        if pitch > 0:
            confidence += 0.2  # Good pitch detection

        if energy_db > -40:
            confidence += 0.15  # Good signal level

        if pause_count > 0:
            confidence += 0.1  # Detected pauses (sign of natural speech)

        if breathing:
            confidence += 0.05  # Detected breathing

        return min(confidence, 1.0)


# ============================================================
# STREAMING AUDIO PROCESSOR
# ============================================================

class StreamingAudioProcessor:
    """Real-time streaming audio processing"""

    def __init__(self, provider: VoiceProvider = VoiceProvider.MOCK):
        """
        Initialize streaming processor
        Args:
            provider: STT provider to use
        """
        self.provider = provider
        self.detector = VocalSignalDetector()
        self.sample_rate = 16000
        self.buffer = np.array([], dtype=np.float32)
        self.chunk_size = int(0.1 * self.sample_rate)  # 100ms chunks

        # Latency tracking
        self.latency_metrics = None
        self.start_time = None

        logger.info(f"StreamingAudioProcessor initialized (provider={provider.value})")

    def process_chunk(self, audio_chunk: np.ndarray) -> Optional[Dict]:
        """
        Process audio chunk in real-time

        Args:
            audio_chunk: Audio samples (float32, -1..1)

        Returns:
            Dict with intermediate results or None if processing
        """
        if self.start_time is None:
            self.start_time = time.time()

        # Append to buffer
        self.buffer = np.append(self.buffer, audio_chunk)

        # Process when we have enough data
        if len(self.buffer) >= self.chunk_size:
            result = self._process_buffer()
            self.buffer = np.array([], dtype=np.float32)
            return result

        return None

    def _process_buffer(self) -> Dict:
        """Process accumulated audio buffer"""
        chunk_start = time.time()

        # Analyze vocal signals
        signal_start = time.time()
        signals = self.detector.detect_signals(self.buffer)
        signal_latency = (time.time() - signal_start) * 1000

        # Transcribe (in real implementation)
        stt_start = time.time()
        transcription = self._transcribe_chunk(self.buffer)
        stt_latency = (time.time() - stt_start) * 1000

        # Calculate latencies
        processing_latency = (time.time() - chunk_start) * 1000
        end_to_end = (time.time() - self.start_time) * 1000

        self.latency_metrics = LatencyMetrics(
            total_latency_ms=processing_latency,
            sts_latency_ms=stt_latency,
            signal_analysis_latency_ms=signal_latency,
            processing_latency_ms=processing_latency,
            end_to_end_latency_ms=end_to_end,
            within_target=processing_latency <= 300
        )

        return {
            'signals': asdict(signals),
            'transcription': asdict(transcription) if transcription else None,
            'latency': asdict(self.latency_metrics),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    def _transcribe_chunk(self, audio_chunk: np.ndarray) -> Optional[TranscriptionResult]:
        """Transcribe audio chunk (provider-dependent)"""
        duration_ms = int(len(audio_chunk) / self.sample_rate * 1000)

        if self.provider == VoiceProvider.MOCK:
            return self._mock_transcribe(duration_ms)
        elif self.provider == VoiceProvider.DEEPGRAM:
            return self._deepgram_transcribe(audio_chunk)
        elif self.provider == VoiceProvider.GOOGLE_CLOUD:
            return self._google_transcribe(audio_chunk)
        else:
            return None

    def _mock_transcribe(self, duration_ms: int) -> TranscriptionResult:
        """Mock transcription for testing"""
        return TranscriptionResult(
            text="[Mock transcription]",
            language="en",
            confidence=0.95,
            duration_ms=duration_ms,
            provider="mock",
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def _deepgram_transcribe(self, audio_chunk: np.ndarray) -> Optional[TranscriptionResult]:
        """Deepgram STT integration"""
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            logger.warning("DEEPGRAM_API_KEY not set, using mock")
            return self._mock_transcribe(0)

        # TODO: Implement Deepgram API call
        # For now, return mock
        logger.info("Deepgram integration placeholder")
        return None

    def _google_transcribe(self, audio_chunk: np.ndarray) -> Optional[TranscriptionResult]:
        """Google Cloud Speech-to-Text integration"""
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set, using mock")
            return self._mock_transcribe(0)

        # TODO: Implement Google Cloud Speech API call
        # For now, return mock
        logger.info("Google Cloud Speech integration placeholder")
        return None

    def reset(self):
        """Reset processor state"""
        self.buffer = np.array([], dtype=np.float32)
        self.latency_metrics = None
        self.start_time = None


# ============================================================
# LATENCY MONITOR
# ============================================================

class LatencyMonitor:
    """Monitor real-time latency performance"""

    TARGET_LATENCY_MS = 300

    def __init__(self):
        """Initialize latency monitor"""
        self.measurements = []
        self.start_time = None

    def start(self):
        """Start latency measurement"""
        self.start_time = time.time()

    def record(self, label: str = "processing") -> float:
        """Record elapsed time since start"""
        if self.start_time is None:
            return 0.0

        elapsed = (time.time() - self.start_time) * 1000
        self.measurements.append({
            'label': label,
            'latency_ms': elapsed,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'within_target': elapsed <= self.TARGET_LATENCY_MS
        })

        return elapsed

    def get_stats(self) -> Dict:
        """Get latency statistics"""
        if not self.measurements:
            return {}

        latencies = [m['latency_ms'] for m in self.measurements]

        return {
            'count': len(latencies),
            'mean_ms': float(np.mean(latencies)),
            'median_ms': float(np.median(latencies)),
            'min_ms': float(np.min(latencies)),
            'max_ms': float(np.max(latencies)),
            'std_dev_ms': float(np.std(latencies)),
            'within_target_pct': (sum(1 for m in self.measurements
                                      if m['within_target']) / len(self.measurements)) * 100,
            'target_ms': self.TARGET_LATENCY_MS
        }

    def reset(self):
        """Reset measurements"""
        self.measurements = []
        self.start_time = None


# ============================================================
# VOICE ANALYZER (Main Interface)
# ============================================================

class VoiceAnalyzer:
    """High-level interface for voice analysis"""

    def __init__(self, provider: VoiceProvider = VoiceProvider.MOCK):
        """
        Initialize voice analyzer
        Args:
            provider: STT provider
        """
        self.processor = StreamingAudioProcessor(provider)
        self.latency_monitor = LatencyMonitor()
        self.session_signals = []

        logger.info(f"VoiceAnalyzer initialized (provider={provider.value})")

    def analyze_audio(self, audio_data: np.ndarray) -> Dict:
        """
        Full analysis of audio sample

        Args:
            audio_data: Audio samples (float32, -1..1)

        Returns:
            Comprehensive analysis results
        """
        self.latency_monitor.start()

        # Process audio
        result = self.processor.process_chunk(audio_data)

        if result:
            self.session_signals.append(result)

        latency_ms = self.latency_monitor.record("full_analysis")

        return {
            'result': result,
            'latency_ms': latency_ms,
            'latency_stats': self.latency_monitor.get_stats()
        }

    def get_session_summary(self) -> Dict:
        """Get summary of entire session"""
        if not self.session_signals:
            return {}

        all_signals = [s['signals'] for s in self.session_signals]

        return {
            'chunks_analyzed': len(self.session_signals),
            'avg_pitch_hz': float(np.mean([s['pitch_hz'] for s in all_signals])),
            'avg_pace_wpm': float(np.mean([s['pace_wpm'] for s in all_signals])),
            'avg_energy_db': float(np.mean([s['energy_db'] for s in all_signals])),
            'total_pauses': sum(s['pause_count'] for s in all_signals),
            'breathing_detected': any(s['breathing_detected'] for s in all_signals),
            'avg_confidence': float(np.mean([s['confidence'] for s in all_signals])),
            'latency_stats': self.latency_monitor.get_stats()
        }


if __name__ == "__main__":
    # Example: analyze mock audio
    logger.info("VoiceAnalyzer test mode")

    analyzer = VoiceAnalyzer(VoiceProvider.MOCK)

    # Generate synthetic audio (1 second, 16kHz)
    sample_rate = 16000
    duration_s = 1
    t = np.linspace(0, duration_s, sample_rate * duration_s)

    # Simulate speech-like signal (fundamental + harmonics)
    f0 = 120  # Male voice fundamental
    audio = 0.1 * np.sin(2 * np.pi * f0 * t)  # Fundamental
    audio += 0.05 * np.sin(2 * np.pi * f0 * 2 * t)  # 2nd harmonic
    audio = audio.astype(np.float32)

    result = analyzer.analyze_audio(audio)
    logger.info(f"Analysis result: {json.dumps(result, indent=2, default=str)}")

    summary = analyzer.get_session_summary()
    logger.info(f"Session summary: {json.dumps(summary, indent=2, default=str)}")
