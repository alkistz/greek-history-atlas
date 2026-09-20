from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.refs import ids

if TYPE_CHECKING:
    from app.core.content import Corpus


def validate_regimes(c: Corpus) -> list[str]:
    """Regimes must form one unbroken chain: contiguous, non-overlapping, one open end.

    The chain is the whole bargain. Because it has no gaps, a date inside it resolves
    to exactly one regime, and an event can be filtered by regime without storing a
    regime on any event. A gap would leave events unreachable by every chip in the
    facet; an overlap would put them under two. Neither is something to discover in
    the browser, so both fail the boot, as regions.yaml's partition does.

    The chain deliberately does not have to cover the events. An event before the
    revolution has no Greek regime because there was no Greek state, and that is a
    true answer, not a hole -- it behaves like an event with no atom under the region
    filter. What must not happen is a hole *inside* the chain.
    """
    problems: list[str] = []
    polity_ids = ids(c.polities)

    for i, r in enumerate(c.regimes):
        where = f"regime {r.id!r}" if r.id else f"regimes[{i}]"
        if r.polity not in polity_ids:
            problems.append(f"{where}: unknown polity {r.polity!r}")
        if r.end is not None and r.start >= r.end:
            problems.append(f"{where}: from {r.start} is not before to {r.end}")

    ordered = sorted(c.regimes, key=lambda r: r.start)

    # One open end, and it belongs to the last row. An open row anywhere else would
    # swallow every regime after it.
    for r in ordered[:-1]:
        if r.end is None:
            problems.append(f"regime {r.id!r}: only the last regime may be open-ended")

    # Contiguity. Equality in one direction rules out both gaps and overlaps, which
    # is why this is a single check rather than the two control.yaml needs.
    for a, b in zip(ordered, ordered[1:], strict=False):
        if a.end is None:
            continue  # already reported above; do not pile on
        if a.end < b.start:
            problems.append(
                f"gap between regimes {a.id!r} and {b.id!r}: nothing holds {a.end} to {b.start}"
            )
        elif a.end > b.start:
            problems.append(
                f"overlapping regimes {a.id!r} [{a.start}..{a.end}) and "
                f"{b.id!r} [{b.start}..{b.end or 'open'}): "
                f"both cover {b.start}"
            )

    if ordered and ordered[-1].end is not None:
        problems.append(
            f"regime {ordered[-1].id!r} ends {ordered[-1].end} and nothing follows it; "
            "the last regime is open-ended (`to: null`)"
        )
    return problems
