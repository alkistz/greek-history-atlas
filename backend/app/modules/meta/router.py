"""One payload with everything the map needs besides geometry and rows."""

from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep
from app.modules.atoms import crud as atoms
from app.modules.control import crud as control
from app.modules.instruments import crud as instruments
from app.modules.polities import crud as polities

router = APIRouter(prefix="/meta", tags=["Meta"])


@router.get("")
def meta(corpus: CorpusDep) -> dict[str, Any]:
    """Polities with their colours, the atom index, and the epoch list.

    Epochs are every date on which control changes, so they are the complete set
    of distinct maps.
    """
    epochs = control.epochs(corpus)
    return {
        "polities": [p.model_dump(mode="json") for p in polities.list_polities(corpus)],
        "atoms": [
            {"id": a.id, "name": a.name.model_dump(mode="json"), "external": a.external}
            for a in atoms.list_atoms(corpus)
        ],
        "instruments": [
            {"id": i.id, "name": i.name.model_dump(mode="json"), "signed": i.signed.isoformat()}
            for i in instruments.list_instruments(corpus)
        ],
        "epochs": [d.isoformat() for d in epochs],
        "range": {"from": epochs[0].isoformat(), "to": "1975-01-01"},
    }
