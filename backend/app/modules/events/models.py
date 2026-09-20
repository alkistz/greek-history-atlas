from datetime import date
from functools import cached_property
from typing import Literal

from pydantic import Field, computed_field

from app.core.markdown import render_lang_text
from app.core.models import Citation, FrameId, LangText, Precision, Strict

ParticipationRole = Literal[
    "leader", "commander", "signatory", "victim", "witness", "author", "participant"
]


class AsWritten(Strict):
    """The date as a source gives it, when that is Old Style (Julian)."""

    date: date
    calendar: Literal["julian", "gregorian"] = "julian"


class Participation(Strict):
    figure: str
    role: ParticipationRole = "participant"


class Event(Strict):
    id: str
    title: LangText
    summary: LangText
    period: tuple[date, date]
    precision: Precision
    atom: str | None = None
    place: str | None = None
    instrument: str | None = None
    frame: FrameId = "greece"
    significance: int = Field(ge=1, le=5)
    as_written: AsWritten | None = None
    body: LangText | None = None
    figures: list[Participation] = Field(default_factory=list)
    sources: list[Citation] = Field(default_factory=list)

    @property
    def start(self) -> date:
        return self.period[0]

    @computed_field
    @cached_property
    def body_html(self) -> LangText | None:
        return render_lang_text(self.body)
