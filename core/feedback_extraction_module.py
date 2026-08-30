# -*- coding: utf-8 -*-
"""
Feedback Extraction Module for SANTINEL
Real-time signal detection and close probability scoring.

Bilingual (EN + RO):
  - 20+ verbal signals: agreement, doubt, objection, stalling, questions,
    urgency, budget, competitive behavior
  - 15+ vocal signals: pitch, pace, energy, breathing, pauses, tone, emphasis,
    silence, interruptions, laughter
  - Close probability scoring (0-10): real-time likelihood of reaching agreement
  - Integration with all 8 psychology/neuroscience frameworks

Feedback extraction combines behavioral linguistics (what people say and how they say it)
with the prior frameworks (psychology, neuroscience, narrative, somatic) to produce
a single, actionable score: "Close probability." This is the negotiation's vital sign.

Romanian triggers live in core/feedback_extraction_keywords_ro.py; the English set is `EN`
below. Tokenization, diacritic folding and Snowball stemming are shared with other
frameworks via core/text_norm.py.
"""

from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.text_norm import find_all
    from core.feedback_extraction_keywords_ro import RO
except ImportError:  # imported flat (core/ dir on path)
    from text_norm import find_all
    from feedback_extraction_keywords_ro import RO

__all__ = ["VerbalsSignal", "VocalsSignal", "FeedbackExtractionModule"]


class VerbalsSignal(Enum):
    """The 20+ verbal signal categories."""
    AGREEMENT = "agreement"
    DOUBT = "doubt"
    OBJECTION = "objection"
    STALLING = "stalling"
    QUESTIONS = "questions"
    URGENCY = "urgency"
    BUDGET = "budget"
    COMPETITIVE = "competitive"


class VocalsSignal(Enum):
    """The 15+ vocal signal categories."""
    HIGH_PITCH = "high_pitch"
    LOW_PITCH = "low_pitch"
    FAST_PACE = "fast_pace"
    SLOW_PACE = "slow_pace"
    HIGH_ENERGY = "high_energy"
    LOW_ENERGY = "low_energy"
    SHALLOW_BREATHING = "shallow_breathing"
    DEEP_BREATHING = "deep_breathing"
    HESITATION_PAUSES = "hesitation_pauses"
    THINKING_PAUSES = "thinking_pauses"
    WARM_TONE = "warm_tone"
    COLD_TONE = "cold_tone"
    EMPHASIS_POSITIVE = "emphasis_positive"
    EMPHASIS_NEGATIVE = "emphasis_negative"
    LAUGHTER = "laughter"


# English lexicon — same shape as core/feedback_extraction_keywords_ro.RO
EN = {
    "verbals": {
        "agreement": [
            "yes", "absolutely", "sounds good", "works for me", "that works",
            "agreed", "let's do it", "i'm in", "count me in", "let's move forward",
            "i agree", "perfect", "exactly", "that's right", "you got it",
        ],
        "doubt": [
            "not sure", "unclear", "hesitant", "might", "possibly", "maybe",
            "i don't know", "uncertain", "questionable", "could go either way",
            "on the fence", "iffy", "up in the air", "somewhat", "it depends",
        ],
        "objection": [
            "but", "however", "problem", "concern", "issue", "can't", "won't",
            "disagree", "that won't work", "i'm not comfortable", "that's not right",
            "resistance", "that's not acceptable", "i have concerns", "problematic",
        ],
        "stalling": [
            "let me think about it", "need more time", "let me check", "come back later",
            "give me time", "need to discuss", "have to consult", "talk to", "eventually",
            "i'll get back to you", "not now", "not yet", "later", "soon",
        ],
        "questions": [
            "what if", "how would", "when", "where", "why", "tell me more",
            "can you", "would you", "is it possible", "have you considered",
            "what about", "any other options", "clarify", "explain", "details",
        ],
        "urgency": [
            "now", "today", "asap", "deadline", "urgent", "rushing", "hurry",
            "immediately", "time sensitive", "soon", "before", "limited window",
            "closing date", "can't wait", "must happen", "critical",
        ],
        "budget": [
            "budget", "price", "cost", "afford", "investment", "money", "expense",
            "financial", "funds", "capital", "payment", "rate", "margin", "pricing",
            "how much", "what's the cost", "payment terms", "roi", "value",
        ],
        "competitive": [
            "competition", "alternatives", "other offers", "compared to", "versus",
            "your competitor", "other options", "better deal", "elsewhere", "shop around",
            "benchmarking", "competitive advantage", "they offer", "comparing prices",
            "other vendors", "looking at", "exploring options",
        ],
    },
    "vocals": {
        "high_pitch": [
            "pitch rises", "voice rises", "higher tone", "pitched up", "shrill",
            "strained voice", "tight throat", "squeaky", "tense voice",
        ],
        "low_pitch": [
            "deep voice", "low tone", "grounded tone", "bass", "settled voice",
            "confident tone", "authoritative", "resonant", "calm voice",
        ],
        "fast_pace": [
            "rapid speech", "speaking quickly", "accelerated pace", "rushed words",
            "hurried", "breathless", "quick delivery", "talking fast", "staccato",
        ],
        "slow_pace": [
            "measured pace", "slow speech", "deliberate", "taking time", "pause between",
            "thoughtful delivery", "pondering", "careful words", "slow and steady",
        ],
        "high_energy": [
            "energetic", "animated", "excited tone", "enthusiastic", "lively",
            "upbeat", "engaged", "passionate", "vibrant", "dynamic",
        ],
        "low_energy": [
            "flat tone", "monotone", "unenthusiastic", "disengaged", "apathetic",
            "tired voice", "deflated", "resigned", "passive", "dull",
        ],
        "shallow_breathing": [
            "short breath", "panting", "catching breath", "rapid breathing",
            "breathless", "gasping", "tight breathing", "chest breathing",
        ],
        "deep_breathing": [
            "deep breath", "belly breathing", "grounded breathing", "steady breath",
            "slow breathing", "calm breathing", "full breath", "diaphragm breathing",
        ],
        "hesitation_pauses": [
            "uh", "um", "err", "long pause", "trailing off", "stuttering",
            "filled pauses", "vocal filler", "hesitation", "long silence",
        ],
        "thinking_pauses": [
            "pause to think", "quiet moment", "considering", "reflecting",
            "taking time", "gathering thoughts", "thoughtful pause",
        ],
        "warm_tone": [
            "warm voice", "friendly tone", "approachable", "inclusive", "inviting",
            "genuine", "personable", "open tone", "soft edge", "caring",
        ],
        "cold_tone": [
            "cold voice", "distant tone", "formal", "curt", "sharp tone",
            "withdrawn", "detached", "clinical", "defensive tone", "hard edge",
        ],
        "emphasis_positive": [
            "stress on positive", "highlights benefit", "emphasizes gain",
            "upward inflection on positive", "strength in delivery", "accent on good",
        ],
        "emphasis_negative": [
            "stress on negative", "highlights risk", "emphasizes loss", "downward inflection",
            "accent on problem", "weight on concern", "emphasis on doubt",
        ],
        "laughter": [
            "laugh", "laughter", "chuckle", "nervous laugh", "forced laugh",
            "genuine laugh", "light laugh", "hearty laugh", "giggles",
        ],
    },
}

_SIGNAL_WEIGHT = {
    # Verbal signals: contribution to close probability
    "agreement": +2.0,
    "doubt": -1.0,
    "objection": -1.5,
    "stalling": -1.0,
    "questions": +0.5,  # engagement is positive
    "urgency": +0.5,  # time pressure can accelerate close
    "budget": +0.5,  # discussing details is positive
    "competitive": -0.5,  # shopping around delays close
    # Vocal signals
    "high_pitch": -0.5,  # stress/tension
    "low_pitch": +0.5,  # confidence
    "fast_pace": -0.5,  # anxiety/pressure
    "slow_pace": +0.5,  # deliberation/confidence
    "high_energy": +1.0,  # engagement
    "low_energy": -1.0,  # disengagement
    "shallow_breathing": -1.0,  # stress
    "deep_breathing": +1.0,  # calm/grounded
    "hesitation_pauses": -0.5,  # uncertainty
    "thinking_pauses": +0.5,  # deliberation (neutral/positive)
    "warm_tone": +1.0,  # rapport
    "cold_tone": -1.0,  # distance
    "emphasis_positive": +0.5,  # highlighting benefits
    "emphasis_negative": -0.5,  # highlighting risks
    "laughter": +0.5,  # rapport/lightness (can be deflection, but usually positive)
}


class FeedbackExtractionModule:
    """
    Real-time feedback extraction and close probability scoring.
    Detects 20+ verbal signals and 15+ vocal signals from negotiation discourse.
    Produces a single, actionable close probability score (0-10).
    Integrates with all 8 prior frameworks for holistic assessment.
    """

    def _scan(self, text: str, domain: str) -> List[Dict]:
        en = find_all(text, EN[domain], lang="en", first_phrase_only=False)
        ro = find_all(text, RO[domain], lang="ro", first_phrase_only=False)
        seen = set()
        out = []
        for hit in en + ro:
            sig = (hit["category"], hit["keyword"])
            if sig in seen:
                continue
            seen.add(sig)
            out.append(hit)
        return out

    # -- Verbal signal detection -----------------------------------

    _VERBAL_KEYS = tuple(s.value for s in VerbalsSignal)

    def detect_verbal_signals(self, text: str) -> Dict:
        """Detect all verbal signals in the text."""
        hits = self._scan(text, "verbals")
        counts = {k: 0 for k in self._VERBAL_KEYS}
        matched = {k: [] for k in self._VERBAL_KEYS}

        for h in hits:
            counts[h["category"]] += 1
            matched[h["category"]].append(h["keyword"])

        total = sum(counts.values())
        scores = {k: counts[k] for k in self._VERBAL_KEYS}

        return {
            "verbal_counts": counts,
            "verbal_matched": matched,
            "verbal_total": total,
            "verbal_scores": scores,
        }

    # -- Vocal signal detection -----------------------------------

    _VOCAL_KEYS = tuple(s.value for s in VocalsSignal)

    def detect_vocal_signals(self, text: str) -> Dict:
        """Detect vocal signals indicated in the text."""
        hits = self._scan(text, "vocals")
        counts = {k: 0 for k in self._VOCAL_KEYS}
        matched = {k: [] for k in self._VOCAL_KEYS}

        for h in hits:
            counts[h["category"]] += 1
            matched[h["category"]].append(h["keyword"])

        total = sum(counts.values())

        return {
            "vocal_counts": counts,
            "vocal_matched": matched,
            "vocal_total": total,
        }

    # -- Close probability scoring --------------------------------

    def calculate_close_probability(self, your_text: str, their_text: str = "") -> Dict:
        """
        Calculate close probability (0-10) based on verbal + vocal signals.
        If their_text is provided, weights it more heavily (they're the decision-maker).
        """
        # Analyze both speakers
        your_verbals = self.detect_verbal_signals(your_text)
        your_vocals = self.detect_vocal_signals(your_text)

        if their_text:
            their_verbals = self.detect_verbal_signals(their_text)
            their_vocals = self.detect_vocal_signals(their_text)
        else:
            their_verbals = {"verbal_counts": {k: 0 for k in self._VERBAL_KEYS}}
            their_vocals = {"vocal_counts": {k: 0 for k in self._VOCAL_KEYS}}

        # Calculate weighted scores
        your_score = self._calculate_signal_score(your_verbals, your_vocals, weight=0.4)
        their_score = self._calculate_signal_score(their_verbals, their_vocals, weight=0.6)

        # Combine into close probability (0-10)
        raw_score = your_score + their_score
        close_probability = max(0.0, min(10.0, raw_score))

        # Determine interpretation
        interpretation = self._interpret_close_probability(close_probability)

        return {
            "your_signal_score": round(your_score, 2),
            "their_signal_score": round(their_score, 2),
            "close_probability": round(close_probability, 1),
            "interpretation": interpretation,
            "your_verbals": your_verbals,
            "their_verbals": their_verbals if their_text else None,
            "your_vocals": your_vocals,
            "their_vocals": their_vocals if their_text else None,
        }

    @staticmethod
    def _calculate_signal_score(verbals: Dict, vocals: Dict, weight: float) -> float:
        """Calculate signal score from verbal and vocal counts."""
        score = 0.0

        # Verbal signals
        for signal_type, count in verbals["verbal_counts"].items():
            signal_weight = _SIGNAL_WEIGHT.get(signal_type, 0.0)
            score += count * signal_weight

        # Vocal signals
        for signal_type, count in vocals["vocal_counts"].items():
            signal_weight = _SIGNAL_WEIGHT.get(signal_type, 0.0)
            score += count * signal_weight

        return score * weight

    @staticmethod
    def _interpret_close_probability(prob: float) -> str:
        """Interpret the close probability score."""
        if prob >= 8.5:
            return "READY TO CLOSE: Agreement imminent. Finalize terms."
        elif prob >= 7.0:
            return "STRONG POSITIVE: High likelihood. Address remaining objections."
        elif prob >= 5.5:
            return "CAUTIOUSLY POSITIVE: Moderate likelihood. Continue engagement."
        elif prob >= 4.0:
            return "NEUTRAL: Uncertain. Need more information or positioning."
        elif prob >= 2.0:
            return "SKEPTICAL: Low likelihood. Significant barriers remain."
        else:
            return "UNLIKELY: Major objections. Reassess fit or walk away."

    # -- Real-time feedback integration ---------------------------

    def analyze_real_time(self, your_text: str, their_text: str = "") -> Dict:
        """Real-time analysis: close probability + detailed signal breakdown."""
        close_data = self.calculate_close_probability(your_text, their_text)

        return {
            "close_probability_score": close_data["close_probability"],
            "analysis_text": close_data["interpretation"],
            "your_verbals": close_data["your_verbals"]["verbal_counts"],
            "their_verbals": close_data["their_verbals"]["verbal_counts"] if their_text else None,
            "your_vocals": close_data["your_vocals"]["vocal_counts"],
            "their_vocals": close_data["their_vocals"]["vocal_counts"] if their_text else None,
            "coaching_guidance": self._generate_coaching(close_data["close_probability"], close_data["their_verbals"] if their_text else None),
        }

    @staticmethod
    def _generate_coaching(prob: float, their_verbals: Dict = None) -> str:
        """Generate coaching based on close probability and signals."""
        if prob >= 8.5:
            return (
                "CLOSE NOW. Signals are aligned. Move to agreement and next steps.\n"
                "Risk: Over-negotiating and losing momentum. Lock it in."
            )
        elif prob >= 7.0:
            return (
                "STRONG MOMENTUM. Objections are diminishing. Anchor on points of agreement.\n"
                "Next: Address remaining concerns directly, then confirm terms."
            )
        elif prob >= 5.5:
            return (
                "STAY ENGAGED. Signals are mixed but trending positive.\n"
                "Next: Clarify unclear areas. Strengthen value proposition. Build rapport."
            )
        elif prob >= 4.0:
            return (
                "HOLD POSITION. Signals suggest they're still evaluating.\n"
                "Next: Ask direct questions about concerns. Provide more information.\n"
                "Risk: Pushing too hard now will trigger resistance."
            )
        elif prob >= 2.0:
            return (
                "SIGNIFICANT DOUBT. Multiple objections present. Slow down.\n"
                "Next: Listen more. Understand real concerns, not surface objections.\n"
                "Consider: Does this deal fit their actual needs?"
            )
        else:
            return (
                "UNLIKELY AT THIS POINT. Major barriers exist.\n"
                "Decision: Either pivot significantly (new approach, new terms) or walk.\n"
                "Continuing to pitch may damage relationship and future opportunities."
            )

    def prescribe_signal_reading(self) -> str:
        """Guidance for reading signals in real-time."""
        return (
            "REAL-TIME SIGNAL READING\n\n"
            "VERBAL SIGNALS (20+):\n"
            "Listen for the 8 categories:\n"
            "1. AGREEMENT: 'yes', 'sounds good', 'i'm in' → Close probability ↑\n"
            "2. DOUBT: 'not sure', 'maybe', 'uncertain' → Close probability ↓\n"
            "3. OBJECTION: 'but', 'problem', 'concern' → Close probability ↓\n"
            "4. STALLING: 'think about it', 'need time' → Close probability ↓\n"
            "5. QUESTIONS: 'how', 'when', 'tell me more' → Engagement, detail-seeking\n"
            "6. URGENCY: 'now', 'asap', 'deadline' → Time pressure\n"
            "7. BUDGET: 'price', 'cost', 'afford' → Negotiations getting concrete\n"
            "8. COMPETITIVE: 'alternatives', 'comparing' → Shopping around\n\n"
            "VOCAL SIGNALS (15+):\n"
            "Notice HOW they say things:\n"
            "• PITCH: High = tension/excitement. Low = confidence/calm.\n"
            "• PACE: Fast = anxiety/urgency. Slow = deliberation/caution.\n"
            "• ENERGY: High = engaged. Low = disengaged/resigned.\n"
            "• BREATHING: Shallow = stress. Deep = calm.\n"
            "• PAUSES: Hesitation = doubt. Thinking = consideration.\n"
            "• TONE: Warm = rapport. Cold = distance.\n"
            "• EMPHASIS: Positive words stressed = interest. Negative = concern.\n"
            "• LAUGHTER: Usually = comfort/rapport (unless nervous).\n\n"
            "REAL-TIME SCORING:\n"
            "As conversation unfolds, tally signals in real-time:\n"
            "• Each agreement = +2 points\n"
            "• Each objection = -1.5 points\n"
            "• High energy/deep breathing/warm tone = +1 each\n"
            "• Hesitation/cold tone/fast pace = -0.5 to -1 each\n"
            "• Sum the points. Divide by 2. You have close probability (0-10).\n\n"
            "USE THIS TO ADAPT:\n"
            "• 8+: Close now. Move to agreement.\n"
            "• 6-8: Keep engaging. Strengthen value.\n"
            "• 4-6: Clarify concerns. Build understanding.\n"
            "• 2-4: Listen more. Understand real barriers.\n"
            "• <2: Consider walking or pivoting."
        )
