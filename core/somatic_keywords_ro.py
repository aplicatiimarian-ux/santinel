# -*- coding: utf-8 -*-
"""
Romanian keyword lexicon for SANTINEL's Somatic framework
(core/somatic_module.py).

Structure: ``RO[domain] -> [phrases]`` for the somatic domains:
5 somatic patterns (breathing, tension, presence, confidence, embodied emotion)
and somatic cues (grounding, presence). Phrases are lowercase and diacritic-free
(the form core/text_norm.py normalizes input to); matching is also stem-aware.
The English side lives in somatic_module.py as ``EN`` with the same shape.
"""

RO = {
    "patterns": {
        "breathing_rhythm": [
            "imi lipseste respiratia", "inima imi bate tare", "respiratie superficiala",
            "inima bate repede", "nu pot respira", "respiratia e stransa",
            "suflul scurt", "respiratii repezi", "inima nu se linisteaza",
            "pieptul e strans", "respirare rapida", "nu-mi pot prinde sufletul",
            "respir repede", "respira profund",
        ],
        "tension_relaxation": [
            "umerele sunt tensionate", "incleștez maxilarul", "muschi tensionati",
            "relaxat", "tensiune in gat", "se-nmoaie", "muschi strânsi",
            "corp tensionat", "apasare", "umerele sus", "rigiditate", "liniste",
            "relaxare", "liber",
        ],
        "presence_dissociation": [
            "sunt aici", "prezent", "inradacinat", "plecat mental", "amorțit",
            "departe", "nu sunt aici", "in alt univers", "plutitor", "deconectat",
            "in momentul prezent", "constient", "acolo", "dizzy", "fuzzy", "airhead",
            "incarnat",
        ],
        "confidence_signals": [
            "stau drept", "umerele inapoi", "contact vizual", "vocea mea e puternica",
            "proiectare", "pozitie solida", "prezenta imperioasa", "sigur",
            "ezitant", "vocea nu-i stabila", "privesc in jos", "contradictie",
            "mic", "slab", "tremor",
        ],
        "embodied_emotion": [
            "inima mi se frânge", "simțul intestinelor", "gol in gat",
            "fluturi in burtă", "groaza in stomac", "strângeturi in piept",
            "constringe in gat", "tensiune in burtă", "inima bate tare",
            "caldura in piept", "frisoane reci", "simtind-o in oase",
            "instinctul spune", "stiu corpul",
        ],
    },
    "grounding_cues": [
        "picioare pe sol", "simt sezutul", "greutate", "solid", "inradacinat",
        "inradacinat", "stabil", "ancorat", "patru pe podea", "conectat la pamant",
        "picioarele mele", "fundament", "suportat", "tinut", "tinut de",
    ],
    "presence_cues": [
        "acum", "aici", "momentul asta", "prezent", "viu la", "acordat",
        "constient", "treaz", "atent", "concentrat", "implicat", "in flux",
        "in sincro", "pe punct", "acordat", "prezentul", "ce se intampla",
    ],
}
