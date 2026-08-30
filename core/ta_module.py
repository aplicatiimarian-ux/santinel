# -*- coding: utf-8 -*-
"""
TA (Transactional Analysis) Module for SANTINEL
Analyzes ego states, life positions and psychological games in negotiations.

Bilingual (EN + RO):
  - Functional ego states: Critical/Nurturing Parent, Adult, Free/Adapted Child
  - Life positions: the I'm OK / You're OK matrix (4 quadrants)
  - 5 sales games: Hard to Get, Rapo, Kick Me, Yes But, Wooden Leg

Romanian triggers live in core/ta_keywords_ro.py; the English set is `EN`
below. Tokenization, diacritic folding and Snowball stemming are shared with
the other frameworks via core/text_norm.py.
"""

from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.text_norm import find_all
    from core.ta_keywords_ro import RO
except ImportError:  # imported flat (core/ dir on path, e.g. backend/feedback_database.py)
    from text_norm import find_all
    from ta_keywords_ro import RO

__all__ = ["EgoState", "LifePosition", "TAGame", "TAModule"]


class EgoState(Enum):
    PARENT = "parent"
    ADULT = "adult"
    CHILD = "child"


class LifePosition(Enum):
    I_OK_YOU_OK = "i_ok_you_ok"
    I_OK_YOU_NOT_OK = "i_ok_you_not_ok"
    I_NOT_OK_YOU_OK = "i_not_ok_you_ok"
    I_NOT_OK_YOU_NOT_OK = "i_not_ok_you_not_ok"


class TAGame(Enum):
    """The 5 games SANTINEL watches for in sales / negotiation talk."""
    HARD_TO_GET = "hard_to_get"
    RAPO = "rapo"
    KICK_ME = "kick_me"
    YES_BUT = "yes_but"
    WOODEN_LEG = "wooden_leg"


# English lexicon — same shape as core/ta_keywords_ro.RO
EN = {
    "ego_states": {
        "critical_parent": [
            "you should have", "you must", "that's wrong", "unacceptable",
            "how many times", "that's ridiculous", "you people always",
            "how could you", "frankly amateur",
        ],
        "nurturing_parent": [
            "let me help you", "don't worry", "i'll take care of it",
            "you're in good hands", "poor thing", "there there", "leave it to me",
        ],
        "adult": [
            "the data shows", "let's consider the options", "what are the facts",
            "logically", "let's weigh", "based on the numbers", "what's the real cost",
            "let's look at the evidence",
        ],
        "free_child": [
            "i love this", "awesome", "can't wait", "this is so cool",
            "let's try something new", "so much fun", "wow",
        ],
        "adapted_child": [
            "sorry to bother", "whatever you say", "i guess so", "if you say so",
            "i'm sorry", "it's not fair to me", "my opinion doesn't matter anyway",
        ],
    },
    "life_positions": {
        "i_ok_you_ok": [
            "win-win", "mutual respect", "we both gain", "let's find it together",
            "both of us", "a good solution for both",
        ],
        "i_ok_you_not_ok": [
            "you're wrong", "i'm right", "they don't get it", "they're amateurs",
            "i know how this works", "they're not on our level", "i'm ahead of them",
        ],
        "i_not_ok_you_ok": [
            "i'm probably wrong", "you know better", "i can't compete with you",
            "it must be my fault", "i'm not on your level", "sorry to take your time",
        ],
        "i_not_ok_you_not_ok": [
            "this is hopeless", "there's no point", "we all lose", "it'll turn out bad anyway",
            "nobody wins here", "everyone loses",
        ],
    },
    "games": {
        "hard_to_get": [
            "i'm not sure we need this", "no rush on our side", "we have other options",
            "maybe another time", "we'll see", "this isn't a priority", "i won't push it",
        ],
        "rapo": [
            "i was really interested but", "you seemed perfect until", "don't get the wrong idea",
            "we led you on for nothing", "i thought it worked, but now it doesn't",
        ],
        "kick_me": [
            "you'll probably say no anyway", "i know this is a bad time",
            "i'm terrible at this", "i always mess up the pricing",
            "i'll probably blow this too", "there i go saying something dumb",
        ],
        "yes_but": [
            "yes but that won't work", "i've already tried that", "yes, however the budget",
            "yes but we don't have time", "sounds good, but it can't be done",
        ],
        "wooden_leg": [
            "what do you expect from a small team", "i can't because of the system",
            "it's not my fault, the process", "what can i do if that's the policy",
            "there's only me here",
        ],
    },
}

_EGO_ANALYSIS = {
    "critical_parent": "Critical Parent: judging, controlling. Softens rapport; move to Adult.",
    "nurturing_parent": "Nurturing Parent: helpful but can patronize. Useful in small doses.",
    "adult": "Adult: facts, logic, options. Best state for negotiating.",
    "free_child": "Free Child: spontaneous, enthusiastic. Good for rapport, weak for terms.",
    "adapted_child": "Adapted Child: compliant or sulky. Concedes too fast; re-ground in Adult.",
}

_POSITION_LABEL = {
    "i_ok_you_ok": "I'm OK / You're OK — healthy, collaborative",
    "i_ok_you_not_ok": "I'm OK / You're not OK — one-up, dismissive",
    "i_not_ok_you_ok": "I'm not OK / You're OK — one-down, deferential",
    "i_not_ok_you_not_ok": "I'm not OK / You're not OK — futile, disengaged",
}

_POSITION_GUIDANCE = {
    "i_ok_you_ok": "Protect this. Keep language on shared value and concrete next steps.",
    "i_ok_you_not_ok": "Drop the contempt — it invites resistance. Grant the other side legitimacy.",
    "i_not_ok_you_ok": "Stop deferring. State your value and your walk-away plainly.",
    "i_not_ok_you_not_ok": "Break the fatalism. Name one small improvement that is in reach.",
}

_GAME_INFO = {
    "hard_to_get": (
        "Hard to Get",
        "Feigned indifference / scarcity of interest to pull the other party in.",
        "Stay in control of the frame and set a real deadline; don't chase.",
        "Gains leverage by making the other side work for engagement.",
    ),
    "rapo": (
        "Rapo",
        "Encouragement followed by an abrupt rebuff.",
        "Name the switch calmly and return to explicit, written terms.",
        "Feels powerful, then aggrieved; keeps the other side off balance.",
    ),
    "kick_me": (
        "Kick Me",
        "Self-deprecation that invites the other side to criticize or reject.",
        "Decline the invitation to pile on; redirect to the actual decision.",
        "Confirms a 'nobody backs me' script and offloads responsibility.",
    ),
    "yes_but": (
        "Yes But",
        "Asks for options, then blocks every one of them.",
        "Stop supplying answers; hand the problem back: 'What would work for you?'",
        "Proves the adviser inadequate and avoids committing.",
    ),
    "wooden_leg": (
        "Wooden Leg",
        "Uses a limitation as a standing excuse to dodge responsibility.",
        "Acknowledge the constraint, then ask what is possible within it.",
        "Avoids accountability by pointing at the handicap.",
    ),
}


class TAModule:
    """
    Transactional Analysis coaching engine.
    Detects the ego state a person is speaking from, their life position, and
    whether they are running one of the 5 sales games. Call analyze() for the
    full pass, or an individual method for one domain.
    """

    def _scan(self, text: str, domain: str, unique: bool = False) -> List[Dict]:
        en = find_all(text, EN[domain], lang="en", first_phrase_only=not unique)
        ro = find_all(text, RO[domain], lang="ro", first_phrase_only=not unique)
        seen = set()
        out = []
        for hit in en + ro:
            sig = (hit["category"], hit["keyword"])
            if sig in seen:
                continue
            seen.add(sig)
            out.append(hit)
        return out

    # -- Ego states ---------------------------------------------------

    _EGO_KEYS = ("critical_parent", "nurturing_parent", "adult",
                 "free_child", "adapted_child")

    def detect_ego_state(self, text: str) -> Dict:
        hits = self._scan(text, "ego_states")
        counts = {k: 0 for k in self._EGO_KEYS}
        matched = {k: [] for k in self._EGO_KEYS}
        for h in hits:
            counts[h["category"]] += 1
            matched[h["category"]].append(h["keyword"])
        total = sum(counts.values())
        if total == 0:
            primary = "adult"
            scores = {k: 0.0 for k in self._EGO_KEYS}
        else:
            primary = max(counts, key=counts.get)
            scores = {k: round(v / total, 3) for k, v in counts.items()}
        return {
            "primary_ego_state": primary,
            "scores": scores,
            "matched": matched,
            "analysis": self._ego_state_analysis(primary),
        }

    @staticmethod
    def _ego_state_analysis(state: str) -> str:
        return _EGO_ANALYSIS.get(state, "Mixed ego state detected")

    # -- Life positions --------------------------------------------

    _POSITION_PRIORITY = ("i_not_ok_you_not_ok", "i_ok_you_not_ok",
                          "i_not_ok_you_ok", "i_ok_you_ok")

    def analyze_life_position(self, text: str) -> Dict:
        hits = self._scan(text, "life_positions")
        present = {h["category"]: h for h in hits}
        for pos in self._POSITION_PRIORITY:
            if pos in present:
                position = pos
                break
        else:
            position = "i_ok_you_ok"  # default assumption
        return {
            "life_position": position,
            "label": _POSITION_LABEL[position],
            "positions_present": list(present),
            "matched": [present[p]["keyword"] for p in present],
            "assumed_default": not present,
            "guidance": _POSITION_GUIDANCE[position],
        }

    def detect_life_position(self, text: str, emotion: str = "") -> LifePosition:
        """Backward-compatible: returns the LifePosition enum member."""
        return LifePosition(self.analyze_life_position(text)["life_position"])

    # -- Games ------------------------------------------------

    def detect_psychological_game(self, text: str) -> Dict:
        hits = self._scan(text, "games", unique=True)
        by_game: Dict[str, Dict] = {}
        for h in hits:
            info = _GAME_INFO[h["category"]]
            entry = by_game.setdefault(h["category"], {
                "game": h["category"],
                "name": info[0],
                "description": info[1],
                "exit": info[2],
                "payoff": info[3],
                "matched_keywords": [],
                "language": h["language"],
            })
            entry["matched_keywords"].append(h["keyword"])
        games = list(by_game.values())
        return {
            "games_detected": games,
            "coaching": self._game_coaching(games) if games
            else "No psychological games detected.",
        }

    @staticmethod
    def _game_coaching(games: List[Dict]) -> str:
        g = games[0]
        return (
            f"GAME DETECTED: {g['name']}\n"
            f"  Pattern: {g['description']}\n"
            f"  Payoff:  {g['payoff']}\n"
            f"  Exit:    {g['exit']}\n"
            "  Then: return to Adult, state needs honestly, propose an "
            "Adult-to-Adult transaction."
        )

    # -- Umbrella + prescription -----------------------------

    def analyze(self, text: str) -> Dict:
        return {
            "ego_states": self.detect_ego_state(text),
            "life_position": self.analyze_life_position(text),
            "games": self.detect_psychological_game(text),
        }

    def prescribe_healthy_transaction(self, situation: str = "") -> str:
        return (
            "HEALTHY TRANSACTION — Adult-to-Adult from I'm OK / You're OK\n\n"
            "EGO STATE: move to Adult — facts, logic, problem-solving; own your "
            "position; respect the other side's needs.\n\n"
            "LIFE POSITION: I'm OK / You're OK — I have value to offer, you have "
            "legitimate needs, mutual value is possible.\n\n"
            "LANGUAGE SHIFT:\n"
            "  FROM: \"You're being unreasonable\"\n"
            "  TO:   \"Here's what makes sense for both of us\"\n\n"
            "MOVES: ask genuine questions about their needs; acknowledge real "
            "constraints; propose solutions honoring both parties; keep it "
            "direct and honest."
        )
