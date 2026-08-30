# -*- coding: utf-8 -*-
"""
Demo driver for SANTINEL Somatic framework (core/somatic_module.py).

Runs SomaticModule.analyze() and dual_speaker_somatic() over EN + RO
negotiation lines, each chosen to exercise one domain: 5 somatic patterns
(breathing, tension, presence, confidence, embodied emotion) and somatic states
(grounded/dysregulated, present/dissociated, confident/anxious). Manual demo,
not a test.

Run from the repo root:
    python demo_somatic.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.somatic_module import SomaticModule

# (target, statement)
SINGLE_SAMPLES = [
    ("pattern: Breathing Rhythm (EN)",
     "I'm catching my breath. My heart is racing and I can't seem to breathe. The shortness of breath is real."),
    ("pattern: Tension/Relaxation (RO)",
     "Umerele mele sunt tensionate. Incleștez din maxilar fără să-mi dau seama. Trebuie să mă relaxez."),
    ("pattern: Presence/Dissociation (EN)",
     "I feel checked out right now. Like I'm not really here. I'm distant and kind of zoned out."),
    ("pattern: Confidence Signals (RO)",
     "Stau drept cu umerele inapoi. Contactul vizual e puternic. Vocea mea e solida si sigura."),
    ("pattern: Embodied Emotion (EN)",
     "I have a lump in my throat and butterflies in my stomach. My chest feels tight. My gut is telling me something."),
    ("state: Grounded (RO)",
     "Simt picioarele pe sol. Sunt inradacinat si stabil. Simtesc greutatea corpului meu. Sunt aici."),
    ("state: Dysregulated (EN)",
     "My heart is pounding. I can't catch my breath. I'm trembling. My nervous system is activated."),
    ("state: Present (RO)",
     "Sunt complet aici, in momentul asta. Sunt constient de tot ce se intampla. Acordat si prezent."),
]

DUAL_SAMPLES = [
    (
        "Dual-somatic: You (grounded) vs Them (dysregulated)",
        "I'm grounded here. Feet on the floor. Breathing steady. Shoulders relaxed. I'm present.",
        "My heart is racing. I can't catch my breath. I'm tense and my shoulders are up. I'm not okay.",
    ),
    (
        "Dual-somatic: You (anxious) vs Them (confident)",
        "I'm trembling. Shallow breathing. Checking out. My posture is small. I'm anxious.",
        "I stand tall with shoulders back. Eye contact is strong. My voice is clear and projects. I'm confident.",
    ),
    (
        "Dual-somatic: You (present) vs Them (dissociated)",
        "I'm alive to this moment. Alert and tuned in. I can feel everything happening.",
        "I feel numb and distant. I'm floating. Not really here. Checked out from the interaction.",
    ),
    (
        "Dual-somatic: You (dysregulated) vs Them (grounded)",
        "My jaw is clenched. Tension everywhere. I'm bracing. Can't relax. Dysregulated.",
        "I feel my weight in the chair. Solid and stable. Breathing is easy. I'm grounded and calm.",
    ),
]


def rule(char="=", width=78):
    print(char * width)


def main():
    sm = SomaticModule()

    print("\n")
    rule()
    print("PART 1: SINGLE-SPEAKER SOMATIC ANALYSIS")
    rule()

    for i, (target, statement) in enumerate(SINGLE_SAMPLES, start=1):
        rule()
        print(f"SAMPLE {i} — target: {target}")
        print(f'Statement: "{statement}"')
        rule("-")

        r = sm.analyze(statement)

        patterns = r["somatic_patterns"]
        print(f"[SOMATIC PATTERNS]")
        if patterns["primary_pattern"]:
            print(f"  Primary pattern: {patterns['primary_pattern'].replace('_', ' ').title()}")
            insight = patterns["analysis"]
            print(f"  Label: {insight[0]}")
            print(f"  Indicator: {insight[1]}")
        print(f"  All patterns: {patterns['patterns']}")
        print()

        state = r["somatic_state"]
        print(f"[SOMATIC STATE]")
        print(f"  Overall state: {state['overall_summary']}")
        print(f"  Grounding: {state['grounding_state']} ({state['grounding_indicators']} cues)")
        print(f"  Presence: {state['presence_state']} ({state['presence_indicators']} cues)")
        print(f"  Confidence: {state['confidence_state']} (score: {state['confidence_score']:.2f})")
        print()

    print("\n")
    rule()
    print("PART 2: DUAL-SPEAKER SOMATIC ANALYSIS")
    rule()

    for i, (target, your_text, their_text) in enumerate(DUAL_SAMPLES, start=1):
        rule()
        print(f"DUAL-SAMPLE {i} — scenario: {target}")
        print(f'YOU:  "{your_text}"')
        print(f'THEM: "{their_text}"')
        rule("-")

        r = sm.dual_speaker_somatic(your_text, their_text)

        your_state = r["your_somatic"]["somatic_state"]
        their_state = r["their_somatic"]["somatic_state"]

        print(f"[SOMATIC STATES]")
        print(f"  YOU:  {your_state['overall_summary']}")
        print(f"        Grounding: {your_state['grounding_state']} | Presence: {your_state['presence_state']} | Confidence: {your_state['confidence_state']}")
        print(f"  THEM: {their_state['overall_summary']}")
        print(f"        Grounding: {their_state['grounding_state']} | Presence: {their_state['presence_state']} | Confidence: {their_state['confidence_state']}")
        print()

        print(f"[SOMATIC ALIGNMENT]")
        if your_state["grounding_state"] == their_state["grounding_state"]:
            print(f"  ✓ Grounding alignment: Both {your_state['grounding_state']}")
        else:
            print(f"  ✗ Grounding mismatch: You {your_state['grounding_state']}, Them {their_state['grounding_state']}")

        if your_state["presence_state"] == their_state["presence_state"]:
            print(f"  ✓ Presence alignment: Both {your_state['presence_state']}")
        else:
            print(f"  ✗ Presence mismatch: You {your_state['presence_state']}, Them {their_state['presence_state']}")
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
