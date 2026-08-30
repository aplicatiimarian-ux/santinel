# -*- coding: utf-8 -*-
"""
Demo: SANTINEL Unified Coach - Integration Testing
Demonstrates orchestration of all 10 frameworks on 5 complex real-world scenarios.

Each scenario requires deep multi-lens analysis and synthesis.

Run from repo root:
    python demo_unified_coach.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.santinel_unified_coach import SantinelUnifiedCoach

# 5 complex real-world negotiation scenarios
SCENARIOS = [
    {
        "name": "Scenario 1: Anxious Prospect with Loss Aversion + Competitive Concerns",
        "your_text": "I understand you're concerned about risk. That's smart. Let me show you how we've de-risked this for clients.",
        "their_text": "I'm worried about making the wrong choice. What if this doesn't work? I've seen other vendors fail. And honestly, they're cheaper. What if I'm throwing money away?",
    },
    {
        "name": "Scenario 2: Avoidant Decision-Maker + Status Quo Bias + Budget Pressure",
        "your_text": "The business case is clear. But I sense you're hesitant. What's holding you back?",
        "their_text": "I need to think about it. Our current system works fine. Why fix what isn't broken? And frankly, budget is tight this quarter. I can't commit to new spending right now.",
    },
    {
        "name": "Scenario 3: Dominant Personality + Zero-Sum Framing + Competitive Objections",
        "your_text": "Here's what makes us different. We're not trying to beat your current vendor—we're trying to help you optimize.",
        "their_text": "I appreciate it, but frankly, I'm shopping around. Your competitor offered X and Y. They're also cheaper. I need to see why I should pick you. Why shouldn't I just go with them?",
    },
    {
        "name": "Scenario 4: Secure Attachment + High Engagement + Ready to Close (But Needs Final Reassurance)",
        "your_text": "I think we've covered everything. You've said yes to the features, the pricing, and the timeline. Does this feel right to you?",
        "their_text": "Yes, actually. I'm excited about this. I trust you. I'm comfortable moving forward. I just want to make sure we have a clear implementation plan and support afterward. Can you walk me through that?",
    },
    {
        "name": "Scenario 5: Complex Multi-Framework Conflict - Victim Narrative + Disorganized Attachment + High Threat + Questions Signaling Interest",
        "your_text": "I know you've been burned before. But we're different. Tell me what would make you feel safe.",
        "their_text": "I don't know. Everything I've tried has failed. People promise but don't deliver. My heart is racing just thinking about committing to another vendor. But... I do have questions. Like, how would implementation work? And what if something goes wrong?",
    },
]


def rule(char="=", width=78):
    print(char * width)


def print_framework_finding(framework_name: str, finding: dict, indent="  "):
    """Pretty-print a framework finding."""
    if not finding:
        return
    print(f"{indent}[{framework_name.upper()}]")
    if isinstance(finding, dict):
        for key, value in list(finding.items())[:3]:  # Show first 3 items
            if isinstance(value, (dict, list)):
                print(f"{indent}  {key}: [complex]")
            else:
                print(f"{indent}  {key}: {value}")


def main():
    coach = SantinelUnifiedCoach()

    print("\n")
    rule()
    print("SANTINEL UNIFIED COACH: INTEGRATION TEST")
    print("All 10 frameworks orchestrated in parallel")
    rule()

    for i, scenario in enumerate(SCENARIOS, start=1):
        rule()
        print(f"SCENARIO {i}: {scenario['name']}")
        rule("-")

        print(f"\nYOU:  '{scenario['your_text']}'")
        print(f"THEM: '{scenario['their_text']}'")
        rule("-")

        # Run unified analysis
        result = coach.analyze_unified(scenario["your_text"], scenario["their_text"])

        # Print synthesis
        print("\n[UNIFIED NERVOUS SYSTEM READING]")
        synthesis = result["synthesis"]
        for key, value in synthesis.items():
            print(f"  {key}: {value}")

        # Print close probability
        print(f"\n[CLOSE PROBABILITY] {result['close_probability']:.1f}/10")

        # Print conflicts and synergies
        if result["conflicts"]:
            print(f"\n[CONFLICTS]")
            for conflict in result["conflicts"]:
                print(f"  ⚠ {conflict}")

        if result["synergies"]:
            print(f"\n[SYNERGIES]")
            for synergy in result["synergies"]:
                print(f"  ✓ {synergy}")

        # Print integrated coaching (top moves)
        print(f"\n[INTEGRATED COACHING - NEXT MOVES]")
        for i, move in enumerate(result["next_moves"][:3], start=1):
            print(f"  {i}. {move}")

        print()

    rule()
    print("\nINTEGRATION TEST COMPLETE")
    print("\nKey Insights:")
    print("• All 10 frameworks run in parallel")
    print("• Synthesis creates unified 'nervous system' reading")
    print("• Conflicts detected when frameworks disagree")
    print("• Synergies identified when frameworks align")
    print("• Top 3-5 moves prioritized for immediate action")
    print("• Each move cites supporting frameworks")


if __name__ == "__main__":
    main()
