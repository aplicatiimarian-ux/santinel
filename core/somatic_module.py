# -*- coding: utf-8 -*-
"""
Somatic Module for SANTINEL
Detects and coaches body-based signals in negotiations.

Bilingual (EN + RO):
  - 5 somatic patterns:
    * Breathing rhythm indicators: fast/shallow (threat) vs. slow/deep (calm)
    * Tension/relaxation cues: muscle tension, posture, clenching vs. ease
    * Presence/dissociation markers: grounded, here vs. "checked out", numb
    * Body-based confidence signals: posture, stance, voice, eye contact
    * Embodied emotion markers: where emotions live in the body (chest, throat, gut)
  - Somatic state assessment: grounded vs. dysregulated, present vs. dissociated
  - Grounding + presence coaching: techniques to embody calm and confidence

Somatic psychology (Levine, van der Kolk, Porges): the body holds and expresses
what the mind cannot say. Shallow breathing signals threat. Slumped posture signals
defeat. Grounded stance signals confidence. By attending to somatic cues—breathing,
tension, posture, voice—you can detect dysregulation early and intervene. By grounding
your own body, you access clarity, presence, and authentic confidence.

Romanian triggers live in core/somatic_keywords_ro.py; the English set is `EN`
below. Tokenization, diacritic folding and Snowball stemming are shared with other
frameworks via core/text_norm.py.
"""

from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.text_norm import find_all
    from core.somatic_keywords_ro import RO
except ImportError:  # imported flat (core/ dir on path)
    from text_norm import find_all
    from somatic_keywords_ro import RO

__all__ = ["SomaticState", "SomaticPattern", "SomaticModule"]


class SomaticState(Enum):
    """The primary somatic states in negotiation."""
    GROUNDED = "grounded"
    DYSREGULATED = "dysregulated"
    PRESENT = "present"
    DISSOCIATED = "dissociated"
    CONFIDENT = "confident"
    ANXIOUS = "anxious"


class SomaticPattern(Enum):
    """The 5 key somatic patterns in negotiation."""
    BREATHING_RHYTHM = "breathing_rhythm"
    TENSION_RELAXATION = "tension_relaxation"
    PRESENCE_DISSOCIATION = "presence_dissociation"
    CONFIDENCE_SIGNALS = "confidence_signals"
    EMBODIED_EMOTION = "embodied_emotion"


# English lexicon — same shape as core/somatic_keywords_ro.RO
EN = {
    "patterns": {
        "breathing_rhythm": [
            "i'm catching my breath", "my heart is racing", "shallow breathing",
            "racing heartbeat", "can't breathe", "breathing is tight", "shortness of breath",
            "quick breaths", "pounding heart", "my chest is tight", "rapid breathing",
            "i can't catch my breath", "breathing fast", "breathe deeply",
        ],
        "tension_relaxation": [
            "my shoulders are tense", "jaw clenching", "tight muscles", "relaxed",
            "tension in my neck", "i'm loosening up", "muscles are tight", "tense body",
            "clenching", "shoulders up", "rigidity", "ease", "relaxation", "loose",
        ],
        "presence_dissociation": [
            "i'm here", "present", "grounded", "checked out", "numb", "distant",
            "not here", "zoned out", "floating", "disconnected", "in the moment",
            "aware", "tuned in", "foggy", "hazy", "spacey", "embodied",
        ],
        "confidence_signals": [
            "i stand tall", "shoulders back", "eye contact", "my voice is strong",
            "projecting", "solid stance", "commanding presence", "assured", "hesitant",
            "voice wavers", "looking down", "shrinking", "small", "meek", "trembling",
        ],
        "embodied_emotion": [
            "my heart sinks", "gut feeling", "lump in my throat", "butterflies",
            "pit in my stomach", "chest tightness", "throat constriction",
            "belly tension", "heart pounding", "warmth in my chest", "cold shivers",
            "feeling it in my bones", "gut says", "my body knows",
        ],
    },
    "grounding_cues": [
        "feet on ground", "feeling my seat", "weight", "solid", "rooted",
        "grounded", "stable", "anchored", "four on the floor", "connected to earth",
        "my feet", "foundation", "supported", "held", "held by",
    ],
    "presence_cues": [
        "now", "here", "this moment", "present", "alive to", "tuned in",
        "aware", "awake", "alert", "focused", "engaged", "in flow",
        "in sync", "on point", "dialed in", "the present", "what's happening",
    ],
}

_PATTERN_INSIGHT = {
    "breathing_rhythm": (
        "Breathing Rhythm: the autonomic nervous system's voice.",
        "Fast/shallow: threat response active. Slow/deep: parasympathetic activation.",
        "Signal: notice the breath. Change the breath to shift the nervous system.",
    ),
    "tension_relaxation": (
        "Tension/Relaxation: muscles hold emotion and defensive patterns.",
        "Clenching: bracing, defensive. Ease: openness, safety.",
        "Signal: tension appears before conscious awareness. Release it to shift state.",
    ),
    "presence_dissociation": (
        "Presence/Dissociation: the degree to which you're embodied here.",
        "Present: awake, responsive. Dissociated: numb, distant, checked out.",
        "Signal: grounding practices bring presence back. Dissociation means dysregulation.",
    ),
    "confidence_signals": (
        "Confidence Signals: the body's vote on capability.",
        "Tall, open posture: I can handle this. Collapsed, small: I'm uncertain.",
        "Signal: power posing shifts confidence. Posture shapes self-perception.",
    ),
    "embodied_emotion": (
        "Embodied Emotion: where feelings live in the body.",
        "Emotions aren't abstract; they're visceral, localized, physical.",
        "Signal: scan your body. Name where you feel fear, joy, anger. Awareness dissolves numbness.",
    ),
}

_SOMATIC_STATE_GUIDANCE = {
    "grounded": (
        "Grounded State: connected to earth, stable, rooted.",
        "You can think clearly. Resilient. Responsive, not reactive.",
        "Maintain: keep feet planted. Notice weight. Breathe into your belly.",
    ),
    "dysregulated": (
        "Dysregulated State: nervous system is activated, out of balance.",
        "Flight/fight/freeze is online. Thinking is offline. Reactivity is high.",
        "Recovery: grounding exercises. Slow the breath. Feel your feet. Return to body.",
    ),
    "present": (
        "Present State: awake, here, engaged with what's actually happening.",
        "Clarity, responsiveness, authentic connection are possible.",
        "Maintain: keep attention in five senses. Notice what's happening now.",
    ),
    "dissociated": (
        "Dissociated State: checked out, numb, disconnected from body and environment.",
        "Protection mechanism. Shuts down feeling to avoid overwhelm.",
        "Recovery: gentle grounding. Slow, titrated re-engagement. Body scans.",
    ),
    "confident": (
        "Confident State: body votes yes. Posture is open, breath is steady, voice is clear.",
        "You feel capable and grounded.",
        "Maintain: power poses. Vocal projection. Upright posture. Eye contact.",
    ),
    "anxious": (
        "Anxious State: body is in alert/threat. Shallow breath, tension, small posture.",
        "Amygdala is voting. Prefrontal cortex is offline.",
        "Recovery: grounding, slow breathing, body reassurance, reorientation to safety.",
    ),
}


class SomaticModule:
    """
    Somatic analysis of negotiation dynamics.
    Detects breathing, tension, presence, confidence, and embodied emotion patterns.
    Assesses somatic state (grounded/dysregulated, present/dissociated, confident/anxious).
    Provides grounding and presence coaching.
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

    # -- Somatic pattern detection -----------------------------------

    _PATTERN_KEYS = (
        "breathing_rhythm", "tension_relaxation", "presence_dissociation",
        "confidence_signals", "embodied_emotion"
    )

    def detect_somatic_patterns(self, text: str) -> Dict:
        """Detect somatic patterns in the text."""
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
            "analysis_text": _PATTERN_INSIGHT.get(primary_finding, ("No pattern identified.", "", "")) if primary_finding else None,
        }

    # -- Somatic state assessment -----------------------------------

    def assess_somatic_state(self, text: str) -> Dict:
        """Assess grounded/dysregulated, present/dissociated, confident/anxious."""
        # Grounding assessment
        grounding_hits = find_all(text, {"grounded": EN["grounding_cues"]}, lang="en", first_phrase_only=False)
        ro_grounding = find_all(text, {"grounded": RO["grounding_cues"]}, lang="ro", first_phrase_only=False)
        grounding_count = len(set((h["keyword"] for h in grounding_hits + ro_grounding)))

        # Presence assessment
        presence_hits = find_all(text, {"present": EN["presence_cues"]}, lang="en", first_phrase_only=False)
        ro_presence = find_all(text, {"present": RO["presence_cues"]}, lang="ro", first_phrase_only=False)
        presence_count = len(set((h["keyword"] for h in presence_hits + ro_presence)))

        # Confidence assessment (from patterns)
        patterns = self.detect_somatic_patterns(text)
        confidence_score = patterns["patterns"]["confidence_signals"]

        # Determine states
        grounding_state = "grounded" if grounding_count > 0 else "dysregulated"
        presence_state = "present" if presence_count > 0 else "dissociated"
        confidence_state = "confident" if confidence_score > 0.3 else "anxious"

        return {
            "grounding_state": grounding_state,
            "presence_state": presence_state,
            "emotional_state": confidence_state,
            "grounding_indicators": grounding_count,
            "presence_indicators": presence_count,
            "confidence_score": round(confidence_score, 3),
            "overall_summary": f"{grounding_state} + {presence_state} + {confidence_state}",
        }

    # -- Full analysis -----------------------------------------------

    def analyze(self, text: str) -> Dict:
        """Full somatic analysis: patterns and state."""
        return {
            "somatic_patterns": self.detect_somatic_patterns(text),
            "somatic_state": self.assess_somatic_state(text),
        }

    def dual_speaker_somatic(self, your_text: str, their_text: str) -> Dict:
        """Analyze somatic states in both you and the counterparty."""
        return {
            "your_somatic": self.analyze(your_text),
            "their_somatic": self.analyze(their_text),
            "coaching": self._dual_somatic_coaching(your_text, their_text),
        }

    @staticmethod
    def _dual_somatic_coaching(your_text: str, their_text: str) -> str:
        module = SomaticModule()
        your_state = module.assess_somatic_state(your_text)
        their_state = module.assess_somatic_state(their_text)

        your_summary = your_state["overall_summary"]
        their_summary = their_state["overall_summary"]

        coaching = "DUAL-SPEAKER SOMATIC COACHING\n\n"
        coaching += f"YOUR SOMATIC STATE: {your_summary}\n"
        coaching += f"THEIR SOMATIC STATE: {their_summary}\n\n"

        coaching += (
            "SOMATIC AWARENESS:\n"
            "The body is speaking. Listen.\n\n"
            "If either of you is dysregulated:\n"
            "• Pause. Slow the breath. Ground your feet.\n"
            "• Signal safety: calm voice, open posture, predictability.\n"
            "• Allow the nervous system to reset before continuing.\n\n"
            "If both are grounded + present:\n"
            "• You're in optimal negotiation state.\n"
            "• Listen deeply. Move slowly. Let wisdom emerge from embodied presence.\n\n"
            "KEY SOMATIC MOVES:\n"
            "1. CHECK IN WITH YOUR BODY: Am I grounded? Present? Breathing?\n"
            "2. GROUND YOURSELF: Feet on floor. Feel your weight. Slow breath.\n"
            "3. READ THEIR BODY: What's their posture saying? Breathing? Tension?\n"
            "4. MATCH THEIR RHYTHM: If they're tense, slow and steady your pace.\n"
            "5. HOLD SPACE: Your embodied calm invites their regulation."
        )
        return coaching

    def prescribe_somatic_presence(self) -> str:
        """Coaching for embodied presence and grounding in negotiation."""
        return (
            "SOMATIC PRESENCE FOR NEGOTIATION\n\n"
            "THE POWER OF EMBODIMENT:\n"
            "When you're grounded in your body, you access clarity, presence, and authentic confidence.\n"
            "When you're dysregulated, you're reactive, defended, unclear.\n"
            "The negotiation happens in the body first. The words follow.\n\n"
            "BEFORE YOU NEGOTIATE:\n\n"
            "1. GROUND YOURSELF (2 minutes):\n"
            "   • Stand with feet hip-width apart, or sit with feet flat on floor.\n"
            "   • Feel the points of contact: soles of feet, sits bones, back.\n"
            "   • Notice: I am solid. I am held by the earth. I am stable.\n\n"
            "2. BREATHE (3 minutes):\n"
            "   • Slow your breath. Aim for 5-second inhale, 7-second exhale.\n"
            "   • Belly breathing, not chest. Let the diaphragm do the work.\n"
            "   • Notice: My nervous system is calm. I am present.\n\n"
            "3. EMBODY CONFIDENCE:\n"
            "   • Shoulders back. Chest open. Head upright.\n"
            "   • Feel this posture. Let your body know: I am capable.\n"
            "   • Speak from your belly, not your throat. Project, don't strain.\n\n"
            "DURING NEGOTIATION:\n\n"
            "1. SCAN YOUR BODY (every 2-3 minutes):\n"
            "   • Feet on floor? Check.\n"
            "   • Breathing steady? If shallow, slow it down.\n"
            "   • Shoulders? Relax them if tense.\n"
            "   • Jaw? Unclench it.\n\n"
            "2. NOTICE THEIR BODY:\n"
            "   • Are they grounded or dysregulated?\n"
            "   • Is their breathing shallow or deep?\n"
            "   • What's their posture saying?\n"
            "   • Meet them where they are somatically.\n\n"
            "3. STAY PRESENT:\n"
            "   • Feel your feet. Feel the chair. Feel the air.\n"
            "   • Notice sounds, sights. Five senses, now.\n"
            "   • Your presence invites their presence.\n\n"
            "4. USE TENSION AS SIGNAL:\n"
            "   • Tension is information. What's it saying?\n"
            "   • Instead of pushing through, breathe into it.\n"
            "   • \"I notice I'm tense. Let me slow down.\"\n\n"
            "RESULT: Embodied clarity, authentic confidence, effective presence."
        )
