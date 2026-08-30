# -*- coding: utf-8 -*-
"""
Romanian keyword lexicon for SANTINEL's Behavioral Economics framework
(core/behavioral_econ_module.py).

Structure: ``RO[domain][category] -> [phrases]`` for the 6 cognitive biases
the module detects: loss aversion, anchoring, sunk cost fallacy, framing effect,
status quo bias, and availability heuristic. Phrases are lowercase and diacritic-free
(the form core/text_norm.py normalizes input to); matching is also stem-aware.
The English side lives in behavioral_econ_module.py as ``EN`` with the same shape.
"""

RO = {
    "biases": {
        "loss_aversion": [
            "nu pot sa pierd", "riscul e prea mare", "o sa pierdem bani",
            "e prea riscant", "imi e teama sa pierd", "dezavantajul e",
            "am putea pierde totul", "nu e gata riscul", "daca esueaza",
            "penalitatea e aspra", "nu pot accepta pierderea asta", "prea mult de pierdut",
            "nu putem risca", "riscul e", "s-ar duce rau",
        ],
        "anchoring": [
            "pretul de start e", "trebuie sa incepem cu", "prima oferta e",
            "numarul pe care vorbim e", "ma ancor pe", "valoarea de baza e",
            "am stabilit ca", "cifra e fixa la", "am zis", "suma e",
            "asta e numarul", "ancorul meu", "rata de piata", "primul numar",
            "nu ma misc de", "negocierea e in jurul",
        ],
        "sunk_cost_fallacy": [
            "am cheltuit deja", "dupa ce investisem", "vazand ce pusesem",
            "nu putem irosi ce cheltuisem", "deja m-am angajat", "lucram deja la asta",
            "ganditi la timp investit", "am ajuns prea departe ca sa opresc",
            "prea multi in joc acum", "nu putem arunca",
        ],
        "framing_effect": [
            "daca nu facem asta", "alternativa e mai rea", "singura optiune e",
            "trebuie sa", "o sa regretam daca nu", "e fie sau", "chestia arata ca",
            "problema e prezentata ca", "daca pierdem asta", "altfel va trebui",
        ],
        "status_quo_bias": [
            "am facut asa intotdeauna", "merge pana acum", "de ce sa schimbam",
            "aranjamentul actual e", "lucrul sunt ok cum sunt", "nu rezolva ce nu-i stricat",
            "stim cum merge", "lasam status quo", "confortabil cu", "schimbarea e riscanta",
            "lasati cum e",
        ],
        "availability_heuristic": [
            "imi amintesc cand", "in cazuri recente", "exemplul recent", "bazandu-me pe ce s-a intamplat",
            "toti stiu ca", "evident din", "vezi peste tot", "i-am vazut intamplandu-se",
            "modelul comun e", "situatii similare arata", "caz din urma", "asa se intampla",
            "din urma", "cazuri ca asta", "a esuat groaznic", "se termina prost",
            "imi amintesc", "cand am", "timpul trecut",
        ],
    },
}
