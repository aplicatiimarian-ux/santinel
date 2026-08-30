# -*- coding: utf-8 -*-
"""
Demo driver for SANTINEL psychology framework 3 — TA (core/ta_module.py).

Runs TAModule.analyze() over EN + RO negotiation lines, each chosen to
exercise one domain: functional ego states, the I'm OK / You're OK life
position matrix, and the 5 sales games (Hard to Get, Rapo, Kick Me, Yes But,
Wooden Leg). Manual demo, not a test.

Run from the repo root:
    python demo_ta.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.ta_module import TAModule

# (target, statement)
SAMPLES = [
    ("ego state: Critical Parent (EN)",
     "You should have read the contract. This is unacceptable and frankly amateur."),
    ("ego state: Adult (RO)",
     "Să analizăm opțiunile: care sunt faptele și ce spune bugetul din punct de vedere logic?"),
    ("ego state: Adapted Child (RO)",
     "Scuze de deranj, cred că da, cum spuneți dumneavoastră."),
    ("life position: I'm OK / You're not OK (EN)",
     "I'm right and they don't get it — they're amateurs."),
    ("life position: I'm not OK / You're OK (RO)",
     "Probabil greșesc, voi știți mai bine, nu mă pot compara cu voi."),
    ("game: Yes But (EN)",
     "Yes, but that won't work. I've already tried that."),
    ("game: Hard to Get (RO)",
     "Nu sunt sigur că avem nevoie, nu ne grăbim, avem și alte oferte."),
    ("game: Wooden Leg (EN)",
     "I can't because of the system. It's not my fault, the process is broken."),
    ("game: Kick Me (RO)",
     "Oricum o să refuzați. Știu că e un moment prost, mă pricep prost la asta."),
    ("healthy Adult, no game (RO)",
     "Am trimis oferta și propun să vorbim vineri despre pașii următori."),
]


def rule(char="=", width=78):
    print(char * width)


def main():
    ta = TAModule()
    for i, (target, statement) in enumerate(SAMPLES, start=1):
        rule()
        print(f"SAMPLE {i} — targets: {target}")
        print(f'Statement: "{statement}"')
        rule("-")
        r = ta.analyze(statement)

        ego = r["ego_states"]
        matched = {k: v for k, v in ego["matched"].items() if v}
        print(f"[ego state] primary={ego['primary_ego_state']}"
              f"{'' if matched else ' (assumed, nothing matched)'}")
        if matched:
            print(f"            scores={ego['scores']}")
            print(f"            matched={matched}")
        print(f"            {ego['analysis']}")

        lp = r["life_position"]
        tag = " (assumed default)" if lp["assumed_default"] else ""
        print(f"[life position] {lp['life_position']}{tag} — {lp['label']}")
        if not lp["assumed_default"]:
            print(f"                present={lp['positions_present']} matched={lp['matched']}")
            print(f"                -> {lp['guidance']}")

        games = r["games"]["games_detected"]
        if games:
            for g in games:
                print(f"[game] {g['name']}  matched={g['matched_keywords']} [{g['language']}]")
                print(f"       payoff: {g['payoff']}")
                print(f"       exit:   {g['exit']}")
        else:
            print("[game] none")
        print()

    rule()
    print(f"Done. {len(SAMPLES)} samples processed.")


if __name__ == "__main__":
    main()
