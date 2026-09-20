from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CorpusDep
from app.modules.figures import crud as figures
from app.modules.instruments import crud as instruments
from app.modules.places import crud as places
from app.modules.sources import crud as sources

from . import crud

router = APIRouter(prefix="/events", tags=["Events"])

# What the ledger needs. The body and the links wait for the detail route.
LIST_EXCLUDE = {"body", "body_html", "figures", "sources"}


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
    }
