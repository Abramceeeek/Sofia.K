"""Who may fetch the nightly backup: the repository's own GitHub Actions job, proved by GitHub's signed identity
token (OIDC), so no shared secret has to be put into Render or GitHub (Abram asked Claude to set the backups up
itself, 19 Oct, and this session can't write either).

- GitHub signs the token with RS256; the keys are at `ISSUER/.well-known/jwks` (its openid-configuration, read
  19 Oct 2026). The claims checked: `iss`, `aud` (our own word, `AUDIENCE`), `exp`/`nbf`, `repository`, `ref` and
  `workflow_ref` (only `.github/workflows/ops.yml` on `main`; docs.github.com, OIDC reference, read 19 Oct 2026).
- The backup is sealed to Abram's public key anyway (backup.py), so this guards against load and curiosity, not
  against reading it.
"""

from __future__ import annotations

import base64
import json
import logging
import threading
import time
from typing import Callable

log = logging.getLogger("brain.oidc")

ISSUER = "https://token.actions.githubusercontent.com"
JWKS_URL = ISSUER + "/.well-known/jwks"
AUDIENCE = "odys-brain-backup"
REPOSITORY = "Abramceeeek/Sofia.K"
WORKFLOW_REF = f"{REPOSITORY}/.github/workflows/ops.yml@refs/heads/main"
KEYS_TTL_S = 3600
LEEWAY_S = 60


def _b64(part: str) -> bytes:
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


def _http_json(url: str) -> dict:
    import httpx
    r = httpx.get(url, timeout=10.0)
    r.raise_for_status()
    return r.json()


class GithubOIDC:
    def __init__(self, fetch: Callable[[str], dict] | None = None, clock: Callable[[], float] = time.time,
                 repository: str = REPOSITORY, workflow_ref: str = WORKFLOW_REF, audience: str = AUDIENCE):
        self.fetch = fetch or _http_json
        self.clock = clock
        self.repository, self.workflow_ref, self.audience = repository, workflow_ref, audience
        self._keys: dict[str, object] = {}
        self._fetched = -1e18
        self._lock = threading.Lock()

    def _key(self, kid: str):
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
        now = self.clock()
        with self._lock:
            if kid not in self._keys and now - self._fetched > 300 or now - self._fetched > KEYS_TTL_S:
                try:
                    keys = {}
                    for k in self.fetch(JWKS_URL).get("keys", []):
                        if k.get("kty") == "RSA" and k.get("kid"):
                            n, e = (int.from_bytes(_b64(k[x]), "big") for x in ("n", "e"))
                            keys[k["kid"]] = RSAPublicNumbers(e, n).public_key()
                    self._keys, self._fetched = keys, now
                except Exception as ex:  # noqa: BLE001 - no keys means no backup tonight, never a crash
                    log.warning("GitHub's OIDC keys couldn't be fetched: %s", type(ex).__name__)
            return self._keys.get(kid)

    def verify(self, token: str) -> dict | None:
        """The token's claims if it's a genuine, current token from our ops workflow on main; else None."""
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        try:
            h, p, sig = token.split(".")
            header, claims = json.loads(_b64(h)), json.loads(_b64(p))
        except (ValueError, json.JSONDecodeError):
            return None
        if header.get("alg") != "RS256" or not (key := self._key(str(header.get("kid", "")))):
            return None
        try:
            key.verify(_b64(sig), f"{h}.{p}".encode(), padding.PKCS1v15(), hashes.SHA256())
        except (InvalidSignature, ValueError):
            return None
        now = self.clock()
        aud = claims.get("aud")
        ok = (claims.get("iss") == ISSUER
              and (aud == self.audience or (isinstance(aud, list) and self.audience in aud))
              and isinstance(claims.get("exp"), (int, float)) and claims["exp"] > now - LEEWAY_S
              and claims.get("nbf", 0) <= now + LEEWAY_S
              and claims.get("repository") == self.repository
              and claims.get("ref") == "refs/heads/main"
              and claims.get("workflow_ref") == self.workflow_ref)
        return claims if ok else None
