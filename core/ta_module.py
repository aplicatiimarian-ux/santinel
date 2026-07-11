"""
TA (Transactional Analysis) Module for SANTINEL
Analyzes ego states (Parent, Adult, Child), games, life positions
Professional-grade interpersonal dynamics coaching
"""

from typing import Dict, List, Tuple
from enum import Enum

class EgoState(Enum):
    """Three ego states in Transactional Analysis"""
    PARENT = "parent"      # Critical or Nurturing - authority, rules, judgment
    ADULT = "adult"        # Logical, problem-solving - facts, options, responsibility
    CHILD = "child"        # Free or Adapted - emotions, spontaneity, compliance

class LifePosition(Enum):
    """Four life positions that shape behavior"""
    I_OK_YOU_OK = "i_ok_you_ok"          # Healthy, collaborative, win-win
    I_OK_YOU_NOT_OK = "i_ok_you_not_ok"  # Superior, dismissive, win-lose
    I_NOT_OK_YOU_OK = "i_not_ok_you_ok"  # Inferior, passive, lose-win
    I_NOT_OK_YOU_NOT_OK = "i_not_ok_you_not_ok"  # Hopeless, giving up, lose-lose

class TAGame(Enum):
    """Common psychological games in negotiations"""
    UPROAR = "uproar"              # Create drama to avoid real issue
    RAPO = "rapo"                  # Seduction followed by rejection
    NOW_I_GOT_YOU = "now_i_got_you"  # Set trap for other person
    KICK_ME = "kick_me"            # Invite others to attack you
    YES_BUT = "yes_but"            # Ask for help then reject it
    WOODEN_LEG = "wooden_leg"      # Use limitation as excuse

class TAModule:
    """
    Transactional Analysis Coaching Engine
    Maps ego states, life positions, games in negotiations
    Provides coaching for healthy Adult-to-Adult transactions
    """
    
    def __init__(self):
        self.parent_keywords = {
            "critical": ["should", "must", "wrong", "bad", "ridiculous", "stupid"],
            "nurturing": ["poor thing", "let me help", "you need", "I'll take care"],
        }
        
        self.adult_keywords = [
            "think", "analyze", "data", "facts", "option", "consider",
            "reasonable", "logical", "evidence", "problem-solve"
        ]
        
        self.child_keywords = {
            "free": ["fun", "exciting", "wow", "amazing", "want", "yes"],
            "adapted": ["sorry", "okay", "whatever", "fine", "you decide", "I guess"],
        }
        
        self.game_patterns = {
            TAGame.YES_BUT: ["yes but", "that won't work", "I tried that", "it's impossible"],
            TAGame.WOODEN_LEG: ["I can't because", "I'm not able to", "it's not my fault"],
            TAGame.UPROAR: ["drama", "crisis", "emergency", "disaster", "urgent"],
            TAGame.NOW_I_GOT_YOU: ["caught you", "trap", "gotcha", "I knew it"],
        }

    def detect_ego_state(self, text: str) -> Dict:
        """
        Detect which ego state person is operating from
        Parent (judgmental/nurturing), Adult (logical), or Child (emotional/compliant)
        """
        text_lower = text.lower()
        
        critical_parent = sum(1 for kw in self.parent_keywords["critical"] if kw in text_lower)
        nurturing_parent = sum(1 for kw in self.parent_keywords["nurturing"] if kw in text_lower)
        adult = sum(1 for kw in self.adult_keywords if kw in text_lower)
        free_child = sum(1 for kw in self.child_keywords["free"] if kw in text_lower)
        adapted_child = sum(1 for kw in self.child_keywords["adapted"] if kw in text_lower)
        
        scores = {
            "critical_parent": critical_parent,
            "nurturing_parent": nurturing_parent,
            "adult": adult,
            "free_child": free_child,
            "adapted_child": adapted_child,
        }
        
        primary = max(scores, key=scores.get)
        
        return {
            "primary_ego_state": primary,
            "scores": scores,
            "analysis": self._ego_state_analysis(primary),
        }

    def _ego_state_analysis(self, state: str) -> str:
        """Analysis of current ego state"""
        analyses = {
            "critical_parent": "🚨 CRITICAL PARENT: Judgmental, controlling. Risk: Damages rapport.",
            "nurturing_parent": "💚 NURTURING PARENT: Helpful but can be patronizing. Risk: Creates dependency.",
            "adult": "✅ ADULT: Logical, collaborative. BEST for negotiations.",
            "free_child": "😊 FREE CHILD: Enthusiastic, spontaneous. Risk: Unpredictable, emotional.",
            "adapted_child": "🤐 ADAPTED CHILD: Compliant, passive. Risk: Loses your position.",
        }
        return analyses.get(state, "Mixed ego state detected.")

    def detect_life_position(self, text: str, emotion: str) -> LifePosition:
        """
        Detect underlying life position from language and emotion
        This shapes ALL negotiation behavior
        """
        text_lower = text.lower()
        
        # I_OK_YOU_OK indicators
        if any(kw in text_lower for kw in ["mutual", "win-win", "both", "together", "respect"]):
            return LifePosition.I_OK_YOU_OK
        
        # I_OK_YOU_NOT_OK indicators
        if any(kw in text_lower for kw in ["they're wrong", "I'm right", "superior", "winning"]):
            return LifePosition.I_OK_YOU_NOT_OK
        
        # I_NOT_OK_YOU_OK indicators
        if any(kw in text_lower for kw in ["I'm wrong", "they're right", "apologize", "inferior"]):
            return LifePosition.I_NOT_OK_YOU_OK
        
        # I_NOT_OK_YOU_NOT_OK indicators
        if any(kw in text_lower for kw in ["hopeless", "pointless", "give up", "disaster"]):
            return LifePosition.I_NOT_OK_YOU_NOT_OK
        
        return LifePosition.I_OK_YOU_OK  # Default optimistic

    def detect_psychological_game(self, text: