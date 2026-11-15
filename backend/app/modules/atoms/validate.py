from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_atoms(c: Corpus) -> list[str]:
    """Every atom must have a polygon, no polygon may be orphaned, and every cut a part
    names must exist and be used."""
    problems: list[str] = []
    atom_ids = {a.id for a in c.atoms}
    geo_ids = {f["properties"]["id"] for f in c.geojson["features"]}
    for missing in sorted(atom_ids - geo_ids):
        problems.append(f"atom {missing!r} has no geometry in atoms.geojson")
    for orphan in sorted(geo_ids - atom_ids):
        problems.append(f"atoms.geojson has geometry {orphan!r} with no atom")
    if not any(f.get("id") == "land" for f in c.context.get("features", [])):
        problems.append("context.geojson has no `land` feature")

    cut_ids = [cut.id for cut in c.cuts]
    for dup in sorted({i for i in cut_ids if cut_ids.count(i) > 1}):
        problems.append(f"duplicate cut id {dup!r}")
    used = {p.cut for a in c.atoms for p in a.parts if p.cut}
    for a in c.atoms:
        for p in a.parts:
            if p.cut and p.cut not in cut_ids:
                problems.append(f"atom {a.id!r}: unknown cut {p.cut!r}")
    for unused in sorted(set(cut_ids) - used):
        problems.append(f"cut {unused!r} is used by no atom")
    return problems
