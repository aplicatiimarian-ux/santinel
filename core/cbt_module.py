# -*- coding: utf-8 -*-
"""
CBT (Cognitive Behavioral Therapy) Module for SANTINEL
Identifies cognitive distortions, automatic thoughts, emotions, behaviors
Professional-grade emotional assessment framework

Bilingual (EN + RO): Romanian input is handled with a dedicated lexicon
(core/cbt_keywords_ro.py), diacritic folding, Snowball stemming, and
clause-scoped negation handling.
"""

import re
import unicodedata
from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.cbt_keywords_ro import RO_DISTORTION_KEYWORDS, RO_NEGATION_TOKENS
except ImportError:  # imported flat (core/ dir on path, e.g. backend/feedback_database.py)
    from cbt_keywords_ro import RO_DISTORTION_KEYWORDS, RO_NEGATION_TOKENS

try:  # optional dependency; matching degrades to exact-token if unavailable
    import snowballstemmer

    _EN_STEMMER = snowballstemmer.stemmer("english")
    _RO_STEMMER = snowballstemmer.stemmer("romanian")
except Exception:  # pragma: no cover
    _EN_STEMMER = None
    _RO_STEMMER = None

STEMMING_ENABLED = _RO_STEMMER is not None


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


# ---------------------------------------------------------------------------
# Text normalization helpers (module level, shared EN/RO)
# ---------------------------------------------------------------------------

_NT_CONTRACTION = re.compile(r"n['’`]t\b")
_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
# Clause boundaries for negation scoping. Apostrophes are intra-word (handled
# by tokenization / the n't rule), so they are deliberately not listed here.
_CLAUSE_RE = re.compile(r"[.,;:!?()\[\]{}\"\n–—…]+", re.UNICODE)

_EN_NEGATIONS = {
    "not", "no", "never", "none", "without", "hardly", "barely",
    "cannot", "nor", "neither",
}
_LOCAL_NEG_WINDOW = 3


def _strip_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _prep(text: str) -> str:
    """Lowercase, expand n't -> not, drop diacritics. Punctuation is kept."""
    text = (text or "").lower()
    text = _NT_CONTRACTION.sub(" not ", text)
    return _strip_diacritics(text)


def _tokens(text: str) -> List[str]:
    return _WORD_RE.findall(text)


def _split_clauses(prepped_text: str) -> List[str]:
    return [c for c in _CLAUSE_RE.split(prepped_text) if c and c.strip()]


def _seq_index(haystack: List[str], needle: List[str], fuzzy_last: bool = False) -> int:
    """Index of `needle` in `haystack` as a token subsequence.

    Tokens must match exactly, except that with `fuzzy_last` the final token
    may match by prefix in either direction when both sides are >= 4 chars.
    `fuzzy_last` is only used on the stemmed pass (both sides already reduced
    to roots), so a prefix relation there means a shared stem, e.g. text
    "dezastr" vs keyword "dezastru". It is never used on raw tokens, where a
    short word like "e" would spuriously prefix-match "everyone".
    """
    n, m = len(haystack), len(needle)
    if m == 0 or m > n:
        return -1
    last = m - 1
    for i in range(n - m + 1):
        for j in range(m):
            a, b = haystack[i + j], needle[j]
            if a == b:
                continue
            if (fuzzy_last and j == last
                    and min(len(a), len(b)) >= 4
                    and (a.startswith(b) or b.startswith(a))):
                continue
            break
        else:
            return i
    return -1


def _is_negated(clause_tokens: List[str], start: int, negations: set) -> bool:
    """Negation if a cue sits just before the match (local), or the clause
    opens with a cue that scopes the whole clause (e.g. "nu cred ca ...").
    A phrase that itself starts at the clause opening is treated as an idiom
    ("nu e corect", "it's not fair") and is not suppressed."""
    lo = max(0, start - _LOCAL_NEG_WINDOW)
    if any(tok in negations for tok in clause_tokens[lo:start]):
        return True
    if start > 0 and any(tok in negations for tok in clause_tokens[:2]):
        return True
    return False


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
        results: Dict[str, Dict] = {}
        for clause in _split_clauses(_prep(user_statement)):
            clause_tokens = _tokens(clause)
            if not clause_tokens:
                continue
            for match in self._scan(clause_tokens, self._en_keywords, _EN_STEMMER,
                                    _EN_NEGATIONS, "en"):
                results.setdefault(match["distortion"], match)
            for match in self._scan(clause_tokens, self._ro_keywords, _RO_STEMMER,
                                    RO_NEGATION_TOKENS, "ro"):
                results.setdefault(match["distortion"], match)
        return list(results.values())

    def _scan(self, tokens, keyword_map, stemmer, negations, lang) -> List[Dict]:
        stems = [stemmer.stemWord(t) for t in tokens] if stemmer else None
        found = []
        for key, phrases in keyword_map.items():
            for phrase in phrases:
                phrase_tokens = _tokens(_prep(phrase))
                if not phrase_tokens:
                    continue
                idx = _seq_index(tokens, phrase_tokens)
                matched_by = "exact"
                if idx == -1 and stems is not None:
                    idx = _seq_index(stems, [stemmer.stemWord(t) for t in phrase_tokens],
                                     fuzzy_last=True)
                    matched_by = "stem"
                if idx == -1:
                    continue
                if _is_negated(tokens, idx, negations):
                    continue
                found.append({
                    "distortion": key,
                    "keyword": phrase,
                    "language": lang,
                    "confidence": 0.8,
                    "matched_by": matched_by,
                    "description": self._describe(key),
                })
                break
        return found

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
