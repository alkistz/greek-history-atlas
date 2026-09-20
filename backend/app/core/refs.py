"""Referential-integrity helpers shared by the module validators."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from app.core.models import Citation

if TYPE_CHECKING:
    from app.core.content import Corpus


def ids(items: Iterable) -> set[str]:
    return {it.id for it in items}


def check_citations(c: Corpus, citations: list[Citation], owner: str) -> list[str]:
    known = ids(c.sources)
    return [f"{owner}: unknown source {cit.id!r}" for cit in citations if cit.id not in known]
