from app.core.content import Corpus
from app.modules.events.models import Event


def list_events(corpus: Corpus) -> list[Event]:
    """Every event, sorted by start date."""
    return sorted(corpus.events, key=lambda e: e.period[0])


def get_event(corpus: Corpus, event_id: str) -> Event | None:
    return next((e for e in corpus.events if e.id == event_id), None)
