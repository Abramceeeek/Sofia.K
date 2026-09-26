# Area 14 — Spatial moment detection (light scan)

**Decision:**
- **Score "reveals" on walking approaches with 2D isovists.**
  - Sample points every ~5 m along the walking path (OSRM).
  - At each point, cast rays against OSM or Overture building footprints (Shapely, BSD) and record the visible area A(s).
  - A reveal is a large jump in log A(s) over a short distance: compression, then release.
- **Use it to rank candidate approaches for the founder** and as the value of the *contrast/reveal* feature. It is not a filter.
- **Calibrate against the 5 seed moments** (e.g. South Kensington exit → Natural History Museum), then against per-moment ratings.
- **Add Scenic-Or-Not ratings as a "view quality" prior** near each point.
- **Cost: ~8–10 h after Phase 3.** Not in the v0 36 h.

## What exists

| # | Name | Maturity | Licence | Why it matters |
|---|---|---|---|---|
| 1 | Shapely 2.1.2 (PyPI 2025-09-24; last commit 2026-09-23) | Production | BSD-3 | Ray casting and polygon area. Python ≥3.10, so it runs on 3.12. Enough for 2D isovists |
| 2 | depthmapX (SpaceGroupUCL): 244 stars, last commit 2026-08-09, active | Research tool | GPL-3.0 | Isovist and visibility-graph analysis with a CLI. Fine for internal exploration, since it isn't shipped |
| 3 | pyvispoly: CGAL visibility polygons, 6 stars | Small | GPL (CGAL) | Exact visibility polygons. Heavier dependency; skip unless ray casting is too slow |
| 4 | Scenic-Or-Not: 217k Geograph images rated 1–10, votes to Feb 2015 | Dataset | ODbL | Scenicness near each point. Share-alike applies to derived databases |
| 5 | Overture buildings theme (includes OSM, Microsoft and Google footprints) | Production | ODbL (theme) | Footprints for isovists. Heights are patchy |

## What the evidence says

- **Isovists capture something people feel.** Wiener et al. (2007, *Perception*) correlated isovist measures of 16 virtual indoor scenes with navigation and with "introspective appraisal of experiential qualities". They found **strong correlations with a small set of isovist measures**. Caveat: indoor, virtual and small, so transfer to London streets is unproven.
- **Isovists are Benedikt's (1979) visible-area polygons.** A sequence of them along a route is the computable form of Cullen's "serial vision", the founder's compression-and-release idea (both search only).
- **What makes a place scenic.** Seresinhe, Preis & Moat (2017, *Royal Society Open Science*) found that Scenic-Or-Not ratings rise with coast, mountains and canals, **and** with built features like towers, castles and viaducts. Trees rate highly, but bland green (grass, athletic fields) rates *lower*. A CNN learned to predict scenicness.
- **City-scale 3D isovists** at pedestrian level exist (MDPI *Buildings* 2026, search only). That shows feasibility beyond 2D.

## Gaps / risks

- **2D footprints ignore trees, terrain and building height.** A street canyon opening onto a low square may read like an open field. 3D needs heights (LiDAR). Defer that.
- **Tube exits.** The dark-to-open transition starts underground. Model station entrances (`railway=subway_entrance` in OSM) as A ≈ 0, then the street isovist.
- **The threshold for a "jump" is a guess.** For example, 3× visible area within 20 m. Fit it on the seed moments and the ratings.
- Scenic-Or-Not data stops at 2015, and ODbL share-alike applies if we publish a derived database.

## Addendum (D28): God's Eye View for moment previews (post-v0 only)

**Decision:**
- **Reuse the pattern, not the app.** Build a minimal CesiumJS page (Apache-2.0) that streams **Google Photorealistic 3D Tiles directly with a Google Maps key**. Google's docs say to give the root tileset URL to a renderer "like CesiumJS", so no Cesium ion is needed.
- Add a camera path along the OSRM approach and a camera pose for each shot card.
- **Take none of God's Eye View's tracking or surveillance layers** (flights, ships, satellites, ~3,600 CCTV cameras, licence-plate-reader locations, "sensor modes").
- **Analysis (isovists) stays on OSM/Overture in Python:** Google's terms forbid it on its tiles (below).
- **Cost: ~8–10 h post-v0.** About 6–8 h for the preview page, and ~2 h for Abram to set camera poses for the ~20 shot cards.

| | God's Eye View (bilawalsidhu/gods-eye-view) |
|---|---|
| Stars / licence / last commit | 43.3k stars, 8.8k forks, **MIT**; last commit 2026-09-25, active. JavaScript (Vite, CesiumJS), so Python 3.11+ is n/a |
| Useful parts | Google 3D Tiles in CesiumJS, walk-route planning, a "scene director" for cinematic camera sequences, shareable view-state URLs |
| Excluded | Every tracking and CCTV layer, military installations, OpenAI voice control |
| Keys it expects | Cesium ion (the free Community plan is personal and non-commercial only), Google Maps (metered), OpenAI and others. We would need only Google |

**What Google's terms allow** (Map Tiles API policies, fetched 2026-09-26):

- **(a) Pre-trip moment preview (anticipation, Area 6): yes, as a live render only.**
  - Display with the Google Maps logo and the per-tile data attributions is allowed.
  - Tiles may not be pre-fetched, cached, stored or used offline.
  - Videos made from tiles are allowed only as *promotional* clips up to 30 seconds, not sold or given out as part of the product.
  - → The preview must be an online, in-browser flythrough (web link or Telegram Mini App), **not a video file** sent to the user.
- **(b) Shot-card view preview: yes, as a live camera at the shot pose.** No stored screenshots or rendered images. That is our reading of the no-storage rule, not an explicit clause.
- **Analysis: no.** The Map Tiles API may not be used for "image analysis", "machine interpretation", "object detection" or "geodata extraction". Our own 3D objects may be overlaid only if they aren't traced or derived from the tiles.

**Cost:** Photorealistic 3D Tiles give 1,000 root-tileset requests a month free, then $6.00 per 1,000. One root request covers at least 3 hours of tile requests, so one preview costs about $0.006 after the free tier. Cesium ion Commercial ($149/month individual) is avoided by going direct to Google.

**Risks:**
- **Spoiling the reveal.** A flythrough of a contrast/reveal moment gives away the thing we sell. Preview the approach and the shot card, and stop short of the reveal.
- **Street-level quality.** Photogrammetry is weakest at pedestrian eye level: **UNVERIFIED**. Test on 3 seed moments before building.
- **Mobile data and WebGL in Telegram's in-app browser: UNVERIFIED.**
