#!/usr/bin/env python3
# ============================================================
# SANTINEL — VOICE FEATURES DEMO
# Bilingual test scenarios (EN + RO), real-time analysis
# ============================================================

import os
import json
import logging
import sys
from pathlib import Path
import numpy as np
from typing import Dict, List
from dataclasses import asdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.voice_module import (
    VoiceAnalyzer,
    VoiceProvider,
    VocalSignalDetector,
    StreamingAudioProcessor
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# SYNTHETIC AUDIO GENERATORS
# ============================================================

class SyntheticAudioGenerator:
    """Generate synthetic test audio scenarios"""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def generate_speech_like(self, duration_s: float, f0_hz: float = 120,
                            variability: float = 1.0) -> np.ndarray:
        """
        Generate synthetic speech-like signal

        Args:
            duration_s: Duration in seconds
            f0_hz: Fundamental frequency (pitch)
            variability: Pitch/energy variability (0-1)

        Returns:
            Audio signal (float32, -1..1)
        """
        samples = int(duration_s * self.sample_rate)
        t = np.linspace(0, duration_s, samples)

        # Fundamental frequency with slight modulation (naturalness)
        f0_modulated = f0_hz * (1 + variability * 0.1 * np.sin(2 * np.pi * 2 * t))

        # Synthesize signal with harmonics
        phase = 2 * np.pi * np.cumsum(f0_modulated) / self.sample_rate
        signal = 0.1 * np.sin(phase)  # Fundamental
        signal += 0.05 * np.sin(2 * phase)  # 2nd harmonic
        signal += 0.03 * np.sin(3 * phase)  # 3rd harmonic

        # Add noise (vocal fry, breathiness)
        noise = np.random.randn(samples) * 0.02
        signal = signal + noise

        # Apply envelope (natural speech rises/falls in energy)
        envelope = np.ones_like(signal)
        for i in range(0, samples, self.sample_rate // 10):
            envelope[i:min(i+self.sample_rate//20, samples)] *= (0.5 + np.random.rand() * 0.5)

        signal = signal * envelope

        return np.clip(signal, -1, 1).astype(np.float32)

    def generate_scenario_confident_pitch(self) -> np.ndarray:
        """Confident speaker: high pitch, low variability, steady pace"""
        # Strong, confident: higher pitch, steady tone
        logger.info("Generating: Confident speaker (high pitch, steady)")
        return self.generate_speech_like(duration_s=3, f0_hz=140, variability=0.3)

    def generate_scenario_hesitant_pitch(self) -> np.ndarray:
        """Hesitant speaker: lower pitch, high variability, irregular pauses"""
        # Hesitant: lower pitch, more modulation
        logger.info("Generating: Hesitant speaker (low pitch, variable)")
        audio = self.generate_speech_like(duration_s=3, f0_hz=100, variability=0.8)

        # Add artificial pauses (silence regions)
        pause_positions = [0.5, 1.2, 1.8, 2.3]
        for pos in pause_positions:
            start_sample = int(pos * self.sample_rate)
            pause_length = int(0.2 * self.sample_rate)
            audio[start_sample:start_sample+pause_length] *= 0.1

        return audio

    def generate_scenario_energetic(self) -> np.ndarray:
        """Energetic speaker: high energy, fast pace"""
        logger.info("Generating: Energetic speaker (high energy, fast)")
        # Fast, energetic: higher pitch, less pausing
        return self.generate_speech_like(duration_s=3, f0_hz=150, variability=0.4)

    def generate_scenario_calm_deliberate(self) -> np.ndarray:
        """Calm, deliberate speech: low pitch, clear pauses"""
        logger.info("Generating: Calm speaker (low pitch, deliberate)")
        audio = self.generate_speech_like(duration_s=4, f0_hz=95, variability=0.2)

        # Add clear pauses (negotiation thinking time)
        pause_positions = [1.0, 2.0, 2.8]
        for pos in pause_positions:
            start_sample = int(pos * self.sample_rate)
            pause_length = int(0.4 * self.sample_rate)
            audio[start_sample:start_sample+pause_length] *= 0.05

        return audio

    def generate_scenario_stressed_rushed(self) -> np.ndarray:
        """Stressed, rushed speech: high pitch, variable energy"""
        logger.info("Generating: Stressed/rushed speaker (high pitch, irregular)")
        # Stressed: high pitch, irregular energy
        audio = self.generate_speech_like(duration_s=2.5, f0_hz=155, variability=0.9)

        # Simulate breathing/gasping
        breath_positions = [0.5, 1.0, 1.5, 2.0]
        for pos in breath_positions:
            start_sample = int(pos * self.sample_rate)
            breath_length = int(0.15 * self.sample_rate)
            # Increase amplitude briefly (breath sound)
            audio[start_sample:start_sample+breath_length] *= 1.5

        return audio


# ============================================================
# TEST SCENARIOS
# ============================================================

class VoiceTestScenarios:
    """Bilingual test scenarios for negotiations"""

    # English scenarios
    ENGLISH_SCENARIOS = {
        "confident": {
            "speaker": "Negotiator (You)",
            "text": "I understand your position. However, our analysis shows a 15% increase is justified by market conditions.",
            "analysis_points": ["assertive tone", "clear articulation", "steady pace"]
        },
        "hesitant": {
            "speaker": "Counterparty",
            "text": "Well, um... I think... maybe we could... look at alternative options?",
            "analysis_points": ["uncertainty signals", "filler words", "pitch variation"]
        },
        "energetic": {
            "speaker": "Negotiator (You)",
            "text": "This is a fantastic opportunity! We can expand together and both benefit significantly!",
            "analysis_points": ["enthusiasm", "high energy", "rapid delivery"]
        },
        "calm_deliberate": {
            "speaker": "Counterparty",
            "text": "Let me think through this carefully. I need to understand all the implications before committing.",
            "analysis_points": ["thoughtful pausing", "measured speech", "strategic thinking"]
        },
        "stressed_rushed": {
            "speaker": "Negotiator (You)",
            "text": "Look, we need to decide NOW! The market window is closing and we're running out of time!",
            "analysis_points": ["urgency signals", "rapid speech", "higher stress indicators"]
        }
    }

    # Romanian scenarios (Negociere în limba română)
    ROMANIAN_SCENARIOS = {
        "confident": {
            "speaker": "Negociator (Tu)",
            "text": "Înțeleg poziția dvs. Cu toate acestea, analiza noastră arată că o creștere de 15% este justificată de condițiile pieței.",
            "analysis_points": ["ton asertiv", "pronunție clară", "ritm stabil"]
        },
        "hesitant": {
            "speaker": "Contrapartidă",
            "text": "Ei bine, um... cred că... poate... am putea să ne gândim la alte opțiuni?",
            "analysis_points": ["semnale de incertitudine", "cuvinte de umplutură", "variație de ton"]
        },
        "energetic": {
            "speaker": "Negociator (Tu)",
            "text": "Aceasta este o oportunitate fantastică! Putem să expandăm împreună și ambii vom beneficia semnificativ!",
            "analysis_points": ["entuzias", "energie ridicată", "vorbire rapidă"]
        },
        "calm_deliberate": {
            "speaker": "Contrapartidă",
            "text": "Permiteți-mi să mă gândesc atent la asta. Trebuie să înțeleg toate implicațiile înainte de a mă angaja.",
            "analysis_points": ["pauze gândite", "vorbire liniștită", "gândire strategică"]
        },
        "stressed_rushed": {
            "speaker": "Negociator (Tu)",
            "text": "Ascultă, trebuie să decidem ACUM! Fereastra de piață se închide și ne scapă timpul!",
            "analysis_points": ["semnale de urgență", "vorbire rapidă", "indicatori de stres"]
        }
    }

    @classmethod
    def get_scenario(cls, language: str, scenario_type: str) -> Dict:
        """Get a specific scenario"""
        scenarios = cls.ROMANIAN_SCENARIOS if language == "ro" else cls.ENGLISH_SCENARIOS
        return scenarios.get(scenario_type)


# ============================================================
# DEMO RUNNER
# ============================================================

class VoiceFeatureDemo:
    """Run voice feature demonstrations"""

    def __init__(self):
        self.generator = SyntheticAudioGenerator()
        self.analyzer = VoiceAnalyzer(VoiceProvider.MOCK)

    def run_single_scenario(self, language: str, scenario_type: str) -> Dict:
        """
        Run analysis on a single scenario

        Args:
            language: 'en' or 'ro'
            scenario_type: confident, hesitant, energetic, calm_deliberate, stressed_rushed

        Returns:
            Analysis results
        """
        scenario = VoiceTestScenarios.get_scenario(language, scenario_type)

        if not scenario:
            logger.error(f"Scenario not found: {language}/{scenario_type}")
            return {}

        logger.info(f"\n{'='*70}")
        logger.info(f"Scenario: {scenario['speaker']}")
        logger.info(f"Language: {'Romanian' if language == 'ro' else 'English'}")
        logger.info(f"Type: {scenario_type.replace('_', ' ').title()}")
        logger.info(f"Text: \"{scenario['text']}\"")
        logger.info(f"Analysis points: {', '.join(scenario['analysis_points'])}")
        logger.info(f"{'='*70}")

        # Generate audio based on scenario type
        if scenario_type == "confident":
            audio = self.generator.generate_scenario_confident_pitch()
        elif scenario_type == "hesitant":
            audio = self.generator.generate_scenario_hesitant_pitch()
        elif scenario_type == "energetic":
            audio = self.generator.generate_scenario_energetic()
        elif scenario_type == "calm_deliberate":
            audio = self.generator.generate_scenario_calm_deliberate()
        elif scenario_type == "stressed_rushed":
            audio = self.generator.generate_scenario_stressed_rushed()
        else:
            audio = self.generator.generate_speech_like(3)

        # Create new analyzer for each scenario
        analyzer = VoiceAnalyzer(VoiceProvider.MOCK)
        logger.info("Analyzing vocal signals...")

        # Process in chunks (streaming)
        chunk_size = int(0.2 * 16000)  # 200ms chunks
        all_signals = []

        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i+chunk_size]
            result = analyzer.processor.process_chunk(chunk)

            if result:
                all_signals.append(result)
                logger.info(f"  Chunk {len(all_signals)}: pitch={result['signals']['pitch_hz']:.1f}Hz, "
                           f"pace={result['signals']['pace_wpm']:.1f}wpm, "
                           f"latency={result['latency']['total_latency_ms']:.1f}ms")

        # Compute summary from collected signals
        if all_signals:
            signals_list = [s['signals'] for s in all_signals]
            latencies = [s['latency']['total_latency_ms'] for s in all_signals]

            summary = {
                'chunks_analyzed': len(all_signals),
                'avg_pitch_hz': float(np.mean([s['pitch_hz'] for s in signals_list if s['pitch_hz'] > 0])),
                'avg_pace_wpm': float(np.mean([s['pace_wpm'] for s in signals_list])),
                'avg_energy_db': float(np.mean([s['energy_db'] for s in signals_list])),
                'total_pauses': sum(s['pause_count'] for s in signals_list),
                'breathing_detected': any(s['breathing_detected'] for s in signals_list),
                'avg_confidence': float(np.mean([s['confidence'] for s in signals_list])),
                'latency_stats': {
                    'mean_ms': float(np.mean(latencies)),
                    'median_ms': float(np.median(latencies)),
                    'min_ms': float(np.min(latencies)),
                    'max_ms': float(np.max(latencies)),
                    'within_target_pct': (sum(1 for l in latencies if l <= 300) / len(latencies)) * 100
                }
            }
        else:
            summary = {}

        return {
            'scenario': {
                'language': language,
                'type': scenario_type,
                'speaker': scenario['speaker'],
                'text': scenario['text']
            },
            'signals': all_signals,
            'summary': summary
        }

    def run_all_scenarios(self) -> List[Dict]:
        """Run all test scenarios"""
        results = []
        scenario_types = ["confident", "hesitant", "energetic", "calm_deliberate", "stressed_rushed"]

        logger.info("\n" + "="*70)
        logger.info("SANTINEL VOICE FEATURES DEMO - FULL TEST SUITE")
        logger.info("="*70)

        # English scenarios
        logger.info("\n[ENGLISH SCENARIOS]")
        for scenario_type in scenario_types:
            result = self.run_single_scenario("en", scenario_type)
            results.append(result)

        # Romanian scenarios
        logger.info("\n\n[ROMANIAN SCENARIOS]")
        for scenario_type in scenario_types:
            result = self.run_single_scenario("ro", scenario_type)
            results.append(result)

        return results

    def print_comparative_analysis(self, results: List[Dict]):
        """Print comparative analysis across scenarios"""
        logger.info("\n" + "="*70)
        logger.info("COMPARATIVE ANALYSIS ACROSS SCENARIOS")
        logger.info("="*70)

        for lang in ["en", "ro"]:
            lang_label = "English" if lang == "en" else "Romanian"
            logger.info(f"\n[{lang_label} Scenarios]")
            logger.info(f"{'Scenario':<20} {'Pitch':<12} {'Energy':<12} {'Pauses':<8} {'Latency':<15} {'Confidence':<12}")
            logger.info("-" * 85)

            for result in results:
                if result.get('scenario', {}).get('language') == lang:
                    scenario = result['scenario']['type'].replace('_', ' ').title()
                    summary = result.get('summary', {})

                    pitch = f"{summary.get('avg_pitch_hz', 0):.0f} Hz"
                    energy = f"{summary.get('avg_energy_db', 0):.1f} dB"
                    pauses = f"{summary.get('total_pauses', 0)}"
                    latency_stats = summary.get('latency_stats', {})
                    latency = f"{latency_stats.get('mean_ms', 0):.1f} ms"
                    confidence = f"{summary.get('avg_confidence', 0):.0%}"

                    logger.info(f"{scenario:<20} {pitch:<12} {energy:<12} {pauses:<8} {latency:<15} {confidence:<12}")

    def print_latency_report(self, results: List[Dict]):
        """Print latency performance report"""
        logger.info("\n" + "="*70)
        logger.info("REAL-TIME LATENCY PERFORMANCE REPORT")
        logger.info("="*70)

        all_latencies = []

        for result in results:
            latency_stats = result.get('summary', {}).get('latency_stats', {})
            if latency_stats and 'mean_ms' in latency_stats:
                all_latencies.append(latency_stats)

        if all_latencies:
            mean_latencies = [l['mean_ms'] for l in all_latencies]
            within_target = [l['within_target_pct'] for l in all_latencies]

            logger.info(f"Target latency: ≤300ms")
            logger.info(f"Overall mean latency: {np.mean(mean_latencies):.2f}ms")
            logger.info(f"Latency range: {np.min(mean_latencies):.2f}ms - {np.max(mean_latencies):.2f}ms")
            logger.info(f"Within target: {np.mean(within_target):.1f}%")

            logger.info("\nPer-scenario performance:")
            for i, l in enumerate(all_latencies):
                logger.info(f"  Scenario {i+1}: mean={l['mean_ms']:.2f}ms, "
                           f"median={l['median_ms']:.2f}ms, "
                           f"min={l['min_ms']:.2f}ms, max={l['max_ms']:.2f}ms, "
                           f"within_target={l['within_target_pct']:.1f}%")
        else:
            logger.info("No latency data available")

    def save_results(self, results: List[Dict], output_file: str = "voice_demo_results.json"):
        """Save results to JSON file"""
        # Convert numpy types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_types(item) for item in obj]
            return obj

        converted = convert_types(results)

        output_path = Path(__file__).parent / output_file
        with open(output_path, 'w') as f:
            json.dump(converted, f, indent=2)

        logger.info(f"\nResults saved to: {output_path}")


# ============================================================
# MAIN
# ============================================================

def main():
    """Run the full demo suite"""
    logger.info("SANTINEL Voice Features MVP - Bilingual Demo")
    logger.info("="*70)

    demo = VoiceFeatureDemo()

    # Run all scenarios
    results = demo.run_all_scenarios()

    # Print analysis
    demo.print_comparative_analysis(results)
    demo.print_latency_report(results)

    # Save results
    demo.save_results(results)

    logger.info("\n" + "="*70)
    logger.info("✓ Demo completed successfully")
    logger.info("="*70)

    return results


if __name__ == "__main__":
    main()
