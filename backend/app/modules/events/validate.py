from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.refs import check_citations, ids

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_events(c: Corpus) -> list[str]:
    problems: list[str] = []
    atom_ids = ids(c.atoms)
    place_ids = ids(c.places)
    figure_ids = ids(c.figures)
    instrument_ids = ids(c.instruments)

    for e in c.events:
        where = f"event {e.id!r}"
        if e.atom is not None and e.atom not in atom_ids:
            problems.append(f"{where}: unknown atom {e.atom!r}")
        if e.place is not None and e.place not in place_ids:
            problems.append(f"{where}: unknown place {e.place!r}")
        if e.instrument is not None and e.instrument not in instrument_ids:
            problems.append(f"{where}: unknown instrument {e.instrument!r}")
        if e.period[0] >= e.period[1]:
            problems.append(f"{where}: period start is not before end")
        seen: set[str] = set()
        for p in e.figures:
            if p.figure not in figure_ids:
                problems.append(f"{where}: unknown figure {p.figure!r}")
            if p.figure in seen:
                problems.append(f"{where}: figure {p.figure!r} listed twice")
            seen.add(p.figure)
        problems += check_citations(c, e.sources, where)
    return problems
