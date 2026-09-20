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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from app.core.exceptions import ContentError
from app.core.paths import (
    ATOMS_GEOJSON,
    ATOMS_YAML,
    CONTEXT_GEOJSON,
    CONTROL_YAML,
    EVENTS_DIR,
    FIGURES_DIR,
    INSTRUMENTS_YAML,
    PLACES_YAML,
    POLITIES_YAML,
    REGIMES_YAML,
    REGIONS_YAML,
    SOURCES_YAML,
)
from app.modules.atoms.models import Atom
from app.modules.control.models import Control
from app.modules.events.models import Event
from app.modules.figures.models import Figure
from app.modules.instruments.models import Instrument
from app.modules.places.models import Place
from app.modules.polities.models import Polity
from app.modules.regimes.models import Regime
from app.modules.regions.models import Region
from app.modules.sources.models import Source


@dataclass(frozen=True)
class Corpus:
    atoms: list[Atom] = field(default_factory=list)
    polities: list[Polity] = field(default_factory=list)
    control: list[Control] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    figures: list[Figure] = field(default_factory=list)
    instruments: list[Instrument] = field(default_factory=list)
    places: list[Place] = field(default_factory=list)
    regimes: list[Regime] = field(default_factory=list)
    regions: list[Region] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    geojson: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)


def _parse(item: Any, model: type, where: str, problems: list[str]) -> Any | None:
    try:
        return model(**item)
    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"])
            problems.append(f"{where} {loc}: {err['msg']}")
    except TypeError:
        problems.append(f"{where}: expected a mapping, got {type(item).__name__}")
    return None


def load_yaml(path: Path, model: type, problems: list[str]) -> list:
    """Parse a YAML list into `model` instances, collecting rather than raising."""
    raw = yaml.safe_load(path.read_text())
    if raw is None:
        problems.append(f"{path.name}: file is empty")
        return []
    out = []
    for i, item in enumerate(raw):
        parsed = _parse(item, model, f"{path.name}[{i}]", problems)
        if parsed is not None:
            out.append(parsed)
    return out


def load_dir(directory: Path, model: type, problems: list[str]) -> list:
    """One YAML document per file. The file stem must equal the entry's id."""
    if not directory.is_dir():
        problems.append(f"missing directory {directory}")
        return []
    out = []
    for path in sorted(directory.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        if raw is None:
            problems.append(f"{path.name}: file is empty")
            continue
        parsed = _parse(raw, model, f"{directory.name}/{path.name}", problems)
        if parsed is None:
            continue
        if parsed.id != path.stem:
            problems.append(f"{directory.name}/{path.name}: id {parsed.id!r} does not match file")
        out.append(parsed)
    return out


def validate(c: Corpus) -> list[str]:
    """Every problem in the corpus. Empty means valid."""
    # Imported here rather than at the top: modules import Corpus for typing,
    # and this keeps the dependency pointing one way at import time.
    from app.modules.atoms.validate import validate_atoms
    from app.modules.control.validate import validate_control
    from app.modules.events.validate import validate_events
    from app.modules.figures.validate import validate_figures
    from app.modules.instruments.validate import validate_instruments
    from app.modules.places.validate import validate_places
    from app.modules.polities.validate import validate_polities
    from app.modules.regimes.validate import validate_regimes
    from app.modules.regions.validate import validate_regions

    problems: list[str] = []

    # Generic: ids are unique within each collection.
    collections = (
        ("atom", c.atoms),
        ("polity", c.polities),
        ("event", c.events),
        ("figure", c.figures),
        ("instrument", c.instruments),
        ("place", c.places),
        ("regime", c.regimes),
        ("region", c.regions),
        ("source", c.sources),
    )
    for label, items in collections:
        seen: set[str] = set()
        for it in items:
            if it.id in seen:
                problems.append(f"duplicate {label} id {it.id!r}")
            seen.add(it.id)

    problems += validate_atoms(c)
    problems += validate_polities(c)
    problems += validate_control(c)
    problems += validate_instruments(c)
    problems += validate_places(c)
    problems += validate_regimes(c)
    problems += validate_regions(c)
    problems += validate_figures(c)
    problems += validate_events(c)
    return problems


def load() -> Corpus:
    problems: list[str] = []

    atoms = load_yaml(ATOMS_YAML, Atom, problems)
    polities = load_yaml(POLITIES_YAML, Polity, problems)
    control = load_yaml(CONTROL_YAML, Control, problems)
    instruments = load_yaml(INSTRUMENTS_YAML, Instrument, problems)
    places = load_yaml(PLACES_YAML, Place, problems)
    regimes = load_yaml(REGIMES_YAML, Regime, problems)
    regions = load_yaml(REGIONS_YAML, Region, problems)
    sources = load_yaml(SOURCES_YAML, Source, problems)
    events = load_dir(EVENTS_DIR, Event, problems)
    figures = load_dir(FIGURES_DIR, Figure, problems)

    for built in (ATOMS_GEOJSON, CONTEXT_GEOJSON):
        if not built.exists():
            raise ContentError([f"missing {built}. Run `make fetch && make atoms`."])
    geojson = json.loads(ATOMS_GEOJSON.read_text())
    context = json.loads(CONTEXT_GEOJSON.read_text())

    corpus = Corpus(
        atoms=atoms,
        polities=polities,
        control=control,
        events=events,
        figures=figures,
        instruments=instruments,
        places=places,
        regimes=regimes,
        regions=regions,
        sources=sources,
        geojson=geojson,
        context=context,
    )

    if problems:
        raise ContentError(problems)

    problems = validate(corpus)
    if problems:
        raise ContentError(problems)

    return corpus
