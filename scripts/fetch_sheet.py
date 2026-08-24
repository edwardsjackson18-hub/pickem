"""Pick'em extractor v2.

Sheet semantics (confirmed against the sheet's own tally rows):
  - green pick text  = that team won STRAIGHT UP   (red = lost). Not against the spread.
  - bold pick text   = that player's Superdog for the week (one per player per week).
  - Superdog scores the spread magnitude if that underdog wins outright, else 0.
  - The spread in the game label only matters for Superdog / favorite-dog labelling.
"""
import re, json, os, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SHEET = "1S6EdbH2tCHA76DTdzS0ebDIGMqsSOMwzkrnlP3lbfJc"
URL = "https://docs.google.com/spreadsheets/d/%s/htmlview/sheet?gid=%s"

TABS = [("Week 0","1392174358"),("Week 1","1378354909"),("Week 2","0"),
        ("Week 3","775703549"),("Week 4","292874478"),("Week 5","1757520906"),
        ("Week 6","374123801"),("Week 7","2071882811"),("Week 8","1846490586"),
        ("Week 9","585975588"),("Week 10","1787629366"),("Week 11","733454379"),
        ("Week 12","555159595"),("Week 13","783052014"),("Week 14","1878089129"),
        ("Conf Champ","1707671195"),("BOWLS","1211754437")]

GREEN = {"#00ff00","#0f0","#34a853","#0f9d58","#00b050","#008000","#38761d","#6aa84f","#93c47d","#b6d7a8"}
RED   = {"#ff0000","#f00","#ea4335","#db4437","#cc4125","#c00000","#cc0000","#a61c00","#e06666","#990000"}
SKIP  = re.compile(r"^(noon|afternoon|night|during the week|early|late|mon|tue|wed|thu|fri|sat|sun)", re.I)
TALLY = re.compile(r"^(record|superdog|total|points for the)", re.I)

def fetch(gid):
    req = urllib.request.Request(URL % (SHEET, gid), headers={"User-Agent":"Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8","replace")

def styles(html):
    out = {}
    for n, b in re.findall(r"\.([a-zA-Z0-9_-]+)\{([^}]*)\}", html):
        m = re.search(r"(?<!background-)color:(#[0-9a-fA-F]{3,6})", b)
        out[n] = {"color": (m.group(1).lower() if m else None),
                  "bold": "font-weight:bold" in b}
    return out

def untag(s):
    s = re.sub(r"<[^>]+>", "", s)
    for a, b in [("&amp;","&"),("&lt;","<"),("&gt;",">"),("&quot;",'"'),
                 ("&#39;","'"),("&nbsp;"," ")]:
        s = s.replace(a, b)
    return s.strip()

def parse(html):
    st = styles(html)
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        cells = []
        for attrs, inner in re.findall(r"<t[dh]([^>]*)>(.*?)</t[dh]>", tr, re.S):
            s = {}
            cm = re.search(r'class="([^"]*)"', attrs)
            if cm:
                for c in cm.group(1).split():
                    if c in st: s = st[c]; break
            col = s.get("color")
            cells.append({"t": untag(inner),
                          "r": "win" if col in GREEN else "loss" if col in RED else None,
                          "b": bool(s.get("bold"))})
        if cells: rows.append(cells[1:])
    if rows and all(re.fullmatch(r"[A-Z]{1,2}", c["t"] or "") for c in rows[0][:6]):
        rows = rows[1:]
    return rows

def spread_of(label):
    m = re.search(r"-\s?(\d+(?:\.\d+)?)", label)
    return float(m.group(1)) if m else None

def shape(tab, rows):
    hdr = next((i for i, r in enumerate(rows)
                if len([c for c in r[1:6] if c["t"]]) >= 2), None)
    if hdr is None: return None
    players = []
    for c in rows[hdr][1:]:
        if not c["t"]: break
        players.append(c["t"].strip())
    if not players: return None

    games, stated = [], {}
    slate = None; gdate = None
    for r in rows[hdr+1:]:
        label = r[0]["t"] if r else ""
        picks = [r[i+1] if i+1 < len(r) else {"t":"","r":None,"b":False}
                 for i in range(len(players))]
        if TALLY.match(label):
            k = "superdog" if re.match(r"^(superdog|points)", label, re.I) else "record"
            stated[k] = {p: c["t"] for p, c in zip(players, picks)}
            continue
        # a slate/date header is ALWAYS a header - Week 14's "NOON SLATE" row
        # had stray text in a pick column and leaked through as a game
        if SKIP.match(label):
            if re.match(r"^(mon|tue|wed|thu|fri|sat|sun)", label, re.I): gdate = label
            else: slate = label
            continue
        if not any(p["t"] for p in picks): continue
        games.append({"game": label, "spread": spread_of(label),
                      "slate": slate, "date": gdate,
                      "picks": {p: {"pick": c["t"], "won": c["r"], "superdog": c["b"]}
                                for p, c in zip(players, picks)}})
    return {"tab": tab, "players": players, "games": games, "stated": stated}

def main():
    allw = []
    print("%-11s %s" % ("TAB", "straight-up record  |  superdog pts (mine vs sheet)"))
    for tab, gid in TABS:
        d = shape(tab, parse(fetch(gid)))
        if not d or not d["games"]:
            print("%-11s (empty)" % tab); continue
        allw.append(d)
        rec, sd = d["stated"].get("record", {}), d["stated"].get("superdog", {})
        su, sp = [], []
        for p in d["players"]:
            w = sum(1 for g in d["games"] if g["picks"][p]["won"] == "win")
            l = sum(1 for g in d["games"] if g["picks"][p]["won"] == "loss")
            s = (rec.get(p) or "").strip()
            su.append("%s%s%d-%d" % (p.strip()[:4], "=" if s == "%d-%d" % (w, l) else "~", w, l))
            dog = [g for g in d["games"] if g["picks"][p]["superdog"]]
            pts = sum((g["spread"] or 0) for g in dog if g["picks"][p]["won"] == "win")
            want = (sd.get(p) or "").strip()
            try: ok = abs(float(want) - pts) < 0.01
            except: ok = False
            sp.append("%s%s%g/%s" % (p.strip()[:4], "=" if ok else "~", pts, want or "-"))
        print("%-11s %s" % (tab, " ".join(su)))
        if any(sd.values()):
            print("%-11s   SD %s" % ("", " ".join(sp)))
    json.dump(allw, open(os.path.join(ROOT,"picks.json"),"w",encoding="utf-8"), indent=1)
    print("\nwrote picks.json: %d tabs, %d games" % (len(allw), sum(len(w["games"]) for w in allw)))

main()
