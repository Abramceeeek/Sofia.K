# The isolated QA environment (prepared 25 Nov 2026)

**Decision first:** Abram approved preparing a QA environment kept completely apart from production and the friends' round (25 Nov), with conditions:
- a separate Brain and database, and a separate app identity;
- provenance on every plan;
- no production data;
- nothing uploaded or invited without his explicit approval and the Apple policy check.

**Everything below is prepared. Nothing is created, deployed, uploaded or shared.**

| Piece | Prepared (on the branch) | Abram's step to switch it on | Cost |
|---|---|---|---|
| **QA Brain and database** | `render-qa.yaml`: `odys-brain-qa` deploys this branch by hand (Auto-Deploy off), with its own database `odys-brain-qa-db` and admin token. No safety webhook, no flight or stay keys, no production secret. `render.yaml` is unchanged (m198) | In Render: New → Blueprint, pick `render-qa.yaml`, deploy. Check `GET /v1/health` `version` | $0 (free tier). The free database expires after 30 days, which suits short-lived QA data |
| **Provenance** | Every stored plan already records its Brain commit and the app build (m327). The QA builds record their commit and run number | — | — |
| **Android QA app** | Build type `qa`: `com.odys.app.qa`, version `-qa`, installed beside the real app, reaching only the QA Brain. Workflow `android-qa.yml`, manual only: a debug-signed APK kept 7 days as the run's artifact. It refuses the production Brain's address | Run `android-qa` with the QA Brain's address, then install the APK on his own phone | $0 |
| **iPhone QA app** | Workflow `ios-qa.yml`, manual only. It builds "ODYS QA" for the simulator with a QA bundle ID and the QA Brain, on that run only (`project.yml` unchanged), and refuses the production Brain. Its upload job stops unless `QA_UPLOAD_APPROVED` is `yes`, and isn't wired to TestFlight yet | See "Before any QA TestFlight build" below | $0 while the repository is public |

**What runs on it:** the six moderated sessions (`validation/human-testing/script.md`), including the trip two friends plan together from their own phones (m358). Their data is deleted in the app at the end of each session, and the QA database within 30 days of the last one (proposed; Abram to agree).

## Before any QA TestFlight build (each one Abram's)
1. **The Apple policy check:** Apple's outside-activities policy, and the IP clause in his Apple contract (`CLAUDE.md` legal gates; D60, D94), before any external TestFlight build. A QA group of internal testers on his own account still needs his go-ahead.
2. **A QA app in App Store Connect:** its own bundle ID (for example `….odys.qa`), its own provisioning profile, and an internal TestFlight group named "ODYS QA", never the friends' group.
3. **The QA signing secrets** in GitHub, under QA names, so they never replace the friends' round's.
4. **Then** Claude wires the upload job (~1 h). Abram sets `QA_UPLOAD_APPROVED` to `yes` for one run, and back afterwards.

## What QA never touches
- the production Brain (`moments-brain`) and its database;
- the friends' round app, its TestFlight group and `main`;
- real payments, bookings or financial services (none exist);
- the `android-latest` download.
