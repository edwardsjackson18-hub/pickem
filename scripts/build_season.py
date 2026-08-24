"""Definitive builder: picks.json + teams_2025.json -> season.json

Combines
  - ESPN season-scoped team/conference data (teams_2025.json)
  - the hand-curated alias/mascot/joke table (work/teams.py)
  - the H8 inversion rule: "H8 <opponent mascot>" means pick the OTHER team
  - per-(week,game,player) hard overrides for zero-signal joke picks
and validates with the grading checksum: everyone who picked the same side of a
game must share the same colour, so a colour conflict means a resolver error.

Scoring: green = won straight up, red = lost, BLANK = LOSS. Week 0 never scored.
"""
import json, io, re, sys, os, collections, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from match_team import norm
from smart import smart, JOKES, load_abbrev
from gameparse import parse_game
def canon_player(p):
    """Week 3 renames Michael's column to "Michael (don't delete again jackass)".
    Strip any parenthetical so a header edit doesn't fork a player."""
    return re.split(r"[(\[]", p)[0].strip()

from aliases import TEAMS, HARD_OVERRIDES, EXTRA_OVERRIDES, NON_PICKS

espn = json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"teams_2025.json"), encoding="utf-8"))
by_id = {t["id"]: t for t in espn}

# ---- base ESPN alias index -------------------------------------------------
base = collections.defaultdict(set)
for t in espn:
    for f in ("school", "mascot", "display", "short", "abbr", "slug"):
        if t.get(f): base[norm(t[f])].add(t["id"])
    if t.get("mascot"): base[norm(t["mascot"]).rstrip("s")].add(t["id"])
school = collections.defaultdict(set)
for t in espn:
    for f in ("school", "display", "short", "abbr"):
        if t.get(f): school[norm(t[f])].add(t["id"])
load_abbrev(base, by_id)

def espn_id(name):
    n = norm(name)
    if n in base:
        fbs = [i for i in base[n] if by_id[i]["division"] == "fbs"]
        if len(base[n]) == 1: return next(iter(base[n]))
        if len(fbs) == 1: return fbs[0]
    c = difflib.get_close_matches(n, list(base), n=1, cutoff=0.72)
    if c:
        s = base[c[0]]; fbs = [i for i in s if by_id[i]["division"] == "fbs"]
        return fbs[0] if len(fbs) == 1 else next(iter(s))
    return None

def _pick_one(ids):
    if not ids: return None
    if len(ids) == 1: return next(iter(ids))
    fbs = [i for i in ids if by_id[i]["division"] == "fbs"]
    return fbs[0] if len(fbs) == 1 else None

def canon(name):
    """School name beats any other team's mascot. 'Duke' is Duke, not JMU's Dukes."""
    return _pick_one(school.get(norm(name))) or espn_id(name)

# ---- bridge the curated table's keys onto ESPN ids --------------------------
CID = {}
unbridged = []
for cid, aliases in TEAMS.items():
    tid = canon(aliases[0])
    if tid: CID[cid] = tid
    else:   unbridged.append((cid, aliases[0]))

idx = collections.defaultdict(set, {k: set(v) for k, v in base.items()})
for cid, aliases in TEAMS.items():
    tid = CID.get(cid)
    if not tid: continue
    for a in aliases:
        idx[norm(a)].add(tid)

def team_from_label(name):
    """Resolve a team named in the GAME LABEL. Prefers exact hits in the curated
    alias index; only then falls back to fuzzy. Fuzzy alone matched 'GA Tech'
    to Utah Tech, so exact-first is load-bearing."""
    n = norm(name)
    r = _pick_one(school.get(n))          # exact school name wins outright
    if r: return r
    r = _pick_one(idx.get(n))             # then curated aliases
    if r: return r
    return espn_id(name)

LATE = {"waz":"WSU", "c unt":"UNT", "kstate im scared":"KSU",
        "kstate":"KSU", "ga tech":"GT", "gatech":"GT"}
for _k,_c in LATE.items():
    if _c in CID: idx[_k].add(CID[_c])
LATE_OVR = {("Week 7","#10 Georgia -3.5 @ Auburn","Michael"):"UGA"}
HARD_OVERRIDES.update(LATE_OVR)
NON_PICKS2 = set(NON_PICKS) | {"Who the fuck knows man"}

H8 = re.compile(r"^h8\s+(.+)$")

def resolve_pick(raw, scope, key):
    if key in HARD_OVERRIDES:  return CID.get(HARD_OVERRIDES[key]), "override"
    if key in EXTRA_OVERRIDES: return CID.get(EXTRA_OVERRIDES[key]), "override"
    n = norm(raw)
    m = H8.match(n)
    if m:                                  # pick the team that is NOT the hated one
        parts = [m.group(1)] + re.split(r"[/,]| that | is | also | a ", m.group(1))
        hated = set()
        for part in [p.strip() for p in parts if p and p.strip()]:
            for k, ids in idx.items():
                if k and (k == part or k.rstrip("s") == part.rstrip("s")):
                    hated |= ids
        other = [i for i in scope if i not in hated]
        if len(other) == 1 and (set(scope) & hated): return other[0], "h8"
    sh = school.get(n, set()) & set(scope)
    if len(sh) == 1: return sh.pop(), "school"
    hit = idx.get(n, set()) & set(scope)
    if len(hit) == 1: return hit.pop(), "alias"
    return smart(raw, scope, idx, by_id)

def bucket(sp):
    if sp is None: return "none"
    for hi, lab in ((3,"1-3"),(7,"3.5-7"),(13.5,"7.5-13.5"),(20.5,"14-20.5")):
        if sp <= hi: return lab
    return "21+"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FROZEN_DIR = os.path.join(ROOT, "seasons")
CURRENT_SEASON = 2026
PICKS = os.path.join(ROOT, "picks.json")
OUT   = os.path.join(ROOT, "season.json")

WEEK_ORDER = {t: i for i, t in enumerate(
    ["Week %d" % n for n in range(0, 15)] + ["Conf Champ", "BOWLS"])}

DROP = {("Week 2", "#2 S Dakota St @ #3 Montana St")}
# ---- frozen past seasons: immutable, never re-read from the sheet -----------
FROZEN = {}
if os.path.isdir(FROZEN_DIR):
    for fn in sorted(os.listdir(FROZEN_DIR)):
        if not fn.endswith(".json"): continue
        yr = int(fn[:-5])
        FROZEN[yr] = json.load(io.open(os.path.join(FROZEN_DIR, fn), encoding="utf-8"))

def frozen_games(year, tab):
    for w in FROZEN.get(year, []):
        if w["tab"] == tab:
            return [g["raw"] for g in w["games"]]
    return None

def last_frozen_season(tab):
    """Newest frozen season that still owns this tab."""
    for yr in sorted(FROZEN, reverse=True):
        if frozen_games(yr, tab) is not None:
            return yr
    return None

def rolled_over(w):
    """True once the live tab's games no longer match any frozen snapshot."""
    live = [g["game"] for g in w["games"] if (w["tab"], g["game"]) not in DROP]
    yr = last_frozen_season(w["tab"])
    if yr is None:
        return True                      # nothing frozen for this tab yet
    old = frozen_games(yr, w["tab"])
    return set(live) != set(old)

weeks = json.load(io.open(PICKS, encoding="utf-8"))
out, stat = [], collections.Counter()
unresolved, conflicts = collections.Counter(), []

for w in weeks:
    # The pool reuses the same tabs every year, so a tab belongs to the current
    # season only once its games differ from the frozen snapshot. Until then the
    # sheet still holds last season's picks and the frozen copy wins.
    season = CURRENT_SEASON if rolled_over(w) else last_frozen_season(w["tab"])
    if season is None: season = CURRENT_SEASON
    scored = season != CURRENT_SEASON
    wk = {"tab": w["tab"], "season": season, "players": [canon_player(p) for p in w["players"]], "games": []}
    for gm in w["games"]:
        if (w["tab"], gm["game"]) in DROP: continue
        label = gm["game"].replace('""@""', "@").replace('"@"', "@")
        label = re.sub(r"\s+", " ", label).strip()
        g = parse_game(label)
        aid = team_from_label(g["away"]["name"]) if g["away"] else None
        hid = team_from_label(g["home"]["name"]) if g["home"] else None
        fav = team_from_label(g["fav"]) if g["fav"] else None
        scope = [x for x in (aid, hid) if x]
        stat["games"] += 1

        picks, seen = {}, collections.defaultdict(set)
        for p, v in gm["picks"].items():
            p = canon_player(p); raw = v["pick"]
            blank = (not raw) or raw in NON_PICKS2
            tid = None
            if not blank:
                stat["picks"] += 1
                tid, how = resolve_pick(raw, scope, (w["tab"], gm["game"], p))
                if tid: stat["resolved"] += 1; stat[how] += 1
                else:   unresolved[raw] += 1
            else:
                stat["blank"] += 1
            res = v["won"] or ("loss" if scored else None)
            if tid and res: seen[tid].add(res)
            t = by_id.get(tid) if tid else None
            picks[p] = {"raw": raw, "team_id": tid,
                        "team": t["school"] if t else None,
                        "conf": t["conf_short"] if t else None,
                        "result": res, "superdog": v.get("superdog", False),
                        "sd_points": (gm["spread"] or 0) if (v.get("superdog") and res=="win") else 0,
                        "is_dog": bool(tid and fav and tid != fav),
                        "is_fav": bool(tid and fav and tid == fav)}
        for tid, rs in seen.items():
            if len(rs) > 1:
                conflicts.append((w["tab"], gm["game"], by_id[tid]["school"]))

        wk["games"].append({
            "raw": gm["game"], "spread": gm["spread"], "bucket": bucket(gm["spread"]),
            "slate": gm.get("slate"), "date": gm.get("date"),
            "neutral": g["neutral"], "bowl": g["prefix"], "scored": scored,
            "away_label": g["away"]["name"] if g["away"] else None,
            "home_label": g["home"]["name"] if g["home"] else None,
            "away": by_id[aid]["school"] if aid else None,
            "home": by_id[hid]["school"] if hid else None,
            "away_conf": by_id[aid]["conf_short"] if aid else None,
            "home_conf": by_id[hid]["conf_short"] if hid else None,
            "picks": picks})
    out.append(wk)

# ---- merge: every frozen season, plus whatever the live sheet currently owns.
# A frozen tab is only superseded if the live sheet still claims it for the SAME
# season. Once a tab rolls over to the new year, the frozen copy is what keeps
# the old season's picks alive - the sheet no longer has them anywhere.
live_keys = {(w["season"], w["tab"]) for w in out}
merged = []
for yr in sorted(FROZEN):
    for w in FROZEN[yr]:
        if (yr, w["tab"]) not in live_keys:
            merged.append(w)
merged += out
merged.sort(key=lambda w: (w["season"], WEEK_ORDER.get(w["tab"], 99)))
out = merged

json.dump(out, io.open(OUT,"w",encoding="utf-8"), separators=(",",":"), ensure_ascii=False)

print("bridged %d/%d curated teams to ESPN ids" % (len(CID), len(TEAMS)))
if unbridged: print("  unbridged:", unbridged)
print("games %d | picks %d | resolved %d (%.2f%%) | blank %d"
      % (stat["games"], stat["picks"], stat["resolved"],
         100.0*stat["resolved"]/max(stat["picks"],1), stat["blank"]))
print("  by path:", {k: stat[k] for k in ("school","alias","override","h8","base","joke",
                                          "initials","substr","abbrev") if stat[k]})
bad = []
for w in out:
    for g in w["games"]:
        for side in ("away","home"):
            lab = g.get(side+"_label"); sch = g.get(side)
            if lab and sch and not (set(norm(lab).split()) & set(norm(sch).split())):
                bad.append((w["tab"], g["raw"], lab, sch))
print("LABEL AUDIT: %d suspicious team resolutions" % len(bad))
for b in bad: print("   %-11s %-40s %-14s -> %s"%(b[0],b[1][:40],b[2],b[3]))
by_season = {}
for w in out: by_season[w["season"]] = by_season.get(w["season"], 0) + len(w["games"])
print("SEASONS: %s" % ", ".join("%d (%d games%s)" % (y, n, ", frozen" if y in FROZEN
      and not any(x["season"] == y for x in globals().get("_live", [])) else "")
      for y, n in sorted(by_season.items())))
print("GRADING CHECKSUM: %d conflicts" % len(conflicts))
for c in conflicts[:10]: print("   ", c)
if unresolved:
    print("unresolved (%d distinct):" % len(unresolved))
    for s,c in unresolved.most_common(20): print("   %-40s x%d" % (s[:40], c))
