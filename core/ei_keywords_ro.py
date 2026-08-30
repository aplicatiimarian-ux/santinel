# -*- coding: utf-8 -*-
"""
Romanian keyword lexicon for SANTINEL's EI framework (core/ei_module.py).

Structure: ``RO[domain][category] -> [phrases]`` for the 2 EI domains the
module analyzes: Goleman's 5 emotional intelligence competencies and 6 emotional
states. Phrases are lowercase and diacritic-free (the form core/text_norm.py
normalizes input to); matching is also stem-aware. The English side lives in
ei_module.py as ``EN`` with the same shape.
"""

RO = {
    # Goleman's 5 competencies -----------------------------------------------
    "competencies": {
        "self_awareness": [
            "ma simt", "sunt ingrijorat", "imi dau seama", "observ", "vad cum",
            "ar putea sa fiu", "preocuparea mea e", "sunt constient ca",
            "simt ca", "ceea ce traiesc e",
        ],
        "self_regulation": [
            "sa fiu putin mai calm", "pot face fata", "sa ramanem linistiti",
            "o sa ma gandesc bine", "nu o sa reactionez", "glas adanc", "reconsider",
            "am controlul", "in ciuda sentimentelor", "pot sa gestionez asta",
        ],
        "motivation": [
            "sunt angajat in", "sunt determinat", "putem gasit o cale", "cred in",
            "e important pentru mine", "sunt concentrat pe", "sa continuam",
            "nu voi renunta", "scopul e", "o vom rezolva",
        ],
        "empathy": [
            "inteleg cum te simti", "trebuie sa fii", "din perspectiva ta",
            "inteleg de ce", "te ingrijoreaza", "nevoile tale sunt", "te ascult",
            "e important pentru tine", "vrei", "gasesc",
        ],
        "social_skills": [
            "sa lucram impreuna", "ce crezi tu", "cum putem", "gasim o solutie",
            "apreciez opinia ta", "putem colabora", "ascult", "ce e bine pentru tine",
            "sa ne intelegem", "gasim punct comun",
        ],
    },
    # 6 emotional states -----------------------------------------------
    "emotional_states": {
        "openness": [
            "sunt interesat", "spune mai mult", "e interesant", "sa exploram",
            "sunt deschis", "vreau sa inteleg", "mai mult", "n-am gandit asa",
            "fascinant", "ajuta-ma sa inteleg",
        ],
        "skepticism": [
            "nu sunt sigur", "asta nu are sens", "am indoieli", "chiar?",
            "cum poti fi sigur", "nu cred", "e discutabil", "arata-mi dovada",
            "nu sunt convins", "pare putin probabil",
        ],
        "frustration": [
            "nu ajungem nicaieri", "mergem in cerc", "asta nu merge", "obosit de",
            "destul", "e fara sens", "da seama", "pe serios?", "e ridicol",
            "am ajuns la capat cu",
        ],
        "curiosity": [
            "de ce se intampla", "cum functioneaza", "daca", "putem incerca",
            "ma intreb", "sa testam", "daca s-ar intampla", "ai luat in seama",
            "unghi interesant", "as vrea sa explorez",
        ],
        "fear": [
            "ma ingrijeaza", "daca se inrautateste", "ma tem", "ar putea fi riscant",
            "nu ma simt in siguranta", "e periculos", "sunt preocupat de",
            "care e cel mai rau", "sunt nervos", "asta ma spaimanta",
        ],
        "acceptance": [
            "pot traii cu asta", "e ok pentru mine", "sunt de acord", "suna bine",
            "sunt comfortabil cu", "e acceptabil", "sa mergem inainte",
            "avem o intelegere", "sunt satisfacut", "e corect",
        ],
    },
}
