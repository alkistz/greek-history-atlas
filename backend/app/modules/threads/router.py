from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(prefix="/threads", tags=["Threads"])


def _ref(event) -> dict[str, Any]:
    """An event as an arc sees it. `significance` rides along because an arc's
    shape is mostly which of its steps were the large ones."""
    return {
        "id": event.id,
        "title": event.title.model_dump(mode="json"),
        "period": [d.isoformat() for d in event.period],
        "significance": event.significance,
    }


@router.get("")
def threads(corpus: CorpusDep) -> list[dict[str, Any]]:
    """Every arc with its span and its membership, but without the events resolved.

    The ids are the cheap half of the detail route and the half other pages need:
    with them, one request is enough to filter the ledger by arc or to name the
    arcs an event sits on, instead of nineteen.
    """
    out = []
    for thread in crud.list_threads(corpus):
        events = crud.events_of(corpus, thread)
        out.append(
            {
                **thread.model_dump(mode="json", exclude={"events"}),
                "events": [e.id for e in events],
                "count": len(events),
                "span": [events[0].period[0].isoformat(), events[-1].period[0].isoformat()],
            }
        )
    return out


@router.get("/{thread_id}")
def thread(thread_id: str, corpus: CorpusDep) -> dict[str, Any]:
    """One arc with its events resolved, in reading order."""
    found = crud.get_thread(corpus, thread_id)
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"no thread {thread_id!r}")
    events = crud.events_of(corpus, found)
    return {
        **found.model_dump(mode="json", exclude={"events"}),
        "events": [_ref(e) for e in events],
        "span": [events[0].period[0].isoformat(), events[-1].period[0].isoformat()],
    }
