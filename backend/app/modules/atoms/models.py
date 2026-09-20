from pydantic import Field

from app.core.models import LangText, Strict


class Atom(Strict):
    """An area whose sovereignty history is identical throughout the whole period."""

    id: str
    name: LangText
    nuts3: list[str] = Field(default_factory=list)
