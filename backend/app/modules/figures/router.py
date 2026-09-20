from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CorpusDep
from app.modules.places import crud as places
from app.modules.sources import crud as sources

from . import crud

router = APIRouter(prefix="/figures", tags=["Figures"])

LIST_FIELDS = {"id", "name", "also_known_as", "born", "died", "roles", "summary"}


@router.get("")
def figures(corpus: CorpusDep) -> list[dict[str, Any]]:
    """Every figure, without the long body."""
    return [f.model_dump(mode="json", include=LIST_FIELDS) for f in crud.list_figures(corpus)]


@router.get("/{figure_id}")
def figure(figure_id: str, corpus: CorpusDep) -> dict[str, Any]:
    found = crud.get_figure(corpus, figure_id)
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"no figure {figure_id!r}")

    def life(ev):
        if ev is None:
            return None
        return {**ev.model_dump(mode="json"), "place": places.resolve(corpus, ev.place, ev.date)}

    return {
        **found.model_dump(mode="json", exclude={"body", "sources", "born", "died"}),
        "born": life(found.born),
        "died": life(found.died),
        "sources": sources.resolve_citations(corpus, found.sources),
        "events": [
            {
                "id": e.id,
                "title": e.title.model_dump(mode="json"),
                "period": e.period,
                "role": role,
            }
            for e, role in crud.events_of(corpus, figure_id)
        ],
    }
