from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.refs import check_citations, ids
from app.core.review import check_review, langs_present

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_instruments(c: Corpus) -> list[str]:
    problems: list[str] = []
    polity_ids = ids(c.polities)
    for inst in c.instruments:
        for party in inst.parties:
            if party not in polity_ids:
                problems.append(f"instrument {inst.id!r}: unknown party {party!r}")
        where = f"instrument {inst.id!r}"
        problems += check_citations(c, inst.sources, where)
        problems += check_review(inst.review, langs_present(inst.name, inst.summary), where)
    return problems
