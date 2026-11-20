"""m197: a rehearsal of a Test B round, end to end, on a throwaway SQLite database (never the live one).

Seven made-up installs go through the Brain as the apps would (tester codes typed three ways, a pre-round install with
no code, one who is shown the pair and never answers, a visitor from abroad), then the admin export and the read-out,
and the read-out's numbers are checked against the ones worked out by hand below.

To rehearse the exact code testers use, run it against that commit's Brain (here the friends' round, tag
friends-round-1), from a checkout of it:
    git worktree add /tmp/frozen friends-round-1
    cd /tmp/frozen/brain && PYTHONPATH=src <venv>/bin/python <this repo>/brain/scripts/rehearse_testb.py /tmp/rehearsal
"""
import json
import sys
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

import brain
from brain.api import create_app
from brain.config import DATA_DIR, Settings

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
print("Brain code from:", Path(brain.__file__).resolve().parents[1])
tmp = Path(tempfile.mkdtemp())
settings = Settings(database_url=f"sqlite:///{tmp / 'rehearsal.db'}", data_dir=DATA_DIR, admin_token="rehearsal-admin",
                    alert_webhook_url=None, planner_time_limit_s=1.0)
ADMIN = {"Authorization": "Bearer rehearsal-admin"}

# who: (name, code, based, swipes, pair answer or None for "shown, not answered", survey)
# pair answer: (gut: "personal"|"generic", fit_personal, fit_generic, easier: "personal"|"generic"|"same"|None, why)
TESTERS = [
    ("old-own-build", None, "london", [(4, "loved")], ("personal", 5, 2, None, None), None),   # before the round
    ("f1", "FRIENDS", "london", [(4, "loved"), (3, "didnt_enjoy")], ("personal", 5, 3, "personal", "More me."), {"understood": 4}),
    ("f2", "friends", "london", [(2, "loved")], ("generic", 2, 4, "generic", "Less walking."), {"understood": 3}),
    ("f3", " Friends ", "london", [(1, "loved"), (5, "didnt_enjoy")], ("personal", 4, 4, None, None), None),
    ("f4", "FRIENDS", "uk", [(6, "loved")], ("generic", 3, 3, "same", "Hard to say."), {"typed_or_spoke": "typed"}),
    ("f5", "FRIENDS", "london", [(3, "loved")], None, None),                                    # shown, never answered
    ("f6", "FRIENDS", "abroad", [], "visitor", None),                                           # visitor: no pair
]

with TestClient(create_app(settings)) as c:
    ids = {}
    for name, code, based, swipes, answer, survey in TESTERS:
        body = {"channel": "stranger", "src": None,
                "consent": {"version": "app-2026-10-02", "research": True, "ai_processing": False}}
        if code:
            body["code"] = code
        r = c.post("/v1/installs", json=body)
        assert r.status_code == 201, r.text
        h = {"Authorization": f"Bearer {r.json()['token']}"}
        ids[name] = r.json()["user_id"]
        prof = {"based": based} | ({"home_city": "Paris"} if based == "abroad" else {}) | (
            {"home_city": "Leeds"} if based == "uk" else {})
        assert c.put("/v1/me/profile", headers=h, json=prof).status_code == 204, prof
        if swipes:
            assert c.post("/v1/me/swipes", headers=h,
                          json={"items": [{"item": i, "reaction": x} for i, x in swipes]}).status_code == 204
        if survey:
            assert c.post("/v1/me/survey", headers=h, json=survey).status_code in (200, 201, 204)
        if answer == "visitor":
            r = c.post("/v1/me/testb/pair", headers=h, json={})
            print(f"{name}: visitor asks for the pair -> {r.status_code}")
            continue
        r = c.post("/v1/me/testb/pair", headers=h, json={"mood": "explore", "company": "friends"})
        assert r.status_code == 201, (name, r.text)
        if answer is None:
            continue
        gut, fp, fg, easier, why = answer
        # which label is personal is hidden from the app; the rehearsal reads it from the database, like a cheat sheet
        with c.app.state.Session() as s:
            from brain import db
            rows = s.query(db.Plan).filter_by(user_id=ids[name]).all()
            label = {p.kind: p.label for p in rows if (p.intent or {}).get("testb_pair")}
        lab = lambda k: label[k]
        fits = {lab("personal"): fp, lab("generic"): fg}
        fb = {"chosen": lab(gut), "fit_1": fits["1"], "fit_2": fits["2"]}
        if easier:
            fb["easier"] = "same" if easier == "same" else lab(easier)
        if why:
            fb["why"] = why
        r = c.post("/v1/me/testb/pair/feedback", headers=h, json=fb)
        assert r.status_code == 200, (name, r.text)
    export = c.get("/v1/admin/export", headers=ADMIN).json()

(out / "export.json").write_text(json.dumps(export, indent=1))

# the read-out (this repo's version), checked against the counts worked out by hand
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("testb_report", Path(__file__).with_name("testb_report.py"))
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)
codes = {u["src"] for u in export["users"]}
assert codes == {None, "code:FRIENDS"}, codes                       # "friends" and " Friends " are FRIENDS too
assert export["cohorts"][ids["f6"]] == "visitor"
everyone = "\n".join(tr.only(export)[1] + tr.report(export, overlap=None))
friends, head = tr.only(export, code="FRIENDS")
round_only = "\n".join(head + tr.report(friends, overlap=None))
for text, want in [
    (everyone, ["by source: code:FRIENDS 6, no code 1", "5 UK testers answered", "1 was shown it",
                "chose the personal plan: 3 of 5", "both rated by 5 of 5; missing for 0", "mean +0.60",
                "personal rated higher by 2 of the 3", "3 of 5 answered (2 didn't)"]),
    (round_only, ["6 of the 7 in this export", "4 UK testers answered", "1 was shown it",
                  "chose the personal plan: 2 of 4", "both rated by 4 of 4; missing for 0", "mean +0.00",
                  "3 of 4 answered (1 didn't): personal 1, generic 1, about the same 1",
                  "Chose the generic plan: 2 of 4", "why: Less walking.", "why: Hard to say."]),
]:
    for w in want:
        assert w in text, (w, text)
print(round_only)
print("\nRehearsal passed: every count matches the one worked out by hand.")
