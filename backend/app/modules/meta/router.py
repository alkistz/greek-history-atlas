"""One payload with everything the map needs besides geometry and rows."""

from datetime import date
from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CorpusDep
from app.modules.atoms import crud as atoms
from app.modules.control import crud as control
from app.modules.events import crud as events
from app.modules.instruments import crud as instruments
from app.modules.polities import crud as polities
from app.modules.regimes import crud as regimes
from app.modules.regions import crud as regions

router = APIRouter(prefix="/meta", tags=["Meta"])


def _end(corpus) -> date:
    """The last date the timeline has to reach.

    Control stops moving in 1960 and the corpus does not: a quarter of the events
    happen after the last frontier change. Deriving this from both, rather than
    naming a year here, is what stops the scrubber from ending before the corpus
    does -- a mark past the end of the track is drawn outside the viewBox, which
    is to say not drawn at all.
    """
    last_event = max((e.period[1] for e in events.list_events(corpus)), default=date.min)
    last_epoch = max(control.epochs(corpus), default=date.min)
    # Out to the start of the next year, so the final event is not pinned to the
    # very end of the track with nowhere to scrub past it.
    return date(max(last_event, last_epoch).year + 1, 1, 1)


@router.get("")
def meta(corpus: CorpusDep) -> dict[str, Any]:
    """Polities with their colours, the atom index, the regions and regimes, and the epochs.

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
        "regimes": [r.model_dump(mode="json", by_alias=True) for r in regimes.list_regimes(corpus)],
        "regions": [r.model_dump(mode="json") for r in regions.list_regions(corpus)],
        "epochs": [d.isoformat() for d in epochs],
        "range": {"from": epochs[0].isoformat(), "to": _end(corpus).isoformat()},
    }
