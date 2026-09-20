from datetime import date
from typing import Literal

from pydantic import Field

from app.core.models import LangText, Strict

Precision = Literal["day", "month", "season", "year", "span", "circa"]


class AsWritten(Strict):
    """The date as a source gives it, when that is Old Style (Julian)."""

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
