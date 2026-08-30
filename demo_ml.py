#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SANTINEL ML Enhancement Demo
Comprehensive demonstration of ML models for voice analysis, signal detection,
and script recommendations.

Features:
- Voice Model: Personality prediction from audio features
- Signal Model: Sentiment and emotion detection from text
- Script Recommender: Script effectiveness + counter-response ranking
- Bilingual (EN + RO) inference examples

Run: python demo_ml.py
"""

from core.ml_models import VoiceModelTrainer, SignalML, ScriptRecommenderML
from training.train_voice_model import VoiceModelTrainerPipeline
from training.train_signal_model import SignalModelTrainerPipeline
from training.train_recommender_model import RecommenderModelTrainerPipeline


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_voice_model_english():
    """Voice model demo in English."""
    print_section("VOICE MODEL - ENGLISH EXAMPLES")

    voice_model = VoiceModelTrainer()

    # Test case 1: Driver personality (fast pace, high energy)
    print("TEST 1: DRIVER PERSONALITY")
    driver_audio = {
        "pitch_mean": 135.0,
        "pitch_std": 22.0,
        "pace_wpm": 165.0,
        "pace_pause_ratio": 0.08,
        "energy_db": -17.0,
        "energy_variation": 7.5,
        "breathing_detected": True,
        "breathing_rate": 18.0,
        "voiced_ratio": 0.78,
    }

    personality = voice_model.predict_personality(driver_audio)
    urgency = voice_model.predict_urgency(driver_audio)
    hesitation = voice_model.detect_hesitation(driver_audio)

    print(f"Personality:      {personality.personality_type.upper()}")
    print(f"  Confidence:     {personality.confidence:.2f}")
    print(f"  Dominance:      {personality.dominance_score:.2f}")
    print(f"  Influence:      {personality.influence_score:.2f}")
    print(f"Urgency Score:    {urgency:.2f}")
    print(f"Hesitation Score: {hesitation:.2f}")

    # Test case 2: Amiable personality (slower pace, lower energy)
    print("\nTEST 2: AMIABLE PERSONALITY")
    amiable_audio = {
        "pitch_mean": 110.0,
        "pitch_std": 15.0,
        "pace_wpm": 115.0,
        "pace_pause_ratio": 0.22,
        "energy_db": -24.0,
        "energy_variation": 3.5,
        "breathing_detected": True,
        "breathing_rate": 14.0,
        "voiced_ratio": 0.72,
    }

    personality = voice_model.predict_personality(amiable_audio)
    urgency = voice_model.predict_urgency(amiable_audio)
    hesitation = voice_model.detect_hesitation(amiable_audio)

    print(f"Personality:      {personality.personality_type.upper()}")
    print(f"  Confidence:     {personality.confidence:.2f}")
    print(f"  Steadiness:     {personality.steadiness_score:.2f}")
    print(f"Urgency Score:    {urgency:.2f}")
    print(f"Hesitation Score: {hesitation:.2f}")

    # Test case 3: Expressive personality (high pitch variation, high energy)
    print("\nTEST 3: EXPRESSIVE PERSONALITY")
    expressive_audio = {
        "pitch_mean": 145.0,
        "pitch_std": 42.0,
        "pace_wpm": 155.0,
        "pace_pause_ratio": 0.12,
        "energy_db": -16.0,
        "energy_variation": 9.2,
        "breathing_detected": True,
        "breathing_rate": 17.0,
        "voiced_ratio": 0.81,
    }

    personality = voice_model.predict_personality(expressive_audio)
    print(f"Personality:      {personality.personality_type.upper()}")
    print(f"  Confidence:     {personality.confidence:.2f}")
    print(f"  Influence:      {personality.influence_score:.2f}")


def demo_signal_model_english():
    """Signal model demo in English."""
    print_section("SIGNAL MODEL - ENGLISH EXAMPLES")

    signal_model = SignalML()

    test_texts = [
        ("I'm absolutely delighted! This is fantastic news! Yes, I want to move forward immediately!", "Positive agreement"),
        ("I'm very concerned about this. I have serious doubts. This could be a problem.", "Negative concern"),
        ("Maybe, I need to think about it. Let me consider the options.", "Neutral hesitation"),
        ("I'm excited! This is amazing! What an opportunity!", "Strong enthusiasm"),
    ]

    for text, label in test_texts:
        print(f"\nTEST: {label}")
        print(f"Text: \"{text}\"")

        signals = signal_model.predict_signals(text)

        print(f"  Emotion:              {signals.primary_emotion} ({signals.emotion_confidence:.2f})")
        print(f"  Sentiment:            {signals.sentiment:.2f} ({signals.sentiment_confidence:.2f})")
        print(f"  Detected Signals:     {signals.detected_signals}")
        print(f"  Micro-expressions:    {signals.micro_expressions}")
        print(f"  Urgency Score:        {signals.urgency_score:.2f}")
        print(f"  Agreement Score:      {signals.agreement_score:.2f}")
        print(f"  Hesitation Score:     {signals.hesitation_score:.2f}")


def demo_recommender_english():
    """Script recommender demo in English."""
    print_section("SCRIPT RECOMMENDER - ENGLISH EXAMPLES")

    recommender = ScriptRecommenderML()

    test_cases = [
        ({
            "pitch_mean": 135.0,
            "pitch_std": 22.0,
            "pace_wpm": 165.0,
            "energy_db": -17.0,
            "energy_variation": 7.5,
        }, "I'm very interested. What's the next step?", "closing"),

        ({
            "pitch_mean": 145.0,
            "pitch_std": 42.0,
            "pace_wpm": 155.0,
            "energy_db": -16.0,
            "energy_variation": 9.2,
        }, "This is amazing! Tell me more about it!", "cold_call"),

        ({
            "pitch_mean": 110.0,
            "pitch_std": 15.0,
            "pace_wpm": 115.0,
            "energy_db": -24.0,
            "energy_variation": 3.5,
        }, "I'm concerned about the cost. Can we discuss options?", "objection"),
    ]

    for i, (audio_data, text_data, situation) in enumerate(test_cases, 1):
        print(f"\nTEST CASE {i}: {situation.upper()}")
        print(f"Text: \"{text_data}\"")

        recommendation = recommender.recommend_script(audio_data, text_data, situation)

        print(f"  Script ID:            {recommendation.script_id}")
        print(f"  Personality:          {recommendation.personality_type.upper()}")
        print(f"  Effectiveness:        {recommendation.predicted_effectiveness:.2f}")
        print(f"  Confidence:           {recommendation.confidence:.2f}")
        print(f"  Counter-responses:")

        for response, score in recommendation.counter_responses[:2]:
            print(f"    - {response} ({score:.2f})")


def demo_voice_model_romanian():
    """Voice model demo in Romanian."""
    print_section("VOICE MODEL - ROMANIAN EXAMPLES")

    voice_model = VoiceModelTrainer()

    print("TEST: DETECTARE PERSONALITATE DIN VOCE")
    audio_data = {
        "pitch_mean": 135.0,
        "pitch_std": 22.0,
        "pace_wpm": 165.0,
        "pace_pause_ratio": 0.08,
        "energy_db": -17.0,
        "energy_variation": 7.5,
        "breathing_detected": True,
        "breathing_rate": 18.0,
        "voiced_ratio": 0.78,
    }

    personality = voice_model.predict_personality(audio_data)

    print(f"Personalitate Detectată:  {personality.personality_type.upper()}")
    print(f"  Încredere:              {personality.confidence:.2f}")
    print(f"  Dominanță:              {personality.dominance_score:.2f}")
    print(f"Urgență:                  {voice_model.predict_urgency(audio_data):.2f}")


def demo_signal_model_romanian():
    """Signal model demo in Romanian."""
    print_section("SIGNAL MODEL - ROMANIAN EXAMPLES")

    signal_model = SignalML()

    test_texts = [
        ("Sunt extrem de mulțumit! Aceasta este minunată! Da, vreau să merg mai departe imediat!", "Acord pozitiv"),
        ("Sunt îngrijorat cu privire la aceasta. Am îndoieli grave.", "Îngrijorare negativă"),
        ("Poate, trebuie să mă gândesc la asta. Să iau în considerare opțiunile.", "Ezitare neutră"),
    ]

    for text, label in test_texts:
        print(f"\nTEST: {label}")
        print(f"Text: \"{text}\"")

        signals = signal_model.predict_signals(text)

        print(f"  Emoție:               {signals.primary_emotion} ({signals.emotion_confidence:.2f})")
        print(f"  Sentiment:            {signals.sentiment:.2f}")
        print(f"  Semnale Detectate:    {signals.detected_signals}")
        print(f"  Scor Urgență:         {signals.urgency_score:.2f}")
        print(f"  Scor Acord:           {signals.agreement_score:.2f}")


def demo_training_pipelines():
    """Demonstrate training pipelines."""
    print_section("TRAINING PIPELINES DEMO")

    print("1. VOICE MODEL TRAINING PIPELINE")
    print("-" * 70)

    voice_pipeline = VoiceModelTrainerPipeline(output_dir="models")
    voice_result = voice_pipeline.train("data/voice_training")

    print(f"Status:         {voice_result.get('status', 'unknown')}")
    print(f"Samples:        {voice_result.get('samples', 'N/A')}")
    print(f"Model Type:     {voice_result.get('model_type', 'N/A')}")

    print("\n2. SIGNAL MODEL TRAINING PIPELINE")
    print("-" * 70)

    signal_pipeline = SignalModelTrainerPipeline(output_dir="models")
    signal_result = signal_pipeline.train("data/signal_training.json")

    print(f"Status:         {signal_result.get('status', 'unknown')}")
    print(f"Samples:        {signal_result.get('samples', 'N/A')}")

    print("\n3. RECOMMENDER MODEL TRAINING PIPELINE")
    print("-" * 70)

    recommender_pipeline = RecommenderModelTrainerPipeline(output_dir="models")
    recommender_result = recommender_pipeline.train("data/recommender_training.json")

    print(f"Status:         {recommender_result.get('status', 'unknown')}")
    print(f"Samples:        {recommender_result.get('samples', 'N/A')}")


def main():
    """Run all ML demos."""
    print("\n" + "="*70)
    print("  SANTINEL ML ENHANCEMENT DEMONSTRATION")
    print("  Phase 12: Voice Analysis, Signal Detection, Script Recommendations")
    print("="*70)

    # English demos
    demo_voice_model_english()
    demo_signal_model_english()
    demo_recommender_english()

    # Romanian demos
    demo_voice_model_romanian()
    demo_signal_model_romanian()

    # Training pipelines
    demo_training_pipelines()

    print_section("ML ENHANCEMENT DEMO COMPLETE")
    print("""
✓ Voice Model: Personality prediction from audio features
  - Detects: pitch, pace, energy, breathing patterns
  - Outputs: Personality type + confidence + DISC scores

✓ Signal Model: Sentiment & emotion detection from text
  - Detects: 7 emotions (anger, joy, fear, sadness, surprise, trust, disgust)
  - Measures: Sentiment (-1.0 to 1.0), urgency, agreement, hesitation
  - Languages: English + Romanian

✓ Script Recommender: Script effectiveness + personality matching
  - Predicts: Personality from audio (first 30 seconds)
  - Predicts: Script effectiveness for personality×situation
  - Ranks: Counter-responses by effectiveness

✓ Training Pipelines: Data processing and model training
  - Voice pipeline: Audio preprocessing + feature extraction
  - Signal pipeline: Text normalization + sentiment/emotion training
  - Recommender pipeline: Personality + effectiveness training

Next Steps:
  1. Integrate ML models with API gateway
  2. Deploy voice analysis to negotiation calls
  3. Use signal detection in real-time coaching
  4. A/B test script recommendations against baseline
  5. Continuously retrain on new call outcomes
""")


if __name__ == "__main__":
    main()
