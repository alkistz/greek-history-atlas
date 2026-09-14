"""Read-only API over the content files.

Four routes, all pure reads off an in-memory corpus loaded once at import. There
is no database and no request-path computation worth the name.

`/api/control` deliberately returns every row rather than resolving a date
server side: the client filters as the user scrubs, so there is no request per
slider tick. Add `?on=` when something actually needs it.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from atlas.content import load

CORPUS = load()

app = FastAPI(
    title="after1821",
    description="An atlas of Greek history from 1821.",
    version="0.1.0",
)

# The Vite dev server. Not needed once the frontend proxies /api, but harmless
# and it keeps the API usable from a scratch page.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/atoms")
def atoms() -> dict[str, Any]:
    """The atom geometry, as a GeoJSON FeatureCollection."""
    return CORPUS.geojson


@app.get("/api/meta")
def meta() -> dict[str, Any]:
    """Polities with their colours, the atom index, and the epoch list.

    Epochs are every date on which control changes, so they are the complete set
    of distinct maps.
    """
    epochs = CORPUS.epochs
    return {
        "polities": [p.model_dump(mode="json") for p in CORPUS.polities],
        "atoms": [{"id": a.id, "name": a.name.model_dump(mode="json")} for a in CORPUS.atoms],
        "epochs": [d.isoformat() for d in epochs],
        "range": {"from": epochs[0].isoformat(), "to": "1975-01-01"},
    }


@app.get("/api/control")
def control() -> list[dict[str, Any]]:
    """Every control row. The client filters by date."""
    return [c.model_dump(mode="json", by_alias=True) for c in CORPUS.control]


@app.get("/api/events")
def events() -> list[dict[str, Any]]:
    """Every event, sorted by date."""
    ordered = sorted(CORPUS.events, key=lambda e: e.period[0])
    return [e.model_dump(mode="json") for e in ordered]
