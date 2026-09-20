from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.refs import check_citations, ids
from app.core.review import check_review, langs_present

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_figures(c: Corpus) -> list[str]:
    problems: list[str] = []
    place_ids = ids(c.places)

    for fig in c.figures:
        where = f"figure {fig.id!r}"
        for label, life in (("born", fig.born), ("died", fig.died)):
            if life is not None and life.place is not None and life.place not in place_ids:
                problems.append(f"{where}: unknown {label} place {life.place!r}")
        if fig.born is not None and fig.died is not None and fig.born.date >= fig.died.date:
            problems.append(f"{where}: born {fig.born.date} is not before died {fig.died.date}")
        problems += check_citations(c, fig.sources, where)
        problems += check_review(fig.review, langs_present(fig.summary, fig.body), where)

    return problems


def lifetime_warnings(c: Corpus) -> list[str]:
    """Events a figure is linked to but could not have attended. Reported, not fatal:
    a posthumous link (a treaty that bears someone's name) can be deliberate."""
    figures = {f.id: f for f in c.figures}
    out = []
    for e in c.events:
        for p in e.figures:
            fig = figures.get(p.figure)
            if fig is None:
                continue
            if fig.born is not None and e.period[1] <= fig.born.date:
                out.append(f"event {e.id!r} predates the birth of {fig.id!r}")
            if fig.died is not None and e.period[0] > fig.died.date:
                out.append(f"event {e.id!r} postdates the death of {fig.id!r}")
    return out
