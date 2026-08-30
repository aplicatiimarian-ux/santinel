# -*- coding: utf-8 -*-
"""
Neuroscience Module for SANTINEL
Detects neurobiological patterns and nervous system states in negotiations.

Bilingual (EN + RO):
  - 5 neurobiological patterns:
    * Amygdala activation: threat response, fear, defensiveness
    * Reward system activation: pleasure, motivation, engagement
    * Mirror neuron engagement: empathy, attunement, mimicry
    * Default mode network engagement: self-referential thinking, rumination
    * Vagal tone indicators: social engagement, calm, parasympathetic activation
  - Nervous system state: sympathetic (stress), parasympathetic (calm), balanced
  - Threat/Safety/Reward scoring (0.0-1.0 on each axis)
  - De-escalation + engagement coaching

Neuroscience (Porges, Siegel, Damasio): the nervous system drives negotiation behavior.
When threatened (amygdala), we fight/flee. When safe (vagus), we engage. When rewarded,
we cooperate. Understanding the neurobiology lets you shift the nervous system toward
engagement and away from threat.

Romanian triggers live in core/neuroscience_keywords_ro.py; the English set is `EN`
below. Tokenization, diacritic folding and Snowball stemming are shared with other
frameworks via core/text_norm.py.
"""

from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.text_norm import find_all
    from core.neuroscience_keywords_ro import RO
except ImportError:  # imported flat (core/ dir on path)
    from text_norm import find_all
    from neuroscience_keywords_ro import RO

__all__ = ["NervousSystemState", "NeurobiologicalPattern", "NeuroscienceModule"]


class NervousSystemState(Enum):
    """The 3 primary nervous system states."""
    SYMPATHETIC = "sympathetic"  # stress, arousal, threat response
    PARASYMPATHETIC = "parasympathetic"  # calm, rest, safety
    BALANCED = "balanced"  # optimal for negotiation


class NeurobiologicalPattern(Enum):
    """The 5 key neurobiological patterns in negotiation."""
    AMYGDALA_ACTIVATION = "amygdala_activation"
    REWARD_SYSTEM = "reward_system"
    MIRROR_NEURONS = "mirror_neurons"
    DEFAULT_MODE_NETWORK = "default_mode_network"
    VAGAL_TONE = "vagal_tone"


# English lexicon — same shape as core/neuroscience_keywords_ro.RO
EN = {
    "patterns": {
        "amygdala_activation": [
            "i'm anxious", "i feel threatened", "i'm defensive", "i'm afraid",
            "this makes me nervous", "i'm on edge", "i can feel my heart racing",
            "fight or flight", "i'm activated", "danger", "this triggers me",
            "i feel unsafe", "alarm", "threat",
        ],
        "reward_system": [
            "this excites me", "i'm motivated", "i'm interested", "this appeals to me",
            "i'm drawn to", "this is rewarding", "i enjoy", "this motivates me",
            "i'm engaged", "this lights me up", "i'm enthusiastic", "pleasure",
            "i want this", "compelling",
        ],
        "mirror_neurons": [
            "i resonate with you", "i feel what you feel", "i see myself in you",
            "i'm attuned to you", "we're on the same wavelength", "i mirror you",
            "i feel your concern", "we're aligned", "i get it", "i understand",
            "i'm tracking with you", "we're in sync", "empathy",
        ],
        "default_mode_network": [
            "i'm ruminating", "i'm stuck in my head", "i'm overthinking",
            "i can't stop thinking about", "what if", "this reminds me of",
            "i'm worried about the future", "i keep replaying", "self-doubt",
            "narrative", "story", "this means", "i'm in my own world",
        ],
        "vagal_tone": [
            "i feel calm", "i'm relaxed", "i can breathe easy", "i'm settled",
            "i'm grounded", "i feel at peace", "my nervous system is settled",
            "i'm present", "i'm centered", "social", "connected", "safe",
            "i can slow down", "clarity",
        ],
    },
    "nervous_system": {
        "sympathetic": [
            "stress response", "fight or flight", "activated", "adrenaline",
            "high alert", "defensive", "reactive", "urgent", "emergency mode",
            "pressure", "tense", "on guard", "vigilant", "racing heart",
        ],
        "parasympathetic": [
            "rest and digest", "calm response", "relaxed", "at ease", "settled",
            "grounded", "present", "openness", "connection", "social engagement",
            "vagal tone", "de-escalation", "peaceful", "trusting", "safe",
        ],
        "balanced": [
            "optimal state", "clear thinking", "flexible", "responsive",
            "engaged but calm", "alert but relaxed", "awareness", "presence",
            "integration", "window of tolerance", "resilient", "adaptable",
        ],
    },
}

_PATTERN_INSIGHT = {
    "amygdala_activation": (
        "Amygdala Activation: threat detection circuit. Hijacks rational brain.",
        "Signals: fear, defensiveness, fight/flight language, rapid speech.",
        "Impact: rigid thinking, poor listening, reactivity, escalation.",
    ),
    "reward_system": (
        "Reward System Activation: motivation, pleasure, anticipation.",
        "Signals: excitement, engagement, motivation, interest, wanting.",
        "Impact: creativity, collaboration, risk-taking, cooperation.",
    ),
    "mirror_neurons": (
        "Mirror Neuron Engagement: empathy, attunement, mimicry.",
        "Signals: resonance, understanding, 'we're on the same page', alignment.",
        "Impact: trust, rapport, mutual understanding, creativity.",
    ),
    "default_mode_network": (
        "Default Mode Network: self-referential thinking, narrative, rumination.",
        "Signals: 'what if', 'this reminds me', overthinking, rumination.",
        "Impact: distraction, fear-based thinking, stuck narrative, low presence.",
    ),
    "vagal_tone": (
        "Vagal Tone: parasympathetic activation, social engagement system.",
        "Signals: calm, presence, grounded, connected, social engagement.",
        "Impact: clear thinking, listening, empathy, creative problem-solving.",
    ),
}

_NERVOUS_SYSTEM_GUIDANCE = {
    "sympathetic": (
        "Sympathetic Activation: stress response is on. Threat > trust.",
        "Signs: defensive language, rapid speech, pressure, urgency.",
        "Strategy: First de-escalate (signal safety). Slow pace. Acknowledge concern. Build psychological safety.",
    ),
    "parasympathetic": (
        "Parasympathetic Activation: rest-and-digest. Safe > threat.",
        "Signs: calm language, openness, curiosity, grounded presence.",
        "Strategy: Capitalize on safety. Explore options. Deepen engagement. Build on rapport.",
    ),
    "balanced": (
        "Balanced State: optimal for negotiation. Alert + calm.",
        "Signs: clear thinking, flexibility, responsiveness, integration.",
        "Strategy: Maintain this state. Protect from triggers. Keep both at peace + alert.",
    ),
}

_THREAT_SAFETY_REWARD = {
    "threat_escalation": "Amygdala dominates. Trust collapses. Cooperation dies. De-escalate first.",
    "threat_safety_balance": "Amygdala quieted. Prefrontal cortex online. Rational negotiation possible.",
    "safety_reward_engagement": "Prefrontal cortex + reward system online. Creativity, cooperation, insight flow.",
}


class NeuroscienceModule:
    """
    Neurobiological analysis of negotiation dynamics.
    Detects amygdala activation, reward engagement, mirror neuron synchrony,
    default mode rumination, and vagal tone. Assesses nervous system state
    (sympathetic/parasympathetic) and provides de-escalation and engagement coaching.
    Call analyze() for the full pass, or individual methods for one domain.
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

    # -- Neurobiological patterns -----------------------------------

    _PATTERN_KEYS = (
        "amygdala_activation", "reward_system", "mirror_neurons",
        "default_mode_network", "vagal_tone"
    )

    def detect_patterns(self, text: str) -> Dict:
        """Detect neurobiological patterns in the text."""
        hits = self._scan(text, "patterns")
        counts = {k: 0 for k in self._PATTERN_KEYS}
        raw_matches = {k: [] for k in self._PATTERN_KEYS}

        for h in hits:
            counts[h["category"]] += 1
            raw_matches[h["category"]].append(h["keyword"])

        total = sum(counts.values())
        if total == 0:
            scores = {k: 0.0 for k in self._PATTERN_KEYS}
            primary_finding = None
        else:
            primary_finding = max(counts, key=counts.get)
            scores = {k: round(v / total, 3) for k, v in counts.items()}

        return {
            "patterns": scores,
            "primary_finding": primary_finding,
            "raw_matches": raw_matches,
            "analysis_text": self._pattern_analysis(primary_finding) if primary_finding else None,
        }

    @staticmethod
    def _pattern_analysis(pattern: str) -> tuple:
        return _PATTERN_INSIGHT.get(pattern, ("No pattern identified.", "", ""))

    # -- Nervous system state ---------------------------------------

    def assess_nervous_system_state(self, text: str) -> Dict:
        """Assess sympathetic vs. parasympathetic activation."""
        sympathetic_hits = find_all(text, {"sympathetic": EN["nervous_system"]["sympathetic"]}, lang="en", first_phrase_only=False)
        parasympathetic_hits = find_all(text, {"parasympathetic": EN["nervous_system"]["parasympathetic"]}, lang="en", first_phrase_only=False)
        balanced_hits = find_all(text, {"balanced": EN["nervous_system"]["balanced"]}, lang="en", first_phrase_only=False)

        ro_sympathetic = find_all(text, {"sympathetic": RO["nervous_system"]["sympathetic"]}, lang="ro", first_phrase_only=False)
        ro_parasympathetic = find_all(text, {"parasympathetic": RO["nervous_system"]["parasympathetic"]}, lang="ro", first_phrase_only=False)
        ro_balanced = find_all(text, {"balanced": RO["nervous_system"]["balanced"]}, lang="ro", first_phrase_only=False)

        symp_count = len(set((h["keyword"] for h in sympathetic_hits + ro_sympathetic)))
        para_count = len(set((h["keyword"] for h in parasympathetic_hits + ro_parasympathetic)))
        bal_count = len(set((h["keyword"] for h in balanced_hits + ro_balanced)))

        # Classify state
        if symp_count > max(para_count, bal_count):
            state = "sympathetic"
        elif para_count > max(symp_count, bal_count):
            state = "parasympathetic"
        else:
            state = "balanced"

        return {
            "emotional_state": state,
            "sympathetic_indicators": symp_count,
            "parasympathetic_indicators": para_count,
            "balanced_indicators": bal_count,
            "analysis_text": _NERVOUS_SYSTEM_GUIDANCE[state][0],
            "coaching_guidance": _NERVOUS_SYSTEM_GUIDANCE[state][2],
        }

    # -- Threat/Safety/Reward scoring --------------------------------

    def score_threat_safety_reward(self, text: str) -> Dict:
        """Score the text on 3D axes: threat (amygdala), safety (vagal), reward."""
        patterns = self.detect_patterns(text)
        scores = patterns["patterns"]

        # Threat = amygdala + default mode network (rumination amplifies threat)
        threat_score = round((scores["amygdala_activation"] + scores["default_mode_network"]) / 2, 3)

        # Safety = vagal tone + mirror neurons (empathy signals safety)
        safety_score = round((scores["vagal_tone"] + scores["mirror_neurons"]) / 2, 3)

        # Reward = reward system activation
        reward_score = scores["reward_system"]

        # Determine overall state
        if threat_score > safety_score and threat_score > reward_score:
            state = "threat_escalation"
        elif safety_score > threat_score and reward_score > threat_score:
            state = "safety_reward_engagement"
        else:
            state = "threat_safety_balance"

        return {
            "threat": threat_score,
            "safety": safety_score,
            "reward": reward_score,
            "primary_finding": state,
            "coaching_guidance": _THREAT_SAFETY_REWARD[state],
        }

    # -- Full analysis -----------------------------------------------

    def analyze(self, text: str) -> Dict:
        """Full neuroscience analysis: patterns, nervous system state, threat/safety/reward."""
        return {
            "neurobiological_patterns": self.detect_patterns(text),
            "nervous_system_state": self.assess_nervous_system_state(text),
            "threat_safety_reward": self.score_threat_safety_reward(text),
        }

    def dual_speaker_neuroscience(self, your_text: str, their_text: str) -> Dict:
        """Analyze neurobiology in both you and the counterparty."""
        return {
            "your_neurobiology": self.analyze(your_text),
            "their_neurobiology": self.analyze(their_text),
            "coaching": self._dual_neuroscience_coaching(your_text, their_text),
        }

    @staticmethod
    def _dual_neuroscience_coaching(your_text: str, their_text: str) -> str:
        module = NeuroscienceModule()
        your_state = module.assess_nervous_system_state(your_text)["state"]
        their_state = module.assess_nervous_system_state(their_text)["state"]

        coaching = "DUAL-SPEAKER NEUROSCIENCE COACHING\n\n"
        coaching += f"YOU: {your_state.upper()} nervous system activation\n"
        coaching += f"THEM: {their_state.upper()} nervous system activation\n\n"

        coaching += "NEUROBIOLOGICAL REALITY:\n"
        if your_state == "sympathetic" or their_state == "sympathetic":
            coaching += "• Someone's amygdala is active. Threat > trust.\n"
            coaching += "• Strategy: De-escalate FIRST before negotiating.\n\n"
        if your_state == "parasympathetic" and their_state == "parasympathetic":
            coaching += "• Both nervous systems are calm. Optimal for negotiation.\n"
            coaching += "• Strategy: Maintain safety. Deepen engagement.\n\n"

        coaching += (
            "KEY MOVES FOR DE-ESCALATION:\n"
            "1. Slow your own nervous system: deep breath, grounded posture.\n"
            "2. Signal safety: calm tone, open body, reduced urgency.\n"
            "3. Acknowledge their concern: 'I hear you're worried about...'\n"
            "4. Offer predictability: 'Here's what happens next...'\n"
            "5. Build psychological safety: consistency, honesty, follow-through.\n\n"
            "KEY MOVES FOR ENGAGEMENT:\n"
            "1. Activate reward system: 'Here's what we both gain...'\n"
            "2. Mirror neurons: match their energy, pace, tone.\n"
            "3. Shared humanity: 'We both want...' 'We're both concerned about...'\n"
            "4. Autonomy: 'You're in control of...' 'Your choice is...'\n"
            "5. Purpose: connect to deeper 'why' for both."
        )
        return coaching

    def prescribe_nervous_system_optimization(self) -> str:
        """Coaching for managing nervous system state during negotiation."""
        return (
            "NERVOUS SYSTEM OPTIMIZATION FOR NEGOTIATION\n\n"
            "BEFORE THE CONVERSATION:\n"
            "1. Self-regulate: breathwork, movement, grounding to activate parasympathetic.\n"
            "2. Set intention: 'I'm safe. They're not a threat. We're collaborating.'\n"
            "3. Arrive regulated: amygdala quiet, prefrontal cortex online.\n\n"
            "DURING THE CONVERSATION:\n"
            "1. MONITOR YOUR OWN STATE: Am I calm? Alert? Or activated?\n"
            "   If activated: pause, breathe, ground. Don't negotiate from amygdala.\n\n"
            "2. DETECT THEIR STATE: Are they calm? Defensive? Excited? Ruminating?\n"
            "   Match their pace. Reassure if threatened. Excite if disengaged.\n\n"
            "3. SIGNAL SAFETY: Calm voice, open body, predictability, honesty.\n"
            "   When they feel safe, their amygdala quiets and cortex online.\n\n"
            "4. BUILD RAPPORT: Mirror their tone/energy. Share concern.\n"
            "   Mirror neurons + shared humanity = trust + creativity.\n\n"
            "5. ACTIVATE REWARD: 'Here's what we gain together...'\n"
            "   Dopamine engagement overcomes amygdala threat.\n\n"
            "6. MAINTAIN PRESENCE: Slow down. Listen. Don't ruminate (default mode off).\n"
            "   Presence = prefrontal cortex + social engagement.\n\n"
            "RESULT: Both nervous systems regulated. Negotiation from intelligence, not fear."
        )
