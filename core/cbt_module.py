"""
CBT (Cognitive Behavioral Therapy) Module for SANTINEL
Identifies cognitive distortions, automatic thoughts, emotions, behaviors
Professional-grade emotional assessment framework
"""

from typing import Dict, List, Tuple
from enum import Enum

class CognitivDistortion(Enum):
    """Common cognitive distortions identified in negotiations"""
    CATASTROPHIZING = "catastrophizing"  # Expecting worst outcome
    BLACK_AND_WHITE = "black_and_white"  # All or nothing thinking
    OVERGENERALIZATION = "overgeneralization"  # One bad event = always happens
    MIND_READING = "mind_reading"  # Assuming you know what other thinks
    FORTUNE_TELLING = "fortune_telling"  # Predicting negative future
    PERSONALIZATION = "personalization"  # Taking others' reactions personally
    FILTERING = "filtering"  # Focusing only on negatives
    EMOTIONAL_REASONING = "emotional_reasoning"  # Feelings = facts
    SHOULD_STATEMENTS = "should_statements"  # Rigid rules
    LABELING = "labeling"  # Negative self-labels

class CBTAssessment:
    """
    CBT Assessment Engine
    Maps: Situation → Automatic Thoughts → Emotions → Behaviors → Consequences
    """
    
    def __init__(self):
        self.distortion_keywords = {
            CognitivDistortion.CATASTROPHIZING: [
                "worst", "disaster", "never", "always fail", "ruined", "impossible"
            ],
            CognitivDistortion.BLACK_AND_WHITE: [
                "either/or", "all or nothing", "perfect", "completely", "total failure"
            ],
            CognitivDistortion.OVERGENERALIZATION: [
                "always", "never", "every time", "everyone", "nobody"
            ],
            CognitivDistortion.MIND_READING: [
                "they think", "they want", "they don't like", "I know they believe"
            ],
            CognitivDistortion.FORTUNE_TELLING: [
                "will fail", "going to lose", "definitely won't", "won't succeed"
            ],
            CognitivDistortion.PERSONALIZATION: [
                "it's my fault", "because of me", "I caused", "my problem"
            ],
            CognitivDistortion.FILTERING: [
                "only bad", "nothing good", "worst part", "ignore the positive"
            ],
            CognitivDistortion.EMOTIONAL_REASONING: [
                "I feel like", "feeling means", "I feel therefore"
            ],
            CognitivDistortion.SHOULD_STATEMENTS: [
                "should", "must", "ought to", "have to", "supposed to"
            ],
            CognitivDistortion.LABELING: [
                "I'm a failure", "I'm stupid", "I'm incompetent", "I'm weak"
            ],
        }

    def identify_distortions(self, user_statement: str) -> List[Dict]:
        """
        Identify cognitive distortions in user's statement
        Returns list of distortions found with confidence scores
        """
        text_lower = user_statement.lower()
        found_distortions = []

        for distortion, keywords in self.distortion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_distortions.append({
                        "distortion": distortion.value,
                        "keyword": keyword,
                        "confidence": 0.8,
                        "description": self._get_distortion_description(distortion)
                    })
                    break

        return found_distortions

    def _get_distortion_description(self, distortion: CognitivDistortion) -> str:
        """Get therapeutic description of distortion"""
        descriptions = {
            CognitivDistortion.CATASTROPHIZING: "Expecting worst-case scenario without evidence",
            CognitivDistortion.BLACK_AND_WHITE: "Seeing situations as entirely good or bad",
            CognitivDistortion.OVERGENERALIZATION: "Making broad conclusions from single events",
            CognitivDistortion.MIND_READING: "Assuming you know what others are thinking",
            CognitivDistortion.FORTUNE_TELLING: "Predicting negative outcomes with certainty",
            CognitivDistortion.PERSONALIZATION: "Blaming yourself for external events",
            CognitivDistortion.FILTERING: "Focusing only on negative details",
            CognitivDistortion.EMOTIONAL_REASONING: "Treating emotions as facts",
            CognitivDistortion.SHOULD_STATEMENTS: "Using rigid rules instead of flexibility",
            CognitivDistortion.LABELING: "Using negative global labels about yourself",
        }
        return descriptions.get(distortion, "Cognitive distortion detected")

    def generate_cbt_intervention(self, distortions: List[Dict], situation: str) -> str:
        """
        Generate CBT-based coaching intervention
        Follows: Identify → Challenge → Reframe → Action
        """
        if not distortions:
            return "No significant cognitive distortions detected. Focus on evidence-based strategy."

        primary_distortion = distortions[0]
        intervention = f"""
CBT COACHING INTERVENTION:

🔍 IDENTIFIED PATTERN: {primary_distortion['distortion'].replace('_', ' ').title()}
   Description: {primary_distortion['description']}

❓ CHALLENGE THE THOUGHT:
   • What evidence supports this thought? What contradicts it?
   • Are you treating a feeling as a fact?
   • What would you tell a friend in this situation?

🔄 REFRAME THE SITUATION:
   • What's a more balanced perspective?
   • What are you overlooking?
   • What's within your control?

✅ ACTION STEP:
   • Focus on facts, not predictions
   • Use "I might..." instead of "I will..."
   • Prepare for multiple outcomes, not just worst-case
"""
        return intervention

    def assess_emotional_state(self, 
                              situation: str, 
                              emotions: Dict[str, float]) -> Dict:
        """
        Comprehensive emotional assessment using CBT framework
        Returns: Situation Analysis → Thoughts → Emotions → Behaviors → Consequences
        """
        distortions = self.identify_distortions(situation)
        
        return {
            "situation": situation,
            "cognitive_distortions": distortions,
            "emotion_intensity": max(emotions.values()) if emotions else 0,
            "dominant_emotion": max(emotions, key=emotions.get) if emotions else "neutral",
            "cbt_intervention": self.generate_cbt_intervention(distortions, situation),
            "therapeutic_insight": self._generate_insight(distortions, emotions),
        }

    def _generate_insight(self, distortions: List[Dict], emotions: Dict) -> str:
        """Generate therapeutic insight from assessment"""
        if not distortions:
            return "You're thinking clearly. Channel this clarity into strategic action."
        
        distortion_count = len(set(d['distortion'] for d in distortions))
        
        if distortion_count >= 3:
            return "Multiple thinking patterns are active. Slow down. Focus on one fact at a time."
        elif distortion_count == 2:
            return "You're experiencing some cognitive distortions. Ground yourself in observable facts."
        else:
            return "One primary thinking pattern detected. Challenge it with evidence."