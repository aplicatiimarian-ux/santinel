"""
Dual-Speaker Analysis Module for SANTINEL
Analyzes BOTH negotiators: You + Counterparty
Provides coaching for each person's state + interaction dynamics
Professional-grade multi-party negotiation coaching
"""

from typing import Dict, List, Tuple
from enum import Enum
import json

class PartyRole(Enum):
    """Roles in negotiation"""
    USER = "user"              # You (primary person being coached)
    COUNTERPARTY = "counterparty"  # The other negotiator

class NegotiationDynamic(Enum):
    """Types of negotiation dynamics"""
    COLLABORATIVE = "collaborative"    # Both working together
    COMPETITIVE = "competitive"        # Both fighting for advantage
    MIXED = "mixed"                     # Unclear intentions
    COMPLEMENTARY = "complementary"    # One leads, one follows
    SYMMETRICAL = "symmetrical"        # Equal power dynamics

class DualSpeakerAnalyzer:
    """
    Analyzes both parties in negotiation
    Maps emotional states, ego states, life positions
    Provides coaching strategies for each
    """
    
    def __init__(self):
        self.user_data = {
            "transcription": "",
            "emotions": {},
            "ego_state": None,
            "life_position": None,
            "communication_style": None,
        }
        
        self.counterparty_data = {
            "inferred_position": "",
            "inferred_emotions": {},
            "inferred_ego_state": None,
            "inferred_life_position": None,
            "communication_style": None,
        }

    def analyze_user(self, 
                     transcription: str, 
                     emotions: Dict[str, float],
                     ego_state: str,
                     life_position: str) -> Dict:
        """
        Analyze the user (primary negotiator)
        Direct assessment from audio/text
        """
        self.user_data = {
            "transcription": transcription,
            "emotions": emotions,
            "ego_state": ego_state,
            "life_position": life_position,
            "communication_style": self._assess_communication_style(transcription),
            "emotional_state": max(emotions, key=emotions.get) if emotions else "neutral",
        }
        
        return self.user_data

    def infer_counterparty_state(self, 
                                 user_transcription: str,
                                 context: str = "") -> Dict:
        """
        Infer counterparty's emotional state, needs, position
        Based on: What user SAID they said/did + context
        """
        # Keywords indicating counterparty emotional state
        resistance_indicators = [
            "resistant", "unwilling", "refused", "angry", "frustrated",
            "defensive", "closed off", "not listening", "dismissive"
        ]
        
        interest_indicators = [
            "interested", "engaged", "asking questions", "open",
            "nodding", "leaning in", "taking notes", "curious"
        ]
        
        pressure_indicators = [
            "pushing", "demanding", "ultimatum", "deadline",
            "take it or leave it", "final offer", "no flexibility"
        ]
        
        text_lower = user_transcription.lower()
        
        counterparty_emotions = {}
        if any(ind in text_lower for ind in resistance_indicators):
            counterparty_emotions["resistance"] = 0.8
            counterparty_emotions["defensiveness"] = 0.7
        
        if any(ind in text_lower for ind in interest_indicators):
            counterparty_emotions["interest"] = 0.8
            counterparty_emotions["openness"] = 0.7
        
        if any(ind in text_lower for ind in pressure_indicators):
            counterparty_emotions["assertiveness"] = 0.9
            counterparty_emotions["pressure"] = 0.8
        
        self.counterparty_data = {
            "inferred_emotions": counterparty_emotions,
            "inferred_position": self._infer_position(counterparty_emotions),
            "likely_ego_state": self._infer_ego_state(user_transcription),
            "communication_style": self._infer_communication_style(user_transcription),
            "readiness_to_agree": self._assess_readiness(counterparty_emotions),
        }
        
        return self.counterparty_data

    def _infer_position(self, emotions: Dict) -> str:
        """Infer counterparty's negotiating position from emotions"""
        if emotions.get("resistance", 0) > 0.6:
            return "Defensive - protecting current position"
        elif emotions.get("interest", 0) > 0.6:
            return "Open - exploring possibilities"
        elif emotions.get("pressure", 0) > 0.6:
            return "Aggressive - pushing for concessions"
        else:
            return "Unclear - need more information"

    def _infer_ego_state(self, user_statement: str) -> str:
        """Infer counterparty's ego state from what user described"""
        text_lower = user_statement.lower()
        
        if any(kw in text_lower for kw in ["told me", "ordered", "demanded", "insisted"]):
            return "Critical Parent"
        elif any(kw in text_lower for kw in ["worried", "concerned", "afraid", "uncertain"]):
            return "Adapted Child"
        elif any(kw in text_lower for kw in ["asked questions", "listened", "considered"]):
            return "Adult"
        else:
            return "Mixed"

    def _infer_communication_style(self, statement: str) -> str:
        """Infer how counterparty likely communicates"""
        text_lower = statement.lower()
        
        if any(kw in text_lower for kw in ["aggressive", "direct", "blunt", "no nonsense"]):
            return "Direct/Aggressive"
        elif any(kw in text_lower for kw in ["careful", "diplomatic", "subtle", "hints"]):
            return "Diplomatic/Subtle"
        elif any(kw in text_lower for kw in ["collaborative", "cooperative", "working together"]):
            return "Collaborative"
        else:
            return "Unknown - observe more"

    def _assess_readiness(self, emotions: Dict) -> str:
        """Assess if counterparty is ready to agree"""
        interest = emotions.get("interest", 0)
        resistance = emotions.get("resistance", 0)
        
        if interest > 0.7 and resistance < 0.3:
            return "🟢 HIGH: They seem ready to move forward"
        elif interest > 0.5 or resistance < 0.5:
            return "🟡 MEDIUM: Possibilities exist, need more work"
        else:
            return "🔴 LOW: Significant resistance, may need different approach"

    def _assess_communication_style(self, text: str) -> str:
        """Assess user's own communication style"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["we", "together", "let's", "mutual"]):
            return "Collaborative"
        elif any(kw in text_lower for kw in ["I", "my", "mine", "need"]):
            return "Assertive"
        elif any(kw in text_lower for kw in ["sorry", "maybe", "if", "perhaps"]):
            return "Tentative"
        else:
            return "Neutral"

    def analyze_interaction_dynamics(self) -> Dict:
        """
        Analyze the dynamic BETWEEN the two parties
        Is it collaborative? Competitive? Mismatched?
        """
        user_style = self.user_data.get("communication_style", "Unknown")
        counterparty_style = self.counterparty_data.get("communication_style", "Unknown")
        
        # Determine dynamic type
        if "collaborative" in user_style.lower() and "collaborative" in counterparty_style.lower():
            dynamic = NegotiationDynamic.COLLABORATIVE
        elif "assertive" in user_style.lower() and "direct" in counterparty_style.lower():
            dynamic = NegotiationDynamic.COMPETITIVE
        else:
            dynamic = NegotiationDynamic.MIXED
        
        return {
            "dynamic_type": dynamic.value,
            "compatibility": self._assess_compatibility(user_style, counterparty_style),
            "risk_factors": self._identify_risk_factors(dynamic),
            "opportunity_factors": self._identify_opportunities(dynamic),
        }

    def _assess_compatibility(self, user_style: str, counterparty_style: str) -> str:
        """How well-matched are the two communication styles?"""
        if user_style == counterparty_style:
            return "🟢 MATCHED: Same communication style - easier rapport"
        else:
            return "🟡 MISMATCHED: Different styles - need translation"

    def _identify_risk_factors(self, dynamic: NegotiationDynamic) -> List[str]:
        """Identify risks in this dynamic"""
        risks = {
            NegotiationDynamic.COLLABORATIVE: ["Both may miss own interests", "Agreement without clear terms"],
            NegotiationDynamic.COMPETITIVE: ["Escalation of conflict", "Deadlock possible", "Relationship damage"],
            NegotiationDynamic.MIXED: ["Unclear expectations", "Misunderstandings likely", "Trust issues"],
        }
        return risks.get(dynamic, [])

    def _identify_opportunities(self, dynamic: NegotiationDynamic) -> List[str]:
        """Identify opportunities in this dynamic"""
        opportunities = {
            NegotiationDynamic.COLLABORATIVE: ["Creative solutions possible", "Strong agreement", "Relationship building"],
            NegotiationDynamic.COMPETITIVE: ["Clear positions", "Efficient negotiation", "No wasted time"],
            NegotiationDynamic.MIXED: ["Flexibility", "Room to explore", "Potential for surprise solutions"],
        }
        return opportunities.get(dynamic, [])

    def generate_dual_coaching(self) -> str:
        """
        Generate coaching for BOTH parties
        What you should do + how to respond to counterparty's style
        """
        user_state = self.user_data.get("emotional_state", "unknown")
        counterparty_readiness = self.counterparty_data.get("readiness_to_agree", "")
        dynamic = self.analyze_interaction_dynamics()
        
        coaching = f"""
🎯 DUAL-PARTY COACHING STRATEGY

YOUR STATE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Emotional: {user_state.upper()}
Ego State: {self.user_data.get('ego_state', 'Unknown')}
Position: {self.user_data.get('life_position', 'Unknown')}

✅ YOUR NEXT MOVE:
- Stay in Adult ego state (logical, problem-solving)
- Lead from "I'm OK/You're OK" position
- Use your communication style strategically


THEIR STATE (Inferred):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Likely Emotions: {', '.join(self.counterparty_data.get('inferred_emotions', {}).keys()) or 'Unknown'}
Ego State: {self.counterparty_data.get('inferred_ego_state', 'Unknown')}
Readiness: {counterparty_readiness}

🎯 HOW TO RESPOND TO THEM:
- Acknowledge their {self.counterparty_data.get('inferred_ego_state', 'state')}
- Match their pace (don't rush if they're cautious)
- Address their concerns specifically


INTERACTION DYNAMIC:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type: {dynamic['dynamic_type'].upper()}
Compatibility: {dynamic['compatibility']}

⚠️ WATCH FOR:
{chr(10).join(['• ' + risk for risk in dynamic.get('risk_factors', [])])}

💡 LEVERAGE:
{chr(10).join(['• ' + opp for opp in dynamic.get('opportunity_factors', [])])}


🚀 STRATEGIC MOVES:
1. Validate their position (builds trust)
2. Ask questions about their needs
3. Propose options that meet both needs
4. Lock in agreement with clear terms
"""
        
        return coaching