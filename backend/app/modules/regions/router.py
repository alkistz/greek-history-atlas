from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(prefix="/regions", tags=["Regions"])


@router.get("")
def regions(corpus: CorpusDep) -> list[dict[str, Any]]:
    return [r.model_dump(mode="json") for r in crud.list_regions(corpus)]
