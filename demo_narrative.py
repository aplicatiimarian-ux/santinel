# -*- coding: utf-8 -*-
"""
Demo driver for SANTINEL Narrative framework (core/narrative_module.py).

Runs NarrativeModule.analyze() and dual_speaker_narrative() over EN + RO
negotiation lines, each chosen to exercise one domain: 4 narrative archetypes
(hero's journey, victim, victor, collaborative), identity patterns (agency,
passivity, connection), and meaning-making (growth, loss, purpose). Manual
demo, not a test.

Run from the repo root:
    python demo_narrative.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.narrative_module import NarrativeModule

# (target, statement)
SINGLE_SAMPLES = [
    ("narrative: Hero's Journey (EN)",
     "I faced this challenge head-on. It was hard, but I learned a lot and grew stronger. Adversity made me wiser."),
    ("narrative: Victim (RO)",
     "Mi-a facut asta. Nu am control asupra situatiei. Sistemul e impotriva mea. Nu pot scapa."),
    ("narrative: Victor (EN)",
     "I defeated them. I dominated the negotiation. My strategy worked and I came out on top. I always win."),
    ("narrative: Collaborative (RO)",
     "Am lucrat impreuna si amandoi am beneficiat. Parteneriul nostru a dus la castig reciproc."),
    ("identity: Agentic (EN)",
     "I decided to pursue this. I took charge of the situation. I initiated the conversation and shaped the outcome."),
    ("identity: Passive (RO)",
     "Mi s-a spus ca trebuie. Circumstantele m-au fortat. Nu am avut alegere. Am fost supus la decizia lor."),
    ("meaning: Growth-Oriented (EN)",
     "This taught me something valuable. I gained new perspective and insight. I transformed through this experience."),
    ("meaning: Loss-Focused (RO)",
     "Am pierdut asa mult. Totul s-a distrus. Nu se va recupera niciodata. Totul e gata."),
]

DUAL_SAMPLES = [
    (
        "Dual-narrative: You (hero) vs Them (victim)",
        "I faced this challenge and I grew through it. It was difficult but I learned.",
        "They did this to me. I'm stuck. The system is against me. I have no control.",
    ),
    (
        "Dual-narrative: You (collaborative) vs Them (victor)",
        "We built something together and both benefited. Our partnership was key.",
        "I won the negotiation. My strategy dominated. I came out on top.",
    ),
    (
        "Dual-narrative: You (agentic) vs Them (passive)",
        "I decided to take charge. I initiated this and shaped the direction we went.",
        "Circumstances forced me here. I had no choice. They made the decisions.",
    ),
    (
        "Dual-narrative: You (growth) vs Them (loss-focused)",
        "This experience taught me valuable insights. I transformed through the challenge.",
        "I lost so much. It's all destroyed. Nothing can be recovered. It's ruined.",
    ),
]


def rule(char="=", width=78):
    print(char * width)


def main():
    nm = NarrativeModule()

    print("\n")
    rule()
    print("PART 1: SINGLE-SPEAKER NARRATIVE ANALYSIS")
    rule()

    for i, (target, statement) in enumerate(SINGLE_SAMPLES, start=1):
        rule()
        print(f"SAMPLE {i} — target: {target}")
        print(f'Statement: "{statement}"')
        rule("-")

        r = nm.analyze(statement)

        narrative = r["dominant_narrative"]
        print(f"[DOMINANT NARRATIVE]")
        print(f"  Archetype: {narrative['dominant_narrative'].replace('_', ' ').title()}")
        print(f"  Scores: {narrative['scores']}")
        print(f"  Profile: {narrative['profile'][0]}")
        print(f"  Impact: {narrative['impact']}")
        print()

        identity = r["identity_patterns"]
        print(f"[IDENTITY PATTERNS]")
        print(f"  {identity['identity_summary']}")
        print(f"  Agency: {identity['agency_stance']} ({identity['agency_indicators']} indicators)")
        print(f"  Connection: {identity['connection_stance']} ({identity['connection_indicators']} indicators)")
        print()

        meaning = r["meaning_patterns"]
        print(f"[MEANING-MAKING]")
        print(f"  Orientation: {meaning['meaning_orientation']}")
        print(f"  Growth indicators: {meaning['growth_indicators']}")
        print(f"  Loss indicators: {meaning['loss_indicators']}")
        print(f"  Purpose indicators: {meaning['purpose_indicators']}")
        print()

    print("\n")
    rule()
    print("PART 2: DUAL-SPEAKER NARRATIVE ANALYSIS")
    rule()

    for i, (target, your_text, their_text) in enumerate(DUAL_SAMPLES, start=1):
        rule()
        print(f"DUAL-SAMPLE {i} — scenario: {target}")
        print(f'YOU:  "{your_text}"')
        print(f'THEM: "{their_text}"')
        rule("-")

        r = nm.dual_speaker_narrative(your_text, their_text)

        your_narrative = r["your_narrative"]["dominant_narrative"]["dominant_narrative"]
        their_narrative = r["their_narrative"]["dominant_narrative"]["dominant_narrative"]
        your_identity = r["your_narrative"]["identity_patterns"]["identity_summary"]
        their_identity = r["their_narrative"]["identity_patterns"]["identity_summary"]

        print(f"[NARRATIVE ARCHETYPES]")
        print(f"  YOU: {your_narrative.replace('_', ' ').title()}")
        print(f"  THEM: {their_narrative.replace('_', ' ').title()}")
        if your_narrative == their_narrative:
            print(f"  ✓ ALIGNMENT: Both tell {your_narrative.replace('_', ' ')} stories")
        else:
            print(f"  ✗ MISMATCH: Different narratives")
        print()

        print(f"[IDENTITY PATTERNS]")
        print(f"  YOUR IDENTITY: {your_identity}")
        print(f"  THEIR IDENTITY: {their_identity}")
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
