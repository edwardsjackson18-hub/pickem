"""Parse the All-Time Pick 'Em workbook into history.json.

The workbook holds one block per season (2023, 2024, 2025). Each block is five
side-by-side player panels of Week / Win / Losses / Superdawg, then Total and
All-Time rows. It also carries a Champions table.

Unlike the Google Sheet this is WEEKLY AGGREGATES only - there is no pick-level
detail for 2023 or 2024. So the explorer stays 2025-only while records, the
season race and the trophy case go all the way back.
"""
import json, io, os, sys, openpyxl

SRC = sys.argv[1] if len(sys.argv) > 1 else \
      os.path.expanduser(r"~/Downloads/All_Time_Pick_Em (1).xlsx")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "history.json")

# Player panels run left to right in this fixed order; win-column indices below.
PLAYERS = ["JP", "Jack", "Robert", "Jackson", "Michael"]
WIN_COL = [2, 6, 10, 14, 18]          # 0-based; week = win-1, loss = win+1, sd = win+2

def num(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    s = str(v).strip()
    if s in ("", "-", "N/A"): return None
    try: return float(s)
    except ValueError: return None

def main():
    wb = openpyxl.load_workbook(SRC, data_only=True)
    ws = wb["Sheet1"]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    def cell(r, c):
        return rows[r][c] if r < len(rows) and c < len(rows[r]) else None
    def txt(r, c):
        v = cell(r, c)
        return "" if v is None else str(v).strip()

    seasons, champions = [], []

    # --- season blocks: a header row has "Week" in column B -------------------
    for i, row in enumerate(rows):
        if txt(i, 1).lower() != "week":
            continue
        # the season label sits in the row above, in the first win column
        year = None
        for back in (1, 2):
            cand = txt(i - back, WIN_COL[0])
            if cand[:4].isdigit():
                year = int(cand[:4]); break
        if year is None:
            continue

        weeks, totals = [], {}
        j = i + 1
        while j < len(rows):
            label = txt(j, 1)
            if label == "" and all(cell(j, c) is None for c in WIN_COL):
                break
            if label.lower() == "week":
                break
            entry = {"week": label, "players": {}}
            for p, c in zip(PLAYERS, WIN_COL):
                w, l, sd = num(cell(j, c)), num(cell(j, c + 1)), num(cell(j, c + 2))
                entry["players"][p] = {"w": w, "l": l, "sd": sd}
            low = label.lower()
            if low in ("total", "all-time"):
                totals[low] = entry["players"]
            elif label:
                weeks.append(entry)
            j += 1

        if weeks:
            seasons.append({"year": year, "weeks": weeks,
                            "total": totals.get("total", {}),
                            "alltime": totals.get("all-time", {})})

    # --- champions table ------------------------------------------------------
    for i, row in enumerate(rows):
        if any(txt(i, c).lower() == "champions" for c in range(len(row))):
            # header is the next row; find its column offsets
            h = i + 1
            cols = {}
            for c in range(len(rows[h])):
                key = txt(h, c).lower().rstrip(". ")
                if key in ("year", "full season", "reg. szn", "reg szn", "bowls", "superdog"):
                    cols[key] = c
            ycol = cols.get("year")
            if ycol is None: continue
            k = h + 1
            while k < len(rows):
                y = txt(k, ycol)
                if not y[:4].isdigit(): break
                rec = {"year": int(y[:4])}
                for key, c in cols.items():
                    if key == "year": continue
                    v = txt(k, c)
                    rec[key.replace(". ", "").replace(" ", "_")] = (v if v and v != "N/A" else None)
                champions.append(rec)
                k += 1
            break

    seasons.sort(key=lambda s: s["year"])

    # --- derived: per-season standings + true all-time ------------------------
    for s in seasons:
        st = []
        for p in PLAYERS:
            t = s["total"].get(p) or {}
            w, l, sd = t.get("w"), t.get("l"), t.get("sd")
            if w is None or l is None: continue
            st.append({"player": p, "w": int(w), "l": int(l),
                       "sd": sd or 0, "pct": w / (w + l) if (w + l) else 0})
        s["standings"] = sorted(st, key=lambda x: -x["pct"])
        s["sd_standings"] = sorted(st, key=lambda x: -x["sd"])

    alltime = []
    for p in PLAYERS:
        w = sum(int(s["total"][p]["w"]) for s in seasons if s["total"].get(p, {}).get("w") is not None)
        l = sum(int(s["total"][p]["l"]) for s in seasons if s["total"].get(p, {}).get("l") is not None)
        sd = sum((s["total"].get(p, {}).get("sd") or 0) for s in seasons)
        alltime.append({"player": p, "w": w, "l": l, "sd": sd,
                        "pct": w / (w + l) if (w + l) else 0})
    alltime.sort(key=lambda x: -x["pct"])

    # --- audit against the workbook's own All-Time row ------------------------
    audit = []
    last = seasons[-1]["alltime"] if seasons else {}
    for a in alltime:
        stated = last.get(a["player"]) or {}
        sw, sl, ssd = stated.get("w"), stated.get("l"), stated.get("sd")
        if sw is not None and (int(sw) != a["w"] or int(sl) != a["l"]):
            audit.append("%s: computed %d-%d, workbook says %d-%d"
                         % (a["player"], a["w"], a["l"], int(sw), int(sl)))
        if ssd is not None and abs((ssd or 0) - a["sd"]) > 0.01:
            audit.append("%s superdog: computed %g, workbook says %g" % (a["player"], a["sd"], ssd))

    out = {"players": PLAYERS, "seasons": seasons,
           "alltime": alltime, "champions": champions, "audit": audit}
    json.dump(out, io.open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    print("seasons: %s" % ", ".join(str(s["year"]) for s in seasons))
    for s in seasons:
        print("  %d  %d weeks  |  %s" % (s["year"], len(s["weeks"]),
              "  ".join("%s %d-%d sd%g" % (x["player"], x["w"], x["l"], x["sd"])
                        for x in s["standings"])))
    print("\nALL-TIME (computed from season totals)")
    for a in alltime:
        print("  %-8s %3d-%-3d  %.4f   superdog %g" % (a["player"], a["w"], a["l"], a["pct"], a["sd"]))
    print("\nchampions:")
    for c in champions:
        print("  %s" % c)
    print("\nAUDIT vs the workbook's own All-Time row: %s"
          % ("clean" if not audit else str(len(audit)) + " mismatches"))
    for a in audit: print("   " + a)

main()
