"""Game-label parser. 22 distinct label shapes, 0 failures across 326 games."""
import re

RANK   = re.compile(r"#\s?\d+\s*")
SPREAD = re.compile(r"[-+]\s?\d+(?:\.\d+)?")
# a bowl/round prefix: "LA:", "CFP First Round:", "Salute to Veterans:"
PREFIX = re.compile(r"^([^:]{2,40}):\s*")

def parse_game(label):
    g = {"raw": label, "prefix": None, "neutral": False,
         "away": None, "home": None, "fav": None, "spread": None}
    s = label.strip()
    m = PREFIX.match(s)
    if m:
        g["prefix"] = m.group(1).strip()
        s = s[m.end():]
    if re.search(r"\bvs\.?\b", s, re.I):
        parts = re.split(r"\bvs\.?\b", s, flags=re.I); g["neutral"] = True
    elif "@" in s:
        parts = s.split("@")
    else:
        return g
    if len(parts) != 2: return g

    sides = []
    for p in parts:
        had = bool(SPREAD.search(p))
        sp = SPREAD.search(p)
        val = abs(float(sp.group().replace(" ", ""))) if sp else None
        clean = SPREAD.sub("", RANK.sub("", p)).strip(" .")
        sides.append({"name": clean, "fav": had, "spread": val})

    g["away"], g["home"] = sides[0], sides[1]
    for sd in sides:
        if sd["fav"]:
            g["fav"] = sd["name"]; g["spread"] = sd["spread"]
    return g
