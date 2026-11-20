"""A1 and A3 (Abram, 20 Nov §2) on the development code: the alert says only that a message is waiting, and the log
never holds a safety message, who sent it, or a failed write's values."""
import json
import logging

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from brain import db, notify

from test_api import client, install  # noqa: F401 - the app fixture


class _Resp:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_the_webhook_gets_exactly_the_words_abram_set(monkeypatch):
    sent = []
    monkeypatch.setattr(notify.urllib.request, "urlopen", lambda req, timeout: sent.append(req.data) or _Resp())
    assert notify.send_alert("https://hooks.example.invalid/x", 42)
    assert json.loads(sent[0]) == {"text": "Safety message #42 is waiting"}


def test_a_safety_message_sent_through_the_app_stays_out_of_the_log(client, caplog):
    h, uid = install(client)
    with caplog.at_level(logging.INFO, logger="brain"):
        r = client.post("/v1/me/safety", headers=h, json={"message": "PRIVATE lost near the river", "contact": "07700 900123"})
    assert r.status_code == 201
    assert "PRIVATE" not in caplog.text and uid not in caplog.text and "07700" not in caplog.text


def test_a_failed_write_never_shows_its_values():
    engine = db.make_engine("sqlite://")
    with engine.begin() as c:
        c.execute(text("create table t (k text primary key)"))
        c.execute(text("insert into t values (:k)"), {"k": "PRIVATE-VALUE"})
    with pytest.raises(IntegrityError) as e, engine.begin() as c:
        c.execute(text("insert into t values (:k)"), {"k": "PRIVATE-VALUE"})
    assert "PRIVATE-VALUE" not in str(e.value)
