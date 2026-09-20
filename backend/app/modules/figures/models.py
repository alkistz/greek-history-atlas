from datetime import date
from functools import cached_property
from typing import Literal

from pydantic import Field, computed_field

from app.core.markdown import render_lang_text
from app.core.models import Citation, LangText, Precision, Review, Strict
from app.modules.events.models import AsWritten

FigureRole = Literal[
    "monarch",
    "statesman",
    "military",
    "revolutionary",
    "diplomat",
    "writer",
    "cleric",
    "athlete",
    "benefactor",
]


class LifeEvent(Strict):
    """A birth or a death: a date, how sure we are of it, and optionally where."""

    date: date
    precision: Precision = "day"
    place: str | None = None
    # The same affordance events have. Most nineteenth-century Greek lives are
    # dated Old Style in the sources, and without somewhere to put that date the
    # only safe precision is `year` even where the day is documented -- which is
    # why several figures here are less precise than their sources are.
    as_written: AsWritten | None = None


class Figure(Strict):
    id: str
    name: LangText
    also_known_as: list[LangText] = Field(default_factory=list)
    born: LifeEvent | None = None
    died: LifeEvent | None = None
    roles: list[FigureRole] = Field(min_length=1)
    summary: LangText
    body: LangText | None = None
    sources: list[Citation] = Field(default_factory=list)
    review: Review | None = None

    @computed_field
    @cached_property
    def body_html(self) -> LangText | None:
        return render_lang_text(self.body)
