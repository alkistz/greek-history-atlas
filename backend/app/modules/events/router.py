from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CorpusDep
from app.modules.figures import crud as figures
from app.modules.instruments import crud as instruments
from app.modules.places import crud as places
from app.modules.sources import crud as sources
from app.modules.threads import crud as threads

from . import crud

router = APIRouter(prefix="/events", tags=["Events"])

# What the ledger needs. The body and the links wait for the detail route.
LIST_EXCLUDE = {"body", "body_html", "figures", "sources"}


def _ref(event) -> dict[str, Any] | None:
    """A neighbour in an arc, or None at either end of it."""
    if event is None:
        return None
    return {"id": event.id, "title": event.title.model_dump(mode="json"), "period": event.period}


def _arcs(corpus, event_id: str) -> list[dict[str, Any]]:
    """Every arc this event sits on, with the step either way along each.

    This is the way off the page that `related` could not give: proximity finds
    nothing for most modern events, whereas an arc always has a next unless the
    event ends it.
    """
    out = []
    for thread in threads.threads_of(corpus, event_id):
        previous, following = threads.neighbours(corpus, thread, event_id)
        out.append(
            {
                "id": thread.id,
                "name": thread.name.model_dump(mode="json"),
                "previous": _ref(previous),
                "next": _ref(following),
            }
        )
    return out


@router.get("")
def events(corpus: CorpusDep) -> list[dict[str, Any]]:
    """Every event, sorted by date, without prose or links."""
    return [e.model_dump(mode="json", exclude=LIST_EXCLUDE) for e in crud.list_events(corpus)]


@router.get("/{event_id}")
def event(event_id: str, corpus: CorpusDep) -> dict[str, Any]:
    """One event with everything it links to resolved."""
    found = crud.get_event(corpus, event_id)
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"no event {event_id!r}")

    instrument = instruments.get_instrument(corpus, found.instrument) if found.instrument else None
    return {
        **found.model_dump(mode="json", exclude={"body", "figures", "sources", "place"}),
        "place": places.resolve(corpus, found.place, found.period[0]),
        "instrument": (
            {"id": instrument.id, "name": instrument.name.model_dump(mode="json")}
            if instrument
            else None
        ),
        "figures": [
            {"id": fig.id, "name": fig.name.model_dump(mode="json"), "role": p.role}
            for p in found.figures
            if (fig := figures.get_figure(corpus, p.figure)) is not None
        ],
        "sources": sources.resolve_citations(corpus, found.sources),
        "related": [
            {"id": e.id, "title": e.title.model_dump(mode="json"), "period": e.period}
            for e in crud.related(corpus, found)
        ],
        "threads": _arcs(corpus, found.id),
    }
