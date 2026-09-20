"""Load and validate the corpus.

Everything lives in memory: the whole corpus is a few hundred kilobytes.

Validation runs at load time and raises. The app refuses to boot on bad content,
which is where the "no CI in v0" decision gets paid for: the invariants that a
PostGIS EXCLUDE constraint would have enforced are enforced here instead.

This file only orchestrates. Each module owns its own models and its own
validation rules; the cross-module wiring (which files, in what order, what is
generic) is the only thing that lives here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from app.core.exceptions import ContentError
from app.core.paths import ATOMS_GEOJSON, ATOMS_YAML, CONTROL_YAML, EVENTS_YAML, POLITIES_YAML
from app.modules.atoms.models import Atom
from app.modules.control.models import Control
from app.modules.events.models import Event
from app.modules.polities.models import Polity


@dataclass(frozen=True)
class Corpus:
    atoms: list[Atom]
    polities: list[Polity]
    control: list[Control]
    events: list[Event]
    geojson: dict[str, Any]


def load_yaml(path: Path, model: type, problems: list[str]) -> list:
    """Parse a YAML list into `model` instances, collecting rather than raising."""
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


def validate(c: Corpus) -> list[str]:
    """Every problem in the corpus. Empty means valid."""
    # Imported here rather than at the top: modules import Corpus for typing,
    # and this keeps the dependency pointing one way at import time.
    from app.modules.atoms.validate import validate_atoms
    from app.modules.control.validate import validate_control
    from app.modules.events.validate import validate_events

    problems: list[str] = []

    # Generic: ids are unique within each collection.
    for label, items in (("atom", c.atoms), ("polity", c.polities), ("event", c.events)):
        seen: set[str] = set()
        for it in items:
            if it.id in seen:
                problems.append(f"duplicate {label} id {it.id!r}")
            seen.add(it.id)

    problems += validate_atoms(c)
    problems += validate_control(c)
    problems += validate_events(c)
    return problems


def load() -> Corpus:
    problems: list[str] = []

    atoms = load_yaml(ATOMS_YAML, Atom, problems)
    polities = load_yaml(POLITIES_YAML, Polity, problems)
    control = load_yaml(CONTROL_YAML, Control, problems)
    events = load_yaml(EVENTS_YAML, Event, problems)

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

    problems = validate(corpus)
    if problems:
        raise ContentError(problems)

    return corpus
