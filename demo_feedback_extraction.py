# -*- coding: utf-8 -*-
"""
Demo driver for SANTINEL Feedback Extraction framework
(core/feedback_extraction_module.py).

Real-time close probability scoring based on 20+ verbal signals and 15+ vocal signals.
Runs FeedbackExtractionModule.analyze_real_time() over EN + RO negotiation exchanges.

Run from the repo root:
    python demo_feedback_extraction.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.feedback_extraction_module import FeedbackExtractionModule

# (scenario name, your text, their text)
SCENARIOS = [
    (
        "Scenario 1: Strong Agreement Signal",
        "Here's what I'm proposing. Does this work for you?",
        "Yes, absolutely! That sounds perfect. Let's move forward with this.",
    ),
    (
        "Scenario 2: Significant Doubt",
        "The timeline is 3 months. We'll start next week.",
        "I'm not sure about that timeline. It's unclear if we can commit. Maybe eventually.",
    ),
    (
        "Scenario 3: Stalling Behavior",
        "We've covered all the main points. Ready to close?",
        "Actually, I need to think about it. Let me consult with my team first.",
    ),
    (
        "Scenario 4: Budget Negotiation",
        "The investment is $50K per year. That's our best offer.",
        "What's the exact cost breakdown? How much can you negotiate on pricing?",
    ),
    (
        "Scenario 5: Strong Objection",
        "This solution will solve your main problem.",
        "But I'm not comfortable with the implementation. The problem is timing is wrong.",
    ),
    (
        "Scenario 6: Competitive Shopping",
        "We're the best partner for this. Let's finalize terms.",
        "I appreciate it, but we're comparing with other vendors. Exploring other options.",
    ),
    (
        "Scenario 7: Urgency + Enthusiasm",
        "I'm excited about this partnership. Can we start now?",
        "Absolutely! The deadline is coming up soon. We need to move fast. Let's do this!",
    ),
    (
        "Scenario 8: Mixed Signals",
        "Let me clarify our value proposition. Questions?",
        "That's interesting. I'm somewhat interested but hesitant. Tell me more.",
    ),
    (
        "Scenario 9: Low Energy Disengagement",
        "I think this could work well for both of us.",
        "Um... I guess so. I don't know. It's uncertain. Maybe. We'll see.",
    ),
    (
        "Scenario 10: Ready to Close",
        "I believe we have an agreement. Shall we confirm the terms?",
        "Yes, let's do it. I'm in. This works perfectly. Let's move forward!",
    ),
]


def rule(char="=", width=78):
    print(char * width)


def main():
    fem = FeedbackExtractionModule()

    print("\n")
    rule()
    print("REAL-TIME FEEDBACK EXTRACTION & CLOSE PROBABILITY SCORING")
    rule()

    for i, (scenario, your_text, their_text) in enumerate(SCENARIOS, start=1):
        rule()
        print(f"SCENARIO {i}: {scenario}")
        print(f'YOU:  "{your_text}"')
        print(f'THEM: "{their_text}"')
        rule("-")

        r = fem.analyze_real_time(your_text, their_text)

        close_prob = r["close_probability_score"]
        interpretation = r["interpretation"]

        print(f"[CLOSE PROBABILITY] {close_prob}/10")
        print(f"[INTERPRETATION] {interpretation}")
        print()

        print(f"[VERBAL SIGNALS]")
        your_v = r["your_verbals"]
        their_v = r["their_verbals"]
        print(f"  YOU:  agreement={your_v['agreement']} doubt={your_v['doubt']} objection={your_v['objection']} stalling={your_v['stalling']}")
        print(f"  THEM: agreement={their_v['agreement']} doubt={their_v['doubt']} objection={their_v['objection']} stalling={their_v['stalling']}")
        print()

        print(f"[VOCAL SIGNALS]")
        your_vo = r["your_vocals"]
        their_vo = r["their_vocals"]
        print(f"  YOU:  high_energy={your_vo['high_energy']} low_energy={your_vo['low_energy']} hesitation={your_vo['hesitation_pauses']} warm={your_vo['warm_tone']}")
        print(f"  THEM: high_energy={their_vo['high_energy']} low_energy={their_vo['low_energy']} hesitation={their_vo['hesitation_pauses']} warm={their_vo['warm_tone']}")
        print()

        print(f"[COACHING]")
        for line in r["coaching"].split("\n"):
            print(f"  {line}")
        print()

    rule()
    print(f"Completed {len(SCENARIOS)} real-time feedback scenarios.")
    print("\nKEY TAKEAWAYS:")
    print("• Close probability = quantified likelihood of reaching agreement")
    print("• Based on 20+ verbal signals + 15+ vocal signals")
    print("• Updates in real-time as conversation progresses")
    print("• Guides whether to push for close, build understanding, or walk away")


if __name__ == "__main__":
    main()
