from typing import Literal

from app.core.models import LangText, Strict

PolityKind = Literal["state", "empire", "protectorate", "occupation", "autonomous", "de_facto"]


class Polity(Strict):
    """A state or state-like entity. Parties to treaties that never hold territory on
    the map (France, Russia) are polities too, and need no colour."""

    id: str
    name: LangText
    kind: PolityKind
    colour: str | None = None
    short: LangText | None = None  # label text on the map, when the full name is too long
