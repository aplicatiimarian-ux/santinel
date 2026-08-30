# -*- coding: utf-8 -*-
"""
Narrative Module for SANTINEL
Detects and reframes the stories people tell in negotiations.

Bilingual (EN + RO):
  - 4 narrative archetypes: hero's journey, victim, victor, collaborative
  - Dominant narrative vs. alternative narratives detection
  - Identity story analysis (who am I in this story?)
  - Meaning-making patterns (causality, agency, purpose)
  - Narrative reframing coaching (same facts, different story)

Narrative psychology (McAdams, Bruner): we make sense of life through stories.
In negotiation, the narrative people tell shapes their choices. A victim narrative
("they control everything") limits agency. A hero narrative ("I can overcome this")
enables resilience. A collaborative narrative ("we can both win") opens creativity.
Reframing the narrative—keeping facts the same, changing meaning—shifts behavior.

Romanian triggers live in core/narrative_keywords_ro.py; the English set is `EN`
below. Tokenization, diacritic folding and Snowball stemming are shared with other
frameworks via core/text_norm.py.
"""

from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.text_norm import find_all
    from core.narrative_keywords_ro import RO
except ImportError:  # imported flat (core/ dir on path)
    from text_norm import find_all
    from narrative_keywords_ro import RO

__all__ = ["NarrativeArchetype", "NarrativeModule"]


class NarrativeArchetype(Enum):
    """The 4 primary narrative archetypes in negotiation."""
    HEROS_JOURNEY = "heros_journey"
    VICTIM_NARRATIVE = "victim_narrative"
    VICTOR_NARRATIVE = "victor_narrative"
    COLLABORATIVE_NARRATIVE = "collaborative_narrative"


# English lexicon — same shape as core/narrative_keywords_ro.RO
EN = {
    "narratives": {
        "heros_journey": [
            "i faced a challenge", "i overcame", "i learned", "i grew",
            "it was hard but i made it", "i struggled and succeeded", "i found a way",
            "adversity made me stronger", "i discovered", "i persevered", "i transformed",
            "the difficulty led to growth", "i became", "through struggle came wisdom",
        ],
        "victim_narrative": [
            "they did this to me", "i was wronged", "i have no control",
            "this happened to me", "they always", "i'm stuck", "powerless",
            "the system is against me", "bad luck", "i'm a victim of",
            "i can't escape this", "i'm trapped", "they won't let me",
        ],
        "victor_narrative": [
            "i won", "i defeated", "i dominated", "i crushed",
            "i beat them", "i'm the winner", "i came out on top",
            "i conquered", "my strategy worked", "i outmaneuvered",
            "victory is mine", "i proved i'm stronger", "i always win",
        ],
        "collaborative_narrative": [
            "we worked together", "we both benefited", "we solved it together",
            "collaboration led to", "our partnership", "we found a way",
            "mutual benefit", "we're stronger together", "together we created",
            "our shared goal", "collective success", "we achieved",
        ],
    },
    "identity_patterns": {
        "agency": [
            "i decided", "i chose", "i made", "i controlled", "i acted",
            "i took charge", "i led", "i drove", "i initiated", "i determined",
            "in my power", "i'm the architect", "i shaped", "i created",
        ],
        "passivity": [
            "it happened", "i was told", "i had to", "i couldn't",
            "they decided", "circumstances forced me", "i was compelled",
            "left with no choice", "i was powerless", "at their mercy",
            "things happened to me", "i had no say", "i was subjected to",
        ],
        "connection": [
            "we built", "together", "our shared", "mutual", "interdependent",
            "connected", "partnership", "aligned", "solidarity", "united",
            "collective", "we're in this together", "our common", "shared success",
        ],
    },
    "meaning_patterns": {
        "growth": [
            "i learned", "insight", "wisdom", "transformation", "evolution",
            "became wiser", "gained understanding", "deeper perspective",
            "sees things differently now", "newfound appreciation", "personal growth",
        ],
        "loss": [
            "lost", "wasted", "ruined", "destroyed", "failed",
            "broken", "damaged", "irreversible", "never recover", "all gone",
            "nothing left", "end of", "finished",
        ],
        "purpose": [
            "for a reason", "meant to", "purpose of", "why this matters",
            "greater meaning", "bigger picture", "contributes to", "serves",
            "aligns with values", "makes sense now", "it all fits", "the point is",
        ],
    },
}

_NARRATIVE_PROFILE = {
    "heros_journey": (
        "Hero's Journey: protagonist faces challenge, grows, succeeds through perseverance.",
        "Identity: 'I can overcome adversity. I learn from difficulty. I transform.'",
        "In negotiation: resilient, resourceful, willing to face pressure. Growth-oriented.",
    ),
    "victim_narrative": (
        "Victim Narrative: protagonist is acted upon, powerless, wronged by forces beyond control.",
        "Identity: 'I'm helpless. They control me. The system is rigged.'",
        "In negotiation: defensive, blame-focused, resigned. Limited agency.",
    ),
    "victor_narrative": (
        "Victor Narrative: protagonist wins, dominates, proves superiority.",
        "Identity: 'I'm the strongest. I always win. Dominance is what matters.'",
        "In negotiation: competitive, win-at-all-costs, sees negotiation as conquest.",
    ),
    "collaborative_narrative": (
        "Collaborative Narrative: protagonist succeeds through partnership, mutual benefit, shared values.",
        "Identity: 'We're stronger together. Mutual success is possible. Connection matters.'",
        "In negotiation: cooperative, trust-building, seeks win-win. Values relationship.",
    ),
}

_NARRATIVE_IMPACT = {
    "heros_journey": "Empowers resilience. Enables creative problem-solving. Builds trust over time.",
    "victim_narrative": "Disempowers agency. Reinforces defensiveness. Narrows solution space.",
    "victor_narrative": "Drives competitiveness. Makes collaboration difficult. Creates adversaries.",
    "collaborative_narrative": "Enables cooperation. Builds sustainable agreements. Creates allies.",
}


class NarrativeModule:
    """
    Narrative analysis of negotiation discourse.
    Detects dominant narrative archetype, identifies identity stories,
    recognizes meaning-making patterns, and coaches narrative reframing.
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

    # -- Narrative archetype detection ----------------------------

    _NARRATIVE_KEYS = (
        "heros_journey", "victim_narrative", "victor_narrative", "collaborative_narrative"
    )

    def detect_dominant_narrative(self, text: str) -> Dict:
        """Detect which narrative archetype dominates the text."""
        hits = self._scan(text, "narratives")
        counts = {k: 0 for k in self._NARRATIVE_KEYS}
        matched = {k: [] for k in self._NARRATIVE_KEYS}

        for h in hits:
            counts[h["category"]] += 1
            matched[h["category"]].append(h["keyword"])

        total = sum(counts.values())
        if total == 0:
            primary = "collaborative_narrative"  # assume collaborative by default
            scores = {k: 0.0 for k in self._NARRATIVE_KEYS}
        else:
            primary = max(counts, key=counts.get)
            scores = {k: round(v / total, 3) for k, v in counts.items()}

        return {
            "dominant_narrative": primary,
            "scores": scores,
            "matched": matched,
            "profile": _NARRATIVE_PROFILE[primary],
            "impact": _NARRATIVE_IMPACT[primary],
        }

    # -- Identity story analysis ---------------------------------

    def analyze_identity_patterns(self, text: str) -> Dict:
        """Analyze identity: agency, passivity, connection."""
        agency_hits = self._scan_identity_domain(text, "agency")
        passivity_hits = self._scan_identity_domain(text, "passivity")
        connection_hits = self._scan_identity_domain(text, "connection")

        agency_count = len(set((h["keyword"] for h in agency_hits)))
        passivity_count = len(set((h["keyword"] for h in passivity_hits)))
        connection_count = len(set((h["keyword"] for h in connection_hits)))

        # Determine primary identity pattern
        if agency_count > passivity_count:
            agency_stance = "agentic"
        elif passivity_count > agency_count:
            agency_stance = "passive"
        else:
            agency_stance = "mixed"

        connection_stance = "connected" if connection_count > 0 else "isolated"

        return {
            "agency_stance": agency_stance,
            "agency_indicators": agency_count,
            "passivity_indicators": passivity_count,
            "connection_stance": connection_stance,
            "connection_indicators": connection_count,
            "identity_summary": f"Identity: {agency_stance} + {connection_stance}",
        }

    @staticmethod
    def _scan_identity_domain(text: str, domain: str) -> List[Dict]:
        """Scan identity patterns (agency, passivity, connection)."""
        en_dict = {"agency": EN["identity_patterns"]["agency"],
                   "passivity": EN["identity_patterns"]["passivity"],
                   "connection": EN["identity_patterns"]["connection"]}
        ro_dict = {"agency": RO["identity_patterns"]["agency"],
                   "passivity": RO["identity_patterns"]["passivity"],
                   "connection": RO["identity_patterns"]["connection"]}

        en = find_all(text, {domain: en_dict[domain]}, lang="en", first_phrase_only=False)
        ro = find_all(text, {domain: ro_dict[domain]}, lang="ro", first_phrase_only=False)

        seen = set()
        out = []
        for hit in en + ro:
            sig = (hit["keyword"],)
            if sig in seen:
                continue
            seen.add(sig)
            out.append(hit)
        return out

    # -- Meaning-making patterns ---------------------------------

    def detect_meaning_patterns(self, text: str) -> Dict:
        """Detect how the text makes meaning: growth, loss, purpose."""
        growth_hits = find_all(text, {"growth": EN["meaning_patterns"]["growth"]}, lang="en", first_phrase_only=False)
        loss_hits = find_all(text, {"loss": EN["meaning_patterns"]["loss"]}, lang="en", first_phrase_only=False)
        purpose_hits = find_all(text, {"purpose": EN["meaning_patterns"]["purpose"]}, lang="en", first_phrase_only=False)

        ro_growth = find_all(text, {"growth": RO["meaning_patterns"]["growth"]}, lang="ro", first_phrase_only=False)
        ro_loss = find_all(text, {"loss": RO["meaning_patterns"]["loss"]}, lang="ro", first_phrase_only=False)
        ro_purpose = find_all(text, {"purpose": RO["meaning_patterns"]["purpose"]}, lang="ro", first_phrase_only=False)

        growth_count = len(set((h["keyword"] for h in growth_hits + ro_growth)))
        loss_count = len(set((h["keyword"] for h in loss_hits + ro_loss)))
        purpose_count = len(set((h["keyword"] for h in purpose_hits + ro_purpose)))

        return {
            "growth_indicators": growth_count,
            "loss_indicators": loss_count,
            "purpose_indicators": purpose_count,
            "meaning_orientation": self._classify_meaning(growth_count, loss_count, purpose_count),
        }

    @staticmethod
    def _classify_meaning(growth: int, loss: int, purpose: int) -> str:
        if growth > loss and purpose > 0:
            return "growth-oriented"
        elif loss > growth:
            return "loss-focused"
        elif purpose > 0:
            return "purpose-driven"
        else:
            return "neutral"

    # -- Full analysis -----------------------------------------------

    def analyze(self, text: str) -> Dict:
        """Full narrative analysis: archetype, identity, meaning-making."""
        return {
            "dominant_narrative": self.detect_dominant_narrative(text),
            "identity_patterns": self.analyze_identity_patterns(text),
            "meaning_patterns": self.detect_meaning_patterns(text),
        }

    def dual_speaker_narrative(self, your_text: str, their_text: str) -> Dict:
        """Analyze narratives in both you and the counterparty."""
        return {
            "your_narrative": self.analyze(your_text),
            "their_narrative": self.analyze(their_text),
            "coaching": self._dual_narrative_coaching(your_text, their_text),
        }

    @staticmethod
    def _dual_narrative_coaching(your_text: str, their_text: str) -> str:
        module = NarrativeModule()
        your_narrative = module.detect_dominant_narrative(your_text)["dominant_narrative"]
        their_narrative = module.detect_dominant_narrative(their_text)["dominant_narrative"]
        your_identity = module.analyze_identity_patterns(your_text)["identity_summary"]
        their_identity = module.analyze_identity_patterns(their_text)["identity_summary"]

        coaching = "DUAL-SPEAKER NARRATIVE ANALYSIS\n\n"
        coaching += f"YOUR STORY: {your_narrative.replace('_', ' ').title()}\n"
        coaching += f"           Identity: {your_identity}\n\n"
        coaching += f"THEIR STORY: {their_narrative.replace('_', ' ').title()}\n"
        coaching += f"            Identity: {their_identity}\n\n"

        if your_narrative == their_narrative:
            coaching += f"NARRATIVE ALIGNMENT: Both tell a {your_narrative.replace('_', ' ')} story.\n\n"
        else:
            coaching += f"NARRATIVE MISMATCH: You tell {your_narrative.replace('_', ' ')},\n"
            coaching += f"                    they tell {their_narrative.replace('_', ' ')}.\n"
            coaching += "This shapes how you each approach the negotiation.\n\n"

        coaching += (
            "KEY MOVES FOR REFRAMING:\n"
            "1. Name the narrative: 'I notice we're both telling a story about this.'\n"
            "2. Separate facts from interpretation: 'The facts are X. The story we tell is Y.'\n"
            "3. Propose alternative narratives: 'What if we told this as a hero's journey?\n"
            "   What if this is actually a collaboration waiting to happen?'\n"
            "4. Shift from victim → hero: 'You faced this challenge. What did you learn?\n"
            "   What strength did you discover?'\n"
            "5. Shift from victor → collaborative: 'We both want something real here.\n"
            "   What if we succeeded together instead of against each other?'"
        )
        return coaching

    def prescribe_narrative_awareness(self) -> str:
        """Coaching for working with narratives in negotiation."""
        return (
            "NARRATIVE AWARENESS IN NEGOTIATION\n\n"
            "THE POWER OF NARRATIVE:\n"
            "We don't see reality; we see our story about reality. The narrative we tell\n"
            "shapes how we feel, what options we see, and what we do.\n\n"
            "COMMON TRAP NARRATIVES:\n"
            "• VICTIM: 'They control everything. I'm helpless.' → Resignation, defensiveness.\n"
            "• VICTOR: 'I win or nothing. Dominance is the goal.' → Mistrust, adversarialism.\n"
            "• FALSE HERO: 'I'll overcome them alone.' → Exhaustion, isolation.\n\n"
            "EMPOWERING NARRATIVES:\n"
            "• TRUE HERO: 'I face challenges, learn, and grow.' → Resilience, creativity.\n"
            "• COLLABORATIVE: 'We can both win together.' → Trust, cooperation, innovation.\n\n"
            "HOW TO REFRAME:\n"
            "1. NOTICE YOUR NARRATIVE: What story are you telling?\n"
            "   'They're attacking me.' vs. 'We're figuring this out.'\n\n"
            "2. SEPARATE FACTS FROM STORY:\n"
            "   FACTS: They said no. Deadline is tight. Budget is limited.\n"
            "   STORY: 'They're being unreasonable.' vs. 'They have constraints like I do.'\n\n"
            "3. CHOOSE A GENERATIVE NARRATIVE:\n"
            "   Same facts, different story:\n"
            "   FROM: 'This negotiation is a battle I need to win.'\n"
            "   TO: 'This negotiation is a puzzle we can solve together.'\n\n"
            "4. TEST THE NEW NARRATIVE:\n"
            "   Does it open options or close them?\n"
            "   Does it invite collaboration or defensiveness?\n"
            "   Does it honor both parties or just one?\n\n"
            "5. SHARE THE REFRAME:\n"
            "   'I noticed I was telling myself a story that this was a battle.\n"
            "   What if we tell it as a collaboration instead?'\n\n"
            "RESULT: New narrative → new emotions → new possibilities → new outcomes."
        )
