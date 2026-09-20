from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(prefix="/control", tags=["Control"])


@router.get("")
def control(corpus: CorpusDep) -> list[dict[str, Any]]:
    """Every control row. The client filters by date.

    Deliberately not resolved server side: the client filters as the user
    scrubs, so there is no request per slider tick. Add `?on=` when something
    actually needs it.
    """
    return [c.model_dump(mode="json", by_alias=True) for c in crud.list_control(corpus)]
