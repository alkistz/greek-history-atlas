from typing import Literal

from pydantic import Field

from app.core.models import LangText, Strict

# Nouns, deliberately: a tie is a standing relation, not an act. An act (a coup,
# an appointment, an execution) is an event, and the event links both figures.
RelationKind = Literal[
    "parent",
    "child",
    "sibling",
    "kin",
    "rival",
    "ally",
    "patron",
    "protege",
    "predecessor",
    "successor",
]

# What `to` is to `from`, given what `from` is to `to`. A tie is written once
# and read from either end.
INVERSE: dict[str, str] = {
    "parent": "child",
    "child": "parent",
    "sibling": "sibling",
    "kin": "kin",
    "rival": "rival",
    "ally": "ally",
    "patron": "protege",
    "protege": "patron",
    "predecessor": "successor",
    "successor": "predecessor",
}


class Relation(Strict):
    """`source` is the `kind` of `target`: George I is the parent of Constantine I.

    Written as `from` and `to` in YAML, like a control row's period, because the
    row reads as a sentence that way.
    """

    source: str = Field(alias="from")
    target: str = Field(alias="to")
    kind: RelationKind
    note: LangText | None = None

    def pair(self) -> tuple[str, str]:
        """The tie regardless of which end it was written from."""
        return (min(self.source, self.target), max(self.source, self.target))
