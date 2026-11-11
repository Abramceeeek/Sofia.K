# A day, flat and in relief (proof of concept)

The audit's one 3D experiment (`decisions/odys-3d-and-spatial-experience.md`). One file, `index.html`: no libraries, no
map tiles, no network. Open it in any browser.

It draws the app's own sample day (`app/Sources/Demo/demo_plan.json`, copied into `day.json`) two ways from the same
numbers: **flat** (from above, each stop a dot sized by the time spent there) and **in relief** (the same ground
tilted, each stop a column as tall as the time spent there, in plain WebGL). It is a sketch of the day, not a model of
London: only the stops' own coordinates are drawn, so nothing in it can be wrong about the real place.

```bash
node prototype/day-in-relief/measure.js     # writes measurements.json and screens/
```

Measured on 11 Nov 2026 in headless Chromium, a 390 × 844 screen at 2× (`measurements.json`):

| | Flat | In relief |
|---|---|---|
| One drawing | 0.5 ms (2.0 ms with the processor slowed 4×) | 7.1 ms (10.7 ms slowed 4×) |
| First drawing after opening | 49 ms (94 ms slowed 4×), both views in the one file | the same file |
| Size | 18.7 KB for both views together (7.4 KB compressed) | |
| Network requests | 0 | 0 |
| Works with a screen reader | The day is a list in words; the drawing is hidden from readers and adds nothing to it | The same |
| Moves by itself | No | No (one drawing per change; drag, pinch or arrow keys turn it) |

Headless Chromium draws WebGL in software, so the relief time is a worst case for a phone with a working graphics chip,
and nothing here measures battery: only a phone can.

**What it shows.** Both are quick and small. The relief view is about 14 times the work per drawing and tells the
person nothing the flat view doesn't: a day's stops last 45 to 50 minutes each, so the columns are all but the same
height, and tilting the ground makes the far stop (Greenwich, 8 km away) look nearer than it is. The verdict and what
to do instead are in the decision document.
