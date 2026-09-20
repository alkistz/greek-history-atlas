from typing import Literal

from app.core.models import LangText, Strict

PolityKind = Literal["state", "empire", "protectorate", "occupation", "autonomous", "de_facto"]


class Polity(Strict):
    """A state or state-like entity that held territory."""

    id: str
    name: LangText
    kind: PolityKind
    colour: str
