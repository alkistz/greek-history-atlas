from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_sources(c: Corpus) -> list[str]:
    """A source has to be findable.

    A book is found by its title and, where given, its ISBN. A web page is found
    only by its URL, so one without a URL is not a citation, it is a rumour with
    a name attached.
    """
    problems: list[str] = []
    for s in c.sources:
        if s.kind == "web" and not s.url:
            problems.append(f"source {s.id!r}: a web source needs a url")
    return problems
