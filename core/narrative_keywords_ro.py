# -*- coding: utf-8 -*-
"""
Romanian keyword lexicon for SANTINEL's Narrative framework
(core/narrative_module.py).

Structure: ``RO[domain] -> [phrases]`` for the narrative domains:
4 narrative archetypes, identity patterns (agency, passivity, connection),
and meaning patterns (growth, loss, purpose). Phrases are lowercase and
diacritic-free (the form core/text_norm.py normalizes input to); matching
is also stem-aware. The English side lives in narrative_module.py as ``EN``
with the same shape.
"""

RO = {
    "narratives": {
        "heros_journey": [
            "am intampinat o provocare", "am depasit", "am invatat", "am crescut",
            "a fost greu dar am reusit", "am luptat si am castigat", "am gasit o cale",
            "adversitatea m-a facut mai puternic", "am descoperit", "am perseverat",
            "m-am transformat", "dificultatea a dus la crestere", "am devenit",
            "din lupta a venit intelepciune",
        ],
        "victim_narrative": [
            "mi-a facut asta", "am fost tradat", "nu am control",
            "s-a intamplat mie", "ei intotdeauna", "sunt blocat", "neputincios",
            "sistemul e impotriva mea", "noroc rau", "sunt victima",
            "nu pot scapa", "sunt prins", "nu-mi permit",
        ],
        "victor_narrative": [
            "am castigat", "i-am infrant", "i-am dominat", "i-am strivit",
            "i-am batutz", "eu sunt castigator", "am iesit pe primul loc",
            "am cucerit", "strategia mea a functionat", "i-am depasit",
            "victoria e mea", "am dovedit ca sunt mai puternic", "intotdeauna castig",
        ],
        "collaborative_narrative": [
            "am lucrat impreuna", "amandoi am beneficiat", "am rezolvat impreuna",
            "colaborarea a dus la", "parteneriatul nostru", "am gasit o cale",
            "castig reciproc", "suntem mai puternici impreuna", "am creat impreuna",
            "scopul nostru comun", "succes colectiv", "am realizat impreuna",
        ],
    },
    "identity_patterns": {
        "agency": [
            "am decis", "am ales", "am facut", "am controlat", "am actionat",
            "am preluat comanda", "am condus", "am impulsionat", "am initiat",
            "am determinat", "in puterea mea", "eu sunt arhitectul", "am modelat",
            "am creat",
        ],
        "passivity": [
            "s-a intamplat", "mi s-a spus", "am trebuit sa", "nu am putut",
            "ei au decis", "circumstantele m-au fortat", "am fost obligat",
            "fara alegere", "am fost neputincios", "la mila lor",
            "mi s-a intamplat", "nu am avut cuvant", "am fost supus",
        ],
        "connection": [
            "am construit", "impreuna", "al nostru comun", "reciproc", "interdependent",
            "conectat", "parteneriat", "aliniat", "solidaritate", "uniti",
            "colectiv", "suntem in asta impreuna", "comun", "succes comun",
        ],
    },
    "meaning_patterns": {
        "growth": [
            "am invatat", "insight", "intelepciune", "transformare", "evolutie",
            "am devenit mai intelept", "am castigat intelegere", "perspectiva mai adanca",
            "vede lucrurile altfel acum", "apreciere noua", "crestere personala",
        ],
        "loss": [
            "pierdut", "risipitor", "distrus", "ruinat", "esuat",
            "rupt", "damatat", "irecuperabil", "niciodata nu se va recupera",
            "totul disparut", "nimic ramas", "final al", "gata",
        ],
        "purpose": [
            "pentru un motiv", "era sa", "scopul", "de ce conteaza asta",
            "sens mai mare", "tablou mai mare", "contribuie la", "serveste",
            "se aliniaza cu valorile", "are sens acum", "totul se potriveste",
            "punctul e", "inteleg acum de ce",
        ],
    },
}
