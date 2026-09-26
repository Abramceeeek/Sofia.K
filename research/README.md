# Research

One note per area in `notes/`, copied from `notes/_template.md` and named `NN-slug.md`
(e.g. `01-onboarding.md`). Every source cited in a note gets one row in `sources.csv`.

## `sources.csv` columns

| Column | Values |
|---|---|
| `area` | Area number, `1`–`12` |
| `type` | `paper`, `book`, `repo`, `dataset`, `product`, `docs`, `pricing`, `guidance` |
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

The network policy blocks most publisher, docs and vendor-pricing sites, including arxiv.org, dl.acm.org, huggingface.co, developers.google.com, api.tfl.gov.uk, open-meteo.com and journals.sagepub.com. GitHub pages and PyPI are reachable. Rows marked `search` should be re-checked against the primary page once those hosts are allowed. Prices are the first thing to re-check.
