from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get("")
def sources(corpus: CorpusDep) -> list[dict[str, Any]]:
    return [s.model_dump(mode="json") for s in crud.list_sources(corpus)]
