# -*- coding: utf-8 -*-
"""
Shared bilingual (EN + RO) text-normalization and keyword-matching helpers.

Used by SANTINEL's psychology frameworks (core/cbt_module.py, core/nlp_module.py)
so they all fold diacritics, stem, and scope negation the same way.

Pipeline: prep() -> split_clauses() -> tokens() -> find_all() per clause, with
matching done first on raw tokens and then on Snowball stems. Negation is
clause-scoped: a cue in the few tokens before a match, or one that opens the
clause, suppresses the hit (unless the matched phrase itself opens the clause,
which keeps idioms like "nu e corect" / "it's not fair").
"""

import re
import unicodedata
from typing import Dict, List, Optional

try:  # optional dependency; matching degrades to exact-token if unavailable
    import snowballstemmer

    EN_STEMMER = snowballstemmer.stemmer("english")
    RO_STEMMER = snowballstemmer.stemmer("romanian")
except Exception:  # pragma: no cover
    EN_STEMMER = None
    RO_STEMMER = None

STEMMING_ENABLED = RO_STEMMER is not None

_NT_CONTRACTION = re.compile(r"n['’`]t\b")
_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
# Clause boundaries for negation scoping. Apostrophes are intra-word (handled by
# tokenization / the n't rule), so they are deliberately not listed here.
_CLAUSE_RE = re.compile(r"[.,;:!?()\[\]{}\"\n–—…]+", re.UNICODE)

# Diacritic-stripped, lowercased tokens that flag a negated context.
EN_NEGATIONS = {
    "not", "no", "never", "none", "without", "hardly", "barely",
    "cannot", "nor", "neither",
}
RO_NEGATIONS = {
    "nu", "n", "nici", "niciun", "nicio", "nicidecum", "deloc", "fara",
}

_LOCAL_NEG_WINDOW = 3


def strip_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def prep(text: str) -> str:
    """Lowercase, expand n't -> not, drop diacritics. Punctuation is kept."""
    text = (text or "").lower()
    text = _NT_CONTRACTION.sub(" not ", text)
    return strip_diacritics(text)


def tokens(text: str) -> List[str]:
    return _WORD_RE.findall(text)


def split_clauses(prepped_text: str) -> List[str]:
    return [c for c in _CLAUSE_RE.split(prepped_text) if c and c.strip()]


def stemmer_for(lang: str):
    return RO_STEMMER if lang == "ro" else EN_STEMMER


def negations_for(lang: str) -> set:
    return RO_NEGATIONS if lang == "ro" else EN_NEGATIONS


def seq_index(haystack: List[str], needle: List[str], fuzzy_last: bool = False) -> int:
    """Index of `needle` in `haystack` as a token subsequence.

    Tokens must match exactly, except that with `fuzzy_last` the final token may
    match by prefix in either direction when both sides are >= 5 chars.
    `fuzzy_last` is only meant for the stemmed pass (both sides already reduced
    to roots), where a prefix relation means a shared stem, e.g. text "dezastr"
    vs keyword "dezastru". It is never used on raw tokens, where a short word
    like "e" would spuriously prefix-match "everyone". The 5-char floor keeps
    short shared prefixes (e.g. "tens-") from bridging unrelated words.
    """
    n, m = len(haystack), len(needle)
    if m == 0 or m > n:
        return -1
    last = m - 1
    for i in range(n - m + 1):
        for j in range(m):
            a, b = haystack[i + j], needle[j]
            if a == b:
                continue
            if (fuzzy_last and j == last
                    and min(len(a), len(b)) >= 5
                    and (a.startswith(b) or b.startswith(a))):
                continue
            break
        else:
            return i
    return -1


def is_negated(clause_tokens: List[str], start: int, negations: set) -> bool:
    """Negation if a cue sits just before the match (local), or the clause opens
    with a cue that scopes the whole clause (e.g. "nu cred ca ..."). A phrase
    that itself starts at the clause opening is treated as an idiom
    ("nu e corect", "it's not fair") and is not suppressed."""
    lo = max(0, start - _LOCAL_NEG_WINDOW)
    if any(tok in negations for tok in clause_tokens[lo:start]):
        return True
    if start > 0 and any(tok in negations for tok in clause_tokens[:2]):
        return True
    return False


def _phrase_index(clause_tokens, clause_stems, phrase_tokens, stemmer):
    """(index, matched_by) of a phrase in one clause, or (-1, None)."""
    idx = seq_index(clause_tokens, phrase_tokens)
    if idx != -1:
        return idx, "exact"
    if clause_stems is not None:
        phrase_stems = [stemmer.stemWord(t) for t in phrase_tokens]
        idx = seq_index(clause_stems, phrase_stems, fuzzy_last=True)
        if idx != -1:
            return idx, "stem"
    return -1, None


def find_all(
    text: str,
    keyword_map: Dict[str, List[str]],
    *,
    lang: str,
    stemmer=None,
    negations: Optional[set] = None,
    first_phrase_only: bool = True,
) -> List[Dict]:
    """Scan `text` for the phrases in `keyword_map` (``category -> [phrases]``).

    Returns one dict per hit: ``{category, keyword, language, matched_by}``.
    Clause-scoped negation is applied when `negations` is given. With
    `first_phrase_only` (default) at most one hit per category per clause is
    reported; set it False to get every matching phrase (used for scoring).
    """
    stemmer = stemmer if stemmer is not None else stemmer_for(lang)
    hits: List[Dict] = []
    for clause in split_clauses(prep(text)):
        clause_tokens = tokens(clause)
        if not clause_tokens:
            continue
        clause_stems = (
            [stemmer.stemWord(t) for t in clause_tokens] if stemmer else None
        )
        for category, phrases in keyword_map.items():
            for phrase in phrases:
                phrase_tokens = tokens(prep(phrase))
                if not phrase_tokens:
                    continue
                idx, matched_by = _phrase_index(
                    clause_tokens, clause_stems, phrase_tokens, stemmer
                )
                if idx == -1:
                    continue
                if negations and is_negated(clause_tokens, idx, negations):
                    continue
                hits.append({
                    "category": category,
                    "keyword": phrase,
                    "language": lang,
                    "matched_by": matched_by,
                })
                if first_phrase_only:
                    break
    return hits


def merge_by_category(*hit_lists: List[Dict]) -> List[Dict]:
    """Flatten hit lists, keeping the first hit seen per category."""
    out: Dict[str, Dict] = {}
    for hits in hit_lists:
        for hit in hits:
            out.setdefault(hit["category"], hit)
    return list(out.values())
