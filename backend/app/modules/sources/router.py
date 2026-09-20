from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get("")
def sources(corpus: CorpusDep) -> list[dict[str, Any]]:
    """Every cited work, with what cites it.

    The inverse is computed here rather than in the browser because citations are
    authored on the entries and live only in their detail responses: a client
    building this index itself would have to fetch all 237 of them.
    """
    return [
        {**source.model_dump(mode="json"), "cited_by": crud.citing(corpus, source.id)}
        for source in crud.list_sources(corpus)
    ]
