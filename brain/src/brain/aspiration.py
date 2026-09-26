"""Aspiration match (D77): the fields that inspire a person, mapped onto moments.

One optional Test A question ("Which of these fields inspire you?") gives a set of fields. A moment
belongs to a field through an existing tag (e.g. food ≥ 2) or, for fields with no tag, by id
(data/aspiration.yaml). The model feature `aspiration_match` is 1 when a moment belongs to any of the
person's fields. It is an interaction between a person-level answer and a moment-level trait, so its
population weight is a prior (a GUESS, priors.yaml) and swipes can move each person's δ on it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from .moments import Moment

NONE = "none"


@dataclass(frozen=True)
class AspirationField:
    code: str
    label: str
    tags: dict[str, int]
    moments: frozenset[str]


@dataclass(frozen=True)
class AspirationMap:
    question: str
    note: str
    min_ready: int
    fields: dict[str, AspirationField]

    def fields_of(self, m: Moment) -> set[str]:
        out = set()
        for f in self.fields.values():
            if m.id in f.moments or any((m.tag(t) or 0) >= lvl for t, lvl in f.tags.items()):
                out.add(f.code)
        return out

    def match(self, m: Moment, person: frozenset[str] | set[str]) -> float:
        return 1.0 if person and self.fields_of(m) & set(person) else 0.0

    def parse(self, text: str | None) -> tuple[frozenset[str], list[str]]:
        """A cell like "food, nature" (codes or labels, any case) → (fields, unknown parts)."""
        if not text or not str(text).strip():
            return frozenset(), []
        by_name = {}
        for f in self.fields.values():
            by_name[f.code.lower()] = f.code
            by_name[f.label.lower()] = f.code
            by_name[f.label.lower().replace(" & ", " and ")] = f.code
        found, unknown = set(), []
        for part in re.split(r"[,;/|]", str(text)):
            p = part.strip().lower()
            if not p:
                continue
            if p in by_name:
                found.add(by_name[p])
            else:
                unknown.append(part.strip())
        found.discard(NONE)
        return frozenset(found), unknown

    def labels(self, codes) -> list[str]:
        return [self.fields[c].label for c in sorted(codes) if c in self.fields]

    def coverage(self, moments: list[Moment]) -> list[dict]:
        """Moments per field: checked (ready and plannable) vs draft. `flag` if fewer than min_ready are ready."""
        rows = []
        for f in self.fields.values():
            if f.code == NONE:
                continue
            members = [m for m in moments if f.code in self.fields_of(m)]
            ready = [m for m in members if m.status == "ready" and m.plannable()]
            groups = {m.variant_of or m.id for m in ready}
            rows.append({"field": f.code, "label": f.label, "ready": len(ready), "ready_groups": len(groups),
                         "drafts": len(members) - len(ready), "moments": [m.id for m in members],
                         "flag": len(ready) < self.min_ready})
        return rows


def load_aspiration(path: Path) -> AspirationMap:
    d = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    fields = {code: AspirationField(code, v["label"], {k: int(x) for k, x in (v.get("tags") or {}).items()},
                                    frozenset(v.get("moments") or []))
              for code, v in d["fields"].items()}
    if NONE not in fields:
        raise ValueError("aspiration.yaml needs a 'none' option")
    return AspirationMap(d["question"], d.get("note", ""), int(d.get("min_ready_moments", 2)), fields)
