"""
NLP (Neuro-Linguistic Programming) Module for SANTINEL
Analyzes language patterns, reframes situations, models excellence
Professional-grade communication coaching
"""

from typing import Dict, List, Tuple
from enum import Enum

class NLPRepresentationSystem(Enum):
    """Primary sensory representational systems in NLP"""
    VISUAL = "visual"      # See, look, picture, imagine
    AUDITORY = "auditory"  # Hear, listen, sound, say
    KINESTHETIC = "kinesthetic"  # Feel, touch, sense, experience

class NLPAnchor(Enum):
    """Emotional anchors and states"""
    RESOURCEFUL = "resourceful"  # Confident, capable, ready
    ANXIOUS = "anxious"  # Worried, uncertain, tense
    ASSERTIVE = "assertive"  # Strong, direct, clear
    COLLABORATIVE = "collaborative"  # Open, cooperative, flexible
    DEFENSIVE = "defensive"  # Guarded, closed, resistant

class NLPModule:
    """
    NLP Coaching Engine
    Maps language patterns → Sensory systems → Emotional anchors
    Provides reframing and strategic language coaching
    """
    
    def __init__(self):
        self.visual_keywords = [
            "see", "look", "picture", "imagine", "watch", "view", 
            "bright", "dark", "clear", "fuzzy", "visualize", "show"
        ]
        self.auditory_keywords = [
            "hear", "listen", "sound", "say", "tell", "voice", 
            "loud", "quiet", "tone", "harmony", "ring", "silent"
        ]
        self.kinesthetic_keywords = [
            "feel", "touch", "sense", "grasp", "handle", "experience",
            "warm", "cold", "smooth", "rough", "pressure", "contact"
        ]
        
        self.problem_frames = {
            "conflict": ["fight", "battle", "win/lose", "enemy", "attack"],
            "obstacle": ["blocked", "stuck", "barrier", "can't", "impossible"],
            "negotiation": ["deal", "agreement", "exchange", "value", "trade"],
        }

    def detect_representation_system(self, text: str) -> Dict:
        """
        Detect which sensory system the person is using
        Visual, Auditory, or Kinesthetic preference
        """
        text_lower = text.lower()
        
        visual_score = sum(1 for kw in self.visual_keywords if kw in text_lower)
        auditory_score = sum(1 for kw in self.auditory_keywords if kw in text_lower)
        kinesthetic_score = sum(1 for kw in self.kinesthetic_keywords if kw in text_lower)
        
        total = visual_score + auditory_score + kinesthetic_score
        
        if total == 0:
            primary = "kinesthetic"  # Default
            scores = {"visual": 0, "auditory": 0, "kinesthetic": 0.5}
        else:
            primary = max(
                [("visual", visual_score), ("auditory", auditory_score), ("kinesthetic", kinesthetic_score)],
                key=lambda x: x[1]
            )[0]
            scores = {
                "visual": visual_score / total if total else 0,
                "auditory": auditory_score / total if total else 0,
                "kinesthetic": kinesthetic_score / total if total else 0,
            }
        
        return {
            "primary_system": primary,
            "scores": scores,
            "recommendation": self._get_system_recommendation(primary)
        }

    def _get_system_recommendation(self, system: str) -> str:
        """Coaching recommendation based on representation system"""
        recommendations = {
            "visual": "Use visual metaphors, show the bigger picture, help them 'see' the value",
            "auditory": "Use auditory metaphors, listen actively, get their 'voice' heard",
            "kinesthetic": "Use tactile metaphors, acknowledge feelings, help them 'feel' the agreement",
        }
        return recommendations.get(system, "")

    def detect_problem_frame(self, text: str) -> str:
        """Detect how person is framing the situation"""
        text_lower = text.lower()
        
        for frame, keywords in self.problem_frames.items():
            if any(kw in text_lower for kw in keywords):
                return frame
        
        return "other"

    def generate_nlp_reframe(self, situation: str, current_frame: str, emotion: str) -> str:
        """
        Generate NLP reframe that shifts from problem to opportunity
        Problem frame → Negotiation frame
        """
        reframes = {
            "conflict": """
🔄 NLP REFRAME: From Conflict to Collaborative Problem-Solving
   CURRENT: "We're in a battle"
   REFRAME: "We're partners solving a puzzle together"
   
   ACTION: Shift language from "win/lose" to "mutual value"
   USE: "Let's explore what works for both of us"
""",
            "obstacle": """
🔄 NLP REFRAME: From Obstacle to Opportunity
   CURRENT: "This is impossible / blocking us"
   REFRAME: "This is a constraint that clarifies what we need"
   
   ACTION: Find creative solutions within constraints
   USE: "Given this situation, what are our options?"
""",
            "negotiation": """
🔄 NLP REFRAME: Anchor Resourceful State
   CURRENT: "I need to get the best deal"
   REFRAME: "I create mutual value and clear agreements"
   
   ACTION: Lead from capability, not desperation
   USE: "Here's what I can offer that creates value for both"
""",
        }
        
        return reframes.get(current_frame, "Recognize this is a negotiation. Focus on mutual value.")

    def model_excellence(self, target_outcome: str) -> str:
        """
        NLP modeling: How would an excellent negotiator approach this?
        Anchors to resourceful, assertive, collaborative state
        """
        excellent_negotiator = f"""
✨ MODELING EXCELLENCE: How Expert Negotiators Approach This

🧠 INTERNAL REPRESENTATION:
   • They see the negotiation as problem-solving, not conflict
   • They hear mutual respect and clear communication
   • They feel grounded, confident, flexible

📍 ANCHORING STATES:
   ✅ RESOURCEFUL: "I have options and value to offer"
   ✅ ASSERTIVE: "I can clearly state my needs and boundaries"
   ✅ COLLABORATIVE: "We can find solutions that work for both"

🎯 BEHAVIOR SEQUENCE:
   1. Listen deeply to understand their needs (Auditory anchor)
   2. Show how your solution fits their picture (Visual anchor)
   3. Create comfort with the agreement (Kinesthetic anchor)

🗣️ LINGUISTIC PATTERNS:
   • Use "we" and "together" (inclusive)
   • Specific, sensory-rich language (clear pictures)
   • Present tense, possibility language ("we can", "let's create")

💪 POWER MOVE:
   Access your resourceful state first, then engage from that anchor.
"""
        return excellent_negotiator

    def linguistic_pattern_analysis(self, statement: str) -> Dict:
        """
        Analyze linguistic patterns that limit or empower
        Modal operators: can/can't, will/won't, must/don't have to
        """
        text_lower = statement.lower()
        
        limitations = {
            "can't": statement.count("can't"),
            "won't": statement.count("won't"),
            "impossible": statement.count("impossible"),
            "must": statement.count("must"),
            "should": statement.count("should"),
        }
        
        possibilities = {
            "can": statement.count("can") - limitations["can't"],
            "will": statement.count("will") - limitations["won't"],
            "could": statement.count("could"),
            "might": statement.count("might"),
            "possible": statement.count("possible"),
        }
        
        total_limiting = sum(limitations.values())
        total_possible = sum(max(0, v) for v in possibilities.values())
        
        return {
            "limiting_language_count": total_limiting,
            "possibility_language_count": total_possible,
            "modal_ratio": total_possible / (total_limiting + 1),  # Avoid division by zero
            "coaching": self._language_coaching(total_limiting, total_possible)
        }

    def _language_coaching(self, limiting: int, possible: int) -> str:
        """Coaching based on language pattern balance"""
        if limiting > possible:
            return "🎯 COACHING: Shift from limiting language ('can't', 'must') to possibility language ('could', 'might')"
        elif possible > limiting:
            return "✅ STRONG: You're using empowering language. Maintain this resourceful state."
        else:
            return "⚖️ BALANCE: Mix limiting and possibility language. Lean more toward 'could' and 'might'."