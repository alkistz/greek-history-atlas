from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("")
def events(corpus: CorpusDep) -> list[dict[str, Any]]:
    """Every event, sorted by date."""
    return [e.model_dump(mode="json") for e in crud.list_events(corpus)]


@router.get("/{event_id}")
def event(event_id: str, corpus: CorpusDep) -> dict[str, Any]:
    found = crud.get_event(corpus, event_id)
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"no event {event_id!r}")
    return found.model_dump(mode="json")
