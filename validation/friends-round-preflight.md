# The friends' round preflight: moved (20 Nov 2026)

**The checks before the tag are now one table in `validation/friends-round.md`:** "The seven conditions before the tag" (Abram, 20 Nov §4), after the ordered list "Open before the first invite".

This page's 19 Nov checks were:
- `main` and the live Brain at `80a0da3`;
- TestFlight 91 and Android 21 matching the manifest;
- no remote tag;
- the latest backup;
- the rehearsal;
- no experimental change.

They all held then, and all are carried into that table. Two things changed since:
- **Android build 21 is ruled out:** its certificate is the public debug key's (`decisions/android-signing-key-runbook.md`).
- **The backup check is now the single `preflight` command** (`decisions/database-before-6-dec.md`).
