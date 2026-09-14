"""Content schemas.

These are the ingest models and the API response models at the same time. At v0
there is no reason for two layers: nothing is stored, so nothing can drift.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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

PolityKind = Literal["state", "empire", "protectorate", "occupation", "autonomous", "de_facto"]

Precision = Literal["day", "month", "season", "year", "span", "circa"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class LangText(Strict):
    """English is required; Greek follows as it is written."""

    en: str
    el: str | None = None


class Atom(Strict):
    id: str
    name: LangText
    nuts3: list[str] = Field(default_factory=list)


class Polity(Strict):
    id: str
    name: LangText
    kind: PolityKind
    colour: str


class Control(Strict):
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


class AsWritten(Strict):
    date: date
    calendar: Literal["julian", "gregorian"] = "julian"


class Event(Strict):
    id: str
    title: LangText
    summary: LangText
    period: tuple[date, date]
    precision: Precision
    atom: str | None = None
    significance: int = Field(ge=1, le=5)
    as_written: AsWritten | None = None

    @property
    def start(self) -> date:
        return self.period[0]
