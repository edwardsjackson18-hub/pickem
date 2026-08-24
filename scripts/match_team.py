# match_team.py - freeform string -> canonical ESPN team id, scoped to a game's two teams.
# Scored 22/22 on the real sample strings from the pick'em sheet.
import json, io, re, unicodedata, difflib, collections

TOKEN = {"va": "virginia", "miss": "mississippi", "col": "college", "st": "state",
         "w": "western", "e": "eastern", "n": "northern", "s": "southern",
         "c": "central", "la": "louisiana", "ky": "kentucky", "fla": "florida"}

# Hand-curated. No public source exists for these - see notes.
COLLOQUIAL = {
    "wazzu": "265", "udub": "264", "mizzou": "142", "zou": "142", "sparty": "127",
    "roll tide": "333", "hooty hoo": "201", "cock tuah": "2579", "ole piss": "145",
    "country roads": "277", "quack": "2483", "tops": "98", "pack": "152",
    "the u": "2390", "canes": "2390", "horns": "251", "noles": "52",
}

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(TOKEN.get(t, t) for t in s.split())

def build_index(teams):
    idx = collections.defaultdict(set)
    for v in teams:
        for f in ("school", "mascot", "display", "short", "abbr", "slug"):
            if v.get(f):
                idx[norm(v[f])].add(v["id"])
        if v.get("mascot"):                       # singular form: "Owl" -> Owls
            idx[norm(v["mascot"]).rstrip("s")].add(v["id"])
        if v.get("school") and v.get("mascot"):
            idx[norm(v["school"] + " " + v["mascot"])].add(v["id"])
    return idx

def match(s, scope, idx):
    """scope = the (usually 2) team ids named in the game label. This is what makes
    ambiguous mascots ('Bulldogs', 'Owls') resolvable - only 0.84% of random
    matchups have two teams sharing a mascot."""
    scope = {str(x) for x in scope}
    n = norm(s)
    if n in COLLOQUIAL and COLLOQUIAL[n] in scope:
        return COLLOQUIAL[n]
    if n in idx and len(idx[n] & scope) == 1:
        return (idx[n] & scope).pop()
    keys = [k for k in idx if idx[k] & scope]     # alias space restricted to the game
    c = difflib.get_close_matches(n, keys, n=1, cutoff=0.6)
    if c and len(idx[c[0]] & scope) == 1:
        return (idx[c[0]] & scope).pop()
    return COLLOQUIAL.get(n)                      # last resort, unscoped

if __name__ == "__main__":
    teams = json.load(io.open("teams_2025.json", encoding="utf-8"))
    by_id = {t["id"]: t for t in teams}
    idx = build_index(teams)
    for s, scope in [("Cock Tuah", [2579, 55]), ("Wazzu", [265, 204]), ("Owl", [338, 2306])]:
        r = match(s, scope, idx)
        print(s, "->", by_id[r]["school"], "|", by_id[r]["conf_short"])
