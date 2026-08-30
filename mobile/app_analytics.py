# -*- coding: utf-8 -*-
"""
SANTINEL Mobile App Analytics
Performance summary, personality strengths/weaknesses, top/worst scripts.

Lightweight module for mobile app to display key metrics and insights.
Designed for quick rendering and offline support.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PerformanceSummary:
    """High-level performance summary."""
    total_calls: int
    win_rate: float
    avg_effectiveness: float
    top_script: str
    top_personality: str
    streak_wins: int  # Current win streak
    last_updated: str


@dataclass
class ScriptStats:
    """Statistics for a single script."""
    script_id: str
    situation: str
    personality_type: str
    win_rate: float
    uses: int
    effectiveness: float
    status: str  # "hot" (trending up), "stable", "cold" (trending down)


@dataclass
class PersonalityInsight:
    """Insights for a personality type."""
    personality_type: str
    avg_win_rate: float
    best_situation: str
    worst_situation: str
    strength: str
    weakness: str
    recommendation: str


class MobileAnalytics:
    """Mobile-optimized analytics interface."""

    def __init__(self):
        self.cache = {}

    def get_performance_summary(self, analytics_engine) -> PerformanceSummary:
        """Get quick performance summary."""
        snapshot = analytics_engine.get_snapshot("week")

        # Calculate win streak
        streak = 0
        for call in reversed(analytics_engine.call_history[-20:]):  # Last 20 calls
            if call.get("outcome") == "won":
                streak += 1
            else:
                break

        return PerformanceSummary(
            total_calls=snapshot.total_calls,
            win_rate=round(snapshot.win_rate, 3),
            avg_effectiveness=round(snapshot.average_effectiveness, 3),
            top_script=snapshot.top_script_id or "N/A",
            top_personality=snapshot.top_personality_type or "N/A",
            streak_wins=streak,
            last_updated=datetime.now().isoformat(),
        )

    def get_top_scripts(self, analytics_engine, limit: int = 5) -> List[ScriptStats]:
        """Get top performing scripts for mobile display."""
        top_scripts = analytics_engine.get_top_scripts(limit)
        return [
            ScriptStats(
                script_id=s["script_id"],
                situation=s["situation"],
                personality_type=s["personality"],
                win_rate=round(s["win_rate"], 3),
                uses=s["total_uses"],
                effectiveness=round(s["avg_effectiveness"], 3),
                status=s["trending"],
            )
            for s in top_scripts
        ]

    def get_worst_scripts(self, analytics_engine, limit: int = 5) -> List[ScriptStats]:
        """Get worst performing scripts for improvement focus."""
        worst = analytics_engine.get_worst_scripts(limit)
        return [
            ScriptStats(
                script_id=s["script_id"],
                situation=s["situation"],
                personality_type=s["personality"],
                win_rate=round(s["win_rate"], 3),
                uses=s["total_uses"],
                effectiveness=round(s["avg_effectiveness"], 3),
                status="cold",
            )
            for s in worst
        ]

    def get_personality_insights(self, analytics_engine) -> Dict[str, PersonalityInsight]:
        """Get insights for each personality type."""
        analysis = analytics_engine.get_personality_strengths_weaknesses()
        insights = {}

        personality_profiles = {
            "driver": {
                "strength": "Responds to direct, results-focused language",
                "weakness": "May dismiss relationship-building efforts",
                "recommendation": "Use time pressure and urgency tactics; focus on ROI",
            },
            "expressive": {
                "strength": "High energy and enthusiasm are contagious",
                "weakness": "May lack focus on details and data",
                "recommendation": "Tell compelling stories; create excitement; follow up with data",
            },
            "amiable": {
                "strength": "Builds strong relationships and trust",
                "weakness": "Takes longer to make decisions; conflict-averse",
                "recommendation": "Invest time in rapport; multiple touchpoints; emphasize collaboration",
            },
            "analytical": {
                "strength": "Thorough evaluation and due diligence",
                "weakness": "Slow decision-making; may over-analyze",
                "recommendation": "Provide detailed data, metrics, case studies, competitive analysis",
            },
        }

        for personality, data in analysis.items():
            profile = personality_profiles.get(personality, {})
            insights[personality] = PersonalityInsight(
                personality_type=personality.upper(),
                avg_win_rate=round(data.get("avg_win_rate", 0), 3),
                best_situation=data.get("best_situation", "N/A").replace("_", " ").title(),
                worst_situation=data.get("worst_situation", "N/A").replace("_", " ").title(),
                strength=profile.get("strength", ""),
                weakness=profile.get("weakness", ""),
                recommendation=profile.get("recommendation", ""),
            )

        return insights

    def get_action_items(self, analytics_engine) -> List[str]:
        """Get actionable insights for the user."""
        actions = []

        # Check win rate
        snapshot = analytics_engine.get_snapshot("week")
        if snapshot.win_rate > 0.8:
            actions.append("🔥 Hot streak! Keep using your top-performing scripts.")
        elif snapshot.win_rate < 0.5:
            actions.append("📊 Win rate below 50%. Review worst-performing scripts and rotate in new approaches.")

        # Check personality patterns
        patterns = analytics_engine.get_personality_patterns()
        if patterns:
            total_patterns = sum(len(p) for p in patterns.values())
            actions.append(f"🔍 {total_patterns} personality patterns detected. Use these insights to customize your approach.")

        # Check specific scripts
        worst = analytics_engine.get_worst_scripts(1)
        if worst:
            worst_script = worst[0]
            actions.append(
                f"⚠️ Script '{worst_script['script_id']}' underperforming ({worst_script['win_rate']*100:.0f}%). "
                f"Consider alternatives for {worst_script['personality']}."
            )

        top = analytics_engine.get_top_scripts(1)
        if top:
            top_script = top[0]
            actions.append(
                f"✅ Leverage '{top_script['script_id']}' more often—it's {top_script['win_rate']*100:.0f}% effective with {top_script['personality']}"
            )

        # Check framework effectiveness
        frameworks = analytics_engine.get_framework_effectiveness()
        if frameworks and len(frameworks) > 0:
            top_fw = frameworks[0]
            actions.append(
                f"💡 {top_fw['framework'].upper()} framework has {top_fw['close_rate']*100:.0f}% close rate. "
                f"Trust its signals when scoring deals."
            )

        return actions[:5]  # Limit to top 5 actions

    def format_for_display(self, analytics_engine) -> Dict[str, Any]:
        """Format all analytics for mobile app display."""
        return {
            "performance_summary": self.get_performance_summary(analytics_engine).__dict__,
            "top_scripts": [s.__dict__ for s in self.get_top_scripts(analytics_engine)],
            "worst_scripts": [s.__dict__ for s in self.get_worst_scripts(analytics_engine)],
            "personality_insights": {
                k: v.__dict__ for k, v in self.get_personality_insights(analytics_engine).items()
            },
            "action_items": self.get_action_items(analytics_engine),
            "generated_at": datetime.now().isoformat(),
        }

    def format_for_display_bilingual(self, analytics_engine, language: str = "en") -> Dict[str, Any]:
        """Format analytics with bilingual labels."""
        labels = {
            "en": {
                "performance_summary": "Performance Summary",
                "total_calls": "Total Calls",
                "win_rate": "Win Rate",
                "avg_effectiveness": "Avg Effectiveness",
                "top_script": "Top Script",
                "top_personality": "Top Personality",
                "win_streak": "Win Streak",
                "top_scripts": "Top Performing Scripts",
                "worst_scripts": "Worst Performing Scripts",
                "personality_insights": "Personality Insights",
                "action_items": "Action Items",
                "script_id": "Script",
                "situation": "Situation",
                "personality_type": "Personality",
                "uses": "Uses",
                "effectiveness": "Effectiveness",
                "best_situation": "Best Situation",
                "worst_situation": "Worst Situation",
                "strength": "Strength",
                "weakness": "Weakness",
                "recommendation": "Recommendation",
            },
            "ro": {
                "performance_summary": "Rezumatul Performanței",
                "total_calls": "Total Apeluri",
                "win_rate": "Rata Câștig",
                "avg_effectiveness": "Eficacitate Medie",
                "top_script": "Scenariul Superior",
                "top_personality": "Personalitate Superioară",
                "win_streak": "Seria de Câștiguri",
                "top_scripts": "Scenarii cu Performanță Ridicată",
                "worst_scripts": "Scenarii cu Performanță Scăzută",
                "personality_insights": "Perspective asupra Personalității",
                "action_items": "Articole de Acțiune",
                "script_id": "Scenariul",
                "situation": "Situația",
                "personality_type": "Personalitate",
                "uses": "Utilizări",
                "effectiveness": "Eficacitate",
                "best_situation": "Situația Optimă",
                "worst_situation": "Situația Slabă",
                "strength": "Puncte Forte",
                "weakness": "Puncte Slabe",
                "recommendation": "Recomandare",
            },
        }

        t = labels.get(language, labels["en"])

        data = self.format_for_display(analytics_engine)

        return {
            "labels": t,
            "performance_summary": {
                t["total_calls"]: data["performance_summary"]["total_calls"],
                t["win_rate"]: f"{data['performance_summary']['win_rate']*100:.1f}%",
                t["avg_effectiveness"]: f"{data['performance_summary']['avg_effectiveness']:.2f}",
                t["top_script"]: data["performance_summary"]["top_script"],
                t["top_personality"]: data["performance_summary"]["top_personality"],
                t["win_streak"]: data["performance_summary"]["streak_wins"],
            },
            "top_scripts": data["top_scripts"],
            "worst_scripts": data["worst_scripts"],
            "personality_insights": data["personality_insights"],
            "action_items": data["action_items"],
            "generated_at": data["generated_at"],
        }


# Command-line interface for testing
if __name__ == "__main__":
    from core.analytics_engine import AnalyticsEngine

    print("=== SANTINEL MOBILE ANALYTICS ===\n")

    # Create engine with sample data
    engine = AnalyticsEngine()

    test_calls = [
        {
            "call_id": "call-001",
            "script_id": "script_closing_driver",
            "situation": "closing",
            "personality_type": "driver",
            "outcome": "won",
            "coaching_effectiveness": 0.94,
            "duration_seconds": 600,
            "framework_findings": {"ta": {"confidence_score": 0.8}},
            "signals_detected": {"verbal": ["agreement"]},
            "close_probability": 8.5,
        },
        {
            "call_id": "call-002",
            "script_id": "script_objection_amiable",
            "situation": "objection",
            "personality_type": "amiable",
            "outcome": "advanced",
            "coaching_effectiveness": 0.87,
            "duration_seconds": 1200,
            "framework_findings": {"attachment": {"confidence_score": 0.78}},
            "signals_detected": {"vocal": ["warm_tone"]},
            "close_probability": 5.5,
        },
        {
            "call_id": "call-003",
            "script_id": "script_discovery_analytical",
            "situation": "discovery",
            "personality_type": "analytical",
            "outcome": "won",
            "coaching_effectiveness": 0.75,
            "duration_seconds": 1800,
            "framework_findings": {"neuroscience": {"confidence_score": 0.72}},
            "signals_detected": {"verbal": ["questions"]},
            "close_probability": 6.2,
        },
    ]

    for call in test_calls:
        engine.record_call(call)

    # Get mobile analytics
    mobile = MobileAnalytics()

    print("PERFORMANCE SUMMARY (Last 7 days):")
    summary = mobile.get_performance_summary(engine)
    print(f"  Total Calls: {summary.total_calls}")
    print(f"  Win Rate: {summary.win_rate*100:.1f}%")
    print(f"  Avg Effectiveness: {summary.avg_effectiveness:.2f}")
    print(f"  Win Streak: {summary.streak_wins}")

    print("\nTOP SCRIPTS:")
    for script in mobile.get_top_scripts(engine):
        print(f"  {script.script_id}: {script.win_rate*100:.0f}% ({script.uses} uses)")

    print("\nWORST SCRIPTS:")
    for script in mobile.get_worst_scripts(engine):
        print(f"  {script.script_id}: {script.win_rate*100:.0f}% ({script.uses} uses)")

    print("\nPERSONALITY INSIGHTS:")
    insights = mobile.get_personality_insights(engine)
    for pers, insight in insights.items():
        print(f"  {pers}:")
        print(f"    Win Rate: {insight.avg_win_rate*100:.1f}%")
        print(f"    Best: {insight.best_situation}")
        print(f"    Strength: {insight.strength}")

    print("\nACTION ITEMS:")
    for item in mobile.get_action_items(engine):
        print(f"  • {item}")

    print("\nBILINGUAL EXPORT (Romanian):")
    bilingual = mobile.format_for_display_bilingual(engine, "ro")
    print(f"  {bilingual['labels']['performance_summary']}:")
    for key, value in bilingual["performance_summary"].items():
        print(f"    {key}: {value}")
