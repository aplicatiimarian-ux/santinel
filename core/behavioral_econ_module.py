# -*- coding: utf-8 -*-
"""
Behavioral Economics Module for SANTINEL
Detects cognitive biases and decision-making traps in negotiations.

Bilingual (EN + RO):
  - 6 primary cognitive biases: loss aversion, anchoring, sunk cost fallacy,
    framing effect, status quo bias, availability heuristic
  - Bias detection via language cues (keywords, framing patterns)
  - Mitigation strategies tailored to each bias
  - Dual-speaker bias analysis (you vs. counterparty)

Behavioral economics (Kahneman, Tversky): predictable patterns in how people
decide under uncertainty. In negotiation, both parties are subject to these
biases; awareness allows you to recognize the trap and navigate around it.

Romanian triggers live in core/behavioral_econ_keywords_ro.py; the English set
is `EN` below. Tokenization, diacritic folding and Snowball stemming are shared
with other frameworks via core/text_norm.py.
"""

from enum import Enum
from typing import Dict, List

try:  # imported as package (repo root on path)
    from core.text_norm import find_all
    from core.behavioral_econ_keywords_ro import RO
except ImportError:  # imported flat (core/ dir on path)
    from text_norm import find_all
    from behavioral_econ_keywords_ro import RO

__all__ = ["CognitiveBias", "BehavioralEconomicsModule"]


class CognitiveBias(Enum):
    """The 6 primary cognitive biases in negotiation."""
    LOSS_AVERSION = "loss_aversion"
    ANCHORING = "anchoring"
    SUNK_COST_FALLACY = "sunk_cost_fallacy"
    FRAMING_EFFECT = "framing_effect"
    STATUS_QUO_BIAS = "status_quo_bias"
    AVAILABILITY_HEURISTIC = "availability_heuristic"


# English lexicon — same shape as core/behavioral_econ_keywords_ro.RO
EN = {
    "biases": {
        "loss_aversion": [
            "i can't afford to lose", "the risk is too high", "we'll lose money",
            "this is too risky", "i'm afraid of losing", "the downside is",
            "we might lose everything", "it's not worth the risk", "what if it fails",
            "the penalty is harsh", "i can't take that loss",
        ],
        "anchoring": [
            "the starting price is", "we need to start at", "my first offer is",
            "the number we're discussing is", "i'm anchoring on", "this is my baseline",
            "we established that", "the figure is fixed at", "we said", "the amount is",
            "that's the number", "my anchor", "the market rate is", "first number",
            "don't move from", "everything else is negotiation around",
        ],
        "sunk_cost_fallacy": [
            "we've already spent", "after all we've invested", "given what we've put in",
            "we can't waste what we've spent", "i've already committed", "we've been working on this",
            "think of all the time we've invested", "we've come too far to stop",
            "too much at stake now", "we can't throw away",
        ],
        "framing_effect": [
            "if we don't do this", "the alternative is worse", "the only choice is",
            "we have to", "we'll regret not", "it's either or", "the real issue is",
            "the problem is framed as", "if we lose this", "or we'll have to accept",
        ],
        "status_quo_bias": [
            "we've always done it this way", "it's worked so far", "why change",
            "the current arrangement is", "things are fine as they are", "don't fix what isn't broken",
            "we know how this works", "let's keep the status quo", "we're comfortable with",
            "change is risky", "leave it as is",
        ],
        "availability_heuristic": [
            "i remember when", "in recent cases", "the latest example", "based on what happened",
            "everyone knows that", "it's obvious from", "you can see it everywhere",
            "i've seen it happen", "the common pattern is", "similar situations show",
            "last time we", "those situations always", "it was a disaster", "all cases like that",
            "i recall", "remember the", "vivid example",
        ],
    },
}

_BIAS_PROFILE = {
    "loss_aversion": (
        "Loss Aversion: pain of loss > pleasure of gain. Makes people risk-averse.",
        "In negotiation: clings to current position; oversells downside; resists new proposals.",
        "Mitigation: reframe as 'what we gain' not 'what we lose'; use concrete gains.",
    ),
    "anchoring": (
        "Anchoring: first number disproportionately influences final outcome.",
        "In negotiation: whoever anchors first often wins. Anchors stick psychologically.",
        "Mitigation: anchor first with confidence; if anchored against, explicitly counter-anchor.",
    ),
    "sunk_cost_fallacy": (
        "Sunk Cost Fallacy: throwing good money after bad because of past investment.",
        "In negotiation: 'we've invested too much to stop'; justifies poor decisions by history.",
        "Mitigation: isolate past from future. Ask: 'Is this deal good if we ignore sunk cost?'",
    ),
    "framing_effect": (
        "Framing Effect: how options are presented (loss vs. gain) changes choice.",
        "In negotiation: 'you'll lose 10%' feels worse than 'you'll keep 90%', though identical.",
        "Mitigation: reframe the same terms in opposite direction; show multiple framings.",
    ),
    "status_quo_bias": (
        "Status Quo Bias: preference for current state over change, even if change is better.",
        "In negotiation: 'let's not rock the boat'; resists new terms even when beneficial.",
        "Mitigation: show cost of inaction; make change feel 'normal'; minimize disruption.",
    ),
    "availability_heuristic": (
        "Availability Heuristic: likelihood judged by how easily examples come to mind.",
        "In negotiation: recent failures loom large; fears are inflated; success is discounted.",
        "Mitigation: provide base rates, statistical evidence; counter vivid examples with data.",
    ),
}

_BIAS_DANGER = {
    "loss_aversion": "Risk paralysis: defensive posture, slow decisions, poor deal design.",
    "anchoring": "Outcome is largely set by first number. Whoever anchors wins.",
    "sunk_cost_fallacy": "Justifies throwing more resources at a bad deal to 'not waste' past investment.",
    "framing_effect": "Same deal rejected if framed as loss, accepted if framed as gain.",
    "status_quo_bias": "Beneficial change is rejected reflexively. Inertia dominates logic.",
    "availability_heuristic": "Overweighting vivid but rare scenarios; underweighting statistical reality.",
}

_BIAS_MITIGATION = {
    "loss_aversion": (
        "1. Acknowledge the fear: 'I hear the downside concerns.'\n"
        "2. Quantify vs. assume: 'Let's look at the actual numbers.'\n"
        "3. Reframe: 'What we gain' not 'what we risk.'\n"
        "4. Separate worst case from likely case.\n"
        "5. Propose safeguards to reduce real risk."
    ),
    "anchoring": (
        "1. ANCHOR FIRST if you can: set the psychological baseline.\n"
        "2. If anchored against: explicitly reject it. 'That number doesn't reflect reality.'\n"
        "3. Counter-anchor with confidence and data.\n"
        "4. Ignore the initial anchor; focus on market value and fundamentals.\n"
        "5. Propose a very different anchor to break the hold of the first one."
    ),
    "sunk_cost_fallacy": (
        "1. Isolate past from future: 'What's the decision if we ignore sunk costs?'\n"
        "2. Ask: 'Is this the best use of resources going forward?'\n"
        "3. Reframe: 'Past investment is irrelevant to future value.'\n"
        "4. Cut losses if the forward case is weak.\n"
        "5. Celebrate pivoting as wise, not wasteful."
    ),
    "framing_effect": (
        "1. Present the same deal in BOTH frames: loss and gain.\n"
        "2. 'You lose 10% OR you keep 90% — which framing is fairest?'\n"
        "3. Use neutral language: facts, percentages, not 'risk' or 'opportunity.'\n"
        "4. Make the frame explicit: 'I'm framing this as...'\n"
        "5. Let them propose the frame to increase buy-in."
    ),
    "status_quo_bias": (
        "1. Make change feel inevitable: 'The market is shifting; we must adapt.'\n"
        "2. Highlight cost of inaction: 'Staying put costs us X.'\n"
        "3. Minimize disruption: 'Small change, big benefit.'\n"
        "4. Provide a clear implementation path (reduces fear).\n"
        "5. Point to similar successful changes elsewhere."
    ),
    "availability_heuristic": (
        "1. Acknowledge the vivid example: 'I see why that case worries you.'\n"
        "2. Provide base rates: 'But statistically, X% of similar deals succeed.'\n"
        "3. Counter vivid bad example with vivid good example.\n"
        "4. Use data: averages, distributions, not just memorable anecdotes.\n"
        "5. Reframe: 'That was an outlier; the median outcome is...'"
    ),
}


class BehavioralEconomicsModule:
    """
    Cognitive bias detection and mitigation for negotiations.
    Detects language cues that indicate the speaker is falling into a bias trap.
    Call analyze() for the full pass, or an individual method for one bias.
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

    # -- Bias detection -------------------------------------------

    _BIAS_KEYS = (
        "loss_aversion", "anchoring", "sunk_cost_fallacy",
        "framing_effect", "status_quo_bias", "availability_heuristic"
    )

    def detect_biases(self, text: str) -> Dict:
        """Detect all cognitive biases present in the text."""
        hits = self._scan(text, "biases")
        by_bias: Dict[str, Dict] = {}

        for h in hits:
            entry = by_bias.setdefault(h["category"], {
                "bias": h["category"],
                "name": h["category"].replace("_", " ").title(),
                "label": _BIAS_PROFILE[h["category"]][0],
                "in_negotiation": _BIAS_PROFILE[h["category"]][1],
                "danger": _BIAS_DANGER[h["category"]],
                "mitigation": _BIAS_MITIGATION[h["category"]],
                "matched_keywords": [],
                "language": h["language"],
            })
            entry["matched_keywords"].append(h["keyword"])

        biases = list(by_bias.values())
        return {
            "biases_detected": biases,
            "count": len(biases),
            "primary_bias": biases[0]["bias"] if biases else None,
        }

    def analyze(self, text: str) -> Dict:
        """Full behavioral economics analysis: all biases detected."""
        return {
            "cognitive_biases": self.detect_biases(text),
        }

    def dual_speaker_bias_analysis(self, your_text: str, their_text: str) -> Dict:
        """Analyze cognitive biases in both you and the counterparty."""
        return {
            "your_biases": self.analyze(your_text),
            "their_biases": self.analyze(their_text),
            "coaching": self._dual_bias_coaching(your_text, their_text),
        }

    @staticmethod
    def _dual_bias_coaching(your_text: str, their_text: str) -> str:
        module = BehavioralEconomicsModule()
        your_analysis = module.analyze(your_text)
        their_analysis = module.analyze(their_text)

        your_biases = your_analysis["cognitive_biases"]["biases_detected"]
        their_biases = their_analysis["cognitive_biases"]["biases_detected"]

        summary = "DUAL-SPEAKER BIAS ANALYSIS\n\n"
        if your_biases:
            summary += f"YOU: {len(your_biases)} bias(es) detected:\n"
            for b in your_biases[:2]:
                summary += f"  • {b['name']}: {b['danger']}\n"
        else:
            summary += "YOU: No major biases detected.\n"

        summary += "\n"

        if their_biases:
            summary += f"THEM: {len(their_biases)} bias(es) detected:\n"
            for b in their_biases[:2]:
                summary += f"  • {b['name']}: {b['danger']}\n"
        else:
            summary += "THEM: No major biases detected.\n"

        summary += (
            "\nKEY MOVES:\n"
            "1. Recognize the bias in both of you (none are immune).\n"
            "2. Name it gently: 'I notice we're both anchored to our starting positions.'\n"
            "3. Propose a reset: 'Let's look at market data, not our initial hunches.'\n"
            "4. Use the mitigation tailored to the bias.\n"
            "5. Build in decision safeguards: sleep on it, data review, scenario planning."
        )
        return summary

    def prescribe_bias_aware_negotiation(self) -> str:
        """Guidance for negotiating while aware of cognitive biases."""
        return (
            "BIAS-AWARE NEGOTIATION STRATEGY\n\n"
            "1. RECOGNIZE YOUR OWN BIASES:\n"
            "   Before the table, note: What am I anchored to? What am I afraid to lose?\n"
            "   What past investment is clouding my judgment?\n\n"
            "2. DETECT THEIRS:\n"
            "   Listen for: 'We've invested too much.' 'The risk is.' 'We've always.'\n"
            "   These are bias cues. Name them gently.\n\n"
            "3. ANCHOR CONSCIOUSLY:\n"
            "   If you move first, anchor to a number you can defend with data.\n"
            "   If they anchor, counter-anchor explicitly.\n\n"
            "4. USE DATA TO ESCAPE VIVID FEARS:\n"
            "   'I see why that example worries you. Here's what the data shows:'\n\n"
            "5. REFRAME TO BREAK TRAPS:\n"
            "   Loss aversion? 'Here's what we gain.'\n"
            "   Status quo bias? 'Here's the cost of staying put.'\n"
            "   Sunk cost? 'Forget past spending. Is this deal good forward?'\n\n"
            "6. PROPOSE SAFEGUARDS:\n"
            "   Reduce fear of loss: 'Let's phase it in.' 'Let's add a review clause.'\n"
            "   Reduce fear of change: 'Most similar transitions succeed.'\n\n"
            "7. BUILD IN PAUSES:\n"
            "   'Let's sleep on it and talk tomorrow.' (Reduces reactive bias.)\n"
            "   'Let me check the numbers.' (Inserts data before emotion.)\n\n"
            "RESULT: Clearer thinking, better agreements, less regret."
        )
