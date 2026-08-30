# -*- coding: utf-8 -*-
"""
Romanian keyword lexicon for SANTINEL's Neuroscience framework
(core/neuroscience_module.py).

Structure: ``RO[domain] -> [phrases]`` for the neurobiological domains:
5 patterns (amygdala, reward, mirror neurons, default mode, vagal tone) and
nervous system states (sympathetic, parasympathetic, balanced). Phrases are
lowercase and diacritic-free (the form core/text_norm.py normalizes input to);
matching is also stem-aware. The English side lives in neuroscience_module.py
as ``EN`` with the same shape.
"""

RO = {
    "patterns": {
        "amygdala_activation": [
            "sunt ingrijorat", "ma simt amenintat", "sunt defensiv", "imi e teama",
            "asta ma face nervos", "sunt in alerta", "pot simti inima batandu-mi",
            "lupta sau fuga", "sunt activat", "pericol", "asta ma declanseaza",
            "nu ma simt in siguranta", "alarma", "amenintare",
        ],
        "reward_system": [
            "asta ma incanta", "sunt motivat", "ma intereseaza", "asta imi place",
            "sunt atras de", "asta e gratifiant", "ma bucur", "asta ma motiveaza",
            "sunt implicat", "asta ma aprinde", "sunt entuziast", "placere",
            "vreau asta", "captivant",
        ],
        "mirror_neurons": [
            "rezonez cu tine", "simt ce simti tu", "ma vad in tine",
            "sunt atent la tine", "suntem pe aceeasi lungime de unda", "te oglindesc",
            "simt preocuparea ta", "suntem aliniate", "inteleg", "inteleg",
            "te urmăresc", "suntem sincro", "empatia",
        ],
        "default_mode_network": [
            "ma gandesc prea mult", "sunt blocat mental", "ma gândesc prea mult la",
            "nu pot inchide gândurile despre", "daca", "asta imi aminteste de",
            "sunt ingrijorat de viitor", "continuu sa retraiesc", "auto-indoiala",
            "poveste", "narativ", "asta inseamna", "sunt in propriul meu univers",
        ],
        "vagal_tone": [
            "ma simt calm", "sunt relaxat", "pot respira ușor", "sunt asezat",
            "sunt inradacinat", "ma simt in pace", "sistemul meu nervos e calm",
            "sunt prezent", "sunt centrat", "social", "conectat", "in siguranta",
            "pot incetini", "claritate",
        ],
    },
    "nervous_system": {
        "sympathetic": [
            "raspuns la stres", "lupta sau fuga", "activat", "adrenalina",
            "alerta inalta", "defensiv", "reactiv", "urgent", "mod de urgenta",
            "presiune", "tensionat", "in garda", "vigilent", "inima bate repede",
        ],
        "parasympathetic": [
            "odihnă si digestie", "raspuns calm", "relaxat", "linistit", "asezat",
            "inradacinat", "prezent", "deschidere", "conexiune", "implicare sociala",
            "ton vagal", "deescaladare", "pasnic", "incredulos", "sigur",
        ],
        "balanced": [
            "stare optima", "gandire clara", "flexibil", "responsiv",
            "implicat dar calm", "alerta dar relaxat", "constinta", "prezenta",
            "integrare", "fereastra de toleranta", "rezilent", "adaptabil",
        ],
    },
}
