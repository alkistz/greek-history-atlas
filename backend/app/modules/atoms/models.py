from pydantic import Field, model_validator

from app.core.models import LangText, Strict


class Part(Strict):
    """The polygon parts of one NUTS3 unit whose bounds fall inside `bbox` (w, s, e, n).
    How an island group is cut off a mainland unit without hand-drawn geometry."""

    nuts3: str
    bbox: tuple[float, float, float, float]


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
