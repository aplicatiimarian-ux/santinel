# -*- coding: utf-8 -*-
"""
Demo driver for SANTINEL Game Theory framework (core/game_theory_module.py).

Runs GameTheoryModule.analyze() and dual_speaker_game_analysis() over EN + RO
negotiation lines, each chosen to exercise one domain: game archetypes
(prisoner's dilemma, zero-sum, coordination, battle of sexes), strategic
positions, BATNA, and ZOPA. Manual demo, not a test.

Run from the repo root:
    python demo_game_theory.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.game_theory_module import GameTheoryModule

# (target, statement)
SINGLE_SAMPLES = [
    ("game: Prisoner's Dilemma (EN)",
     "We both benefit if we cooperate, but if you betray me, I'm exposed. Can I trust you?"),
    ("game: Zero-Sum (RO)",
     "Fiecare leu pe care-l economisești este un leu pe care-l pierd eu. Nu putem castiga amandoi."),
    ("game: Coordination Game (EN)",
     "We want the same outcome. The challenge is coordinating on how to get there."),
    ("game: Battle of the Sexes (RO)",
     "Tu preferi asa, eu prefer asa. Noi vrem lucruri diferite dar suntem de acord sa colaboram."),
    ("position: Dominant (EN)",
     "I hold the cards here. I have leverage and options. They need this more than I do."),
    ("position: Parity (RO)",
     "Suntem egali. Amandoi avem nevoie de asta. Nici unu nu-si permite sa piarda."),
    ("BATNA/ZOPA (EN)",
     "My walk-away point is if you can't offer at least 50K. Below that, I use my alternative."),
    ("game + position (RO)",
     "E un joc zero-sum, iar eu sunt in pozitia dominanta. Am parghie si optiuni pe care tu nu le ai."),
]

DUAL_SAMPLES = [
    (
        "Dual-game: You (dilemma) vs Them (zero-sum)",
        "We both benefit if we cooperate. I want to work together and build trust.",
        "This is simple: what you save is what I lose. I'm going to maximize my gain.",
    ),
    (
        "Dual-position: You (parity) vs Them (dominant)",
        "We're on equal footing here. We both have leverage, and we both need a deal.",
        "Actually, I hold most of the cards. I have several alternatives. I'm in the driver's seat.",
    ),
    (
        "Dual-game: You (coordination) vs Them (battle of sexes)",
        "We want the same outcome. We just need to align on the how. We're on the same team.",
        "I prefer this outcome, you prefer that one. We disagree on priorities, but we both want agreement.",
    ),
    (
        "Dual-position: You (disadvantaged) vs Them (dominant)",
        "I need this deal. My alternative isn't great, so I'm motivated to find terms that work.",
        "I have multiple options. I can walk away anytime. I'm in a strong position.",
    ),
]


def rule(char="=", width=78):
    print(char * width)


def main():
    gt = GameTheoryModule()

    print("\n")
    rule()
    print("PART 1: SINGLE-SPEAKER GAME-THEORETIC ANALYSIS")
    rule()

    for i, (target, statement) in enumerate(SINGLE_SAMPLES, start=1):
        rule()
        print(f"SAMPLE {i} — target: {target}")
        print(f'Statement: "{statement}"')
        rule("-")

        r = gt.analyze(statement)

        game = r["game_archetype"]
        print(f"[GAME ARCHETYPE]")
        print(f"  Type: {game['game_archetype'].replace('_', ' ').title()}")
        print(f"  Scores: {game['scores']}")
        print(f"  Label: {game['label']}")
        print()

        position = r["strategic_position"]
        print(f"[STRATEGIC POSITION]")
        print(f"  Position: {position['strategic_position'].upper()}")
        print(f"  Guidance: {position['guidance']}")
        print()

        batna = r["batna_zopa"]
        print(f"[BATNA/ZOPA]")
        print(f"  BATNA clarity: {batna['batna_clarity']}")
        if batna["batna_count"] > 0:
            print(f"  BATNA indicators: {batna['batna_indicators'][:2]}")
        print(f"  ZOPA clarity: {batna['zopa_clarity']}")
        if batna["zopa_count"] > 0:
            print(f"  ZOPA indicators: {batna['zopa_indicators'][:2]}")
        print()

    print("\n")
    rule()
    print("PART 2: DUAL-SPEAKER GAME-THEORETIC ANALYSIS")
    rule()

    for i, (target, your_text, their_text) in enumerate(DUAL_SAMPLES, start=1):
        rule()
        print(f"DUAL-SAMPLE {i} — scenario: {target}")
        print(f'YOU:  "{your_text}"')
        print(f'THEM: "{their_text}"')
        rule("-")

        r = gt.dual_speaker_game_analysis(your_text, their_text)

        your_game = r["your_game"]["game_archetype"]
        their_game = r["their_game"]["game_archetype"]
        your_pos = r["your_position"]["strategic_position"]
        their_pos = r["their_position"]["strategic_position"]

        print(f"[GAME PERCEPTION]")
        print(f"  YOU see: {your_game.replace('_', ' ').title()}")
        print(f"  THEM see: {their_game.replace('_', ' ').title()}")
        if your_game == their_game:
            print(f"  ALIGNMENT: ✓ Both agree on game type")
        else:
            print(f"  MISMATCH: ✗ Different game perceptions")
        print()

        print(f"[STRATEGIC POSITIONS]")
        print(f"  YOUR position: {your_pos.upper()}")
        print(f"  THEIR position: {their_pos.upper()}")
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
