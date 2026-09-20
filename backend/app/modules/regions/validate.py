from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from app.core.refs import ids

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_regions(c: Corpus) -> list[str]:
    """Regions must partition the atoms: every atom in exactly one region.

    Without the partition an atom added to atoms.yaml and forgotten here would
    silently hold events that no region filter could ever reach. This turns that
    into a boot failure.
    """
    problems: list[str] = []
    atom_ids = ids(c.atoms)
    owners: dict[str, list[str]] = defaultdict(list)

    for region in c.regions:
        where = f"region {region.id!r}"
        for atom in region.atoms:
            if atom not in atom_ids:
                problems.append(f"{where}: unknown atom {atom!r}")
            else:
                owners[atom].append(region.id)

    for atom in sorted(atom_ids - set(owners)):
        problems.append(f"atom {atom!r} belongs to no region")
    for atom, names in sorted(owners.items()):
        if len(names) > 1:
            problems.append(f"atom {atom!r} belongs to more than one region: {', '.join(names)}")
    return problems
