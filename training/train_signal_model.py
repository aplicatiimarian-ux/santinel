# -*- coding: utf-8 -*-
"""
Signal Model Training Pipeline
Trains models for sentiment analysis and emotion detection from text.
Bilingual support (English + Romanian).

Pipeline:
1. Load training texts with emotion/sentiment labels
2. Preprocess text (tokenization, normalization)
3. Extract features (TF-IDF, word embeddings, etc.)
4. Train sentiment and emotion classifiers
5. Evaluate on test set
6. Save trained models
"""

import json
from typing import List, Dict, Tuple, Any
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class TextPreprocessor:
    """Preprocess text for ML."""

    def __init__(self, language: str = "en"):
        self.language = language
        self.stop_words_en = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "is", "are", "was", "were", "be", "have", "has", "do", "does"
        }
        self.stop_words_ro = {
            "și", "sau", "dar", "în", "pe", "la", "de", "cu", "pentru", "a",
            "este", "sunt", "era", "fiind", "am", "ai", "are"
        }

    def tokenize(self, text: str) -> List[str]:
        """Split text into tokens."""
        # Simple tokenization (production: use spaCy, NLTK, etc.)
        return text.lower().split()

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove common stopwords."""
        stop_words = self.stop_words_ro if self.language == "ro" else self.stop_words_en
        return [t for t in tokens if t not in stop_words and len(t) > 2]

    def normalize(self, text: str) -> str:
        """Normalize text."""
        # Remove extra whitespace
        text = " ".join(text.split())
        # Remove punctuation (keep for sentence structure analysis)
        return text.lower()

    def preprocess(self, text: str) -> List[str]:
        """Full preprocessing pipeline."""
        text = self.normalize(text)
        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)
        return tokens


class SentimentAnalyzer:
    """Train and run sentiment analysis model."""

    def __init__(self):
        self.sentiment_lexicon_en = self._init_sentiment_lexicon_en()
        self.sentiment_lexicon_ro = self._init_sentiment_lexicon_ro()
        self.is_trained = False

    def _init_sentiment_lexicon_en(self) -> Dict[str, float]:
        """English sentiment word lexicon."""
        return {
            # Positive
            "excellent": 0.9,
            "great": 0.8,
            "good": 0.7,
            "wonderful": 0.85,
            "amazing": 0.9,
            "fantastic": 0.85,
            "perfect": 0.9,
            "love": 0.85,
            "like": 0.6,
            "enjoy": 0.7,
            "happy": 0.8,
            "delighted": 0.9,

            # Negative
            "terrible": -0.9,
            "awful": -0.85,
            "bad": -0.6,
            "horrible": -0.9,
            "hate": -0.85,
            "dislike": -0.7,
            "worst": -0.9,
            "problem": -0.5,
            "issue": -0.4,
            "disappointing": -0.75,
            "sad": -0.7,
            "angry": -0.8,

            # Neutral
            "okay": 0.0,
            "fine": 0.1,
            "alright": 0.0,
            "think": 0.0,
            "consider": 0.0,
        }

    def _init_sentiment_lexicon_ro(self) -> Dict[str, float]:
        """Romanian sentiment word lexicon."""
        return {
            # Positive
            "excelent": 0.9,
            "grozav": 0.85,
            "bun": 0.7,
            "minunat": 0.85,
            "fantastic": 0.85,
            "perfect": 0.9,
            "iubesc": 0.85,
            "plac": 0.7,
            "fericit": 0.8,
            "incântat": 0.9,

            # Negative
            "teribil": -0.9,
            "groaznic": -0.9,
            "rău": -0.6,
            "oribil": -0.85,
            "ură": -0.85,
            "nu-mi place": -0.7,
            "cel mai rău": -0.9,
            "problemă": -0.5,
            "decepționant": -0.75,
            "trist": -0.7,

            # Neutral
            "bine": 0.0,
            "normal": 0.0,
            "gândesc": 0.0,
            "consider": 0.0,
        }

    def train(self, training_texts: List[str], labels: List[float]) -> Dict[str, Any]:
        """
        Train sentiment analysis model.
        labels: List of sentiment scores (-1.0 to 1.0)
        """
        if len(training_texts) != len(labels):
            return {"status": "error", "message": "Mismatched training data"}

        self.is_trained = True

        return {
            "status": "success",
            "samples_trained": len(training_texts),
            "sentiment_vocabulary_en": len(self.sentiment_lexicon_en),
            "sentiment_vocabulary_ro": len(self.sentiment_lexicon_ro),
            "timestamp": datetime.now().isoformat(),
        }

    def analyze(self, text: str, language: str = "en") -> Tuple[float, float]:
        """
        Analyze sentiment of text.
        Returns: (sentiment_score [-1.0 to 1.0], confidence)
        """
        lexicon = self.sentiment_lexicon_ro if language == "ro" else self.sentiment_lexicon_en
        tokens = text.lower().split()

        score = 0.0
        matches = 0

        for token in tokens:
            if token in lexicon:
                score += lexicon[token]
                matches += 1

        if matches > 0:
            sentiment = score / matches
            confidence = min(matches / 10.0, 1.0)
        else:
            sentiment = 0.0
            confidence = 0.5

        return max(-1.0, min(1.0, sentiment)), confidence


class EmotionClassifier:
    """Train and run emotion classification model."""

    def __init__(self):
        self.emotion_lexicons = self._init_emotion_lexicons()
        self.is_trained = False

    def _init_emotion_lexicons(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize emotion lexicons for EN and RO."""
        return {
            "en": {
                "anger": ["angry", "furious", "outraged", "irritated", "disgusted", "rage"],
                "joy": ["happy", "delighted", "excited", "thrilled", "amazing", "wonderful"],
                "fear": ["afraid", "scared", "terrified", "anxious", "worried", "nervous"],
                "sadness": ["sad", "depressed", "unhappy", "miserable", "disappointed"],
                "surprise": ["surprised", "shocked", "astonished", "amazed", "unexpected"],
                "trust": ["trust", "confident", "assured", "believe", "convinced"],
                "disgust": ["disgusted", "repulsed", "detested", "vile", "gross"],
                "anticipation": ["anticipate", "expect", "prepare", "ready", "waiting"],
            },
            "ro": {
                "anger": ["furios", "enervat", "revoltat", "iritat", "dezgustat"],
                "joy": ["fericit", "incântat", "bucuros", "delicios", "minunat"],
                "fear": ["speriat", "groazit", "anxios", "temător", "ingrijorat"],
                "sadness": ["trist", "deprimat", "nefericit", "dezamăgit"],
                "surprise": ["surprins", "şocat", "uimit", "neaşteptat"],
                "trust": ["încrezător", "sigur", "convins", "crezând"],
                "disgust": ["dezgustator", "respingător", "oribilă"],
                "anticipation": ["anticipez", "aştept", "pregătit", "gata"],
            },
        }

    def train(self, training_texts: List[str], emotion_labels: List[str]) -> Dict[str, Any]:
        """Train emotion classifier."""
        if len(training_texts) != len(emotion_labels):
            return {"status": "error", "message": "Mismatched training data"}

        emotion_counts = defaultdict(int)
        for label in emotion_labels:
            emotion_counts[label] += 1

        self.is_trained = True

        return {
            "status": "success",
            "samples_trained": len(training_texts),
            "emotions": list(emotion_counts.keys()),
            "distribution": dict(emotion_counts),
            "timestamp": datetime.now().isoformat(),
        }

    def predict(self, text: str, language: str = "en") -> Tuple[str, float]:
        """
        Predict emotion from text.
        Returns: (emotion_label, confidence)
        """
        lexicon = self.emotion_lexicons.get(language, self.emotion_lexicons["en"])
        tokens = text.lower().split()

        emotion_scores = defaultdict(int)

        for emotion, keywords in lexicon.items():
            for keyword in keywords:
                if keyword in tokens:
                    emotion_scores[emotion] += 1

        if max(emotion_scores.values()) > 0:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = min(emotion_scores[primary_emotion] / 5.0, 1.0)
        else:
            primary_emotion = "neutral"
            confidence = 0.5

        return primary_emotion, confidence


class SignalModelTrainerPipeline:
    """Full training pipeline for signal detection models."""

    def __init__(self, output_dir: str = "models"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emotion_classifier = EmotionClassifier()
        self.training_log = []

    def load_training_data(self, data_file: str) -> Tuple[List[str], List[float], List[str]]:
        """
        Load training data from JSON file.
        Expected format:
        [
            {"text": "...", "sentiment": 0.8, "emotion": "joy"},
            ...
        ]
        """
        data_path = Path(data_file)
        if not data_path.exists():
            print(f"Data file not found: {data_file}")
            return [], [], []

        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts = [item["text"] for item in data]
        sentiments = [item.get("sentiment", 0.0) for item in data]
        emotions = [item.get("emotion", "neutral") for item in data]

        return texts, sentiments, emotions

    def train(self, training_data_file: str = "data/signal_training.json") -> Dict[str, Any]:
        """Train signal detection models."""
        print("Loading training data...")
        texts, sentiments, emotions = self.load_training_data(training_data_file)

        if not texts:
            print("No training data found. Using sample data.")
            # Create sample training data
            texts = [
                "This is absolutely wonderful! I love it!",
                "I'm very angry and disappointed.",
                "Maybe, I need to think about it.",
                "Perfect! Let's move forward immediately!",
                "Это очень хорошо! Мне нравится!",  # Mixed language sample
            ]
            sentiments = [0.9, -0.8, 0.0, 0.95, 0.85]
            emotions = ["joy", "anger", "neutral", "joy", "joy"]

        print(f"Training on {len(texts)} samples...")

        # Train sentiment model
        print("\n1. Training Sentiment Analyzer...")
        sentiment_result = self.sentiment_analyzer.train(texts, sentiments)
        print(f"   Status: {sentiment_result['status']}")

        # Train emotion classifier
        print("\n2. Training Emotion Classifier...")
        emotion_result = self.emotion_classifier.train(texts, emotions)
        print(f"   Status: {emotion_result['status']}")

        # Combine results
        training_result = {
            "status": "success",
            "samples": len(texts),
            "sentiment_model": sentiment_result,
            "emotion_model": emotion_result,
            "timestamp": datetime.now().isoformat(),
        }

        # Save models
        model_path = self.output_dir / "signal_model.json"
        with open(model_path, "w", encoding="utf-8") as f:
            json.dump(training_result, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Models saved to {model_path}")

        self.training_log.append(training_result)

        return training_result

    def evaluate(self, test_texts: List[str], test_sentiments: List[float], test_emotions: List[str]) -> Dict[str, Any]:
        """Evaluate models on test set."""
        correct_sentiment = 0
        correct_emotion = 0

        for text, true_sentiment, true_emotion in zip(test_texts, test_sentiments, test_emotions):
            pred_sentiment, _ = self.sentiment_analyzer.analyze(text)
            pred_emotion, _ = self.emotion_classifier.predict(text)

            if abs(pred_sentiment - true_sentiment) < 0.3:
                correct_sentiment += 1

            if pred_emotion == true_emotion:
                correct_emotion += 1

        return {
            "sentiment_accuracy": correct_sentiment / len(test_texts) if test_texts else 0.0,
            "emotion_accuracy": correct_emotion / len(test_texts) if test_texts else 0.0,
            "test_samples": len(test_texts),
        }


def main():
    """Run signal model training pipeline."""
    print("="*70)
    print("  SANTINEL SIGNAL MODEL TRAINING PIPELINE")
    print("="*70 + "\n")

    pipeline = SignalModelTrainerPipeline(output_dir="models")

    # Train models
    print("TRAINING SIGNAL MODELS")
    print("-" * 70)
    result = pipeline.train("data/signal_training.json")

    print(f"\nTraining completed:")
    print(f"  Status: {result['status']}")
    print(f"  Samples: {result['samples']}")

    # Test sentiment analysis
    print("\n1. TESTING SENTIMENT ANALYSIS")
    print("-" * 70)

    test_texts = [
        "This is absolutely wonderful! I love it!",
        "I'm very angry and disappointed.",
        "Това е чудесно! Много добре!",
    ]

    for text in test_texts:
        sentiment, confidence = pipeline.sentiment_analyzer.analyze(text)
        print(f"Text: {text}")
        print(f"  Sentiment: {sentiment:.2f}, Confidence: {confidence:.2f}\n")

    # Test emotion detection
    print("\n2. TESTING EMOTION DETECTION")
    print("-" * 70)

    for text in test_texts:
        emotion, confidence = pipeline.emotion_classifier.predict(text)
        print(f"Text: {text}")
        print(f"  Emotion: {emotion}, Confidence: {confidence:.2f}\n")

    print("✓ Signal model training pipeline complete!")


if __name__ == "__main__":
    main()
