# -*- coding: utf-8 -*-
"""
Romanian keyword lexicon for SANTINEL's Attachment framework (core/attachment_module.py).

Structure: ``RO[domain] -> [phrases]`` for the attachment-related domains:
anxiety (fear of abandonment), avoidance (discomfort with closeness), secure attachment,
and core wounds (abandonment, control, inadequacy, distrust). Phrases are lowercase and
diacritic-free (the form core/text_norm.py normalizes input to); matching is also stem-aware.
The English side lives in attachment_module.py as ``EN`` with the same shape.
"""

RO = {
    "anxiety_markers": {
        "anxiety": [
            "ma tem ca o sa ma parasesti", "si daca ma parasesti", "am nevoie de siguranta",
            "nu pleca de la mine", "nu pot suporta sa te pierd", "imi e groaza sa ma refuzi",
            "te rog nu pleca", "am nevoie sa confirm constant", "o sa rami cu mine?",
            "imi e teama sa fiu parasit", "imi e groaza", "si daca", "nu pot accepta",
            "am nevoie sa stiu", "o sa refuzi", "imi e teama",
        ],
    },
    "avoidance_markers": {
        "avoidance": [
            "nu am nevoie de nimeni", "apropierea ma inconfortabila", "prefer sa fiu singur",
            "relatiile sunt prea dependente", "tin distanta", "am nevoie de libertate",
            "nu-mi place sa depind de oameni", "intimitatea ma infoaca", "nu vreau sa vorbesc despre asta",
            "nu te apropia prea mult", "pot fara ajutor", "pot singur", "prefer independent", "nu am nevoie",
            "las-o asa", "nu pierde vreme", "singur e bine",
        ],
    },
    "secure_markers": {
        "secure": [
            "iti am incredere", "putem rezolva asta impreuna", "ma simt in siguranta cu tine",
            "sunt comfortabil sa fiu deschis", "pot conta pe tine", "sa fim sinceri impreuna",
            "apreciez perspectiva ta", "sunt sigur de noi", "pot fi vulnerabil",
            "putem face fata acestui lucru",
        ],
    },
    "wounds": {
        "abandonment": [
            "intotdeauna pleci", "intotdeauna sunt parasit", "nimeni nu ramane pentru mine",
            "o sa fiu singur", "vei gasit pe cineva mai bun", "nu sunt destul de important",
            "o sa ma refuzi ca pe toti ceilalti", "sunt de neplacut",
        ],
        "control": [
            "incerc sa ma controlez", "trebuie sa comand", "lasa sa decid",
            "nu incerc sa judeca", "ma domini", "trebuie sa fac singur",
            "daca-mi pasezi o sa fac cum spun", "trebuie sa control", "felul meu",
            "control total", "numai eu pot", "cum spun eu",
        ],
        "inadequacy": [
            "nu sunt destul de bun", "nu sunt destul de inteligent", "n-o sa fiu niciodata bun la asta",
            "te dezamagesc", "sunt prea lent", "nu merit sa-ti iei timp",
            "sunt incompetent", "nu o sa fiu la nivelul tau niciodata",
        ],
        "distrust": [
            "nu-ti cred", "minți", "nu pot avea incredere in nimeni",
            "toti m-au tradat", "nimeni nu spune adevarul", "ai scopuri ascunse",
            "te suspectez", "ascunzi ceva",
        ],
    },
}
