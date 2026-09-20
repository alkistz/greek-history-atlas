from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_polities(c: Corpus) -> list[str]:
    """A polity that is drawn needs a colour; one that only signs treaties does not."""
    drawn = {row.polity for row in c.control}
    return [
        f"polity {p.id!r} holds territory but has no colour"
        for p in c.polities
        if p.id in drawn and p.colour is None
    ]
