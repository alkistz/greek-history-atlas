from typing import Literal

from pydantic import Field, model_validator

from app.core.models import LangText, Strict


class Cut(Strict):
    """A historical frontier that runs through a NUTS3 unit rather than along one.

    Either an OpenHistoricalMap relation (CC0), the boundary of a state on some date,
    which `scripts/fetch_geo.py` downloads; or, where that relation is too coarse, a
    polygon written out here, whose `note` must say where its line comes from.
    `scripts/build_atoms.py` splits the units that name a cut, so a cut is data rather
    than code.
    """

    id: str
    name: LangText
    # OpenHistoricalMap relation id: https://www.openhistoricalmap.org/relation/<ohm>
    ohm: int | None = None
    # (lon, lat) ring; one side of the frontier, loose wherever it is off the line.
    polygon: list[tuple[float, float]] | None = None
    note: str | None = None

    @model_validator(mode="after")
    def _one_source(self):
        if (self.ohm is None) == (self.polygon is None):
            raise ValueError("a cut needs exactly one of `ohm` or `polygon`")
        if self.polygon is not None and (len(self.polygon) < 4 or not self.note):
            raise ValueError("a polygon cut needs at least four points and a `note` on its source")
        return self


class Part(Strict):
    """Part of one NUTS3 unit, where an atom takes less than the whole of it.

    Either `bbox` (w, s, e, n): the polygon parts whose bounds fall inside it, which
    is how an island group is cut off a mainland unit. Or `cut` and `side`: the unit
    split along a historical frontier, taking what lies inside or outside it. Another
    atom listing the unit under `nuts3` gets whatever is left.
    """

    nuts3: str
    bbox: tuple[float, float, float, float] | None = None
    cut: str | None = None
    side: Literal["inside", "outside"] | None = None

    @model_validator(mode="after")
    def _one_way_to_cut(self):
        if (self.bbox is None) == (self.cut is None):
            raise ValueError("a part needs exactly one of `bbox` or `cut`")
        if (self.cut is None) != (self.side is None):
            raise ValueError("`side` goes with `cut`, and only with it")
        return self


class Atom(Strict):
    """An area whose sovereignty history is identical throughout the whole period."""

    id: str
    name: LangText
    nuts3: list[str] = Field(default_factory=list)
    parts: list[Part] = Field(default_factory=list)
    # Outside the modern Greek state. Excluded from area totals; drawn only while a
    # control row covers it.
    external: bool = False

    @model_validator(mode="after")
    def _has_geometry_source(self):
        if not self.nuts3 and not self.parts:
            raise ValueError("an atom needs `nuts3` units or `parts`")
        return self
