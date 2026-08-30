# -*- coding: utf-8 -*-
"""
Romanian keyword lexicon for SANTINEL's NLP framework (core/nlp_module.py).

Structure: ``RO[domain][category] -> [phrases]``, one entry per the 7 NLP
domains the module analyzes. Phrases are stored lowercase and diacritic-free
(the form core/text_norm.py normalizes input to); matching is also stem-aware.
The English side lives in nlp_module.py as ``EN`` with the same shape.
"""

RO = {
    # 1. Representation systems (VAK) -----------------------------------------
    "representation_systems": {
        "visual": [
            "vad", "privesc", "imagine", "imi imaginez", "clar", "neclar",
            "perspectiva", "luminos", "intunecat", "arata", "observ",
            "vizualizez", "tablou", "in imagine de ansamblu", "punct de vedere",
        ],
        "auditory": [
            "aud", "ascult", "suna", "spune", "zice", "ton", "voce", "tacere",
            "zgomot", "rezoneaza", "in acord", "surd la", "mi se pare ca aud",
            "discutam", "ecou",
        ],
        "kinesthetic": [
            "simt", "prind ideea", "tin", "apas", "presiune", "greu", "usor",
            "cald", "rece", "aspru", "neted", "contact", "ating", "tensiune",
            "confortabil", "solid", "mi se pune un nod",
        ],
    },
    # 2. Anchoring ----------------------------------------------------------
    "anchoring": {
        "state_resourceful": [
            "increzator", "pregatit", "calm", "stapan pe situatie", "concentrat",
            "hotarat", "in control",
        ],
        "state_anxious": [
            "anxios", "tensionat", "ingrijorat", "nesigur", "panicat", "stresat",
            "mi-e teama",
        ],
        "state_assertive": [
            "ferm", "direct", "spun clar", "asertiv", "imi sustin pozitia",
        ],
        "state_defensive": [
            "defensiv", "inchis", "reticent", "pe pozitie de aparare", "suspicios",
            "ma feresc",
        ],
        "anchor_reference": [
            "data trecuta", "ultima oara", "cand am reusit", "imi amintesc cand",
            "ca atunci cand", "in trecut am", "am mai trecut prin asta",
        ],
    },
    # 3. Modeling ---------------------------------------------------------
    "modeling": {
        "exemplar_reference": [
            "cel mai bun negociator", "mentorul meu", "cum ar face", "cum ar proceda",
            "un profesionist ar", "modelul meu", "invat de la", "cineva experimentat ar",
        ],
        "admiration": [
            "il admir", "ma inspira", "as vrea sa fiu ca", "face asta perfect",
            "reuseste mereu",
        ],
    },
    # 4. Pacing and leading ---------------------------------------------
    "pacing_and_leading": {
        "pacing_marker": [
            "da si", "inteleg", "are sens", "sunt de acord", "exact asa", "asa e",
            "vad ce spui", "apreciez punctul tau",
        ],
        "resistance_marker": [
            "dar", "insa", "nu sunt de acord", "nu cred", "totusi", "ba nu",
            "nici vorba",
        ],
        "lead_marker": [
            "hai sa", "propun sa", "ce zici sa", "putem sa", "urmatorul pas",
            "sa trecem la", "as sugera sa",
        ],
    },
    # 5. Milton language (Milton Model) -------------------------------
    "milton_language": {
        "mind_read": [
            "stiu ca va intrebati", "va intrebati probabil", "stiu ce simti",
            "iti dai seama ca", "probabil ganditi",
        ],
        "lost_performative": [
            "e bine sa", "e important sa", "e firesc sa", "se stie ca",
            "e clar ca",
        ],
        "cause_effect": [
            "pentru ca", "asta inseamna ca", "pe masura ce", "fiindca",
            "tocmai de aceea",
        ],
        "presupposition": [
            "cand veti decide", "dupa ce alegeti", "inainte sa semnati",
            "de indata ce incepeti", "cat de repede veti observa",
        ],
        "universal_quantifier": [
            "mereu", "niciodata", "toata lumea", "oricine", "nimeni", "de fiecare data",
        ],
        "tag_question": [
            "nu-i asa", "nu credeti", "nu-i corect", "asa-i",
        ],
        "embedded_command": [
            "puteti incepe sa observati", "ati putea lua in calcul",
            "va invit sa va imaginati", "incepeti sa simtiti",
            "poate veti descoperi",
        ],
    },
    # 6. Reframing ------------------------------------------------------
    "reframing": {
        "frame_conflict": [
            "lupta", "razboi", "adversar", "atac", "ii batem", "invingem",
            "de partea cealalta",
        ],
        "frame_obstacle": [
            "blocat", "imposibil", "zid", "nu se poate", "fara iesire", "impas",
            "batem pasul pe loc",
        ],
        "frame_scarcity": [
            "nu ajunge", "prea putin", "pierdem", "resurse limitate", "nu e destul",
            "ori noi ori ei",
        ],
        "frame_blame": [
            "e vina lor", "din cauza lor", "ei sunt problema", "numai ei",
        ],
        "frame_opportunity": [
            "oportunitate", "ajungem la un acord", "valoare comuna", "castig reciproc",
            "gasim o solutie", "beneficiu pentru amandoi",
        ],
    },
    # 7. Submodalities ------------------------------------------------
    "submodalities": {
        "visual_brightness": ["luminos", "stralucitor", "intunecat", "sters", "palid"],
        "visual_size": ["urias", "imens", "enorm", "mic", "minuscul"],
        "visual_distance": ["aproape", "departe", "in fata mea", "in departare"],
        "visual_focus": ["clar", "in focus", "neclar", "incetosat", "blurat"],
        "auditory_volume": ["tare", "asurzitor", "incet", "in soapta", "abia se aude"],
        "auditory_tempo": ["rapid", "alert", "lent", "taraganat"],
        "kinesthetic_weight": ["greu", "apasator", "usor", "ca un fulg"],
        "kinesthetic_temperature": ["fierbinte", "cald", "rece", "inghetat"],
        "kinesthetic_tension": ["incordat", "tensionat", "relaxat", "destins"],
    },
}
