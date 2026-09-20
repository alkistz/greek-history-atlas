"""Base classes and value types shared by every module's models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


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
