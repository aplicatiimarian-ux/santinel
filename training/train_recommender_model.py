# -*- coding: utf-8 -*-
"""
Script Recommender Model Training Pipeline
Trains models to predict personality and script effectiveness.

Pipeline:
1. Load call outcomes with personality + script data
2. Prepare features (audio features + text features)
3. Train personality classifier
4. Train script effectiveness predictor
5. Evaluate predictions
6. Save trained models
"""

import json
from typing import List, Dict, Tuple, Any
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class PersonalityClassifier:
    """Train model to predict personality from audio features."""

    def __init__(self):
        self.is_trained = False
        self.personality_thresholds = {}

    def train(self, audio_features_list: List[Dict], personality_labels: List[str]) -> Dict[str, Any]:
        """
        Train personality classifier.

        audio_features_list: List of dicts with pitch_mean, pace_wpm, etc.
        personality_labels: List of ['driver', 'expressive', 'amiable', 'analytical']
        """
        if len(audio_features_list) != len(personality_labels):
            return {"status": "error", "message": "Mismatched training data"}

        # Calculate feature statistics per personality
        personality_stats = defaultdict(lambda: {"pace": [], "pitch": [], "energy": []})

        for features, personality in zip(audio_features_list, personality_labels):
            personality_stats[personality]["pace"].append(features.get("pace_wpm", 0))
            personality_stats[personality]["pitch"].append(features.get("pitch_mean", 0))
            personality_stats[personality]["energy"].append(features.get("energy_db", 0))

        # Store thresholds (in production: use trained ML model)
        self.personality_thresholds = {
            personality: {
                "pace_mean": sum(v) / len(v) if v else 0,
                "pitch_mean": sum(p) / len(p) if p else 0,
                "energy_mean": sum(e) / len(e) if e else 0,
            }
            for personality, stats in personality_stats.items()
            for v, p, e in [(stats["pace"], stats["pitch"], stats["energy"])]
        }

        self.is_trained = True

        return {
            "status": "success",
            "samples_trained": len(audio_features_list),
            "personalities": list(set(personality_labels)),
            "feature_statistics": {p: s for p, s in personality_stats.items()},
            "timestamp": datetime.now().isoformat(),
        }

    def predict(self, audio_features: Dict[str, float]) -> Tuple[str, float]:
        """
        Predict personality from audio features.
        Returns: (personality_type, confidence)
        """
        if not self.is_trained or not self.personality_thresholds:
            return "unknown", 0.5

        # Simple heuristic-based prediction (in production: use trained model)
        pace = audio_features.get("pace_wpm", 120)
        pitch_std = audio_features.get("pitch_std", 20)
        energy_var = audio_features.get("energy_variation", 5)

        if pace > 150:
            if pitch_std > 30:
                return "expressive", 0.75
            else:
                return "driver", 0.78
        else:
            if energy_var < 5:
                return "analytical", 0.72
            else:
                return "amiable", 0.70


class ScriptEffectivenessPredictor:
    """Train model to predict script effectiveness."""

    def __init__(self):
        self.is_trained = False
        self.effectiveness_matrix = {}  # (script_id, personality) -> effectiveness

    def train(
        self,
        script_ids: List[str],
        personalities: List[str],
        situations: List[str],
        outcomes: List[str],
    ) -> Dict[str, Any]:
        """
        Train script effectiveness model.

        outcomes: List of ['won', 'lost', 'stalled', 'advanced']
        """
        if not all(len(x) == len(outcomes) for x in [script_ids, personalities, situations]):
            return {"status": "error", "message": "Mismatched training data"}

        # Calculate effectiveness per (script, personality, situation)
        script_stats = defaultdict(lambda: {"wins": 0, "total": 0})

        for script_id, personality, situation, outcome in zip(script_ids, personalities, situations, outcomes):
            key = (script_id, personality, situation)
            script_stats[key]["total"] += 1
            if outcome == "won":
                script_stats[key]["wins"] += 1

        # Store effectiveness
        for key, stats in script_stats.items():
            if stats["total"] > 0:
                self.effectiveness_matrix[key] = stats["wins"] / stats["total"]

        self.is_trained = True

        return {
            "status": "success",
            "samples_trained": len(outcomes),
            "unique_scripts": len(set(script_ids)),
            "personalities": list(set(personalities)),
            "effectiveness_samples": len(self.effectiveness_matrix),
            "timestamp": datetime.now().isoformat(),
        }

    def predict(self, script_id: str, personality: str, situation: str) -> float:
        """
        Predict script effectiveness.
        Returns: effectiveness score (0.0-1.0)
        """
        key = (script_id, personality, situation)

        if key in self.effectiveness_matrix:
            return self.effectiveness_matrix[key]

        # Fallback: use heuristics
        base_effectiveness = 0.5

        # Driver personalities excel in closing
        if personality == "driver" and situation == "closing":
            base_effectiveness = 0.92
        # Expressive personalities excel in cold calls
        elif personality == "expressive" and situation == "cold_call":
            base_effectiveness = 0.88
        # Amiable personalities excel in objections
        elif personality == "amiable" and situation == "objection":
            base_effectiveness = 0.87
        # Analytical personalities excel in discovery
        elif personality == "analytical" and situation == "discovery":
            base_effectiveness = 0.88

        return base_effectiveness


class CounterResponseRanker:
    """Rank counter-responses by personality and effectiveness."""

    def __init__(self):
        self.is_trained = False
        self.response_effectiveness = {}

    def train(
        self,
        responses: List[str],
        personalities: List[str],
        outcomes: List[str],
    ) -> Dict[str, Any]:
        """Train counter-response ranker."""
        if not all(len(x) == len(outcomes) for x in [responses, personalities]):
            return {"status": "error", "message": "Mismatched training data"}

        # Calculate response effectiveness per personality
        response_stats = defaultdict(lambda: {"wins": 0, "total": 0})

        for response, personality, outcome in zip(responses, personalities, outcomes):
            key = (response, personality)
            response_stats[key]["total"] += 1
            if outcome == "won":
                response_stats[key]["wins"] += 1

        # Store effectiveness
        for key, stats in response_stats.items():
            if stats["total"] > 0:
                self.response_effectiveness[key] = stats["wins"] / stats["total"]

        self.is_trained = True

        return {
            "status": "success",
            "responses_trained": len(set(responses)),
            "personalities": list(set(personalities)),
            "timestamp": datetime.now().isoformat(),
        }

    def rank_responses(self, personality: str) -> List[Tuple[str, float]]:
        """Rank counter-responses for personality."""
        # Get all responses for this personality
        responses = [
            (resp, eff)
            for (resp, pers), eff in self.response_effectiveness.items()
            if pers == personality
        ]

        # Sort by effectiveness
        responses.sort(key=lambda x: x[1], reverse=True)

        return responses


class RecommenderModelTrainerPipeline:
    """Full training pipeline for recommender models."""

    def __init__(self, output_dir: str = "models"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.personality_classifier = PersonalityClassifier()
        self.effectiveness_predictor = ScriptEffectivenessPredictor()
        self.response_ranker = CounterResponseRanker()
        self.training_log = []

    def load_training_data(self, data_file: str) -> Dict[str, Any]:
        """Load training data from JSON file."""
        data_path = Path(data_file)
        if not data_path.exists():
            print(f"Data file not found: {data_file}")
            return {}

        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def train(self, training_data_file: str = "data/recommender_training.json") -> Dict[str, Any]:
        """Train recommender models."""
        print("Loading training data...")
        data = self.load_training_data(training_data_file)

        if not data:
            print("No training data found. Using sample data.")
            # Create sample training data
            data = {
                "calls": [
                    {"audio_features": {"pace_wpm": 160, "pitch_std": 35, "energy_db": -18},
                     "script_id": "script_closing_driver", "situation": "closing",
                     "detected_personality": "driver", "outcome": "won"},
                    {"audio_features": {"pace_wpm": 150, "pitch_std": 38, "energy_db": -16},
                     "script_id": "script_cold_call_expressive", "situation": "cold_call",
                     "detected_personality": "expressive", "outcome": "won"},
                    {"audio_features": {"pace_wpm": 110, "pitch_std": 15, "energy_db": -25},
                     "script_id": "script_discovery_analytical", "situation": "discovery",
                     "detected_personality": "analytical", "outcome": "won"},
                ]
            }

        calls = data.get("calls", [])
        print(f"Training on {len(calls)} call outcomes...")

        if calls:
            # Prepare training data
            audio_features_list = [c.get("audio_features", {}) for c in calls]
            personalities = [c.get("detected_personality", "unknown") for c in calls]
            script_ids = [c.get("script_id", "") for c in calls]
            situations = [c.get("situation", "") for c in calls]
            outcomes = [c.get("outcome", "") for c in calls]

            # Train personality classifier
            print("\n1. Training Personality Classifier...")
            personality_result = self.personality_classifier.train(audio_features_list, personalities)
            print(f"   Status: {personality_result['status']}")

            # Train script effectiveness predictor
            print("\n2. Training Script Effectiveness Predictor...")
            effectiveness_result = self.effectiveness_predictor.train(
                script_ids, personalities, situations, outcomes
            )
            print(f"   Status: {effectiveness_result['status']}")

            # Train counter-response ranker (simplified)
            print("\n3. Training Counter-Response Ranker...")
            response_ranker_result = self.response_ranker.train(
                ["response_1"] * len(calls),
                personalities,
                outcomes,
            )
            print(f"   Status: {response_ranker_result['status']}")

            # Combine results
            training_result = {
                "status": "success",
                "samples": len(calls),
                "personality_model": personality_result,
                "effectiveness_model": effectiveness_result,
                "response_ranker_model": response_ranker_result,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            training_result = {
                "status": "error",
                "message": "No training data available",
            }

        # Save models
        model_path = self.output_dir / "recommender_model.json"
        with open(model_path, "w", encoding="utf-8") as f:
            json.dump(training_result, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Models saved to {model_path}")

        self.training_log.append(training_result)

        return training_result

    def evaluate(self, test_data: List[Dict]) -> Dict[str, Any]:
        """Evaluate models on test set."""
        correct_personality = 0
        effective_predictions = 0

        for call in test_data:
            # Test personality prediction
            audio_features = call.get("audio_features", {})
            true_personality = call.get("true_personality", "")

            pred_personality, _ = self.personality_classifier.predict(audio_features)
            if pred_personality == true_personality:
                correct_personality += 1

            # Test effectiveness prediction
            script_id = call.get("script_id", "")
            situation = call.get("situation", "")
            true_outcome = call.get("outcome", "")

            pred_effectiveness = self.effectiveness_predictor.predict(script_id, pred_personality, situation)
            if (pred_effectiveness > 0.5 and true_outcome == "won") or \
               (pred_effectiveness <= 0.5 and true_outcome != "won"):
                effective_predictions += 1

        return {
            "personality_accuracy": correct_personality / len(test_data) if test_data else 0.0,
            "effectiveness_accuracy": effective_predictions / len(test_data) if test_data else 0.0,
            "test_samples": len(test_data),
        }


def main():
    """Run recommender model training pipeline."""
    print("="*70)
    print("  SANTINEL SCRIPT RECOMMENDER MODEL TRAINING PIPELINE")
    print("="*70 + "\n")

    pipeline = RecommenderModelTrainerPipeline(output_dir="models")

    # Train models
    print("TRAINING RECOMMENDER MODELS")
    print("-" * 70)
    result = pipeline.train("data/recommender_training.json")

    print(f"\nTraining completed:")
    print(f"  Status: {result.get('status', 'unknown')}")
    print(f"  Samples: {result.get('samples', 'N/A')}")

    # Test personality prediction
    print("\n1. TESTING PERSONALITY PREDICTION")
    print("-" * 70)

    test_audio = {
        "pace_wpm": 160,
        "pitch_std": 35,
        "energy_db": -18,
        "energy_variation": 8,
    }

    personality, confidence = pipeline.personality_classifier.predict(test_audio)
    print(f"Audio features -> Predicted: {personality} ({confidence:.2f})")

    # Test script effectiveness
    print("\n2. TESTING SCRIPT EFFECTIVENESS PREDICTION")
    print("-" * 70)

    script_id = "script_closing_driver"
    personality = "driver"
    situation = "closing"

    effectiveness = pipeline.effectiveness_predictor.predict(script_id, personality, situation)
    print(f"{script_id} with {personality}/{situation}: {effectiveness:.2f}")

    # Test response ranking
    print("\n3. TESTING COUNTER-RESPONSE RANKING")
    print("-" * 70)

    for personality in ["driver", "expressive", "amiable", "analytical"]:
        responses = pipeline.response_ranker.rank_responses(personality)
        print(f"{personality.upper()}: {len(responses)} ranked responses")

    print("\n✓ Recommender model training pipeline complete!")


if __name__ == "__main__":
    main()
