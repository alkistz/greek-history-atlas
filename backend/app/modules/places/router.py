from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(prefix="/places", tags=["Places"])


@router.get("")
def places(corpus: CorpusDep) -> list[dict[str, Any]]:
    return [p.model_dump(mode="json", by_alias=True) for p in crud.list_places(corpus)]
