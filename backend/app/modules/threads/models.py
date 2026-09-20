from pydantic import Field

from app.core.models import LangText, Strict


class Thread(Strict):
    """A narrative arc: the events that form one story, in one place.

    Membership lives here and nowhere else, as region membership lives in
    regions.yaml, so an arc can be rewritten or dropped without touching an event.

    `events` is a set rather than a sequence. Reading order is chronological and
    derived, so a list written out of order cannot produce an arc that contradicts
    the timeline. Two events is the minimum: one event is not a story.
    """

    id: str
    name: LangText
    summary: LangText
    events: list[str] = Field(min_length=2)
