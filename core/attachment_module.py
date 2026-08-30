# -*- coding: utf-8 -*-
"""
Attachment Framework Module for SANTINEL
Detects attachment styles and relational wounds in negotiation discourse.

Bilingual (EN + RO):
  - 4 attachment styles: secure, anxious, avoidant, fearful-avoidant
  - 2D anxiety-avoidance scoring (0.0 to 1.0 on each axis)
  - Core wounds and triggers (abandonment, control, inadequacy, distrust)
  - Coaching for secure attachment conversation

Attachment theory (Bowlby, Hazan & Shaver): early relational patterns shape
how people respond to pressure, disagreement, vulnerability, and trust.

Romanian triggers live in core/attachment_keywords_ro.py; the English set is `EN`
below. Tokenization, diacritic folding and Snowball stemming are shared with
other frameworks via core/text_norm.py.
"""

from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.text_norm import find_all
    from core.attachment_keywords_ro import RO
except ImportError:  # imported flat (core/ dir on path)
    from text_norm import find_all
    from attachment_keywords_ro import RO

__all__ = ["AttachmentStyle", "CoreWound", "AttachmentModule"]


class AttachmentStyle(Enum):
    """The 4 primary attachment styles (Hazan & Shaver)."""
    SECURE = "secure"
    ANXIOUS = "anxious"
    AVOIDANT = "avoidant"
    FEARFUL_AVOIDANT = "fearful_avoidant"


class CoreWound(Enum):
    """Relational wounds that drive attachment patterns."""
    ABANDONMENT = "abandonment"
    CONTROL = "control"
    INADEQUACY = "inadequacy"
    DISTRUST = "distrust"


# English lexicon — same shape as core/attachment_keywords_ro.RO
EN = {
    "anxiety_markers": {
        "anxiety": [
            "i'm worried you'll leave", "what if you abandon me", "i need reassurance",
            "don't leave me", "i can't bear losing you", "i'm so afraid you'll reject me",
            "please don't go", "i need constant confirmation", "will you stay with me",
            "i'm terrified of abandonment", "i'm scared", "what if you refuse", "will you abandon me",
            "are you scared", "i'm afraid", "but what if", "i can't accept without",
        ],
    },
    "avoidance_markers": {
        "avoidance": [
            "i don't need anyone", "closeness makes me uncomfortable", "i prefer to be alone",
            "relationships are too dependent", "i keep my distance", "i need my freedom",
            "i don't like depending on people", "intimacy feels suffocating", "i'd rather not talk about this",
            "don't get too close", "i'm fine on my own", "i can handle this myself", "i don't need help",
            "let me handle it", "i prefer independence", "don't waste time",
        ],
    },
    "secure_markers": {
        "secure": [
            "i trust you", "we can work this out together", "i feel safe with you",
            "i'm comfortable being open", "i can rely on you", "let's be honest with each other",
            "i appreciate your perspective", "i'm confident in us", "i'm willing to be vulnerable",
            "we can handle this",
        ],
    },
    "wounds": {
        "abandonment": [
            "you always leave", "i'm always left behind", "nobody stays for me",
            "i'm going to be alone", "you'll find someone better", "i don't matter enough",
            "you'll reject me like everyone else", "i'm unlovable",
        ],
        "control": [
            "you're trying to control me", "i need to be in charge", "let me decide",
            "i can't trust your judgment", "you're dominating me", "i have to do it myself",
            "if you care you'll do it my way", "i must be in control", "must be my way",
            "have to do in my way", "need to do myself", "only i can", "my control",
        ],
        "inadequacy": [
            "i'm not good enough", "i'm not smart enough", "i'll never be good at this",
            "i'm failing you", "i'm too slow", "i'm not worthy of your time",
            "i'm incompetent", "i'll never measure up",
        ],
        "distrust": [
            "i don't believe you", "you're lying", "i can't trust anyone",
            "people always betray me", "nobody tells the truth", "you have hidden motives",
            "i'm suspicious of your intentions", "you're hiding something",
        ],
    },
}

_ATTACHMENT_STYLE_PROFILE = {
    "secure": (
        "Secure Attachment: comfortable with closeness and independence; trusts and is trustworthy.",
        "Strengths: negotiates with clarity; handles disagreement without threat; vulnerable but boundaried.",
        "In negotiation: direct, collaborative, adaptable. Ideal partner.",
    ),
    "anxious": (
        "Anxious Attachment: craves closeness; fears rejection; seeks reassurance.",
        "Strengths: attuned to others; collaborative; willing to compromise.",
        "Vulnerabilities: may concede too much; oversensitive to signs of rejection; clingy.",
    ),
    "avoidant": (
        "Avoidant Attachment: uncomfortable with closeness; values independence; detached.",
        "Strengths: self-reliant; clear on boundaries; won't be exploited.",
        "Vulnerabilities: may withdraw when pressure rises; hard to reach emotionally; dismissive.",
    ),
    "fearful_avoidant": (
        "Fearful-Avoidant Attachment: conflicted — craves closeness but fears it deeply.",
        "Strengths: aware of the conflict; may seek resolution once safe.",
        "Vulnerabilities: inconsistent; unpredictable; may flip between clinging and fleeing.",
    ),
}

_WOUND_IMPACT = {
    "abandonment": (
        "Abandonment Wound: 'I will be left behind.'",
        "Triggered by: delay, distance, signs of disengagement, unclear commitment.",
        "In negotiation: clings, over-yields, over-communicates to hold the deal.",
    ),
    "control": (
        "Control Wound: 'I must control to be safe.'",
        "Triggered by: perceived directives, loss of autonomy, others' priorities overriding theirs.",
        "In negotiation: resists, escalates, demands their way, or withdraws.",
    ),
    "inadequacy": (
        "Inadequacy Wound: 'I'm not good/smart/capable enough.'",
        "Triggered by: comparison, criticism, being asked to stretch, complexity.",
        "In negotiation: apologizes excessively, defers, self-sabotages.",
    ),
    "distrust": (
        "Distrust Wound: 'People have hidden motives; I can't rely on them.'",
        "Triggered by: unfamiliar context, opacity, jargon, or any sign of deception.",
        "In negotiation: questions motives, reads between the lines, slow to commit.",
    ),
}


class AttachmentModule:
    """
    Attachment-based relational analysis for negotiations.
    Detects attachment style via anxiety and avoidance scoring, identifies
    core wounds and triggers, and provides coaching to secure attachment.
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

    # -- Anxiety-Avoidance Scoring ----------------------------------

    def score_attachment(self, text: str) -> Dict:
        """
        Score attachment on 2D axes:
        - anxiety (0.0-1.0): fear of abandonment, need for reassurance
        - avoidance (0.0-1.0): discomfort with intimacy, independence
        """
        anxiety_hits = find_all(text, EN["anxiety_markers"], lang="en", first_phrase_only=False)
        avoidance_hits = find_all(text, EN["avoidance_markers"], lang="en", first_phrase_only=False)
        secure_hits = find_all(text, EN["secure_markers"], lang="en", first_phrase_only=False)

        ro_anxiety = find_all(text, RO["anxiety_markers"], lang="ro", first_phrase_only=False)
        ro_avoidance = find_all(text, RO["avoidance_markers"], lang="ro", first_phrase_only=False)
        ro_secure = find_all(text, RO["secure_markers"], lang="ro", first_phrase_only=False)

        anxiety_count = len(set((h["keyword"] for h in anxiety_hits + ro_anxiety)))
        avoidance_count = len(set((h["keyword"] for h in avoidance_hits + ro_avoidance)))
        secure_count = len(set((h["keyword"] for h in secure_hits + ro_secure)))

        # Normalize: total references anchor the scale
        total = max(1, anxiety_count + avoidance_count + secure_count)
        anxiety_score = round(anxiety_count / total, 3)
        avoidance_score = round(avoidance_count / total, 3)
        secure_score = round(secure_count / total, 3)

        # Determine primary style based on quadrant
        style = self._classify_style(anxiety_score, avoidance_score)

        return {
            "anxiety": anxiety_score,
            "avoidance": avoidance_score,
            "confidence_score": secure_score,
            "primary_finding": style,
            "raw_matches_anxiety": [h["keyword"] for h in (anxiety_hits + ro_anxiety)],
            "raw_matches_avoidance": [h["keyword"] for h in (avoidance_hits + ro_avoidance)],
        }

    @staticmethod
    def _classify_style(anxiety: float, avoidance: float) -> str:
        """Classify attachment style based on 2D scores."""
        if anxiety < 0.33 and avoidance < 0.33:
            return "secure"
        elif anxiety >= 0.33 and avoidance < 0.33:
            return "anxious"
        elif anxiety < 0.33 and avoidance >= 0.33:
            return "avoidant"
        else:  # anxiety >= 0.33 and avoidance >= 0.33
            return "fearful_avoidant"

    # -- Wounds and Triggers ----------------------------------------

    def detect_wounds(self, text: str) -> Dict:
        """Identify triggered core wounds in the discourse."""
        wounds_hits = self._scan(text, "wounds")
        by_wound: Dict[str, Dict] = {}

        for h in wounds_hits:
            entry = by_wound.setdefault(h["category"], {
                "wound": h["category"],
                "analysis_text": _WOUND_IMPACT[h["category"]][0],
                "trigger_pattern": _WOUND_IMPACT[h["category"]][1],
                "coaching_guidance": _WOUND_IMPACT[h["category"]][2],
                "raw_matches": [],
            })
            entry["raw_matches"].append(h["keyword"])

        wounds = list(by_wound.values())
        return {
            "detected_patterns": wounds,
            "count": len(wounds),
            "primary_finding": wounds[0]["wound"] if wounds else None,
        }

    # -- Full analysis -----------------------------------------------

    def analyze(self, text: str) -> Dict:
        """Full attachment analysis: style, anxiety-avoidance scores, wounds."""
        return {
            "attachment_style": self.score_attachment(text),
            "wounds": self.detect_wounds(text),
        }

    def dual_speaker_attachment(self, your_text: str, their_text: str) -> Dict:
        """Assess attachment in both you and the counterparty."""
        return {
            "your_attachment": self.analyze(your_text),
            "their_attachment": self.analyze(their_text),
            "coaching": self._dual_attachment_coaching(your_text, their_text),
        }

    @staticmethod
    def _dual_attachment_coaching(your_text: str, their_text: str) -> str:
        module = AttachmentModule()
        your = module.score_attachment(your_text)
        their = module.score_attachment(their_text)

        your_style = your.get("primary_finding") or your.get("attachment_style", "secure")
        their_style = their.get("primary_finding") or their.get("attachment_style", "secure")

        return (
            f"DUAL-ATTACHMENT COACHING\n\n"
            f"YOU: {your_style.upper()} (anxiety={your['anxiety']:.2f}, avoidance={your['avoidance']:.2f})\n"
            f"THEM: {their_style.upper()} (anxiety={their['anxiety']:.2f}, avoidance={their['avoidance']:.2f})\n\n"
            f"KEY MOVES:\n"
            f"1. Recognize the dance: both have protective patterns.\n"
            f"2. Name it calmly: 'I notice we both get cautious when pressure rises.'\n"
            f"3. Propose secure behavior: direct, honest, predictable.\n"
            f"4. Offer reassurance tailored to their style:\n"
            f"   - If anxious: regular updates, clear timelines, commitment language.\n"
            f"   - If avoidant: respect autonomy, reduce pressure, give space to decide.\n"
            f"   - If fearful: go slow, be consistent, offer safety *and* freedom.\n"
            f"5. Lead by your secure attachment: stay open, follow through, admit mistakes."
        )

    def prescribe_secure_attachment_negotiation(self) -> str:
        """Guidance for a secure-attachment conversation."""
        return (
            "SECURE ATTACHMENT IN NEGOTIATION\n\n"
            "FOUNDATION: Trust is earned through consistency, honesty, and reliability.\n\n"
            "1. BE PRESENT: Listen to understand, not to defend. Ask questions.\n\n"
            "2. BE HONEST: State your needs, constraints, and bottom line clearly.\n"
            "   Do not pretend or hide. Vulnerability builds trust.\n\n"
            "3. BE RELIABLE: Follow through on every commitment, no matter how small.\n"
            "   Predictability quiets old fears.\n\n"
            "4. RESPECT AUTONOMY: Acknowledge their right to decide, even if they refuse.\n"
            "   Control-seeking triggers avoidance; respect invites closeness.\n\n"
            "5. NAME THE DYNAMIC: If you sense fear or withdrawal,\n"
            "   say it aloud: 'I notice we're both hesitant. What would help?'\n\n"
            "6. REPAIR QUICKLY: If you misstep, own it and correct.\n"
            "   'I wasn't clear; let me try again.'\n\n"
            "RESULT: Both sides feel safe. Creativity and collaboration follow."
        )
