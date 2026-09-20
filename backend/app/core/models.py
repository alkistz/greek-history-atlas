"""Base classes and value types shared by every module's models."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    """Content models reject unknown keys: a typo in YAML is an error, not a no-op."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class LangText(Strict):
    """English is required; Greek follows as it is written."""

    en: str
    el: str | None = None


class Citation(Strict):
    """A pointer into `content/sources.yaml`, with an optional page or section locator."""

    id: str
    locator: str | None = None


# How exact a date is. `span` means the period itself is the fact, not a point in it.
Precision = Literal["day", "month", "season", "year", "span", "circa"]

# Named map extents. The frontend owns the bounding boxes; this is the shared vocabulary.
FrameId = Literal["greece", "cyprus", "aegean-east", "epirus"]


# The two languages every entry is written in. Greek is optional on the model but
# not in policy: the two texts say the same thing, so a fact wrong in one is wrong
# in both.
Lang = Literal["en", "el"]

# What an examination concluded. `unresolved` is the state a boolean would destroy,
# and the most valuable one: it distinguishes "nobody looked" from "someone looked
# hard and the sources do not agree".
ReviewResult = Literal["clean", "corrected", "unresolved"]


class Pass(Strict):
    """One examination of an entry, by a person or by a machine.

    `langs` is load-bearing rather than bookkeeping. The two texts can disagree --
    Navarino was wrong in English while the Greek was right -- so a pass that does
    not record which languages it read cannot be trusted about either of them.
    """

    # Not `on`: YAML 1.1 reads a bare `on` key as the boolean true.
    date: date
    result: ReviewResult
    langs: list[Lang] = Field(min_length=1)
    by: str | None = None
    note: str | None = None


class Review(Strict):
    """Two independent tracks that deliberately never share a column.

    `auto` is broad, cheap, repeatable and never authoritative: it checks arithmetic,
    dates and which instrument did what, against whatever is public. `manual` is a
    person who has read the sources. Merging them would let the cheap pass launder
    itself as the expensive one, which is the whole thing this is built to prevent.

    Absent means nobody has looked yet, so every entry written before this existed
    stays valid and says so honestly.
    """

    auto: Pass | None = None
    manual: Pass | None = None
