from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from app.core.refs import ids

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_relations(c: Corpus) -> list[str]:
    """Both ends must be real figures, a figure cannot be tied to itself, and a
    pair appears once: the inverse is derived, so writing it from both ends is
    either a duplicate or, worse, two kinds that disagree.

    A parent must be born before the child where both dates are known. It is the
    one kind with an arithmetic check, and it catches a row written backwards.
    """
    problems: list[str] = []
    figure_ids = ids(c.figures)
    born = {f.id: f.born.date for f in c.figures if f.born is not None}

    for i, r in enumerate(c.relations):
        where = f"relation [{i}] {r.source!r} -> {r.target!r}"
        for end in (r.source, r.target):
            if end not in figure_ids:
                problems.append(f"{where}: unknown figure {end!r}")
        if r.source == r.target:
            problems.append(f"{where}: a figure cannot be tied to itself")
        parent, child = {
            "parent": (r.source, r.target),
            "child": (r.target, r.source),
        }.get(r.kind, (None, None))
        if parent in born and child in born and born[parent] >= born[child]:
            problems.append(f"{where}: parent {parent!r} is not born before child {child!r}")

    for pair, n in sorted(Counter(r.pair() for r in c.relations).items()):
        if n > 1:
            problems.append(f"relation {pair[0]!r} -- {pair[1]!r} written {n} times; write it once")
    return problems
