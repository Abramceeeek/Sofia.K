"""D114: sharing a rated moment, and the referral funnel for Test C's K.

A person who rates a stop can share a card (the moment's photo, their own rating, "planned with Days out") with a link
to `/r/<code>?m=<moment>`. The funnel is: shared (the app's `share_sent` event) → opened (the page's script, so link
previews don't count) → installed with `src = "ref:<code>"` → onboarded (`onboarding_done`) → first plan.

No rewards, and no names: a code belongs to one install, and the person who installs through it only carries the code.
"""

from __future__ import annotations

import html
import json
import secrets

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import db

ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"   # no 0/O or 1/I/L, so a code read aloud survives
CODE_PATTERN = r"^[A-HJ-NP-Z2-9]{8}$"
SHARE_TEXT = "I think you'd love this day — try it"   # prosocial wording (D114); the app adds the link


def new_code(s: Session) -> str:
    while True:
        code = "".join(secrets.choice(ALPHABET) for _ in range(8))
        if s.scalar(select(db.Referral).where(db.Referral.code == code)) is None:
            return code


def code_for(s: Session, user: db.User) -> str:
    """The person's share code, made the first time they share."""
    ref = s.get(db.Referral, user.id)
    if ref is None:
        ref = db.Referral(user_id=user.id, code=new_code(s))
        s.add(ref)
        s.commit()
    return ref.code


def page(code: str, known: bool, moment_title: str | None, moment_id: str | None, testflight_url: str | None) -> str:
    """The page a share link opens. Its script counts each opening; nothing about the reader is stored."""
    esc = html.escape
    title = f"<p class=\"moment\">{esc(moment_title)}</p>" if moment_title else ""
    deep = f"daysout://r/{code}" + (f"?m={esc(moment_id)}" if moment_id else "")
    if testflight_url:
        get = (f"<a class=\"button\" href=\"{esc(testflight_url)}\">Get Days out</a>"
               "<p class=\"small\">It installs through Apple's TestFlight, the app for testing new apps.</p>")
    else:
        get = ("<p>Days out is in a small closed test for now. Ask the person who sent you this how to join.</p>")
    # counted from the page's script, so link previews (which don't run scripts) don't count; nothing is stored on
    # the reader's device (no cookie, no local storage: PECR), so a reload counts again
    count = (f"<script>try{{fetch('/r/{code}/open',{{method:'POST',headers:{{'Content-Type':'application/json'}},"
             f"body:JSON.stringify({{m:{json.dumps(moment_id)}}})}});}}catch(e){{}}</script>") if known else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>A day out for you</title>
<style>
:root {{ --bg:#f6f2ea; --ink:#1d1b18; --soft:#5d574e; --accent:#c9822b; --card:#fffdf8; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#121417; --ink:#f1ece2; --soft:#aaa396; --accent:#e0a458; --card:#1c1f23; }} }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:17px/1.5 -apple-system,system-ui,sans-serif; }}
main {{ max-width:30rem; margin:0 auto; padding:32px 16px; }}
h1 {{ font:600 1.6rem/1.25 Georgia,serif; margin:0 0 12px; }}
.moment {{ font:600 1.2rem/1.3 Georgia,serif; background:var(--card); padding:14px 16px; border-radius:12px;
           border-left:4px solid var(--accent); }}
.button {{ display:block; text-align:center; background:var(--accent); color:#1d1b18; font-weight:600;
           text-decoration:none; padding:14px; border-radius:14px; margin:18px 0 6px; }}
.second {{ background:transparent; color:var(--ink); border:1px solid var(--soft); }}
.small {{ color:var(--soft); font-size:.9rem; }}
a {{ color:var(--accent); }}
</style></head><body><main>
<h1>A friend thinks you'd love this day</h1>
{title}
<p>Days out plans a London day around what you enjoy, not a list of famous sights. It's a small research test run
by one person in London. Nothing is sold.</p>
{get}
<a class="button second" href="{deep}">Already installed? Open Days out</a>
<p class="small">This page counts that it was opened. It stores nothing about you: no address, no device details,
nothing on your device.
<a href="/privacy">Privacy notice</a></p>
</main>{count}</body></html>"""


def record_open(s: Session, code: str, moment_id: str | None) -> bool:
    if s.scalar(select(db.Referral).where(db.Referral.code == code)) is None:
        return False
    s.add(db.LinkOpen(code=code, moment_id=(moment_id or None) and moment_id[:64]))
    s.commit()
    return True


def funnel(s: Session) -> dict:
    """Per code and in total: shared → opened → installed → onboarded → first plan, split by the sharer's channel
    (D43: K counts stranger participants' invitees; friends and family are reported separately)."""
    def n_events(user_id: str, name: str) -> int:
        return s.scalar(select(func.count()).select_from(db.Event)
                        .where(db.Event.user_id == user_id, db.Event.name == name)) or 0

    rows = []
    for ref in s.scalars(select(db.Referral).order_by(db.Referral.created_at)):
        sharer = s.get(db.User, ref.user_id)
        joined = list(s.scalars(select(db.User).where(db.User.src == f"ref:{ref.code}")))
        rows.append({
            "code": ref.code,
            "sharer_channel": sharer.channel if sharer else None,
            "share_sheets": n_events(ref.user_id, "share_sheet"),
            "shared": n_events(ref.user_id, "share_sent"),
            "opened": s.scalar(select(func.count()).select_from(db.LinkOpen).where(db.LinkOpen.code == ref.code)) or 0,
            "installed": len(joined),
            "onboarded": sum(n_events(u.id, "onboarding_done") > 0 for u in joined),
            "first_plan": sum((s.scalar(select(func.count()).select_from(db.Plan).where(db.Plan.user_id == u.id)) or 0)
                              > 0 for u in joined),
        })
    steps = ("share_sheets", "shared", "opened", "installed", "onboarded", "first_plan")
    by_channel = {}
    for ch in sorted({r["sharer_channel"] or "unknown" for r in rows}):
        sel = [r for r in rows if (r["sharer_channel"] or "unknown") == ch]
        by_channel[ch] = {"sharers": sum(r["shared"] > 0 for r in sel), **{k: sum(r[k] for r in sel) for k in steps}}
    return {"codes": rows, "by_channel": by_channel,
            "note": "K (Test C) = installs from stranger sharers ÷ stranger participants who did Test C (D43)"}
