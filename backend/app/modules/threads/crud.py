from app.core.content import Corpus
from app.modules.events.models import Event
from app.modules.threads.models import Thread


def list_threads(corpus: Corpus) -> list[Thread]:
    """By the date an arc opens, so the index reads as a chronology of stories."""
    return sorted(corpus.threads, key=lambda t: min(_starts(corpus, t), default=""))


def get_thread(corpus: Corpus, thread_id: str) -> Thread | None:
    return next((t for t in corpus.threads if t.id == thread_id), None)


def _starts(corpus: Corpus, thread: Thread) -> list[str]:
    by_id = {e.id: e for e in corpus.events}
    return [by_id[i].period[0].isoformat() for i in thread.events if i in by_id]


def events_of(corpus: Corpus, thread: Thread) -> list[Event]:
    """The arc's events in date order. Unknown ids cannot survive validation."""
    by_id = {e.id: e for e in corpus.events}
    found = [by_id[i] for i in thread.events if i in by_id]
    return sorted(found, key=lambda e: (e.period[0], e.id))


def threads_of(corpus: Corpus, event_id: str) -> list[Thread]:
    """Every arc an event belongs to. Overlap is intended, so this is a list."""
    return [t for t in list_threads(corpus) if event_id in t.events]


def neighbours(corpus: Corpus, thread: Thread, event_id: str) -> tuple[Event | None, Event | None]:
    """What comes before and after an event inside one arc.

    This is the navigation the detail page lacked: `related` answers "what else was
    nearby", which on a corpus this modern is usually nothing. An arc always has a
    next unless you are at its end.
    """
    ordered = events_of(corpus, thread)
    index = next((i for i, e in enumerate(ordered) if e.id == event_id), None)
    if index is None:
        return None, None
    return (
        ordered[index - 1] if index > 0 else None,
        ordered[index + 1] if index + 1 < len(ordered) else None,
    )
