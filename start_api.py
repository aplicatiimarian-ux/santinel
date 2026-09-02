# -*- coding: utf-8 -*-
"""
SANTINEL API Gateway — real framework analysis.

`/analyze` routes the negotiation text through all 10 psychology framework
modules in `core/`, extracts a headline finding + confidence + coaching
suggestion from each, and aggregates them into the shape the web app expects
(`close_probability`, `frameworks`, `top_frameworks`, `coaching`).

Output language is controlled by `?lang=`:
  - `?lang=both` (default) → every human-readable field is `{"en": ..., "ro": ...}`
  - `?lang=en` / `?lang=ro` → fields are flat strings in that language
"""

import os
import re
import sys
sys.path.insert(0, '.')

from typing import Callable, Dict, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()

_SYMBOL_RE = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿←-⇿️•▪●]"
)

import requests
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from auth_guard import get_current_user

# --------------------------------------------------------------------------- #
#  Live transcription (FAZA 23.2) — thin, stateless proxy to Groq Whisper.    #
#  Audio bytes are read, forwarded, and discarded; nothing is persisted.      #
# --------------------------------------------------------------------------- #

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_STT_MODEL = os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo").strip()
GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
MAX_AUDIO_BYTES = 25 * 1024 * 1024  # Groq per-file limit

# --------------------------------------------------------------------------- #
#  Framework module imports (graceful — a missing module just drops out)      #
# --------------------------------------------------------------------------- #

_MODULE_SPECS = [
    ("cbt", "core.cbt_module", "CBTAssessment"),
    ("nlp", "core.nlp_module", "NLPModule"),
    ("ta", "core.ta_module", "TAModule"),
    ("ei", "core.ei_module", "EIModule"),
    ("attachment", "core.attachment_module", "AttachmentModule"),
    ("behavioral_econ", "core.behavioral_econ_module", "BehavioralEconomicsModule"),
    ("game_theory", "core.game_theory_module", "GameTheoryModule"),
    ("neuroscience", "core.neuroscience_module", "NeuroscienceModule"),
    ("narrative", "core.narrative_module", "NarrativeModule"),
    ("somatic", "core.somatic_module", "SomaticModule"),
]

FRAMEWORK_ORDER = [slug for slug, _, _ in _MODULE_SPECS]

_INSTANCES: Dict[str, object] = {}
for _slug, _mod_path, _cls_name in _MODULE_SPECS:
    try:
        _mod = __import__(_mod_path, fromlist=[_cls_name])
        _INSTANCES[_slug] = getattr(_mod, _cls_name)()
    except Exception as exc:  # pragma: no cover - import diagnostics
        print(f"[santinel] could not load {_mod_path}: {exc}")
        _INSTANCES[_slug] = None


# --------------------------------------------------------------------------- #
#  Bilingual helpers                                                          #
# --------------------------------------------------------------------------- #

def bi(en: str, ro: str, lang: str):
    """Return {en, ro} for lang='both', otherwise the single requested string."""
    if lang == "en":
        return en
    if lang == "ro":
        return ro
    return {"en": en, "ro": ro}


def humanize(token: Optional[str]) -> str:
    if not token:
        return "No clear signal"
    return token.replace("_", " ").strip().capitalize()


def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    if isinstance(text, (list, tuple)):
        text = " ".join(str(t) for t in text)
    text = _SYMBOL_RE.sub("", str(text))
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text)
    # drop shouty ALL-CAPS lead-ins like "CBT COACHING INTERVENTION:"
    text = re.sub(r"^[A-Z][A-Z \-]{6,}:\s*", "", text.strip())
    return text.strip()


def first_sentences(text: Optional[str], n: int = 2, limit: int = 220) -> str:
    text = clean_text(text)
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = " ".join(p.strip() for p in parts[:n] if p.strip()).strip()
    if len(out) > limit:
        out = out[:limit].rsplit(" ", 1)[0].rstrip(",;: ") + "…"
    return out


# Headline label translations (token -> Romanian). Unknown tokens fall back to
# an English-ish humanized form, which is acceptable and never crashes.
RO_LABELS: Dict[str, str] = {
    # CBT cognitive distortions
    "catastrophizing": "Catastrofizare",
    "black_and_white": "Gândire în alb-negru",
    "overgeneralization": "Suprageneralizare",
    "mind_reading": "Citirea gândurilor",
    "fortune_telling": "Ghicitul viitorului",
    "personalization": "Personalizare",
    "filtering": "Filtrare negativă",
    "emotional_reasoning": "Raționament emoțional",
    "should_statements": "Afirmații cu «trebuie»",
    "labeling": "Etichetare",
    "disqualifying_positive": "Desconsiderarea pozitivului",
    "magnification_minimization": "Amplificare / minimalizare",
    "blaming": "Învinovățire",
    "control_fallacy": "Iluzia controlului",
    "fairness_fallacy": "Iluzia corectitudinii",
    "always_being_right": "Nevoia de a avea mereu dreptate",
    # TA ego states / life positions
    "parent": "Stare de Părinte",
    "adult": "Stare de Adult",
    "child": "Stare de Copil",
    "critical_parent": "Părinte critic",
    "nurturing_parent": "Părinte protector",
    "free_child": "Copil liber",
    "adapted_child": "Copil adaptat",
    "rebellious_child": "Copil rebel",
    "i_ok_you_ok": "Eu OK / Tu OK",
    "i_ok_you_not_ok": "Eu OK / Tu nu ești OK",
    "i_not_ok_you_ok": "Eu nu sunt OK / Tu OK",
    "i_not_ok_you_not_ok": "Eu nu sunt OK / Tu nu ești OK",
    # EI emotional states / competencies
    "openness": "Deschidere",
    "skepticism": "Scepticism",
    "frustration": "Frustrare",
    "curiosity": "Curiozitate",
    "fear": "Teamă",
    "acceptance": "Acceptare",
    "anxiety": "Anxietate",
    "excitement": "Entuziasm",
    "enthusiasm": "Entuziasm",
    "calm": "Calm",
    "grounded": "Ancorat",
    "neutral": "Neutru",
    "empathy": "Empatie",
    "self_awareness": "Conștiență de sine",
    "self_regulation": "Autoreglare",
    "motivation": "Motivație",
    "social_skills": "Abilități sociale",
    # Attachment styles
    "secure": "Atașament securizant",
    "anxious": "Atașament anxios",
    "avoidant": "Atașament evitant",
    "fearful_avoidant": "Atașament anxios-evitant",
    # Behavioral economics biases
    "loss_aversion": "Aversiune față de pierdere",
    "anchoring": "Ancorare",
    "sunk_cost_fallacy": "Eroarea costului irecuperabil",
    "framing_effect": "Efectul de încadrare",
    "status_quo_bias": "Preferința pentru status quo",
    "availability_heuristic": "Euristica disponibilității",
    "social_proof": "Dovada socială",
    "scarcity": "Raritate",
    "endowment_effect": "Efectul de posesie",
    "confirmation_bias": "Confirmarea propriei păreri",
    # Game theory archetypes / positions
    "prisoners_dilemma": "Dilema prizonierului",
    "zero_sum": "Joc cu sumă nulă",
    "coordination_game": "Joc de coordonare",
    "battle_of_sexes": "Bătălia sexelor",
    "stag_hunt": "Vânătoarea de cerb",
    "chicken": "Jocul curajului",
    "non_zero_sum": "Joc cu sumă non-nulă",
    "cooperative": "Joc cooperativ",
    "dominant": "Poziție dominantă",
    "advantageous": "Poziție avantajoasă",
    "parity": "Echilibru de forțe",
    "disadvantaged": "Poziție dezavantajată",
    # Neuroscience
    "sympathetic": "Sistem nervos simpatic (alertă)",
    "parasympathetic": "Sistem nervos parasimpatic (calm)",
    "balanced": "Sistem nervos echilibrat",
    "amygdala_activation": "Activarea amigdalei",
    "reward_system": "Sistem de recompensă activ",
    "mirror_neurons": "Neuroni-oglindă activi",
    "vagal_tone": "Ton vagal ridicat",
    "default_mode_network": "Rețea neuronală în repaus",
    "safety_reward_engagement": "Angajare din siguranță și recompensă",
    "threat_activation": "Activare de amenințare",
    # Narrative archetypes
    "heros_journey": "Călătoria eroului",
    "victim_narrative": "Narațiune de victimă",
    "victor_narrative": "Narațiune de învingător",
    "collaborative_narrative": "Narațiune colaborativă",
    # Somatic sub-states
    "dysregulated": "dereglat",
    "present": "prezent",
    "dissociated": "disociat",
    "confident": "încrezător",
    # NLP representation systems
    "visual": "Sistem reprezentațional vizual",
    "auditory": "Sistem reprezentațional auditiv",
    "kinesthetic": "Sistem reprezentațional kinestezic",
    "digital": "Sistem reprezentațional logic-digital",
}


def ro_label(token: Optional[str]) -> str:
    if not token:
        return "Semnal neconcludent"
    if token in RO_LABELS:
        return RO_LABELS[token]
    # compound like "grounded + present + confident"
    if " + " in token:
        return " + ".join(RO_LABELS.get(p.strip(), humanize(p)) for p in token.split(" + "))
    return humanize(token)


# Curated Romanian coaching suggestions for the frameworks whose modules do not
# emit a per-branch coaching string. One generic line per framework, plus a few
# keyed by finding token.
RO_SUGGESTIONS: Dict[str, Dict[str, str]] = {
    "cbt": {
        "_": "Provoacă gândul cu dovezi observabile: separă faptele de interpretare și vezi ce probe susțin concluzia.",
        "catastrophizing": "Recalibrează scenariul: «Care e cel mai rău caz realist și cum l-am gestiona?» Treci de la panică la plan.",
        "overgeneralization": "Înlocuiește «mereu/niciodată» cu concret: ce caz, când, cât de des. Un exemplu nu e un tipar.",
        "black_and_white": "Caută opțiunea de mijloc între cele două extreme; majoritatea acordurilor stau acolo.",
        "mind_reading": "Verifică presupunerea direct: întreabă ce cred ei, nu ghici intenția.",
        "should_statements": "Schimbă regula rigidă cu o preferință: «aș vrea X», nu «trebuie neapărat X».",
        "emotional_reasoning": "Certitudinea emoțională nu e dovadă. Numește emoția, apoi caută faptele de sub ea.",
    },
    "attachment": {
        "_": "Oferă predictibilitate: pași clari, termene clare, follow-through. Siguranța relației deschide conversația reală.",
        "anxious": "Redu incertitudinea: confirmă pe scurt, dă un calendar clar și revino cu update-uri la timp.",
        "avoidant": "Respectă autonomia: scade presiunea, lasă spațiu de decizie și evită ultimatumurile.",
        "fearful_avoidant": "Mergi încet și consecvent: oferă simultan siguranță și libertate de alegere.",
        "secure": "Bază relațională solidă. Poți trece direct la conținut și la rezolvarea problemei.",
    },
    "behavioral_econ": {
        "_": "Numește distorsiunea decizională și readu discuția la cifre și criterii obiective.",
        "loss_aversion": "Reformulează în termeni de câștig: ce se pierde prin inacțiune, nu doar riscul acțiunii.",
        "anchoring": "Nu contra-ancora imediat; adu un reper independent (piață, alternative) înainte de a discuta cifra.",
        "framing_effect": "Testează decizia în ambele încadrări (câștig și pierdere) înainte de a o accepta.",
        "sunk_cost_fallacy": "Decide pe baza valorii viitoare, nu a investiției deja făcute.",
    },
    "narrative": {
        "_": "Separă faptele de interpretare: «Faptele sunt X; povestea pe care ne-o spunem este Y».",
        "victim_narrative": "Redă agentivitatea: mută discuția spre ce poate controla și alege interlocutorul acum.",
        "victor_narrative": "Reîncadrează din «cucerire» în «rezultat comun»: câștigul durabil vine din acord, nu din dominare.",
        "collaborative_narrative": "Poveste favorabilă. Consolideaz-o cu limbaj de parteneriat și pași comuni.",
        "heros_journey": "Folosește energia de creștere: încadrează obstacolul ca etapă spre un rezultat mai bun.",
    },
    "somatic": {
        "_": "Verifică-ți corpul: picioarele pe podea, respirație lentă. Semnalează siguranță prin ton calm și postură deschisă.",
        "grounded": "Stare corporală optimă. Ascultă profund, mergi încet, lasă deciziile să se maturizeze.",
        "dysregulated": "Pauză scurtă. Respiră adânc, ancorează-te, apoi reia negocierea din calm.",
    },
}

EN_SUGGESTIONS: Dict[str, Dict[str, str]] = {
    "cbt": {
        "_": "Challenge the thought with observable evidence: separate fact from interpretation, ask what actually supports the conclusion.",
        "catastrophizing": "Rescale the outcome: 'What is the realistic worst case, and how would we handle it?' Move from dread to plan.",
        "overgeneralization": "Replace 'always/never' with specifics: which case, when, how often. One data point is not a pattern.",
        "black_and_white": "Find the middle option between the two extremes on the table; most deals live there.",
        "mind_reading": "Check the assumption directly: ask what they actually think instead of guessing their intent.",
        "should_statements": "Swap the rigid rule for a preference: 'I'd like X' instead of 'they must X'.",
        "emotional_reasoning": "Feeling certain is not evidence. Name the feeling, then look for the facts underneath it.",
    },
    "attachment": {
        "_": "Offer predictability: clear steps, clear timelines, follow-through. Relational safety unlocks the real conversation.",
        "anxious": "Lower uncertainty: acknowledge briefly, give a firm timeline, and come back with updates on time.",
        "avoidant": "Respect autonomy: reduce pressure, leave room to decide, avoid ultimatums.",
        "fearful_avoidant": "Go slow and consistent: provide safety and freedom of choice at the same time.",
        "secure": "Solid relational base. You can go straight to content and problem-solving.",
    },
    "behavioral_econ": {
        "_": "Name the decision bias and bring the discussion back to numbers and objective criteria.",
        "loss_aversion": "Reframe around gains: what is lost by not acting, not just the risk of acting.",
        "anchoring": "Don't counter-anchor immediately; introduce an independent reference before discussing the figure.",
        "framing_effect": "Test the decision in both framings (gain and loss) before accepting it.",
        "sunk_cost_fallacy": "Decide on future value, not on the investment already made.",
    },
    "narrative": {
        "_": "Separate fact from interpretation: 'The facts are X; the story we tell is Y.'",
        "victim_narrative": "Restore agency: move the talk toward what the counterparty can control and choose now.",
        "victor_narrative": "Reframe from 'conquest' to 'shared outcome': durable wins come from the deal, not domination.",
        "collaborative_narrative": "Favorable story. Reinforce it with partnership language and shared next steps.",
        "heros_journey": "Use the growth energy: frame the obstacle as a step toward a better outcome.",
    },
    "somatic": {
        "_": "Check in with your body: feet on the floor, slow breath. Signal safety with calm tone and open posture.",
        "grounded": "Optimal body state. Listen deeply, move slowly, let decisions mature.",
        "dysregulated": "Short pause. Breathe deep, ground yourself, then resume from calm.",
    },
}


def curated_suggestion(slug: str, token: Optional[str], lang_table: Dict) -> str:
    table = lang_table.get(slug, {})
    if token and token in table:
        return table[token]
    return table.get("_", "")


# --------------------------------------------------------------------------- #
#  Per-framework extractors: raw module output -> (token, confidence,          #
#  suggestion_en, suggestion_ro, detail_en, triggered)                        #
# --------------------------------------------------------------------------- #

def _clamp01(x: float) -> float:
    return round(max(0.05, min(0.99, float(x))), 2)


def _pick(slug: str, token: Optional[str], module_en: str = "") -> Tuple[str, str]:
    """Curated EN/RO coaching line for (framework, token); module text as EN fallback."""
    en_tbl = EN_SUGGESTIONS.get(slug, {})
    ro_tbl = RO_SUGGESTIONS.get(slug, {})
    en = en_tbl.get(token or "")
    if not en:
        cleaned = first_sentences(module_en, 2, 220)
        en = cleaned if len(cleaned) >= 30 else (en_tbl.get("_") or cleaned)
    ro = ro_tbl.get(token or "") or ro_tbl.get("_", "")
    return en, ro


def ex_cbt(r: Dict):
    cd = r.get("cognitive_distortions", {}) or {}
    token = cd.get("primary_finding")
    triggered = bool(cd.get("detected_patterns"))
    conf = r.get("confidence_score", 0.5)
    if not triggered:
        conf = min(conf, 0.45)
        token = token or "clear_thinking"
    if token == "clear_thinking":
        sug_en = "Clear thinking, no distortions. Channel the clarity into strategy."
        sug_ro = "Gândire clară, fără distorsiuni. Canalizează claritatea în strategie."
    else:
        sug_en, sug_ro = _pick("cbt", token, cd.get("coaching_guidance"))
    detail = first_sentences(cd.get("analysis_text"), 2)
    en_label = "Clear thinking, no distortions" if token == "clear_thinking" else humanize(token)
    ro_label_v = "Gândire clară, fără distorsiuni" if token == "clear_thinking" else ro_label(token)
    return en_label, ro_label_v, _clamp01(conf), sug_en, sug_ro, detail, triggered


def ex_nlp(r: Dict):
    rs = r.get("representation_systems", {}) or {}
    pl = r.get("pacing_and_leading", {}) or {}
    token = rs.get("primary_finding")
    raw = rs.get("raw_matches", {}) or {}
    triggered = any(raw.values())
    conf = r.get("confidence_score", 0.7)
    if not triggered:
        conf = 0.5
    sug_en = first_sentences(rs.get("coaching_guidance") or pl.get("coaching_guidance"))
    sug_ro = {
        "visual": "Folosește metafore vizuale: arată-i imaginea de ansamblu și fă-l să «vadă» valoarea.",
        "auditory": "Reia-i cuvintele exacte și structura logică; sună-i «corect» ceea ce spui.",
        "kinesthetic": "Creează confort concret: pași tangibili, mostre, senzația că acordul e «solid».",
    }.get(token, "Fă pacing la ritmul lor o propoziție în plus, apoi condu spre subiectul tău.")
    return (humanize(token), ro_label(token), _clamp01(conf), sug_en, sug_ro,
            first_sentences(rs.get("analysis_text")), triggered)


def ex_ta(r: Dict):
    ego = r.get("ego_states", {}) or {}
    token = ego.get("primary_finding")
    triggered = bool(ego.get("detected_patterns"))
    conf = r.get("confidence_score", 0.7)
    if not triggered:
        conf = min(conf, 0.5)
    sug_en = first_sentences(ego.get("analysis_text") or ego.get("coaching_guidance"))
    sug_ro = {
        "adult": "Rămâi în Adult: fapte, opțiuni, întrebări reale. Nu răspunde din Părinte sau Copil.",
        "parent": "Coboară din Părinte: înlocuiește sfatul/critica cu opțiuni și întrebări deschise.",
        "child": "Ieși din Copil: revino la fapte și la ce poți controla, fără reactivitate emoțională.",
    }.get(token, "Menține tranzacții Adult-Adult: direct, onest, orientat spre problemă.")
    return (humanize(token), ro_label(token), _clamp01(conf), sug_en, sug_ro,
            first_sentences(ego.get("analysis_text")), triggered)


def ex_ei(r: Dict):
    st = r.get("emotional_state", {}) or {}
    comp = r.get("competencies", {}) or {}
    token = st.get("primary_finding")
    triggered = bool(st.get("detected_patterns")) or not st.get("assumed_default", False)
    conf = r.get("confidence_score", 0.6)
    if not triggered:
        conf = min(conf, 0.5)
    sug_en = first_sentences(st.get("coaching_guidance") or comp.get("coaching_guidance"))
    sug_ro = {
        "skepticism": "Numește îndoiala fără să o combați: «pare că nu ești convins». Apoi cere criteriul lor.",
        "frustration": "Recunoaște emoția întâi: «înțeleg că e frustrant». Apoi fă pauză și lasă-i să confirme.",
        "fear": "Redu amenințarea: numește riscul perceput și oferă o cale de ieșire sigură.",
        "openness": "Fereastră bună: pune întrebări de descoperire și avansează spre pașii următori.",
        "acceptance": "Consolidează acceptarea cu un pas concret și mic de angajament.",
    }.get(token, "Numește emoția explicit, apoi fă pauză înainte de a trece la soluție.")
    return (humanize(token), ro_label(token), _clamp01(conf), sug_en, sug_ro,
            first_sentences(st.get("analysis_text")), triggered)


def ex_attachment(r: Dict):
    style = r.get("attachment_style", {}) or {}
    wounds = r.get("wounds", {}) or {}
    token = style.get("primary_finding") or "secure"
    anx = float(style.get("anxiety", 0.0) or 0.0)
    avd = float(style.get("avoidance", 0.0) or 0.0)
    triggered = bool(style.get("raw_matches_anxiety") or style.get("raw_matches_avoidance")
                     or wounds.get("detected_patterns"))
    if triggered:
        conf = 0.45 + max(anx, avd) * 0.5 + (0.1 if wounds.get("detected_patterns") else 0.0)
    else:
        conf = 0.4
    wlist = wounds.get("detected_patterns") or []
    sug_en = first_sentences(wlist[0].get("coaching_guidance")) if wlist else curated_suggestion("attachment", token, EN_SUGGESTIONS)
    sug_ro = curated_suggestion("attachment", token, RO_SUGGESTIONS)
    detail = f"anxiety={anx:.2f}, avoidance={avd:.2f}"
    return (humanize(token), ro_label(token), _clamp01(conf), sug_en, sug_ro, detail, triggered)


def ex_behavioral_econ(r: Dict):
    cb = r.get("cognitive_biases", {}) or {}
    token = cb.get("primary_finding")
    n = int(cb.get("count", 0) or 0)
    triggered = n > 0
    conf = (0.45 + 0.13 * min(3, n)) if triggered else 0.38
    dp = cb.get("detected_patterns") or []
    sug_en = first_sentences(dp[0].get("coaching_guidance")) if dp else curated_suggestion("behavioral_econ", token, EN_SUGGESTIONS)
    sug_ro = curated_suggestion("behavioral_econ", token, RO_SUGGESTIONS)
    en_label = humanize(token) if token else "No decision biases detected"
    ro_label_v = ro_label(token) if token else "Fără distorsiuni decizionale"
    detail = f"{n} bias(es) detected"
    return (en_label, ro_label_v, _clamp01(conf), sug_en, sug_ro, detail, triggered)


def ex_game_theory(r: Dict):
    ga = r.get("game_archetype", {}) or {}
    sp = r.get("strategic_position", {}) or {}
    token = ga.get("primary_finding")
    scores = ga.get("scores", {}) or {}
    pos_scores = sp.get("position_scores", {}) or {}
    triggered = any(v > 0 for v in scores.values()) or any(v > 0 for v in pos_scores.values())
    conf = (0.45 + max(list(scores.values()) or [0]) * 0.5) if triggered else 0.4
    sug_en = first_sentences(ga.get("coaching_guidance") or sp.get("coaching_guidance"))
    sug_ro = {
        "zero_sum": "Nu intra în logica «sumă nulă». Mărește tortul: negociază scop, termeni și calendar înainte de cifră.",
        "prisoners_dilemma": "Construiește încredere reciprocă: fă un prim gest cooperant vizibil și cere reciprocitate.",
        "coordination_game": "Interesul e comun. Semnalează clar preferința ta, ascult-o pe a lor, găsiți terenul comun.",
    }.get(token, "Clarifică tipul de joc: colaborativ sau câștigător-ia-tot. Numește-l explicit.")
    detail = f"strategic position: {sp.get('primary_finding', 'parity')}"
    return (humanize(token), ro_label(token), _clamp01(conf), sug_en, sug_ro, detail, triggered)


def ex_neuroscience(r: Dict):
    nss = r.get("nervous_system_state", {}) or {}
    nbp = r.get("neurobiological_patterns", {}) or {}
    tsr = r.get("threat_safety_reward", {}) or {}
    raw = nbp.get("raw_matches", {}) or {}
    indicators = (nss.get("sympathetic_indicators", 0) + nss.get("parasympathetic_indicators", 0)
                  + nss.get("balanced_indicators", 0))
    triggered = any(raw.values()) or indicators > 0
    if any(raw.values()):
        token = nbp.get("primary_finding")
    elif indicators > 0:
        token = nss.get("emotional_state")
    else:
        token = nss.get("emotional_state", "balanced")
    match_count = sum(len(v) for v in raw.values())
    conf = (0.5 + 0.1 * min(3, match_count + (1 if indicators else 0))) if triggered else 0.4
    sug_en = first_sentences(nss.get("coaching_guidance") or tsr.get("coaching_guidance"))
    sug_ro = {
        "sympathetic": "Cineva e în alertă (amigdala activă). De-escaladează întâi: ton calm, ritm lent, previzibilitate.",
        "parasympathetic": "Ambele sisteme nervoase sunt calme. Optim pentru negociere — menține siguranța, adâncește angajamentul.",
        "balanced": "Stare echilibrată: alert și calm. Protejeaz-o de factori declanșatori.",
        "amygdala_activation": "Semnale de amenințare. Oferă siguranță și claritate înainte de orice cerere.",
        "reward_system": "Sistemul de recompensă e activ — evidențiază beneficiile concrete și pașii spre ele.",
    }.get(token, "Reglează-ți propriul sistem nervos întâi: respirație, postură, ton. Apoi semnalează siguranță.")
    threat = tsr.get("threat", 0.0)
    detail = f"threat={threat}, safety={tsr.get('safety', 0.0)}, reward={tsr.get('reward', 0.0)}"
    return (humanize(token), ro_label(token), _clamp01(conf), sug_en, sug_ro, detail, triggered)


def ex_narrative(r: Dict):
    dn = r.get("dominant_narrative", {}) or {}
    token = dn.get("primary_finding")
    scores = dn.get("scores", {}) or {}
    triggered = any(v > 0 for v in scores.values())
    conf = (0.45 + max(list(scores.values()) or [0]) * 0.5) if triggered else 0.4
    sug_en = curated_suggestion("narrative", token, EN_SUGGESTIONS)
    sug_ro = curated_suggestion("narrative", token, RO_SUGGESTIONS)
    impact = dn.get("impact")
    detail = first_sentences(impact if isinstance(impact, str) else " ".join(impact or []))
    return (humanize(token), ro_label(token), _clamp01(conf), sug_en, sug_ro, detail, triggered)


def ex_somatic(r: Dict):
    ss = r.get("somatic_state", {}) or {}
    sp = r.get("somatic_patterns", {}) or {}
    raw = sp.get("raw_matches", {}) or {}
    indicators = ss.get("grounding_indicators", 0) + ss.get("presence_indicators", 0)
    triggered = indicators > 0 or any(raw.values())
    if triggered:
        token = ss.get("overall_summary")
        conf = ss.get("confidence_score", 0.0) or 0.0
        if conf < 0.4:
            conf = 0.55
    else:
        token = None
        conf = 0.38
    sub = sp.get("primary_finding")
    sug_en = curated_suggestion("somatic", "grounded" if ss.get("grounding_state") == "grounded" else "dysregulated", EN_SUGGESTIONS) \
        if triggered else EN_SUGGESTIONS["somatic"]["_"]
    sug_ro = curated_suggestion("somatic", "grounded" if ss.get("grounding_state") == "grounded" else "dysregulated", RO_SUGGESTIONS) \
        if triggered else RO_SUGGESTIONS["somatic"]["_"]
    en_label = humanize(token) if token else "No clear somatic signal"
    ro_label_v = ro_label(token) if token else "Fără semnale corporale clare"
    detail = f"pattern: {sub}" if sub else ""
    return (en_label, ro_label_v, _clamp01(conf), sug_en, sug_ro, detail, triggered)


EXTRACTORS: Dict[str, Callable] = {
    "cbt": ex_cbt,
    "nlp": ex_nlp,
    "ta": ex_ta,
    "ei": ex_ei,
    "attachment": ex_attachment,
    "behavioral_econ": ex_behavioral_econ,
    "game_theory": ex_game_theory,
    "neuroscience": ex_neuroscience,
    "narrative": ex_narrative,
    "somatic": ex_somatic,
}

FRAMEWORK_NAMES: Dict[str, Tuple[str, str]] = {
    "cbt": ("CBT", "TCC"),
    "nlp": ("NLP", "PNL"),
    "ta": ("Transactional Analysis", "Analiză Tranzacțională"),
    "ei": ("Emotional Intelligence", "Inteligență Emoțională"),
    "attachment": ("Attachment", "Atașament"),
    "behavioral_econ": ("Behavioral Economics", "Economie Comportamentală"),
    "game_theory": ("Game Theory", "Teoria Jocurilor"),
    "neuroscience": ("Neuroscience", "Neuroștiință"),
    "narrative": ("Narrative", "Narativ"),
    "somatic": ("Somatic", "Somatic"),
}


# --------------------------------------------------------------------------- #
#  Aggregation                                                               #
# --------------------------------------------------------------------------- #

def _close_probability(tokens: Dict[str, str], triggered: Dict[str, bool], raw: Dict[str, Dict]) -> int:
    score = 5.0

    def tok(slug):
        return tokens.get(slug) if triggered.get(slug) else None

    if tokens.get("ta") == "adult":
        score += 0.6
    elif tok("ta") in ("parent", "child", "critical_parent", "adapted_child"):
        score -= 0.5

    ei_t = tok("ei")
    if ei_t in ("openness", "acceptance", "curiosity", "calm", "grounded", "enthusiasm"):
        score += 0.8
    elif ei_t == "skepticism":
        score -= 0.6
    elif ei_t in ("frustration", "fear", "anxiety"):
        score -= 1.0

    at = tok("attachment")
    if at == "anxious":
        score -= 0.8
    elif at == "avoidant":
        score -= 0.7
    elif at == "fearful_avoidant":
        score -= 1.2

    ns = raw.get("neuroscience", {}) or {}
    nss = (ns.get("nervous_system_state", {}) or {}).get("emotional_state")
    tsr = ns.get("threat_safety_reward", {}) or {}
    if nss == "parasympathetic":
        score += 0.7
    elif nss == "balanced":
        score += 0.3
    elif nss == "sympathetic":
        score -= 1.2
    if float(tsr.get("threat", 0) or 0) > 0.5:
        score -= 1.0
    if float(tsr.get("reward", 0) or 0) > 0.4:
        score += 0.6

    som = raw.get("somatic", {}) or {}
    sstate = som.get("somatic_state", {}) or {}
    if triggered.get("somatic"):
        if sstate.get("grounding_state") == "grounded":
            score += 0.5
        elif sstate.get("grounding_state") == "dysregulated":
            score -= 0.8
        if sstate.get("presence_state") == "dissociated":
            score -= 0.5

    cbt_raw = raw.get("cbt", {}) or {}
    n_distortions = len((cbt_raw.get("cognitive_distortions", {}) or {}).get("detected_patterns", []))
    if n_distortions:
        score -= min(1.5, 0.5 * n_distortions)
    else:
        score += 0.4

    gt = tok("game_theory")
    if gt in ("zero_sum", "prisoners_dilemma"):
        score -= 0.6
    elif gt in ("coordination_game", "cooperative", "non_zero_sum"):
        score += 0.4
    gpos = (raw.get("game_theory", {}) or {}).get("strategic_position", {}) or {}
    if gpos.get("primary_finding") == "dominant" and any((gpos.get("position_scores") or {}).values()):
        score += 0.8
    elif gpos.get("primary_finding") == "disadvantaged" and any((gpos.get("position_scores") or {}).values()):
        score -= 0.8

    be_raw = raw.get("behavioral_econ", {}) or {}
    n_bias = int((be_raw.get("cognitive_biases", {}) or {}).get("count", 0) or 0)
    if n_bias:
        score -= min(1.2, 0.3 * n_bias)

    nar = tok("narrative")
    if nar == "collaborative_narrative":
        score += 0.5
    elif nar == "victim_narrative":
        score -= 0.6
    elif nar == "victor_narrative":
        score -= 0.4

    return int(round(max(0, min(10, score))))


def run_all_frameworks(text: str, lang: str) -> Dict:
    raw_results: Dict[str, Dict] = {}
    frameworks: Dict[str, Dict] = {}
    tokens: Dict[str, str] = {}
    triggered_map: Dict[str, bool] = {}
    conf_map: Dict[str, float] = {}
    sug_en_map: Dict[str, str] = {}
    sug_ro_map: Dict[str, str] = {}
    name_en_map: Dict[str, str] = {}

    for slug in FRAMEWORK_ORDER:
        inst = _INSTANCES.get(slug)
        en_name, ro_name = FRAMEWORK_NAMES[slug]
        if inst is None:
            frameworks[slug] = {
                "name": bi(en_name, ro_name, lang),
                "primary_finding": bi("Module unavailable", "Modul indisponibil", lang),
                "confidence": 0.0,
                "suggestion": bi("", "", lang),
                "triggered": False,
            }
            continue
        try:
            raw = inst.analyze(text)
        except Exception as exc:  # pragma: no cover
            print(f"[santinel] {slug}.analyze failed: {exc}")
            raw = {}
        raw_results[slug] = raw
        try:
            en_lbl, ro_lbl, conf, sug_en, sug_ro, detail, triggered = EXTRACTORS[slug](raw)
        except Exception as exc:  # pragma: no cover
            print(f"[santinel] extractor {slug} failed: {exc}")
            en_lbl, ro_lbl, conf, sug_en, sug_ro, detail, triggered = (
                "No clear signal", "Semnal neconcludent", 0.3, "", "", "", False)

        tok = None
        cd = (raw.get("cognitive_distortions") or {}) if slug == "cbt" else {}
        # token used for close-probability heuristics
        if slug == "cbt":
            tok = cd.get("primary_finding")
        elif slug == "nlp":
            tok = (raw.get("representation_systems") or {}).get("primary_finding")
        elif slug == "ta":
            tok = (raw.get("ego_states") or {}).get("primary_finding")
        elif slug == "ei":
            tok = (raw.get("emotional_state") or {}).get("primary_finding")
        elif slug == "attachment":
            tok = (raw.get("attachment_style") or {}).get("primary_finding")
        elif slug == "behavioral_econ":
            tok = (raw.get("cognitive_biases") or {}).get("primary_finding")
        elif slug == "game_theory":
            tok = (raw.get("game_archetype") or {}).get("primary_finding")
        elif slug == "neuroscience":
            tok = (raw.get("nervous_system_state") or {}).get("emotional_state")
        elif slug == "narrative":
            tok = (raw.get("dominant_narrative") or {}).get("primary_finding")
        elif slug == "somatic":
            tok = (raw.get("somatic_state") or {}).get("grounding_state")

        # A framework that actually fired should never read as low-confidence,
        # even when its module's internal score formula is conservative.
        if triggered and conf < 0.55:
            conf = round(0.55 + conf * 0.3, 2)

        tokens[slug] = tok
        triggered_map[slug] = triggered
        conf_map[slug] = conf
        sug_en_map[slug] = sug_en
        sug_ro_map[slug] = sug_ro
        name_en_map[slug] = en_name

        entry = {
            "name": bi(en_name, ro_name, lang),
            "primary_finding": bi(en_lbl, ro_lbl, lang),
            "confidence": conf,
            "suggestion": bi(sug_en, sug_ro, lang),
            "triggered": bool(triggered),
        }
        if detail:
            entry["detail"] = detail
        frameworks[slug] = entry

    close_probability = _close_probability(tokens, triggered_map, raw_results)

    # top 3 frameworks by confidence — triggered first, then fill by confidence
    ordered = sorted(FRAMEWORK_ORDER, key=lambda s: conf_map.get(s, 0), reverse=True)
    top = [s for s in ordered if triggered_map.get(s)]
    for s in ordered:
        if s not in top:
            top.append(s)
    top_frameworks = top[:3]

    # synthesized coaching from the top frameworks
    def synth(lang_key: str) -> str:
        sug_map = sug_en_map if lang_key == "en" else sug_ro_map
        if lang_key == "en":
            head = f"Close probability sits at {close_probability}/10."
            joiner = "Also"
        else:
            head = f"Probabilitatea de închidere este {close_probability}/10."
            joiner = "De asemenea"
        parts = [head]
        for i, s in enumerate(top_frameworks):
            tip = first_sentences(sug_map.get(s, ""), 1, 130)
            if not tip:
                continue
            label = FRAMEWORK_NAMES[s][0] if lang_key == "en" else FRAMEWORK_NAMES[s][1]
            prefix = "Priority" if (i == 0 and lang_key == "en") else ("Prioritate" if i == 0 else joiner)
            parts.append(f"{prefix} — {label}: {tip}")
        return " ".join(parts)

    coaching = bi(synth("en"), synth("ro"), lang)

    return {
        "close_probability": close_probability,
        "frameworks": frameworks,
        "frameworks_order": FRAMEWORK_ORDER,
        "top_frameworks": top_frameworks,
        "coaching": coaching,
    }


# --------------------------------------------------------------------------- #
#  FastAPI app                                                               #
# --------------------------------------------------------------------------- #

app = FastAPI(
    title="SANTINEL API Gateway",
    description="Real-time AI coaching for negotiations — 10-framework analysis",
    version="2.0.0",
)

_CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://192.168.1.50:5173"
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health")
def health():
    loaded = [s for s, inst in _INSTANCES.items() if inst is not None]
    return {
        "status": "healthy",
        "service": "SANTINEL API",
        "frameworks_loaded": loaded,
        "frameworks_missing": [s for s in FRAMEWORK_ORDER if s not in loaded],
    }


@app.get("/analyze")
@app.post("/analyze")
def analyze(text: str = None, lang: str = "both", user: dict = Depends(get_current_user)):
    lang = (lang or "both").lower()
    if lang not in ("both", "en", "ro"):
        lang = "both"
    if not text or not text.strip():
        return {"error": "No text provided"}

    result = run_all_frameworks(text.strip(), lang)
    return {"input": text, "lang": lang, **result}


@app.post("/api/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    lang: str = Form("auto"),
    user: dict = Depends(get_current_user),
):
    """Live speech-to-text: proxy one audio segment to Groq Whisper.

    The web app's Live Coaching module posts ~4s webm/opus segments here while
    recording. Stateless — the bytes are forwarded to Groq and dropped.
    """
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="transcription not configured (GROQ_API_KEY missing)",
        )

    audio = await file.read()
    if not audio:
        return {"text": "", "model": GROQ_STT_MODEL}
    if len(audio) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="audio segment too large")

    form = {"model": GROQ_STT_MODEL, "response_format": "json", "temperature": "0"}
    if lang in ("en", "ro"):
        form["language"] = lang

    try:
        resp = requests.post(
            GROQ_STT_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            files={
                "file": (
                    file.filename or "segment.webm",
                    audio,
                    file.content_type or "audio/webm",
                )
            },
            data=form,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"transcription upstream error: {exc}")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"transcription failed ({resp.status_code}): {resp.text[:200]}",
        )

    try:
        text = (resp.json().get("text") or "").strip()
    except ValueError:
        raise HTTPException(status_code=502, detail="transcription returned non-JSON")
    return {"text": text, "model": GROQ_STT_MODEL}


@app.get("/docs")
def docs():
    return {"docs": "Visit /docs for Swagger UI"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
