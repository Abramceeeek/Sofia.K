# Research

One note per area in `notes/`, copied from `notes/_template.md` and named `NN-slug.md`
(e.g. `01-onboarding.md`). Every source cited in a note gets one row in `sources.csv`.

## `sources.csv` columns

| Column | Values |
|---|---|
| `area` | Area number (`1`–`19`), `econ` for unit-economics sources, or `val` for Phase 3 validation tooling |
| `type` | `paper`, `book`, `repo`, `dataset`, `product`, `docs`, `pricing`, `guidance`, `report` |
| `title` | Title as published (third-party sources say so in the title) |
| `url` | Canonical link (DOI / repo / official page), or the third-party page actually used |
| `date_accessed` | `YYYY-MM-DD` |
| `key_finding` | One sentence; quote numbers where they exist |
| `use_adapt_skip` | `use`, `adapt` or `skip` |
| `verified` | `fetched`: page opened in the session and the finding read on it. `search`: finding confirmed only through web-search result text, because the page was blocked or not opened. `UNVERIFIED`: seen only as a secondary citation, or not traced to its source |
| `stars` | Repos only: GitHub stars at access date |
| `last_commit` | Repos only: date of latest commit on the default branch |
| `licence` | Repos only: SPDX id where possible |
| `maintenance` | Repos only: `active` (commit ≤3 months), `slow` (3–12 months), `stale` (>12 months), `archived` |
| `py311` | Repos only: runs on Python 3.11+? (`yes (...)`, `no`, `untested`, `n/a` for non-Python) |

## Access limits in this environment

Areas 1 and 4 were first researched under a network policy that blocked most publisher, docs and pricing sites, so many of their rows are `search`. Network access was widened on 2026-09-26, and arxiv.org, aclanthology.org, huggingface.co, open-meteo.com, developers.google.com and author homepages now load. Three publisher sites still return 403 to automated requests: dl.acm.org, tandfonline.com and journals.sagepub.com. For those, use arXiv or author-hosted copies. Re-check `search` rows against the primary page whenever a note is revised. Prices come first.
