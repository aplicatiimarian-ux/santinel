# -*- coding: utf-8 -*-
"""
Demo driver for the Romanian side of SANTINEL psychology framework 1 — CBT.

Exercises core.cbt_module.CBTAssessment on Romanian negotiation statements to
show: the Romanian lexicon (core/cbt_keywords_ro.py), Snowball stemming
(inflected forms), clause-scoped negation handling, and mixed EN/RO input.

Run from the repo root:
    python demo_cbt_ro.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.cbt_module import CBTAssessment, STEMMING_ENABLED

# (label, statement, emotions)
SAMPLES = [
    (
        "Catastrofizare + gândire alb-negru",
        "Dacă pierd contractul ăsta e un dezastru total și cariera mea e distrusă.",
        {"frica": 0.8, "rusine": 0.5},
    ),
    (
        "Suprageneralizare + citirea gândurilor (formă flexionată)",
        "Clienții ăștia mereu mă refuză, de fiecare dată. Sigur mă consideră disperat.",
        {"furie": 0.7, "frustrare": 0.6},
    ),
    (
        "Enunțuri cu „trebuie” + eroarea corectitudinii",
        "Ar trebui să obțin 20% sau e un eșec total. Nu e corect ce cer ei.",
        {"regret": 0.6, "anxietate": 0.5},
    ),
    (
        "Negație pe aceeași propoziție -> distorsiune suprimată",
        "Nu cred că e un dezastru, avem argumente bune și un plan clar.",
        {"calm": 0.6, "incredere": 0.6},
    ),
    (
        "Eroarea controlului + învinovățire (negația nu trece de virgulă)",
        "Nu depinde de mine, e numai vina lor că totul s-a blocat.",
        {"neputinta": 0.7, "furie": 0.5},
    ),
    (
        "Input mixt EN/RO -> o singură suprageneralizare (dedup)",
        "They always lowball us și mereu găsesc un motiv nou.",
        {"frustrare": 0.6},
    ),
    (
        "Fără distorsiuni",
        "Prețul lor e agresiv, dar propunerea noastră de valoare e solidă. "
        "Ne concentrăm pe ROI și pe costul de schimbare.",
        {"incredere": 0.7, "calm": 0.6},
    ),
]


def rule(char="=", width=76):
    print(char * width)


def main():
    print(f"Stemming (snowballstemmer) enabled: {STEMMING_ENABLED}")
    cbt = CBTAssessment()

    for i, (label, statement, emotions) in enumerate(SAMPLES, start=1):
        rule()
        print(f"SAMPLE {i} — {label}")
        print(f'Statement: "{statement}"')
        rule("-")

        distortions = cbt.identify_distortions(statement)
        if distortions:
            print(f"Distortions found ({len(distortions)}):")
            for d in distortions:
                print(
                    f"  - {d['distortion']:<26} "
                    f"[{d['language']}/{d['matched_by']}] keyword={d['keyword']!r}"
                )
                print(f"      {d['description']}")
        else:
            print("Distortions found: none")

        assessment = cbt.assess_emotional_state(statement, emotions)
        print()
        print(f"Dominant emotion:    {assessment['dominant_emotion']} "
              f"(intensity {assessment['emotion_intensity']})")
        print(f"Therapeutic insight: {assessment['therapeutic_insight']}")
        print()

    rule()
    print(f"Done. {len(SAMPLES)} samples processed.")


if __name__ == "__main__":
    main()
