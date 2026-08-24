# Brad and the Gang Pick 'Em

A static site over the pool's Google Sheet. Filter every pick by player, team,
conference, spread, favorite/underdog, slate or nickname, and see the records
that fall out.

Live at `https://edwardsjackson18-hub.github.io/pickem/` once Pages is enabled
(Settings → Pages → Deploy from branch → `main` / root).

## How the sheet is read

The sheet encodes more than the CSV export can carry, so the pipeline reads the
`htmlview` export instead, which preserves cell formatting:

| In the sheet | Means |
|---|---|
| **green** pick text | that team won **straight up** |
| **red** pick text | that team lost |
| **bold** pick text | that player's **Superdog** for the week |
| blank cell | counts as a **loss** |

Superdog scores the game's spread if that underdog wins outright, otherwise 0.
The spread is otherwise informational — the pool is **not** graded against the
spread. (Confirmed by the data: favorite win rate climbs 43% → 54% → 68% → 80% →
100% as the spread grows, which is the straight-up curve. Real ATS grading would
sit near 50% in every bucket.)

Two structural quirks, both validated against the sheet's own typed records:

- **Week 0** was never scored — it is excluded from every record.
- **Week 2** lists 21 games but the typed record covers 20. The dropped game is
  `#2 S Dakota St @ #3 Montana St`; excluding it makes all five players reconcile
  exactly. Week 6 has the same 21-vs-20 shape, but both candidate games were
  unanimous hits so which one was dropped can't be determined — and it can't
  change anyone's relative standing.

With those rules, every graded week reconciles exactly with the `Record this
week` row for all five players.

## Two sources, two jobs

| Source | Gives | Covers |
|---|---|---|
| `All_Time_Pick_Em.xlsx` | official weekly W-L and Superdog totals | 2023, 2024, 2025 |
| the Google Sheet | every individual pick, graded | 2025 + 2026 as it happens |

**The workbook is the ledger.** Season standings, all-time records and the
trophy case all come from it. The Google Sheet is where pick-level detail lives,
so the explorer and the charts are built from that.

They deliberately disagree, and the site says so. The official 2025 totals
(Robert 220-121) are higher than what the picks in the sheet add up to
(Robert 208-110), because Weeks 0 and 1 of 2025 were played and scored before
those tabs were cleared to make room for 2026. The records survive in the
workbook; the picks don't survive anywhere.

Note also that the sheet's **"Week 0" tab is now the 2026 opener**, not part of
2025 — confirmed against ESPN, where `SJSU @ USC` is dated 2026-08-29. It is
tagged `season: 2026` and excluded from 2025 records.

## Layout

```
index.html            the whole site - vanilla JS, no dependencies, no build step
season.json           pick-level data the page reads (generated)
history.json          official season + all-time records (generated)
picks.json            raw extract, one step upstream (generated)
scripts/
  fetch_sheet.py      pulls all 17 tabs, keeps colour + bold formatting
  build_season.py     resolves teams, applies scoring rules, writes season.json
  gameparse.py        game-label parser (22 label shapes, 0 failures)
  aliases.py          127-team alias/mascot/nickname table + hard overrides
  match_team.py       scoped fuzzy matcher
  smart.py            initials / substring / abbreviation fallbacks
  teams_2025.json     ESPN team + 2025 conference data
  parse_history.py    reads the all-time workbook -> history.json
  all_time_pickem.xlsx  the workbook itself, committed as the source of record
```

## Refreshing

```bash
python scripts/fetch_sheet.py && python scripts/build_season.py
```

The history only changes when a season ends, so it is refreshed by hand:

```bash
python scripts/parse_history.py scripts/all_time_pickem.xlsx
```

That script cross-checks its own computed all-time totals against the
workbook's `All-Time` row and reports any mismatch. It currently reconciles
exactly for all five players, records and Superdog.

`.github/workflows/refresh.yml` does this every Monday and commits the result.
The sheet is link-shared, so there are no credentials anywhere.

## Resolving nicknames

Picks are freeform and often jokes — `Cock Tuah`, `Hooty Hoo`, `Ole piss`,
`Angry broccoli`. Two things make this tractable:

1. **A pick can only be one of the two teams in that game.** Scoping the match to
   those two turns entity resolution into a coin flip with a strong prior, and
   globally ambiguous strings resolve fine — `USC` is South Carolina in
   `Clemson @ South Carolina`, and Southern Cal everywhere else.
2. **The `H8` rule.** Michael writes `H8 <opponent's mascot>` to mean he's taking
   the *other* side. All nine instances resolve to Georgia.

Currently **1586 / 1586 picks resolve (100%)**.

### The grading checksum

Everyone who picks the same side of a game gets the same colour. So if two picks
resolve to the same team but their colours disagree, the resolver is wrong. This
runs on every build, is enforced in CI, and it caught three real errors:
`Bandans` is Boston College (not Michigan State), `Nerds` is Duke, and
`Super weapon` is Pitt. It also means the actual winner of every graded game is
recoverable from the colours alone — no sports API needed.

**Add new nicknames to `scripts/aliases.py`.** If a pick can't be resolved from
its text, add a `(week, game, player)` entry to `HARD_OVERRIDES`.

## Known gaps

- **Bold-detection of the Superdog is incomplete**, so the site takes Superdog
  totals from the workbook rather than deriving them. Measured against the
  workbook for 2025: Robert reconciles perfectly (50.5), Jack is off by 0.5,
  Jackson by 2, Michael by 6.5, and **JP by 32.5** — he appears not to bold his
  at all. The bold flag is still shown on individual picks where it was found.
- **The 2023 standings block in the workbook has a bad cell.** It lists Michael
  at 163-97, which is 260 games when every other player played 251. His `Total`
  row says 154-97, which is consistent, and that is what the parser uses.
- **2023 and 2024 are weekly aggregates only** — no pick-level data exists, so
  the explorer, the charts and the nickname wall are 2025-only.
- Conference is 2025 alignment, deliberately. Seventeen teams move in 2026, so a
  "current" list would mislabel this season. Rebuild `teams_2025.json` from
  ESPN's season-scoped endpoint for a new year.
