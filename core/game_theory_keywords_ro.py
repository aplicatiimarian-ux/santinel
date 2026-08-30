# -*- coding: utf-8 -*-
"""
Romanian keyword lexicon for SANTINEL's Game Theory framework
(core/game_theory_module.py).

Structure: ``RO[domain][category] -> [phrases]`` for the game-theoretic
domains: 4 game archetypes, strategic positions, BATNA, and ZOPA.
Phrases are lowercase and diacritic-free (the form core/text_norm.py normalizes
input to); matching is also stem-aware. The English side lives in
game_theory_module.py as ``EN`` with the same shape.
"""

RO = {
    "games": {
        "prisoners_dilemma": [
            "daca cooperez si tu nu", "amandoi castigam daca cooperam", "incredere reciproca",
            "daca ma tradezi", "nu pot sa cred ca cooperezi", "si daca ma intepezi",
            "ar fi bine daca amandoi", "dar s-ar putea defecta", "defectiunea e ispita",
            "cooperez daca si tu", "ochi cu ochi",
        ],
        "zero_sum": [
            "ce castig eu pierzi tu", "fiecare leu salvat e leu pierdut de mine",
            "castig tău e pierdere mea", "nu putem castiga amandoi", "e fie tu fie eu",
            "cineva trebuie sa piarda", "profitul tau e costul meu", "margina mea e cheltuiala ta",
            "incerc sa ma striveasca", "castigi pe seama mea", "joc zero sum", "parghie",
            "optiuni pe care nu le ai",
        ],
        "coordination_game": [
            "amandoi castigam daca aliniem", "trebuie sa coordonam", "hai sa sincronizam",
            "vrem acelasi lucru", "suntem pe acelasi lagăr", "amandoi preferăm",
            "coordinarea e cheie", "trebuie sa fim sincro", "amandoi vrem", "provocarea e sa fim de acord cum",
            "suntem aliati",
        ],
        "battle_of_sexes": [
            "eu prefer asta, tu prefera ala", "nu suntem de acord cu", "preferinta ta vs a mea",
            "vrem lucruri diferite", "vrem sa fim de acord, dar cum", "tu vrei asa, eu vreau asa",
            "opinii diferite", "tu valori asta, eu asa", "suntem in dezacord cu", "dezacord privind prioritati",
        ],
    },
    "strategic_positions": {
        "dominant": [
            "am cartele in mana", "am parghie", "am nevoie mai mult decat ei",
            "pot sa plec", "am optiuni", "eu conduc", "puterea e de partea mea",
            "sunt intr-o pozitie puternica", "sunt disperati", "pot sa astept",
            "nu si-au permite pierderea",
        ],
        "advantageous": [
            "am un avantaj mic", "pozitia mea e mai puternica", "sunt mai bine pozitionat",
            "am parghie", "am plan de rezerva", "nu sunt disperat",
            "am flexibilitate", "sunt intr-un loc rezonabil bun", "am optiuni pe care ei nu le au",
            "nu sunt la fel de expus ca ei",
        ],
        "parity": [
            "suntem potriviti egal", "suntem pe picior egal", "amandoi avem nevoie",
            "dependenta reciproca", "suntem intr-o pozitie echilibrata", "niciunu nu-si poate permite pierdere",
            "suntem echivalenti", "amandoi avem parghie", "e o lupta corecta",
            "suntem egal pozitionati", "pat",
        ],
        "disadvantaged": [
            "ei au cartele", "ei conduc", "am nevoie mai mult decat ei",
            "sunt intr-o pozitie slaba", "pot pleca usor", "sunt disperat",
            "nu am rezerva", "ei au optiuni pe care nu le am", "sunt blocat",
            "puterea e de partea lor", "sunt dezavantajat",
        ],
    },
    "batna": [
        "plan de rezerva e", "daca cade asta", "alternativa e", "pragul meu de plecare e",
        "in cel mai rau caz", "daca nu ajungem la acord", "retragerea e", "cea mai buna alternativa",
        "optiunea externa e", "daca negotiatia esueaza", "pot intotdeauna",
    ],
    "zopa": [
        "amandoi castigam daca", "suprapunerea e", "e loc pentru ca amandoi sa castigam",
        "pragul tau e", "minimul meu e", "amandoi putem accepta", "punctul comun e",
        "zona de acord", "amandoi putem trai cu", "castig reciproc daca",
        "domeniul unde amandoi", "ambele acceptable la",
    ],
}
