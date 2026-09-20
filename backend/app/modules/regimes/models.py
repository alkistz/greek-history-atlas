from datetime import date
from typing import Literal

from pydantic import Field

from app.core.models import LangText, Strict
from app.core.periods import covers as _covers

RegimeKind = Literal[
    "revolutionary",
    "absolute_monarchy",
    "constitutional_monarchy",
    "republic",
    "dictatorship",
    "occupation",
    "interregnum",
]


class Regime(Strict):
    """What kind of state Greece was, over a half-open period.

    `Control` answers who held which ground. This answers what the state holding it
    was, which is the axis the map cannot draw and the one the corpus needs after
    1947, when the borders stop moving and the events do not.

    The rows are an unbroken chain, so a date inside it resolves to exactly one
    regime. That is what lets an event's regime be derived from its date with
    nothing stored per event, the way a region is derived from an atom.
    """

    id: str
    kind: RegimeKind
    name: LangText
    polity: str
    start: date = Field(alias="from")
    end: date | None = Field(default=None, alias="to")
    summary: LangText | None = None

    def covers(self, on: date) -> bool:
        """Half-open [start, end): a transition date belongs to the new regime."""
        return _covers(self.start, self.end, on)
