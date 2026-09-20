from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep

from . import crud

router = APIRouter(tags=["Atoms"])


@router.get("/atoms")
def atoms(corpus: CorpusDep) -> dict[str, Any]:
    """The atom geometry, as a GeoJSON FeatureCollection."""
    return crud.geojson(corpus)


@router.get("/context")
def context(corpus: CorpusDep) -> dict[str, Any]:
    """Neighbouring land at present-day extent, uncoloured, for the map backdrop."""
    return crud.context(corpus)
