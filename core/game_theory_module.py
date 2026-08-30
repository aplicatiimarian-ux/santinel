# -*- coding: utf-8 -*-
"""
Game Theory Module for SANTINEL
Analyzes strategic interactions and game structures in negotiations.

Bilingual (EN + RO):
  - 4 game archetypes: prisoner's dilemma, zero-sum, coordination game, battle of sexes
  - Nash equilibrium detection (what rational self-interest drives)
  - Cooperative outcome detection (what's best for both)
  - BATNA (Best Alternative To Negotiated Agreement) assessment
  - ZOPA (Zone Of Possible Agreement) identification
  - Strategic position: dominant, advantageous, parity, disadvantaged
  - Coaching for cooperative vs. competitive play

Game theory (von Neumann, Nash, Schelling): predicts outcomes when rational actors
pursue self-interest. In negotiation, knowing the game structure lets you either
cooperate (if mutual benefit exists) or compete (if truly zero-sum).

Romanian triggers live in core/game_theory_keywords_ro.py; the English set is `EN`
below. Tokenization, diacritic folding and Snowball stemming are shared with other
frameworks via core/text_norm.py.
"""

from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.text_norm import find_all
    from core.game_theory_keywords_ro import RO
except ImportError:  # imported flat (core/ dir on path)
    from text_norm import find_all
    from game_theory_keywords_ro import RO

__all__ = ["GameArchetype", "StrategicPosition", "GameTheoryModule"]


class GameArchetype(Enum):
    """The 4 primary game structures in negotiation."""
    PRISONERS_DILEMMA = "prisoners_dilemma"
    ZERO_SUM = "zero_sum"
    COORDINATION_GAME = "coordination_game"
    BATTLE_OF_SEXES = "battle_of_sexes"


class StrategicPosition(Enum):
    """Your relative position in the negotiation."""
    DOMINANT = "dominant"
    ADVANTAGEOUS = "advantageous"
    PARITY = "parity"
    DISADVANTAGED = "disadvantaged"


# English lexicon — same shape as core/game_theory_keywords_ro.RO
EN = {
    "games": {
        "prisoners_dilemma": [
            "if i cooperate and you don't", "we both benefit if we cooperate", "mutual trust",
            "if you betray me", "i can't trust you to cooperate", "what if you backstab",
            "we'd both be better off if we", "but you might defect", "defection is tempting",
            "i'll cooperate if you do", "tit for tat",
        ],
        "zero_sum": [
            "what you gain is what i lose", "every dollar you save is a dollar i spend",
            "your win is my loss", "we can't both win", "it's either you or me",
            "one of us has to lose", "your profit is my cost", "my margin is your expense",
            "you're trying to squeeze me", "you win at my expense",
        ],
        "coordination_game": [
            "we both benefit if we align", "we need to coordinate", "let's sync up",
            "we want the same thing", "we're on the same team", "we both prefer",
            "coordination is key", "we need to be in sync", "both of us want",
            "the challenge is agreeing on how", "we're allied", "the challenge is coordinating",
            "we want the same outcome", "aligning on",
        ],
        "battle_of_sexes": [
            "i prefer this, you prefer that", "we disagree on", "your preference vs mine",
            "we want different things", "we both want to agree, but on what",
            "you want one way, i want another", "conflicting priorities",
            "you value this, i value that", "we're at odds on", "disagreement on priorities",
        ],
    },
    "strategic_positions": {
        "dominant": [
            "i hold the cards", "i have leverage", "they need me more than i need them",
            "i can walk away", "i have options", "i'm in the driver's seat",
            "the power is on my side", "i'm in a strong position", "they're desperate",
            "i can afford to wait", "they can't afford to lose this",
        ],
        "advantageous": [
            "i have a slight edge", "my position is stronger", "i'm better positioned",
            "i have some leverage", "i have a backup plan", "i'm not desperate",
            "i have some flexibility", "i'm in a reasonably strong spot",
            "i have options they don't", "i'm not as exposed as they are",
        ],
        "parity": [
            "we're evenly matched", "we're on equal footing", "we both need this",
            "mutual dependence", "we're in a balanced position", "neither of us can afford to lose",
            "we're roughly equivalent", "we both have leverage", "it's a fair fight",
            "we're equally positioned", "stalemate",
        ],
        "disadvantaged": [
            "they have the leverage", "they hold the cards", "i need this more than they do",
            "i'm in a weak position", "they can walk away easily", "i'm desperate",
            "i have no backup", "they have options i don't", "i'm trapped",
            "the power is on their side", "i'm at a disadvantage",
        ],
    },
    "batna": [
        "my backup plan is", "if this falls through", "my alternative is", "my walk away point is",
        "worst case i", "if we don't reach a deal", "my fallback is", "my best alternative",
        "my outside option is", "if negotiation fails", "i can always",
    ],
    "zopa": [
        "we can both gain if", "the overlap is", "there's room for both to win",
        "your bottom line is", "my minimum is", "both of us could accept",
        "we have common ground at", "the zone of agreement", "we both could live with",
        "mutual benefit exists if", "the range where both", "both acceptable at",
    ],
}

_GAME_PROFILE = {
    "prisoners_dilemma": (
        "Prisoner's Dilemma: mutual cooperation is best, but rational self-interest leads to mutual defection.",
        "Nash equilibrium: both defect (bad for both). Cooperative outcome: both cooperate (good for both).",
        "The tragedy: trust enables cooperation; distrust forces defection.",
    ),
    "zero_sum": (
        "Zero-Sum Game: what you gain is exactly what I lose. No mutual gain possible.",
        "Nash equilibrium: compete fully. Cooperative outcome: none (it's not a cooperative game).",
        "The paradox: we can't both win; negotiation is about who wins how much.",
    ),
    "coordination_game": (
        "Coordination Game: we both benefit from coordinating, but disagree on *how*.",
        "Nash equilibrium: multiple equilibria (both ways of coordinating work). Cooperative outcome: any alignment.",
        "The challenge: pick a focal point both find natural/fair.",
    ),
    "battle_of_sexes": (
        "Battle of the Sexes: conflicting preferences but both prefer agreement to disagreement.",
        "Nash equilibrium: mixed (random choices). Cooperative outcome: compromise or alternation.",
        "The tension: you want A, I want B, but we both prefer (A or B) to (nothing).",
    ),
}

_GAME_DYNAMICS = {
    "prisoners_dilemma": "Risk: defection. Reward: mutual cooperation. Build trust via: small steps, verification, repetition.",
    "zero_sum": "No trust possible. Maximize your gain; assume opponent is doing the same. Anchor high; negotiate hard.",
    "coordination_game": "Alignment is mutual interest. Signal your preference clearly. Listen for theirs. Find common ground.",
    "battle_of_sexes": "Both prefer agreement. Reframe: find option that satisfies both better. Compromise or take turns.",
}

_STRATEGIC_POSITION_GUIDANCE = {
    "dominant": "You can afford to be patient and firm. Set terms. Offer takeaways but stay high. They need a deal more.",
    "advantageous": "You have leverage. Use it, but don't waste it on small moves. Save ultimatums for key items.",
    "parity": "Both have leverage. Collaborative approach works. Fair splits appeal to both. Look for trades.",
    "disadvantaged": "You need this deal. Separate your BATNA (know it cold) from your aspirations. Don't show desperation.",
}


class GameTheoryModule:
    """
    Game-theoretic analysis of strategic interactions in negotiation.
    Detects which game archetype you're playing, identifies strategic positions,
    assesses BATNA and ZOPA, and coaches for cooperative vs. competitive play.
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

    # -- Game detection -------------------------------------------

    _GAME_KEYS = (
        "prisoners_dilemma", "zero_sum", "coordination_game", "battle_of_sexes"
    )

    def detect_game_archetype(self, text: str) -> Dict:
        """Detect which game structure the negotiation resembles."""
        hits = self._scan(text, "games")
        counts = {k: 0 for k in self._GAME_KEYS}
        raw_matches = {k: [] for k in self._GAME_KEYS}

        for h in hits:
            counts[h["category"]] += 1
            raw_matches[h["category"]].append(h["keyword"])

        total = sum(counts.values())
        if total == 0:
            primary_finding = "coordination_game"  # assume cooperation-friendly by default
            scores = {k: 0.0 for k in self._GAME_KEYS}
        else:
            primary_finding = max(counts, key=counts.get)
            scores = {k: round(v / total, 3) for k, v in counts.items()}

        return {
            "primary_finding": primary_finding,
            "scores": scores,
            "raw_matches": raw_matches,
            "analysis_text": _GAME_PROFILE[primary_finding][0],
            "coaching_guidance": _GAME_DYNAMICS[primary_finding],
        }

    # -- Strategic position assessment ----------------------------

    def assess_strategic_position(self, text: str) -> Dict:
        """Assess your strategic position: dominant, advantageous, parity, disadvantaged."""
        hits = self._scan(text, "strategic_positions")

        positions_count = {"dominant": 0, "advantageous": 0, "parity": 0, "disadvantaged": 0}
        for h in hits:
            positions_count[h["category"]] += 1

        dominant_count = positions_count["dominant"]
        advantageous_count = positions_count["advantageous"]
        parity_count = positions_count["parity"]
        disadvantaged_count = positions_count["disadvantaged"]

        positions = {
            "dominant": dominant_count,
            "advantageous": advantageous_count,
            "parity": parity_count,
            "disadvantaged": disadvantaged_count,
        }

        primary_finding = max(positions, key=positions.get) if max(positions.values()) > 0 else "parity"

        return {
            "primary_finding": primary_finding,
            "position_scores": positions,
            "coaching_guidance": _STRATEGIC_POSITION_GUIDANCE[primary_finding],
        }

    # -- BATNA & ZOPA -----------------------------------------------

    def identify_batna_and_zopa(self, text: str) -> Dict:
        """Identify BATNA (your walk-away point) and ZOPA (zone of possible agreement)."""
        batna_hits = find_all(text, {"batna": EN["batna"]}, lang="en", first_phrase_only=False)
        zopa_hits = find_all(text, {"zopa": EN["zopa"]}, lang="en", first_phrase_only=False)

        ro_batna = find_all(text, {"batna": RO["batna"]}, lang="ro", first_phrase_only=False)
        ro_zopa = find_all(text, {"zopa": RO["zopa"]}, lang="ro", first_phrase_only=False)

        return {
            "raw_matches_batna": [h["keyword"] for h in batna_hits + ro_batna],
            "batna_count": len(set((h["keyword"] for h in batna_hits + ro_batna))),
            "raw_matches_zopa": [h["keyword"] for h in zopa_hits + ro_zopa],
            "zopa_count": len(set((h["keyword"] for h in zopa_hits + ro_zopa))),
            "batna_clarity": "clear" if len(set((h["keyword"] for h in batna_hits + ro_batna))) > 0 else "unclear",
            "zopa_clarity": "exists" if len(set((h["keyword"] for h in zopa_hits + ro_zopa))) > 0 else "undefined",
        }

    # -- Full analysis -----------------------------------------------

    def analyze(self, text: str) -> Dict:
        """Full game-theoretic analysis: game type, position, BATNA, ZOPA."""
        return {
            "game_archetype": self.detect_game_archetype(text),
            "strategic_position": self.assess_strategic_position(text),
            "batna_zopa": self.identify_batna_and_zopa(text),
        }

    def dual_speaker_game_analysis(self, your_text: str, their_text: str) -> Dict:
        """Analyze the game structure from both players' perspectives."""
        your_game = self.detect_game_archetype(your_text)
        their_game = self.detect_game_archetype(their_text)
        your_position = self.assess_strategic_position(your_text)
        their_position = self.assess_strategic_position(their_text)

        return {
            "your_game": your_game,
            "their_game": their_game,
            "your_position": your_position,
            "their_position": their_position,
            "coaching": self._dual_game_coaching(your_game, their_game, your_position, their_position),
        }

    @staticmethod
    def _dual_game_coaching(your_game: Dict, their_game: Dict, your_pos: Dict, their_pos: Dict) -> str:
        your_archetype = your_game["game_archetype"]
        their_archetype = their_game["game_archetype"]
        your_position = your_pos["strategic_position"]
        their_position = their_pos["strategic_position"]

        coaching = "DUAL-SPEAKER GAME ANALYSIS\n\n"
        coaching += f"YOU: perceive a {your_archetype.replace('_', ' ').title()} game\n"
        coaching += f"     your strategic position: {your_position.upper()}\n\n"
        coaching += f"THEM: perceive a {their_archetype.replace('_', ' ').title()} game\n"
        coaching += f"      their strategic position: {their_position.upper()}\n\n"

        if your_archetype == their_archetype:
            coaching += f"ALIGNMENT: you agree on game type ({your_archetype.replace('_', ' ').title()}).\n"
        else:
            coaching += f"MISMATCH: you see {your_archetype.replace('_', ' ')} but they see {their_archetype.replace('_', ' ')}.\n"
            coaching += "This shapes how you each approach negotiation. Name it.\n\n"

        coaching += (
            "KEY MOVES:\n"
            "1. Identify the game: If it's a Prisoner's Dilemma, build trust. If zero-sum, anchor high.\n"
            "2. Know your BATNA: your walk-away point anchors your aspiration.\n"
            "3. Estimate their BATNA: how badly do they need a deal?\n"
            "4. Find the ZOPA: overlap where both could accept.\n"
            "5. If both in Coordination or Battle of Sexes: cooperate. If zero-sum: compete hard.\n"
        )
        return coaching

    def prescribe_game_aware_strategy(self, game_type: str = "coordination_game") -> str:
        """Coaching for playing the game strategically."""
        coaching = f"STRATEGIC PLAY: {game_type.replace('_', ' ').title()}\n\n"

        if game_type == "prisoners_dilemma":
            coaching += (
                "1. RECOGNIZE: mutual cooperation beats mutual defection, but defection tempts both.\n"
                "2. BUILD TRUST: start cooperative; escalate only if they defect.\n"
                "3. USE TIT-FOR-TAT: mirror their play. Cooperate until they don't.\n"
                "4. ENABLE VERIFICATION: make it easy to verify they cooperated.\n"
                "5. COMMUNICATE: explicit commitment to cooperation reduces fear.\n\n"
                "GOAL: Reach the cooperative equilibrium."
            )
        elif game_type == "zero_sum":
            coaching += (
                "1. RECOGNIZE: no mutual gain. It's about who captures how much value.\n"
                "2. ANCHOR FIRST: set the psychological baseline with a number you can defend.\n"
                "3. MAXIMIZE YOUR GAIN: assume they're doing the same.\n"
                "4. KNOW YOUR ZOPA: below which you walk away.\n"
                "5. COMPETE HARD: civilly, but without apology.\n\n"
                "GOAL: Capture the most value you can extract."
            )
        elif game_type == "coordination_game":
            coaching += (
                "1. RECOGNIZE: both benefit from coordinating. The challenge is *how*.\n"
                "2. SIGNAL: make your preference clear and credible.\n"
                "3. LISTEN: understand their preference and constraints.\n"
                "4. FIND FOCAL POINTS: solutions that feel natural/fair to both.\n"
                "5. BREAK TIES: if preferences are equal, pick by fairness, convention, or luck.\n\n"
                "GOAL: Coordinate on a mutually beneficial outcome."
            )
        elif game_type == "battle_of_sexes":
            coaching += (
                "1. RECOGNIZE: you disagree on preferred outcome but both prefer agreement to deadlock.\n"
                "2. SEPARATE PREFERENCE FROM DEAL: neither outcome is *that* much better.\n"
                "3. SEARCH FOR COMPROMISE: can you find something better than either alone?\n"
                "4. PROPOSE ALTERNATION: 'You get A this time, I get B next time.'\n"
                "5. REFRAME: 'We both win if we cooperate on *how* to handle the disagreement.'\n\n"
                "GOAL: Agreement that honors both preferences."
            )

        return coaching
