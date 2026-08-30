# -*- coding: utf-8 -*-
"""
Demo driver for SANTINEL Neuroscience framework (core/neuroscience_module.py).

Runs NeuroscienceModule.analyze() and dual_speaker_neuroscience() over EN + RO
negotiation lines, each chosen to exercise one domain: 5 neurobiological patterns
(amygdala, reward, mirror, default mode, vagal tone), nervous system states
(sympathetic, parasympathetic, balanced), and threat/safety/reward scoring. Manual
demo, not a test.

Run from the repo root:
    python demo_neuroscience.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.neuroscience_module import NeuroscienceModule

# (target, statement)
SINGLE_SAMPLES = [
    ("pattern: Amygdala Activation (EN)",
     "I'm feeling really anxious about this. This makes me nervous. My heart is racing and I feel threatened."),
    ("pattern: Reward System (RO)",
     "Asta ma incanta! Sunt foarte motivat. Asta ma aprinde și sunt entuziast pentru posibilitati."),
    ("pattern: Mirror Neurons (EN)",
     "I resonate with what you're saying. I feel your concern. We're on the same wavelength here."),
    ("state: Sympathetic (RO)",
     "Sunt in alarma. Lupta sau fuga. Asta e urgent si sunt activat. Presiune pura."),
    ("state: Parasympathetic (EN)",
     "I feel calm and relaxed here. I'm grounded and present. Safe to explore options together."),
    ("pattern: Default Mode Network (RO)",
     "Continuu sa mă gândesc la asta. Asta îmi amintește de un caz din urmă care a eșuat. Am gânduri negative."),
    ("pattern: Vagal Tone (EN)",
     "I'm centered and grounded. I can breathe easily. I feel at peace and connected with you."),
    ("threat/safety: Mixed (RO)",
     "Sunt puțin ingrijorat dar și interesat. Simt o oarecare ansietate dar și speranță de colaborare."),
]

DUAL_SAMPLES = [
    (
        "Dual-neurology: You (activated) vs Them (calm)",
        "I'm anxious about this. My heart is racing. I feel like we're under pressure and time is running out.",
        "I'm feeling calm and centered. Let's take our time. There's no rush. We can figure this out.",
    ),
    (
        "Dual-neurology: You (reward-engaged) vs Them (amygdala-activated)",
        "This excites me! The possibilities are incredible. I'm motivated and engaged in finding a solution.",
        "I'm not sure about this. I feel threatened by the risk. Can we really trust this will work?",
    ),
    (
        "Dual-neurology: You (vagal-tone) vs Them (default-mode ruminating)",
        "I'm grounded in this moment. Let's be present with what's actually happening right now.",
        "But what if this goes wrong like last time? I keep replaying that disaster in my head.",
    ),
    (
        "Dual-neurology: You (balanced) vs Them (sympathetic-activated)",
        "I'm calm but alert. Let's solve this step by step. We both have what the other needs.",
        "We need to move fast. This is urgent. I'm stressed about our timeline. We can't waste time.",
    ),
]


def rule(char="=", width=78):
    print(char * width)


def main():
    ns = NeuroscienceModule()

    print("\n")
    rule()
    print("PART 1: SINGLE-SPEAKER NEUROBIOLOGICAL ANALYSIS")
    rule()

    for i, (target, statement) in enumerate(SINGLE_SAMPLES, start=1):
        rule()
        print(f"SAMPLE {i} — target: {target}")
        print(f'Statement: "{statement}"')
        rule("-")

        r = ns.analyze(statement)

        patterns = r["neurobiological_patterns"]
        print(f"[NEUROBIOLOGICAL PATTERNS]")
        print(f"  Primary pattern: {patterns['primary_pattern']}")
        if patterns["primary_pattern"]:
            print(f"  Label: {patterns['analysis'][0]}")
            print(f"  Signals: {patterns['analysis'][1]}")
        print(f"  All pattern scores: {patterns['patterns']}")
        print()

        state = r["nervous_system_state"]
        print(f"[NERVOUS SYSTEM STATE]")
        print(f"  State: {state['state'].upper()}")
        print(f"  Sympathetic: {state['sympathetic_indicators']}, Parasympathetic: {state['parasympathetic_indicators']}")
        print(f"  Label: {state['label']}")
        print()

        tsr = r["threat_safety_reward"]
        print(f"[THREAT/SAFETY/REWARD SCORING]")
        print(f"  Threat: {tsr['threat']:.3f}  |  Safety: {tsr['safety']:.3f}  |  Reward: {tsr['reward']:.3f}")
        print(f"  Overall state: {tsr['overall_state']}")
        print(f"  Guidance: {tsr['state_guidance']}")
        print()

    print("\n")
    rule()
    print("PART 2: DUAL-SPEAKER NEUROBIOLOGICAL ANALYSIS")
    rule()

    for i, (target, your_text, their_text) in enumerate(DUAL_SAMPLES, start=1):
        rule()
        print(f"DUAL-SAMPLE {i} — scenario: {target}")
        print(f'YOU:  "{your_text}"')
        print(f'THEM: "{their_text}"')
        rule("-")

        r = ns.dual_speaker_neuroscience(your_text, their_text)

        your_state = r["your_neurobiology"]["nervous_system_state"]["state"]
        their_state = r["their_neurobiology"]["nervous_system_state"]["state"]
        your_threat = r["your_neurobiology"]["threat_safety_reward"]["threat"]
        their_threat = r["their_neurobiology"]["threat_safety_reward"]["threat"]
        your_reward = r["your_neurobiology"]["threat_safety_reward"]["reward"]
        their_reward = r["their_neurobiology"]["threat_safety_reward"]["reward"]

        print(f"[NERVOUS SYSTEM STATES]")
        print(f"  YOU: {your_state.upper()}")
        print(f"       Threat={your_threat:.3f}  Safety Score, Reward={your_reward:.3f}")
        print(f"  THEM: {their_state.upper()}")
        print(f"        Threat={their_threat:.3f}, Reward={their_reward:.3f}")
        print()

        print(f"[NEUROSCIENCE ALIGNMENT]")
        if your_state == their_state:
            print(f"  ✓ Both in {your_state} state")
        else:
            print(f"  ✗ Mismatch: You {your_state}, Them {their_state}")
        print()

        print(f"[COACHING]")
        for line in r["coaching"].split("\n"):
            if line.strip():
                print(f"  {line}")
        print()

    rule()
    print(f"Done. {len(SINGLE_SAMPLES)} single-speaker + {len(DUAL_SAMPLES)} dual-speaker samples processed.")


if __name__ == "__main__":
    main()
