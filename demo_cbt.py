"""
Demo driver for SANTINEL psychology framework 1 — CBT (core/cbt_module.py).

Runs CBTAssessment against sample negotiation statements and prints the
cognitive distortions found, the generated CBT intervention, and a full
emotional assessment. This is a manual demo, not a test.

Run from the repo root:
    python demo_cbt.py
"""

import sys

# core/cbt_module.py emits emoji; force UTF-8 so it prints on a cp1252 console.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.cbt_module import CBTAssessment

# (statement, emotions) — emotions feed assess_emotional_state()
SAMPLES = [
    (
        "If I don't close this deal I'm a failure and my whole career is ruined.",
        {"fear": 0.8, "shame": 0.6, "anger": 0.2},
    ),
    (
        "They always lowball me, every time. They think I'm desperate.",
        {"anger": 0.7, "frustration": 0.6},
    ),
    (
        "I should have pushed harder. I must get 20% or it's a total failure.",
        {"regret": 0.7, "anxiety": 0.5},
    ),
    (
        "We're going to lose this client for sure.",
        {"fear": 0.65, "sadness": 0.4},
    ),
    (
        "Their pricing is aggressive, but our value proposition is strong. "
        "Let's focus the next call on ROI and switching cost.",
        {"confidence": 0.7, "calm": 0.6},
    ),
]


def rule(char="=", width=72):
    print(char * width)


def main():
    cbt = CBTAssessment()

    for i, (statement, emotions) in enumerate(SAMPLES, start=1):
        rule()
        print(f"SAMPLE {i}")
        print(f'Statement: "{statement}"')
        print(f"Emotions:  {emotions}")
        rule("-")

        distortions = cbt.identify_distortions(statement)
        if distortions:
            print(f"Distortions found ({len(distortions)}):")
            for d in distortions:
                print(
                    f"  - {d['distortion']:<20} "
                    f"(keyword={d['keyword']!r}, confidence={d['confidence']})"
                )
                print(f"      {d['description']}")
        else:
            print("Distortions found: none")

        print()
        print(cbt.generate_cbt_intervention(distortions, statement).strip())

        print()
        assessment = cbt.assess_emotional_state(statement, emotions)
        print(f"Dominant emotion:  {assessment['dominant_emotion']} "
              f"(intensity {assessment['emotion_intensity']})")
        print(f"Therapeutic insight: {assessment['therapeutic_insight']}")
        print()

    rule()
    print(f"Done. {len(SAMPLES)} samples processed.")


if __name__ == "__main__":
    main()
