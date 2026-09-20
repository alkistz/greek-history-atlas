from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_atoms(c: Corpus) -> list[str]:
    """Every atom must have a polygon, and no polygon may be orphaned."""
    problems: list[str] = []
    atom_ids = {a.id for a in c.atoms}
    geo_ids = {f["properties"]["id"] for f in c.geojson["features"]}
    for missing in sorted(atom_ids - geo_ids):
        problems.append(f"atom {missing!r} has no geometry in atoms.geojson")
    for orphan in sorted(geo_ids - atom_ids):
        problems.append(f"atoms.geojson has geometry {orphan!r} with no atom")
    return problems
