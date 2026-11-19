# The friends' round: preflight for the tag `friends-round-1` at `80a0da3` (19 Nov 2026)

Abram's decision of 19 Nov, §3: the tag goes on **exactly `80a0da3`**, never `474eca1` or anything newer, once every check below holds. **Abram pushes the tag himself.** Nothing here creates a tag, deploys or changes the experiment.

| # | Check | Result (19 Nov, ~19:00 UTC) | How it was checked | Who |
|---|---|---|---|---|
| 1 | `main` is still `80a0da3` | **Holds** | `git ls-remote origin refs/heads/main` → `80a0da3d117a…` | Claude |
| 2 | The live Brain reports `80a0da3` | **Holds** | one read-only `GET https://moments-brain.onrender.com/v1/health`: `"version":"80a0da3"`. It also reported flights `duffel_test`, stays `liteapi_sandbox`, travel `tfl`, weather `met_office`: test keys, labelled in the apps | Claude |
| 3 | TestFlight build 91 matches the manifest | **Holds on GitHub's side** | iOS workflow run **#91** is the push build of `80a0da3` on `main`, green (6 Nov 22:18 UTC). The build number is the run number (`ios.yml`) | Claude. **Abram: confirm App Store Connect → TestFlight shows build 91 as the one testers get** |
| 4 | Android build 21 matches the manifest | **Holds** | the `android-latest` release is "ODYS for Android (build 21)", target `80a0da3`, asset `ODYS-android-21.apk`, digest sha256 `43a3e80dd38abdab72a3a1bb2da6f7c2b8104682729189829a83d4563129174c`, published 6 Nov | Claude |
| 5 | The remote tag doesn't already exist | **Holds** | `git ls-remote origin refs/tags/friends-round-1` returns nothing. The only tag is `android-latest` | Claude |
| 6 | The latest backup is valid | **Made; not yet opened** | the nightly `ops` backup job ran green on 19 Nov at 10:30 UTC on `80a0da3`: the sealed file is kept 30 days. **Opening it needs Abram's private key:** `python -m brain.backup verify <file> --key <key>` gives "Whole and consistent." | **Abram** |
| 7 | The real-device rehearsal passed on both phones | **Waiting** | `friends-round-rehearsal.md`, 25 steps, with the code `REHEARSAL`, on TestFlight 91 and Android 21 | **Abram** (Claude reads the read-out) |
| 8 | No experimental question or recommendation logic has changed | **Holds** | `main` hasn't moved from `80a0da3` since 6 Nov (check 1), and the live Brain runs it (check 2). The development work, PR #1 included, is on other branches and never reaches `main` | Claude |

**Abram's Render items before the first invite** (from his 19 Nov decisions; not part of the tag):
- **The 1 CPU server:** the live Brain runs on Render's **free** plan today (0.1 CPU), not 1 CPU. Keeping the round on 1 CPU means changing `moments-brain` to `1c-2g` ($25 a month) **before the first invite**, so every tester's plans come from the same machine.
  - It redeploys the same commit: check that `/v1/health` still says `80a0da3` afterwards.
  - About the Blueprint, see `decisions/database-upgrade-runbook.md`.
- **The alert webhook:** check `BRAIN_ALERT_WEBHOOK_URL` and decide on the privacy patch (`decisions/production-privacy-patch.md`).
  - If the A1 or A2 patch is deployed, check 2 becomes "reports the approved privacy commit", and the manifest records it.
  - The tag stays on `80a0da3`.

**When checks 6 and 7 hold, Abram runs:**

```bash
git fetch origin main && git tag -a friends-round-1 80a0da3 -m "The friends' round's fixed version" && git push origin friends-round-1
```

**Then Claude confirms:**
- `git ls-remote origin refs/tags/friends-round-1` points at `80a0da3`;
- the manifest (`validation/friends-round.md`) records the date.
