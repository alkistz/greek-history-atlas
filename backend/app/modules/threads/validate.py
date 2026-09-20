from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from app.core.refs import ids

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_threads(c: Corpus) -> list[str]:
    """Every id in an arc must name a real event, and name it once.

    A dangling id would silently shorten an arc and break the prev/next chain
    around the gap, which is invisible until someone walks that arc in the
    browser. A repeated id would put the same event before and after itself.

    Coverage is deliberately not checked. An arc is a claim that these events
    form one story; requiring every event to be in one would force arcs that do
    not exist, and an event in no thread is a normal event, not a mistake.
    """
    problems: list[str] = []
    event_ids = ids(c.events)

    for thread in c.threads:
        where = f"thread {thread.id!r}"
        for event_id in thread.events:
            if event_id not in event_ids:
                problems.append(f"{where}: unknown event {event_id!r}")
        for event_id, n in sorted(Counter(thread.events).items()):
            if n > 1:
                problems.append(f"{where}: event {event_id!r} listed {n} times")
    return problems
