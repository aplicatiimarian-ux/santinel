# -*- coding: utf-8 -*-
"""
EI (Emotional Intelligence) Module for SANTINEL
Analyzes emotional states and Goleman competencies in negotiations.

Bilingual (EN + RO):
  - 5 Goleman competencies: self-awareness, self-regulation, motivation, empathy, social skills
  - 6 emotional states: openness, skepticism, frustration, curiosity, fear, acceptance
  - Dual-speaker mode: assess both you and counterparty

Romanian triggers live in core/ei_keywords_ro.py; the English set is `EN` below.
Tokenization, diacritic folding and Snowball stemming are shared with other
frameworks via core/text_norm.py.
"""

from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.text_norm import find_all
    from core.ei_keywords_ro import RO
except ImportError:  # imported flat (core/ dir on path)
    from text_norm import find_all
    from ei_keywords_ro import RO

__all__ = ["Competency", "EmotionalState", "EIModule"]


class Competency(Enum):
    """Goleman's 5 emotional intelligence competencies."""
    SELF_AWARENESS = "self_awareness"
    SELF_REGULATION = "self_regulation"
    MOTIVATION = "motivation"
    EMPATHY = "empathy"
    SOCIAL_SKILLS = "social_skills"


class EmotionalState(Enum):
    """6 core emotional states detected in negotiation discourse."""
    OPENNESS = "openness"
    SKEPTICISM = "skepticism"
    FRUSTRATION = "frustration"
    CURIOSITY = "curiosity"
    FEAR = "fear"
    ACCEPTANCE = "acceptance"


# English lexicon — same shape as core/ei_keywords_ro.RO
EN = {
    "competencies": {
        "self_awareness": [
            "i feel", "i'm anxious", "i realize", "i notice", "i can see how",
            "i might be", "my concern is", "i'm aware that", "i sense",
            "what i'm experiencing",
        ],
        "self_regulation": [
            "let me take a step back", "i can manage this", "let's stay calm",
            "i'll pause and think", "i won't react", "deep breath", "let me reconsider",
            "i'm in control", "despite my feelings", "i can handle this",
        ],
        "motivation": [
            "i'm committed to", "i'm determined", "we can find a way", "i believe in",
            "this matters to me", "i'm focused on", "let's keep going", "i won't give up",
            "the goal is", "we'll figure it out",
        ],
        "empathy": [
            "i understand how you feel", "that must be", "from your perspective",
            "i can see why", "you're concerned about", "your needs are", "i hear you",
            "that's important to you", "you want", "i get it",
        ],
        "social_skills": [
            "let's work together", "what do you think", "how can we", "let's find a solution",
            "i value your input", "we can collaborate", "let me listen", "what works for you",
            "let's agree on", "can we find common ground",
        ],
    },
    "emotional_states": {
        "openness": [
            "i'm interested in", "tell me more", "that's interesting", "let's explore",
            "i'm open to", "i'd like to understand", "what else", "i hadn't thought of that",
            "fascinating", "help me understand",
        ],
        "skepticism": [
            "i'm not sure", "that doesn't make sense", "i have doubts", "really?",
            "how can you be certain", "i don't believe", "that's questionable",
            "show me the proof", "i'm not convinced", "that seems unlikely",
        ],
        "frustration": [
            "this is getting nowhere", "we're going in circles", "that's not working",
            "i'm tired of", "enough", "this is pointless", "come on", "seriously?",
            "this is ridiculous", "i'm done with",
        ],
        "curiosity": [
            "why is that", "how does that work", "what if", "could we try",
            "i wonder", "let's test", "what would happen if", "have you considered",
            "interesting angle", "i'd like to explore",
        ],
        "fear": [
            "i'm worried about", "what if it fails", "i'm afraid", "this could be risky",
            "i don't feel safe", "that's dangerous", "i'm concerned about",
            "what's the worst that could happen", "i'm nervous", "this scares me",
        ],
        "acceptance": [
            "i can live with that", "that works for me", "i agree", "sounds good",
            "i'm comfortable with", "that's acceptable", "let's move forward",
            "we have a deal", "i'm satisfied with", "that's fair",
        ],
    },
}

_COMPETENCY_ANALYSIS = {
    "self_awareness": (
        "Self-Awareness: recognizes and names own emotions. Foundation for all other skills.",
        "Strengthen by: naming feelings before reacting; asking 'why am I feeling this?'",
    ),
    "self_regulation": (
        "Self-Regulation: manages emotional impulses; stays composed under pressure.",
        "Strengthen by: pause before responding; use physical cues (breath, posture); reframe.",
    ),
    "motivation": (
        "Motivation: driven by purpose, not just outcome. Resilient in setbacks.",
        "Strengthen by: connect to the deeper 'why'; break goals into steps; celebrate small wins.",
    ),
    "empathy": (
        "Empathy: understands and feels what the other side needs. Builds trust.",
        "Strengthen by: ask open questions; listen to understand, not to reply; name their concerns.",
    ),
    "social_skills": (
        "Social Skills: manages relationships, influences, collaborates.",
        "Strengthen by: reflect back what you hear; find shared interests; propose win-win solutions.",
    ),
}

_EMOTIONAL_STATE_GUIDANCE = {
    "openness": (
        "Openness: receptive, curious, ready to learn.",
        "Leverage: ask for their ideas; explore options together.",
    ),
    "skepticism": (
        "Skepticism: doubtful, questioning, wants evidence.",
        "Leverage: provide data; address concerns directly; acknowledge the risk.",
    ),
    "frustration": (
        "Frustration: impatient, irritable, wants progress.",
        "Leverage: break impasse with a concrete proposal; acknowledge the slow pace; move forward.",
    ),
    "curiosity": (
        "Curiosity: inquisitive, engaged, exploring possibilities.",
        "Leverage: ask 'what if' questions; share ideas; experiment together.",
    ),
    "fear": (
        "Fear: anxious, protective, risk-averse.",
        "Leverage: address the specific fear; offer reassurance; propose safeguards; go slow.",
    ),
    "acceptance": (
        "Acceptance: satisfied, ready to agree, wants closure.",
        "Leverage: confirm next steps; formalize the agreement; celebrate progress.",
    ),
}


class EIModule:
    """
    Emotional Intelligence coaching engine.
    Detects Goleman competencies in your own language and emotional state
    (yours and/or the other party's). Call analyze() for the full pass, or
    an individual method for one domain.
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

    # -- Competencies -----------------------------------------------

    _COMPETENCY_KEYS = ("self_awareness", "self_regulation", "motivation",
                        "empathy", "social_skills")

    def detect_competencies(self, text: str) -> Dict:
        """Assess emotional intelligence competencies demonstrated in the text."""
        hits = self._scan(text, "competencies")
        counts = {k: 0 for k in self._COMPETENCY_KEYS}
        matched = {k: [] for k in self._COMPETENCY_KEYS}
        for h in hits:
            counts[h["category"]] += 1
            matched[h["category"]].append(h["keyword"])

        total = sum(counts.values())
        if total == 0:
            scores = {k: 0.0 for k in self._COMPETENCY_KEYS}
            primary = None
        else:
            primary = max(counts, key=counts.get)
            scores = {k: round(v / total, 3) for k, v in counts.items()}

        analysis = self._competency_analysis(primary) if primary else \
                   ("No competencies detected.", "Practice naming emotions and managing reactions.")

        return {
            "primary_finding": primary,
            "scores": scores,
            "detected_patterns": [k for k in self._COMPETENCY_KEYS if counts[k] > 0],
            "raw_matches": matched,
            "analysis_text": analysis[0],
            "coaching_guidance": analysis[1],
        }

    @staticmethod
    def _competency_analysis(comp: str) -> tuple:
        return _COMPETENCY_ANALYSIS.get(comp, ("Mixed competencies.", ""))

    # -- Emotional states -------------------------------------------

    _STATE_PRIORITY = ("fear", "frustration", "skepticism", "curiosity",
                       "openness", "acceptance")

    def detect_emotional_state(self, text: str) -> Dict:
        """Detect the primary emotional state and all present states."""
        hits = self._scan(text, "emotional_states")
        present = {h["category"]: h for h in hits}

        for state in self._STATE_PRIORITY:
            if state in present:
                primary = state
                break
        else:
            primary = "openness"  # neutral default

        guidance = _EMOTIONAL_STATE_GUIDANCE.get(primary, ("Unknown state", ""))

        return {
            "primary_finding": primary,
            "detected_patterns": list(present.keys()),
            "raw_matches": [present[s]["keyword"] for s in present] if present else [],
            "assumed_default": not present,
            "analysis_text": guidance[0],
            "coaching_guidance": guidance[1],
        }

    # -- Umbrella + coaching ----------------------------------------

    def analyze(self, text: str) -> Dict:
        """Full EI analysis: competencies + emotional state."""
        comp = self.detect_competencies(text)
        state = self.detect_emotional_state(text)

        confidence = 0.6
        if comp["detected_patterns"]:
            confidence += 0.2
        if state["detected_patterns"]:
            confidence += 0.2

        return {
            "competencies": comp,
            "emotional_state": state,
            "confidence_score": min(float(confidence), 1.0),
        }

    def dual_speaker_assessment(self, your_text: str, their_text: str) -> Dict:
        """Assess EI in both you and the counterparty."""
        return {
            "your_ei": self.analyze(your_text),
            "their_ei": self.analyze(their_text),
            "coaching": self._dual_coaching(your_text, their_text),
        }

    @staticmethod
    def _dual_coaching(your_text: str, their_text: str) -> str:
        your_ei = EIModule().analyze(your_text)
        their_ei = EIModule().analyze(their_text)

        your_state = your_ei["emotional_state"]["primary_emotional_state"]
        their_state = their_ei["emotional_state"]["primary_emotional_state"]
        your_comp = your_ei["competencies"]["primary_competency"]

        return (
            f"DUAL-SPEAKER COACHING\n\n"
            f"YOU: in {your_state} state"
            f"{f', demonstrating {your_comp}' if your_comp else ''}.\n"
            f"THEM: in {their_state} state.\n\n"
            f"MOVE: acknowledge their {their_state} ('I sense you're concerned').\n"
            f"Then ground yourself in {your_comp or 'Adult state'}.\n"
            f"Propose one concrete step forward."
        )

    def prescribe_ei_conversation(self) -> str:
        """Guidance for an emotionally intelligent negotiation."""
        return (
            "EMOTIONALLY INTELLIGENT CONVERSATION\n\n"
            "1. SELF-AWARENESS: Notice what you feel (anxiety, enthusiasm, frustration).\n"
            "   Name it to yourself first.\n\n"
            "2. SELF-REGULATION: Pause. Do not react from emotion.\n"
            "   Take a breath. Ask yourself: 'What's the smart move here?'\n\n"
            "3. MOTIVATION: Connect to your deeper 'why' — not just winning,\n"
            "   but building a sustainable relationship.\n\n"
            "4. EMPATHY: Listen to understand their needs, fears, and constraints.\n"
            "   Ask: 'What's most important to you in this deal?'\n\n"
            "5. SOCIAL SKILLS: Propose solutions that honor both parties.\n"
            "   Use collaborative language: 'we', 'let's', 'together'.\n\n"
            "RESULT: Higher trust, better agreements, less conflict."
        )
