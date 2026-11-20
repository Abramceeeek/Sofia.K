"""A4 (Abram, 20 Nov): the nightly backup reports the database's size, for a warning long before it is full."""
from dataclasses import replace

from brain import backup, db

from test_api import ADMIN, client, install  # noqa: F401 - the frozen suite's app fixture


def test_the_backup_reports_the_database_size_and_nothing_else_new(client):
    public, _ = backup.keygen()
    install(client)
    client.app.state.settings = replace(client.app.state.settings, backup_key=public)
    r = client.get("/v1/admin/backup", headers=ADMIN)
    assert r.status_code == 200 and r.content.startswith(backup.MAGIC)
    size = r.headers["X-Database-Bytes"]
    assert size.isdigit() and int(size) > 0


def test_the_size_is_a_number_or_nothing():
    assert backup.database_bytes(db.make_engine("sqlite://")) >= 0

    class Broken:
        dialect = type("D", (), {"name": "postgresql"})()

        def connect(self):
            raise OSError("down")
    assert backup.database_bytes(Broken()) is None


def test_the_route_still_needs_its_token(client):
    public, _ = backup.keygen()
    client.app.state.settings = replace(client.app.state.settings, backup_key=public)
    r = client.get("/v1/admin/backup", headers={"Authorization": "Bearer wrong"})
    assert r.status_code == 403 and "X-Database-Bytes" not in r.headers
