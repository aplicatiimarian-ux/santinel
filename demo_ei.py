# -*- coding: utf-8 -*-
"""
Demo driver for SANTINEL EI framework (core/ei_module.py).

Runs EIModule.analyze() and dual_speaker_assessment() over EN + RO negotiation
lines, each chosen to exercise one domain: Goleman's 5 competencies and 6 emotional
states (openness, skepticism, frustration, curiosity, fear, acceptance). Manual
demo, not a test.

Run from the repo root:
    python demo_ei.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.ei_module import EIModule

# (target, statement)
SINGLE_SAMPLES = [
    ("competency: Self-Awareness (EN)",
     "I realize I'm anxious about this, and that's making me push too hard."),
    ("competency: Self-Regulation (RO)",
     "Să fiu puțin mai calm. Voi lua o pauză și voi reconsider strategia."),
    ("competency: Motivation (EN)",
     "I'm committed to finding a solution that works for both of us. We can figure this out."),
    ("competency: Empathy (RO)",
     "Înțeleg cum te simți, și e important pentru tine. Vorbim despre nevoile tale?"),
    ("competency: Social Skills (EN)",
     "Let's work together on this. What do you think would be fair for both of us?"),
    ("state: Openness (RO)",
     "Asta e interesant. Spune-mi mai mult, vreau să înțeleg perspectiva ta."),
    ("state: Skepticism (EN)",
     "I'm not sure that's going to work. Show me the data and maybe I'll be convinced."),
    ("state: Frustration (RO)",
     "Nu ajungem nicăieri cu asta. Asta nu are sens, suntem în cerc."),
    ("state: Curiosity (EN)",
     "Why is that? I wonder what would happen if we tried a different approach."),
    ("state: Fear (RO)",
     "Mă îngrijorează riscul ăsta. Mă spaimantă gândul că se poate înrăutăți."),
    ("state: Acceptance (EN)",
     "That sounds good to me. I'm comfortable with those terms, let's move forward."),
]

DUAL_SAMPLES = [
    (
        "Dual-speaker: You (frustrated) vs Them (fearful)",
        "This is going nowhere! We've been talking for two hours and nothing is working.",
        "I'm worried this deal might fall through. What if we can't make it work?",
    ),
    (
        "Dual-speaker: You (empathetic) vs Them (skeptical)",
        "I hear your concerns. Let me understand what's most important to you.",
        "I'm not convinced this will actually solve our problem. Where's the proof?",
    ),
    (
        "Dual-speaker: You (self-aware) vs Them (curious)",
        "I sense I'm being defensive, so let me take a step back and listen.",
        "That's an interesting angle. What if we approached it that way instead?",
    ),
]


def rule(char="=", width=78):
    print(char * width)


def main():
    ei = EIModule()

    print("\n")
    rule()
    print("PART 1: SINGLE-SPEAKER EI ANALYSIS (Competencies + Emotional State)")
    rule()

    for i, (target, statement) in enumerate(SINGLE_SAMPLES, start=1):
        rule()
        print(f"SAMPLE {i} — target: {target}")
        print(f'Statement: "{statement}"')
        rule("-")

        r = ei.analyze(statement)

        comp = r["competencies"]
        print(f"[competencies] primary={comp['primary_competency']}")
        if comp["matched"]:
            print(f"               scores={comp['scores']}")
            matched = {k: v for k, v in comp["matched"].items() if v}
            print(f"               matched={matched}")
        if comp["analysis"]:
            print(f"               {comp['analysis'][0]}")

        state = r["emotional_state"]
        tag = " (assumed default)" if state["assumed_default"] else ""
        print(f"[emotional state] {state['primary_emotional_state']}{tag}")
        print(f"                  {state['label']}")
        if not state["assumed_default"]:
            print(f"                  present={state['states_present']}")
            print(f"                  matched={state['matched']}")
        print(f"                  -> {state['guidance']}")
        print()

    print("\n")
    rule()
    print("PART 2: DUAL-SPEAKER EI ASSESSMENT (You vs Them)")
    rule()

    for i, (target, your_text, their_text) in enumerate(DUAL_SAMPLES, start=1):
        rule()
        print(f"DUAL-SAMPLE {i} — scenario: {target}")
        print(f'YOU:  "{your_text}"')
        print(f'THEM: "{their_text}"')
        rule("-")

        r = ei.dual_speaker_assessment(your_text, their_text)

        your_ei = r["your_ei"]
        their_ei = r["their_ei"]

        your_state = your_ei["emotional_state"]["primary_emotional_state"]
        your_comp = your_ei["competencies"]["primary_competency"]
        their_state = their_ei["emotional_state"]["primary_emotional_state"]
        their_comp = their_ei["competencies"]["primary_competency"]

        print(f"[YOUR EI]  emotional_state={your_state}"
              f"{f', competency={your_comp}' if your_comp else ''}")
        print(f"[THEIR EI] emotional_state={their_state}"
              f"{f', competency={their_comp}' if their_comp else ''}")
        print(f"\n[DUAL COACHING]\n{r['coaching']}")
        print()

    rule()
    print(f"Done. {len(SINGLE_SAMPLES)} single-speaker + {len(DUAL_SAMPLES)} dual-speaker samples processed.")


if __name__ == "__main__":
    main()
