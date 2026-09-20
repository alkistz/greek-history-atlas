"""Half-open periods [start, end) and the overlap check every temporal table needs."""

from collections.abc import Callable, Iterable
from datetime import date

OPEN_ENDED = date(9999, 12, 31)


def covers(start: date, end: date | None, on: date) -> bool:
    """A transfer date belongs to the new holder."""
    return start <= on and (end is None or on < end)


def find_overlaps[T](
    rows: Iterable[T],
    start: Callable[[T], date | None],
    end: Callable[[T], date | None],
) -> list[tuple[T, T]]:
    """Pairs of rows whose periods overlap. `None` start means from the beginning of
    time; `None` end means open-ended."""
    ordered = sorted(rows, key=lambda r: start(r) or date.min)
    return [
        (a, b)
        for a, b in zip(ordered, ordered[1:], strict=False)
        if (end(a) or OPEN_ENDED) > (start(b) or date.min)
    ]
