from datetime import date
from typing import Literal

from pydantic import Field

from app.core.models import LangText, Strict

PlaceKind = Literal["city", "town", "village", "battlefield", "island", "region", "building", "sea"]


class PlaceName(Strict):
    """A name in force over a half-open period. Both ends optional."""

    name: LangText
    start: date | None = Field(default=None, alias="from")
    end: date | None = Field(default=None, alias="to")


class Place(Strict):
    """A point on the map. Names change; the point does not."""

    id: str
    kind: PlaceKind
    lon: float
    lat: float
    atom: str | None = None
    names: list[PlaceName] = Field(min_length=1)
