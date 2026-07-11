"""
Goal-Based Coaching Engine for SANTINEL
Combines predefined goals + reactive coaching
Provides dual-path coaching: Goal-focused + Situation-responsive
Professional-grade negotiation coaching
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
from datetime import datetime

class GoalType(Enum):
    """Types of negotiation goals"""
    PRICE = "price"                # Price negotiation
    TERMS = "terms"                # Contract terms
    SCOPE = "scope"                # Project scope
    TIMELINE = "timeline"          # Deadlines/timeline
    RELATIONSHIP = "relationship"  # Long-term partnership
    INFORMATION = "information"    # Gathering information
    CUSTOM = "custom"              # User-defined goal

class GoalStatus(Enum):
    """Current status relative to goal"""
    EXCEEDING = "exceeding"        # Doing better than goal
    ON_TRACK = "on_track"          # Meeting goal
    AT_RISK = "at_risk"            # May miss goal
    FAILED = "failed"              # Goal missed

class NegotiationGoal:
    """Represents a single negotiation goal"""
    
    def __init__(self, 
                 goal_type: GoalType,
                 description: str,
                 target_value: str,
                 minimum_acceptable: str,
                 priority: int = 1):
        self.goal_type = goal_type
        self.description = description
        self.target_value = target_value
        self.minimum_acceptable = minimum_acceptable
        self.priority = priority  # 1 = highest priority
        self.current_position = None
        self.status = GoalStatus.ON_TRACK
        self.created_at = datetime.now()

class GoalCoachingEngine:
    """
    Goal-Based Coaching Engine
    Tracks goals + provides reactive coaching aligned with goals
    """
    
    def __init__(self):
        self.goals: List[NegotiationGoal] = []
        self.goal_progress = {}
        self.reactive_situations = []

    def add_goal(self, 
                 goal_type: GoalType,
                 description: str,
                 target_value: str,
                 minimum_acceptable: str,
                 priority: int = 1) -> NegotiationGoal:
        """Add a goal to the negotiation"""
        goal = NegotiationGoal(goal_type, description, target_value, minimum_acceptable, priority)
        self.goals.append(goal)
        self.goals.sort(key=lambda g: g.priority)
        
        return goal

    def add_custom_goal(self, description: str, target: str, minimum: str) -> NegotiationGoal:
        """Add a custom user-defined goal"""
        return self.add_goal(GoalType.CUSTOM, description, target, minimum, priority=1)

    def update_goal_progress(self, goal_index: int, current_position: str) -> Dict:
        """
        Update current progress on a goal
        Returns assessment: exceeding/on_track/at_risk/failed
        """
        if goal_index >= len(self.goals):
            return {"error": "Goal not found"}
        
        goal = self.goals[goal_index]
        goal.current_position = current_position
        
        # Simple assessment (would be more sophisticated in production)
        if current_position == goal.target_value:
            goal.status = GoalStatus.EXCEEDING
        elif current_position == goal.minimum_acceptable:
            goal.status = GoalStatus.ON_TRACK
        else:
            goal.status = GoalStatus.AT_RISK
        
        return {
            "goal": goal.description,
            "status": goal.status.value,
            "current": current_position,
            "target": goal.target_value,
            "minimum": goal.minimum_acceptable,
        }

    def get_goal_coaching(self) -> str:
        """
        Get coaching focused on achieving your goals
        Prioritizes highest-priority goals
        """
        if not self.goals:
            return "No goals defined. Establish your negotiation goals first."
        
        # Sort by priority
        prioritized = sorted(self.goals, key=lambda g: g.priority)
        
        coaching = f"""
🎯 GOAL-FOCUSED COACHING STRATEGY

YOUR PRIMARY GOAL (Priority 1):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{prioritized[0].goal_type.value.upper()}: {prioritized[0].description}
- TARGET: {prioritized[0].target_value}
- ACCEPTABLE MINIMUM: {prioritized[0].minimum_acceptable}
- CURRENT STATUS: {prioritized[0].status.value.upper()}

✅ STRATEGY FOR THIS GOAL:
"""
        
        # Add goal-specific strategies
        coaching += self._get_goal_strategy(prioritized[0].goal_type)
        
        # Add secondary goals if any
        if len(prioritized) > 1:
            coaching += f"""

SECONDARY GOALS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
            for goal in prioritized[1:3]:  # Show top 2 secondary
                coaching += f"""
{goal.goal_type.value.upper()}: {goal.description}
- Target: {goal.target_value} | Minimum: {goal.minimum_acceptable}"""
        
        coaching += f"""

📊 GOAL SCORECARD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 EXCEEDING: Goals better than expected
🟡 ON_TRACK: Meeting minimum goals  
🔴 AT_RISK: Falling behind on goals
⚫ FAILED: Goals not achievable this round

YOUR CURRENT POSITION:
{self._get_goal_status_summary()}
"""
        
        return coaching

    def _get_goal_strategy(self, goal_type: GoalType) -> str:
        """Get strategy tailored to goal type"""
        strategies = {
            GoalType.PRICE: """
1️⃣ ANCHOR FIRST: Propose your target price before they anchor
2️⃣ JUSTIFY VALUE: Explain why your price is justified
3️⃣ OFFER OPTIONS: "Here's the price at standard terms, or X if you can do Y"
4️⃣ KNOW YOUR WALK-AWAY: Never go below minimum acceptable
5️⃣ LINK PRICE TO VALUE: "This price reflects the value you receive"
""",
            GoalType.TERMS: """
1️⃣ DEFINE TERMS FIRST: Establish which terms matter most
2️⃣ BUNDLE TERMS: "I can offer this term IF you agree to that term"
3️⃣ GET THEIR PRIORITIES: Ask which terms matter to them
4️⃣ TRADE TERMS: Trade high-value (for you) for low-value (for them)
5️⃣ DOCUMENT CLEARLY: Get agreement in writing before closing
""",
            GoalType.SCOPE: """
1️⃣ CLARIFY SCOPE: Define exactly what's included vs excluded
2️⃣ USE SCOPE AS LEVERAGE: "Wider scope requires higher price/timeline"
3️⃣ GET AGREEMENT ON SCOPE: Confirm they understand what's included
4️⃣ PROTECT SCOPE: Resist scope creep - "That's additional scope"
5️⃣ BUILD IN CONTINGENCY: Add buffer for scope changes
""",
            GoalType.TIMELINE: """
1️⃣ PROPOSE REALISTIC TIMELINE: Show it's achievable
2️⃣ LINK TIMELINE TO RESOURCES: "This timeline requires these resources"
3️⃣ BUILD IN BUFFER: Add cushion for delays
4️⃣ GET INTERMEDIATE MILESTONES: Break into checkpoints
5️⃣ DOCUMENT TIMELINE CLEARLY: Written schedule prevents disputes
""",
            GoalType.RELATIONSHIP: """
1️⃣ BUILD TRUST FIRST: Small agreements build toward big partnership
2️⃣ SHOW LONG-TERM THINKING: "I see us working together long-term"
3️⃣ RESOLVE DISPUTES FAIRLY: Set precedent for future dealings
4️⃣ COMMUNICATE REGULARLY: Maintain ongoing dialogue
5️⃣ DELIVER ON PROMISES: Build reputation for reliability
""",
            GoalType.INFORMATION: """
1️⃣ ASK OPEN QUESTIONS: "Tell me about your priorities"
2️⃣ LISTEN ACTIVELY: Take notes, show you're interested
3️⃣ ASK FOLLOW-UP QUESTIONS: "What else is important?"
4️⃣ LOOK FOR INTERESTS BEHIND POSITIONS: "Why is that important to you?"
5️⃣ SYNTHESIZE INFORMATION: Summarize what you heard to confirm
""",
            GoalType.CUSTOM: """
Focus on your specific custom goal.
Break it into smaller milestones.
Measure progress toward the goal regularly.
Adjust strategy if goal becomes at-risk.
"""
        }
        
        return strategies.get(goal_type, "Focus on your goal strategically.")

    def _get_goal_status_summary(self) -> str:
        """Summarize status of all goals"""
        if not self.goals:
            return "No goals tracked"
        
        summary = ""
        for i, goal in enumerate(self.goals, 1):
            status_emoji = {
                GoalStatus.EXCEEDING: "🟢",
                GoalStatus.ON_TRACK: "🟡",
                GoalStatus.AT_RISK: "🔴",
                GoalStatus.FAILED: "⚫",
            }.get(goal.status, "⚪")
            
            summary += f"\n{status_emoji} #{i} ({goal.goal_type.value}): {goal.status.value}"
        
        return summary

    def get_reactive_coaching(self, situation: str) -> str:
        """
        Provide reactive coaching for current situation
        Aligned with your goals but responsive to what's happening NOW
        """
        coaching = f"""
⚡ REACTIVE COACHING FOR CURRENT SITUATION

SITUATION: {situation}

🎯 GOAL-ALIGNED RESPONSE:
"""
        
        # Show how current situation relates to goals
        for i, goal in enumerate(self.goals):
            goal_relevance = self._assess_situation_relevance(situation, goal)
            if goal_relevance > 0.5:
                coaching += f"""
Goal #{i+1} ({goal.goal_type.value}):
{self._get_situational_response(situation, goal)}
"""
        
        coaching += """

✅ IMMEDIATE ACTIONS:
1. Stay calm and grounded (return to Adult ego state)
2. Listen for their underlying interests
3. Clarify what they actually need
4. Propose options that meet BOTH needs + your goals
5. Confirm agreement before moving forward
"""
        
        return coaching

    def _assess_situation_relevance(self, situation: str, goal: NegotiationGoal) -> float:
        """How relevant is this situation to the goal?"""
        situation_lower = situation.lower()
        goal_lower = goal.description.lower()
        
        # Simple keyword matching (production would be more sophisticated)
        relevant_words = goal_lower.split()
        matches = sum(1 for word in relevant_words if len(word) > 3 and word in situation_lower)
        
        return matches / max(len(relevant_words), 1)

    def _get_situational_response(self, situation: str, goal: NegotiationGoal) -> str:
        """Get response specific to this situation"""
        return f"""
Target: {goal.target_value}
Minimum: {goal.minimum_acceptable}

In this situation:
- Reference your goal: "{goal.description}"
- Listen to what they're saying about this
- Propose how both sides can win on this
- Check: Does this move you toward your goal?
"""

    def get_dual_coaching(self, situation: str) -> str:
        """
        Combine goal-focused + reactive coaching
        Best of both strategies
        """
        goal_coaching = self.get_goal_coaching()
        reactive_coaching = self.get_reactive_coaching(situation)
        
        return f"""
🎯 COMBINED GOAL + REACTIVE COACHING

{goal_coaching}

⚡ RESPONDING TO CURRENT SITUATION:
{reactive_coaching}

🔄 INTEGRATION:
- Your goals guide the big picture
- Reactive coaching handles this moment
- Together: Strategic agility
"""