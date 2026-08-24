"""Freeze a completed season's pick-level data into seasons/<year>.json.

The pool reuses the same tabs every year, so once the sheet rolls over the old
season's picks are gone for good. Run this when a season finishes.

    python scripts/freeze_season.py 2026
"""
import json, io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
year = int(sys.argv[1]) if len(sys.argv) > 1 else None
if year is None:
    print(__doc__); raise SystemExit(1)

season = json.load(io.open(os.path.join(ROOT, "season.json"), encoding="utf-8"))
weeks = [w for w in season if w.get("season") == year]
if not weeks:
    print("nothing tagged season %d in season.json" % year); raise SystemExit(1)

os.makedirs(os.path.join(ROOT, "seasons"), exist_ok=True)
out = os.path.join(ROOT, "seasons", "%d.json" % year)
json.dump(weeks, io.open(out, "w", encoding="utf-8"),
          separators=(",", ":"), ensure_ascii=False)
g = sum(len(w["games"]) for w in weeks)
p = sum(len(x["picks"]) for w in weeks for x in w["games"])
print("froze %d: %d tabs, %d games, %d picks -> seasons/%d.json"
      % (year, len(weeks), g, p, year))
