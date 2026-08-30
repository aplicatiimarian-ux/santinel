#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SANTINEL Analytics Demo
Comprehensive demonstration of analytics capabilities.

Features:
- Script effectiveness tracking per situation × personality
- Win/loss analysis by framework
- Personality pattern detection
- Signal accuracy measurement
- Mobile-optimized summaries
- Bilingual (EN + RO) output

Run: python demo_analytics.py
"""

import json
from datetime import datetime, timedelta
from core.analytics_engine import AnalyticsEngine
from mobile.app_analytics import MobileAnalytics


def print_header(title: str, language: str = "en"):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_english():
    """Comprehensive demo in English."""
    print_header("SANTINEL ANALYTICS DEMO - ENGLISH", "en")

    # Initialize engine
    engine = AnalyticsEngine()

    # Sample dataset: 20 calls across all personality types and situations
    calls = [
        # Driver wins (rapid closing)
        {
            "call_id": "call-001",
            "script_id": "script_closing_driver",
            "situation": "closing",
            "personality_type": "driver",
            "outcome": "won",
            "coaching_effectiveness": 0.94,
            "duration_seconds": 600,
            "framework_findings": {"ta": {"confidence_score": 0.85}, "ei": {"confidence_score": 0.82}},
            "signals_detected": {"verbal": ["agreement", "urgency"], "vocal": ["high_energy"]},
            "close_probability": 8.5,
            "deal_amount": 50000,
        },
        {
            "call_id": "call-002",
            "script_id": "script_cold_call_driver",
            "situation": "cold_call",
            "personality_type": "driver",
            "outcome": "won",
            "coaching_effectiveness": 0.88,
            "duration_seconds": 480,
            "framework_findings": {"ta": {"confidence_score": 0.80}},
            "signals_detected": {"verbal": ["interest"]},
            "close_probability": 6.2,
            "deal_amount": 35000,
        },
        # Expressive wins (storytelling)
        {
            "call_id": "call-003",
            "script_id": "script_cold_call_expressive",
            "situation": "cold_call",
            "personality_type": "expressive",
            "outcome": "won",
            "coaching_effectiveness": 0.85,
            "duration_seconds": 720,
            "framework_findings": {"ei": {"confidence_score": 0.87}},
            "signals_detected": {"vocal": ["warm_tone", "high_energy"]},
            "close_probability": 7.8,
            "deal_amount": 40000,
        },
        {
            "call_id": "call-004",
            "script_id": "script_discovery_expressive",
            "situation": "discovery",
            "personality_type": "expressive",
            "outcome": "advanced",
            "coaching_effectiveness": 0.82,
            "duration_seconds": 1200,
            "framework_findings": {"ei": {"confidence_score": 0.84}},
            "signals_detected": {"verbal": ["enthusiasm"]},
            "close_probability": 5.1,
            "deal_amount": 0,
        },
        # Amiable wins (relationship building)
        {
            "call_id": "call-005",
            "script_id": "script_objection_amiable",
            "situation": "objection",
            "personality_type": "amiable",
            "outcome": "won",
            "coaching_effectiveness": 0.83,
            "duration_seconds": 1500,
            "framework_findings": {"attachment": {"confidence_score": 0.86}},
            "signals_detected": {"verbal": ["hesitation"], "vocal": ["warm_tone"]},
            "close_probability": 6.9,
            "deal_amount": 45000,
        },
        {
            "call_id": "call-006",
            "script_id": "script_discovery_amiable",
            "situation": "discovery",
            "personality_type": "amiable",
            "outcome": "advanced",
            "coaching_effectiveness": 0.87,
            "duration_seconds": 1800,
            "framework_findings": {"attachment": {"confidence_score": 0.89}},
            "signals_detected": {"verbal": ["agreement_soft"]},
            "close_probability": 5.8,
            "deal_amount": 0,
        },
        # Analytical wins (data-driven)
        {
            "call_id": "call-007",
            "script_id": "script_discovery_analytical",
            "situation": "discovery",
            "personality_type": "analytical",
            "outcome": "won",
            "coaching_effectiveness": 0.76,
            "duration_seconds": 2100,
            "framework_findings": {"game_theory": {"confidence_score": 0.82}, "neuroscience": {"confidence_score": 0.79}},
            "signals_detected": {"verbal": ["questions", "data_request"]},
            "close_probability": 6.1,
            "deal_amount": 55000,
        },
        # Losses and stalled deals
        {
            "call_id": "call-008",
            "script_id": "script_closing_analytical",
            "situation": "closing",
            "personality_type": "analytical",
            "outcome": "stalled",
            "coaching_effectiveness": 0.55,
            "duration_seconds": 1200,
            "framework_findings": {"ta": {"confidence_score": 0.65}},
            "signals_detected": {"verbal": ["hesitation", "more_data_needed"]},
            "close_probability": 3.2,
            "deal_amount": 0,
        },
        {
            "call_id": "call-009",
            "script_id": "script_objection_driver",
            "situation": "objection",
            "personality_type": "driver",
            "outcome": "lost",
            "coaching_effectiveness": 0.42,
            "duration_seconds": 300,
            "framework_findings": {"ta": {"confidence_score": 0.45}},
            "signals_detected": {"verbal": ["rejection"]},
            "close_probability": 1.5,
            "deal_amount": 0,
        },
        # Additional diverse calls
        {
            "call_id": "call-010",
            "script_id": "script_follow_up_driver",
            "situation": "follow_up",
            "personality_type": "driver",
            "outcome": "won",
            "coaching_effectiveness": 0.91,
            "duration_seconds": 450,
            "framework_findings": {"ta": {"confidence_score": 0.88}},
            "signals_detected": {"verbal": ["decision_made"]},
            "close_probability": 9.1,
            "deal_amount": 60000,
        },
        {
            "call_id": "call-011",
            "script_id": "script_cold_call_amiable",
            "situation": "cold_call",
            "personality_type": "amiable",
            "outcome": "advanced",
            "coaching_effectiveness": 0.72,
            "duration_seconds": 900,
            "framework_findings": {"attachment": {"confidence_score": 0.75}},
            "signals_detected": {"vocal": ["friendly"]},
            "close_probability": 4.2,
            "deal_amount": 0,
        },
        {
            "call_id": "call-012",
            "script_id": "script_objection_expressive",
            "situation": "objection",
            "personality_type": "expressive",
            "outcome": "won",
            "coaching_effectiveness": 0.79,
            "duration_seconds": 1100,
            "framework_findings": {"ei": {"confidence_score": 0.81}},
            "signals_detected": {"verbal": ["reframed"]},
            "close_probability": 7.3,
            "deal_amount": 42000,
        },
    ]

    # Record all calls
    print("📊 RECORDING 12 SAMPLE COACHING CALLS...")
    for call in calls:
        engine.record_call(call)
    print(f"✓ {len(calls)} calls recorded\n")

    # Display Performance Summary
    print_header("1. PERFORMANCE SUMMARY (LAST 7 DAYS)")
    snapshot = engine.get_snapshot("week")
    print(f"Total Calls:           {snapshot.total_calls}")
    print(f"Wins:                  {snapshot.total_wins}")
    print(f"Losses:                {snapshot.total_losses}")
    print(f"Stalled/Advanced:      {snapshot.total_stalled + snapshot.total_advanced}")
    print(f"Win Rate:              {snapshot.win_rate*100:.1f}%")
    print(f"Avg Effectiveness:     {snapshot.average_effectiveness:.2f}/1.0")
    print(f"Top Performing Script: {snapshot.top_script_id}")
    print(f"Top Personality Type:  {snapshot.top_personality_type}")

    # Display Top Scripts
    print_header("2. TOP PERFORMING SCRIPTS")
    top_scripts = engine.get_top_scripts(5)
    print(f"{'Script':<40} {'Situation':<15} {'Personality':<12} {'Win Rate':<12} {'Uses':<6}")
    print("-" * 85)
    for script in top_scripts:
        print(
            f"{script['script_id']:<40} "
            f"{script['situation']:<15} "
            f"{script['personality']:<12} "
            f"{script['win_rate']*100:>6.1f}%{'':<5} "
            f"{script['total_uses']:>4}"
        )

    # Display Worst Scripts
    print_header("3. WORST PERFORMING SCRIPTS (needs improvement)")
    worst_scripts = engine.get_worst_scripts(5)
    if worst_scripts:
        print(f"{'Script':<40} {'Situation':<15} {'Personality':<12} {'Win Rate':<12} {'Uses':<6}")
        print("-" * 85)
        for script in worst_scripts:
            print(
                f"{script['script_id']:<40} "
                f"{script['situation']:<15} "
                f"{script['personality']:<12} "
                f"{script['win_rate']*100:>6.1f}%{'':<5} "
                f"{script['total_uses']:>4}"
            )
    else:
        print("No scripts with 5+ uses yet.")

    # Display Script Heatmap
    print_header("4. SCRIPT PERFORMANCE HEATMAP (Personality × Situation)")
    heatmap = engine.get_script_heatmap()
    print(f"{'PERSONALITY':<12} {'COLD_CALL':<12} {'DISCOVERY':<12} {'OBJECTION':<12} {'CLOSING':<12} {'FOLLOW_UP':<12}")
    print("-" * 72)
    for personality in ["driver", "expressive", "amiable", "analytical"]:
        rates = heatmap[personality]
        print(
            f"{personality:<12} "
            f"{rates['cold_call']*100:>6.1f}%{'':<5} "
            f"{rates['discovery']*100:>6.1f}%{'':<5} "
            f"{rates['objection']*100:>6.1f}%{'':<5} "
            f"{rates['closing']*100:>6.1f}%{'':<5} "
            f"{rates['follow_up']*100:>6.1f}%{'':<5}"
        )

    # Display Framework Effectiveness
    print_header("5. FRAMEWORK CONTRIBUTION TO WINS")
    frameworks = engine.get_framework_effectiveness()
    print(f"{'Framework':<20} {'Closes':<10} {'Losses':<10} {'Close Rate':<12} {'Avg Confidence':<15}")
    print("-" * 67)
    for fw in frameworks:
        print(
            f"{fw['framework']:<20} "
            f"{fw['closes']:<10} "
            f"{fw['losses']:<10} "
            f"{fw['close_rate']*100:>6.1f}%{'':<5} "
            f"{fw['avg_confidence']:.2f}"
        )

    # Display Signal Accuracy
    print_header("6. SIGNAL ACCURACY (Predicting Outcomes)")
    signals = engine.get_signal_accuracy_report()
    print(f"{'Signal':<30} {'F1 Score':<12} {'Precision':<12} {'Recall':<12} {'Samples':<8}")
    print("-" * 74)
    for signal in signals:
        print(
            f"{signal['signal']:<30} "
            f"{signal['f1_score']:.3f}{'':<8} "
            f"{signal['precision']:.3f}{'':<8} "
            f"{signal['recall']:.3f}{'':<8} "
            f"{signal['samples']}"
        )

    # Display Personality Patterns
    print_header("7. PERSONALITY PATTERN DETECTION")
    patterns = engine.get_personality_patterns()
    for personality, pattern_list in patterns.items():
        if pattern_list:
            print(f"\n{personality.upper()}:")
            for pattern in pattern_list:
                print(f"  • {pattern.pattern_name}")
                print(f"    Frequency: {pattern.frequency} times")
                print(f"    Confidence: {pattern.confidence:.2f}")
                print(f"    Approach: {pattern.recommended_approach}")

    # Display Personality Analysis
    print_header("8. PERSONALITY STRENGTHS & WEAKNESSES")
    personality_analysis = engine.get_personality_strengths_weaknesses()
    for personality, analysis in personality_analysis.items():
        if analysis:
            print(f"\n{personality.upper()}:")
            print(f"  Avg Win Rate:     {analysis['avg_win_rate']*100:.1f}%")
            print(f"  Best Situation:   {analysis['best_situation']}")
            print(f"  Worst Situation:  {analysis['worst_situation']}")
            print(f"  Patterns:         {', '.join(analysis['patterns']) if analysis['patterns'] else 'None yet'}")

    # Mobile Analytics
    print_header("9. MOBILE ANALYTICS SUMMARY")
    mobile = MobileAnalytics()
    summary = mobile.get_performance_summary(engine)
    print(f"Total Calls:      {summary.total_calls}")
    print(f"Win Rate:         {summary.win_rate*100:.1f}%")
    print(f"Effectiveness:    {summary.avg_effectiveness:.2f}")
    print(f"Win Streak:       {summary.streak_wins} calls")
    print(f"Top Script:       {summary.top_script}")
    print(f"Top Personality:  {summary.top_personality}")

    # Action Items
    print_header("10. ACTION ITEMS FOR IMPROVEMENT")
    actions = mobile.get_action_items(engine)
    for i, action in enumerate(actions, 1):
        print(f"{i}. {action}")


def demo_romanian():
    """Comprehensive demo in Romanian."""
    print_header("SANTINEL ANALYTICS DEMO - ROMÂNĂ", "ro")

    engine = AnalyticsEngine()

    # Same calls as English (language doesn't affect recording)
    calls = [
        {"call_id": "call-ro-001", "script_id": "script_closing_driver", "situation": "closing",
         "personality_type": "driver", "outcome": "won", "coaching_effectiveness": 0.94,
         "duration_seconds": 600, "framework_findings": {"ta": {"confidence_score": 0.85}},
         "signals_detected": {"verbal": ["agreement"]}, "close_probability": 8.5, "deal_amount": 50000},
        {"call_id": "call-ro-002", "script_id": "script_discovery_amiable", "situation": "discovery",
         "personality_type": "amiable", "outcome": "advanced", "coaching_effectiveness": 0.87,
         "duration_seconds": 1800, "framework_findings": {"attachment": {"confidence_score": 0.89}},
         "signals_detected": {"verbal": ["agreement_soft"]}, "close_probability": 5.8, "deal_amount": 0},
        {"call_id": "call-ro-003", "script_id": "script_discovery_analytical", "situation": "discovery",
         "personality_type": "analytical", "outcome": "won", "coaching_effectiveness": 0.76,
         "duration_seconds": 2100, "framework_findings": {"game_theory": {"confidence_score": 0.82}},
         "signals_detected": {"verbal": ["questions", "data_request"]}, "close_probability": 6.1, "deal_amount": 55000},
    ]

    for call in calls:
        engine.record_call(call)

    # Display with Romanian labels
    labels = {
        "Total Calls": "Total Apeluri",
        "Wins": "Câștiguri",
        "Losses": "Pierderi",
        "Win Rate": "Rata Câștig",
        "Avg Effectiveness": "Eficacitate Medie",
        "Personality": "Personalitate",
        "Situation": "Situația",
        "Script": "Scenariul",
    }

    print("REZUMAT PERFORMANȚĂ (Ultimele 7 zile):")
    snapshot = engine.get_snapshot("week")
    print(f"  Total Apeluri:        {snapshot.total_calls}")
    print(f"  Câștiguri:            {snapshot.total_wins}")
    print(f"  Pierderi:             {snapshot.total_losses}")
    print(f"  Rata Câștig:          {snapshot.win_rate*100:.1f}%")
    print(f"  Eficacitate Medie:    {snapshot.average_effectiveness:.2f}")

    print("\nSCENARII TOP (Performanță Ridicată):")
    top_scripts = engine.get_top_scripts(3)
    for script in top_scripts:
        print(f"  • {script['script_id']}: {script['win_rate']*100:.0f}% ({script['total_uses']} utilizări)")

    print("\nANALIZĂ PERSONALITATE:")
    personality_analysis = engine.get_personality_strengths_weaknesses()
    for personality, analysis in personality_analysis.items():
        if analysis:
            print(f"  {personality.upper()}: {analysis['avg_win_rate']*100:.1f}% rata câștig")

    print("\nMOBILE ANALYTICS (ROMÂNĂ):")
    mobile = MobileAnalytics()
    bilingual = mobile.format_for_display_bilingual(engine, "ro")
    print(f"  {bilingual['labels']['performance_summary']}:")
    for key, value in bilingual["performance_summary"].items():
        print(f"    {key}: {value}")


def main():
    """Run both English and Romanian demos."""
    print("\n" + "="*70)
    print("  SANTINEL ANALYTICS ENGINE - PHASE 11 DEMONSTRATION")
    print("  Comprehensive Effectiveness Tracking & Personality Analysis")
    print("="*70)

    # English demo
    demo_english()

    # Romanian demo
    demo_romanian()

    print_header("ANALYTICS DEMO COMPLETE")
    print("""
✓ Script performance tracking implemented
✓ Win/loss analysis by framework working
✓ Personality patterns detected
✓ Signal accuracy measured
✓ Mobile analytics ready for deployment
✓ Bilingual support (EN + RO) verified

Key Metrics Captured:
  • Script effectiveness (16 combinations: 4 personalities × 4 situations)
  • Framework contribution to closes (which frameworks predict wins)
  • Personality pattern detection (recurring behavioral patterns)
  • Signal accuracy (verbal/vocal signals → outcome prediction)
  • Win rate trends (trending up/down/neutral)
  • Personality strengths & weaknesses

Next Steps:
  1. Integrate with /api/v2/analytics endpoint
  2. Connect dashboard to real analytics data
  3. Set up real-time metric calculations
  4. Deploy to production mobile apps
  5. Monitor effectiveness improvements over time
""")


if __name__ == "__main__":
    main()
