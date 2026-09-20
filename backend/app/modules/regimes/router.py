from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(prefix="/regimes", tags=["Regimes"])


@router.get("")
def regimes(corpus: CorpusDep) -> list[dict[str, Any]]:
    return [r.model_dump(mode="json", by_alias=True) for r in crud.list_regimes(corpus)]
