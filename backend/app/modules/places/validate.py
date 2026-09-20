from __future__ import annotations

from typing import TYPE_CHECKING

from shapely.geometry import Point, shape

from app.core.periods import find_overlaps
from app.core.refs import ids

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_places(c: Corpus) -> list[str]:
    problems: list[str] = []
    atom_ids = ids(c.atoms)
    geometry = {f["properties"]["id"]: f["geometry"] for f in c.geojson.get("features", [])}

    for place in c.places:
        where = f"place {place.id!r}"
        for n in place.names:
            if n.start is not None and n.end is not None and n.start >= n.end:
                problems.append(f"{where}: name period from {n.start} is not before to {n.end}")
        for a, b in find_overlaps(place.names, lambda n: n.start, lambda n: n.end):
            problems.append(f"{where}: names {a.name.en!r} and {b.name.en!r} overlap in time")

        if place.atom is None:
            continue
        if place.atom not in atom_ids:
            problems.append(f"{where}: unknown atom {place.atom!r}")
        elif place.atom in geometry:
            polygon = shape(geometry[place.atom])
            if not polygon.buffer(0.02).contains(Point(place.lon, place.lat)):
                problems.append(f"{where}: point is not inside atom {place.atom!r}")
    return problems
