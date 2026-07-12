"""
TA (Transactional Analysis) Module for SANTINEL
Analyzes ego states (Parent, Adult, Child), games, life positions
Professional-grade interpersonal dynamics coaching
"""

from typing import Dict, List, Tuple
from enum import Enum

class EgoState(Enum):
    """Three ego states in Transactional Analysis"""
    PARENT = "parent"
    ADULT = "adult"
    CHILD = "child"

class LifePosition(Enum):
    """Four life positions that shape behavior"""
    I_OK_YOU_OK = "i_ok_you_ok"
    I_OK_YOU_NOT_OK = "i_ok_you_not_ok"
    I_NOT_OK_YOU_OK = "i_not_ok_you_ok"
    I_NOT_OK_YOU_NOT_OK = "i_not_ok_you_not_ok"

class TAGame(Enum):
    """Common psychological games in negotiations"""
    UPROAR = "uproar"
    RAPO = "rapo"
    NOW_I_GOT_YOU = "now_i_got_you"
    KICK_ME = "kick_me"
    YES_BUT = "yes_but"
    WOODEN_LEG = "wooden_leg"

class TAModule:
    """
    Transactional Analysis Coaching Engine
    Maps ego states, life positions, games in negotiations
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
        """Detect which ego state person is operating from"""
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
            "critical_parent": "🚨 CRITICAL PARENT: Judgmental, controlling",
            "nurturing_parent": "💚 NURTURING PARENT: Helpful but can be patronizing",
            "adult": "✅ ADULT: Logical, collaborative. BEST for negotiations",
            "free_child": "😊 FREE CHILD: Enthusiastic, spontaneous",
            "adapted_child": "🤐 ADAPTED CHILD: Compliant, passive",
        }
        return analyses.get(state, "Mixed ego state detected")

    def detect_life_position(self, text: str, emotion: str) -> LifePosition:
        """Detect underlying life position from language and emotion"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["mutual", "win-win", "both", "together", "respect"]):
            return LifePosition.I_OK_YOU_OK
        
        if any(kw in text_lower for kw in ["they're wrong", "I'm right", "superior", "winning"]):
            return LifePosition.I_OK_YOU_NOT_OK
        
        if any(kw in text_lower for kw in ["I'm wrong", "they're right", "apologize", "inferior"]):
            return LifePosition.I_NOT_OK_YOU_OK
        
        if any(kw in text_lower for kw in ["hopeless", "pointless", "give up", "disaster"]):
            return LifePosition.I_NOT_OK_YOU_NOT_OK
        
        return LifePosition.I_OK_YOU_OK

    def detect_psychological_game(self, text: str) -> Dict:
        """Detect if person is playing a psychological game"""
        text_lower = text.lower()
        
        detected_games = []
        for game, keywords in self.game_patterns.items():
            if any(kw in text_lower for kw in keywords):
                detected_games.append({
                    "game": game.value,
                    "description": self._get_game_description(game),
                    "payoff": self._get_game_payoff(game),
                })
        
        return {
            "games_detected": detected_games,
            "coaching": self._game_coaching(detected_games) if detected_games else "No psychological games detected."
        }

    def _get_game_description(self, game: TAGame) -> str:
        """Description of psychological game"""
        descriptions = {
            TAGame.UPROAR: "Creating drama to avoid dealing with core issue",
            TAGame.RAPO: "Seduction followed by unexpected rejection",
            TAGame.NOW_I_GOT_YOU: "Setting a trap to catch other person in mistake",
            TAGame.KICK_ME: "Inviting others to attack or criticize you",
            TAGame.YES_BUT: "Asking for help then rejecting all suggestions",
            TAGame.WOODEN_LEG: "Using a limitation as excuse to avoid responsibility",
        }
        return descriptions.get(game, "Psychological game detected")

    def _get_game_payoff(self, game: TAGame) -> str:
        """The hidden payoff or 'winner' in the game"""
        payoffs = {
            TAGame.UPROAR: "Avoid dealing with real problem",
            TAGame.RAPO: "Feel powerful then victimized",
            TAGame.NOW_I_GOT_YOU: "Prove other person is wrong/bad",
            TAGame.KICK_ME: "Confirm belief that 'nobody likes me'",
            TAGame.YES_BUT: "Prove advice-giver inadequate",
            TAGame.WOODEN_LEG: "Avoid responsibility and blame",
        }
        return payoffs.get(game, "Unknown payoff")

    def _game_coaching(self, games: List[Dict]) -> str:
        """Coaching to exit the game"""
        if not games:
            return "No games detected"
        
        return f"""
⚠️ PSYCHOLOGICAL GAME DETECTED: {games[0]['game'].upper()}

🎭 PATTERN: {games[0]['description']}
💰 PAYOFF: {games[0]['payoff']}

🚪 EXIT STRATEGY:
1. Recognize you're in it
2. Stop playing your role
3. Return to Adult ego state
4. Speak honestly about needs
5. Propose Adult-to-Adult transaction
"""

    def prescribe_healthy_transaction(self, situation: str) -> str:
        """Prescribe healthy Adult-to-Adult transaction"""
        prescription = """
✅ HEALTHY TRANSACTIONAL ANALYSIS COACHING

🎯 TARGET: Adult-to-Adult Transaction from I'm OK/You're OK position

📍 EGO STATE: Move to ADULT
   • Facts, logic, problem-solving
   • Responsibility for own position
   • Respect for other person's needs

💡 LIFE POSITION: I'm OK/You're OK
   ✅ I have value to offer
   ✅ You have legitimate needs
   ✅ Mutual respect is possible
   ✅ We can create mutual value

🗣️ LANGUAGE SHIFTS:
   FROM: "You're being unreasonable"
   TO: "Here's what makes sense for both of us"

🤝 HEALTHY NEGOTIATION:
   • Ask genuine questions about other's needs
   • Acknowledge legitimate constraints
   • Propose solutions honoring both parties
   • Keep communication direct and honest

⚡ POWER: Creates psychological safety → Faster resolution
"""
        return prescription