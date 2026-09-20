from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import TYPE_CHECKING

from app.modules.control.models import EXCLUSIVE_KINDS, Control

if TYPE_CHECKING:
    from app.core.content import Corpus

OPEN_ENDED = date(9999, 12, 31)


def validate_control(c: Corpus) -> list[str]:
    problems: list[str] = []
    atom_ids = {a.id for a in c.atoms}
    polity_ids = {p.id for p in c.polities}

    # Referential integrity and well-formed periods.
    for i, row in enumerate(c.control):
        if row.atom not in atom_ids:
            problems.append(f"control[{i}]: unknown atom {row.atom!r}")
        if row.polity not in polity_ids:
            problems.append(f"control[{i}]: unknown polity {row.polity!r}")
        if row.end is not None and row.start >= row.end:
            problems.append(
                f"control[{i}] {row.atom}/{row.polity}: from {row.start} is not before to {row.end}"
            )

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
