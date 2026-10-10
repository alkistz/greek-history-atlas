from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(prefix="/network", tags=["Network"])


@router.get("/figures")
def figures(corpus: CorpusDep) -> dict[str, Any]:
    """The whole figure graph in one payload: every figure as a node, every pair
    that shares an event or a tie as an edge, with the events and ties on it."""
    return crud.figure_graph(corpus)
