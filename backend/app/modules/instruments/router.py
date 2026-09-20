from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CorpusDep
from app.modules.sources import crud as sources

from . import crud

router = APIRouter(prefix="/instruments", tags=["Instruments"])


@router.get("")
def instruments(corpus: CorpusDep) -> list[dict[str, Any]]:
    return [i.model_dump(mode="json", exclude={"sources"}) for i in crud.list_instruments(corpus)]


@router.get("/{instrument_id}")
def instrument(instrument_id: str, corpus: CorpusDep) -> dict[str, Any]:
    found = crud.get_instrument(corpus, instrument_id)
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"no instrument {instrument_id!r}")
    return {
        **found.model_dump(mode="json", exclude={"sources"}),
        "sources": sources.resolve_citations(corpus, found.sources),
        "control": [
            r.model_dump(mode="json", by_alias=True)
            for r in crud.control_rows_of(corpus, instrument_id)
        ],
        "events": [
            {"id": e.id, "title": e.title.model_dump(mode="json"), "period": e.period}
            for e in crud.events_citing(corpus, instrument_id)
        ],
    }
