from datetime import timedelta

from app.core.content import Corpus
from app.modules.events.models import Event

RELATED_WINDOW = timedelta(days=2 * 365)


def list_events(corpus: Corpus) -> list[Event]:
    """Every event, sorted by start date."""
    return sorted(corpus.events, key=lambda e: e.period[0])


def get_event(corpus: Corpus, event_id: str) -> Event | None:
    return next((e for e in corpus.events if e.id == event_id), None)


def related(corpus: Corpus, event: Event) -> list[Event]:
    """Other events on the same atom within two years, either side."""
    if event.atom is None:
        return []
    return [
        e
        for e in list_events(corpus)
        if e.id != event.id
        and e.atom == event.atom
        and abs(e.period[0] - event.period[0]) <= RELATED_WINDOW
    ]
