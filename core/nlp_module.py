# -*- coding: utf-8 -*-
"""
NLP (Neuro-Linguistic Programming) Module for SANTINEL
Analyzes language patterns for real-time negotiation coaching.

Covers 7 NLP domains, bilingual (EN + RO):
  1. Representation systems (VAK)   4. Pacing and leading   7. Submodalities
  2. Anchoring                      5. Milton language
  3. Modeling                       6. Reframing

Romanian triggers live in core/nlp_keywords_ro.py; the English set is `EN`
below. Diacritic folding, Snowball stemming and tokenization are shared with
the other frameworks via core/text_norm.py.
"""

from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.text_norm import find_all, merge_by_category
    from core.nlp_keywords_ro import RO
except ImportError:  # imported flat (core/ dir on path, e.g. backend/feedback_database.py)
    from text_norm import find_all, merge_by_category
    from nlp_keywords_ro import RO

__all__ = [
    "NLPRepresentationSystem", "NLPAnchor", "NLPModule",
]


class NLPRepresentationSystem(Enum):
    """Primary sensory representational systems in NLP"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"


class NLPAnchor(Enum):
    """Emotional anchors and states"""
    RESOURCEFUL = "resourceful"
    ANXIOUS = "anxious"
    ASSERTIVE = "assertive"
    COLLABORATIVE = "collaborative"
    DEFENSIVE = "defensive"


# English lexicon — same shape as core/nlp_keywords_ro.RO
EN = {
    "representation_systems": {
        "visual": [
            "see", "look", "picture", "imagine", "watch", "view", "bright",
            "dark", "clear", "fuzzy", "visualize", "show", "focus", "perspective",
            "big picture", "appears",
        ],
        "auditory": [
            "hear", "listen", "sound", "say", "tell", "voice", "loud", "quiet",
            "tone", "harmony", "ring", "silent", "resonate", "in tune", "we talk",
            "echo",
        ],
        "kinesthetic": [
            "feel", "touch", "sense", "grasp", "handle", "experience", "warm",
            "cold", "smooth", "rough", "pressure", "contact", "solid", "tension",
            "comfortable", "get a grip",
        ],
    },
    "anchoring": {
        "state_resourceful": [
            "confident", "ready", "calm", "in control", "focused", "determined",
            "grounded",
        ],
        "state_anxious": [
            "anxious", "tense", "worried", "unsure", "panicked", "stressed",
            "afraid",
        ],
        "state_assertive": [
            "firm", "direct", "i state clearly", "assertive", "i hold my position",
        ],
        "state_defensive": [
            "defensive", "closed off", "guarded", "on the defensive", "suspicious",
            "wary",
        ],
        "anchor_reference": [
            "last time", "the time i", "when i succeeded", "i remember when",
            "just like when", "in the past i", "i've been through this",
        ],
    },
    "modeling": {
        "exemplar_reference": [
            "the best negotiator", "my mentor", "how would", "what would a pro do",
            "a professional would", "my role model", "i learn from",
            "someone experienced would",
        ],
        "admiration": [
            "i admire", "inspires me", "i wish i were like", "does this perfectly",
            "always pulls it off",
        ],
    },
    "pacing_and_leading": {
        "pacing_marker": [
            "yes and", "i understand", "makes sense", "i agree", "exactly",
            "i see what you mean", "i appreciate your point", "fair point",
        ],
        "resistance_marker": [
            "but", "however", "i disagree", "i don't think", "still", "no way",
            "not really",
        ],
        "lead_marker": [
            "let's", "i propose", "how about we", "we can", "the next step",
            "let's move to", "i'd suggest",
        ],
    },
    "milton_language": {
        "mind_read": [
            "you're probably wondering", "you may be wondering", "i know how you feel",
            "you realize that", "you're thinking",
        ],
        "lost_performative": [
            "it's good to", "it's important to", "it's natural to", "it's known that",
            "it's clear that",
        ],
        "cause_effect": [
            "because", "which means that", "as you", "the more you", "that's why",
        ],
        "presupposition": [
            "when you decide", "after you choose", "before you sign",
            "as soon as you start", "how quickly you'll notice",
        ],
        "universal_quantifier": [
            "always", "never", "everyone", "everybody", "nobody", "every time",
        ],
        "tag_question": [
            "isn't it", "don't you", "aren't they", "wouldn't you say",
        ],
        "embedded_command": [
            "you can begin to notice", "you might consider", "imagine for a moment",
            "you start to feel", "you may find",
        ],
    },
    "reframing": {
        "frame_conflict": [
            "fight", "battle", "war", "enemy", "attack", "beat them", "the other side",
        ],
        "frame_obstacle": [
            "blocked", "stuck", "barrier", "impossible", "dead end", "no way out",
            "spinning our wheels",
        ],
        "frame_scarcity": [
            "not enough", "too little", "we lose", "limited resources", "zero sum",
            "us or them",
        ],
        "frame_blame": [
            "it's their fault", "because of them", "they're the problem", "only them",
        ],
        "frame_opportunity": [
            "opportunity", "reach an agreement", "shared value", "win-win",
            "find a solution", "benefit for both",
        ],
    },
    "submodalities": {
        "visual_brightness": ["bright", "vivid", "dark", "dim", "washed out"],
        "visual_size": ["huge", "massive", "small", "tiny", "enormous"],
        "visual_distance": ["close", "near", "far away", "in the distance"],
        "visual_focus": ["sharp", "in focus", "blurry", "out of focus", "hazy"],
        "auditory_volume": ["loud", "deafening", "quiet", "a whisper", "barely audible"],
        "auditory_tempo": ["fast", "rapid", "slow", "dragging"],
        "kinesthetic_weight": ["heavy", "crushing", "light", "weightless"],
        "kinesthetic_temperature": ["hot", "warm", "cold", "freezing"],
        "kinesthetic_tension": ["tense", "tight", "relaxed", "loose"],
    },
}

_MODALITY_OF = {
    "visual_brightness": "visual", "visual_size": "visual",
    "visual_distance": "visual", "visual_focus": "visual",
    "auditory_volume": "auditory", "auditory_tempo": "auditory",
    "kinesthetic_weight": "kinesthetic", "kinesthetic_temperature": "kinesthetic",
    "kinesthetic_tension": "kinesthetic",
}

_LEGACY_FRAME = {
    "frame_conflict": "conflict",
    "frame_obstacle": "obstacle",
    "frame_opportunity": "negotiation",
}


class NLPModule:
    """
    NLP Coaching Engine.
    Runs 7 bilingual pattern analyzers over negotiation language and returns
    structured coaching cues. Call analyze() for the full pass, or an
    individual analyze_*() method for one domain.
    """

    # -- shared scan ----------------------------------------------------

    def _scan(self, text: str, domain: str, first_phrase_only: bool = True) -> List[Dict]:
        """EN + RO hits for one domain.

        With `first_phrase_only` (default) at most one hit per category, EN
        before RO. Otherwise every distinct (category, keyword) hit — the same
        lexicon entry appearing in both languages (e.g. "solid") is not
        double-counted.
        """
        en = find_all(text, EN[domain], lang="en", first_phrase_only=first_phrase_only)
        ro = find_all(text, RO[domain], lang="ro", first_phrase_only=first_phrase_only)
        if first_phrase_only:
            return merge_by_category(en, ro)
        seen = set()
        out = []
        for hit in en + ro:
            sig = (hit["category"], hit["keyword"])
            if sig not in seen:
                seen.add(sig)
                out.append(hit)
        return out

    # -- 1. Representation systems (VAK) ------------------------------

    def analyze_representation_system(self, text: str) -> Dict:
        hits = self._scan(text, "representation_systems", first_phrase_only=False)
        counts = {"visual": 0, "auditory": 0, "kinesthetic": 0}
        matched: Dict[str, List[str]] = {"visual": [], "auditory": [], "kinesthetic": []}
        for h in hits:
            counts[h["category"]] += 1
            matched[h["category"]].append(h["keyword"])
        total = sum(counts.values())
        if total == 0:
            primary = "kinesthetic"
            scores = {"visual": 0.0, "auditory": 0.0, "kinesthetic": 0.5}
        else:
            primary = max(counts, key=counts.get)
            scores = {k: round(v / total, 3) for k, v in counts.items()}
        return {
            "primary_system": primary,
            "scores": scores,
            "matched": matched,
            "recommendation": self._get_system_recommendation(primary),
        }

    def _get_system_recommendation(self, system: str) -> str:
        return {
            "visual": "Use visual metaphors, show the bigger picture, help them 'see' the value",
            "auditory": "Use auditory metaphors, listen actively, get their 'voice' heard",
            "kinesthetic": "Use tactile metaphors, acknowledge feelings, help them 'feel' the agreement",
        }.get(system, "")

    # backward-compatible name (used by backend/feedback_database.py)
    def detect_representation_system(self, text: str) -> Dict:
        return self.analyze_representation_system(text)

    # -- 2. Anchoring ------------------------------------------------

    def analyze_anchoring(self, text: str) -> Dict:
        hits = self._scan(text, "anchoring")
        by_cat = {h["category"]: h for h in hits}
        states = [c.replace("state_", "") for c in by_cat if c.startswith("state_")]
        has_ref = "anchor_reference" in by_cat
        negative = any(s in ("anxious", "defensive") for s in states)
        if has_ref:
            guidance = ("Reference to a past resourceful memory detected — fire that "
                        "anchor now: relive it in full sensory detail before re-engaging.")
        elif negative:
            guidance = ("Unresourceful state language. Break state, then set an anchor "
                        "from a past win (posture + a cue word) and step into it.")
        else:
            guidance = "Establish a resourceful anchor pre-call so it is ready to fire under pressure."
        return {
            "current_states": states,
            "has_anchor_reference": has_ref,
            "anchor_cues": [by_cat[c]["keyword"] for c in by_cat if c == "anchor_reference"],
            "suggested_anchor": "resourceful" if negative or not states else states[0],
            "guidance": guidance,
        }

    # -- 3. Modeling ----------------------------------------------

    def analyze_modeling(self, text: str) -> Dict:
        hits = self._scan(text, "modeling")
        cats = [h["category"] for h in hits]
        return {
            "modeling_cues": [h["keyword"] for h in hits],
            "is_modeling": bool(hits),
            "prompt": (
                "Model the exemplar explicitly: what do they SEE, HEAR and FEEL "
                "in this spot, and what is their first move? Then borrow that."
                if hits else
                "No modeling in play. Pick a negotiator you rate and ask how they'd open this."
            ),
            "exemplar_brief": self.model_excellence(text) if hits else "",
            "categories": cats,
        }

    # -- 4. Pacing and leading ----------------------------------

    def analyze_pacing_leading(self, text: str) -> Dict:
        hits = self._scan(text, "pacing_and_leading", first_phrase_only=False)
        pacing = [h["keyword"] for h in hits if h["category"] == "pacing_marker"]
        resistance = [h["keyword"] for h in hits if h["category"] == "resistance_marker"]
        lead = [h["keyword"] for h in hits if h["category"] == "lead_marker"]
        if resistance and not pacing:
            stance = "mismatched"
            guidance = ("Rapport break: you're leading before pacing. Acknowledge their "
                        "position in their words first, then introduce your move.")
        elif pacing and lead:
            stance = "pacing_then_leading"
            guidance = "Good sequence — pace acknowledged, now lead. Keep 2-3 paces per lead."
        elif pacing:
            stance = "pacing"
            guidance = "Rapport is building. Add a lead: propose the next small step."
        elif lead:
            stance = "leading"
            guidance = "You're leading without visible pacing. Mirror their language before pushing on."
        else:
            stance = "neutral"
            guidance = "No rapport markers yet. Open by pacing observable facts and their stated goal."
        return {
            "stance": stance,
            "pacing_markers": pacing,
            "resistance_markers": resistance,
            "lead_markers": lead,
            "guidance": guidance,
        }

    # -- 5. Milton language ------------------------------------

    def analyze_milton_language(self, text: str) -> Dict:
        hits = self._scan(text, "milton_language", first_phrase_only=False)
        patterns = [
            {"pattern": h["category"], "keyword": h["keyword"], "language": h["language"]}
            for h in hits
        ]
        names = sorted({h["category"] for h in hits})
        return {
            "patterns_detected": patterns,
            "pattern_types": names,
            "count": len(patterns),
            "note": (
                f"{len(names)} Milton-Model pattern type(s) present: {', '.join(names)}. "
                "Artfully vague language paces the other party's experience — use "
                "sparingly and ethically to keep options open."
                if names else
                "No Milton-Model language detected. Current phrasing is specific/literal."
            ),
        }

    # -- 6. Reframing ----------------------------------------

    def analyze_reframing(self, text: str) -> Dict:
        hits = self._scan(text, "reframing")
        by_cat = {h["category"]: h for h in hits}
        # priority order when several frames co-occur
        for frame in ("frame_conflict", "frame_obstacle", "frame_scarcity",
                      "frame_blame", "frame_opportunity"):
            if frame in by_cat:
                current = frame
                break
        else:
            current = "unframed"
        context, meaning = self._reframes(current)
        return {
            "current_frame": current.replace("frame_", ""),
            "frames_present": [c.replace("frame_", "") for c in by_cat],
            "context_reframe": context,
            "meaning_reframe": meaning,
        }

    @staticmethod
    def _reframes(frame: str):
        table = {
            "frame_conflict": (
                "Same facts, different context: this is a joint problem-solving session, "
                "not a fight. \"We're on the same side of the table, facing the problem.\"",
                "Their pushback doesn't mean hostility — it means the issue matters to them "
                "enough to argue about. Engagement is information.",
            ),
            "frame_obstacle": (
                "The block is a spec, not a wall: it tells you the exact constraint any "
                "deal must satisfy. \"Given this, what options fit?\"",
                "\"Impossible\" usually means \"impossible the way I first framed it\". "
                "It's a prompt to change the approach, not to quit.",
            ),
            "frame_scarcity": (
                "Move from dividing a fixed pie to expanding it: which interests differ and "
                "can be traded? \"What's cheap for us and valuable to them?\"",
                "Limited on one axis is not limited on all. Scarcity of price can be "
                "abundance of terms, timing, or scope.",
            ),
            "frame_blame": (
                "Shift from who caused it to what now: \"Regardless of how we got here, "
                "what's the smallest step that improves it?\"",
                "Blame is a backward-facing filter. The same energy aimed forward becomes "
                "a corrective plan.",
            ),
            "frame_opportunity": (
                "Frame is already constructive — protect it: keep language on shared value "
                "and concrete next steps.",
                "You're reading this as a chance to create value. That expectation shapes "
                "the other party's response.",
            ),
        }
        return table.get(frame, (
            "No dominant frame yet. Name the situation as a negotiation over mutual value.",
            "How you label this in the first minute sets the tone — choose 'problem to "
            "solve together'.",
        ))

    # backward-compatible names
    def detect_problem_frame(self, text: str) -> str:
        current = self.analyze_reframing(text)["current_frame"]
        return _LEGACY_FRAME.get("frame_" + current, "other")

    def generate_nlp_reframe(self, situation: str, current_frame: str, emotion: str = "") -> str:
        reframes = {
            "conflict": (
                "\U0001f504 NLP REFRAME: From Conflict to Collaborative Problem-Solving\n"
                "   CURRENT: \"We're in a battle\"\n"
                "   REFRAME: \"We're partners solving a puzzle together\"\n"
                "   ACTION: Shift language from \"win/lose\" to \"mutual value\""
            ),
            "obstacle": (
                "\U0001f504 NLP REFRAME: From Obstacle to Opportunity\n"
                "   CURRENT: \"This is impossible / blocking us\"\n"
                "   REFRAME: \"This is a constraint that clarifies what we need\"\n"
                "   ACTION: Find creative solutions within constraints"
            ),
            "negotiation": (
                "\U0001f504 NLP REFRAME: Anchor Resourceful State\n"
                "   CURRENT: \"I need to get the best deal\"\n"
                "   REFRAME: \"I create mutual value and clear agreements\"\n"
                "   ACTION: Lead from capability, not desperation"
            ),
        }
        return reframes.get(current_frame, "Recognize this is a negotiation. Focus on mutual value.")

    # -- 7. Submodalities ----------------------------------

    def analyze_submodalities(self, text: str) -> Dict:
        hits = self._scan(text, "submodalities", first_phrase_only=False)
        detected = []
        modalities = set()
        for h in hits:
            modality = _MODALITY_OF.get(h["category"], "")
            modalities.add(modality)
            detected.append({
                "modality": modality,
                "submodality": h["category"].split("_", 1)[1],
                "keyword": h["keyword"],
                "language": h["language"],
            })
        if detected:
            shift = (
                "Submodality shift: take the stressful representation and turn its dials "
                "down — shrink the picture, dim it, push it further away; drop the volume; "
                "make the body sensation lighter and cooler. Then amplify the same dials "
                "on the calm, resourceful representation."
            )
        else:
            shift = ("No submodality language yet. Ask how they picture the deal (size, "
                     "distance, brightness) to get material to work with.")
        return {
            "detected": detected,
            "modalities_present": sorted(m for m in modalities if m),
            "shift_suggestion": shift,
        }

    # -- Umbrella + legacy statics ------------------------

    def analyze(self, text: str) -> Dict:
        return {
            "representation_systems": self.analyze_representation_system(text),
            "anchoring": self.analyze_anchoring(text),
            "modeling": self.analyze_modeling(text),
            "pacing_and_leading": self.analyze_pacing_leading(text),
            "milton_language": self.analyze_milton_language(text),
            "reframing": self.analyze_reframing(text),
            "submodalities": self.analyze_submodalities(text),
        }

    def model_excellence(self, target_outcome: str = "") -> str:
        return (
            "✨ MODELING EXCELLENCE: How Expert Negotiators Approach This\n\n"
            "INTERNAL REPRESENTATION:\n"
            "   - They see the negotiation as problem-solving, not conflict\n"
            "   - They hear mutual respect and clear communication\n"
            "   - They feel grounded, confident, flexible\n\n"
            "ANCHORING STATES:\n"
            "   - RESOURCEFUL: \"I have options and value to offer\"\n"
            "   - ASSERTIVE: \"I can clearly state my needs and boundaries\"\n"
            "   - COLLABORATIVE: \"We can find solutions that work for both\"\n\n"
            "BEHAVIOR SEQUENCE:\n"
            "   1. Listen deeply to understand their needs (auditory)\n"
            "   2. Show how your solution fits their picture (visual)\n"
            "   3. Create comfort with the agreement (kinesthetic)\n\n"
            "POWER MOVE: Access your resourceful state first, then engage from that anchor."
        )

    def linguistic_pattern_analysis(self, statement: str) -> Dict:
        """
        Modal-operator balance: limiting language (can't/won't/must) vs
        possibility language (could/might/possible). English heuristic.
        """
        text = (statement or "").lower()
        limitations = {
            "can't": text.count("can't") + text.count("cannot"),
            "won't": text.count("won't"),
            "impossible": text.count("impossible"),
            "must": text.count("must"),
            "should": text.count("should"),
        }
        possibilities = {
            "can": max(0, text.count("can ") - limitations["can't"]),
            "will": max(0, text.count("will ") - limitations["won't"]),
            "could": text.count("could"),
            "might": text.count("might"),
            "possible": text.count("possible") - limitations["impossible"],
        }
        total_limiting = sum(limitations.values())
        total_possible = sum(max(0, v) for v in possibilities.values())
        return {
            "limiting_language_count": total_limiting,
            "possibility_language_count": total_possible,
            "modal_ratio": round(total_possible / (total_limiting + 1), 3),
            "coaching": self._language_coaching(total_limiting, total_possible),
        }

    @staticmethod
    def _language_coaching(limiting: int, possible: int) -> str:
        if limiting > possible:
            return "Shift from limiting language ('can't', 'must') to possibility language ('could', 'might')."
        if possible > limiting:
            return "You're using empowering language. Maintain this resourceful state."
        return "Mix of limiting and possibility language. Lean more toward 'could' and 'might'."
