# -*- coding: utf-8 -*-
"""
SANTINEL Analytics Engine
Tracks coaching effectiveness, personality patterns, framework performance.

Metrics tracked:
- Win/loss rates per script × personality × situation
- Framework contribution to closes (which frameworks predict wins)
- Personality pattern detection (recurring behavioral patterns)
- Signal accuracy (vocal/verbal signals → outcome prediction)
- Coaching effectiveness by situation type
- Script performance heatmaps (16 combinations)
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
from collections import defaultdict


class Personality(Enum):
    """DISC personality types."""
    DRIVER = "driver"
    EXPRESSIVE = "expressive"
    AMIABLE = "amiable"
    ANALYTICAL = "analytical"


class Situation(Enum):
    """Sales situations."""
    COLD_CALL = "cold_call"
    DISCOVERY = "discovery"
    OBJECTION = "objection"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"


class Outcome(Enum):
    """Negotiation outcomes."""
    WON = "won"
    LOST = "lost"
    STALLED = "stalled"
    ADVANCED = "advanced"


@dataclass
class ScriptPerformance:
    """Performance metrics for a script."""
    script_id: str
    situation: str
    personality_type: str
    total_uses: int = 0
    wins: int = 0
    losses: int = 0
    stalled: int = 0
    advanced: int = 0
    avg_effectiveness: float = 0.0
    avg_duration_seconds: int = 0
    signal_accuracy: float = 0.0
    trending: str = "neutral"  # up, down, neutral


@dataclass
class PersonalityPattern:
    """Recurring patterns detected for a personality type."""
    personality_type: str
    pattern_name: str
    frequency: int  # How often observed
    confidence: float  # 0.0-1.0
    description: str
    recommended_approach: str
    success_rate: float


@dataclass
class FrameworkContribution:
    """Framework's contribution to win/loss outcomes."""
    framework_name: str
    triggered_closes: int
    triggered_losses: int
    avg_confidence_when_triggered: float
    correlation_to_win: float  # Pearson correlation to outcome
    correlation_to_loss: float


@dataclass
class SignalAccuracy:
    """Accuracy of vocal/verbal signals in predicting outcomes."""
    signal_type: str  # "verbal", "vocal", "behavioral"
    signal_name: str  # "agreement", "doubt", "urgency", etc.
    true_positives: int  # Signal present + won
    false_positives: int  # Signal present + lost
    true_negatives: int  # Signal absent + lost
    false_negatives: int  # Signal absent + won
    precision: float  # TP / (TP + FP)
    recall: float  # TP / (TP + FN)
    f1_score: float  # Harmonic mean of precision & recall


@dataclass
class AnalyticsSnapshot:
    """Point-in-time analytics snapshot."""
    timestamp: str
    period: str  # "day", "week", "month"
    total_calls: int
    total_wins: int
    total_losses: int
    total_stalled: int
    total_advanced: int
    win_rate: float  # 0.0-1.0
    loss_rate: float
    average_effectiveness: float
    top_script_id: Optional[str] = None
    top_personality_type: Optional[str] = None


class AnalyticsEngine:
    """Central analytics engine for SANTINEL coaching."""

    def __init__(self):
        # Script performance tracking
        self.script_performance: Dict[Tuple[str, str, str], ScriptPerformance] = {}

        # Personality pattern detection
        self.personality_patterns: Dict[str, List[PersonalityPattern]] = defaultdict(list)

        # Framework contribution analysis
        self.framework_contributions: Dict[str, FrameworkContribution] = {}

        # Signal accuracy tracking
        self.signal_accuracy: Dict[str, SignalAccuracy] = {}

        # Call history for retrospective analysis
        self.call_history: List[Dict[str, Any]] = []

        # Aggregated metrics
        self.aggregated_metrics: Dict[str, AnalyticsSnapshot] = {}

    def record_call(self, call_data: Dict[str, Any]) -> bool:
        """Record a coaching call with all associated data."""
        try:
            call_record = {
                "call_id": call_data.get("call_id", f"call-{datetime.now().timestamp()}"),
                "timestamp": call_data.get("timestamp", datetime.now().isoformat()),
                "script_id": call_data.get("script_id"),
                "situation": call_data.get("situation"),
                "personality_type": call_data.get("personality_type"),
                "outcome": call_data.get("outcome"),  # won, lost, stalled, advanced
                "coaching_effectiveness": call_data.get("coaching_effectiveness", 0.0),
                "duration_seconds": call_data.get("duration_seconds", 0),
                "framework_findings": call_data.get("framework_findings", {}),
                "signals_detected": call_data.get("signals_detected", {}),
                "close_probability": call_data.get("close_probability", 0.0),
                "deal_amount": call_data.get("deal_amount", 0.0),
            }

            self.call_history.append(call_record)

            # Update script performance
            self._update_script_performance(call_record)

            # Update framework contribution
            self._update_framework_contribution(call_record)

            # Update signal accuracy
            self._update_signal_accuracy(call_record)

            # Detect personality patterns
            self._detect_personality_patterns(call_record)

            return True
        except Exception as e:
            print(f"Error recording call: {e}")
            return False

    def _update_script_performance(self, call: Dict[str, Any]):
        """Update script performance metrics."""
        key = (
            call.get("script_id", "unknown"),
            call.get("situation", "unknown"),
            call.get("personality_type", "unknown"),
        )

        if key not in self.script_performance:
            self.script_performance[key] = ScriptPerformance(
                script_id=key[0],
                situation=key[1],
                personality_type=key[2],
            )

        perf = self.script_performance[key]
        perf.total_uses += 1

        outcome = call.get("outcome", "stalled").lower()
        if outcome == "won":
            perf.wins += 1
        elif outcome == "lost":
            perf.losses += 1
        elif outcome == "stalled":
            perf.stalled += 1
        elif outcome == "advanced":
            perf.advanced += 1

        # Update average effectiveness
        effectiveness = call.get("coaching_effectiveness", 0.0)
        perf.avg_effectiveness = (
            (perf.avg_effectiveness * (perf.total_uses - 1) + effectiveness) / perf.total_uses
        )

        # Update average duration
        duration = call.get("duration_seconds", 0)
        perf.avg_duration_seconds = (
            (perf.avg_duration_seconds * (perf.total_uses - 1) + duration) // perf.total_uses
        )

        # Determine trend
        if perf.total_uses >= 5:
            recent = self.call_history[-5:]
            recent_wins = sum(1 for c in recent if c.get("outcome") == "won" and c.get("script_id") == key[0])
            earlier = self.call_history[-(10 if len(self.call_history) >= 10 else len(self.call_history))-5:-5]
            earlier_wins = sum(1 for c in earlier if c.get("outcome") == "won" and c.get("script_id") == key[0])

            if recent_wins > earlier_wins:
                perf.trending = "up"
            elif recent_wins < earlier_wins:
                perf.trending = "down"
            else:
                perf.trending = "neutral"

    def _update_framework_contribution(self, call: Dict[str, Any]):
        """Track which frameworks predict wins/losses."""
        outcome = call.get("outcome", "stalled").lower()
        findings = call.get("framework_findings", {})

        for framework_name, framework_result in findings.items():
            if framework_name not in self.framework_contributions:
                self.framework_contributions[framework_name] = FrameworkContribution(
                    framework_name=framework_name,
                    triggered_closes=0,
                    triggered_losses=0,
                    avg_confidence_when_triggered=0.0,
                    correlation_to_win=0.0,
                    correlation_to_loss=0.0,
                )

            fc = self.framework_contributions[framework_name]

            if outcome == "won":
                fc.triggered_closes += 1
            elif outcome == "lost":
                fc.triggered_losses += 1

            # Update confidence
            confidence = framework_result.get("confidence_score", 0.0) if isinstance(framework_result, dict) else 0.0
            fc.avg_confidence_when_triggered = (
                (fc.avg_confidence_when_triggered * max(1, fc.triggered_closes + fc.triggered_losses - 1) + confidence)
                / max(1, fc.triggered_closes + fc.triggered_losses)
            )

    def _update_signal_accuracy(self, call: Dict[str, Any]):
        """Measure accuracy of signals in predicting outcomes."""
        signals = call.get("signals_detected", {})
        outcome = call.get("outcome", "stalled").lower()
        is_win = outcome == "won"

        for signal_type, signal_list in signals.items():
            if not isinstance(signal_list, list):
                signal_list = [signal_list]

            for signal_name in signal_list:
                key = f"{signal_type}_{signal_name}"

                if key not in self.signal_accuracy:
                    self.signal_accuracy[key] = SignalAccuracy(
                        signal_type=signal_type,
                        signal_name=signal_name,
                        true_positives=0,
                        false_positives=0,
                        true_negatives=0,
                        false_negatives=0,
                        precision=0.0,
                        recall=0.0,
                        f1_score=0.0,
                    )

                sa = self.signal_accuracy[key]

                if is_win:
                    sa.true_positives += 1
                else:
                    sa.false_positives += 1

                # Calculate metrics
                tp_fp = sa.true_positives + sa.false_positives
                sa.precision = sa.true_positives / tp_fp if tp_fp > 0 else 0.0

                tp_fn = sa.true_positives + sa.false_negatives
                sa.recall = sa.true_positives / tp_fn if tp_fn > 0 else 0.0

                precision_recall = sa.precision + sa.recall
                sa.f1_score = (2 * sa.precision * sa.recall) / precision_recall if precision_recall > 0 else 0.0

    def _detect_personality_patterns(self, call: Dict[str, Any]):
        """Detect recurring patterns in personality types."""
        personality = call.get("personality_type", "unknown")
        outcome = call.get("outcome", "stalled").lower()
        close_prob = call.get("close_probability", 0.0)
        duration = call.get("duration_seconds", 0)

        # Pattern: Driver personalities often need rapid closing
        if personality == "driver" and outcome == "won" and duration < 900:
            pattern_name = "driver_quick_close"
            self._add_pattern(
                personality,
                pattern_name,
                "Drivers respond to time pressure and rapid closing",
                "Use direct closing language; set urgency with deadlines",
            )

        # Pattern: Amiable personalities need relationship building
        if personality == "amiable" and duration > 1200:
            pattern_name = "amiable_long_engagement"
            self._add_pattern(
                personality,
                pattern_name,
                "Amiables prefer longer conversations to build trust",
                "Invest time in rapport; multiple touchpoints improve outcomes",
            )

        # Pattern: Analytical personalities need data
        if personality == "analytical" and close_prob < 5:
            pattern_name = "analytical_needs_proof"
            self._add_pattern(
                personality,
                pattern_name,
                "Analyticals require comprehensive data before deciding",
                "Provide detailed ROI, metrics, case studies, competitive analysis",
            )

        # Pattern: Expressive personalities respond to energy
        if personality == "expressive" and outcome == "won" and close_prob > 7:
            pattern_name = "expressive_high_energy"
            self._add_pattern(
                personality,
                pattern_name,
                "Expressives close when matched with enthusiasm",
                "Use energetic language, tell stories, create excitement",
            )

    def _add_pattern(self, personality: str, pattern_name: str, description: str, approach: str):
        """Add or update a personality pattern."""
        patterns = self.personality_patterns[personality]

        existing = next((p for p in patterns if p.pattern_name == pattern_name), None)
        if existing:
            existing.frequency += 1
            existing.confidence = min(existing.confidence + 0.05, 1.0)
        else:
            patterns.append(PersonalityPattern(
                personality_type=personality,
                pattern_name=pattern_name,
                frequency=1,
                confidence=0.6,
                description=description,
                recommended_approach=approach,
                success_rate=0.75,
            ))

    def get_script_performance(self, script_id: Optional[str] = None) -> Dict[Tuple[str, str, str], ScriptPerformance]:
        """Get performance metrics for scripts."""
        if script_id:
            return {k: v for k, v in self.script_performance.items() if k[0] == script_id}
        return self.script_performance

    def get_personality_patterns(self, personality_type: Optional[str] = None) -> Dict[str, List[PersonalityPattern]]:
        """Get detected personality patterns."""
        if personality_type:
            return {personality_type: self.personality_patterns.get(personality_type, [])}
        return dict(self.personality_patterns)

    def get_framework_effectiveness(self) -> List[Dict[str, Any]]:
        """Rank frameworks by contribution to wins."""
        rankings = []
        for name, contrib in self.framework_contributions.items():
            total = contrib.triggered_closes + contrib.triggered_losses
            if total > 0:
                win_rate = contrib.triggered_closes / total
                rankings.append({
                    "framework": name,
                    "closes": contrib.triggered_closes,
                    "losses": contrib.triggered_losses,
                    "close_rate": win_rate,
                    "avg_confidence": contrib.avg_confidence_when_triggered,
                })

        return sorted(rankings, key=lambda x: x["close_rate"], reverse=True)

    def get_signal_accuracy_report(self) -> List[Dict[str, Any]]:
        """Get accuracy of all signals in predicting outcomes."""
        signals = []
        for key, sa in self.signal_accuracy.items():
            if sa.true_positives + sa.false_positives > 0:
                signals.append({
                    "signal": key,
                    "precision": round(sa.precision, 3),
                    "recall": round(sa.recall, 3),
                    "f1_score": round(sa.f1_score, 3),
                    "samples": sa.true_positives + sa.false_positives,
                })

        return sorted(signals, key=lambda x: x["f1_score"], reverse=True)

    def get_top_scripts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing scripts."""
        scripts = []
        for (script_id, situation, personality), perf in self.script_performance.items():
            if perf.total_uses > 0:
                win_rate = perf.wins / perf.total_uses
                scripts.append({
                    "script_id": script_id,
                    "situation": situation,
                    "personality": personality,
                    "total_uses": perf.total_uses,
                    "wins": perf.wins,
                    "win_rate": round(win_rate, 3),
                    "avg_effectiveness": round(perf.avg_effectiveness, 3),
                    "trending": perf.trending,
                })

        return sorted(scripts, key=lambda x: x["win_rate"], reverse=True)[:limit]

    def get_worst_scripts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get worst performing scripts (with minimum uses)."""
        scripts = []
        for (script_id, situation, personality), perf in self.script_performance.items():
            if perf.total_uses >= 5:  # Only scripts used at least 5 times
                win_rate = perf.wins / perf.total_uses
                scripts.append({
                    "script_id": script_id,
                    "situation": situation,
                    "personality": personality,
                    "total_uses": perf.total_uses,
                    "wins": perf.wins,
                    "win_rate": round(win_rate, 3),
                    "avg_effectiveness": round(perf.avg_effectiveness, 3),
                    "trending": perf.trending,
                })

        return sorted(scripts, key=lambda x: x["win_rate"])[:limit]

    def get_personality_strengths_weaknesses(self) -> Dict[str, Dict[str, Any]]:
        """Analyze strengths and weaknesses by personality type."""
        analysis = {}

        for personality in ["driver", "expressive", "amiable", "analytical"]:
            scripts = [
                (script_id, situation, perf.wins / perf.total_uses if perf.total_uses > 0 else 0)
                for (script_id, situation, pers), perf in self.script_performance.items()
                if pers == personality and perf.total_uses > 0
            ]

            if scripts:
                avg_win_rate = sum(wr for _, _, wr in scripts) / len(scripts)
                best_situation = sorted(scripts, key=lambda x: x[2], reverse=True)[0][1] if scripts else None
                worst_situation = sorted(scripts, key=lambda x: x[2])[0][1] if scripts else None

                analysis[personality] = {
                    "avg_win_rate": round(avg_win_rate, 3),
                    "best_situation": best_situation,
                    "worst_situation": worst_situation,
                    "patterns": [p.pattern_name for p in self.personality_patterns.get(personality, [])],
                }

        return analysis

    def get_snapshot(self, period: str = "day") -> AnalyticsSnapshot:
        """Get aggregated snapshot for a time period."""
        if not self.call_history:
            return AnalyticsSnapshot(
                timestamp=datetime.now().isoformat(),
                period=period,
                total_calls=0,
                total_wins=0,
                total_losses=0,
                total_stalled=0,
                total_advanced=0,
                win_rate=0.0,
                loss_rate=0.0,
                average_effectiveness=0.0,
            )

        # Filter calls by period
        if period == "day":
            cutoff = datetime.now() - timedelta(days=1)
        elif period == "week":
            cutoff = datetime.now() - timedelta(weeks=1)
        elif period == "month":
            cutoff = datetime.now() - timedelta(days=30)
        else:
            cutoff = datetime.min

        recent_calls = [
            c for c in self.call_history
            if datetime.fromisoformat(c["timestamp"]) > cutoff
        ]

        if not recent_calls:
            recent_calls = self.call_history

        total = len(recent_calls)
        wins = sum(1 for c in recent_calls if c.get("outcome") == "won")
        losses = sum(1 for c in recent_calls if c.get("outcome") == "lost")
        stalled = sum(1 for c in recent_calls if c.get("outcome") == "stalled")
        advanced = sum(1 for c in recent_calls if c.get("outcome") == "advanced")

        avg_effectiveness = sum(c.get("coaching_effectiveness", 0) for c in recent_calls) / total if total > 0 else 0

        top_script = None
        if self.script_performance:
            top_script = max(
                self.script_performance.items(),
                key=lambda x: x[1].wins / x[1].total_uses if x[1].total_uses > 0 else 0,
            )[0][0]

        top_personality = None
        if recent_calls:
            personalities = defaultdict(int)
            for c in recent_calls:
                if c.get("outcome") == "won":
                    personalities[c.get("personality_type", "unknown")] += 1
            if personalities:
                top_personality = max(personalities, key=personalities.get)

        return AnalyticsSnapshot(
            timestamp=datetime.now().isoformat(),
            period=period,
            total_calls=total,
            total_wins=wins,
            total_losses=losses,
            total_stalled=stalled,
            total_advanced=advanced,
            win_rate=wins / total if total > 0 else 0,
            loss_rate=losses / total if total > 0 else 0,
            average_effectiveness=avg_effectiveness,
            top_script_id=top_script,
            top_personality_type=top_personality,
        )

    def get_script_heatmap(self) -> Dict[str, Dict[str, float]]:
        """Generate heatmap of script performance (personality × situation)."""
        heatmap = {
            "driver": {},
            "expressive": {},
            "amiable": {},
            "analytical": {},
        }

        for situation in ["cold_call", "discovery", "objection", "closing", "follow_up"]:
            for personality in ["driver", "expressive", "amiable", "analytical"]:
                key = (f"script_{situation}_{personality}", situation, personality)
                perf = self.script_performance.get(key)
                if perf and perf.total_uses > 0:
                    win_rate = perf.wins / perf.total_uses
                    heatmap[personality][situation] = round(win_rate, 3)
                else:
                    heatmap[personality][situation] = 0.0

        return heatmap

    def export_report(self, filepath: str = "analytics_report.json"):
        """Export full analytics report to JSON."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": asdict(self.get_snapshot("month")),
            "top_scripts": self.get_top_scripts(10),
            "worst_scripts": self.get_worst_scripts(10),
            "framework_effectiveness": self.get_framework_effectiveness(),
            "signal_accuracy": self.get_signal_accuracy_report(),
            "personality_patterns": {
                p: [asdict(pat) for pat in patterns]
                for p, patterns in self.personality_patterns.items()
            },
            "personality_analysis": self.get_personality_strengths_weaknesses(),
            "script_heatmap": self.get_script_heatmap(),
            "total_calls_recorded": len(self.call_history),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return filepath


if __name__ == "__main__":
    # Test analytics engine
    engine = AnalyticsEngine()

    print("=== SANTINEL ANALYTICS ENGINE ===\n")

    # Record sample calls
    test_calls = [
        {
            "call_id": "call-001",
            "script_id": "script_closing_driver",
            "situation": "closing",
            "personality_type": "driver",
            "outcome": "won",
            "coaching_effectiveness": 0.94,
            "duration_seconds": 600,
            "framework_findings": {
                "ta": {"confidence_score": 0.8},
                "ei": {"confidence_score": 0.75},
            },
            "signals_detected": {"verbal": ["agreement"], "vocal": ["high_energy"]},
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
            "framework_findings": {
                "ta": {"confidence_score": 0.85},
                "attachment": {"confidence_score": 0.78},
            },
            "signals_detected": {"verbal": ["hesitation"], "vocal": ["warm_tone"]},
            "close_probability": 5.5,
        },
        {
            "call_id": "call-003",
            "script_id": "script_discovery_analytical",
            "situation": "discovery",
            "personality_type": "analytical",
            "outcome": "stalled",
            "coaching_effectiveness": 0.65,
            "duration_seconds": 1800,
            "framework_findings": {
                "ta": {"confidence_score": 0.7},
                "neuroscience": {"confidence_score": 0.72},
            },
            "signals_detected": {"verbal": ["questions"]},
            "close_probability": 3.2,
        },
    ]

    for call in test_calls:
        engine.record_call(call)

    # Get insights
    print("TOP SCRIPTS:")
    for script in engine.get_top_scripts(5):
        print(f"  {script['script_id']}: {script['win_rate']*100:.1f}% win rate ({script['total_uses']} uses)")

    print("\nFRAMEWORK EFFECTIVENESS:")
    for fw in engine.get_framework_effectiveness():
        print(f"  {fw['framework']}: {fw['close_rate']*100:.1f}% close rate")

    print("\nPERSONALITY ANALYSIS:")
    for pers, analysis in engine.get_personality_strengths_weaknesses().items():
        print(f"  {pers.upper()}: {analysis['avg_win_rate']*100:.1f}% avg win rate")

    print("\nSCRIPT HEATMAP:")
    heatmap = engine.get_script_heatmap()
    print("  COLD_CALL  DISCOVERY  OBJECTION  CLOSING  FOLLOW_UP")
    for personality in ["driver", "expressive", "amiable", "analytical"]:
        rates = [str(heatmap[personality].get(s, 0.0)) for s in ["cold_call", "discovery", "objection", "closing", "follow_up"]]
        print(f"{personality:10} {' '.join(rates)}")

    print("\nSnapshop (Last 30 days):")
    snapshot = engine.get_snapshot("month")
    print(f"  Total Calls: {snapshot.total_calls}")
    print(f"  Win Rate: {snapshot.win_rate*100:.1f}%")
    print(f"  Avg Effectiveness: {snapshot.average_effectiveness:.2f}")
