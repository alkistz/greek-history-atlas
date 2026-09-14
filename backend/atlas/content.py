"""Load and validate the corpus.

Everything lives in memory: the whole corpus is a few hundred kilobytes.

Validation runs at load time and raises. The app refuses to boot on bad content,
which is where the "no CI in v0" decision gets paid for: the invariants that a
PostGIS EXCLUDE constraint would have enforced are enforced here instead.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any

import yaml
from pydantic import ValidationError

from atlas.models import EXCLUSIVE_KINDS, Atom, Control, Event, Polity
from atlas.paths import (
    ATOMS_GEOJSON,
    ATOMS_YAML,
    CONTROL_YAML,
    EVENTS_YAML,
    POLITIES_YAML,
)

OPEN_ENDED = date(9999, 12, 31)


class ContentError(Exception):
    """Raised with every problem found, not just the first."""

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        body = "\n".join(f"  - {p}" for p in problems)
        super().__init__(f"{len(problems)} problem(s) in content/:\n{body}")


def _load_yaml(path, model, problems: list[str]) -> list:
    raw = yaml.safe_load(path.read_text())
    if raw is None:
        problems.append(f"{path.name}: file is empty")
        return []
    out = []
    for i, item in enumerate(raw):
        try:
            out.append(model(**item))
        except ValidationError as e:
            for err in e.errors():
                loc = ".".join(str(x) for x in err["loc"])
                problems.append(f"{path.name}[{i}] {loc}: {err['msg']}")
    return out


@dataclass(frozen=True)
class Corpus:
    atoms: list[Atom]
    polities: list[Polity]
    control: list[Control]
    events: list[Event]
    geojson: dict[str, Any]

    @property
    def epochs(self) -> list[date]:
        """Every date on which any control row starts or ends.

        This is the complete set of dates on which the map changes: between two
        consecutive epochs the picture is identical.
        """
        ds: set[date] = set()
        for c in self.control:
            ds.add(c.start)
            if c.end is not None:
                ds.add(c.end)
        return sorted(ds)

    def control_on(self, on: date) -> list[Control]:
        return [c for c in self.control if c.covers(on)]


def _validate(c: Corpus) -> list[str]:
    problems: list[str] = []

    atom_ids = {a.id for a in c.atoms}
    polity_ids = {p.id for p in c.polities}

    for label, items in (
        ("atom", c.atoms),
        ("polity", c.polities),
        ("event", c.events),
    ):
        seen: set[str] = set()
        for it in items:
            if it.id in seen:
                problems.append(f"duplicate {label} id {it.id!r}")
            seen.add(it.id)

    # Referential integrity.
    for i, row in enumerate(c.control):
        if row.atom not in atom_ids:
            problems.append(f"control[{i}]: unknown atom {row.atom!r}")
        if row.polity not in polity_ids:
            problems.append(f"control[{i}]: unknown polity {row.polity!r}")
        if row.end is not None and row.start >= row.end:
            problems.append(
                f"control[{i}] {row.atom}/{row.polity}: from {row.start} is not before to {row.end}"
            )
    for e in c.events:
        if e.atom is not None and e.atom not in atom_ids:
            problems.append(f"event {e.id!r}: unknown atom {e.atom!r}")
        if e.period[0] >= e.period[1]:
            problems.append(f"event {e.id!r}: period start is not before end")

    # Geometry: every atom must have a polygon, and nothing may be orphaned.
    geo_ids = {f["properties"]["id"] for f in c.geojson["features"]}
    for missing in sorted(atom_ids - geo_ids):
        problems.append(f"atom {missing!r} has no geometry in atoms.geojson")
    for orphan in sorted(geo_ids - atom_ids):
        problems.append(f"atoms.geojson has geometry {orphan!r} with no atom")

    # The load-bearing invariant: no two holders of the same atom at the same
    # moment, for sovereign and occupied only.
    groups: dict[tuple[str, str], list[Control]] = defaultdict(list)
    for row in c.control:
        if row.kind in EXCLUSIVE_KINDS:
            groups[(row.atom, row.kind)].append(row)

    for (atom, kind), rows in sorted(groups.items()):
        rows.sort(key=lambda r: r.start)
        for a, b in zip(rows, rows[1:], strict=False):
            if (a.end or OPEN_ENDED) > b.start:
                problems.append(
                    f"overlapping {kind!r} rows for atom {atom!r}: "
                    f"{a.polity} [{a.start}..{a.end or 'open'}) and "
                    f"{b.polity} [{b.start}..{b.end or 'open'}) "
                    f"both hold it on {b.start}"
                )

    return problems


def load() -> Corpus:
    problems: list[str] = []

    atoms = _load_yaml(ATOMS_YAML, Atom, problems)
    polities = _load_yaml(POLITIES_YAML, Polity, problems)
    control = _load_yaml(CONTROL_YAML, Control, problems)
    events = _load_yaml(EVENTS_YAML, Event, problems)

    if not ATOMS_GEOJSON.exists():
        raise ContentError([f"missing {ATOMS_GEOJSON}. Run `make fetch && make atoms`."])
    geojson = json.loads(ATOMS_GEOJSON.read_text())

    corpus = Corpus(
        atoms=atoms,
        polities=polities,
        control=control,
        events=events,
        geojson=geojson,
    )

    if problems:
        raise ContentError(problems)

    problems = _validate(corpus)
    if problems:
        raise ContentError(problems)

    return corpus
