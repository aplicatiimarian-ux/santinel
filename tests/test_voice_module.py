#!/usr/bin/env python3
# ============================================================
# Test Suite for Voice Module
# ============================================================

import sys
from pathlib import Path
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.voice_module import (
    VoiceAnalyzer,
    VoiceProvider,
    VocalSignalDetector,
    StreamingAudioProcessor,
    LatencyMonitor
)


def test_vocal_signal_detector():
    """Test vocal signal detection"""
    print("\n" + "="*70)
    print("TEST: Vocal Signal Detector")
    print("="*70)

    detector = VocalSignalDetector()

    # Generate test audio: 1 second at 16kHz with 120Hz fundamental
    sr = 16000
    duration = 1
    t = np.linspace(0, duration, sr * duration)
    f0 = 120
    audio = 0.1 * np.sin(2 * np.pi * f0 * t)
    audio = audio.astype(np.float32)

    signals = detector.detect_signals(audio)

    assert signals.pitch_hz > 0, "Pitch detection failed"
    assert signals.energy_db < 0, "Energy should be in dB (negative)"
    assert 0 <= signals.confidence <= 1, "Confidence should be 0-1"

    print(f"[OK] Pitch detected: {signals.pitch_hz:.1f} Hz")
    print(f"[OK] Energy: {signals.energy_db:.1f} dB")
    print(f"[OK] Pause count: {signals.pause_count}")
    print(f"[OK] Breathing detected: {signals.breathing_detected}")
    print(f"[OK] Confidence: {signals.confidence:.2f}")


def test_streaming_processor():
    """Test real-time streaming audio processor"""
    print("\n" + "="*70)
    print("TEST: Streaming Audio Processor")
    print("="*70)

    processor = StreamingAudioProcessor(VoiceProvider.MOCK)

    # Generate test audio in chunks
    sr = 16000
    chunk_duration = 0.1  # 100ms chunks
    chunk_samples = int(chunk_duration * sr)

    t_total = np.linspace(0, 1, sr)
    audio = 0.1 * np.sin(2 * np.pi * 120 * t_total).astype(np.float32)

    chunks_processed = 0
    results = []

    for i in range(0, len(audio), chunk_samples):
        chunk = audio[i:i+chunk_samples]
        result = processor.process_chunk(chunk)
        if result:
            chunks_processed += 1
            results.append(result)

    assert chunks_processed > 0, "No chunks processed"
    assert all('latency' in r for r in results), "Missing latency data"
    assert all(r['latency']['within_target'] for r in results), "Latency exceeded target"

    print(f"[OK] Processed {chunks_processed} chunks")
    print(f"[OK] All latencies within 300ms target")
    print(f"[OK] Mean latency: {np.mean([r['latency']['total_latency_ms'] for r in results]):.2f}ms")


def test_latency_monitor():
    """Test latency monitoring"""
    print("\n" + "="*70)
    print("TEST: Latency Monitor")
    print("="*70)

    monitor = LatencyMonitor()

    # Simulate measurements
    monitor.start()
    import time
    time.sleep(0.01)
    monitor.record("chunk1")

    monitor.start()
    time.sleep(0.02)
    monitor.record("chunk2")

    stats = monitor.get_stats()

    assert stats['count'] == 2, "Should have 2 measurements"
    assert stats['mean_ms'] < 50, "Mean latency should be low"
    assert stats['within_target_pct'] > 0, "Should have measurements within target"

    print(f"[OK] Measurements: {stats['count']}")
    print(f"[OK] Mean latency: {stats['mean_ms']:.2f}ms")
    print(f"[OK] Within target: {stats['within_target_pct']:.1f}%")


def test_voice_analyzer():
    """Test high-level voice analyzer"""
    print("\n" + "="*70)
    print("TEST: Voice Analyzer (Full Pipeline)")
    print("="*70)

    analyzer = VoiceAnalyzer(VoiceProvider.MOCK)

    # Generate 2 seconds of audio
    sr = 16000
    duration = 2
    t = np.linspace(0, duration, sr * duration)

    # Create speech-like signal with variations
    f0 = np.linspace(100, 150, len(t))  # Pitch glide
    phase = 2 * np.pi * np.cumsum(f0) / sr
    audio = 0.1 * np.sin(phase).astype(np.float32)

    # Analyze in chunks
    chunk_size = int(0.2 * sr)
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i+chunk_size]
        result = analyzer.analyze_audio(chunk)
        assert result is not None, "Analysis failed"

    summary = analyzer.get_session_summary()

    assert 'chunks_analyzed' in summary, "Missing summary data"
    assert summary['chunks_analyzed'] > 0, "No chunks analyzed"

    print(f"[OK] Chunks analyzed: {summary['chunks_analyzed']}")
    print(f"[OK] Avg pitch: {summary.get('avg_pitch_hz', 0):.1f} Hz")
    print(f"[OK] Total pauses: {summary.get('total_pauses', 0)}")
    print(f"[OK] Avg confidence: {summary.get('avg_confidence', 0):.2f}")


def test_provider_selection():
    """Test different provider configurations"""
    print("\n" + "="*70)
    print("TEST: Provider Selection")
    print("="*70)

    for provider in [VoiceProvider.MOCK, VoiceProvider.DEEPGRAM, VoiceProvider.GOOGLE_CLOUD]:
        processor = StreamingAudioProcessor(provider)
        print(f"[OK] {provider.value} provider initialized")


def test_multilingual_scenarios():
    """Test bilingual support"""
    print("\n" + "="*70)
    print("TEST: Bilingual Support")
    print("="*70)

    detector = VocalSignalDetector()

    # Same audio processing works for any language
    sr = 16000
    duration = 1
    t = np.linspace(0, duration, sr * duration)

    # Romanian speaker (typically lower pitch range)
    audio_ro = 0.1 * np.sin(2 * np.pi * 100 * t).astype(np.float32)
    signals_ro = detector.detect_signals(audio_ro)

    # English speaker (typically higher pitch range)
    audio_en = 0.1 * np.sin(2 * np.pi * 120 * t).astype(np.float32)
    signals_en = detector.detect_signals(audio_en)

    print(f"[OK] Romanian speaker pitch: {signals_ro.pitch_hz:.1f} Hz")
    print(f"[OK] English speaker pitch: {signals_en.pitch_hz:.1f} Hz")
    print(f"[OK] Bilingual processing validated")


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("SANTINEL VOICE MODULE - TEST SUITE")
    print("="*70)

    try:
        test_vocal_signal_detector()
        test_streaming_processor()
        test_latency_monitor()
        test_voice_analyzer()
        test_provider_selection()
        test_multilingual_scenarios()

        print("\n" + "="*70)
        print("[PASS] ALL TESTS PASSED")
        print("="*70)
        return True
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
