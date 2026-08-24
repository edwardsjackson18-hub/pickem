"""Link each game in season.json to its real ESPN event, and grade it.

Why this exists
---------------
The pool grades by hand, by colouring cells. This asks ESPN who actually won,
which does three things:

  1. **Auto-grading.** Once a game is final, the winner is known without anyone
     colouring a cell. New weeks can score themselves.
  2. **Auditing.** Where the sheet IS coloured, ESPN and the colour must agree.
     A disagreement is either a mis-scored game or a mis-resolved team.
  3. **Team-resolution checks the colour checksum can't do.** It already caught
     "Sac State" resolving to South Carolina State instead of Sacramento State -
     an ungraded 2026 game, invisible to the colour check.

The join
--------
Not by week number (ESPN's `week` param under-returns) and not by date range
(misses FCS opponents). Instead: pull the HOME team's season schedule and find
the event whose two team ids match ours. One request per distinct team, cached.
No key, no auth, CORS-open.

    https://site.api.espn.com/apis/site/v2/sports/football/college-football
        /teams/{team_id}/schedule?season={year}

Usage:  python scripts/espn_link.py [year]     (default: the current season)
"""
import json, io, os, sys, time, urllib.request, urllib.error, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEASON_JSON = os.path.join(ROOT, "season.json")
OUT = os.path.join(ROOT, "espn.json")
UA = {"User-Agent": "Mozilla/5.0"}
SCHED = ("https://site.api.espn.com/apis/site/v2/sports/football/college-football"
         "/teams/%s/schedule?season=%d&seasontype=%d")

def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            if i == tries - 1: return None
            time.sleep(1.5 * (i + 1))
    return None

_cache = {}
def schedule(team_id, year):
    """Regular season AND postseason - the default response omits bowls."""
    key = (team_id, year)
    if key in _cache: return _cache[key]
    raw = []
    for stype in (2, 3):
        d = get(SCHED % (team_id, year, stype)) or {}
        for e in d.get("events", []):
            raw.append((stype, e))
    ev = []
    for stype, e in raw:
        c = (e.get("competitions") or [{}])[0]
        comps = c.get("competitors") or []
        if len(comps) != 2: continue
        ev.append({
            "seasontype": stype,
            "id": e.get("id"), "name": e.get("shortName"),
            "date": (e.get("date") or "")[:10],
            "ids": frozenset(x["team"]["id"] for x in comps),
            "status": ((c.get("status") or {}).get("type") or {}).get("name", "").replace("STATUS_", ""),
            "completed": bool(((c.get("status") or {}).get("type") or {}).get("completed")),
            "scores": {x["team"]["id"]: x.get("score") for x in comps},
            "winner": next((x["team"]["id"] for x in comps if x.get("winner")), None),
        })
    _cache[key] = ev
    return ev

def find(away_id, home_id, year, tab=""):
    """Two teams can meet TWICE in a season - regular season, then the
    conference title game. Taking the first match silently graded 20 of the
    Conf Champ picks against the wrong game, so disambiguate by tab."""
    want = frozenset([away_id, home_id])
    hits, seen = [], set()
    for tid in (home_id, away_id):
        if not tid: continue
        for e in schedule(tid, year):
            if e["ids"] == want and e["id"] not in seen:
                seen.add(e["id"]); hits.append(e)
    if not hits: return None
    if len(hits) == 1: return hits[0]
    postseason = tab in ("Conf Champ", "BOWLS")
    pool = [e for e in hits if (e["seasontype"] == 3) == postseason] or hits
    pool.sort(key=lambda e: e["date"] or "")
    return pool[-1] if postseason else pool[0]

def main():
    year = int(sys.argv[1]) if len(sys.argv) > 1 else None
    weeks = json.load(io.open(SEASON_JSON, encoding="utf-8"))
    if year is None:
        year = max(w.get("season", 0) for w in weeks)

    stat = collections.Counter()
    disagreements, unmatched, graded = [], [], {}

    for w in weeks:
        if w.get("season") != year: continue
        for g in w["games"]:
            aid, hid = g.get("away_id"), g.get("home_id")
            if not aid or not hid:
                stat["no_ids"] += 1; unmatched.append((w["tab"], g["raw"], "unresolved teams")); continue
            e = find(aid, hid, year, w["tab"])
            stat["games"] += 1
            if not e:
                stat["unmatched"] += 1; unmatched.append((w["tab"], g["raw"], "no ESPN event")); continue
            stat["matched"] += 1
            rec = {"event": e["id"], "name": e["name"], "date": e["date"],
                   "status": e["status"], "winner": e["winner"],
                   "scores": e["scores"]}
            graded.setdefault(w["tab"], {})[g["raw"]] = rec
            if not e["completed"]:
                stat["pending"] += 1; continue
            stat["final"] += 1

            # audit: where the sheet is coloured, ESPN must agree
            for p, v in g["picks"].items():
                if not v.get("team_id") or not v.get("result"): continue
                espn_win = (v["team_id"] == e["winner"])
                sheet_win = (v["result"] == "win")
                if espn_win != sheet_win:
                    stat["disagree"] += 1
                    disagreements.append((w["tab"], g["raw"], p, v.get("raw"),
                                          "sheet=%s espn=%s" % (v["result"],
                                          "win" if espn_win else "loss")))
                else:
                    stat["agree"] += 1

    json.dump({"season": year, "games": graded},
              io.open(OUT, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)

    print("season %d" % year)
    print("  games %d | matched %d | unmatched %d | final %d | pending %d"
          % (stat["games"], stat["matched"], stat["unmatched"], stat["final"], stat["pending"]))
    if stat["agree"] or stat["disagree"]:
        tot = stat["agree"] + stat["disagree"]
        print("  graded picks checked: %d, agree %d (%.1f%%), DISAGREE %d"
              % (tot, stat["agree"], 100.0 * stat["agree"] / tot, stat["disagree"]))
    if unmatched:
        print("\n  unmatched games (%d) - usually a mis-resolved team:" % len(unmatched))
        for t, r, why in unmatched[:15]: print("    %-11s %-46s %s" % (t, r[:46], why))
    if disagreements:
        print("\n  DISAGREEMENTS (%d) - sheet colour vs ESPN result:" % len(disagreements))
        for t, r, p, raw, why in disagreements[:20]:
            print("    %-11s %-40s %-8s %-14s %s" % (t, r[:40], p, (raw or "")[:14], why))
    print("\nwrote espn.json")

main()
