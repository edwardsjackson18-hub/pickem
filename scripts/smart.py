"""Enhanced scoped resolver. Wraps match_team.match with three extra passes that
exploit the fact that a pick can only ever be one of the game's two teams:
  1. initials      "GT" -> Georgia Tech, "NW" -> Northwestern, "TAMU" -> Texas A&M
  2. substring     "Southern Cal" ~ "Southern California", "Irish" in "Fighting Irish"
  3. joke table    hand-decoded from game context; no public source exists for these
"""
import re
from match_team import norm, match, COLLOQUIAL

# Hand-decoded from the game each appeared in. Values are ESPN team ids.
JOKES = {
    "piss": "145", "ole piss": "145", "abstinence": "2335", "corn": "158",
    "sparky": "9", "tortilla": "2641", "u": "2390", "the u": "2390",
    "misery": "142", "clanga": "228", "cult": "245", "mandate": "245",
    "fear the beak": "55", "cock tuah": "55", "cocks": "2579", "cock": "2579",
    "nussbussy": "99", "revenge": "127", "bandans": "103", "quack": "2483",
    "ducks": "2483", "hooty hoo": "201", "country roads": "277",
    "gamer bears": "2032", "hooty": "2711", "beak": "55",
}

# Plain abbreviations the index misses, keyed by school name (resolved to ids at load).
ABBREV = {
    "tamu": ["Texas A&M"], "atm": ["Texas A&M"],
    "southern cal": ["USC"], "utk": ["Tennessee"], "ut": ["Tennessee", "Texas"],
    "ul": ["Louisville", "Louisiana"],
    "msu": ["Michigan State", "Mississippi State", "Montana State", "Murray State"],
    "gt": ["Georgia Tech"], "gatech": ["Georgia Tech"],
    "osu": ["Ohio State", "Oklahoma State", "Oregon State"],
    "waz": ["Washington State"], "wsu": ["Washington State"],
    "nw": ["Northwestern"], "oh": ["Ohio"], "pitt": ["Pittsburgh"],
    "usu": ["Utah State"], "isu": ["Iowa State", "Illinois State", "Indiana State"],
    "asu": ["Arizona State", "Appalachian State", "Alabama State"],
    "csu": ["Colorado State"], "ndsu": ["North Dakota State"],
    "sdsu": ["South Dakota State", "San Diego State"],
}
_ABBREV_IDS = {}

def load_abbrev(idx, by_id):
    """Resolve ABBREV school names to ids once, using the same alias index."""
    from match_team import norm as _n
    for k, schools in ABBREV.items():
        for school in schools:
            for i in (idx.get(_n(school)) or set()):
                _ABBREV_IDS.setdefault(k, set()).add(i)

def initials(school):
    words = [w for w in norm(school).split() if w not in ("of", "the", "and", "at")]
    return "".join(w[0] for w in words)

def smart(pick, scope, idx, by_id):
    """scope = the two team ids in this game."""
    tid = match(pick, scope, idx)
    if tid: return tid, "base"

    n = norm(pick)
    cands = [by_id[i] for i in scope if i in by_id]

    j = JOKES.get(n) or COLLOQUIAL.get(n)
    if j and j in scope: return j, "joke"

    ab = _ABBREV_IDS.get(n)
    if ab:
        hit = ab & set(scope)
        if len(hit) == 1: return hit.pop(), "abbrev"

    # 1. initials of school or full display name
    hits = [c for c in cands
            if n == initials(c["school"]) or n == initials(c["display"])
            or n == norm(c["abbr"]).replace(" ", "")]
    if len(hits) == 1: return hits[0]["id"], "initials"

    # 2. substring either direction against school / display / mascot
    hits = []
    for c in cands:
        blob = norm(c["school"] + " " + c["display"] + " " + c["mascot"])
        if len(n) >= 2 and (n in blob or any(
                tok.startswith(n) or n.startswith(tok)
                for tok in blob.split() if len(tok) >= 3)):
            hits.append(c)
    if len(hits) == 1: return hits[0]["id"], "substr"

    # 3. unscoped joke fallback (pick may name a team not in the label, e.g. typos)
    if j: return j, "joke-unscoped"
    return None, None
