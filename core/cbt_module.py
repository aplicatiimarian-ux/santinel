# -*- coding: utf-8 -*-
"""
CBT (Cognitive Behavioral Therapy) Module for SANTINEL
Identifies cognitive distortions, automatic thoughts, emotions, behaviors
Professional-grade emotional assessment framework

Bilingual (EN + RO): Romanian input is handled with a dedicated lexicon
(core/cbt_keywords_ro.py). Diacritic folding, Snowball stemming and
clause-scoped negation are shared with the other frameworks via
core/text_norm.py.
"""

from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.text_norm import find_all, merge_by_category, EN_NEGATIONS, STEMMING_ENABLED
    from core.cbt_keywords_ro import RO_DISTORTION_KEYWORDS, RO_NEGATION_TOKENS
except ImportError:  # imported flat (core/ dir on path, e.g. backend/feedback_database.py)
    from text_norm import find_all, merge_by_category, EN_NEGATIONS, STEMMING_ENABLED
    from cbt_keywords_ro import RO_DISTORTION_KEYWORDS, RO_NEGATION_TOKENS

__all__ = ["CognitivDistortion", "CBTAssessment", "STEMMING_ENABLED"]


class CognitivDistortion(Enum):
    """Common cognitive distortions identified in negotiations"""

    CATASTROPHIZING = "catastrophizing"          # Expecting worst outcome
    BLACK_AND_WHITE = "black_and_white"           # All or nothing thinking
    OVERGENERALIZATION = "overgeneralization"     # One bad event = always happens
    MIND_READING = "mind_reading"                 # Assuming you know what other thinks
    FORTUNE_TELLING = "fortune_telling"           # Predicting negative future
    PERSONALIZATION = "personalization"           # Taking others' reactions personally
    FILTERING = "filtering"                       # Focusing only on negatives
    EMOTIONAL_REASONING = "emotional_reasoning"   # Feelings = facts
    SHOULD_STATEMENTS = "should_statements"       # Rigid rules
    LABELING = "labeling"                         # Negative self-labels
    DISQUALIFYING_POSITIVE = "disqualifying_positive"          # Positives "don't count"
    MAGNIFICATION_MINIMIZATION = "magnification_minimization"  # Blow up bad / shrink good
    BLAMING = "blaming"                           # Others fully responsible
    CONTROL_FALLACY = "control_fallacy"           # Helpless / hyper-responsible
    FAIRNESS_FALLACY = "fairness_fallacy"         # Everything judged by "fair"
    ALWAYS_BEING_RIGHT = "always_being_right"     # Being wrong is intolerable


class CBTAssessment:
    """
    CBT Assessment Engine
    Maps: Situation → Automatic Thoughts → Emotions → Behaviors → Consequences
    """

    def __init__(self):
        self.distortion_keywords = {
            CognitivDistortion.CATASTROPHIZING: [
                "worst", "disaster", "never", "always fail", "ruined", "impossible"
            ],
            CognitivDistortion.BLACK_AND_WHITE: [
                "either/or", "all or nothing", "perfect", "completely", "total failure"
            ],
            CognitivDistortion.OVERGENERALIZATION: [
                "always", "never", "every time", "everyone", "nobody"
            ],
            CognitivDistortion.MIND_READING: [
                "they think", "they want", "they don't like", "i know they believe"
            ],
            CognitivDistortion.FORTUNE_TELLING: [
                "will fail", "going to lose", "definitely won't", "won't succeed"
            ],
            CognitivDistortion.PERSONALIZATION: [
                "it's my fault", "because of me", "i caused", "my problem"
            ],
            CognitivDistortion.FILTERING: [
                "only bad", "nothing good", "worst part", "ignore the positive"
            ],
            CognitivDistortion.EMOTIONAL_REASONING: [
                "i feel like", "feeling means", "i feel therefore"
            ],
            CognitivDistortion.SHOULD_STATEMENTS: [
                "should", "must", "ought to", "have to", "supposed to"
            ],
            CognitivDistortion.LABELING: [
                "i'm a failure", "i'm stupid", "i'm incompetent", "i'm weak"
            ],
            CognitivDistortion.DISQUALIFYING_POSITIVE: [
                "doesn't count", "just luck", "anyone could have",
                "that doesn't mean anything", "it was a fluke", "only because"
            ],
            CognitivDistortion.MAGNIFICATION_MINIMIZATION: [
                "blowing it out of proportion", "making a big deal", "it's nothing",
                "not a big deal", "huge catastrophe", "exaggerating"
            ],
            CognitivDistortion.BLAMING: [
                "it's all their fault", "they're to blame", "because of them",
                "they ruined", "he made me", "she made me"
            ],
            CognitivDistortion.CONTROL_FALLACY: [
                "nothing i can do", "out of my hands", "powerless", "no control",
                "can't change anything", "it's all up to them"
            ],
            CognitivDistortion.FAIRNESS_FALLACY: [
                "it's not fair", "so unfair", "should be fair", "i deserve better",
                "that's unjust"
            ],
            CognitivDistortion.ALWAYS_BEING_RIGHT: [
                "i'm right", "you're wrong", "i can't be wrong", "i know better",
                "prove me wrong"
            ],
        }

        # value-keyed views used by the matcher
        self._en_keywords = {d.value: kws for d, kws in self.distortion_keywords.items()}
        self._ro_keywords = RO_DISTORTION_KEYWORDS

    # -- detection ---------------------------------------------------------

    def identify_distortions(self, user_statement: str) -> List[Dict]:
        """
        Identify cognitive distortions in user's statement (English + Romanian).
        Returns one entry per distortion, each with keyword, language,
        confidence and description. Negated mentions are skipped.
        """
        en = find_all(user_statement, self._en_keywords, lang="en",
                      negations=EN_NEGATIONS)
        ro = find_all(user_statement, self._ro_keywords, lang="ro",
                      negations=RO_NEGATION_TOKENS)
        out = []
        for hit in merge_by_category(en, ro):
            out.append({
                "distortion": hit["category"],
                "keyword": hit["keyword"],
                "language": hit["language"],
                "confidence": 0.8,
                "matched_by": hit["matched_by"],
                "description": self._describe(hit["category"]),
            })
        return out

    def _describe(self, key: str) -> str:
        for distortion in CognitivDistortion:
            if distortion.value == key:
                return self._get_distortion_description(distortion)
        return "Cognitive distortion detected"

    def _get_distortion_description(self, distortion: CognitivDistortion) -> str:
        """Get therapeutic description of distortion"""
        descriptions = {
            CognitivDistortion.CATASTROPHIZING: "Expecting worst-case scenario without evidence",
            CognitivDistortion.BLACK_AND_WHITE: "Seeing situations as entirely good or bad",
            CognitivDistortion.OVERGENERALIZATION: "Making broad conclusions from single events",
            CognitivDistortion.MIND_READING: "Assuming you know what others are thinking",
            CognitivDistortion.FORTUNE_TELLING: "Predicting negative outcomes with certainty",
            CognitivDistortion.PERSONALIZATION: "Blaming yourself for external events",
            CognitivDistortion.FILTERING: "Focusing only on negative details",
            CognitivDistortion.EMOTIONAL_REASONING: "Treating emotions as facts",
            CognitivDistortion.SHOULD_STATEMENTS: "Using rigid rules instead of flexibility",
            CognitivDistortion.LABELING: "Using negative global labels about yourself",
            CognitivDistortion.DISQUALIFYING_POSITIVE: "Rejecting positive experiences as if they don't count",
            CognitivDistortion.MAGNIFICATION_MINIMIZATION: "Blowing negatives out of proportion or shrinking positives",
            CognitivDistortion.BLAMING: "Holding others entirely responsible for your feelings or outcomes",
            CognitivDistortion.CONTROL_FALLACY: "Seeing yourself as helpless or as totally responsible for everything",
            CognitivDistortion.FAIRNESS_FALLACY: "Judging every outcome against a fixed standard of fairness",
            CognitivDistortion.ALWAYS_BEING_RIGHT: "Treating being wrong as unacceptable and defending your view at all costs",
        }
        return descriptions.get(distortion, "Cognitive distortion detected")

    # -- intervention / assessment (unchanged behavior) -------------------

    def generate_cbt_intervention(self, distortions: List[Dict], situation: str) -> str:
        """
        Generate CBT-based coaching intervention
        Follows: Identify → Challenge → Reframe → Action
        """
        if not distortions:
            return "No significant cognitive distortions detected. Focus on evidence-based strategy."

        primary_distortion = distortions[0]
        intervention = f"""
CBT COACHING INTERVENTION:

🔍 IDENTIFIED PATTERN: {primary_distortion['distortion'].replace('_', ' ').title()}
   Description: {primary_distortion['description']}

❓ CHALLENGE THE THOUGHT:
   • What evidence supports this thought? What contradicts it?
   • Are you treating a feeling as a fact?
   • What would you tell a friend in this situation?

🔄 REFRAME THE SITUATION:
   • What's a more balanced perspective?
   • What are you overlooking?
   • What's within your control?

✅ ACTION STEP:
   • Focus on facts, not predictions
   • Use "I might..." instead of "I will..."
   • Prepare for multiple outcomes, not just worst-case
"""
        return intervention

    def assess_emotional_state(self,
                               situation: str,
                               emotions: Dict[str, float]) -> Dict:
        """
        Comprehensive emotional assessment using CBT framework
        Returns: Situation Analysis → Thoughts → Emotions → Behaviors → Consequences
        """
        distortions = self.identify_distortions(situation)

        return {
            "situation": situation,
            "cognitive_distortions": distortions,
            "emotion_intensity": max(emotions.values()) if emotions else 0,
            "dominant_emotion": max(emotions, key=emotions.get) if emotions else "neutral",
            "cbt_intervention": self.generate_cbt_intervention(distortions, situation),
            "therapeutic_insight": self._generate_insight(distortions, emotions),
        }

    def _generate_insight(self, distortions: List[Dict], emotions: Dict) -> str:
        """Generate therapeutic insight from assessment"""
        if not distortions:
            return "You're thinking clearly. Channel this clarity into strategic action."

        distortion_count = len(set(d['distortion'] for d in distortions))

        if distortion_count >= 3:
            return "Multiple thinking patterns are active. Slow down. Focus on one fact at a time."
        elif distortion_count == 2:
            return "You're experiencing some cognitive distortions. Ground yourself in observable facts."
        else:
            return "One primary thinking pattern detected. Challenge it with evidence."
