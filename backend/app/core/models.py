"""Base classes and value types shared by every module's models."""

from pydantic import BaseModel, ConfigDict


class Strict(BaseModel):
    """Content models reject unknown keys: a typo in YAML is an error, not a no-op."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class LangText(Strict):
    """English is required; Greek follows as it is written."""

    en: str
    el: str | None = None
