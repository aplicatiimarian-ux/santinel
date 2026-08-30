# -*- coding: utf-8 -*-
"""
Demo driver for SANTINEL Behavioral Economics framework (core/behavioral_econ_module.py).

Runs BehavioralEconomicsModule.analyze() and dual_speaker_bias_analysis() over
EN + RO negotiation lines, each chosen to exercise one cognitive bias: loss aversion,
anchoring, sunk cost fallacy, framing effect, status quo bias, and availability heuristic.
Manual demo, not a test.

Run from the repo root:
    python demo_behavioral_econ.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.behavioral_econ_module import BehavioralEconomicsModule

# (target, statement)
SINGLE_SAMPLES = [
    ("bias: Loss Aversion (EN)",
     "The risk is too high. We can't afford to lose money on this. What if it fails?"),
    ("bias: Anchoring (RO)",
     "Cifra pe care vorbim trebuie să fie 50 mii. Asta e primul număr și nu mă mișc de acolo."),
    ("bias: Sunk Cost Fallacy (EN)",
     "We've already spent 200K on development. We can't waste that. We have to continue."),
    ("bias: Framing Effect (RO)",
     "Dacă nu faceți asta, o să pierdeți 30% din valoare. Asta e riscul pe care îl luați."),
    ("bias: Status Quo Bias (EN)",
     "Why change? We've always done it this way and it works. Let's keep things as they are."),
    ("bias: Availability Heuristic (RO)",
     "Mi-amintesc din urmă caz similar și a eșuat groaznic. Toate cazurile ca asta se termină prost."),
    ("bias: Loss Aversion (RO)",
     "Nu pot accepta riscul ăsta. Prea mult de pierdut dacă se duce rău."),
    ("bias: Anchoring (EN)",
     "The market rate is $100. That's my anchor. Everything else is negotiation around that baseline."),
]

DUAL_SAMPLES = [
    (
        "Dual-bias: You (loss-averse) vs Them (anchoring)",
        "The downside risk is huge. We can't afford to fail. I'm nervous about this move.",
        "My first offer is 75 thousand. That's the number. Let's not waste time on alternatives.",
    ),
    (
        "Dual-bias: You (sunk-cost) vs Them (status-quo)",
        "We've invested 18 months and $500K. We can't throw that away. We have to push through.",
        "Honestly, the current deal is fine. Why fix something that isn't broken? Let's keep the status quo.",
    ),
    (
        "Dual-bias: You (framing) vs Them (availability heuristic)",
        "If we don't do this now, we'll lose the window. The real issue is urgency: act or regret.",
        "I remember the last time we rushed. It was a disaster. Those situations always go sideways.",
    ),
    (
        "Dual-bias: You (data-aware) vs Them (multiple biases)",
        "I understand the fears. Let's look at the data: 82% of similar deals succeed. That's the baseline.",
        "But the risk still feels enormous. We've spent so much already. And the market's changing. Everything points to wait.",
    ),
]


def rule(char="=", width=78):
    print(char * width)


def main():
    bem = BehavioralEconomicsModule()

    print("\n")
    rule()
    print("PART 1: SINGLE-SPEAKER COGNITIVE BIAS DETECTION")
    rule()

    for i, (target, statement) in enumerate(SINGLE_SAMPLES, start=1):
        rule()
        print(f"SAMPLE {i} — target: {target}")
        print(f'Statement: "{statement}"')
        rule("-")

        r = bem.analyze(statement)
        biases = r["cognitive_biases"]["biases_detected"]

        if biases:
            for b in biases:
                print(f"[{b['name'].upper()}]")
                print(f"  Label: {b['label']}")
                print(f"  In negotiation: {b['in_negotiation']}")
                print(f"  Danger: {b['danger']}")
                print(f"  Matched keywords: {b['matched_keywords'][:2]}")
                print()
        else:
            print("[NO BIASES DETECTED]")
            print()

    print("\n")
    rule()
    print("PART 2: DUAL-SPEAKER COGNITIVE BIAS ANALYSIS")
    rule()

    for i, (target, your_text, their_text) in enumerate(DUAL_SAMPLES, start=1):
        rule()
        print(f"DUAL-SAMPLE {i} — scenario: {target}")
        print(f'YOU:  "{your_text}"')
        print(f'THEM: "{their_text}"')
        rule("-")

        r = bem.dual_speaker_bias_analysis(your_text, their_text)

        your_biases = r["your_biases"]["cognitive_biases"]["biases_detected"]
        their_biases = r["their_biases"]["cognitive_biases"]["biases_detected"]

        if your_biases:
            print(f"[YOUR BIASES]  count={len(your_biases)}")
            for b in your_biases[:2]:
                print(f"  • {b['name']}: {b['danger']}")
        else:
            print("[YOUR BIASES]  none detected")

        print()

        if their_biases:
            print(f"[THEIR BIASES]  count={len(their_biases)}")
            for b in their_biases[:2]:
                print(f"  • {b['name']}: {b['danger']}")
        else:
            print("[THEIR BIASES]  none detected")

        print(f"\n[DUAL COACHING]")
        for line in r["coaching"].split("\n"):
            print(f"  {line}")
        print()

    rule()
    print(f"Done. {len(SINGLE_SAMPLES)} single-speaker + {len(DUAL_SAMPLES)} dual-speaker samples processed.")


if __name__ == "__main__":
    main()
