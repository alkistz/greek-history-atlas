from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(prefix="/relations", tags=["Relations"])


@router.get("")
def relations(corpus: CorpusDep) -> list[dict[str, Any]]:
    """Every tie as written, from the end it was written from."""
    return [r.model_dump(mode="json", by_alias=True) for r in crud.list_relations(corpus)]
