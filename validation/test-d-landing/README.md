# Test D landing page — set-up (≈1 founder hour)

A static page with **no payments and no card details** (D1, D25). It randomly shows arm A (£4.99/month) or arm B (£9.99/month); both arms also show £59.99/year. Every button leads to the same waitlist form, and the priced buttons first show an honest note.

## Steps

1. **Waitlist form (Tally, free plan).**
   - Fields: email, and "anything you'd want from it?" (optional).
   - Add **hidden fields** `arm`, `choice`, `price`, `src`, `ref`. Tally fills hidden fields from URL parameters (tally.so/help/hidden-fields, fetched 2026-09-26).
   - Add a consent line linking to the privacy page.
2. **Visit counting (GoatCounter, free for reasonable use, no cookies, fetched 2026-09-26).**
   - Create a site and put its code in place of `GOATCOUNTER_CODE`.
   - Page views arrive as `/arm-A` and `/arm-B`; study participants arrive as `/participant-arm-A` and `/participant-arm-B`.
   - Clicks arrive as events such as `click-monthly-arm-B`.
3. **Fill in** `TALLY_FORM_URL` and `CONTACT_EMAIL` in `index.html`, and `[date]`, `[surname]` and `[email]` in `privacy.html` (generated from `../privacy-notice.md`; keep the two in sync).
4. **Host as a Render static site** ("always free to deploy", render.com/pricing, fetched 2026-09-26).
   - GitHub Pages is not suitable: its limits page rules out sites "primarily directed at ... commercial transactions".
5. **Test both arms:** open in a private window twice, and check the form receives `arm`, `choice`, `price`, `src` and `ref`.

## Links to post

| Use | Link |
|---|---|
| Recruitment post in a group | `https://<site>/?src=<group-id>` |
| Study participant's referral link (Test C) | `https://<site>/?src=invite&ref=P07` |
| Study participants at the close | `https://<site>/?src=participant` |

## Reading the results (into `results-sheet.xlsx` → `TestD`)

- **Visits per arm:** GoatCounter paths `/arm-A` and `/arm-B` (exclude the `participant` paths).
- **Sign-ups per arm and option:** the Tally export, filtered to `src` ≠ `participant`.
- **Invitee sign-ups:** Tally rows with a `ref` code. These go to the `TestC` tab for K. Report the Test D rates with and without them.
