# Daily Incantation

A single page that shows one incantation a day. Built to be added to an iPhone home screen,
where it opens full screen with no browser chrome and works offline once loaded.

Live at **https://nati-nath.github.io/incantations/**

## How it picks the line

Not at random, and not from the date. It is a **rotation**: the app walks
`incantations.json` in file order, one line per day, and wraps back to the top at the end.
So every line is seen exactly once per cycle, currently 103 days.

The position is stored on the device rather than derived from the date. That means editing
the collection never changes the line already showing for today.

## Keep and remove

**♡ Love it** marks a line. **✕ Not for me** drops it out of the rotation immediately.
Both are stored on the device only, never in this repo.

The counter at the bottom opens a panel with a Copy button that exports the rejected ids,
so they can be deleted from `incantations.json` for good. That is the only way votes make it
off the phone, and it is deliberate: nothing about what you rejected is ever published.

## The collection

103 lines, each tagged with a `category` recording how well-sourced it is, because they are
not equally attributable:

| category | count | what it is |
|---|---|---|
| `incantation` | 6 | Robbins' own incantations, from his event manuals |
| `primary-question` | 1 | His stated Primary Question |
| `winners-creed` | 10 | The Winner's Creed from a Life Mastery manual, adapted from Napoleon Hill |
| `quote` | 31 | Robbins speaking or writing, usable in the first person |
| `event-manual` | 33 | Quotes by **other** people, collected in his manuals |
| `circulating-online` | 22 | Widely shared in Robbins-adjacent lists but **not traceable to him** |

The last group is shown in gold in the app with the label "Widely shared, but not traceable
to Robbins", rather than being passed off as his.

Sourced chiefly from unleashyourinnerstrength.com, which reproduces material from Unleash the
Power Within, Date With Destiny, Wealth Mastery, Life Mastery and Leadership Academy manuals.

## Files

| file | purpose |
|---|---|
| `index.html` | the whole app: markup, styles and logic |
| `incantations.json` | the collection. File order is rotation order. `id` is permanent |
| `icon-180.png`, `icon-512.png` | home screen icons |
| `make-icon.py` | regenerates the icons |
| `manifest.webmanifest` | app name and colours for the home screen |

## Running it locally

It must be **served**, not opened as a file, because a browser will not let a local file read
another local file:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000

## Changing the collection

```bash
# 1. edit incantations.json: add a line, or delete ones you rejected on the phone

# 2. check the JSON still parses
python3 -m json.tool incantations.json > /dev/null && echo valid

# 3. publish
git add -A && git commit -m "prune the collection" && git push
```

The live site updates about a minute later. Close and reopen the phone app to get past the cached copy.

Rules:

- **Never renumber `id`.** The device's keep/remove votes refer to ids, so renumbering silently
  reassigns your votes to the wrong lines.
- File order is rotation order. Reorder freely, it will not move the line already showing today.
- Adding at the end is safe; it gets reached at the end of the current cycle.
- To act on the votes stored on a device, open the counter at the bottom of the app, tap Copy, and
  use the exported `remove ids: ...` list to delete those entries here.
