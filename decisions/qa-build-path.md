# An internal QA build (proposal, 24 Nov 2026)

**Decision first:** a version-labelled QA build Abram can use on his own phone, kept entirely apart from the friends' round. It is prepared but **nothing is uploaded, deployed or handed out without Abram's approval** (24 Nov: "Do not upload or distribute anything without Abram's approval").

## What exists now, at no cost
- **iPhone:** a manual run of `ios.yml` on this branch compiles the app for the simulator and takes the screenshots, with bundled sample data. The repository is public, so GitHub's macOS runners are free. A branch run can't reach TestFlight: the m197 guard uploads only from `main`.
- **Android:** every push builds the app and draws every screen with Robolectric, saved as the run's `ODYS-android-screens-<run>` artifact. No APK is handed out (Abram, 20 Nov: off until his own release key exists).
- **Brain:** the branch's Brain runs only in CI and locally. Render deploys `main` only, by hand, so the live Brain is still the friends' round's.

**Labels:** each screenshot set belongs to its CI run, whose commit is shown on the run page. The app shows its own version and build in settings. Every stored plan is stamped with its Brain commit and the app build (m327).

## The screenshots Abram asked for (24 Nov), and where they are

| Screen | iPhone screenshot (`ios.yml`) | Android screen test |
|---|---|---|
| Trip creation, with "How would you like your days to feel?" | `tripwhere`, `tripwhen`, `tripfrom`, `tripdays` | `20-tripcreate`, `21-tripwhen`, `22-tripfrom`, `22a-tripdays` |
| The generated itinerary | `trip`, `tripday`, `plan`, `plan2` | `24-trip`, `25-tripday`, `09-plan`, `09b-plan2` |
| Other places for one stop | `swap` | `10i-swap` |
| The rain swap (new, m349) | `stoprain` | `10p-stoprain` |
| Re-planning the rest of the day | `replan` | `10h-replan` |
| Costs and practical information | `planbudget`, `stop`, `stop2` | `09g-planbudget`, `10-stop`, `10a-stop2` |

These are **screenshots of sample data, not proof the app works on a phone with the real Brain.** That needs the QA build below.

## What a QA build on a phone needs (each step is Abram's to approve)

1. **A QA Brain:** the branch's Brain as its own Render service (for example `odys-brain-qa`), with its own empty database. It must never touch the friends' round's database.
   - **Cost:** Render's free tier, $0, with a slow first start; or the paid plan Abram uses for production.
   - **Hours (GUESS):** Claude ~0.5 h for the blueprint entry; Abram ~20 min in Render.
2. **iPhone, one of two ways:**
   - **(a) A separate app:** another bundle ID (`ODYS QA`) and its own TestFlight internal group, pointed at the QA Brain. It can't replace or notify the friends' build. It needs the m197 guard to allow that one bundle from a branch, which is a change to a release control, so **Abram decides it**.
   - **(b) Wait for the merge:** test after the round, on `main`.
   - **Hours (GUESS):** (a) Claude ~1.5 h for the workflow input, the bundle and the label on the app ("QA build · Brain <commit>"); Abram ~15 min in App Store Connect.
3. **Android:** an APK signed with a debug key, installed only on Abram's own phone, pointed at the QA Brain.
   - This goes against his 20 Nov rule (no APK until his release key exists), so **it's his call**.
   - **Hours (GUESS):** Claude ~0.5 h.

**Risk to the friends' round:** none, if the QA app has its own bundle ID, its own TestFlight group and its own Brain and database. All three are required.
