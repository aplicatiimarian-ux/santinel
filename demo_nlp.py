# -*- coding: utf-8 -*-
"""
Demo driver for SANTINEL psychology framework 2 — NLP (core/nlp_module.py).

Runs NLPModule.analyze() over EN + RO negotiation statements, each chosen to
exercise one of the 7 domains: representation systems (VAK), anchoring,
modeling, pacing & leading, Milton language, reframing, submodalities.
This is a manual demo, not a test.

Run from the repo root:
    python demo_nlp.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from core.nlp_module import NLPModule

# (target domain, statement)
SAMPLES = [
    ("representation systems / VAK (EN, visual)",
     "I can't see how this comes together — show me the big picture and it gets clear."),
    ("representation systems / VAK (RO, kinesthetic)",
     "Simt o presiune uriașă și nu prind ideea; totul pare greu și rece."),
    ("anchoring (RO)",
     "Sunt anxios și tensionat înainte de negociere. Îmi amintesc când am reușit data trecută."),
    ("modeling (EN)",
     "How would the best negotiator open this? My mentor always pulls it off."),
    ("pacing and leading (RO)",
     "Înțeleg ce spui și are sens, dar hai să trecem la următorul pas."),
    ("Milton language (EN)",
     "You're probably wondering why, and because it matters, when you decide you'll "
     "notice the value, isn't it?"),
    ("reframing (RO)",
     "E un război cu adversarul: ori îi batem, ori pierdem."),
    ("submodalities (EN)",
     "The deal feels like a huge dark picture right in my face; the pressure is heavy and hot."),
    ("no NLP patterns (RO)",
     "Am trimis oferta revizuită și așteptăm răspunsul lor până vineri."),
]


def rule(char="=", width=78):
    print(char * width)


def summarize(domain: str, r: dict) -> list:
    """One or two compact lines describing a domain result."""
    if domain == "representation_systems":
        matched = {k: v for k, v in r["matched"].items() if v}
        if not matched:  # nothing matched -> only the default fallback, skip
            return []
        return [f"primary={r['primary_system']} scores={r['scores']} matched={matched}"]
    if domain == "anchoring":
        if not r["current_states"] and not r["has_anchor_reference"]:
            return []
        return [f"states={r['current_states']} anchor_ref={r['has_anchor_reference']} "
                f"cues={r['anchor_cues']}", f"-> {r['guidance']}"]
    if domain == "modeling":
        if not r["is_modeling"]:
            return []
        return [f"cues={r['modeling_cues']}", f"-> {r['prompt']}"]
    if domain == "pacing_and_leading":
        if r["stance"] == "neutral":
            return []
        return [f"stance={r['stance']} pacing={r['pacing_markers']} "
                f"resistance={r['resistance_markers']} lead={r['lead_markers']}",
                f"-> {r['guidance']}"]
    if domain == "milton_language":
        if not r["count"]:
            return []
        return [f"types={r['pattern_types']}",
                *[f"   {p['pattern']}: {p['keyword']!r} [{p['language']}]"
                  for p in r["patterns_detected"]]]
    if domain == "reframing":
        if r["current_frame"] == "unframed":
            return []
        return [f"frame={r['current_frame']} (present={r['frames_present']})",
                f"   context: {r['context_reframe'].splitlines()[0]}",
                f"   meaning: {r['meaning_reframe'].splitlines()[0]}"]
    if domain == "submodalities":
        if not r["detected"]:
            return []
        items = ", ".join(f"{d['submodality']}:{d['keyword']}" for d in r["detected"])
        return [f"modalities={r['modalities_present']} [{items}]"]
    return []


def main():
    nlp = NLPModule()
    for i, (target, statement) in enumerate(SAMPLES, start=1):
        rule()
        print(f"SAMPLE {i} — targets: {target}")
        print(f'Statement: "{statement}"')
        rule("-")
        result = nlp.analyze(statement)
        fired = False
        for domain, r in result.items():
            lines = summarize(domain, r)
            if lines:
                fired = True
                print(f"[{domain}]")
                for ln in lines:
                    print(f"  {ln}")
        if not fired:
            print("(no NLP patterns detected)")
        print()
    rule()
    print(f"Done. {len(SAMPLES)} samples processed.")


if __name__ == "__main__":
    main()
