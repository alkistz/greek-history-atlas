from datetime import date
from typing import Literal

from pydantic import Field

from app.core.models import Citation, LangText, Strict

InstrumentKind = Literal["treaty", "protocol", "convention", "armistice", "decree"]


class Instrument(Strict):
    """A treaty, protocol or similar act that moved a frontier."""

    id: str
    name: LangText
    kind: InstrumentKind
    signed: date
    parties: list[str] = Field(default_factory=list)  # polity ids
    summary: LangText | None = None
    sources: list[Citation] = Field(default_factory=list)
