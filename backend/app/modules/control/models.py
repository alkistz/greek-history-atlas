from datetime import date
from typing import Literal

from pydantic import Field

from app.core.models import Strict

ControlKind = Literal[
    "sovereign",
    "occupied",
    "administered",
    "autonomous",
    "insurgent",
    "disputed",
    "claimed",
]

# Kinds where two simultaneous holders of one atom is a modelling error rather
# than history. `disputed` and `claimed` are deliberately excluded: overlapping
# claims by rival states are the whole point of those kinds.
EXCLUSIVE_KINDS: frozenset[str] = frozenset({"sovereign", "occupied"})


class Control(Strict):
    """Who held which atom, in what capacity, over a half-open period."""

    atom: str
    polity: str
    kind: ControlKind
    start: date = Field(alias="from")
    end: date | None = Field(default=None, alias="to")
    instrument: str | None = None
    note: str | None = None

    def covers(self, on: date) -> bool:
        """Half-open [start, end): a transfer date belongs to the new holder."""
        return self.start <= on and (self.end is None or on < self.end)
