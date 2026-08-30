# -*- coding: utf-8 -*-
"""
Demo driver for SANTINEL Sales Scripts framework (core/sales_scripts_module.py).

Demonstrates script selection based on:
- Sales situation (cold outreach, pitch, objection, negotiation, closing)
- Personality type (driver, expressive, amiable, analytical)
- Emotional state and framework signals
- Real-time counter-response to objections

Run from the repo root:
    python demo_sales_scripts.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.sales_scripts_module import SalesScriptsModule

# Demo scenarios
SCENARIOS = [
    {
        "name": "Cold Outreach to a Driver (Direct, Results-Oriented)",
        "category": "cold_outreach",
        "personality": "driver",
        "framework_signals": {"tags": ["game_theory_coordination", "ei_social_skills"]},
        "language": "en",
    },
    {
        "name": "Initial Pitch to an Analytical Prospect",
        "category": "initial_pitch",
        "personality": "analytical",
        "framework_signals": {"tags": ["behavioral_econ_framing", "game_theory_coordination"]},
        "language": "en",
    },
    {
        "name": "Objection Handling: Price Concern",
        "category": "objection_handling",
        "personality": "analytical",
        "framework_signals": {"tags": ["ta_adult_dialogue", "behavioral_econ_loss_aversion"]},
        "language": "en",
    },
    {
        "name": "Negotiation with an Amiable Prospect",
        "category": "negotiation",
        "personality": "amiable",
        "framework_signals": {"tags": ["attachment_secure", "narrative_collaborative"]},
        "language": "en",
    },
    {
        "name": "Closing with a Driver",
        "category": "closing",
        "personality": "driver",
        "framework_signals": {"tags": ["ta_adult_directness", "game_theory_commitment"]},
        "language": "en",
    },
    {
        "name": "Cold Outreach în limba Română (Driver)",
        "category": "cold_outreach",
        "personality": "driver",
        "framework_signals": {"tags": ["game_theory_coordination", "ei_social_skills"]},
        "language": "ro",
    },
]


def rule(char="=", width=78):
    print(char * width)


def main():
    ssm = SalesScriptsModule()

    print("\n")
    rule()
    print("SALES SCRIPTS SELECTION ALGORITHM DEMO")
    rule()

    for i, scenario in enumerate(SCENARIOS, start=1):
        rule()
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"Category: {scenario['category']}")
        print(f"Personality Type: {scenario['personality']}")
        print(f"Language: {scenario['language'].upper()}")
        rule("-")

        # Select best script
        result = ssm.select_script(
            category=scenario["category"],
            personality_type=scenario["personality"],
            framework_signals=scenario["framework_signals"],
            language=scenario["language"],
        )

        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            script = result["selected_script"]
            print(f"[SELECTED SCRIPT]")
            print(f"  ID: {script.get('id')}")
            print(f"  Situation: {script.get('situation')}")
            print(f"  Confidence: {result['confidence_score']:.2f}/1.0")
            print(f"  Effectiveness (historical): {script.get('effectiveness'):.0%}")
            print()
            print(f"[SCRIPT]")
            print(f"  {script.get('script')}")
            print()
            print(f"[WHY THIS SCRIPT]")
            print(f"  {result['why_selected']}")
            print()

            # Show counter-response if objection handling
            if scenario["category"] == "objection_handling":
                print(f"[COUNTER-RESPONSES IF OBJECTED]")
                counter_responses = ssm.get_counter_responses("price", scenario["language"])
                for counter in counter_responses[:2]:
                    print(f"  Option {counter['rank']}: {counter['response']}")
                    print(f"            Effectiveness: {counter['effectiveness']:.0%}")
                print()

    rule()
    print("\nKEY INSIGHTS:")
    print("• Scripts are templates, not rigid memorization")
    print("• Selection algorithm matches personality + situation + frameworks")
    print("• Effectiveness scores are from real-world data")
    print("• Counter-responses are ranked by proven effectiveness")
    print("• Scripts adapt based on emotional state and framework signals")


if __name__ == "__main__":
    main()
