# -*- coding: utf-8 -*-
"""
Romanian keyword lexicon for SANTINEL's Feedback Extraction framework
(core/feedback_extraction_module.py).

Structure: ``RO[domain] -> [phrases]`` for verbal and vocal signals.
Phrases are lowercase and diacritic-free (the form core/text_norm.py normalizes
input to); matching is also stem-aware. The English side lives in
feedback_extraction_module.py as ``EN`` with the same shape.
"""

RO = {
    "verbals": {
        "agreement": [
            "da", "absolut", "suna bine", "merge pentru mine", "asta merge",
            "sunt de acord", "hai sa facem", "sunt in", "conteaza pe mine",
            "hai sa mergem inainte", "sunt de acord", "perfect", "exact",
            "asa e", "ai dreptate",
        ],
        "doubt": [
            "nu sunt sigur", "confuz", "indeciş", "ar putea", "posibil",
            "poate", "nu stiu", "nesigur", "discutabil", "putea merge în oricare direcţie",
            "pe gard", "incetar", "in aer", "putin", "depinde",
        ],
        "objection": [
            "dar", "totusi", "problema", "preocupare", "problema", "nu pot",
            "nu voi", "nu sunt de acord", "asta nu merge", "nu sunt confortabil",
            "asta nu-i corect", "rezistenta", "asta nu-i acceptabil", "am preocupari",
            "problematic",
        ],
        "stalling": [
            "lasa-ma sa mă gândesc", "am nevoie de timp", "lasa-ma sa verific",
            "revino mai tarziu", "da-mi timp", "trebuie sa discuti", "trebuie sa consult",
            "vorbesc cu", "eventual", "o sa-ti revin", "nu acum", "nu inca",
            "mai tarziu", "in curand",
        ],
        "questions": [
            "daca", "cum", "cand", "unde", "de ce", "spune-mi mai mult",
            "poti", "ai putea", "e posibil", "ai luat in seama",
            "ce zici de", "alte optiuni", "clarifica", "explica", "detalii",
        ],
        "urgency": [
            "acum", "azi", "asap", "termen", "urgent", "grabind", "repede",
            "imediat", "sensibil la timp", "curand", "inainte", "fereastra limitata",
            "data de inchidere", "nu pot astepyta", "trebuie sa se intample",
            "critic",
        ],
        "budget": [
            "buget", "pret", "cost", "isi permite", "investitie", "bani",
            "cheltuiala", "financiar", "fonduri", "capital", "plata",
            "tarif", "margine", "pret", "cat", "care-i costul",
            "termeni de plata", "roi", "valoare",
        ],
        "competitive": [
            "competitie", "alternative", "alte oferte", "comparat cu",
            "versus", "competitorul tau", "alte optiuni", "deal mai bun",
            "undeva", "imboldesc", "benchmark", "avantaj competitiv",
            "ei ofera", "comparand preturi", "alti furnizori", "cautand",
            "explorand optiuni",
        ],
    },
    "vocals": {
        "high_pitch": [
            "pas sus", "vocea se ridica", "ton mai inalt", "pitch crescut",
            "strident", "voce tensionata", "gat strans", "squeaky", "voce tensionata",
        ],
        "low_pitch": [
            "voce adanca", "ton jos", "ton inradacinat", "bass", "voce calmă",
            "ton sigur", "autoritativ", "rezonant", "voce linistita",
        ],
        "fast_pace": [
            "vorbire rapida", "vorba repede", "pas accelerat", "cuvinte grabite",
            "grabind", "fara suflet", "livrare rapida", "vorbind repede",
            "staccato",
        ],
        "slow_pace": [
            "pas masurat", "vorbire lenta", "deliberat", "iau timp",
            "pauza intre", "livrare ganditoare", "punand in cumpene", "cuvinte atente",
            "lent si stabil",
        ],
        "high_energy": [
            "energic", "animat", "ton entuziast", "entuziasm", "viu",
            "pozitiv", "implicat", "apasionat", "vibrant", "dinamic",
        ],
        "low_energy": [
            "ton plat", "monoton", "fara entuziasm", "dezangajat", "apatica",
            "voce oboşita", "deflatata", "resemnata", "pasiva", "plictisita",
        ],
        "shallow_breathing": [
            "sufletul scurt", "oftand", "prindand sufletul", "respiratie rapida",
            "fara suflet", "oftatare", "respiratie stransa", "respiratie in piept",
        ],
        "deep_breathing": [
            "respiratie adanca", "respiratie burta", "respiratie inradacinata",
            "respir stabil", "respiratie lenta", "respiratie linistita",
            "respir complet", "respiratie diafragma",
        ],
        "hesitation_pauses": [
            "uh", "um", "err", "pauza lunga", "trail off", "balbait",
            "pauze umplute", "filler vocal", "indecizie", "tacere lunga",
        ],
        "thinking_pauses": [
            "pauza ca sa ma gandesc", "moment linistit", "considerand",
            "reflectand", "iau timp", "adunand ganduri", "pauza ganditoare",
        ],
        "warm_tone": [
            "voce calda", "ton prietenos", "abordabil", "incluziv", "invitator",
            "autentic", "personabil", "ton deschis", "margine moale", "ingrijitor",
        ],
        "cold_tone": [
            "voce rece", "ton distant", "formal", "sec", "ton ascutit",
            "retras", "detasat", "clinic", "ton defensiv", "margine greu",
        ],
        "emphasis_positive": [
            "stres pe pozitiv", "evidentiaza beneficiu", "enfatizeaza castig",
            "inflexiune in sus pe pozitiv", "putere in livrare", "accent pe bun",
        ],
        "emphasis_negative": [
            "stres pe negativ", "evidentiaza risc", "enfatizeaza pierdere",
            "inflexiune in jos", "accent pe problema", "greutate pe preocupare",
            "enfatizare pe indoiala",
        ],
        "laughter": [
            "rasa", "rasete", "chuckle", "rasa nervoasa", "rasa fortata",
            "rasa autentica", "rasa usoara", "rasa pline", "risete",
        ],
    },
}
