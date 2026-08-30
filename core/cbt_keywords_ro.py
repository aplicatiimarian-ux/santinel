# -*- coding: utf-8 -*-
"""
Romanian keyword lexicon for SANTINEL's CBT framework (core/cbt_module.py).

Keys are the string values of ``core.cbt_module.CognitivDistortion`` members.
Values are Romanian trigger phrases stored in the normalized form the matcher
compares against: lowercase, no diacritics (so "esec" also covers user input
"eșec"). Matching in ``CBTAssessment`` is additionally stem-aware, so a base
form such as "dezastru" also catches "dezastrul", "dezastre", etc.

Kept as plain data with no imports so ``cbt_module`` can import it without a
cycle. 16 distortion categories are covered.
"""

RO_DISTORTION_KEYWORDS = {
    "catastrophizing": [
        "dezastru",
        "catastrofa",
        "e sfarsitul",
        "totul e pierdut",
        "distrus",
        "ruinat",
        "o nenorocire",
        "nu mai am nicio sansa",
    ],
    "black_and_white": [
        "totul sau nimic",
        "esec total",
        "dezastru total",
        "perfect sau deloc",
        "ori reusesc ori pierd",
        "complet ratat",
    ],
    "overgeneralization": [
        "mereu",
        "intotdeauna",
        "niciodata",
        "de fiecare data",
        "tot timpul",
        "nimeni nu",
        "toata lumea",
        "toti sunt la fel",
    ],
    "mind_reading": [
        "ei cred ca",
        "el crede ca",
        "ea crede ca",
        "sigur ma considera",
        "stiu ca ma crede",
        "ma vad ca pe",
        "gandeste despre mine",
    ],
    "fortune_telling": [
        "o sa pierd",
        "voi esua",
        "sigur nu va merge",
        "n-o sa reusesc",
        "va fi un esec",
        "cu siguranta voi rata",
        "nu are cum sa iasa bine",
    ],
    "personalization": [
        "e vina mea",
        "din cauza mea",
        "numai eu sunt de vina",
        "eu am stricat tot",
        "e numai problema mea",
        "din pricina mea",
    ],
    "filtering": [
        "numai partea proasta",
        "doar ce e rau",
        "nimic bun",
        "ignor pozitivul",
        "cea mai proasta parte",
        "vad doar minusurile",
    ],
    "emotional_reasoning": [
        "simt ca asa e",
        "daca ma simt asa inseamna",
        "ma simt deci e adevarat",
        "sentimentul imi spune ca",
        "am o senzatie proasta deci",
    ],
    "should_statements": [
        "ar trebui sa",
        "trebuie neaparat sa",
        "sunt obligat sa",
        "musai sa",
        "n-ar fi trebuit sa",
        "e obligatoriu sa",
    ],
    "labeling": [
        "sunt un ratat",
        "sunt prost",
        "sunt incompetent",
        "sunt slab",
        "sunt un esec",
        "sunt inutil",
        "sunt o gluma",
    ],
    "disqualifying_positive": [
        "nu conteaza ca am reusit",
        "a fost doar noroc",
        "oricine ar fi putut",
        "nu inseamna nimic",
        "a fost o exceptie",
        "doar din intamplare",
    ],
    "magnification_minimization": [
        "e o catastrofa uriasa",
        "fac din tantar armasar",
        "nu e mare lucru ce am facut",
        "am umflat totul",
        "e neinsemnat ce am realizat",
        "exagerez enorm",
    ],
    "blaming": [
        "e numai vina lor",
        "ei sunt de vina",
        "din cauza lor",
        "el mi-a stricat tot",
        "ea a distrus totul",
        "numai clientul e de vina",
    ],
    "control_fallacy": [
        "nu depinde de mine",
        "nu pot schimba nimic",
        "sunt neputincios",
        "nu am niciun control",
        "totul e in mainile lor",
        "nu sta in puterea mea",
    ],
    "fairness_fallacy": [
        "nu e corect",
        "e nedrept",
        "ar trebui sa fie corect",
        "merit mai mult de atat",
        "e o nedreptate",
        "nu e drept fata de mine",
    ],
    "always_being_right": [
        "am dreptate oricum",
        "tu gresesti",
        "nu se poate sa gresesc",
        "eu stiu mai bine",
        "sigur am dreptate",
        "nu am cum sa ma insel",
    ],
}

# Tokens (diacritic-stripped, lowercased) that flag a negated context.
RO_NEGATION_TOKENS = {
    "nu",
    "n",
    "nici",
    "niciun",
    "nicio",
    "nicidecum",
    "deloc",
    "fara",
}
