from datetime import date
from typing import Literal

from pydantic import Field

from app.core.models import Citation, LangText, Review, Strict

InstrumentKind = Literal["treaty", "protocol", "convention", "armistice", "decree"]


class Instrument(Strict):
    """A treaty, protocol or similar act that moved a frontier."""

    id: str
    name: LangText
    kind: InstrumentKind
    signed: date
    parties: list[str] = Field(default_factory=list)  # polity ids
    summary: LangText | None = None
    # The instrument's own text. Not a citation: a treaty is not a work written
    # about itself, and its text is the most authoritative thing this atlas can
    # point at for the borders it draws.
    text_url: str | None = None
    sources: list[Citation] = Field(default_factory=list)
    review: Review | None = None
