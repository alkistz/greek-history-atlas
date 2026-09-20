from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_events(c: Corpus) -> list[str]:
    problems: list[str] = []
    atom_ids = {a.id for a in c.atoms}
    for e in c.events:
        if e.atom is not None and e.atom not in atom_ids:
            problems.append(f"event {e.id!r}: unknown atom {e.atom!r}")
        if e.period[0] >= e.period[1]:
            problems.append(f"event {e.id!r}: period start is not before end")
    return problems
