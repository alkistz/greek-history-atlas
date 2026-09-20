from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(prefix="/atoms", tags=["Atoms"])


@router.get("")
def atoms(corpus: CorpusDep) -> dict[str, Any]:
    """The atom geometry, as a GeoJSON FeatureCollection."""
    return crud.geojson(corpus)
