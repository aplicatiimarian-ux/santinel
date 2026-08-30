# -*- coding: utf-8 -*-
"""
Romanian keyword lexicon for SANTINEL's TA framework (core/ta_module.py).

Structure: ``RO[domain][category] -> [phrases]`` for the 3 TA domains the
module analyzes: functional ego states, life positions (I'm OK / You're OK
matrix) and the 5 sales games. Phrases are lowercase and diacritic-free (the
form core/text_norm.py normalizes input to); matching is also stem-aware.
The English side lives in ta_module.py as ``EN`` with the same shape.
"""

RO = {
    # Functional ego states ------------------------------------------------
    "ego_states": {
        "critical_parent": [
            "ar trebui sa", "trebuie sa", "e gresit", "e inadmisibil", "e inacceptabil",
            "de cate ori ti-am spus", "asa nu se face", "e rusinos", "cum ai putut",
        ],
        "nurturing_parent": [
            "lasa ca te ajut", "nu-ti face griji", "ai grija", "esti pe maini bune",
            "ma ocup eu de tine", "te inteleg, saracul", "hai ca reusesti",
        ],
        "adult": [
            "datele arata", "sa analizam optiunile", "care sunt faptele",
            "din punct de vedere logic", "sa cantarim", "pe baza cifrelor",
            "care e costul real", "sa vedem argumentele",
        ],
        "free_child": [
            "imi place la nebunie", "super", "abia astept", "ce tare", "haaa ce fain",
            "sa incercam ceva nou", "ma distrez",
        ],
        "adapted_child": [
            "scuze de deranj", "cum spuneti dumneavoastra", "cred ca da",
            "cum ziceti", "imi pare rau", "nu e corect fata de mine", "oricum nu conteaza parerea mea",
        ],
    },
    # Life positions (I'm OK / You're OK matrix) --------------------------
    "life_positions": {
        "i_ok_you_ok": [
            "castig reciproc", "respect reciproc", "amandoi avem de castigat",
            "gasim impreuna", "si eu si tu", "solutie buna pentru amandoi",
        ],
        "i_ok_you_not_ok": [
            "gresiti", "am dreptate", "habar n-au", "sunt niste amatori",
            "eu stiu cum se face", "nu se ridica la nivel", "ii depasesc",
        ],
        "i_not_ok_you_ok": [
            "probabil gresesc", "voi stiti mai bine", "nu ma pot compara cu voi",
            "sigur e vina mea", "nu sunt la nivelul vostru", "scuze ca va retin",
        ],
        "i_not_ok_you_not_ok": [
            "e fara speranta", "n-are rost", "pierdem si noi si ei", "oricum iese prost",
            "nu are nimeni de castigat", "toata lumea pierde",
        ],
    },
    # 5 sales games -----------------------------------------------------
    "games": {
        "hard_to_get": [
            "nu sunt sigur ca avem nevoie", "nu ne grabim", "avem si alte oferte",
            "poate alta data", "vedem noi", "nu depinde de asta", "nu insist",
        ],
        "rapo": [
            "chiar eram interesat, dar", "pareati perfecti pana", "nu va faceti iluzii",
            "v-am dat sperante degeaba", "credeam ca merge, insa acum nu",
        ],
        "kick_me": [
            "oricum o sa refuzati", "stiu ca e un moment prost", "ma pricep prost la asta",
            "mereu incurc preturile", "probabil o sa dau gres si acum", "iar am zis o prostie",
        ],
        "yes_but": [
            "da, dar nu merge", "am incercat deja asta", "da, insa bugetul",
            "da, dar nu avem timp", "suna bine, dar nu se poate",
        ],
        "wooden_leg": [
            "ce pretentii ai de la o echipa mica", "nu pot din cauza sistemului",
            "nu e vina mea, procesul", "ce sa fac daca asa e politica",
            "n-am cum, sunt doar eu aici",
        ],
    },
}
