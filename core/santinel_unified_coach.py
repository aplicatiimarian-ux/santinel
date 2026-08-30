# -*- coding: utf-8 -*-
"""
SANTINEL Unified Coach: Orchestration Layer
Synthesizes all 10 frameworks into integrated coaching recommendations.

This module routes negotiation dialogue through all 10 frameworks in parallel,
detects conflicts and synergies, and produces a single, prioritized coaching output.

Frameworks orchestrated:
1. TA (Transactional Analysis)
2. EI (Emotional Intelligence)
3. Attachment
4. Behavioral Economics
5. Game Theory
6. Neuroscience
7. Narrative
8. Somatic
9. Feedback Extraction
10. Sales Scripts

Integration algorithm:
- Run all frameworks in parallel on input text
- Synthesize findings into unified "nervous system" reading
- Detect conflicts (e.g., game theory says compete, attachment says safe)
- Identify synergies (e.g., narrative + neuroscience both signal dysregulation)
- Rank recommendations by impact and confidence
- Output: 1-5 key moves for the next 5 minutes
"""

from typing import Dict, List, Tuple
from enum import Enum

try:
    from core.ta_module import TAModule
    from core.ei_module import EIModule
    from core.attachment_module import AttachmentModule
    from core.behavioral_econ_module import BehavioralEconomicsModule
    from core.game_theory_module import GameTheoryModule
    from core.neuroscience_module import NeuroscienceModule
    from core.narrative_module import NarrativeModule
    from core.somatic_module import SomaticModule
    from core.feedback_extraction_module import FeedbackExtractionModule
    from core.sales_scripts_module import SalesScriptsModule
except ImportError:
    # Fallback for testing
    TAModule = EIModule = AttachmentModule = None
    BehavioralEconomicsModule = GameTheoryModule = NeuroscienceModule = None
    NarrativeModule = SomaticModule = FeedbackExtractionModule = None
    SalesScriptsModule = None


class FrameworkPriority(Enum):
    """Framework importance hierarchy."""
    CRITICAL = 5  # Immediate threat/safety
    HIGH = 4      # Major pattern/signal
    MEDIUM = 3    # Secondary insight
    LOW = 2       # Supporting info
    MINIMAL = 1   # Context only


class SantinelUnifiedCoach:
    """
    Orchestrates all 10 frameworks and synthesizes recommendations.
    """

    def __init__(self):
        self.ta = TAModule() if TAModule else None
        self.ei = EIModule() if EIModule else None
        self.attachment = AttachmentModule() if AttachmentModule else None
        self.behavioral_econ = BehavioralEconomicsModule() if BehavioralEconomicsModule else None
        self.game_theory = GameTheoryModule() if GameTheoryModule else None
        self.neuroscience = NeuroscienceModule() if NeuroscienceModule else None
        self.narrative = NarrativeModule() if NarrativeModule else None
        self.somatic = SomaticModule() if SomaticModule else None
        self.feedback = FeedbackExtractionModule() if FeedbackExtractionModule else None
        self.scripts = SalesScriptsModule() if SalesScriptsModule else None

    def analyze_unified(self, your_text: str, their_text: str = "") -> Dict:
        """
        Route input through all 10 frameworks in parallel.
        Synthesize findings into integrated coaching.
        """
        findings = {}

        # Framework 1: Transactional Analysis
        if self.ta:
            findings["ta"] = self.ta.analyze(their_text) if their_text else None

        # Framework 2: Emotional Intelligence
        if self.ei:
            findings["ei"] = self.ei.analyze(their_text) if their_text else None

        # Framework 3: Attachment
        if self.attachment:
            findings["attachment"] = self.attachment.analyze(their_text) if their_text else None

        # Framework 4: Behavioral Economics
        if self.behavioral_econ:
            findings["behavioral_econ"] = self.behavioral_econ.analyze(their_text) if their_text else None

        # Framework 5: Game Theory
        if self.game_theory:
            findings["game_theory"] = self.game_theory.analyze(their_text) if their_text else None

        # Framework 6: Neuroscience
        if self.neuroscience:
            findings["neuroscience"] = self.neuroscience.analyze(their_text) if their_text else None

        # Framework 7: Narrative
        if self.narrative:
            findings["narrative"] = self.narrative.analyze(their_text) if their_text else None

        # Framework 8: Somatic
        if self.somatic:
            findings["somatic"] = self.somatic.analyze(their_text) if their_text else None

        # Framework 9: Feedback Extraction
        if self.feedback:
            findings["feedback"] = self.feedback.analyze_real_time(your_text, their_text)

        # Framework 10: Sales Scripts (assess situation)
        if self.scripts:
            # Determine situation from other frameworks
            situation = self._determine_situation(findings)
            personality = self._determine_personality(findings)
            findings["scripts"] = {
                "situation": situation,
                "personality": personality,
            }

        # Synthesize all frameworks
        synthesis = self._synthesize_frameworks(findings)

        # Detect conflicts and synergies
        conflicts, synergies = self._detect_patterns(findings)

        # Generate integrated coaching
        coaching = self._generate_integrated_coaching(synthesis, conflicts, synergies, findings)

        return {
            "framework_findings": findings,
            "synthesis": synthesis,
            "conflicts": conflicts,
            "synergies": synergies,
            "integrated_coaching": coaching,
            "close_probability": findings.get("feedback", {}).get("close_probability_score", 0),
            "next_moves": self._prioritize_moves(coaching),
        }

    @staticmethod
    def _determine_situation(findings: Dict) -> str:
        """Infer situation from framework findings."""
        if findings.get("feedback"):
            close_prob = findings["feedback"].get("close_probability_score", 0)
            if close_prob >= 8:
                return "closing"
            elif close_prob <= 2:
                return "objection_handling"
            else:
                return "negotiation"
        return "unknown"

    @staticmethod
    def _determine_personality(findings: Dict) -> str:
        """Infer personality type from framework signals."""
        ei = findings.get("ei", {})
        emotional_state = ei.get("emotional_state", {}).get("primary_finding", "neutral")

        if emotional_state in ["excitement", "enthusiasm"]:
            return "expressive"
        elif emotional_state in ["calm", "grounded", "openness"]:
            return "analytical"
        else:
            return "driver"

    def _synthesize_frameworks(self, findings: Dict) -> Dict:
        """Create unified nervous system reading."""
        synthesis = {
            "threat_level": "unknown",
            "engagement_level": "unknown",
            "decision_readiness": "unknown",
            "relationship_quality": "unknown",
            "strategic_position": "unknown",
        }

        # Threat level from neuroscience + somatic + attachment
        neuro = findings.get("neuroscience", {})
        if neuro:
            threat_score = neuro.get("threat_safety_reward", {}).get("threat", 0)
            synthesis["threat_level"] = "HIGH" if threat_score > 0.6 else "MEDIUM" if threat_score > 0.3 else "LOW"

        # Engagement from EI + feedback + somatic
        ei = findings.get("ei", {})
        if ei and ei.get("emotional_state"):
            state = ei["emotional_state"].get("primary_finding")
            synthesis["engagement_level"] = "HIGH" if state in ["openness", "curiosity"] else "MEDIUM" if state in ["acceptance"] else "LOW"

        # Decision readiness from feedback
        feedback = findings.get("feedback", {})
        if feedback:
            close_prob = feedback.get("close_probability_score", 0)
            synthesis["decision_readiness"] = "READY" if close_prob >= 8 else "PROGRESSING" if close_prob >= 5 else "EARLY"

        # Relationship quality from attachment + narrative + somatic
        attach = findings.get("attachment", {})
        attachment_style = attach.get("attachment_style", {})
        synthesis["relationship_quality"] = attachment_style.get("primary_finding", "unknown")

        # Strategic position from game theory
        game = findings.get("game_theory", {})
        strategic_pos = game.get("strategic_position", {})
        synthesis["strategic_position"] = strategic_pos.get("primary_finding", "unknown")

        return synthesis

    @staticmethod
    def _detect_patterns(findings: Dict) -> Tuple[List[str], List[str]]:
        """Detect conflicts and synergies across frameworks."""
        conflicts = []
        synergies = []

        # Example conflicts
        game_theory = findings.get("game_theory", {})
        narrative = findings.get("narrative", {})

        game_archetype = game_theory.get("game_archetype", {}).get("primary_finding")
        dominant_narrative = narrative.get("dominant_narrative", {}).get("primary_finding")

        if game_archetype == "zero_sum" and dominant_narrative == "collaborative_narrative":
            conflicts.append("CONFLICT: Game theory says zero-sum (compete) but narrative says collaborative. Clarify whether this is win-win or winner-take-all.")

        # Example synergies
        neuroscience = findings.get("neuroscience", {})
        somatic = findings.get("somatic", {})

        nervous_state = neuroscience.get("nervous_system_state", {}).get("primary_finding")
        somatic_state = somatic.get("somatic_state", {}).get("primary_finding")

        if nervous_state == "parasympathetic" and somatic_state == "grounded":
            synergies.append("SYNERGY: Both neuroscience and somatic show calm, grounded state. Optimal for trust-building and problem-solving.")

        return conflicts, synergies

    def _generate_integrated_coaching(self, synthesis: Dict, conflicts: List[str], synergies: List[str], findings: Dict) -> List[Dict]:
        """Generate integrated coaching recommendations."""
        recommendations = []

        threat_level = synthesis["threat_level"]
        if threat_level == "HIGH":
            recommendations.append({
                "priority": FrameworkPriority.CRITICAL.value,
                "move": "DE-ESCALATE",
                "reasoning": "Neuroscience + Somatic show dysregulation. Move to grounding and safety signals.",
                "frameworks": ["neuroscience", "somatic"],
            })

        decision_readiness = synthesis["decision_readiness"]
        if decision_readiness == "READY":
            recommendations.append({
                "priority": FrameworkPriority.CRITICAL.value,
                "move": "CLOSE",
                "reasoning": f"Close probability high. Feedback extraction shows readiness. Use direct closing script.",
                "frameworks": ["feedback", "scripts"],
            })

        engagement_level = synthesis["engagement_level"]
        if engagement_level == "LOW":
            recommendations.append({
                "priority": FrameworkPriority.HIGH.value,
                "move": "ENGAGE",
                "reasoning": "EI shows low engagement. Use high-energy rapport-building. Activate reward system (highlight benefits).",
                "frameworks": ["ei", "neuroscience"],
            })

        # Add synergy recommendations
        for synergy in synergies:
            recommendations.append({
                "priority": FrameworkPriority.MEDIUM.value,
                "move": "LEVERAGE",
                "reasoning": synergy,
                "frameworks": ["combined"],
            })

        # Add conflict resolution
        for conflict in conflicts:
            recommendations.append({
                "priority": FrameworkPriority.HIGH.value,
                "move": "CLARIFY",
                "reasoning": conflict,
                "frameworks": ["meta"],
            })

        return recommendations

    @staticmethod
    def _prioritize_moves(recommendations: List[Dict]) -> List[str]:
        """Prioritize moves for next 5 minutes."""
        sorted_recs = sorted(recommendations, key=lambda x: x["priority"], reverse=True)
        return [rec["move"] for rec in sorted_recs[:5]]

    def prescribe_unified_approach(self) -> str:
        """Guidance for using unified coach."""
        return (
            "UNIFIED COACHING APPROACH\n\n"
            "The unified coach runs all 10 frameworks simultaneously and synthesizes into one voice.\n\n"
            "INPUT: Your text + their text\n"
            "↓\n"
            "PARALLEL PROCESSING:\n"
            "• Frameworks 1-10 analyze simultaneously\n"
            "• Each provides its lens on the situation\n"
            "• Results stream in as complete\n"
            "↓\n"
            "SYNTHESIS:\n"
            "• Unified nervous system reading (threat, engagement, decision readiness)\n"
            "• Conflict detection (when frameworks disagree)\n"
            "• Synergy identification (when frameworks align)\n"
            "↓\n"
            "RECOMMENDATION:\n"
            "• 1-5 priority moves for the next 5 minutes\n"
            "• Ranked by impact and confidence\n"
            "• Each move cites which frameworks support it\n"
            "↓\n"
            "OUTPUT: One clear, actionable coaching move.\n\n"
            "EXAMPLE:\n"
            "Input: 'I'm not sure about timing. It's a big investment. What's the risk?'\n"
            "↓\n"
            "Frameworks detect:\n"
            "  TA: Adult ego state (good)\n"
            "  EI: Skeptical emotional state\n"
            "  Behavioral Econ: Loss aversion active\n"
            "  Neuroscience: Amygdala slightly activated\n"
            "  Attachment: Anxious attachment showing\n"
            "  Feedback: -1.0 close probability shift\n"
            "↓\n"
            "Unified output:\n"
            "  THREAT LEVEL: MEDIUM (loss aversion + anxiety)\n"
            "  MOVE 1: Acknowledge risk (validates fear)\n"
            "  MOVE 2: Reframe as opportunity (behavioral econ reframe)\n"
            "  MOVE 3: Offer 30-day pilot (reduces amygdala activation)\n"
            "↓\n"
            "Result: Three moves addressing six different frameworks simultaneously."
        )
