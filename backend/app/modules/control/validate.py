from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from app.core.periods import find_overlaps
from app.core.refs import ids
from app.modules.control.models import EXCLUSIVE_KINDS, Control

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_control(c: Corpus) -> list[str]:
    problems: list[str] = []
    atom_ids = ids(c.atoms)
    polity_ids = ids(c.polities)
    instrument_ids = ids(c.instruments)

    # Referential integrity and well-formed periods.
    for i, row in enumerate(c.control):
        where = f"control[{i}] {row.atom}/{row.polity}"
        if row.atom not in atom_ids:
            problems.append(f"{where}: unknown atom {row.atom!r}")
        if row.polity not in polity_ids:
            problems.append(f"{where}: unknown polity {row.polity!r}")
        if row.instrument is not None and row.instrument not in instrument_ids:
            problems.append(f"{where}: unknown instrument {row.instrument!r}")
        if row.end is not None and row.start >= row.end:
            problems.append(f"{where}: from {row.start} is not before to {row.end}")

    # The load-bearing invariant: no two holders of the same atom at the same
    # moment, for sovereign and occupied only.
    groups: dict[tuple[str, str], list[Control]] = defaultdict(list)
    for row in c.control:
        if row.kind in EXCLUSIVE_KINDS:
            groups[(row.atom, row.kind)].append(row)

    for (atom, kind), rows in sorted(groups.items()):
        for a, b in find_overlaps(rows, lambda r: r.start, lambda r: r.end):
            problems.append(
                f"overlapping {kind!r} rows for atom {atom!r}: "
                f"{a.polity} [{a.start}..{a.end or 'open'}) and "
                f"{b.polity} [{b.start}..{b.end or 'open'}) "
                f"both hold it on {b.start}"
            )

    return problems
