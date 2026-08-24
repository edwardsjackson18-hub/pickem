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

## Layout

```
index.html            the whole site - vanilla JS, no dependencies, no build step
season.json           what the page reads (generated)
picks.json            raw extract, one step upstream (generated)
scripts/
  fetch_sheet.py      pulls all 17 tabs, keeps colour + bold formatting
  build_season.py     resolves teams, applies scoring rules, writes season.json
  gameparse.py        game-label parser (22 label shapes, 0 failures)
  aliases.py          127-team alias/mascot/nickname table + hard overrides
  match_team.py       scoped fuzzy matcher
  smart.py            initials / substring / abbreviation fallbacks
  teams_2025.json     ESPN team + 2025 conference data
```

## Refreshing

```bash
python scripts/fetch_sheet.py && python scripts/build_season.py
```

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

- **JP's Superdog isn't detected.** The other four bold their pick and their
  totals reconcile (Robert 50.5 exactly matches the sheet). JP's don't, so
  either he marks his differently or doesn't bold it. His Superdog totals are
  understated until that's sorted.
- Conference is 2025 alignment, deliberately. Seventeen teams move in 2026, so a
  "current" list would mislabel this season. Rebuild `teams_2025.json` from
  ESPN's season-scoped endpoint for a new year.
