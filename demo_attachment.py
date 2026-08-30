# -*- coding: utf-8 -*-
"""
Demo driver for SANTINEL Attachment framework (core/attachment_module.py).

Runs AttachmentModule.analyze() and dual_speaker_attachment() over EN + RO
negotiation lines, each chosen to exercise one domain: attachment styles
(secure, anxious, avoidant, fearful-avoidant), anxiety-avoidance scoring,
and core wounds (abandonment, control, inadequacy, distrust). Manual demo,
not a test.

Run from the repo root:
    python demo_attachment.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.attachment_module import AttachmentModule

# (target, statement)
SINGLE_SAMPLES = [
    ("style: Secure (EN)",
     "I trust you on this. Let's work through the details together and find what works for both of us."),
    ("style: Anxious (RO)",
     "Mă tem că o să mă parasite dacă nu accept oferta asta. Nu-i asta ceea ce vrei?"),
    ("style: Avoidant (EN)",
     "I don't need this deal to fall through. I'm fine on my own. Let's not waste time on details."),
    ("style: Fearful-Avoidant (RO)",
     "Vreau să mă apropii de tine, dar imi e groază. Și dacă mă refuzi? Dar nici nu pot suporta singurătatea."),
    ("wound: Abandonment (EN)",
     "You always leave me in the end. Everyone does. I'm going to be alone again."),
    ("wound: Control (RO)",
     "Nu pot să accept asta dacă nu fac asta în felul meu. Trebuie să am control total."),
    ("wound: Inadequacy (EN)",
     "I'm not smart enough for this deal. I'll probably mess it up like I always do."),
    ("wound: Distrust (RO)",
     "Nu-ți cred. Care-i scopul ascuns? Toți oamenii au motive ascunse, și tu la fel."),
]

DUAL_SAMPLES = [
    (
        "Dual-attachment: You (anxious) vs Them (avoidant)",
        "Please don't leave the table. I need to know you're committed to this. Will you stay?",
        "I don't see why this matters so much. I'm fine handling this on my own.",
    ),
    (
        "Dual-attachment: You (secure) vs Them (fearful-avoidant)",
        "I trust you. We can take this step by step. You're in control of how fast we move.",
        "I want this but it scares me. What if I mess up? But also, I don't want to give up control.",
    ),
    (
        "Dual-attachment: You (avoidant) vs Them (anxious)",
        "Look, I can handle this myself. I don't need constant reassurance or check-ins.",
        "But what if something goes wrong? Can you at least confirm we're still on track?",
    ),
    (
        "Dual-attachment: You (secure with abandonment wound) vs Them (secure)",
        "I notice I'm worried you'll leave if we hit a problem. That's old fear. Let's keep talking.",
        "I'm not going anywhere. We'll work through this together. That's what partners do.",
    ),
]


def rule(char="=", width=78):
    print(char * width)


def main():
    att = AttachmentModule()

    print("\n")
    rule()
    print("PART 1: SINGLE-SPEAKER ATTACHMENT ANALYSIS")
    rule()

    for i, (target, statement) in enumerate(SINGLE_SAMPLES, start=1):
        rule()
        print(f"SAMPLE {i} — target: {target}")
        print(f'Statement: "{statement}"')
        rule("-")

        r = att.analyze(statement)

        score = r["attachment_style"]
        print(f"[attachment style] {score['attachment_style'].upper()}")
        print(f"                   anxiety={score['anxiety']:.3f}, avoidance={score['avoidance']:.3f}")
        print(f"                   secure_baseline={score['secure_baseline']:.3f}")
        if score["matched_anxiety"]:
            print(f"                   anxiety triggers: {score['matched_anxiety'][:2]}")
        if score["matched_avoidance"]:
            print(f"                   avoidance triggers: {score['matched_avoidance'][:2]}")

        wounds = r["wounds"]["wounds_detected"]
        if wounds:
            print(f"[wounds detected]  count={len(wounds)}")
            for w in wounds:
                print(f"                   • {w['label']}")
                print(f"                     {w['trigger_pattern']}")
        else:
            print("[wounds detected]  none")
        print()

    print("\n")
    rule()
    print("PART 2: DUAL-SPEAKER ATTACHMENT ASSESSMENT")
    rule()

    for i, (target, your_text, their_text) in enumerate(DUAL_SAMPLES, start=1):
        rule()
        print(f"DUAL-SAMPLE {i} — scenario: {target}")
        print(f'YOU:  "{your_text}"')
        print(f'THEM: "{their_text}"')
        rule("-")

        r = att.dual_speaker_attachment(your_text, their_text)

        your_att = r["your_attachment"]["attachment_style"]
        their_att = r["their_attachment"]["attachment_style"]

        print(f"[YOUR ATTACHMENT]")
        print(f"  style={your_att['attachment_style'].upper()}")
        print(f"  anxiety={your_att['anxiety']:.3f}, avoidance={your_att['avoidance']:.3f}")

        print(f"\n[THEIR ATTACHMENT]")
        print(f"  style={their_att['attachment_style'].upper()}")
        print(f"  anxiety={their_att['anxiety']:.3f}, avoidance={their_att['avoidance']:.3f}")

        your_wounds = r["your_attachment"]["wounds"]["wounds_detected"]
        their_wounds = r["their_attachment"]["wounds"]["wounds_detected"]

        if your_wounds:
            print(f"\n[YOUR WOUNDS]")
            for w in your_wounds[:2]:
                print(f"  • {w['wound']}: {w['impact_in_negotiation']}")

        if their_wounds:
            print(f"\n[THEIR WOUNDS]")
            for w in their_wounds[:2]:
                print(f"  • {w['wound']}: {w['impact_in_negotiation']}")

        print(f"\n[DUAL COACHING]")
        for line in r["coaching"].split("\n"):
            print(f"  {line}")
        print()

    rule()
    print(f"Done. {len(SINGLE_SAMPLES)} single-speaker + {len(DUAL_SAMPLES)} dual-speaker samples processed.")


if __name__ == "__main__":
    main()
